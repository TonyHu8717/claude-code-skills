---
name: kpi-dashboard-design
description: 设计有效的 KPI 仪表板，包括指标选择、可视化最佳实践和实时监控模式。在构建跟踪 MRR、流失率和 LTV/CAC 比率的高管 SaaS 指标仪表板、设计具有实时服务健康和请求吞吐量的运营中心、为产品团队创建队列留存分析视图，或调试因计算方法不一致导致指标矛盾的仪表板时使用此技能。
---

# KPI 仪表板设计

设计有效的关键绩效指标（KPI）仪表板的综合模式，以驱动业务决策。

## 何时使用此技能

- 设计高管仪表板
- 选择有意义的 KPI
- 构建实时监控显示
- 创建部门特定的指标视图
- 改进现有仪表板布局
- 建立指标治理

## 核心概念

### 1. KPI 框架

| 层级            | 关注点           | 更新频率          | 受众       |
| --------------- | ---------------- | ----------------- | ---------- |
| **战略级**      | 长期目标         | 月度/季度         | 高管       |
| **战术级**      | 部门目标         | 周/月             | 经理       |
| **运营级**      | 日常运营         | 实时/每日         | 团队       |

### 2. SMART KPI

```
具体（Specific）：清晰的定义
可衡量（Measurable）：可量化
可实现（Achievable）：现实的目标
相关性（Relevant）：与目标对齐
时限性（Time-bound）：定义的时间段
```

### 3. 仪表板层级

```
├── 高管摘要（1 页）
│   ├── 4-6 个关键 KPI
│   ├── 趋势指标
│   └── 关键告警
├── 部门视图
│   ├── 销售仪表板
│   ├── 市场仪表板
│   ├── 运营仪表板
│   └── 财务仪表板
└── 详细下钻
    ├── 单个指标
    └── 根因分析
```

## 按部门划分的常见 KPI

### 销售 KPI

```yaml
收入指标：
  - 月度经常性收入（MRR）
  - 年度经常性收入（ARR）
  - 每用户平均收入（ARPU）
  - 收入增长率

管道指标：
  - 销售管道价值
  - 赢单率
  - 平均交易规模
  - 销售周期长度

活动指标：
  - 每位销售的通话/邮件数
  - 安排的演示
  - 发送的提案
  - 关单率
```

### 市场 KPI

```yaml
获客：
  - 每次获客成本（CPA）
  - 客户获取成本（CAC）
  - 线索量
  - 市场合格线索（MQL）

参与度：
  - 网站流量
  - 转化率
  - 邮件打开/点击率
  - 社交参与度

ROI：
  - 市场 ROI
  - 活动绩效
  - 渠道归因
  - CAC 回收期
```

### 产品 KPI

```yaml
使用情况：
  - 日活/月活用户（DAU/MAU）
  - 会话时长
  - 功能采用率
  - 粘性（DAU/MAU）

质量：
  - 净推荐值（NPS）
  - 客户满意度（CSAT）
  - Bug/问题数量
  - 解决时间

增长：
  - 用户增长率
  - 激活率
  - 留存率
  - 流失率
```

### 财务 KPI

```yaml
盈利能力：
  - 毛利率
  - 净利润率
  - EBITDA
  - 营业利润率

流动性：
  - 流动比率
  - 速动比率
  - 现金流
  - 营运资本

效率：
  - 每员工收入
  - 营业费用比率
  - 应收账款周转天数
  - 存货周转率
```

## 仪表板布局模式

### 模式 1：高管摘要

```
┌─────────────────────────────────────────────────────────────┐
│  高管仪表板                               [日期范围 ▼]       │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   收入      │   利润      │   客户      │   NPS 分数      │
│   $2.4M     │   $450K     │   12,450    │      72         │
│   ▲ 12%     │   ▲ 8%      │   ▲ 15%     │    ▲ 5pts      │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│                                                             │
│  收入趋势                       │  按产品划分的收入          │
│  ┌───────────────────────┐      │  ┌──────────────────┐    │
│  │    /\    /\          │      │  │ ████████ 45%     │    │
│  │   /  \  /  \    /\   │      │  │ ██████   32%     │    │
│  │  /    \/    \  /  \  │      │  │ ████     18%     │    │
│  │ /            \/    \ │      │  │ ██        5%     │    │
│  └───────────────────────┘      │  └──────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  🔴 告警：流失率超过阈值（>5%）                              │
│  🟡 警告：工单量高于平均值 20%                               │
└─────────────────────────────────────────────────────────────┘
```

