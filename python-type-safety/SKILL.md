---
name: python-type-safety
description: 使用类型提示、泛型、协议和严格类型检查实现 Python 类型安全。在添加类型注解、实现泛型类、定义结构化接口或配置 mypy/pyright 时使用。
---

# Python 类型安全

利用 Python 的类型系统在静态分析时捕获错误。类型注解作为工具自动验证的强制性文档。

## 何时使用此技能

- 为现有代码添加类型提示
- 创建泛型、可复用的类
- 使用协议定义结构化接口
- 配置 mypy 或 pyright 进行严格检查
- 理解类型缩窄和守卫
- 构建类型安全的 API 和库

## 核心概念

### 1. 类型注解

为函数参数、返回值和变量声明预期类型。

### 2. 泛型

编写在不同类型之间保留类型信息的可复用代码。

### 3. 协议

无需继承即可定义结构化接口（带类型安全的鸭子类型）。

### 4. 类型缩窄

使用守卫和条件在代码块中缩窄类型。

## 快速开始

```python
def get_user(user_id: str) -> User | None:
    """Return type makes 'might not exist' explicit."""
    ...

# Type checker enforces handling None case
user = get_user("123")
if user is None:
    raise UserNotFoundError("123")
print(user.name)  # Type checker knows user is User here
```

## 基础模式

### 模式 1：注解所有公共签名

每个公共函数、方法和类都应该有类型注解。

```python
def get_user(user_id: str) -> User:
    """Retrieve user by ID."""
    ...

def process_batch(
    items: list[Item],
    max_workers: int = 4,
) -> BatchResult[ProcessedItem]:
    """Process items concurrently."""
    ...

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_id(self, user_id: str) -> User | None:
        """Return User if found, None otherwise."""
        ...

    async def find_by_email(self, email: str) -> User | None:
        ...

    async def save(self, user: User) -> User:
        """Save and return user with generated ID."""
        ...
```

在 CI 中使用 `mypy --strict` 或 `pyright` 尽早捕获类型错误。对于现有项目，使用每模块覆盖逐步启用严格模式。

### 模式 2：使用现代联合语法

Python 3.10+ 提供更清晰的联合语法。

```python
# Preferred (3.10+)
def find_user(user_id: str) -> User | None:
    ...

def parse_value(v: str) -> int | float | str:
    ...

# Older style (still valid, needed for 3.9)
from typing import Optional, Union

def find_user(user_id: str) -> Optional[User]:
    ...
```

### 模式 3：使用守卫进行类型缩窄

使用条件为类型检查器缩窄类型。

```python
def process_user(user_id: str) -> UserData:
    user = find_user(user_id)

    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")

    # Type checker knows user is User here, not User | None
    return UserData(
        name=user.name,
        email=user.email,
    )

def process_items(items: list[Item | None]) -> list[ProcessedItem]:
    # Filter and narrow types
    valid_items = [item for item in items if item is not None]
    # valid_items is now list[Item]
    return [process(item) for item in valid_items]
```

### 模式 4：泛型类

创建类型安全的可复用容器。

```python
from typing import TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

class Result(Generic[T, E]):
    """Represents either a success value or an error."""

    def __init__(
        self,
        value: T | None = None,
        error: E | None = None,
    ) -> None:
        if (value is None) == (error is None):
            raise ValueError("Exactly one of value or error must be set")
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        """Get value or raise the error."""
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]

    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        if self._error is not None:
            return default
        return self._value  # type: ignore[return-value]

# Usage preserves types
def parse_config(path: str) -> Result[Config, ConfigError]:
    try:
        return Result(value=Config.from_file(path))
    except ConfigError as e:
        return Result(error=e)

result = parse_config("config.yaml")
if result.is_success:
    config = result.unwrap()  # Type: Config
```

## 高级模式

### 模式 5：泛型仓储

创建类型安全的数据访问模式。

```python
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar("T")
ID = TypeVar("ID")

class Repository(ABC, Generic[T, ID]):
    """Generic repository interface."""

    @abstractmethod
    async def get(self, id: ID) -> T | None:
        """Get entity by ID."""
        ...

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save and return entity."""
        ...

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete entity, return True if existed."""
        ...

class UserRepository(Repository[User, str]):
    """Concrete repository for Users with string IDs."""

    async def get(self, id: str) -> User | None:
        row = await self._db.fetchrow(
            "SELECT * FROM users WHERE id = $1", id
        )
        return User(**row) if row else None

    async def save(self, entity: User) -> User:
        ...

    async def delete(self, id: str) -> bool:
        ...
```

### 模式 6：带边界的 TypeVar

将泛型参数限制为特定类型。

