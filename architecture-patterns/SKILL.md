---
name: architecture-patterns
description: 实现经过验证的后端架构模式，包括清洁架构、六边形架构和领域驱动设计。在为新微服务设计清洁架构、在重构单体应用使用限界上下文、在实现六边形或洋葱架构模式或在调试应用层之间的依赖循环时使用此技能。
---

# 架构模式

掌握经过验证的后端架构模式，包括清洁架构、六边形架构和领域驱动设计，构建可维护、可测试和可扩展的系统。

**给定：** 一个服务边界或模块需要架构设计。
**产出：** 具有清晰依赖规则、接口定义和测试边界的分层结构。

## 使用场景

- 从头设计新的后端服务或微服务
- 重构业务逻辑与 ORM 模型或 HTTP 关注点纠缠的单体应用
- 在将系统拆分为服务之前建立限界上下文
- 调试基础设施代码渗入领域层的依赖循环
- 创建可测试的代码库，用例测试不需要运行中的数据库
- 实现领域驱动设计战术模式（聚合、值对象、领域事件）

## 核心概念

### 1. 清洁架构（Uncle Bob）

**层（依赖向内流动）：**

- **实体**：核心业务模型，无框架导入
- **用例**：应用业务规则，编排实体
- **接口适配器**：控制器、展示器、网关 — 在用例和外部格式之间转换
- **框架和驱动**：UI、数据库、外部服务 — 全部在最外层

**关键原则：**

- 依赖仅指向内部；内层对外层一无所知
- 业务逻辑独立于框架、数据库和交付机制
- 每个层边界通过抽象接口跨越
- 无需 UI、数据库或外部服务即可测试

### 2. 六边形架构（端口和适配器）

**组件：**

- **领域核心**：业务逻辑在此，无框架
- **端口**：定义核心如何与外部世界交互的抽象接口（驱动和被驱动）
- **适配器**：端口的具体实现（PostgreSQL 适配器、Stripe 适配器、REST 适配器）

**好处：**

- 无需触碰核心即可替换实现（例如用 DynamoDB 替换 PostgreSQL）
- 在测试中使用内存适配器 — 无需 Docker
- 技术决策推迟到边缘

### 3. 领域驱动设计（DDD）

**战略模式：**

- **限界上下文**：为一个子领域隔离连贯模型；避免在整个系统中共享单一模型
- **上下文映射**：定义上下文如何关联（反腐层、共享内核、开放主机服务）
- **统一语言**：代码中的每个术语都与领域专家使用的术语匹配

**战术模式：**

- **实体**：具有稳定标识符的对象，随时间变化
- **值对象**：由其属性标识的不可变对象（Email、Money、Address）
- **聚合**：一致性边界；只有根可从外部访问
- **仓储**：持久化和重建聚合；抽象存储机制
- **领域事件**：捕获领域内发生的事情；用于跨聚合协调

## 清洁架构 — 目录结构

```
app/
├── domain/           # Entities, value objects, interfaces
│   ├── entities/
│   │   ├── user.py
│   │   └── order.py
│   ├── value_objects/
│   │   ├── email.py
│   │   └── money.py
│   └── interfaces/   # Abstract ports (no implementations)
│       ├── user_repository.py
│       └── payment_gateway.py
├── use_cases/        # Application business rules
│   ├── create_user.py
│   ├── process_order.py
│   └── send_notification.py
├── adapters/         # Concrete implementations
│   ├── repositories/
│   │   ├── postgres_user_repository.py
│   │   └── redis_cache_repository.py
│   ├── controllers/
│   │   └── user_controller.py
│   └── gateways/
│       ├── stripe_payment_gateway.py
│       └── sendgrid_email_gateway.py
└── infrastructure/   # Framework wiring, config, DI container
    ├── database.py
    ├── config.py
    └── logging.py
```

**依赖规则一句话：** `domain/` 和 `use_cases/` 中的每个 `import` 语句必须仅指向 `domain/`；这些层中的任何内容都不得从 `adapters/` 或 `infrastructure/` 导入。

## 清洁架构 — 核心实现

