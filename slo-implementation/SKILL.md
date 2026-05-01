---
name: slo-implementation
description: 定义和实现服务水平指标（SLI）和服务水平目标（SLO），包含错误预算和告警。在建立可靠性目标、实现 SRE 实践或衡量服务性能时使用。
---

# SLO 实现

定义和实现服务水平指标（SLI）、服务水平目标（SLO）和错误预算的框架。

## 目的

使用 SLI、SLO 和错误预算实现可衡量的可靠性目标，以平衡可靠性与创新速度。

## 何时使用

- 定义服务可靠性目标
- 衡量用户感知的可靠性
- 实现错误预算
- 创建基于 SLO 的告警
- 跟踪可靠性目标

## SLI/SLO/SLA 层次结构

```
SLA（服务水平协议）
  ↓ 与客户的合同
SLO（服务水平目标）
  ↓ 内部可靠性目标
SLI（服务水平指标）
  ↓ 实际测量
```

## 定义 SLI

### 常见 SLI 类型

#### 1. 可用性 SLI

```promql
# 成功请求 / 总请求
sum(rate(http_requests_total{status!~"5.."}[28d]))
/
sum(rate(http_requests_total[28d]))
```

#### 2. 延迟 SLI

```promql
# 低于延迟阈值的请求 / 总请求
sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
/
sum(rate(http_request_duration_seconds_count[28d]))
```

#### 3. 持久性 SLI

```
# 成功写入 / 总写入
sum(storage_writes_successful_total)
/
sum(storage_writes_total)
```

**参考：**参见 `references/slo-definitions.md`

## 设置 SLO 目标

### 可用性 SLO 示例

| SLO %  | 每月停机时间 | 每年停机时间 |
| ------ | ------------ | ------------ |
| 99%    | 7.2 小时     | 3.65 天      |
| 99.9%  | 43.2 分钟    | 8.76 小时    |
| 99.95% | 21.6 分钟    | 4.38 小时    |
| 99.99% | 4.32 分钟    | 52.56 分钟   |

### 选择适当的 SLO

**考虑因素：**

- 用户期望
- 业务需求
- 当前性能
- 可靠性成本
- 竞争对手基准

**SLO 示例：**

```yaml
slos:
  - name: api_availability
    target: 99.9
    window: 28d
    sli: |
      sum(rate(http_requests_total{status!~"5.."}[28d]))
      /
      sum(rate(http_requests_total[28d]))

  - name: api_latency_p95
    target: 99
    window: 28d
    sli: |
      sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
      /
      sum(rate(http_request_duration_seconds_count[28d]))
```

## 错误预算计算

### 错误预算公式

```
错误预算 = 1 - SLO 目标
```

**示例：**

- SLO：99.9% 可用性
- 错误预算：0.1% = 43.2 分钟/月
- 当前错误：0.05% = 21.6 分钟/月
- 剩余预算：50%

### 错误预算策略

```yaml
error_budget_policy:
  - remaining_budget: 100%
    action: 正常开发速度
  - remaining_budget: 50%
    action: 考虑推迟有风险的变更
  - remaining_budget: 10%
    action: 冻结非关键变更
  - remaining_budget: 0%
    action: 功能冻结，专注于可靠性
```

**参考：**参见 `references/error-budget.md`

## SLO 实现

### Prometheus 记录规则

```yaml
# SLI 记录规则
groups:
  - name: sli_rules
    interval: 30s
    rules:
      # 可用性 SLI
      - record: sli:http_availability:ratio
        expr: |
          sum(rate(http_requests_total{status!~"5.."}[28d]))
          /
          sum(rate(http_requests_total[28d]))

      # 延迟 SLI（请求 < 500ms）
      - record: sli:http_latency:ratio
        expr: |
          sum(rate(http_request_duration_seconds_bucket{le="0.5"}[28d]))
          /
          sum(rate(http_request_duration_seconds_count[28d]))

  - name: slo_rules
    interval: 5m
    rules:
      # SLO 合规性（1 = 满足 SLO，0 = 违反）
      - record: slo:http_availability:compliance
        expr: sli:http_availability:ratio >= bool 0.999

      - record: slo:http_latency:compliance
        expr: sli:http_latency:ratio >= bool 0.99

      # 错误预算剩余（百分比）
      - record: slo:http_availability:error_budget_remaining
        expr: |
          (sli:http_availability:ratio - 0.999) / (1 - 0.999) * 100

      # 错误预算消耗速率
      - record: slo:http_availability:burn_rate_5m
        expr: |
          (1 - (
            sum(rate(http_requests_total{status!~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          )) / (1 - 0.999)
```

