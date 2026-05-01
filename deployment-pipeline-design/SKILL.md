---
name: deployment-pipeline-design
description: 设计包含审批门控、安全检查和部署编排的多阶段 CI/CD 流水线。在设计零停机部署流水线、实现金丝雀发布策略、设置多环境晋升工作流或调试 CI/CD 中失败的部署门控时使用此技能。
---

# 部署流水线设计

多阶段 CI/CD 流水线的架构模式，包含审批门控、部署策略和环境晋升工作流。

## 目的

设计稳健、安全的部署流水线，通过合理的阶段组织、自动化质量门控和渐进式交付策略来平衡速度与安全性。此技能涵盖流水线架构的结构设计和可靠生产部署的运营模式。

## 输入/输出

### 您需要提供

- **应用类型**：语言/运行时、容器化或裸机、单体或微服务
- **部署目标**：Kubernetes、ECS、虚拟机、无服务器或平台即服务
- **环境拓扑**：环境数量（开发/预发/生产）、区域布局、气隙要求
- **发布要求**：可接受的停机时间、回滚 SLA、流量分割需求、金丝雀还是蓝绿偏好
- **门控约束**：审批团队、所需测试覆盖率阈值、合规扫描（SAST、DAST、SCA）
- **监控栈**：用于自动晋升决策的 Prometheus、Datadog、CloudWatch 或其他指标源

### 此技能产出

- **流水线配置**：阶段定义、作业依赖、并行性和缓存策略
- **部署策略**：带注释配置的选定发布模式（金丝雀权重、蓝绿切换、滚动参数）
- **健康检查设置**：浅层与深层就绪探针、部署后冒烟测试脚本
- **门控定义**：自动化指标阈值和手动审批工作流
- **回滚计划**：自动化回滚触发器和手动运维手册步骤

## 何时使用

- 为新服务或平台迁移设计 CI/CD 架构
- 在环境之间实现部署门控
- 配置带有强制安全扫描的多环境流水线
- 使用金丝雀或蓝绿策略建立渐进式交付
- 调试阶段成功但生产行为异常的流水线
- 通过指标降级时自动回滚来减少平均恢复时间

## 流水线阶段

### 标准流水线流程

```
┌─────────┐   ┌──────┐   ┌─────────┐   ┌────────┐   ┌──────────┐
│  构建    │ → │ 测试 │ → │ 预发    │ → │ 审批  │ → │ 生产     │
└─────────┘   └──────┘   └─────────┘   └────────┘   └──────────┘
```

### 详细阶段分解

1. **源代码** - 代码检出、依赖图解析
2. **构建** - 编译、打包、容器化、签名制品
3. **测试** - 单元测试、集成测试、SAST/SCA 安全扫描
4. **预发部署** - 部署到预发环境并进行冒烟测试
5. **集成测试** - 端到端测试、契约测试、性能基线
6. **审批门控** - 手动或基于指标的自动化门控
7. **生产部署** - 金丝雀、蓝绿或滚动策略
8. **验证** - 深度健康检查、合成监控
9. **回滚** - 失败信号时自动回滚

## 审批门控模式

### 模式 1：手动审批（GitHub Actions）

```yaml
production-deploy:
  needs: staging-deploy
  environment:
    name: production
    url: https://app.example.com
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to production
      run: kubectl apply -f k8s/production/
```

GitHub 中的环境保护规则在此作业开始前强制要求审批人。在 **Settings -> Environments -> production -> Required reviewers** 中配置审批人。

### 模式 2：基于时间的审批（GitLab CI）

```yaml
deploy:production:
  stage: deploy
  script:
    - deploy.sh production
  environment:
    name: production
  when: delayed
  start_in: 30 minutes
  only:
    - main
```

### 模式 3：多审批人（Azure Pipelines）

```yaml
stages:
  - stage: Production
    dependsOn: Staging
    jobs:
      - deployment: Deploy
        environment:
          name: production
          resourceType: Kubernetes
        strategy:
          runOnce:
            preDeploy:
              steps:
                - task: ManualValidation@0
                  inputs:
                    notifyUsers: "team-leads@example.com"
                    instructions: "Review staging metrics before approving"
```

### 模式 4：自动化指标门控

使用 AnalysisTemplate（Argo Rollouts）或自定义门控脚本，在错误率超过阈值时阻止晋升：

```yaml
# Argo Rollouts AnalysisTemplate — 自动阻止金丝雀晋升
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
  - name: success-rate
    interval: 60s
    successCondition: "result[0] >= 0.95"
    failureCondition: "result[0] < 0.90"
    inconclusiveLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{status!~"5..",job="my-app"}[2m]))
          / sum(rate(http_requests_total{job="my-app"}[2m]))
```

## 部署策略

### 决策表

| 策略       | 停机时间 | 回滚速度 | 成本影响         | 最适合                         |
|-----------|---------|---------|-----------------|-------------------------------|
| 滚动       | 无      | ~分钟    | 无               | 大多数无状态服务                |
| 蓝绿       | 无      | 即时     | 2 倍基础设施（临时）| 高风险或数据库迁移              |
| 金丝雀     | 无      | 即时     | 最小             | 高流量、指标驱动                |
| 重建       | 有      | 快       | 无               | 开发/测试、批处理作业            |
| 功能标志    | 无      | 即时     | 无               | 渐进式功能暴露                  |