```python
from typing import TypeVar
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

def validate_and_create(model_cls: type[ModelT], data: dict) -> ModelT:
    """Create a validated Pydantic model from dict."""
    return model_cls.model_validate(data)

# Works with any BaseModel subclass
class User(BaseModel):
    name: str
    email: str

user = validate_and_create(User, {"name": "Alice", "email": "a@b.com"})
# user is typed as User

# Type error: str is not a BaseModel subclass
result = validate_and_create(str, {"name": "Alice"})  # Error!
```

### 模式 7：用于结构化类型的协议

无需继承即可定义接口。

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    """Any class that can be serialized to/from dict."""

    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serializable":
        ...

# User satisfies Serializable without inheriting from it
class User:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(id=data["id"], name=data["name"])

def serialize(obj: Serializable) -> str:
    """Works with any Serializable object."""
    return json.dumps(obj.to_dict())

# Works - User matches the protocol
serialize(User("1", "Alice"))

# Runtime checking with @runtime_checkable
isinstance(User("1", "Alice"), Serializable)  # True
```

### 模式 8：常见协议模式

定义可复用的结构化接口。

```python
from typing import Protocol

class Closeable(Protocol):
    """Resource that can be closed."""
    def close(self) -> None: ...

class AsyncCloseable(Protocol):
    """Async resource that can be closed."""
    async def close(self) -> None: ...

class Readable(Protocol):
    """Object that can be read from."""
    def read(self, n: int = -1) -> bytes: ...

class HasId(Protocol):
    """Object with an ID property."""
    @property
    def id(self) -> str: ...

class Comparable(Protocol):
    """Object that supports comparison."""
    def __lt__(self, other: "Comparable") -> bool: ...
    def __le__(self, other: "Comparable") -> bool: ...
```

### 模式 9：类型别名

创建有意义的类型名称。

**注意：** `type Alias = ...` 语句语法（PEP 695）是在 **Python 3.12** 中引入的，而不是 3.10。对于目标为早期版本（包括 3.10/3.11）的项目，请使用 `TypeAlias` 注解（PEP 613，自 Python 3.10 起可用）。

```python
# Python 3.12+ type statement (PEP 695)
type UserId = str
type UserDict = dict[str, Any]

# Python 3.12+ type statement with generics (PEP 695)
type Handler[T] = Callable[[Request], T]
type AsyncHandler[T] = Callable[[Request], Awaitable[T]]
```

```python
# Python 3.10-3.11 style (needed for broader compatibility)
from typing import TypeAlias
from collections.abc import Callable, Awaitable

UserId: TypeAlias = str
Handler: TypeAlias = Callable[[Request], Response]
```

```python
# Usage
def register_handler(path: str, handler: Handler[Response]) -> None:
    ...
```

### 模式 10：Callable 类型

为函数参数和回调添加类型。

```python
from collections.abc import Callable, Awaitable

# Sync callback
ProgressCallback = Callable[[int, int], None]  # (current, total)

# Async callback
AsyncHandler = Callable[[Request], Awaitable[Response]]

# With named parameters (using Protocol)
class OnProgress(Protocol):
    def __call__(
        self,
        current: int,
        total: int,
        *,
        message: str = "",
    ) -> None: ...

def process_items(
    items: list[Item],
    on_progress: ProgressCallback | None = None,
) -> list[Result]:
    for i, item in enumerate(items):
        if on_progress:
            on_progress(i, len(items))
        ...
```

## 配置

### 严格模式检查清单

对于 `mypy --strict` 合规：

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
no_implicit_optional = true
```

逐步采用目标：
- 所有函数参数已注解
- 所有返回类型已注解
- 类属性已注解
- 最小化 `Any` 使用（对于真正的动态数据可接受）
- 泛型集合使用类型参数（`list[str]` 而不是 `list`）

对于现有代码库，使用 `# mypy: strict` 按模块启用严格模式，或在 `pyproject.toml` 中配置每模块覆盖。

## 最佳实践总结

1. **注解所有公共 API** - 函数、方法、类属性
2. **使用 `T | None`** - 现代联合语法优于 `Optional[T]`
3. **运行严格类型检查** - CI 中使用 `mypy --strict`
4. **使用泛型** - 在可复用代码中保留类型信息
5. **定义协议** - 接口的结构化类型
6. **缩窄类型** - 使用守卫帮助类型检查器
7. **限制类型变量** - 将泛型限制为有意义的类型
8. **创建类型别名** - 为复杂类型使用有意义的名称
9. **最小化 `Any`** - 使用特定类型或泛型。`Any` 对于真正的动态数据或与非类型化第三方代码交互时是可接受的
10. **用类型记录** - 类型是可强制执行的文档
