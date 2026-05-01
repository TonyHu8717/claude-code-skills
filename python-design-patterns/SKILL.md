---
name: python-design-patterns
description: Python 设计模式，包括 KISS、关注点分离、单一职责和组合优于继承。在从头设计新服务或组件并选择如何分层职责时、在重构增长过大的上帝类或单体函数时、在决定是添加新抽象还是接受重复时、在评估拉取请求中的结构问题（如紧耦合或泄露内部类型）时、在为新类层次结构选择继承与组合时、或在代码库因 I/O 和业务逻辑纠缠而变得难以测试时，使用此技能。
---

# Python 设计模式

使用基本设计原则编写可维护的 Python 代码。这些模式帮助你构建易于理解、测试和修改的系统。

## 何时使用此技能

- 设计新组件或服务
- 重构复杂或纠缠的代码
- 决定是否创建抽象
- 在继承和组合之间选择
- 评估代码复杂性和耦合度
- 规划模块化架构

## 核心概念

### 1. KISS（保持简单）

选择可行的最简单解决方案。复杂性必须由具体需求来证明合理性。

### 2. 单一职责（SRP）

每个单元应该只有一个变更原因。将关注点分离到专注的组件中。

### 3. 组合优于继承

通过组合对象而非扩展类来构建行为。

### 4. 三法则

在抽象之前等待有三个实例。重复通常优于过早抽象。

## 快速开始

```python
# Simple beats clever
# Instead of a factory/registry pattern:
FORMATTERS = {"json": JsonFormatter, "csv": CsvFormatter}

def get_formatter(name: str) -> Formatter:
    return FORMATTERS[name]()
```

## 基础模式

### 模式 1：KISS - 保持简单

在添加复杂性之前，问一下：更简单的解决方案可行吗？

```python
# Over-engineered: Factory with registration
class OutputFormatterFactory:
    _formatters: dict[str, type[Formatter]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(formatter_cls):
            cls._formatters[name] = formatter_cls
            return formatter_cls
        return decorator

    @classmethod
    def create(cls, name: str) -> Formatter:
        return cls._formatters[name]()

@OutputFormatterFactory.register("json")
class JsonFormatter(Formatter):
    ...

# Simple: Just use a dictionary
FORMATTERS = {
    "json": JsonFormatter,
    "csv": CsvFormatter,
    "xml": XmlFormatter,
}

def get_formatter(name: str) -> Formatter:
    """Get formatter by name."""
    if name not in FORMATTERS:
        raise ValueError(f"Unknown format: {name}")
    return FORMATTERS[name]()
```

工厂模式在这里增加了代码但没有增加价值。将模式保留到它们能解决真正问题的时候。

### 模式 2：单一职责原则

每个类或函数应该只有一个变更原因。

```python
# BAD: Handler does everything
class UserHandler:
    async def create_user(self, request: Request) -> Response:
        # HTTP parsing
        data = await request.json()

        # Validation
        if not data.get("email"):
            return Response({"error": "email required"}, status=400)

        # Database access
        user = await db.execute(
            "INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *",
            data["email"], data["name"]
        )

        # Response formatting
        return Response({"id": user.id, "email": user.email}, status=201)

# GOOD: Separated concerns
class UserService:
    """Business logic only."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def create_user(self, data: CreateUserInput) -> User:
        # Only business rules here
        user = User(email=data.email, name=data.name)
        return await self._repo.save(user)

class UserHandler:
    """HTTP concerns only."""

    def __init__(self, service: UserService) -> None:
        self._service = service

    async def create_user(self, request: Request) -> Response:
        data = CreateUserInput(**(await request.json()))
        user = await self._service.create_user(data)
        return Response(user.to_dict(), status=201)
```

现在 HTTP 变更不会影响业务逻辑，反之亦然。

### 模式 3：关注点分离

将代码组织成具有清晰职责的不同层。

