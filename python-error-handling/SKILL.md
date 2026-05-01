---
name: python-error-handling
description: Python 错误处理模式，包括输入验证、异常层次结构和部分失败处理。在实现验证逻辑、设计异常策略、处理批量处理失败或构建健壮的 API 时使用。
---

# Python 错误处理

通过适当的输入验证、有意义的异常和优雅的失败处理来构建健壮的 Python 应用程序。良好的错误处理使调试更容易，系统更可靠。

## 何时使用此技能

- 验证用户输入和 API 参数
- 为应用程序设计异常层次结构
- 处理批量操作中的部分失败
- 将外部数据转换为域类型
- 构建用户友好的错误消息
- 实现快速失败验证模式

## 核心概念

### 1. 快速失败

尽早验证输入，在昂贵的操作之前。尽可能一次性报告所有验证错误。

### 2. 有意义的异常

使用带有上下文的适当异常类型。消息应解释什么失败了、为什么以及如何修复。

### 3. 部分失败

在批量操作中，不要让一个失败中止所有操作。分别跟踪成功和失败。

### 4. 保留上下文

链接异常以维护完整的错误跟踪路径用于调试。

## 快速开始

```python
def fetch_page(url: str, page_size: int) -> Page:
    if not url:
        raise ValueError("'url' is required")
    if not 1 <= page_size <= 100:
        raise ValueError(f"'page_size' must be 1-100, got {page_size}")
    # Now safe to proceed...
```

## 基础模式

### 模式 1：早期输入验证

在任何处理开始之前，在 API 边界验证所有输入。

```python
def process_order(
    order_id: str,
    quantity: int,
    discount_percent: float,
) -> OrderResult:
    """Process an order with validation."""
    # Validate required fields
    if not order_id:
        raise ValueError("'order_id' is required")

    # Validate ranges
    if quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")

    if not 0 <= discount_percent <= 100:
        raise ValueError(
            f"'discount_percent' must be 0-100, got {discount_percent}"
        )

    # Validation passed, proceed with processing
    return _process_validated_order(order_id, quantity, discount_percent)
```

### 模式 2：尽早转换为域类型

在系统边界将字符串和外部数据解析为类型化的域对象。

```python
from enum import Enum

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"

def parse_output_format(value: str) -> OutputFormat:
    """Parse string to OutputFormat enum.

    Args:
        value: Format string from user input.

    Returns:
        Validated OutputFormat enum member.

    Raises:
        ValueError: If format is not recognized.
    """
    try:
        return OutputFormat(value.lower())
    except ValueError:
        valid_formats = [f.value for f in OutputFormat]
        raise ValueError(
            f"Invalid format '{value}'. "
            f"Valid options: {', '.join(valid_formats)}"
        )

# Usage at API boundary
def export_data(data: list[dict], format_str: str) -> bytes:
    output_format = parse_output_format(format_str)  # Fail fast
    # Rest of function uses typed OutputFormat
    ...
```

### 模式 3：使用 Pydantic 进行复杂验证

使用 Pydantic 模型进行结构化输入验证，自动提供错误消息。

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserInput(BaseModel):
    """Input model for user creation."""

    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()

# Usage
try:
    user_input = CreateUserInput(
        email="user@example.com",
        name="john doe",
        age=25,
    )
except ValidationError as e:
    # Pydantic provides detailed error information
    print(e.errors())
```

### 模式 4：映射到标准异常

适当使用 Python 的内置异常类型，根据需要添加上下文。

| 失败类型 | 异常 | 示例 |
|--------------|-----------|---------|
| 无效输入 | `ValueError` | 错误的参数值 |
| 类型错误 | `TypeError` | 期望字符串，得到 int |
| 缺少项 | `KeyError` | 字典键未找到 |
| 操作失败 | `RuntimeError` | 服务不可用 |
| 超时 | `TimeoutError` | 操作时间过长 |
| 文件未找到 | `FileNotFoundError` | 路径不存在 |
| 权限拒绝 | `PermissionError` | 访问被禁止 |

```python
# Good: Specific exception with context
raise ValueError(f"'page_size' must be 1-100, got {page_size}")

