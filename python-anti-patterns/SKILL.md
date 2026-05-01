---
name: python-anti-patterns
description: 在审查 Python 代码中应避免的常见反模式时使用此技能。在审查代码、最终确定实现或调试可能源于已知不良实践的问题时，将其作为检查清单使用。
---

# Python 反模式检查清单

Python 代码中常见错误和反模式的参考检查清单。在最终确定实现之前审查此清单，以便尽早发现问题。

## 何时使用此技能

- 合并前审查代码
- 调试神秘问题
- 教授或学习 Python 最佳实践
- 制定团队编码标准
- 重构遗留代码

**注意：** 此技能侧重于应避免的内容。有关正面模式和架构的指导，请参阅 `python-design-patterns` 技能。

## 基础设施反模式

### 分散的超时/重试逻辑

```python
# BAD: Timeout logic duplicated everywhere
def fetch_user(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching user")
        return None

def fetch_orders(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching orders")
        return None
```

**修复：** 集中到装饰器或客户端包装器中。

```python
# GOOD: Centralized retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def http_get(url: str) -> Response:
    return requests.get(url, timeout=30)
```

### 双重重试

```python
# BAD: Retrying at multiple layers
@retry(max_attempts=3)  # Application retry
def call_service():
    return client.request()  # Client also has retry configured!
```

**修复：** 仅在一层进行重试。了解基础设施的重试行为。

### 硬编码配置

```python
# BAD: Secrets and config in code
DB_HOST = "prod-db.example.com"
API_KEY = "sk-12345"

def connect():
    return psycopg.connect(f"host={DB_HOST}...")
```

**修复：** 使用带类型设置的环境变量。

```python
# GOOD
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    api_key: str = Field(alias="API_KEY")

settings = Settings()
```

## 架构反模式

### 暴露内部类型

```python
# BAD: Leaking ORM model to API
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:  # SQLAlchemy model
    return db.query(UserModel).get(id)
```

**修复：** 使用 DTO/响应模型。

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.from_orm(user)
```

### 混合 I/O 和业务逻辑

```python
# BAD: SQL embedded in business logic
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    # Business logic mixed with data access
    if len(orders) > 10:
        return 0.15
    return 0.0
```

**修复：** 仓储模式。保持业务逻辑纯净。

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    # Pure business logic, easily testable
    if len(orders) > 10:
        return 0.15
    return 0.0
```

## 错误处理反模式

### 裸异常处理

```python
# BAD: Swallowing all exceptions
try:
    process()
except Exception:
    pass  # Silent failure - bugs hidden forever
```

**修复：** 捕获特定异常。适当记录或处理。

```python
# GOOD
try:
    process()
except ConnectionError as e:
    logger.warning("Connection failed, will retry", error=str(e))
    raise
except ValueError as e:
    logger.error("Invalid input", error=str(e))
    raise BadRequestError(str(e))
```

### 忽略部分失败

```python
# BAD: Stops on first error
def process_batch(items):
    results = []
    for item in items:
        result = process(item)  # Raises on error - batch aborted
        results.append(result)
    return results
```

**修复：** 同时捕获成功和失败。

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

### 缺少输入验证

```python
# BAD: No validation
def create_user(data: dict):
    return User(**data)  # Crashes deep in code on bad input
```

**修复：** 在 API 边界尽早验证。

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## 资源反模式

### 未关闭的资源

```python
# BAD: File never closed
def read_file(path):
    f = open(path)
    return f.read()  # What if this raises?
```

**修复：** 使用上下文管理器。

```python
# GOOD
def read_file(path):
    with open(path) as f:
        return f.read()
```

### 在异步中阻塞

```python
# BAD: Blocks the entire event loop
async def fetch_data():
    time.sleep(1)  # Blocks everything!
    response = requests.get(url)  # Also blocks!
```

**修复：** 使用异步原生库。

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

## 类型安全反模式

### 缺少类型提示

```python
# BAD: No types
def process(data):
    return data["value"] * 2
```

**修复：** 为所有公共函数添加注解。

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### 无类型集合

```python
# BAD: Generic list without type parameter
def get_users() -> list:
    ...
```

**修复：** 使用类型参数。

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## 测试反模式

### 仅测试正常路径

```python
# BAD: Only tests success case
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

**修复：** 测试错误条件和边界情况。

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None

def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)

def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### 过度模拟

```python
# BAD: Mocking everything
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
    # Test doesn't verify real behavior
```

**修复：** 对关键路径使用集成测试。仅模拟外部服务。

## 快速审查检查清单

在最终确定代码之前，请验证：

- [ ] 没有分散的超时/重试逻辑（已集中）
- [ ] 没有双重重试（应用 + 基础设施）
- [ ] 没有硬编码的配置或密钥
- [ ] 没有暴露内部类型（ORM 模型、protobufs）
- [ ] 没有混合 I/O 和业务逻辑
- [ ] 没有裸 `except Exception: pass`
- [ ] 没有忽略批量中的部分失败
- [ ] 没有缺少输入验证
- [ ] 没有未关闭的资源（使用上下文管理器）
- [ ] 异步代码中没有阻塞调用
- [ ] 所有公共函数都有类型提示
- [ ] 集合有类型参数
- [ ] 错误路径已测试
- [ ] 边界情况已覆盖

## 常见修复总结

| 反模式 | 修复 |
|-------------|-----|
| 分散的重试逻辑 | 集中的装饰器 |
| 硬编码配置 | 环境变量 + pydantic-settings |
| 暴露 ORM 模型 | DTO/响应模式 |
| 混合 I/O + 逻辑 | 仓储模式 |
| 裸异常 | 捕获特定异常 |
| 批量遇错停止 | 返回包含成功/失败的 BatchResult |
| 无验证 | 在边界使用 Pydantic 验证 |
| 未关闭的资源 | 上下文管理器 |
| 异步中阻塞 | 异步原生库 |
| 缺少类型 | 所有公共 API 的类型注解 |
| 仅测试正常路径 | 测试错误和边界情况 |
