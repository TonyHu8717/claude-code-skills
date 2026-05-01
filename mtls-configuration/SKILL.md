---
name: mtls-configuration
description: 为零信任服务间通信配置双向 TLS（mTLS）。在实现零信任网络、证书管理或保护内部服务通信时使用。
---

# mTLS 配置

实现零信任服务网格通信双向 TLS 的综合指南。

## 何时使用此技能

- 实现零信任网络
- 保护服务间通信
- 证书轮换和管理
- 调试 TLS 握手问题
- 合规要求（PCI-DSS、HIPAA）
- 多集群安全通信

## 核心概念

### 1. mTLS 流程

```
┌─────────┐                              ┌─────────┐
│ Service │                              │ Service │
│    A    │                              │    B    │
└────┬────┘                              └────┬────┘
     │                                        │
┌────┴────┐      TLS 握手               ┌────┴────┐
│  Proxy  │◄───────────────────────────►│  Proxy  │
│(Sidecar)│  1. ClientHello             │(Sidecar)│
│         │  2. ServerHello + Cert      │         │
│         │  3. Client Cert             │         │
│         │  4. 验证双方证书             │         │
│         │  5. 加密通道                 │         │
└─────────┘                              └─────────┘
```

### 2. 证书层次结构

```
根 CA（自签名，长期有效）
    │
    ├── 中间 CA（集群级别）
    │       │
    │       ├── 工作负载证书（服务 A）
    │       └── 工作负载证书（服务 B）
    │
    └── 中间 CA（多集群）
            │
            └── 跨集群证书
```

## 模板

### 模板 1：Istio mTLS（严格模式）

```yaml
# 在整个网格范围启用严格 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
---
# 命名空间级别覆盖（迁移期间使用宽松模式）
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: legacy-namespace
spec:
  mtls:
    mode: PERMISSIVE
---
# 工作负载特定策略
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: payment-service
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  mtls:
    mode: STRICT
  portLevelMtls:
    8080:
      mode: STRICT
    9090:
      mode: DISABLE # 指标端口，不使用 mTLS
```

### 模板 2：Istio 目标规则用于 mTLS

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: default
  namespace: istio-system
spec:
  host: "*.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
---
# 到外部服务的 TLS
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-api
spec:
  host: api.external.com
  trafficPolicy:
    tls:
      mode: SIMPLE
      caCertificates: /etc/certs/external-ca.pem
---
# 到外部服务的双向 TLS
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: partner-api
spec:
  host: api.partner.com
  trafficPolicy:
    tls:
      mode: MUTUAL
      clientCertificate: /etc/certs/client.pem
      privateKey: /etc/certs/client-key.pem
      caCertificates: /etc/certs/partner-ca.pem
```

### 模板 3：Cert-Manager 与 Istio

```yaml
# 为 Istio 安装 cert-manager issuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: istio-ca
spec:
  ca:
    secretName: istio-ca-secret
---
# 创建 Istio CA 密钥
apiVersion: v1
kind: Secret
metadata:
  name: istio-ca-secret
  namespace: cert-manager
type: kubernetes.io/tls
data:
  tls.crt: <base64 编码的 CA 证书>
  tls.key: <base64 编码的 CA 密钥>
---
# 工作负载证书
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-service-cert
  namespace: my-namespace
spec:
  secretName: my-service-tls
  duration: 24h
  renewBefore: 8h
  issuerRef:
    name: istio-ca
    kind: ClusterIssuer
  commonName: my-service.my-namespace.svc.cluster.local
  dnsNames:
    - my-service
    - my-service.my-namespace
    - my-service.my-namespace.svc
    - my-service.my-namespace.svc.cluster.local
  usages:
    - server auth
    - client auth
```

### 模板 4：SPIFFE/SPIRE 集成

```yaml
# SPIRE 服务器配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: spire-server
  namespace: spire
data:
  server.conf: |
    server {
      bind_address = "0.0.0.0"
      bind_port = "8081"
      trust_domain = "example.org"
      data_dir = "/run/spire/data"
      log_level = "INFO"
      ca_ttl = "168h"
      default_x509_svid_ttl = "1h"
    }

    plugins {
      DataStore "sql" {
        plugin_data {
          database_type = "sqlite3"
          connection_string = "/run/spire/data/datastore.sqlite3"
        }
      }

      NodeAttestor "k8s_psat" {
        plugin_data {
          clusters = {
            "demo-cluster" = {
              service_account_allow_list = ["spire:spire-agent"]
            }
          }
        }
      }

      KeyManager "memory" {
        plugin_data {}
      }

      UpstreamAuthority "disk" {
        plugin_data {
          key_file_path = "/run/spire/secrets/bootstrap.key"
          cert_file_path = "/run/spire/secrets/bootstrap.crt"
        }
      }
    }
---
# SPIRE 代理 DaemonSet（简写）
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: spire-agent
  namespace: spire
spec:
  selector:
    matchLabels:
      app: spire-agent
  template:
    spec:
      containers:
        - name: spire-agent
          image: ghcr.io/spiffe/spire-agent:1.8.0
          volumeMounts:
            - name: spire-agent-socket
              mountPath: /run/spire/sockets
      volumes:
        - name: spire-agent-socket
          hostPath:
            path: /run/spire/sockets
            type: DirectoryOrCreate
```

### 模板 5：Linkerd mTLS（自动）

```yaml
# Linkerd 自动启用 mTLS
# 使用以下命令验证：
# linkerd viz edges deployment -n my-namespace

# 对于不使用 mTLS 的外部服务
apiVersion: policy.linkerd.io/v1beta1
kind: Server
metadata:
  name: external-api
  namespace: my-namespace
spec:
  podSelector:
    matchLabels:
      app: my-app
  port: external-api
  proxyProtocol: HTTP/1 # 或 TLS 用于透传
---
# 跳过特定端口的 TLS
apiVersion: v1
kind: Service
metadata:
  name: my-service
  annotations:
    config.linkerd.io/skip-outbound-ports: "3306" # MySQL
```

## 证书轮换

```bash
# Istio - 检查证书过期
istioctl proxy-config secret deploy/my-app -o json | \
  jq '.dynamicActiveSecrets[0].secret.tlsCertificate.certificateChain.inlineBytes' | \
  tr -d '"' | base64 -d | openssl x509 -text -noout

# 强制证书轮换
kubectl rollout restart deployment/my-app

# 检查 Linkerd 身份
linkerd identity -n my-namespace
```

## 调试 mTLS 问题

```bash
# Istio - 检查是否启用了 mTLS
istioctl authn tls-check my-service.my-namespace.svc.cluster.local

# 验证对等认证
kubectl get peerauthentication --all-namespaces

# 检查目标规则
kubectl get destinationrule --all-namespaces

# 调试 TLS 握手
istioctl proxy-config log deploy/my-app --level debug
kubectl logs deploy/my-app -c istio-proxy | grep -i tls

# Linkerd - 检查 mTLS 状态
linkerd viz edges deployment -n my-namespace
linkerd viz tap deploy/my-app --to deploy/my-backend
```

## 最佳实践

### 推荐做法

- **从 PERMISSIVE 开始** - 逐步迁移到 STRICT
- **监控证书过期** - 设置警报
- **使用短期证书** - 工作负载 24 小时或更短
- **定期轮换 CA** - 规划 CA 轮换
- **记录 TLS 错误** - 用于调试和审计

### 避免做法

- **不要禁用 mTLS** - 为了在生产环境中的便利
- **不要忽略证书过期** - 自动化轮换
- **不要使用自签名证书** - 使用正确的 CA 层次结构
- **不要跳过验证** - 验证完整链