```python
# domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    """Core user entity — no framework dependencies."""
    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool = True

    def deactivate(self):
        self.is_active = False

    def can_place_order(self) -> bool:
        return self.is_active


# domain/interfaces/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.user import User

class IUserRepository(ABC):
    """Port: defines contract, no implementation details."""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool: ...


# use_cases/create_user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository

@dataclass
class CreateUserRequest:
    email: str
    name: str

@dataclass
class CreateUserResponse:
    user: Optional[User]
    success: bool
    error: Optional[str] = None

class CreateUserUseCase:
    """Use case: orchestrates business logic, no HTTP or DB details."""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        existing = await self.user_repository.find_by_email(request.email)
        if existing:
            return CreateUserResponse(user=None, success=False, error="Email already exists")

        user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            name=request.name,
            created_at=datetime.now(),
        )
        saved_user = await self.user_repository.save(user)
        return CreateUserResponse(user=saved_user, success=True)


# adapters/repositories/postgres_user_repository.py
from domain.interfaces.user_repository import IUserRepository
from domain.entities.user import User
from typing import Optional
import asyncpg

class PostgresUserRepository(IUserRepository):
    """Adapter: PostgreSQL implementation of the user port."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_by_id(self, user_id: str) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return self._to_entity(row) if row else None

    async def find_by_email(self, email: str) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            return self._to_entity(row) if row else None

    async def save(self, user: User) -> User:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, email, name, created_at, is_active)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE
                SET email = $2, name = $3, is_active = $5
                """,
                user.id, user.email, user.name, user.created_at, user.is_active,
            )
        return user

    async def delete(self, user_id: str) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
            return result == "DELETE 1"

    def _to_entity(self, row) -> User:
        return User(
            id=row["id"], email=row["email"], name=row["name"],
            created_at=row["created_at"], is_active=row["is_active"],
        )


# adapters/controllers/user_controller.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from use_cases.create_user import CreateUserUseCase, CreateUserRequest

router = APIRouter()

class CreateUserDTO(BaseModel):
    email: str
    name: str

@router.post("/users")
async def create_user(
    dto: CreateUserDTO,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    """Controller handles HTTP only — no business logic lives here."""
    response = await use_case.execute(CreateUserRequest(email=dto.email, name=dto.name))
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return {"user": response.user}
```

## 六边形架构 — 端口和适配器

```python
# Core domain service — no infrastructure dependencies
class OrderService:
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        payment_gateway: PaymentGatewayPort,
        notification_service: NotificationPort,
    ):
        self.orders = order_repository
        self.payments = payment_gateway
        self.notifications = notification_service

    async def place_order(self, order: Order) -> OrderResult:
        if not order.is_valid():
            return OrderResult(success=False, error="Invalid order")

        payment = await self.payments.charge(amount=order.total, customer=order.customer_id)
        if not payment.success:
            return OrderResult(success=False, error="Payment failed")

        order.mark_as_paid()
        saved_order = await self.orders.save(order)
        await self.notifications.send(
            to=order.customer_email,
            subject="Order confirmed",
            body=f"Order {order.id} confirmed",
        )
        return OrderResult(success=True, order=saved_order)


# Ports (driving and driven interfaces)
class OrderRepositoryPort(ABC):
    @abstractmethod
    async def save(self, order: Order) -> Order: ...

class PaymentGatewayPort(ABC):
    @abstractmethod
    async def charge(self, amount: Money, customer: str) -> PaymentResult: ...

class NotificationPort(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str): ...


# Production adapter: Stripe
class StripePaymentAdapter(PaymentGatewayPort):
    def __init__(self, api_key: str):
        import stripe
        stripe.api_key = api_key
        self._stripe = stripe

    async def charge(self, amount: Money, customer: str) -> PaymentResult:
        try:
            charge = self._stripe.Charge.create(
                amount=amount.cents, currency=amount.currency, customer=customer
            )
            return PaymentResult(success=True, transaction_id=charge.id)
        except self._stripe.error.CardError as e:
            return PaymentResult(success=False, error=str(e))


# Test adapter: no external dependencies
class MockPaymentAdapter(PaymentGatewayPort):
    async def charge(self, amount: Money, customer: str) -> PaymentResult:
        return PaymentResult(success=True, transaction_id="mock-txn-123")
```

## DDD — 值对象和聚合

