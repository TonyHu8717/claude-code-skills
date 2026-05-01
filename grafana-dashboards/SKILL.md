---
name: grafana-dashboards
description: 创建和管理生产级 Grafana 仪表板，用于系统和应用指标的实时可视化。在构建监控仪表板、可视化指标或创建运维可观测性界面时使用。
---

# Grafana 仪表板

创建和管理生产就绪的 Grafana 仪表板，用于全面的系统可观测性。

## 目的

为监控应用、基础设施和业务指标设计有效的 Grafana 仪表板。

## 何时使用

- 可视化 Prometheus 指标
- 创建自定义仪表板
- 实现 SLO 仪表板
- 监控基础设施
- 跟踪业务 KPI

## 仪表板设计原则

### 1. 信息层级

```
┌─────────────────────────────────────┐
│  关键指标（大数字）                  │
├─────────────────────────────────────┤
│  关键趋势（时间序列）                │
├─────────────────────────────────────┤
│  详细指标（表格/热力图）             │
└─────────────────────────────────────┘
```

### 2. RED 方法（服务）

- **Rate（速率）** - 每秒请求数
- **Errors（错误）** - 错误率
- **Duration（时长）** - 延迟/响应时间

### 3. USE 方法（资源）

- **Utilization（利用率）** - 资源忙碌时间百分比
- **Saturation（饱和度）** - 队列长度/等待时间
- **Errors（错误）** - 错误计数

## 仪表板结构

### API 监控仪表板

```json
{
  "dashboard": {
    "title": "API Monitoring",
    "tags": ["api", "production"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "Error Rate %",
        "type": "graph",
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
            "legendFormat": "Error Rate"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [5], "type": "gt" },
              "operator": { "type": "and" },
              "query": { "params": ["A", "5m", "now"] },
              "type": "query"
            }
          ]
        },
        "gridPos": { "x": 12, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "P95 Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 8, "w": 24, "h": 8 }
      }
    ]
  }
}
```

**参考：** 见 `assets/api-dashboard.json`

## 面板类型

### 1. 统计面板（单值）

```json
{
  "type": "stat",
  "title": "Total Requests",
  "targets": [
    {
      "expr": "sum(http_requests_total)"
    }
  ],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "orientation": "auto",
    "textMode": "auto",
    "colorMode": "value"
  },
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": 0, "color": "green" },
          { "value": 80, "color": "yellow" },
          { "value": 90, "color": "red" }
        ]
      }
    }
  }
}
```

### 2. 时间序列图

```json
{
  "type": "graph",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
    }
  ],
  "yaxes": [
    { "format": "percent", "max": 100, "min": 0 },
    { "format": "short" }
  ]
}
```

### 3. 表格面板

```json
{
  "type": "table",
  "title": "Service Status",
  "targets": [
    {
      "expr": "up",
      "format": "table",
      "instant": true
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": { "Time": true },
        "indexByName": {},
        "renameByName": {
          "instance": "Instance",
          "job": "Service",
          "Value": "Status"
        }
      }
    }
  ]
}
```

### 4. 热力图

```json
{
  "type": "heatmap",
  "title": "Latency Heatmap",
  "targets": [
    {
      "expr": "sum(rate(http_request_duration_seconds_bucket[5m])) by (le)",
      "format": "heatmap"
    }
  ],
  "dataFormat": "tsbuckets",
  "yAxis": {
    "format": "s"
  }
}
```

## 变量

### 查询变量

```json
{
  "templating": {
    "list": [
      {
        "name": "namespace",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_pod_info, namespace)",
        "refresh": 1,
        "multi": false
      },
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_service_info{namespace=\"$namespace\"}, service)",
        "refresh": 1,
        "multi": true
      }
    ]
  }
}
```

### 在查询中使用变量

```
sum(rate(http_requests_total{namespace="$namespace", service=~"$service"}[5m]))
```

## 仪表板中的告警

```json
{
  "alert": {
    "name": "High Error Rate",
    "conditions": [
      {
        "evaluator": {
          "params": [5],
          "type": "gt"
        },
        "operator": { "type": "and" },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "reducer": { "type": "avg" },
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "5m",
    "frequency": "1m",
    "message": "Error rate is above 5%",
    "noDataState": "no_data",
    "notifications": [{ "uid": "slack-channel" }]
  }
}
```

## 仪表板配置

**dashboards.yml：**

```yaml
apiVersion: 1

providers:
  - name: "default"
    orgId: 1
    folder: "General"
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
```

## 常见仪表板模式

### 基础设施仪表板

**关键面板：**

- 每节点 CPU 利用率
- 每节点内存使用率
- 磁盘 I/O
- 网络流量
- 按命名空间统计的 Pod 数量
- 节点状态

**参考：** 见 `assets/infrastructure-dashboard.json`

### 数据库仪表板

**关键面板：**

- 每秒查询数
- 连接池使用率
- 查询延迟（P50、P95、P99）
- 活跃连接数
- 数据库大小
- 复制延迟
- 慢查询

**参考：** 见 `assets/database-dashboard.json`

### 应用仪表板

**关键面板：**

- 请求速率
- 错误率
- 响应时间（百分位数）
- 活跃用户/会话
- 缓存命中率
- 队列长度

## 最佳实践

1. **从模板开始**（Grafana 社区仪表板）
2. **使用一致的命名** 为面板和变量
3. **将相关指标分组** 到行中
4. **设置合适的时间范围**（默认：最近 6 小时）
5. **使用变量** 以获得灵活性
6. **添加面板描述** 提供上下文
7. **正确配置单位**
8. **设置有意义的阈值** 用于颜色显示
9. **跨仪表板使用一致的颜色**
10. **用不同时间范围测试**

## 仪表板即代码

### Terraform 配置

```hcl
resource "grafana_dashboard" "api_monitoring" {
  config_json = file("${path.module}/dashboards/api-monitoring.json")
  folder      = grafana_folder.monitoring.id
}

resource "grafana_folder" "monitoring" {
  title = "Production Monitoring"
}
```

### Ansible 配置

```yaml
- name: Deploy Grafana dashboards
  copy:
    src: "{{ item }}"
    dest: /etc/grafana/dashboards/
  with_fileglob:
    - "dashboards/*.json"
  notify: restart grafana
```


## 相关技能

- `prometheus-configuration` - 用于指标收集
- `slo-implementation` - 用于 SLO 仪表板