### SLO 告警规则

```yaml
groups:
  - name: slo_alerts
    interval: 1m
    rules:
      # 快速消耗：14.4 倍速率，1 小时窗口
      # 1 小时内消耗 2% 错误预算
      - alert: SLOErrorBudgetBurnFast
        expr: |
          slo:http_availability:burn_rate_1h > 14.4
          and
          slo:http_availability:burn_rate_5m > 14.4
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "检测到快速错误预算消耗"
          description: "错误预算以 {{ $value }} 倍速率消耗"

      # 慢速消耗：6 倍速率，6 小时窗口
      # 6 小时内消耗 5% 错误预算
      - alert: SLOErrorBudgetBurnSlow
        expr: |
          slo:http_availability:burn_rate_6h > 6
          and
          slo:http_availability:burn_rate_30m > 6
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "检测到慢速错误预算消耗"
          description: "错误预算以 {{ $value }} 倍速率消耗"

      # 错误预算耗尽
      - alert: SLOErrorBudgetExhausted
        expr: slo:http_availability:error_budget_remaining < 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SLO 错误预算已耗尽"
          description: "错误预算剩余：{{ $value }}%"
```

## SLO 仪表板

**Grafana 仪表板结构：**

```
┌────────────────────────────────────┐
│ SLO 合规性（当前）                  │
│ ✓ 99.95%（目标：99.9%）            │
├────────────────────────────────────┤
│ 错误预算剩余：65%                  │
│ ████████░░ 65%                     │
├────────────────────────────────────┤
│ SLI 趋势（28 天）                  │
│ [时间序列图]                       │
├────────────────────────────────────┤
│ 消耗速率分析                       │
│ [按时间窗口的消耗速率]             │
└────────────────────────────────────┘
```

**示例查询：**

```promql
# 当前 SLO 合规性
sli:http_availability:ratio * 100

# 错误预算剩余
slo:http_availability:error_budget_remaining

# 错误预算耗尽前的天数（按当前消耗速率）
(slo:http_availability:error_budget_remaining / 100)
*
28
/
(1 - sli:http_availability:ratio) * (1 - 0.999)
```

## 多窗口消耗速率告警

```yaml
# 短窗口和长窗口的组合减少误报
rules:
  - alert: SLOBurnRateHigh
    expr: |
      (
        slo:http_availability:burn_rate_1h > 14.4
        and
        slo:http_availability:burn_rate_5m > 14.4
      )
      or
      (
        slo:http_availability:burn_rate_6h > 6
        and
        slo:http_availability:burn_rate_30m > 6
      )
    labels:
      severity: critical
```

## SLO 审查流程

### 每周审查

- 当前 SLO 合规性
- 错误预算状态
- 趋势分析
- 事件影响

### 每月审查

- SLO 达成情况
- 错误预算使用情况
- 事件事后分析
- SLO 调整

### 季度审查

- SLO 相关性
- 目标调整
- 流程改进
- 工具增强

## 最佳实践

1. **从面向用户的服务开始**
2. **使用多个 SLI**（可用性、延迟等）
3. **设置可实现的 SLO**（不要追求 100%）
4. **实现多窗口告警**以减少噪声
5. **持续跟踪错误预算**
6. **定期审查 SLO**
7. **记录 SLO 决策**
8. **与业务目标对齐**
9. **自动化 SLO 报告**
10. **使用 SLO 进行优先级排序**


## 相关技能

- `prometheus-configuration` - 用于指标收集
- `grafana-dashboards` - 用于 SLO 可视化
