---
name: billing-automation
description: 构建自动化计费系统，用于循环支付、发票生成、订阅生命周期和催收管理。用于实现订阅计费、自动化发票生成或管理循环支付系统时使用。
---

# 计费自动化

掌握自动化计费系统，包括循环计费、发票生成、催收管理、按比例计费和税款计算。

## 何时使用此技能

- 实现 SaaS 订阅计费
- 自动化发票生成和交付
- 管理失败支付恢复（催收）
- 计划变更时的按比例计费
- 处理销售税、增值税和 GST
- 处理基于使用量的计费
- 管理计费周期和续订

## 核心概念

### 1. 计费周期

**常见间隔：**

- 月度（SaaS 最常见）
- 年度（长期折扣）
- 季度
- 每周
- 自定义（基于使用量、按席位）

### 2. 订阅状态

```
试用 → 活跃 → 逾期 → 已取消
              → 已暂停 → 已恢复
```

### 3. 催收管理

通过以下方式自动恢复失败支付的流程：

- 重试计划
- 客户通知
- 宽限期
- 账户限制

### 4. 按比例计费

在以下情况下调整费用：

- 周期中升级/降级
- 添加/移除席位
- 更改计费频率

## 快速开始

```python
from billing import BillingEngine, Subscription

# 初始化计费引擎
billing = BillingEngine()

# 创建订阅
subscription = billing.create_subscription(
    customer_id="cus_123",
    plan_id="plan_pro_monthly",
    billing_cycle_anchor=datetime.now(),
    trial_days=14
)

# 处理计费周期
billing.process_billing_cycle(subscription.id)
```

## 订阅生命周期管理

```python
from datetime import datetime, timedelta
from enum import Enum

class SubscriptionStatus(Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    PAUSED = "paused"

class Subscription:
    def __init__(self, customer_id, plan, billing_cycle_day=None):
        self.id = generate_id()
        self.customer_id = customer_id
        self.plan = plan
        self.status = SubscriptionStatus.TRIAL
        self.current_period_start = datetime.now()
        self.current_period_end = self.current_period_start + timedelta(days=plan.trial_days or 30)
        self.billing_cycle_day = billing_cycle_day or self.current_period_start.day
        self.trial_end = datetime.now() + timedelta(days=plan.trial_days) if plan.trial_days else None

    def start_trial(self, trial_days):
        """开始试用期。"""
        self.status = SubscriptionStatus.TRIAL
        self.trial_end = datetime.now() + timedelta(days=trial_days)
        self.current_period_end = self.trial_end

    def activate(self):
        """试用后或立即激活订阅。"""
        self.status = SubscriptionStatus.ACTIVE
        self.current_period_start = datetime.now()
        self.current_period_end = self.calculate_next_billing_date()

    def mark_past_due(self):
        """支付失败后将订阅标记为逾期。"""
        self.status = SubscriptionStatus.PAST_DUE
        # 触发催收工作流

    def cancel(self, at_period_end=True):
        """取消订阅。"""
        if at_period_end:
            self.cancel_at_period_end = True
            # 当前周期结束时取消
        else:
            self.status = SubscriptionStatus.CANCELED
            self.canceled_at = datetime.now()

    def calculate_next_billing_date(self):
        """根据间隔计算下一个计费日期。"""
        if self.plan.interval == 'month':
            return self.current_period_start + timedelta(days=30)
        elif self.plan.interval == 'year':
            return self.current_period_start + timedelta(days=365)
        elif self.plan.interval == 'week':
            return self.current_period_start + timedelta(days=7)
```

## 计费周期处理

```python
class BillingEngine:
    def process_billing_cycle(self, subscription_id):
        """处理订阅的计费。"""
        subscription = self.get_subscription(subscription_id)

        # 检查是否到期
        if datetime.now() < subscription.current_period_end:
            return

        # 生成发票
        invoice = self.generate_invoice(subscription)

        # 尝试支付
        payment_result = self.charge_customer(
            subscription.customer_id,
            invoice.total
        )

        if payment_result.success:
            # 支付成功
            invoice.mark_paid()
            subscription.advance_billing_period()
            self.send_invoice(invoice)
        else:
            # 支付失败
            subscription.mark_past_due()
            self.start_dunning_process(subscription, invoice)

    def generate_invoice(self, subscription):
        """为计费周期生成发票。"""
        invoice = Invoice(
            customer_id=subscription.customer_id,
            subscription_id=subscription.id,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end
        )

        # 添加订阅行项目
        invoice.add_line_item(
            description=subscription.plan.name,
            amount=subscription.plan.amount,
            quantity=subscription.quantity or 1
        )

        # 如果适用，添加基于使用量的费用
        if subscription.has_usage_billing:
            usage_charges = self.calculate_usage_charges(subscription)
            invoice.add_line_item(
                description="Usage charges",
                amount=usage_charges
            )

        # 计算税款
        tax = self.calculate_tax(invoice.subtotal, subscription.customer)
        invoice.tax = tax

        invoice.finalize()
        return invoice

    def charge_customer(self, customer_id, amount):
        """使用保存的支付方式向客户收费。"""
        customer = self.get_customer(customer_id)

        try:
            # 使用支付处理商收费
            charge = stripe.Charge.create(
                customer=customer.stripe_id,
                amount=int(amount * 100),  # 转换为分
                currency='usd'
            )

            return PaymentResult(success=True, transaction_id=charge.id)
        except stripe.error.CardError as e:
            return PaymentResult(success=False, error=str(e))
```

