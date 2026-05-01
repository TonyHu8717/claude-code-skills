---
name: prometheus-configuration
description: 设置 Prometheus 以全面收集、存储和监控基础设施和应用程序的指标。在实现指标收集、设置监控基础设施或配置告警系统时使用。
---

# Prometheus 配置

Prometheus 设置、指标收集、抓取配置和记录规则的完整指南。

## 用途

配置 Prometheus 以全面收集指标、告警和监控基础设施和应用程序。

## 何时使用

- 设置 Prometheus 监控
- 配置指标抓取
- 创建记录规则
- 设计告警规则
- 实现服务发现

## Prometheus 架构

```
┌──────────────┐
│ Applications │ ← Instrumented with client libraries
└──────┬───────┘
       │ /metrics endpoint
       ↓
┌──────────────┐
│  Prometheus  │ ← Scrapes metrics periodically
│    Server    │
└──────┬───────┘
       │
       ├─→ AlertManager (alerts)
       ├─→ Grafana (visualization)
       └─→ Long-term storage (Thanos/Cortex)
```

## 安装

### Kubernetes with Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageVolumeSize=50Gi
```

### Docker Compose

```yaml
version: "3.8"
services:
  prometheus:
    image: prom/prometheus:v3.2
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=30d"

volumes:
  prometheus-data:
```

## 配置文件

**prometheus.yml：**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "production"
    region: "us-west-2"

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules files
rule_files:
  - /etc/prometheus/rules/*.yml

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # Node exporters
  - job_name: "node-exporter"
    static_configs:
      - targets:
          - "node1:9100"
          - "node2:9100"
          - "node3:9100"
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: "([^:]+)(:[0-9]+)?"
        replacement: "${1}"

  # Kubernetes pods with annotations
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels:
          [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: pod

  # Application metrics
  - job_name: "my-app"
    static_configs:
      - targets:
          - "app1.example.com:9090"
          - "app2.example.com:9090"
    metrics_path: "/metrics"
    scheme: "https"
    tls_config:
      ca_file: /etc/prometheus/ca.crt
      cert_file: /etc/prometheus/client.crt
      key_file: /etc/prometheus/client.key
```

**参考：** 查看 `assets/prometheus.yml.template`

## 抓取配置

### 静态目标

```yaml
scrape_configs:
  - job_name: "static-targets"
    static_configs:
      - targets: ["host1:9100", "host2:9100"]
        labels:
          env: "production"
          region: "us-west-2"
```

### 基于文件的服务发现

```yaml
scrape_configs:
  - job_name: "file-sd"
    file_sd_configs:
      - files:
          - /etc/prometheus/targets/*.json
          - /etc/prometheus/targets/*.yml
        refresh_interval: 5m
```

**targets/production.json：**

```json
[
  {
    "targets": ["app1:9090", "app2:9090"],
    "labels": {
      "env": "production",
      "service": "api"
    }
  }
]
```

### Kubernetes 服务发现

```yaml
scrape_configs:
  - job_name: "kubernetes-services"
    kubernetes_sd_configs:
      - role: service
    relabel_configs:
      - source_labels:
          [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels:
          [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

**参考：** 查看 `references/scrape-configs.md`

## 记录规则

为频繁查询的表达式创建预计算指标：

```yaml
# /etc/prometheus/rules/recording_rules.yml
groups:
  - name: api_metrics
    interval: 15s
    rules:
      # HTTP request rate per service
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))

      # Error rate percentage
      - record: job:http_requests_errors:rate5m
        expr: sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))

      - record: job:http_requests_error_rate:percentage
        expr: |
          (job:http_requests_errors:rate5m / job:http_requests:rate5m) * 100

      # P95 latency
      - record: job:http_request_duration:p95
        expr: |
          histogram_quantile(0.95,
            sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
          )

  - name: resource_metrics
    interval: 30s
    rules:
      # CPU utilization percentage
      - record: instance:node_cpu:utilization
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

      # Memory utilization percentage
      - record: instance:node_memory:utilization
        expr: |
          100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)

      # Disk usage percentage
      - record: instance:node_disk:utilization
        expr: |
          100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)
```

**参考：** 查看 `references/recording-rules.md`

## 告警规则

```yaml
# /etc/prometheus/rules/alert_rules.yml
groups:
  - name: availability
    interval: 30s
    rules:
      - alert: ServiceDown
        expr: up{job="my-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "{{ $labels.job }} has been down for more than 1 minute"

      - alert: HighErrorRate
        expr: job:http_requests_error_rate:percentage > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate for {{ $labels.job }}"
          description: "Error rate is {{ $value }}% (threshold: 5%)"

      - alert: HighLatency
        expr: job:http_request_duration:p95 > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency for {{ $labels.job }}"
          description: "P95 latency is {{ $value }}s (threshold: 1s)"

  - name: resources
    interval: 1m
    rules:
      - alert: HighCPUUsage
        expr: instance:node_cpu:utilization > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}%"

      - alert: HighMemoryUsage
        expr: instance:node_memory:utilization > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value }}%"

      - alert: DiskSpaceLow
        expr: instance:node_disk:utilization > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is {{ $value }}%"
```

## 验证

```bash
# Validate configuration
promtool check config prometheus.yml

# Validate rules
promtool check rules /etc/prometheus/rules/*.yml

# Test query
promtool query instant http://localhost:9090 'up'
```

**参考：** 查看 `scripts/validate-prometheus.sh`

## 最佳实践

1. **使用一致的命名** 用于指标（prefix_name_unit）
2. **设置适当的抓取间隔**（通常 15-60 秒）
3. **使用记录规则** 用于昂贵的查询
4. **实现高可用性**（多个 Prometheus 实例）
5. **根据存储容量配置保留期**
6. **使用重新标记** 进行指标清理
7. **监控 Prometheus 本身**
8. **实现联邦** 用于大型部署
9. **使用 Thanos/Cortex** 进行长期存储
10. **记录自定义指标**

## 故障排除

**检查抓取目标：**

```bash
curl http://localhost:9090/api/v1/targets
```

**检查配置：**

```bash
curl http://localhost:9090/api/v1/status/config
```

**测试查询：**

```bash
curl 'http://localhost:9090/api/v1/query?query=up'
```


## 相关技能

- `grafana-dashboards` - 用于可视化
- `slo-implementation` - 用于 SLO 监控
- `distributed-tracing` - 用于请求追踪
