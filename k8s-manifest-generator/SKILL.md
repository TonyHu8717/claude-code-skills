---
name: k8s-manifest-generator
description: 创建生产就绪的 Kubernetes 清单，包括 Deployment、Service、ConfigMap 和 Secret，遵循最佳实践和安全标准。在生成 Kubernetes YAML 清单、创建 K8s 资源或实现生产级 Kubernetes 配置时使用。
---

# Kubernetes 清单生成器

创建生产就绪 Kubernetes 清单的分步指南，包括 Deployment、Service、ConfigMap、Secret 和 PersistentVolumeClaim。

## 目的

本技能提供生成结构良好、安全且生产就绪的 Kubernetes 清单的综合指南，遵循云原生最佳实践和 Kubernetes 约定。

## 何时使用此技能

在以下情况下使用此技能：

- 创建新的 Kubernetes Deployment 清单
- 定义 Service 资源以实现网络连接
- 生成 ConfigMap 和 Secret 资源以进行配置管理
- 为有状态工作负载创建 PersistentVolumeClaim 清单
- 遵循 Kubernetes 最佳实践和命名约定
- 实现资源限制、健康检查和安全上下文
- 设计多环境部署的清单

## 分步工作流

### 1. 收集需求

**了解工作负载：**

- 应用类型（无状态/有状态）
- 容器镜像和版本
- 环境变量和配置需求
- 存储需求
- 网络暴露需求（内部/外部）
- 资源需求（CPU、内存）
- 扩缩需求
- 健康检查端点

**需要询问的问题：**

- 应用名称和用途是什么？
- 使用什么容器镜像和标签？
- 应用是否需要持久存储？
- 应用暴露哪些端口？
- 是否需要任何密钥或配置文件？
- CPU 和内存需求是什么？
- 应用是否需要对外暴露？

### 2. 创建 Deployment 清单

**遵循此结构：**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <app-name>
  namespace: <namespace>
  labels:
    app: <app-name>
    version: <version>
spec:
  replicas: 3
  selector:
    matchLabels:
      app: <app-name>
  template:
    metadata:
      labels:
        app: <app-name>
        version: <version>
    spec:
      containers:
        - name: <container-name>
          image: <image>:<tag>
          ports:
            - containerPort: <port>
              name: http
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: ENV_VAR
              value: "value"
          envFrom:
            - configMapRef:
                name: <app-name>-config
            - secretRef:
                name: <app-name>-secret
```

**应用的最佳实践：**

- 始终设置资源请求和限制
- 实现存活和就绪探针
- 使用特定的镜像标签（绝不使用 `:latest`）
- 为非 root 用户应用安全上下文
- 使用标签进行组织和选择
- 根据可用性需求设置适当的副本数

**参考：** 详细部署选项见 `references/deployment-spec.md`

### 3. 创建 Service 清单

**选择适当的 Service 类型：**

**ClusterIP（仅内部）：**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <app-name>
  namespace: <namespace>
  labels:
    app: <app-name>
spec:
  type: ClusterIP
  selector:
    app: <app-name>
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
```

**LoadBalancer（外部访问）：**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <app-name>
  namespace: <namespace>
  labels:
    app: <app-name>
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  type: LoadBalancer
  selector:
    app: <app-name>
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
```

**参考：** Service 类型和网络详情见 `references/service-spec.md`

### 4. 创建 ConfigMap

**用于应用配置：**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: <app-name>-config
  namespace: <namespace>
data:
  APP_MODE: production
  LOG_LEVEL: info
  DATABASE_HOST: db.example.com
  # 用于配置文件
  app.properties: |
    server.port=8080
    server.host=0.0.0.0
    logging.level=INFO
```

**最佳实践：**

- 仅对非敏感数据使用 ConfigMap
- 将相关配置组织在一起
- 使用有意义的键名
- 考虑每个组件使用一个 ConfigMap
- 更改时对 ConfigMap 进行版本控制

**参考：** 示例见 `assets/configmap-template.yaml`

### 5. 创建 Secret

**用于敏感数据：**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <app-name>-secret
  namespace: <namespace>
type: Opaque
stringData:
  DATABASE_PASSWORD: "changeme"
  API_KEY: "secret-api-key"
  # 用于证书文件
  tls.crt: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  tls.key: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

**安全考虑：**

- 绝不将密钥以明文提交到 Git
- 使用 Sealed Secrets、External Secrets Operator 或 Vault
- 定期轮换密钥
- 使用 RBAC 限制密钥访问
- 考虑对 TLS 密钥使用 Secret 类型：`kubernetes.io/tls`

### 6. 创建 PersistentVolumeClaim（如需要）

**用于有状态应用：**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: <app-name>-data
  namespace: <namespace>
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: gp3
  resources:
    requests:
      storage: 10Gi
```

**在 Deployment 中挂载：**

```yaml
spec:
  template:
    spec:
      containers:
        - name: app
          volumeMounts:
            - name: data
              mountPath: /var/lib/app
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: <app-name>-data
```

**存储考虑：**

- 根据性能需求选择适当的 StorageClass
- 对单 Pod 访问使用 ReadWriteOnce
- 对多 Pod 共享存储使用 ReadWriteMany
- 考虑备份策略
- 设置适当的保留策略

### 7. 应用安全最佳实践

**在 Deployment 中添加安全上下文：**

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: app
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
```

**安全清单：**

- [ ] 以非 root 用户运行
- [ ] 丢弃所有能力
- [ ] 使用只读根文件系统
- [ ] 禁用特权提升
- [ ] 设置 seccomp 配置文件
- [ ] 使用 Pod 安全标准

