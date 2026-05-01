---
name: stripe-integration
description: 实现 Stripe 支付处理，构建健壮的、PCI 合规的支付流程，包括结账、订阅和 Webhook。适用于集成 Stripe 支付、构建订阅系统或实现安全结账流程。
---

# Stripe 集成

掌握 Stripe 支付处理集成，构建健壮的、PCI 合规的支付流程，包括结账、订阅、Webhook 和退款。

## 何时使用此技能

- 在 Web/移动应用中实现支付处理
- 设置订阅计费系统
- 处理一次性支付和定期收费
- 处理退款和争议
- 管理客户支付方式
- 为欧洲支付实施 SCA（强客户认证）
- 使用 Stripe Connect 构建市场支付流程

## 核心概念

### 1. 支付流程

**结账会话（Checkout Sessions）**

- 推荐用于大多数集成
- 支持所有 UI 路径：
  - Stripe 托管的结账页面
  - 嵌入式结账表单
  - 使用 Elements 的自定义 UI（Payment Element、Express Checkout Element），通过 `ui_mode='custom'`
- 提供内置结账功能（订单行项目、折扣、税费、运费、地址收集、已保存支付方式和结账生命周期事件）
- 比 Payment Intents 更低的集成和维护负担

**Payment Intents（定制控制）**

- 你自己计算含税费、折扣、订阅和货币转换的最终金额
- 更复杂的实现和长期维护负担
- 需要 Stripe.js 以实现 PCI 合规

**Setup Intents（保存支付方式）**

- 收集支付方式而不收费
- 用于订阅和未来支付
- 需要客户确认

### 2. Webhook

**关键事件：**

- `payment_intent.succeeded`：支付完成
- `payment_intent.payment_failed`：支付失败
- `customer.subscription.updated`：订阅变更
- `customer.subscription.deleted`：订阅取消
- `charge.refunded`：退款处理
- `invoice.payment_succeeded`：订阅支付成功

### 3. 订阅

**组件：**

- **产品**：你销售的内容
- **价格**：多少和多频繁
- **订阅**：客户的定期支付
- **发票**：每个计费周期生成

### 4. 客户管理

- 创建和管理客户记录
- 存储多个支付方式
- 跟踪客户元数据
- 管理账单详情

## 快速开始

```python
import stripe

stripe.api_key = "sk_test_..."

# 创建结账会话
session = stripe.checkout.Session.create(
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Premium Subscription',
            },
            'unit_amount': 2000,  # $20.00
            'recurring': {
                'interval': 'month',
            },
        },
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='https://yourdomain.com/cancel'
)

# 重定向用户到 session.url
print(session.url)
```

## 支付实现模式

### 模式 1：一次性支付（托管结账）

```python
def create_checkout_session(amount, currency='usd'):
    """创建一次性支付结账会话。"""
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Blue T-shirt',
                        'images': ['https://example.com/product.jpg'],
                    },
                    'unit_amount': amount,  # 金额单位为分
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel',
            metadata={
                'order_id': 'order_123',
                'user_id': 'user_456'
            }
        )
        return session
    except stripe.error.StripeError as e:
        # 处理错误
        print(f"Stripe error: {e.user_message}")
        raise
```

### 模式 2：Elements 与结账会话

```python
def create_checkout_session_for_elements(amount, currency='usd'):
    """创建为 Payment Element 配置的结账会话。"""
    session = stripe.checkout.Session.create(
        mode='payment',
        ui_mode='custom',
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {'name': 'Blue T-shirt'},
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        return_url='https://yourdomain.com/complete?session_id={CHECKOUT_SESSION_ID}'
    )
    return session.client_secret  # 发送到前端
```

```javascript
const stripe = Stripe("pk_test_...");
const appearance = { theme: "stripe" };

const checkout = stripe.initCheckout({
  clientSecret,
  elementsOptions: { appearance },
});
const loadActionsResult = await checkout.loadActions();

if (loadActionsResult.type === "success") {
  const { actions } = loadActionsResult;
  const session = actions.getSession();

  const button = document.getElementById("pay-button");
  const checkoutContainer = document.getElementById("checkout-container");
  const emailInput = document.getElementById("email");
  const emailErrors = document.getElementById("email-errors");
  const errors = document.getElementById("confirm-errors");

  // 显示格式化的总金额字符串
  checkoutContainer.append(`Total: ${session.total.total.amount}`);

  // 挂载 Payment Element
  const paymentElement = checkout.createPaymentElement();
  paymentElement.mount("#payment-element");

  // 存储邮箱用于提交
  emailInput.addEventListener("blur", () => {
    actions.updateEmail(emailInput.value).then((result) => {
      if (result.error) emailErrors.textContent = result.error.message;
    });
  });

  // 处理表单提交
  button.addEventListener("click", () => {
    actions.confirm().then((result) => {
      if (result.type === "error") errors.textContent = result.error.message;
    });
  });
}
```

### 模式 3：Elements 与 Payment Intents

模式 2（Elements 与结账会话）是 Stripe 推荐的方法，但你也可以使用 Payment Intents 作为替代。

```python
def create_payment_intent(amount, currency='usd', customer_id=None):
    """为定制结账 UI 创建 Payment Intent，配合 Payment Element 使用。"""
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        customer=customer_id,
        automatic_payment_methods={
            'enabled': True,
        },
        metadata={
            'integration_check': 'accept_a_payment'
        }
    )
    return intent.client_secret  # 发送到前端
```