## 催收管理

```python
class DunningManager:
    """管理失败支付恢复。"""

    def __init__(self):
        self.retry_schedule = [
            {'days': 3, 'email_template': 'payment_failed_first'},
            {'days': 7, 'email_template': 'payment_failed_reminder'},
            {'days': 14, 'email_template': 'payment_failed_final'}
        ]

    def start_dunning_process(self, subscription, invoice):
        """为失败支付启动催收流程。"""
        dunning_attempt = DunningAttempt(
            subscription_id=subscription.id,
            invoice_id=invoice.id,
            attempt_number=1,
            next_retry=datetime.now() + timedelta(days=3)
        )

        # 发送初始失败通知
        self.send_dunning_email(subscription, 'payment_failed_first')

        # 安排重试
        self.schedule_retries(dunning_attempt)

    def retry_payment(self, dunning_attempt):
        """重试失败的支付。"""
        subscription = self.get_subscription(dunning_attempt.subscription_id)
        invoice = self.get_invoice(dunning_attempt.invoice_id)

        # 再次尝试支付
        result = self.charge_customer(subscription.customer_id, invoice.total)

        if result.success:
            # 支付成功
            invoice.mark_paid()
            subscription.status = SubscriptionStatus.ACTIVE
            self.send_dunning_email(subscription, 'payment_recovered')
            dunning_attempt.mark_resolved()
        else:
            # 仍然失败
            dunning_attempt.attempt_number += 1

            if dunning_attempt.attempt_number < len(self.retry_schedule):
                # 安排下次重试
                next_retry_config = self.retry_schedule[dunning_attempt.attempt_number]
                dunning_attempt.next_retry = datetime.now() + timedelta(days=next_retry_config['days'])
                self.send_dunning_email(subscription, next_retry_config['email_template'])
            else:
                # 重试次数用尽，取消订阅
                subscription.cancel(at_period_end=False)
                self.send_dunning_email(subscription, 'subscription_canceled')

    def send_dunning_email(self, subscription, template):
        """向客户发送催收通知。"""
        customer = self.get_customer(subscription.customer_id)

        email_content = self.render_template(template, {
            'customer_name': customer.name,
            'amount_due': subscription.plan.amount,
            'update_payment_url': f"https://app.example.com/billing"
        })

        send_email(
            to=customer.email,
            subject=email_content['subject'],
            body=email_content['body']
        )
```

## 按比例计费

```python
class ProrationCalculator:
    """计算计划变更的按比例费用。"""

    @staticmethod
    def calculate_proration(old_plan, new_plan, period_start, period_end, change_date):
        """计算计划变更的按比例费用。"""
        # 当前周期的天数
        total_days = (period_end - period_start).days

        # 在旧计划上使用的天数
        days_used = (change_date - period_start).days

        # 新计划剩余的天数
        days_remaining = (period_end - change_date).days

        # 计算按比例金额
        unused_amount = (old_plan.amount / total_days) * days_remaining
        new_plan_amount = (new_plan.amount / total_days) * days_remaining

        # 净费用/信用
        proration = new_plan_amount - unused_amount

        return {
            'old_plan_credit': -unused_amount,
            'new_plan_charge': new_plan_amount,
            'net_proration': proration,
            'days_used': days_used,
            'days_remaining': days_remaining
        }

    @staticmethod
    def calculate_seat_proration(current_seats, new_seats, price_per_seat, period_start, period_end, change_date):
        """计算席位变更的按比例费用。"""
        total_days = (period_end - period_start).days
        days_remaining = (period_end - change_date).days

        # 额外席位费用
        additional_seats = new_seats - current_seats
        prorated_amount = (additional_seats * price_per_seat / total_days) * days_remaining

        return {
            'additional_seats': additional_seats,
            'prorated_charge': max(0, prorated_amount),  # 周期中移除席位不退款
            'effective_date': change_date
        }
```

## 税款计算