```python
# Value Objects: immutable, validated at construction
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value or "." not in self.value.split("@")[-1]:
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Money:
    amount: int   # cents
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if self.currency not in {"USD", "EUR", "GBP"}:
            raise ValueError(f"Unsupported currency: {self.currency}")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)


# Aggregate root: enforces all invariants for its cluster of entities
class Order:
    def __init__(self, id: str, customer_id: str):
        self.id = id
        self.customer_id = customer_id
        self.items: list[OrderItem] = []
        self.status = OrderStatus.PENDING
        self._events: list[DomainEvent] = []

    def add_item(self, product: Product, quantity: int):
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot modify a submitted order")
        item = OrderItem(product=product, quantity=quantity)
        self.items.append(item)
        self._events.append(ItemAddedEvent(order_id=self.id, item=item))

    @property
    def total(self) -> Money:
        totals = [item.subtotal() for item in self.items]
        return sum(totals[1:], totals[0]) if totals else Money(0, "USD")

    def submit(self):
        if not self.items:
            raise ValueError("Cannot submit an empty order")
        if self.status != OrderStatus.PENDING:
            raise ValueError("Order already submitted")
        self.status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmittedEvent(order_id=self.id))

    def pop_events(self) -> list[DomainEvent]:
        events, self._events = self._events, []
        return events


# Repository: persist and reconstitute aggregates
class OrderRepository(ABC):
    @abstractmethod
    async def find_by_id(self, order_id: str) -> Optional[Order]: ...

    @abstractmethod
    async def save(self, order: Order) -> None: ...
    # Implementations persist events via pop_events() after writing state
```

## 测试 — 内存适配器

正确应用清洁架构的标志是每个用例都可以在普通单元测试中执行，无需真实数据库、Docker 或网络：

```python
# tests/unit/test_create_user.py
import asyncio
from typing import Dict, Optional
from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository
from use_cases.create_user import CreateUserUseCase, CreateUserRequest


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._store: Dict[str, User] = {}

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._store.values() if u.email == email), None)

    async def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def delete(self, user_id: str) -> bool:
        return self._store.pop(user_id, None) is not None


async def test_create_user_succeeds():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))

    assert response.success
    assert response.user.email == "alice@example.com"
    assert response.user.id is not None


async def test_duplicate_email_rejected():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))
    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice2"))

    assert not response.success
    assert "already exists" in response.error
```

## 故障排除

### 用例测试需要运行中的数据库

业务逻辑已泄漏到基础设施层。将所有数据库调用移到 `IRepository` 接口后面，并在测试中注入内存实现（参见上面的测试部分）。用例构造函数必须接受抽象端口，而非具体类。

### 层之间的循环导入

常见症状是 `use_cases` 和 `adapters` 之间出现 `ImportError: cannot import name X`。当用例导入具体适配器类而非抽象端口时会发生这种情况。强制执行规则：`use_cases/` 仅从 `domain/`（实体和接口）导入。它永远不得从 `adapters/` 或 `infrastructure/` 导入。

### 框架装饰器出现在领域实体中

如果 SQLAlchemy `Column()` 或 Pydantic `Field()` 注解出现在领域实体上，则该实体不再纯净。在 `adapters/repositories/` 中创建单独的 ORM 模型，并在仓储的 `_to_entity()` 方法中映射到/从领域实体。

### 所有逻辑都在控制器中

当控制器增长超出 HTTP 解析和响应格式化时，将逻辑提取到用例类中。控制器方法应只做三件事：解析请求、调用用例、映射响应。

### 值对象报错太晚

在 `__post_init__`（Python）或构造函数中验证不变量，使无效的 `Email` 或 `Money` 根本无法构造。这在边界处暴露坏数据，而不是在业务逻辑深处。

### 跨限界上下文的上下文泄漏

如果 `Order` 上下文从 `Identity` 上下文导入 `User` 实体，引入反腐层。`Order` 上下文应持有自己的轻量级 `CustomerId` 值对象，并仅通过显式接口调用 `Identity` 上下文。

## 高级模式

详细的 DDD 限界上下文映射、完整多服务项目树、反腐层实现和洋葱架构比较参见：

- [`references/advanced-patterns.md`](references/advanced-patterns.md)

## 相关技能

- `microservices-patterns` — 在将单体分解为服务时应用这些架构模式
- `cqrs-implementation` — 使用清洁架构作为 CQRS 命令/查询分离的结构基础
- `saga-orchestration` — Saga 需要明确定义的聚合边界，DDD 战术模式提供
- `event-store-design` — 聚合产生的领域事件直接馈入事件存储
