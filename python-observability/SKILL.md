---
name: python-observability
description: Python 可观测性模式，包括结构化日志、指标和分布式追踪。在添加日志、实现指标收集、设置追踪或调试生产系统时使用。
---

# Python 可观测性

使用结构化日志、指标和追踪来检测 Python 应用程序。当生产环境出现问题时，你需要在不部署新代码的情况下回答"什么、在哪里以及为什么"。

## 何时使用此技能

- 为应用程序添加结构化日志
- 使用 Prometheus 实现指标收集
- 跨服务设置分布式追踪
- 在请求链中传播关联 ID
- 调试生产问题
- 构建可观测性仪表板

## 核心概念

### 1. 结构化日志

在生产环境中以 JSON 形式发出日志，包含一致的字段。机器可读的日志支持强大的查询和告警。对于本地开发，考虑使用人类可读的格式。

### 2. 四个黄金信号

跟踪每个服务边界的延迟、流量、错误和饱和度。

### 3. 关联 ID

为单个请求在所有日志和 span 中贯穿唯一 ID，实现端到端追踪。

### 4. 有界基数

保持指标标签值有界。无界标签（如用户 ID）会导致存储成本爆炸。

## 快速开始

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()
logger.info("Request processed", user_id="123", duration_ms=45)
```

## 基础模式

### 模式 1：使用 Structlog 的结构化日志

配置 structlog 以输出包含一致字段的 JSON。

```python
import logging
import structlog

def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Initialize at application startup
configure_logging("INFO")
logger = structlog.get_logger()
```

### 模式 2：一致的日志字段

每个日志条目应包含用于过滤和关联的标准字段。

```python
import structlog
from contextvars import ContextVar

# Store correlation ID in context
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

logger = structlog.get_logger()

def process_request(request: Request) -> Response:
    """Process request with structured logging."""
    logger.info(
        "Request received",
        correlation_id=correlation_id.get(),
        method=request.method,
        path=request.path,
        user_id=request.user_id,
    )

    try:
        result = handle_request(request)
        logger.info(
            "Request completed",
            correlation_id=correlation_id.get(),
            status_code=200,
            duration_ms=elapsed,
        )
        return result
    except Exception as e:
        logger.error(
            "Request failed",
            correlation_id=correlation_id.get(),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        raise
```

### 模式 3：语义化日志级别

在整个应用程序中一致地使用日志级别。

| 级别 | 用途 | 示例 |
|-------|---------|----------|
| `DEBUG` | 开发诊断 | 变量值、内部状态 |
| `INFO` | 请求生命周期、操作 | 请求开始/结束、作业完成 |
| `WARNING` | 可恢复的异常 | 重试尝试、使用回退 |
| `ERROR` | 需要关注的失败 | 异常、服务不可用 |

```python
# DEBUG: Detailed internal information
logger.debug("Cache lookup", key=cache_key, hit=cache_hit)

# INFO: Normal operational events
logger.info("Order created", order_id=order.id, total=order.total)

# WARNING: Abnormal but handled situations
logger.warning(
    "Rate limit approaching",
    current_rate=950,
    limit=1000,
    reset_seconds=30,
)

# ERROR: Failures requiring investigation
logger.error(
    "Payment processing failed",
    order_id=order.id,
    error=str(e),
    payment_provider="stripe",
)
```

永远不要将预期行为记录为 `ERROR`。用户输入错误密码是 `INFO`，而不是 `ERROR`。

### 模式 4：关联 ID 传播

在入口生成唯一 ID 并在所有操作中贯穿。

```python
from contextvars import ContextVar
import uuid
import structlog

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def set_correlation_id(cid: str | None = None) -> str:
    """Set correlation ID for current context."""
    cid = cid or str(uuid.uuid4())
    correlation_id.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid)
    return cid

# FastAPI middleware example
from fastapi import Request

async def correlation_middleware(request: Request, call_next):
    """Middleware to set and propagate correlation ID."""
    # Use incoming header or generate new
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    set_correlation_id(cid)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response
```

传播到出站请求：

```python
import httpx