### 1. 滚动部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2         # 发布期间最多 12 个 pod
      maxUnavailable: 1   # 始终至少有 9 个 pod 提供服务
```

特点：渐进式发布、零停机、易于回滚、最适合大多数应用。

### 2. 蓝绿部署

```bash
# 将流量从蓝切换到绿
kubectl apply -f k8s/green-deployment.yaml
kubectl rollout status deployment/my-app-green

# 切换服务选择器
kubectl patch service my-app -p '{"spec":{"selector":{"version":"green"}}}'

# 如果需要，即时回滚
kubectl patch service my-app -p '{"spec":{"selector":{"version":"blue"}}}'
```

特点：即时切换、易于回滚、临时基础设施成本翻倍、适用于启动时间长的高风险部署。

### 3. 金丝雀部署（Argo Rollouts）

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      analysis:
        templates:
          - templateName: success-rate
        startingStep: 2
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - setWeight: 25
        - pause: { duration: 5m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
```

特点：渐进式流量转移、真实用户指标验证、自动晋升或回滚、需要 Argo Rollouts 或服务网格。

### 4. 功能标志

```python
from flagsmith import Flagsmith

flagsmith = Flagsmith(environment_key="API_KEY")

if flagsmith.has_feature("new_checkout_flow"):
    process_checkout_v2()
else:
    process_checkout_v1()
```

特点：部署但不发布、A/B 测试、按用户细分即时回滚、独立于部署的细粒度控制。

## 流水线编排

### 多阶段流水线示例（GitHub Actions）

```yaml
name: Production Pipeline

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.build.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      - name: Build and push Docker image
        id: build
        run: |
          IMAGE=myapp:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE
          echo "image=$IMAGE" >> $GITHUB_OUTPUT

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Unit tests
        run: make test
      - name: Security scan
        run: trivy image ${{ needs.build.outputs.image }}

  deploy-staging:
    needs: test
    environment:
      name: staging
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/

  integration-test:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: Run E2E tests
        run: npm run test:e2e

  deploy-production:
    needs: integration-test
    environment:
      name: production        # 在此处阻塞，直到所需审批人批准
    runs-on: ubuntu-latest
    steps:
      - name: Canary deployment
        run: |
          kubectl apply -f k8s/production/
          kubectl argo rollouts promote my-app

  verify:
    needs: deploy-production
    runs-on: ubuntu-latest
    steps:
      - name: Deep health check
        run: |
          for i in {1..12}; do
            STATUS=$(curl -sf https://app.example.com/health/ready | jq -r '.status')
            [ "$STATUS" = "ok" ] && exit 0
            sleep 10
          done
          exit 1
      - name: Notify on success
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text":"Production deployment successful: ${{ github.sha }}"}'
```

## 健康检查

### 浅层与深层健康端点

浅层 `/ping` 在下游依赖中断时仍返回 200。使用深度就绪端点在提升流量前验证实际依赖。

```python
# /health/ready — 检查真实依赖，由流水线门控使用
@app.get("/health/ready")
async def readiness():
    checks = {
        "database": await check_db_connection(),
        "cache":    await check_redis_connection(),
        "queue":    await check_queue_connection(),
    }
    status = "ok" if all(checks.values()) else "degraded"
    code = 200 if status == "ok" else 503
    return JSONResponse({"status": status, "checks": checks}, status_code=code)
```

### 部署后验证脚本

```bash
#!/usr/bin/env bash
# verify-deployment.sh — 每次生产部署后运行
set -euo pipefail

ENDPOINT="${1:?用法: verify-deployment.sh <base-url>}"
MAX_ATTEMPTS=12
SLEEP_SECONDS=10

for i in $(seq 1 $MAX_ATTEMPTS); do
  STATUS=$(curl -sf "$ENDPOINT/health/ready" | jq -r '.status' 2>/dev/null || echo "unreachable")
  if [ "$STATUS" = "ok" ]; then
    echo "健康检查在 $((i * SLEEP_SECONDS))s 后通过"
    exit 0
  fi
  echo "尝试 $i/$MAX_ATTEMPTS：status=$STATUS — ${SLEEP_SECONDS}s 后重试"
  sleep "$SLEEP_SECONDS"
done

echo "健康检查在 $((MAX_ATTEMPTS * SLEEP_SECONDS))s 后失败"
exit 1
```

## 回滚策略

### 流水线中的自动回滚

```yaml
deploy-and-verify:
  steps:
    - name: Deploy new version
      run: kubectl apply -f k8s/

    - name: Wait for rollout
      run: kubectl rollout status deployment/my-app --timeout=5m

    - name: Post-deployment health check
      id: health
      run: ./scripts/verify-deployment.sh https://app.example.com

    - name: Rollback on failure
      if: failure()
      run: |
        kubectl rollout undo deployment/my-app
        echo "Rolled back to previous revision"
```