### 模式 2：SaaS 指标仪表板

```
┌─────────────────────────────────────────────────────────────┐
│  SaaS 指标                      2024年1月  [月度 ▼]          │
├──────────────────────┬──────────────────────────────────────┤
│  ┌────────────────┐  │  MRR 增长                            │
│  │      MRR       │  │  ┌────────────────────────────────┐  │
│  │    $125,000    │  │  │                          /──   │  │
│  │     ▲ 8%       │  │  │                    /────/      │  │
│  └────────────────┘  │  │              /────/            │  │
│  ┌────────────────┐  │  │        /────/                  │  │
│  │      ARR       │  │  │   /────/                       │  │
│  │   $1,500,000   │  │  └────────────────────────────────┘  │
│  │     ▲ 15%      │  │  1  2  3  4  5  6  7  8  9  10 11 12 │
│  └────────────────┘  │                                      │
├──────────────────────┼──────────────────────────────────────┤
│  单元经济             │  队列留存                             │
│                      │                                      │
│  CAC:     $450       │  第1月: ████████████████████ 100%     │
│  LTV:     $2,700     │  第3月: █████████████████    85%      │
│  LTV/CAC: 6.0x       │  第6月: ████████████████     80%      │
│                      │  第12月: ██████████████      72%      │
│  回收期: 4个月        │                                      │
├──────────────────────┴──────────────────────────────────────┤
│  流失分析                                                   │
│  ┌──────────┬──────────┬──────────┬──────────────────────┐  │
│  │ 总流失   │ 净流失   │ 客户流失 │ 扩展                 │  │
│  │ 4.2%     │ 1.8%     │ 3.1%     │ 2.4%                 │  │
│  └──────────┴──────────┴──────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 模式 3：实时运营

```
┌─────────────────────────────────────────────────────────────┐
│  运营中心                         实时 ● 最后更新: 10:42:15  │
├────────────────────────────┬────────────────────────────────┤
│  系统健康                   │  服务状态                      │
│  ┌──────────────────────┐  │                                │
│  │   CPU    内存   磁盘  │  │  ● API 网关        健康       │
│  │   45%    72%    58%  │  │  ● 用户服务        健康       │
│  │   ███    ████   ███  │  │  ● 支付服务        降级       │
│  │   ███    ████   ███  │  │  ● 数据库          健康       │
│  │   ███    ████   ███  │  │  ● 缓存            健康       │
│  └──────────────────────┘  │                                │
├────────────────────────────┼────────────────────────────────┤
│  请求吞吐量                 │  错误率                        │
│  ┌──────────────────────┐  │  ┌──────────────────────────┐  │
│  │ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅ │  │  │ ▁▁▁▁▁▂▁▁▁▁▁▁▁▁▁▁▁▁▁▁  │  │
│  └──────────────────────┘  │  └──────────────────────────┘  │
│  当前: 12,450 req/s        │  当前: 0.02%                   │
│  峰值: 18,200 req/s        │  阈值: 1.0%                    │
├────────────────────────────┴────────────────────────────────┤
│  最近告警                                                   │
│  10:40  🟡 支付服务高延迟（p99 > 500ms）                     │
│  10:35  🟢 已解决：数据库连接池恢复                          │
│  10:22  🔴 支付服务熔断器触发                                │
└─────────────────────────────────────────────────────────────┘
```

## 实现模式

### KPI 计算的 SQL

```sql
-- 月度经常性收入（MRR）
WITH mrr_calculation AS (
    SELECT
        DATE_TRUNC('month', billing_date) AS month,
        SUM(
            CASE subscription_interval
                WHEN 'monthly' THEN amount
                WHEN 'yearly' THEN amount / 12
                WHEN 'quarterly' THEN amount / 3
            END
        ) AS mrr
    FROM subscriptions
    WHERE status = 'active'
    GROUP BY DATE_TRUNC('month', billing_date)
)
SELECT
    month,
    mrr,
    LAG(mrr) OVER (ORDER BY month) AS prev_mrr,
    (mrr - LAG(mrr) OVER (ORDER BY month)) / LAG(mrr) OVER (ORDER BY month) * 100 AS growth_pct