```python
class TaxCalculator:
    """计算销售税、增值税、GST。"""

    def __init__(self):
        # 按地区划分的税率
        self.tax_rates = {
            'US_CA': 0.0725,  # 加州销售税
            'US_NY': 0.04,    # 纽约销售税
            'GB': 0.20,       # 英国增值税
            'DE': 0.19,       # 德国增值税
            'FR': 0.20,       # 法国增值税
            'AU': 0.10,       # 澳大利亚 GST
        }

    def calculate_tax(self, amount, customer):
        """计算适用税款。"""
        # 确定税务管辖区
        jurisdiction = self.get_tax_jurisdiction(customer)

        if not jurisdiction:
            return 0

        # 获取税率
        tax_rate = self.tax_rates.get(jurisdiction, 0)

        # 计算税款
        tax = amount * tax_rate

        return {
            'tax_amount': tax,
            'tax_rate': tax_rate,
            'jurisdiction': jurisdiction,
            'tax_type': self.get_tax_type(jurisdiction)
        }

    def get_tax_jurisdiction(self, customer):
        """根据客户位置确定税务管辖区。"""
        if customer.country == 'US':
            # 美国：根据客户所在州征税
            return f"US_{customer.state}"
        elif customer.country in ['GB', 'DE', 'FR']:
            # 欧盟：增值税
            return customer.country
        elif customer.country == 'AU':
            # 澳大利亚：GST
            return 'AU'
        else:
            return None

    def get_tax_type(self, jurisdiction):
        """获取管辖区的税种。"""
        if jurisdiction.startswith('US_'):
            return 'Sales Tax'
        elif jurisdiction in ['GB', 'DE', 'FR']:
            return 'VAT'
        elif jurisdiction == 'AU':
            return 'GST'
        return 'Tax'

    def validate_vat_number(self, vat_number, country):
        """验证欧盟增值税号。"""
        # 使用 VIES API 进行验证
        # 有效返回 True，否则返回 False
        pass
```

## 发票生成

```python
class Invoice:
    def __init__(self, customer_id, subscription_id=None):
        self.id = generate_invoice_number()
        self.customer_id = customer_id
        self.subscription_id = subscription_id
        self.status = 'draft'
        self.line_items = []
        self.subtotal = 0
        self.tax = 0
        self.total = 0
        self.created_at = datetime.now()

    def add_line_item(self, description, amount, quantity=1):
        """向发票添加行项目。"""
        line_item = {
            'description': description,
            'unit_amount': amount,
            'quantity': quantity,
            'total': amount * quantity
        }
        self.line_items.append(line_item)
        self.subtotal += line_item['total']

    def finalize(self):
        """完成发票并计算总额。"""
        self.total = self.subtotal + self.tax
        self.status = 'open'
        self.finalized_at = datetime.now()

    def mark_paid(self):
        """将发票标记为已支付。"""
        self.status = 'paid'
        self.paid_at = datetime.now()

    def to_pdf(self):
        """生成 PDF 发票。"""
        from reportlab.pdfgen import canvas

        # 生成 PDF
        # 包含：公司信息、客户信息、行项目、税款、总额
        pass

    def to_html(self):
        """生成 HTML 发票。"""
        template = """
        <!DOCTYPE html>
        <html>
        <head><title>Invoice #{invoice_number}</title></head>
        <body>
            <h1>Invoice #{invoice_number}</h1>
            <p>Date: {date}</p>
            <h2>Bill To:</h2>
            <p>{customer_name}<br>{customer_address}</p>
            <table>
                <tr><th>Description</th><th>Quantity</th><th>Amount</th></tr>
                {line_items}
            </table>
            <p>Subtotal: ${subtotal}</p>
            <p>Tax: ${tax}</p>
            <h3>Total: ${total}</h3>
        </body>
        </html>
        """

        return template.format(
            invoice_number=self.id,
            date=self.created_at.strftime('%Y-%m-%d'),
            customer_name=self.customer.name,
            customer_address=self.customer.address,
            line_items=self.render_line_items(),
            subtotal=self.subtotal,
            tax=self.tax,
            total=self.total
        )
```

## 基于使用量的计费

```python
class UsageBillingEngine:
    """跟踪和计费使用量。"""

    def track_usage(self, customer_id, metric, quantity):
        """跟踪使用事件。"""
        UsageRecord.create(
            customer_id=customer_id,
            metric=metric,
            quantity=quantity,
            timestamp=datetime.now()
        )

    def calculate_usage_charges(self, subscription, period_start, period_end):
        """计算计费周期内的使用费用。"""
        usage_records = UsageRecord.get_for_period(
            subscription.customer_id,
            period_start,
            period_end
        )

        total_usage = sum(record.quantity for record in usage_records)

        # 阶梯定价
        if subscription.plan.pricing_model == 'tiered':
            charge = self.calculate_tiered_pricing(total_usage, subscription.plan.tiers)
        # 按单位定价
        elif subscription.plan.pricing_model == 'per_unit':
            charge = total_usage * subscription.plan.unit_price
        # 数量定价
        elif subscription.plan.pricing_model == 'volume':
            charge = self.calculate_volume_pricing(total_usage, subscription.plan.tiers)

        return charge

    def calculate_tiered_pricing(self, total_usage, tiers):
        """使用阶梯定价计算成本。"""
        charge = 0
        remaining = total_usage

        for tier in sorted(tiers, key=lambda x: x['up_to']):
            tier_usage = min(remaining, tier['up_to'] - tier['from'])
            charge += tier_usage * tier['unit_price']
            remaining -= tier_usage

            if remaining <= 0:
                break

        return charge
```