# Avoid: Generic exception, no context
raise Exception("Invalid parameter")
```

## 高级模式

### 模式 5：带上下文的自定义异常

创建携带结构化信息的域特定异常。

```python
class ApiError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

class RateLimitError(ApiError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s",
            status_code=429,
        )

# Usage
def handle_response(response: Response) -> dict:
    match response.status_code:
        case 200:
            return response.json()
        case 401:
            raise ApiError("Invalid credentials", 401)
        case 404:
            raise ApiError(f"Resource not found: {response.url}", 404)
        case 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)
        case code if 400 <= code < 500:
            raise ApiError(f"Client error: {response.text}", code)
        case code if code >= 500:
            raise ApiError(f"Server error: {response.text}", code)
```

### 模式 6：异常链接

在重新引发时保留原始异常以维护调试路径。

```python
import httpx

class ServiceError(Exception):
    """High-level service operation failed."""
    pass

def upload_file(path: str) -> str:
    """Upload file and return URL."""
    try:
        with open(path, "rb") as f:
            response = httpx.post("https://upload.example.com", files={"file": f})
            response.raise_for_status()
            return response.json()["url"]
    except FileNotFoundError as e:
        raise ServiceError(f"Upload failed: file not found at '{path}'") from e
    except httpx.HTTPStatusError as e:
        raise ServiceError(
            f"Upload failed: server returned {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        raise ServiceError(f"Upload failed: network error") from e
```

### 模式 7：带部分失败的批量处理

永远不要让一个坏项中止整个批量。逐项跟踪结果。

```python
from dataclasses import dataclass

@dataclass
class BatchResult[T]:
    """Results from batch processing."""

    succeeded: dict[int, T]  # index -> result
    failed: dict[int, Exception]  # index -> error

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)

    @property
    def all_succeeded(self) -> bool:
        return len(self.failed) == 0

def process_batch(items: list[Item]) -> BatchResult[ProcessedItem]:
    """Process items, capturing individual failures.

    Args:
        items: Items to process.

    Returns:
        BatchResult with succeeded and failed items by index.
    """
    succeeded: dict[int, ProcessedItem] = {}
    failed: dict[int, Exception] = {}

    for idx, item in enumerate(items):
        try:
            result = process_single_item(item)
            succeeded[idx] = result
        except Exception as e:
            failed[idx] = e

    return BatchResult(succeeded=succeeded, failed=failed)

# Caller handles partial results
result = process_batch(items)
if not result.all_succeeded:
    logger.warning(
        f"Batch completed with {result.failure_count} failures",
        failed_indices=list(result.failed.keys()),
    )
```

### 模式 8：长时间操作的进度报告

提供批量进度的可见性，而不将业务逻辑耦合到 UI。

```python
from collections.abc import Callable

ProgressCallback = Callable[[int, int, str], None]  # current, total, status

def process_large_batch(
    items: list[Item],
    on_progress: ProgressCallback | None = None,
) -> BatchResult:
    """Process batch with optional progress reporting.

    Args:
        items: Items to process.
        on_progress: Optional callback receiving (current, total, status).
    """
    total = len(items)
    succeeded = {}
    failed = {}

    for idx, item in enumerate(items):
        if on_progress:
            on_progress(idx, total, f"Processing {item.id}")

        try:
            succeeded[idx] = process_single_item(item)
        except Exception as e:
            failed[idx] = e

    if on_progress:
        on_progress(total, total, "Complete")

    return BatchResult(succeeded=succeeded, failed=failed)
```

## 最佳实践总结

1. **尽早验证** - 在昂贵操作之前检查输入
2. **使用特定异常** - `ValueError`、`TypeError`，而不是通用 `Exception`
3. **包含上下文** - 消息应解释什么、为什么以及如何修复
4. **在边界转换类型** - 尽早将字符串解析为枚举/域类型
5. **链接异常** - 使用 `raise ... from e` 保留调试信息
6. **处理部分失败** - 不要因单个项错误而中止批量
7. **使用 Pydantic** - 用于带结构化错误的复杂输入验证
8. **记录失败模式** - 文档字符串应列出可能的异常
9. **带上下文记录** - 包含 ID、计数和其他调试信息
10. **测试错误路径** - 验证异常是否正确引发