```javascript
// 挂载 Payment Element 并通过 Payment Intents 确认
const stripe = Stripe("pk_test_...");
const appearance = { theme: "stripe" };
const elements = stripe.elements({ appearance, clientSecret });

const paymentElement = elements.create("payment");
paymentElement.mount("#payment-element");

document.getElementById("pay-button").addEventListener("click", async () => {
  const { error } = await stripe.confirmPayment({
    elements,
    confirmParams: {
      return_url: "https://yourdomain.com/complete",
    },
  });

  if (error) {
    document.getElementById("errors").textContent = error.message;
  }
});
```

### 模式 4：创建订阅

```python
def create_subscription(customer_id, price_id):
    """为客户创建订阅。"""
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )

        return {
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        }
    except stripe.error.StripeError as e:
        print(f"Subscription creation failed: {e}")
        raise
```

### 模式 5：客户门户

```python
def create_customer_portal_session(customer_id):
    """创建门户会话，让客户管理订阅。"""
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url='https://yourdomain.com/account',
    )
    return session.url  # 将客户重定向到此处
```

## Webhook 处理

### 安全 Webhook 端点

```python
from flask import Flask, request
import stripe

app = Flask(__name__)

endpoint_secret = 'whsec_...'

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # 无效负载
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        # 无效签名
        return 'Invalid signature', 400

    # 处理事件
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_failed_payment(payment_intent)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_canceled(subscription)

    return 'Success', 200

def handle_successful_payment(payment_intent):
    """处理成功的支付。"""
    customer_id = payment_intent.get('customer')
    amount = payment_intent['amount']
    metadata = payment_intent.get('metadata', {})

    # 更新你的数据库
    # 发送确认邮件
    # 履行订单
    print(f"Payment succeeded: {payment_intent['id']}")

def handle_failed_payment(payment_intent):
    """处理失败的支付。"""
    error = payment_intent.get('last_payment_error', {})
    print(f"Payment failed: {error.get('message')}")
    # 通知客户
    # 更新订单状态

def handle_subscription_canceled(subscription):
    """处理订阅取消。"""
    customer_id = subscription['customer']
    # 更新用户访问权限
    # 发送取消邮件
    print(f"Subscription canceled: {subscription['id']}")
```

### Webhook 最佳实践

```python
import hashlib
import hmac

def verify_webhook_signature(payload, signature, secret):
    """手动验证 Webhook 签名。"""
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_sig)

def handle_webhook_idempotently(event_id, handler):
    """确保 Webhook 只被处理一次。"""
    # 检查事件是否已处理
    if is_event_processed(event_id):
        return

    # 处理事件
    try:
        handler()
        mark_event_processed(event_id)
    except Exception as e:
        log_error(e)
        # Stripe 会重试失败的 Webhook
        raise
```

## 客户管理

```python
def create_customer(email, name, payment_method_id=None):
    """创建 Stripe 客户。"""
    customer = stripe.Customer.create(
        email=email,
        name=name,
        payment_method=payment_method_id,
        invoice_settings={
            'default_payment_method': payment_method_id
        } if payment_method_id else None,
        metadata={
            'user_id': '12345'
        }
    )
    return customer

def attach_payment_method(customer_id, payment_method_id):
    """将支付方式附加到客户。"""
    stripe.PaymentMethod.attach(
        payment_method_id,
        customer=customer_id
    )

    # 设为默认
    stripe.Customer.modify(
        customer_id,
        invoice_settings={
            'default_payment_method': payment_method_id
        }
    )

def list_customer_payment_methods(customer_id):
    """列出客户的所有支付方式。"""
    payment_methods = stripe.PaymentMethod.list(
        customer=customer_id,
        type='card'
    )
    return payment_methods.data
```

## 退款处理

```python
def create_refund(payment_intent_id, amount=None, reason=None):
    """创建退款。"""
    refund_params = {
        'payment_intent': payment_intent_id
    }

    if amount:
        refund_params['amount'] = amount  # 部分退款

    if reason:
        refund_params['reason'] = reason  # 'duplicate'、'fraudulent'、'requested_by_customer'

    refund = stripe.Refund.create(**refund_params)
    return refund

def handle_dispute(charge_id, evidence):
    """使用证据更新争议。"""
    stripe.Dispute.modify(
        charge_id,
        evidence={
            'customer_name': evidence.get('customer_name'),
            'customer_email_address': evidence.get('customer_email'),
            'shipping_documentation': evidence.get('shipping_proof'),
            'customer_communication': evidence.get('communication'),
        }
    )
```

## 测试

```python
# 使用测试模式密钥
stripe.api_key = "sk_test_..."

# 测试卡号
TEST_CARDS = {
    'success': '4242424242424242',
    'declined': '4000000000000002',
    '3d_secure': '4000002500003155',
    'insufficient_funds': '4000000000009995'
}

def test_payment_flow():
    """测试完整支付流程。"""
    # 创建测试客户
    customer = stripe.Customer.create(
        email="test@example.com"
    )

    # 创建 Payment Intent
    intent = stripe.PaymentIntent.create(
        amount=1000,
        automatic_payment_methods={
            'enabled': True
        },
        currency='usd',
        customer=customer.id
    )

    # 使用测试卡确认
    confirmed = stripe.PaymentIntent.confirm(
        intent.id,
        payment_method='pm_card_visa'  # 测试支付方式
    )

    assert confirmed.status == 'succeeded'
```
