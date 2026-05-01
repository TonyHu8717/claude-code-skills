---
name: incident-runbook-templates
description: 创建结构化的事件响应手册，包含分步流程、升级路径和恢复操作。在为支付处理系统构建服务中断手册、创建涵盖连接池耗尽、复制延迟和磁盘空间告警的数据库事件流程、为需要在凌晨 3 点也能理解的分步恢复指南培训新值班工程师，或在多个工程团队之间标准化升级矩阵时使用此技能。
---

# 事件手册模板

生产就绪的事件响应手册模板，涵盖检测、分类、缓解、解决和沟通。

## 何时使用此技能

- 创建事件响应流程
- 构建特定服务的手册
- 建立升级路径
- 记录恢复流程
- 响应活跃事件
- 培训值班工程师

## 核心概念

### 1. 事件严重级别

| 严重级别 | 影响                       | 响应时间          | 示例                    |
| -------- | -------------------------- | ----------------- | ----------------------- |
| **SEV1** | 完全中断、数据丢失         | 15 分钟           | 生产环境宕机            |
| **SEV2** | 严重降级                   | 30 分钟           | 关键功能故障            |
| **SEV3** | 轻微影响                   | 2 小时            | 非关键 bug              |
| **SEV4** | 最小影响                   | 下一个工作日      | 外观问题                |

### 2. 手册结构

```
1. 概述与影响
2. 检测与告警
3. 初始分类
4. 缓解步骤
5. 根因调查
6. 解决流程
7. 验证与回滚
8. 沟通模板
9. 升级矩阵
```

## 手册模板

### 模板 1：服务中断手册

````markdown
# [服务名称] 中断手册

## 概述

**服务**：支付处理服务
**负责人**：平台团队
**Slack**：#payments-incidents
**PagerDuty**：payments-oncall

## 影响评估

- [ ] 哪些客户受到影响？
- [ ] 多大比例的流量受到影响？
- [ ] 是否有财务影响？
- [ ] 影响范围有多大？

## 检测

### 告警

- `payment_error_rate > 5%`（PagerDuty）
- `payment_latency_p99 > 2s`（Slack）
- `payment_success_rate < 95%`（PagerDuty）

### 仪表板