async def call_downstream_service(endpoint: str, data: dict) -> dict:
    """Call downstream service with correlation ID."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=data,
            headers={"X-Correlation-ID": correlation_id.get()},
        )
        return response.json()
```

## 高级模式

### 模式 5：使用 Prometheus 的四个黄金信号

为每个服务边界跟踪这些指标：

```python
from prometheus_client import Counter, Histogram, Gauge

# Latency: How long requests take
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint", "status"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)

# Traffic: Request rate
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

# Errors: Error rate
ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "error_type"],
)

# Saturation: Resource utilization
DB_POOL_USAGE = Gauge(
    "db_connection_pool_used",
    "Number of database connections in use",
)
```

为端点添加检测：

```python
import time
from functools import wraps

def track_request(func):
    """Decorator to track request metrics."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        method = request.method
        endpoint = request.url.path
        start = time.perf_counter()

        try:
            response = await func(request, *args, **kwargs)
            status = str(response.status_code)
            return response
        except Exception as e:
            status = "500"
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type=type(e).__name__,
            ).inc()
            raise
        finally:
            duration = time.perf_counter() - start
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint, status=status).observe(duration)

    return wrapper
```

### 模式 6：有界基数

避免使用无界值的标签以防止指标爆炸。

```python
# BAD: User ID has potentially millions of values
REQUEST_COUNT.labels(method="GET", user_id=user.id)  # Don't do this!

# GOOD: Bounded values only
REQUEST_COUNT.labels(method="GET", endpoint="/users", status="200")

# If you need per-user metrics, use a different approach:
# - Log the user_id and query logs
# - Use a separate analytics system
# - Bucket users by type/tier
REQUEST_COUNT.labels(
    method="GET",
    endpoint="/users",
    user_tier="premium",  # Bounded set of values
)
```

### 模式 7：带上下文管理器的计时操作

创建可复用的计时上下文管理器用于操作。

```python
from contextlib import contextmanager
import time
import structlog

logger = structlog.get_logger()

@contextmanager
def timed_operation(name: str, **extra_fields):
    """Context manager for timing and logging operations."""
    start = time.perf_counter()
    logger.debug("Operation started", operation=name, **extra_fields)

    try:
        yield
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error(
            "Operation failed",
            operation=name,
            duration_ms=round(elapsed_ms, 2),
            error=str(e),
            **extra_fields,
        )
        raise
    else:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Operation completed",
            operation=name,
            duration_ms=round(elapsed_ms, 2),
            **extra_fields,
        )

# Usage
with timed_operation("fetch_user_orders", user_id=user.id):
    orders = await order_repository.get_by_user(user.id)
```

### 模式 8：OpenTelemetry 追踪

使用 OpenTelemetry 设置分布式追踪。

**注意：** OpenTelemetry 正在积极发展中。请查看[官方 Python 文档](https://opentelemetry.io/docs/languages/python/)了解最新的 API 模式和最佳实践。

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def configure_tracing(service_name: str, otlp_endpoint: str) -> None:
    """Configure OpenTelemetry tracing."""
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

async def process_order(order_id: str) -> Order:
    """Process order with tracing."""
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        with tracer.start_as_current_span("validate_order"):
            validate_order(order_id)

        with tracer.start_as_current_span("charge_payment"):
            charge_payment(order_id)

        with tracer.start_as_current_span("send_confirmation"):
            send_confirmation(order_id)

        return order
```

## 最佳实践总结

1. **使用结构化日志** - 带有一致字段的 JSON 日志
2. **传播关联 ID** - 在所有请求和日志中贯穿
3. **跟踪四个黄金信号** - 延迟、流量、错误、饱和度
4. **限制标签基数** - 永远不要使用无界值作为指标标签
5. **在适当的级别记录** - 不要用 ERROR 虚报狼来了
6. **包含上下文** - 日志中的用户 ID、请求 ID、操作名称
7. **使用上下文管理器** - 一致的计时和错误处理
8. **关注点分离** - 可观测性代码不应污染业务逻辑
9. **测试可观测性** - 在集成测试中验证日志和指标
10. **设置告警** - 没有告警的指标是无用的
