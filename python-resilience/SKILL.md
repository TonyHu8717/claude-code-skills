---
name: python-resilience
description: Python 弹性模式，包括自动重试、指数退避、超时和容错装饰器。在添加重试逻辑、实现超时、构建容错服务或处理瞬态故障时使用。
---

# Python 弹性模式

构建能够优雅处理瞬态故障、网络问题和服务中断的容错 Python 应用程序。弹性模式在依赖不可靠时保持系统运行。

## 何时使用此技能

- 为外部服务调用添加重试逻辑
- 为网络操作实现超时
- 构建容错微服务
- 处理速率限制和背压
- 创建基础设施装饰器
- 设计断路器

## 核心概念

### 1. 瞬态 vs 永久故障

重试瞬态错误（网络超时、临时服务问题）。不要重试永久错误（无效凭据、错误请求）。

### 2. 指数退避

增加重试之间的等待时间，以避免压垮正在恢复的服务。

### 3. 抖动

为退避添加随机性，以防止许多客户端同时重试时的惊群效应。

### 4. 有界重试

限制尝试次数和总持续时间，以防止无限重试循环。

## 快速开始

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def call_external_service(request: dict) -> dict:
    return httpx.post("https://api.example.com", json=request).json()
```

## 基础模式

### 模式 1：使用 Tenacity 的基本重试

使用 `tenacity` 库实现生产级重试逻辑。对于更简单的情况，考虑使用内置重试功能或轻量级自定义实现。

```python
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
    retry_if_exception_type,
)

TRANSIENT_ERRORS = (ConnectionError, TimeoutError, OSError)

@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS),
    stop=stop_after_attempt(5) | stop_after_delay(60),
    wait=wait_exponential_jitter(initial=1, max=30),
)
def fetch_data(url: str) -> dict:
    """Fetch data with automatic retry on transient failures."""
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### 模式 2：仅重试适当的错误

白名单特定的瞬态异常。永远不要重试：

- `ValueError`、`TypeError` - 这些是 bug，不是瞬态问题
- `AuthenticationError` - 无效凭据不会变得有效
- HTTP 4xx 错误（除 429 外）- 客户端错误是永久的

```python
from tenacity import retry, retry_if_exception_type
import httpx

# Define what's retryable
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
)

@retry(
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def resilient_api_call(endpoint: str) -> dict:
    """Make API call with retry on network issues."""
    return httpx.get(endpoint, timeout=10).json()
```

### 模式 3：HTTP 状态码重试

重试指示瞬态问题的特定 HTTP 状态码。

```python
from tenacity import retry, retry_if_result, stop_after_attempt
import httpx

RETRY_STATUS_CODES = {429, 502, 503, 504}

def should_retry_response(response: httpx.Response) -> bool:
    """Check if response indicates a retryable error."""
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=retry_if_result(should_retry_response),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def http_request(method: str, url: str, **kwargs) -> httpx.Response:
    """Make HTTP request with retry on transient status codes."""
    return httpx.request(method, url, timeout=30, **kwargs)
```

### 模式 4：组合异常和状态重试

同时处理网络异常和 HTTP 状态码。

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)
import logging
import httpx

logger = logging.getLogger(__name__)

TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectError,
    httpx.ReadTimeout,
)
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

def is_retryable_response(response: httpx.Response) -> bool:
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=(
        retry_if_exception_type(TRANSIENT_EXCEPTIONS) |
        retry_if_result(is_retryable_response)
    ),
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def robust_http_call(
    method: str,
    url: str,
    **kwargs,
) -> httpx.Response:
    """HTTP call with comprehensive retry handling."""
    return httpx.request(method, url, timeout=30, **kwargs)
```

## 高级模式

### 模式 5：记录重试尝试

跟踪重试行为用于调试和告警。

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

def log_retry_attempt(retry_state):
    """Log detailed retry information."""
    exception = retry_state.outcome.exception()
    logger.warning(
        "Retrying operation",
        attempt=retry_state.attempt_number,
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        next_wait_seconds=retry_state.next_action.sleep if retry_state.next_action else None,
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    before_sleep=log_retry_attempt,
)
def call_with_logging(request: dict) -> dict:
    """External call with retry logging."""
    ...
```