### 手动回滚命令

```bash
# 列出修订历史及变更原因注释
kubectl rollout history deployment/my-app

# 回滚到上一版本
kubectl rollout undo deployment/my-app

# 回滚到特定修订版本
kubectl rollout undo deployment/my-app --to-revision=3

# 验证回滚完成
kubectl rollout status deployment/my-app
```

有关高级回滚策略（包括数据库迁移回滚和 Argo Rollouts 中止流程），请参阅 [`references/advanced-strategies.md`](references/advanced-strategies.md)。

## 监控和指标

### 关键 DORA 指标跟踪

| 指标                    | 目标（精英级） | 测量方法                           |
|--------------------------|--------------|-----------------------------------|
| 部署频率                  | 每天多次      | 每天流水线运行次数                   |
| 变更前置时间              | < 1 小时      | 提交时间戳 -> 生产部署              |
| 变更失败率                | < 5%         | 失败部署 / 总部署                   |
| 平均恢复时间              | < 1 小时      | 事件开启 -> 服务恢复                |

### 部署后指标验证

```yaml
- name: Verify error rate post-deployment
  run: |
    sleep 60  # 等待指标积累

    ERROR_RATE=$(curl -sf "$PROMETHEUS_URL/api/v1/query" \
      --data-urlencode 'query=sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))' \
      | jq '.data.result[0].value[1]')

    echo "当前错误率: $ERROR_RATE"
    if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
      echo "错误率 $ERROR_RATE 超过 1% 阈值 — 触发回滚"
      exit 1
    fi
```

## 流水线最佳实践

1. **快速失败** — 在慢速检查（E2E、安全扫描）之前运行快速检查（lint、单元测试）
2. **并行执行** — 并发运行独立作业以最小化总流水线时间
3. **缓存** — 在运行之间缓存依赖层和构建制品
4. **制品晋升** — 构建一次，将相同制品提升通过所有环境
5. **环境一致性** — 使预发基础设施尽可能接近生产环境
6. **密钥管理** — 使用密钥存储（Vault、AWS Secrets Manager、GitHub 加密密钥）— 切勿硬编码
7. **部署窗口** — 优先选择低流量窗口；通过门控策略强制执行变更冻结期
8. **幂等部署** — 确保重新运行部署产生相同结果
9. **回滚自动化** — 在健康检查或指标阈值失败时自动触发回滚
10. **注释部署** — 向监控工具（Datadog、Grafana）发送部署标记以进行关联

## 故障排除

### 流水线中健康检查通过但生产中服务不健康

流水线健康检查命中了浅层 `/ping` 端点，即使数据库不可达也返回 200。使用深度就绪检查来验证实际依赖（请参阅上面的健康检查部分）。

### 金丝雀部署永远不会晋升到 100%

Argo Rollouts 需要有效的 `AnalysisTemplate` 才能自动晋升。如果 Prometheus 查询未返回数据（例如指标名称已更改），分析保持不确定状态，晋升将停滞。添加 `inconclusiveLimit` 以便发布快速失败而不是挂起：

```yaml
spec:
  metrics:
  - name: error-rate
    failureCondition: "result[0] > 0.05"
    inconclusiveLimit: 2   # 2 次不确定结果后失败，而不是无限期挂起
    provider:
      prometheus:
        query: |
          sum(rate(http_requests_total{status=~"5.."}[2m]))
          / sum(rate(http_requests_total[2m]))
```

### 预发部署成功但生产作业永不启动

检查是否配置了生产环境保护规则 — 缺少审批人分配意味着审批门控会无限期等待且无通知。在 GitHub Actions 中，确保在 **Settings -> Environments -> production** 中将 `Required reviewers` 设置为现有用户或团队。

### 每次运行都破坏 Docker 层缓存导致构建缓慢

如果 `COPY . .` 出现在依赖安装之前，任何源文件更改都会使依赖层失效。重新排序以先复制依赖清单：

```dockerfile
# 好的做法：依赖与源代码分开缓存
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

### 回滚后数据库迁移仍应用在旧代码上

没有迁移回滚的服务回滚会导致架构/代码不匹配错误。始终使迁移向后兼容（仅添加）至少一个发布周期，并将撤消脚本与迁移一起版本化：

```bash
# migrations/V20240315__add_nullable_column.sql       （前向）
# migrations/V20240315__add_nullable_column.undo.sql  （后向）
```

在旧代码版本从所有环境中完全退役之前，永远不要运行破坏性迁移（DROP COLUMN、ALTER NOT NULL）。

## 高级主题

有关平台特定的流水线配置、多区域晋升工作流和高级 Argo Rollouts 模式，请参阅：

- [`references/advanced-strategies.md`](references/advanced-strategies.md) — 扩展 YAML 示例、平台特定配置（GitHub Actions、GitLab CI、Azure Pipelines）、多区域金丝雀模式和数据库迁移回滚策略

## 相关技能

- `github-actions-templates` - GitHub Actions 实现模式和可重用工作流
- `gitlab-ci-patterns` - GitLab CI/CD 流水线实现
- `secrets-management` - CI/CD 流水线中的密钥处理