FROM mrr_calculation;

-- 队列留存
WITH cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', created_at) AS cohort_month
    FROM users
),
activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', event_date) AS activity_month
    FROM user_events
    WHERE event_type = 'active_session'
)
SELECT
    c.cohort_month,
    EXTRACT(MONTH FROM age(a.activity_month, c.cohort_month)) AS months_since_signup,
    COUNT(DISTINCT a.user_id) AS active_users,
    COUNT(DISTINCT a.user_id)::FLOAT / COUNT(DISTINCT c.user_id) * 100 AS retention_rate
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
    AND a.activity_month >= c.cohort_month
GROUP BY c.cohort_month, EXTRACT(MONTH FROM age(a.activity_month, c.cohort_month))
ORDER BY c.cohort_month, months_since_signup;

-- 客户获取成本（CAC）
SELECT
    DATE_TRUNC('month', acquired_date) AS month,
    SUM(marketing_spend) / NULLIF(COUNT(new_customers), 0) AS cac,
    SUM(marketing_spend) AS total_spend,
    COUNT(new_customers) AS customers_acquired
FROM (
    SELECT
        DATE_TRUNC('month', u.created_at) AS acquired_date,
        u.id AS new_customers,
        m.spend AS marketing_spend
    FROM users u
    JOIN marketing_spend m ON DATE_TRUNC('month', u.created_at) = m.month
    WHERE u.source = 'marketing'
) acquisition
GROUP BY DATE_TRUNC('month', acquired_date);
```

### Python 仪表板代码（Streamlit）

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="KPI Dashboard", layout="wide")

# 带日期筛选的头部
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Executive Dashboard")
with col2:
    date_range = st.selectbox(
        "Period",
        ["Last 7 Days", "Last 30 Days", "Last Quarter", "YTD"]
    )

# KPI 卡片
def metric_card(label, value, delta, prefix="", suffix=""):
    delta_color = "green" if delta >= 0 else "red"
    delta_arrow = "▲" if delta >= 0 else "▼"
    st.metric(
        label=label,
        value=f"{prefix}{value:,.0f}{suffix}",
        delta=f"{delta_arrow} {abs(delta):.1f}%"
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Revenue", 2400000, 12.5, prefix="$")
with col2:
    metric_card("Customers", 12450, 15.2)
with col3:
    metric_card("NPS Score", 72, 5.0)
with col4:
    metric_card("Churn Rate", 4.2, -0.8, suffix="%")

# 图表
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue Trend")
    revenue_data = pd.DataFrame({
        'Month': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Revenue': [180000, 195000, 210000, 225000, 240000, 255000,
                    270000, 285000, 300000, 315000, 330000, 345000]
    })
    fig = px.line(revenue_data, x='Month', y='Revenue',
                  line_shape='spline', markers=True)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Revenue by Product")
    product_data = pd.DataFrame({
        'Product': ['Enterprise', 'Professional', 'Starter', 'Other'],
        'Revenue': [45, 32, 18, 5]
    })
    fig = px.pie(product_data, values='Revenue', names='Product',
                 hole=0.4)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# 队列热力图
st.subheader("Cohort Retention")
cohort_data = pd.DataFrame({
    'Cohort': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'M0': [100, 100, 100, 100, 100],
    'M1': [85, 87, 84, 86, 88],
    'M2': [78, 80, 76, 79, None],
    'M3': [72, 74, 70, None, None],
    'M4': [68, 70, None, None, None],
})
fig = go.Figure(data=go.Heatmap(
    z=cohort_data.iloc[:, 1:].values,
    x=['M0', 'M1', 'M2', 'M3', 'M4'],
    y=cohort_data['Cohort'],
    colorscale='Blues',
    text=cohort_data.iloc[:, 1:].values,
    texttemplate='%{text}%',
    textfont={"size": 12},
))
fig.update_layout(height=250)
st.plotly_chart(fig, use_container_width=True)

# 告警部分
st.subheader("Alerts")
alerts = [
    {"level": "error", "message": "Churn rate exceeded threshold (>5%)"},
    {"level": "warning", "message": "Support ticket volume 20% above average"},
]
for alert in alerts:
    if alert["level"] == "error":
        st.error(f"🔴 {alert['message']}")
    elif alert["level"] == "warning":
        st.warning(f"🟡 {alert['message']}")
```