### 模式 6：超时装饰器

创建可复用的超时装饰器以实现一致的超时处理。

```python
import asyncio
from functools import wraps
from typing import TypeVar, Callable

T = TypeVar("T")

def with_timeout(seconds: float):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=seconds,
            )
        return wrapper
    return decorator

@with_timeout(30)
async def fetch_with_timeout(url: str) -> dict:
    """Fetch URL with 30 second timeout."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 模式 7：通过装饰器处理横切关注点

堆叠装饰器以将基础设施与业务逻辑分离。

```python
from functools import wraps
from typing import TypeVar, Callable
import structlog

logger = structlog.get_logger()
T = TypeVar("T")

def traced(name: str | None = None):
    """Add tracing to function calls."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        span_name = name or func.__name__

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            logger.info("Operation started", operation=span_name)
            try:
                result = await func(*args, **kwargs)
                logger.info("Operation completed", operation=span_name)
                return result
            except Exception as e:
                logger.error("Operation failed", operation=span_name, error=str(e))
                raise
        return wrapper
    return decorator

# Stack multiple concerns
@traced("fetch_user_data")
@with_timeout(30)
@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter())
async def fetch_user_data(user_id: str) -> dict:
    """Fetch user with tracing, timeout, and retry."""
    ...
```

### 模式 8：依赖注入以实现可测试性

通过构造函数传递基础设施组件以便于测试。

```python
from dataclasses import dataclass
from typing import Protocol

class Logger(Protocol):
    def info(self, msg: str, **kwargs) -> None: ...
    def error(self, msg: str, **kwargs) -> None: ...

class MetricsClient(Protocol):
    def increment(self, metric: str, tags: dict | None = None) -> None: ...
    def timing(self, metric: str, value: float) -> None: ...

@dataclass
class UserService:
    """Service with injected infrastructure."""

    repository: UserRepository
    logger: Logger
    metrics: MetricsClient

    async def get_user(self, user_id: str) -> User:
        self.logger.info("Fetching user", user_id=user_id)
        start = time.perf_counter()

        try:
            user = await self.repository.get(user_id)
            self.metrics.increment("user.fetch.success")
            return user
        except Exception as e:
            self.metrics.increment("user.fetch.error")
            self.logger.error("Failed to fetch user", user_id=user_id, error=str(e))
            raise
        finally:
            elapsed = time.perf_counter() - start
            self.metrics.timing("user.fetch.duration", elapsed)

# Easy to test with fakes
service = UserService(
    repository=FakeRepository(),
    logger=FakeLogger(),
    metrics=FakeMetrics(),
)
```

### 模式 9：安全失败默认值

当非关键操作失败时优雅降级。

```python
from typing import TypeVar
from collections.abc import Callable

T = TypeVar("T")

def fail_safe(default: T, log_failure: bool = True):
    """Return default value on failure instead of raising."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_failure:
                    logger.warning(
                        "Operation failed, using default",
                        function=func.__name__,
                        error=str(e),
                    )
                return default
        return wrapper
    return decorator

@fail_safe(default=[])
async def get_recommendations(user_id: str) -> list[str]:
    """Get recommendations, return empty list on failure."""
    ...
```

## 最佳实践总结

1. **仅重试瞬态错误** - 不要重试 bug 或认证失败
2. **使用指数退避** - 给服务时间恢复
3. **添加抖动** - 防止同步重试导致的惊群效应
4. **限制总持续时间** - `stop_after_attempt(5) | stop_after_delay(60)`
5. **记录每次重试** - 静默重试会隐藏系统性问题
6. **使用装饰器** - 将重试逻辑与业务逻辑分离
7. **注入依赖** - 使基础设施可测试
8. **到处设置超时** - 每个网络调用都需要超时
9. **优雅失败** - 为非关键路径返回缓存/默认值
10. **监控重试率** - 高重试率表示潜在问题
