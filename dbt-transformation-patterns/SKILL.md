---
name: dbt-transformation-patterns
description: 掌握 dbt（数据构建工具）用于分析工程，包括模型组织、测试、文档和增量策略。在构建数据转换、创建数据模型或实施分析工程最佳实践时使用。
---

# dbt 转换模式

dbt（数据构建工具）的生产就绪模式，包括模型组织、测试策略、文档和增量处理。

## 使用场景

- 使用 dbt 构建数据转换管道
- 将模型组织为 staging、intermediate 和 marts 层
- 实施数据质量测试
- 为大型数据集创建增量模型
- 记录数据模型和血缘关系
- 设置 dbt 项目结构

## 核心概念

### 1. 模型层（奖牌架构）

```
sources/          原始数据定义
    ↓
staging/          与源 1:1 对应，轻度清洗
    ↓
intermediate/     业务逻辑、连接、聚合
    ↓
marts/            最终分析表
```

### 2. 命名规范

| 层        | 前缀         | 示例                       |
| ------------ | -------------- | ----------------------------- |
| Staging      | `stg_`         | `stg_stripe__payments`        |
| Intermediate | `int_`         | `int_payments_pivoted`        |
| Marts        | `dim_`, `fct_` | `dim_customers`, `fct_orders` |

## 快速开始

```yaml
# dbt_project.yml
name: "analytics"
version: "1.0.0"
profile: "analytics"

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

vars:
  start_date: "2020-01-01"

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: analytics
```

```
# 项目结构
models/
├── staging/
│   ├── stripe/
│   │   ├── _stripe__sources.yml
│   │   ├── _stripe__models.yml
│   │   ├── stg_stripe__customers.sql
│   │   └── stg_stripe__payments.sql
│   └── shopify/
│       ├── _shopify__sources.yml
│       └── stg_shopify__orders.sql
├── intermediate/
│   └── finance/
│       └── int_payments_pivoted.sql
└── marts/
    ├── core/
    │   ├── _core__models.yml
    │   ├── dim_customers.sql
    │   └── fct_orders.sql
    └── finance/
        └── fct_revenue.sql
```

## 模式

### 模式 1：源定义

```yaml
# models/staging/stripe/_stripe__sources.yml
version: 2

sources:
  - name: stripe
    description: 通过 Fivetran 加载的原始 Stripe 数据
    database: raw
    schema: stripe
    loader: fivetran
    loaded_at_field: _fivetran_synced
    freshness:
      warn_after: { count: 12, period: hour }
      error_after: { count: 24, period: hour }
    tables:
      - name: customers
        description: Stripe 客户记录
        columns:
          - name: id
            description: 主键
            tests:
              - unique
              - not_null
          - name: email
            description: 客户邮箱
          - name: created
            description: 账户创建时间戳

      - name: payments
        description: Stripe 支付交易
        columns:
          - name: id
            tests:
              - unique
              - not_null
          - name: customer_id
            tests:
              - not_null
              - relationships:
                  to: source('stripe', 'customers')
                  field: id
```

### 模式 2：Staging 模型

```sql
-- models/staging/stripe/stg_stripe__customers.sql
with source as (
    select * from {{ source('stripe', 'customers') }}
),

renamed as (
    select
        -- ids
        id as customer_id,

        -- 字符串
        lower(email) as email,
        name as customer_name,

        -- 时间戳
        created as created_at,

        -- 元数据
        _fivetran_synced as _loaded_at

    from source
)

select * from renamed
```

```sql
-- models/staging/stripe/stg_stripe__payments.sql
{{
    config(
        materialized='incremental',
        unique_key='payment_id',
        on_schema_change='append_new_columns'
    )
}}

with source as (
    select * from {{ source('stripe', 'payments') }}

    {% if is_incremental() %}
    where _fivetran_synced > (select max(_loaded_at) from {{ this }})
    {% endif %}
),

renamed as (
    select
        -- ids
        id as payment_id,
        customer_id,
        invoice_id,

        -- 金额（分转换为元）
        amount / 100.0 as amount,
        amount_refunded / 100.0 as amount_refunded,

        -- 状态
        status as payment_status,

        -- 时间戳
        created as created_at,

        -- 元数据
        _fivetran_synced as _loaded_at

    from source
)

select * from renamed
```

### 模式 3：Intermediate 模型

```sql
-- models/intermediate/finance/int_payments_pivoted_to_customer.sql
with payments as (
    select * from {{ ref('stg_stripe__payments') }}
),

customers as (
    select * from {{ ref('stg_stripe__customers') }}
),

payment_summary as (
    select
        customer_id,
        count(*) as total_payments,
        count(case when payment_status = 'succeeded' then 1 end) as successful_payments,
        sum(case when payment_status = 'succeeded' then amount else 0 end) as total_amount_paid,
        min(created_at) as first_payment_at,
        max(created_at) as last_payment_at
    from payments
    group by customer_id
)

select
    customers.customer_id,
    customers.email,
    customers.created_at as customer_created_at,
    coalesce(payment_summary.total_payments, 0) as total_payments,
    coalesce(payment_summary.successful_payments, 0) as successful_payments,
    coalesce(payment_summary.total_amount_paid, 0) as lifetime_value,
    payment_summary.first_payment_at,
    payment_summary.last_payment_at

from customers
left join payment_summary using (customer_id)
```

### 模式 4：Mart 模型（维度和事实）