```
┌─────────────────────────────────────────────────────┐
│  API Layer (handlers)                                │
│  - Parse requests                                    │
│  - Call services                                     │
│  - Format responses                                  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Service Layer (business logic)                      │
│  - Domain rules and validation                       │
│  - Orchestrate operations                            │
│  - Pure functions where possible                     │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  Repository Layer (data access)                      │
│  - SQL queries                                       │
│  - External API calls                                │
│  - Cache operations                                  │
└─────────────────────────────────────────────────────┘
```

每层仅依赖其下层：

```python
# Repository: Data access
class UserRepository:
    async def get_by_id(self, user_id: str) -> User | None:
        row = await self._db.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        return User(**row) if row else None

# Service: Business logic
class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def get_user(self, user_id: str) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

# Handler: HTTP concerns
@app.get("/users/{user_id}")
async def get_user(user_id: str) -> UserResponse:
    user = await user_service.get_user(user_id)
    return UserResponse.from_user(user)
```

### 模式 4：组合优于继承

通过组合对象而非继承来构建行为。

```python
# Inheritance: Rigid and hard to test
class EmailNotificationService(NotificationService):
    def __init__(self):
        super().__init__()
        self._smtp = SmtpClient()  # Hard to mock

    def notify(self, user: User, message: str) -> None:
        self._smtp.send(user.email, message)

# Composition: Flexible and testable
class NotificationService:
    """Send notifications via multiple channels."""

    def __init__(
        self,
        email_sender: EmailSender,
        sms_sender: SmsSender | None = None,
        push_sender: PushSender | None = None,
    ) -> None:
        self._email = email_sender
        self._sms = sms_sender
        self._push = push_sender

    async def notify(
        self,
        user: User,
        message: str,
        channels: set[str] | None = None,
    ) -> None:
        channels = channels or {"email"}

        if "email" in channels:
            await self._email.send(user.email, message)

        if "sms" in channels and self._sms and user.phone:
            await self._sms.send(user.phone, message)

        if "push" in channels and self._push and user.device_token:
            await self._push.send(user.device_token, message)

# Easy to test with fakes
service = NotificationService(
    email_sender=FakeEmailSender(),
    sms_sender=FakeSmsSender(),
)
```

## 高级模式

### 模式 5：三法则

在抽象之前等待有三个实例。

```python
# Two similar functions? Don't abstract yet
def process_orders(orders: list[Order]) -> list[Result]:
    results = []
    for order in orders:
        validated = validate_order(order)
        result = process_validated_order(validated)
        results.append(result)
    return results

def process_returns(returns: list[Return]) -> list[Result]:
    results = []
    for ret in returns:
        validated = validate_return(ret)
        result = process_validated_return(validated)
        results.append(result)
    return results

# These look similar, but wait! Are they actually the same?
# Different validation, different processing, different errors...
# Duplication is often better than the wrong abstraction

# Only after a third case, consider if there's a real pattern
# But even then, sometimes explicit is better than abstract
```

### 模式 6：函数大小指南

保持函数专注。在以下情况下提取函数：

- 超过 20-50 行（因复杂性而异）
- 服务于多个不同目的
- 有深层嵌套逻辑（3+ 层）

```python
# Too long, multiple concerns mixed
def process_order(order: Order) -> Result:
    # 50 lines of validation...
    # 30 lines of inventory check...
    # 40 lines of payment processing...
    # 20 lines of notification...
    pass

# Better: Composed from focused functions
def process_order(order: Order) -> Result:
    """Process a customer order through the complete workflow."""
    validate_order(order)
    reserve_inventory(order)
    payment_result = charge_payment(order)
    send_confirmation(order, payment_result)
    return Result(success=True, order_id=order.id)
```

### 模式 7：依赖注入

通过构造函数传递依赖以实现可测试性。