## 最佳实践

### 应该做的

- **限制在 5-7 个 KPI** - 关注重要的指标
- **显示上下文** - 对比、趋势、目标
- **使用一致的颜色** - 红色=差，绿色=好
- **启用下钻** - 从摘要到详情
- **适当更新** - 匹配指标频率

### 不应该做的

- **不要显示虚荣指标** - 关注可操作的数据
- **不要过度拥挤** - 留白有助于理解
- **不要使用 3D 图表** - 它们会扭曲感知
- **不要隐藏方法论** - 记录计算方式
- **不要忽略移动端** - 确保响应式设计

## 故障排除

### 仪表板上的 MRR 与财务数据矛盾

最常见的原因是年度计划的处理方式不一致。财务可能按日费率摊销，而仪表板则标准化为月度。统一使用单一公式，并直接在仪表板卡片上记录：

```sql
-- 在工具提示/数据字典中显示的明确公式
-- 年度计划：将合同总价值除以 12
-- 季度计划：除以 3
-- 月度计划：原样使用
CASE subscription_interval
    WHEN 'monthly'   THEN amount
    WHEN 'quarterly' THEN amount / 3.0
    WHEN 'yearly'    THEN amount / 12.0
END AS normalized_mrr
```

### 仪表板显示绿色但产品团队报告用户投诉

仪表板可能跟踪的是系统正常运行时间（滞后指标），而非面向用户的质量指标。在基础设施指标旁边添加客户感知指标：

| 基础设施（绿色） | 用户感知（添加这些） |
|---|---|
| API 正常运行时间 99.9% | P95 页面加载时间 |
| 错误率 0.1% | 任务完成率 |
| 队列深度正常 | 工单量 |

### 留存队列看起来平坦 — 队列之间没有变化

检查队列查询是否正确按注册月份分区。常见错误是使用 `created_at::date` 而非 `DATE_TRUNC('month', created_at)`，这会按天分组，产生太小的队列无法显示趋势：

```sql
-- 错误：粒度太细，队列太小
DATE_TRUNC('day', created_at) AS cohort_date

-- 正确：月度队列
DATE_TRUNC('month', created_at) AS cohort_month
```

### 实时仪表板对数据库造成压力

每 10 秒刷新一次的实时仪表板使用复杂的队列 SQL 会降低生产查询性能。通过定时任务将预聚合指标写入汇总表，将 OLAP 工作负载与 OLTP 分离，让仪表板从该表读取：

```python
# 通过 cron/Celery 每 5 分钟定时执行
def refresh_mrr_summary():
    conn.execute("""
        INSERT INTO kpi_snapshot (metric, value, snapshot_at)
        SELECT 'mrr', SUM(...), NOW()
        FROM subscriptions WHERE status = 'active'
        ON CONFLICT (metric) DO UPDATE SET value = EXCLUDED.value
    """)
```

### 告警阈值频繁触发，团队忽略它们

设置一次就再也不审查的静态阈值会导致告警疲劳。使用基于滚动平均值的动态阈值，让告警只在指标显著偏离基线时触发：

```python
# 如果当前值偏离 30 天滚动均值超过 2 个标准差则告警
def is_anomalous(current: float, history: list[float]) -> bool:
    mean = statistics.mean(history)
    stdev = statistics.stdev(history)
    return abs(current - mean) > 2 * stdev
```

## 相关技能

- `data-storytelling` - 将仪表板发现转化为驱动高管决策的叙述