- [支付服务仪表板](https://grafana/d/payments)
- [错误跟踪](https://sentry.io/payments)
- [依赖状态](https://status.stripe.com)

## 初始分类（前 5 分钟）

### 1. 评估范围

```bash
# 检查服务健康
kubectl get pods -n payments -l app=payment-service

# 检查最近部署
kubectl rollout history deployment/payment-service -n payments

# 检查错误率
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{status=~'5..'}[5m]))"
````

### 2. 快速健康检查

- [ ] 能否访问服务？`curl -I https://api.company.com/payments/health`
- [ ] 数据库连接？检查连接池指标
- [ ] 外部依赖？检查 Stripe、银行 API 状态
- [ ] 最近变更？检查部署历史

### 3. 初始分类

| 症状               | 可能原因            | 转到章节          |
| ------------------- | ------------------- | ----------------- |
| 所有请求失败        | 服务宕机            | 第 4.1 节         |
| 高延迟              | 数据库/依赖         | 第 4.2 节         |
| 部分失败            | 代码 bug            | 第 4.3 节         |
| 错误激增            | 流量高峰            | 第 4.4 节         |

## 缓解流程

### 4.1 服务完全宕机

```bash
# 步骤 1：检查 Pod 状态
kubectl get pods -n payments

# 步骤 2：如果 Pod 崩溃循环，检查日志
kubectl logs -n payments -l app=payment-service --tail=100

# 步骤 3：检查最近部署
kubectl rollout history deployment/payment-service -n payments

# 步骤 4：如果怀疑是最近部署导致，回滚
kubectl rollout undo deployment/payment-service -n payments

# 步骤 5：如果资源不足，扩容
kubectl scale deployment/payment-service -n payments --replicas=10

# 步骤 6：验证恢复
kubectl rollout status deployment/payment-service -n payments
```

### 4.2 高延迟

```bash
# 步骤 1：检查数据库连接
kubectl exec -n payments deploy/payment-service -- \
  curl localhost:8080/metrics | grep db_pool

# 步骤 2：检查慢查询（如果是数据库问题）
psql -h $DB_HOST -U $DB_USER -c "
  SELECT pid, now() - query_start AS duration, query
  FROM pg_stat_activity
  WHERE state = 'active' AND duration > interval '5 seconds'
  ORDER BY duration DESC;"

# 步骤 3：如需要，终止长时间运行的查询
psql -h $DB_HOST -U $DB_USER -c "SELECT pg_terminate_backend(pid);"

# 步骤 4：检查外部依赖延迟
curl -w "@curl-format.txt" -o /dev/null -s https://api.stripe.com/v1/health

# 步骤 5：如果依赖缓慢，启用熔断器
kubectl set env deployment/payment-service \
  STRIPE_CIRCUIT_BREAKER_ENABLED=true -n payments
```

### 4.3 部分失败（特定错误）

```bash
# 步骤 1：识别错误模式
kubectl logs -n payments -l app=payment-service --tail=500 | \
  grep -i error | sort | uniq -c | sort -rn | head -20

# 步骤 2：检查错误跟踪
# 访问 Sentry：https://sentry.io/payments

# 步骤 3：如果是特定端点，启用功能标志禁用
curl -X POST https://api.company.com/internal/feature-flags \
  -d '{"flag": "DISABLE_PROBLEMATIC_FEATURE", "enabled": true}'

# 步骤 4：如果是数据问题，检查最近数据变更
psql -h $DB_HOST -c "
  SELECT * FROM audit_log
  WHERE table_name = 'payment_methods'
  AND created_at > now() - interval '1 hour';"
```

### 4.4 流量高峰

```bash
# 步骤 1：检查当前请求速率
kubectl top pods -n payments

# 步骤 2：水平扩容
kubectl scale deployment/payment-service -n payments --replicas=20

# 步骤 3：启用速率限制
kubectl set env deployment/payment-service \
  RATE_LIMIT_ENABLED=true \
  RATE_LIMIT_RPS=1000 -n payments

# 步骤 4：如果是攻击，阻止可疑 IP
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-suspicious
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: payment-service
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 192.168.1.0/24  # 可疑范围
EOF
```

## 验证步骤

```bash
# 验证服务健康
curl -s https://api.company.com/payments/health | jq

# 验证错误率恢复正常
curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{status=~'5..'}[5m]))" | jq '.data.result[0].value[1]'

# 验证延迟可接受
curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.99,sum(rate(http_request_duration_seconds_bucket[5m]))by(le))" | jq

# 冒烟测试关键流程
./scripts/smoke-test-payments.sh
```

## 回滚流程

```bash
# 回滚 Kubernetes 部署
kubectl rollout undo deployment/payment-service -n payments

# 回滚数据库迁移（如适用）
./scripts/db-rollback.sh $MIGRATION_VERSION

# 回滚功能标志
curl -X POST https://api.company.com/internal/feature-flags \
  -d '{"flag": "NEW_PAYMENT_FLOW", "enabled": false}'
```

## 升级矩阵

| 条件                        | 升级给              | 联系方式            |
| --------------------------- | ------------------- | ------------------- |
| SEV1 超过 15 分钟未解决     | 工程经理            | @manager (Slack)    |
| 怀疑数据泄露                | 安全团队            | #security-incidents |
| 财务影响 > $10k             | 财务 + 法务         | @finance-oncall     |
| 需要客户沟通                | 支持负责人          | @support-lead       |

## 沟通模板

### 初始通知（内部）

```
🚨 事件：支付服务降级

严重级别：SEV2
状态：调查中
影响：约 20% 的支付请求失败
开始时间：[时间]
事件指挥官：[姓名]

当前操作：
- 调查根因
- 扩容服务
- 监控仪表板

更新见 #payments-incidents
```

### 状态更新

```
📊 更新：支付服务事件

状态：缓解中
影响：失败率降至约 5%
持续时间：25 分钟

已采取操作：
- 回滚部署 v2.3.4 → v2.3.3
- 服务从 5 扩容到 10 个副本

下一步：
- 持续监控
- 根因分析进行中

预计解决时间：约 15 分钟
```

### 解决通知

```
✅ 已解决：支付服务事件

持续时间：45 分钟
影响：约 5,000 笔受影响的交易
根因：v2.3.4 中的内存泄漏

解决方案：
- 回滚到 v2.3.3
- 交易自动重试成功

后续：
- 复盘会议定于 [日期]
- Bug 修复进行中
````

### 模板 2：数据库事件手册

```markdown
# 数据库事件手册

## 快速参考
| 问题 | 命令 |
|------|------|
| 检查连接 | `SELECT count(*) FROM pg_stat_activity;` |
| 终止查询 | `SELECT pg_terminate_backend(pid);` |
| 检查复制延迟 | `SELECT extract(epoch from (now() - pg_last_xact_replay_timestamp()));` |
| 检查锁 | `SELECT * FROM pg_locks WHERE NOT granted;` |

## 连接池耗尽
```sql
-- 检查当前连接
SELECT datname, usename, state, count(*)
FROM pg_stat_activity
GROUP BY datname, usename, state
ORDER BY count(*) DESC;

-- 识别长时间运行的连接
SELECT pid, usename, datname, state, query_start, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- 终止空闲连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND query_start < now() - interval '10 minutes';
````

## 复制延迟

```sql
-- 检查副本延迟
SELECT
  CASE
    WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN 0
    ELSE extract(epoch from now() - pg_last_xact_replay_timestamp())
  END AS lag_seconds;

-- 如果延迟 > 60s，考虑：
-- 1. 检查主库/副本之间的网络
-- 2. 检查副本磁盘 I/O
-- 3. 如果无法恢复，考虑故障转移
```

## 磁盘空间告急

```bash
# 检查磁盘使用
df -h /var/lib/postgresql/data

# 查找大表
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;"

# VACUUM 回收空间
psql -c "VACUUM FULL large_table;"

# 如果紧急，删除旧数据或扩展磁盘
```

```

## 最佳实践

### 应该做的
- **保持手册更新** - 每次事件后审查
- **定期测试手册** - 演练日、混沌工程
- **包含回滚步骤** - 始终有逃生通道
- **记录假设** - 步骤有效所需的前提条件
- **链接到仪表板** - 压力下快速访问

### 不应该做的
- **不要假设知识** - 为凌晨 3 点的大脑而写
- **不要跳过验证** - 确认每步都成功
- **不要忘记沟通** - 保持利益相关者知情
- **不要独自工作** - 尽早升级
- **不要跳过复盘** - 从每次事件中学习

## 故障排除

### 手册步骤在预发布环境有效但在真实事件中失败

步骤通常假设在健康环境中为真但在中断期间不为真的前提条件。为手册中的每个命令添加前置检查和"如果此命令失败该怎么做"的说明：

```bash
# 步骤：检查 Pod 状态
kubectl get pods -n payments

# 前置条件：kubectl 已配置，kubeconfig 指向正确的集群
# 如果失败：运行 `aws eks update-kubeconfig --name prod-cluster --region us-east-1`
# 预期输出：Pod 处于 Running 状态
```

### 值班工程师恐慌并跳过步骤

在手册顶部添加一个编号清单，镜像章节编号，以便响应者在压力下无需阅读完整文档即可跟踪进度：

```markdown
## 快速清单
- [ ] 1. 声明事件严重级别并开启战情室
- [ ] 2. 检查服务健康（第 4.1 节）
- [ ] 3. 检查最近部署（第 4.1 节）
- [ ] 4. 如果怀疑是部署导致则回滚（第 4.1 节）
- [ ] 5. 在 #payments-incidents 发布初始通知
- [ ] 6. 如果超过 15 分钟未解决则升级
```

### 手册过时 — 命令引用旧的集群名称或端点

手册因为手动更新而失效。在顶部包含"最后验证"日期和负责人，并添加 CI 检查验证所有 `curl` 端点和 `kubectl` 上下文名称是否仍然有效：

```markdown
## 手册元数据
| 字段 | 值 |
|---|---|
| 最后验证 | 2024-11-15 |
| 负责人 | @platform-team |
| 审查频率 | 每次 SEV1/SEV2 之后 |
```

### 工程师埋头工作时利益相关者沟通延迟

指定专门的事件沟通员角色（与事件指挥官分开），唯一职责是发布状态更新。在沟通模板中添加固定议程：

```
每 15 分钟更新一次（即使没有新信息）：
- 当前状态（调查中 / 缓解中 / 监控中）
- 影响（什么坏了、谁受影响、流量百分比）
- 我们现在在做什么
- 下次更新：15 分钟后
```

### 数据库手册命令在错误执行时导致额外停机

在破坏性 SQL 命令前添加明确警告，并要求在执行前进行试运行输出检查：

```sql
-- 警告：这会终止活跃连接。请先验证数量。
-- 试运行（终止前检查数量）：
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';

-- 仅在验证数量合理（< 50）后执行：
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND query_start < now() - interval '10 minutes';
```

## 相关技能

- `postmortem-writing` - 解决事件后，使用复盘模板记录根因和预防措施
- `on-call-handoff-patterns` - 结构化交接班，使接班响应者了解活跃事件的完整上下文