### 8. 添加标签和注解

**标准标签（推荐）：**

```yaml
metadata:
  labels:
    app.kubernetes.io/name: <app-name>
    app.kubernetes.io/instance: <instance-name>
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: <system-name>
    app.kubernetes.io/managed-by: kubectl
```

**有用的注解：**

```yaml
metadata:
  annotations:
    description: "Application description"
    contact: "team@example.com"
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
```

### 9. 组织多资源清单

**文件组织选项：**

**选项 1：使用 `---` 分隔符的单文件**

```yaml
# app-name.yaml
---
apiVersion: v1
kind: ConfigMap
...
---
apiVersion: v1
kind: Secret
...
---
apiVersion: apps/v1
kind: Deployment
...
---
apiVersion: v1
kind: Service
...
```

**选项 2：独立文件**

```
manifests/
├── configmap.yaml
├── secret.yaml
├── deployment.yaml
├── service.yaml
└── pvc.yaml
```

**选项 3：Kustomize 结构**

```
base/
├── kustomization.yaml
├── deployment.yaml
├── service.yaml
└── configmap.yaml
overlays/
├── dev/
│   └── kustomization.yaml
└── prod/
    └── kustomization.yaml
```

### 10. 验证和测试

**验证步骤：**

```bash
# 试运行验证
kubectl apply -f manifest.yaml --dry-run=client

# 服务端验证
kubectl apply -f manifest.yaml --dry-run=server

# 使用 kubeval 验证
kubeval manifest.yaml

# 使用 kube-score 验证
kube-score score manifest.yaml

# 使用 kube-linter 检查
kube-linter lint manifest.yaml
```

**测试清单：**

- [ ] 清单通过试运行验证
- [ ] 所有必需字段都存在
- [ ] 资源限制合理
- [ ] 健康检查已配置
- [ ] 安全上下文已设置
- [ ] 标签遵循约定
- [ ] 命名空间存在或已创建

## 常见模式

### 模式 1：简单无状态 Web 应用

**用例：** 标准 Web API 或微服务

**所需组件：**

- Deployment（3 副本实现高可用）
- ClusterIP Service
- ConfigMap 用于配置
- Secret 用于 API 密钥
- HorizontalPodAutoscaler（可选）

**参考：** 见 `assets/deployment-template.yaml`

### 模式 2：有状态数据库应用

**用例：** 数据库或持久存储应用

**所需组件：**

- StatefulSet（而非 Deployment）
- Headless Service
- PersistentVolumeClaim 模板
- ConfigMap 用于数据库配置
- Secret 用于凭据

### 模式 3：后台任务或 Cron

**用例：** 定时任务或批处理

**所需组件：**

- CronJob 或 Job
- ConfigMap 用于任务参数
- Secret 用于凭据
- 带 RBAC 的 ServiceAccount

### 模式 4：多容器 Pod

**用例：** 带边车容器的应用

**所需组件：**

- 包含多个容器的 Deployment
- 容器间共享卷
- 用于设置的 Init 容器
- Service（如需要）

## 模板

以下模板可在 `assets/` 目录中找到：

- `deployment-template.yaml` - 遵循最佳实践的标准部署
- `service-template.yaml` - Service 配置（ClusterIP、LoadBalancer、NodePort）
- `configmap-template.yaml` - 不同数据类型的 ConfigMap 示例
- `secret-template.yaml` - Secret 示例（应生成，不要提交）
- `pvc-template.yaml` - PersistentVolumeClaim 模板

## 参考文档

- `references/deployment-spec.md` - 详细 Deployment 规范
- `references/service-spec.md` - Service 类型和网络详情

## 最佳实践总结

1. **始终设置资源请求和限制** - 防止资源饥饿
2. **实现健康检查** - 确保 Kubernetes 可以管理你的应用
3. **使用特定的镜像标签** - 避免不可预测的部署
4. **应用安全上下文** - 以非 root 运行，丢弃能力
5. **使用 ConfigMap 和 Secret** - 将配置与代码分离
6. **为所有资源添加标签** - 启用过滤和组织
7. **遵循命名约定** - 使用标准 Kubernetes 标签
8. **应用前验证** - 使用试运行和验证工具
9. **对清单进行版本控制** - 保存在 Git 中进行版本管理
10. **使用注解记录** - 为其他开发者添加上下文

## 故障排除

**Pod 未启动：**

- 检查镜像拉取错误：`kubectl describe pod <pod-name>`
- 验证资源可用性：`kubectl get nodes`
- 检查事件：`kubectl get events --sort-by='.lastTimestamp'`

**Service 无法访问：**

- 验证选择器匹配 Pod 标签：`kubectl get endpoints <service-name>`
- 检查 Service 类型和端口配置
- 从集群内测试：`kubectl run debug --rm -it --image=busybox -- sh`

**ConfigMap/Secret 未加载：**

- 验证 Deployment 中的名称匹配
- 检查命名空间
- 确保资源存在：`kubectl get configmap,secret`

## 后续步骤

创建清单后：

1. 存储在 Git 仓库中
2. 设置 CI/CD 管道进行部署
3. 考虑使用 Helm 或 Kustomize 进行模板化
4. 使用 ArgoCD 或 Flux 实现 GitOps
5. 添加监控和可观测性

## 相关技能

- `helm-chart-scaffolding` - 用于模板化和打包
- `gitops-workflow` - 用于自动化部署
- `k8s-security-policies` - 用于高级安全配置