```sql
-- models/marts/core/dim_customers.sql
{{
    config(
        materialized='table',
        unique_key='customer_id'
    )
}}

with customers as (
    select * from {{ ref('int_payments_pivoted_to_customer') }}
),

orders as (
    select * from {{ ref('stg_shopify__orders') }}
),

order_summary as (
    select
        customer_id,
        count(*) as total_orders,
        sum(total_price) as total_order_value,
        min(created_at) as first_order_at,
        max(created_at) as last_order_at
    from orders
    group by customer_id
),

final as (
    select
        -- 代理键
        {{ dbt_utils.generate_surrogate_key(['customers.customer_id']) }} as customer_key,

        -- 自然键
        customers.customer_id,

        -- 属性
        customers.email,
        customers.customer_created_at,

        -- 支付指标
        customers.total_payments,
        customers.successful_payments,
        customers.lifetime_value,
        customers.first_payment_at,
        customers.last_payment_at,

        -- 订单指标
        coalesce(order_summary.total_orders, 0) as total_orders,
        coalesce(order_summary.total_order_value, 0) as total_order_value,
        order_summary.first_order_at,
        order_summary.last_order_at,

        -- 计算字段
        case
            when customers.lifetime_value >= 1000 then 'high'
            when customers.lifetime_value >= 100 then 'medium'
            else 'low'
        end as customer_tier,

        -- 时间戳
        current_timestamp as _loaded_at

    from customers
    left join order_summary using (customer_id)
)

select * from final
```

```sql
-- models/marts/core/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge'
    )
}}

with orders as (
    select * from {{ ref('stg_shopify__orders') }}

    {% if is_incremental() %}
    where updated_at > (select max(updated_at) from {{ this }})
    {% endif %}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

final as (
    select
        -- 键
        orders.order_id,
        customers.customer_key,
        orders.customer_id,

        -- 维度
        orders.order_status,
        orders.fulfillment_status,
        orders.payment_status,

        -- 度量
        orders.subtotal,
        orders.tax,
        orders.shipping,
        orders.total_price,
        orders.total_discount,
        orders.item_count,

        -- 时间戳
        orders.created_at,
        orders.updated_at,
        orders.fulfilled_at,

        -- 元数据
        current_timestamp as _loaded_at

    from orders
    left join customers on orders.customer_id = customers.customer_id
)

select * from final
```

### 模式 5：测试和文档

```yaml
# models/marts/core/_core__models.yml
version: 2

models:
  - name: dim_customers
    description: 包含支付和订单指标的客户维度
    columns:
      - name: customer_key
        description: 客户维度的代理键
        tests:
          - unique
          - not_null

      - name: customer_id
        description: 来自源系统的自然键
        tests:
          - unique
          - not_null

      - name: email
        description: 客户邮箱地址
        tests:
          - not_null

      - name: customer_tier
        description: 基于生命周期价值的客户价值层级
        tests:
          - accepted_values:
              values: ["high", "medium", "low"]

      - name: lifetime_value
        description: 客户支付总额
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"

  - name: fct_orders
    description: 包含所有订单交易的事实表
    tests:
      - dbt_utils.recency:
          datepart: day
          field: created_at
          interval: 1
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_key
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_key
```

### 模式 6：宏和 DRY 代码

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    round({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}

-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name }}
    {%- endif -%}
{% endmacro %}

-- macros/limit_data_in_dev.sql
{% macro limit_data_in_dev(column_name, days=3) %}
    {% if target.name == 'dev' %}
        where {{ column_name }} >= dateadd(day, -{{ days }}, current_date)
    {% endif %}
{% endmacro %}

-- 在模型中的用法
select * from {{ ref('stg_orders') }}
{{ limit_data_in_dev('created_at') }}
```

### 模式 7：增量策略

```sql
-- Delete+Insert（大多数仓库的默认策略）
{{
    config(
        materialized='incremental',
        unique_key='id',
        incremental_strategy='delete+insert'
    )
}}

-- Merge（最适合迟到数据）
{{
    config(
        materialized='incremental',
        unique_key='id',
        incremental_strategy='merge',
        merge_update_columns=['status', 'amount', 'updated_at']
    )
}}

-- Insert Overwrite（基于分区）
{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        partition_by={
            "field": "created_date",
            "data_type": "date",
            "granularity": "day"
        }
    )
}}

select
    *,
    date(created_at) as created_date
from {{ ref('stg_events') }}

{% if is_incremental() %}
where created_date >= dateadd(day, -3, current_date)
{% endif %}
```

## dbt 命令

```bash
# 开发
dbt run                          # 运行所有模型
dbt run --select staging         # 仅运行 staging 模型
dbt run --select +fct_orders     # 运行 fct_orders 及其上游
dbt run --select fct_orders+     # 运行 fct_orders 及其下游
dbt run --full-refresh           # 重建增量模型

# 测试
dbt test                         # 运行所有测试
dbt test --select stg_stripe     # 测试特定模型
dbt build                        # 按 DAG 顺序运行 + 测试

# 文档
dbt docs generate                # 生成文档
dbt docs serve                   # 本地提供文档

# 调试
dbt compile                      # 编译 SQL 但不运行
dbt debug                        # 测试连接
dbt ls --select tag:critical     # 按标签列出模型
```

## 最佳实践

### 应该做

- **使用 staging 层** - 清洗一次，到处使用
- **积极测试** - 非空、唯一、关系
- **记录一切** - 列描述、模型描述
- **使用增量** - 适用于超过 100 万行的表
- **版本控制** - dbt 项目放在 Git 中

### 不应该做

- **不要跳过 staging** - 原始→mart 是技术债务
- **不要硬编码日期** - 使用 `{{ var('start_date') }}`
- **不要重复逻辑** - 提取为宏
- **不要在生产中测试** - 使用 dev 目标
- **不要忽略新鲜度** - 监控源数据