```python
from typing import Protocol

class Logger(Protocol):
    def info(self, msg: str, **kwargs) -> None: ...
    def error(self, msg: str, **kwargs) -> None: ...

class Cache(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int) -> None: ...

class UserService:
    """Service with injected dependencies."""

    def __init__(
        self,
        repository: UserRepository,
        cache: Cache,
        logger: Logger,
    ) -> None:
        self._repo = repository
        self._cache = cache
        self._logger = logger

    async def get_user(self, user_id: str) -> User:
        # Check cache first
        cached = await self._cache.get(f"user:{user_id}")
        if cached:
            self._logger.info("Cache hit", user_id=user_id)
            return User.from_json(cached)

        # Fetch from database
        user = await self._repo.get_by_id(user_id)
        if user:
            await self._cache.set(f"user:{user_id}", user.to_json(), ttl=300)

        return user

# Production
service = UserService(
    repository=PostgresUserRepository(db),
    cache=RedisCache(redis),
    logger=StructlogLogger(),
)

# Testing
service = UserService(
    repository=InMemoryUserRepository(),
    cache=FakeCache(),
    logger=NullLogger(),
)
```

### 模式 8：避免常见反模式

**不要暴露内部类型：**

```python
# BAD: Leaking ORM model to API
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:  # SQLAlchemy model
    return db.query(UserModel).get(id)

# GOOD: Use response schemas
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.from_orm(user)
```

**不要将 I/O 与业务逻辑混合：**

```python
# BAD: SQL embedded in business logic
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    # Business logic mixed with data access

# GOOD: Repository pattern
def calculate_discount(user: User, order_history: list[Order]) -> float:
    # Pure business logic, easily testable
    if len(order_history) > 10:
        return 0.15
    return 0.0
```

## 最佳实践总结

1. **保持简单** - 选择可行的最简单解决方案
2. **单一职责** - 每个单元只有一个变更原因
3. **关注点分离** - 具有清晰目的的不同层
4. **组合，不要继承** - 组合对象以获得灵活性
5. **三法则** - 在抽象之前等待
6. **保持函数小** - 20-50 行（因复杂性而异），一个目的
7. **注入依赖** - 构造函数注入以实现可测试性
8. **在抽象之前删除** - 删除死代码，然后考虑模式
9. **测试每层** - 每个关注点的隔离测试
10. **显式优于巧妙** - 可读代码胜过优雅代码

## 故障排除

**一个类在增长，似乎有多个职责，但拆分感觉不对。**
应用"变更原因"测试：列出可能需要编辑此类的每个变更。如果列表中有来自不同领域的项目（例如 HTTP 解析和业务规则和格式化），则拆分它。如果所有变更都源于同一个领域关注点，则该类可能大小合适。

**通过构造函数注入所有依赖会产生 7+ 个参数的构造函数。**
这是一个类中有太多职责的迹象，而不是依赖注入的问题。首先将类拆分为更小的单元，然后每个构造函数自然变小。

**组合产生难以跟踪的深层嵌套包装对象。**
保持组合浅层（2-3 层）。如果包装是唯一的机制，考虑基于 Protocol 的方法或简单的函数组合是否比装饰器链更干净。

**三法则说还不要抽象，但当一份副本更新而另一份未更新时，重复会导致错误。**
以危险方式分叉的重复应尽早抽象。三法则是启发式，不是法则。如果副本已经在错误地分叉，立即提取并添加一个测试共享行为的测试。

**服务层从 API 层导入，破坏了依赖方向。**
这是一个分层违规。服务层不得从处理程序导入。引入一个共享的类型/模型层，两者都可以从中导入，保持依赖箭头向下（API -> Service -> Repository）。

## 相关技能

- [python-testing-patterns](../python-testing-patterns/SKILL.md) — 使用此处建立的依赖注入结构隔离测试每一层
- [python-project-setup](../python-project-setup/SKILL.md) — 设置从一开始就强制分层边界的项目结构和工具
