---
name: python-resource-management
description: 使用上下文管理器、清理模式和流式传输进行 Python 资源管理。在管理连接、文件句柄、实现清理逻辑或构建带累积状态的流式响应时使用。
---

# Python 资源管理

使用上下文管理器确定性地管理资源。数据库连接、文件句柄和网络套接字等资源应可靠释放，即使发生异常也是如此。

## 何时使用此技能

- 管理数据库连接和连接池
- 处理文件句柄和 I/O
- 实现自定义上下文管理器
- 构建带状态的流式响应
- 处理嵌套资源清理
- 创建异步上下文管理器

## 核心概念

### 1. 上下文管理器

`with` 语句确保资源自动释放，即使发生异常也是如此。

### 2. 协议方法

`__enter__`/`__exit__` 用于同步，`__aenter__`/`__aexit__` 用于异步资源管理。

### 3. 无条件清理

`__exit__` 始终运行，无论是否发生异常。

### 4. 异常处理

从 `__exit__` 返回 `True` 以抑制异常，返回 `False` 以传播它们。

## 快速开始

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.cleanup()

with managed_resource() as r:
    r.do_work()
```

## 基础模式

### 模式 1：基于类的上下文管理器

为复杂资源实现上下文管理器协议。

```python
class DatabaseConnection:
    """Database connection with automatic cleanup."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: Connection | None = None

    def connect(self) -> None:
        """Establish database connection."""
        self._conn = psycopg.connect(self._dsn)

    def close(self) -> None:
        """Close connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DatabaseConnection":
        """Enter context: connect and return self."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context: always close connection."""
        self.close()

# Usage with context manager (preferred)
with DatabaseConnection(dsn) as db:
    result = db.execute(query)

# Manual management when needed
db = DatabaseConnection(dsn)
db.connect()
try:
    result = db.execute(query)
finally:
    db.close()
```

### 模式 2：异步上下文管理器

对于异步资源，实现异步协议。

```python
class AsyncDatabasePool:
    """Async database connection pool."""

    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> "AsyncDatabasePool":
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(
            self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close all connections in pool."""
        if self._pool is not None:
            await self._pool.close()

    async def execute(self, query: str, *args) -> list[dict]:
        """Execute query using pooled connection."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

# Usage
async with AsyncDatabasePool(dsn) as pool:
    users = await pool.execute("SELECT * FROM users WHERE active = $1", True)
```

### 模式 3：使用 @contextmanager 装饰器

对于简单情况，使用装饰器简化上下文管理器。

```python
from contextlib import contextmanager, asynccontextmanager
import time
import structlog

logger = structlog.get_logger()

@contextmanager
def timed_block(name: str):
    """Time a block of code."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{name} completed", duration_seconds=round(elapsed, 3))

# Usage
with timed_block("data_processing"):
    process_large_dataset()

@asynccontextmanager
async def database_transaction(conn: AsyncConnection):
    """Manage database transaction."""
    await conn.execute("BEGIN")
    try:
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise

# Usage
async with database_transaction(conn) as tx:
    await tx.execute("INSERT INTO users ...")
    await tx.execute("INSERT INTO audit_log ...")
```

### 模式 4：无条件资源释放

无论是否发生异常，始终在 `__exit__` 中清理资源。

```python
class FileProcessor:
    """Process file with guaranteed cleanup."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._file: IO | None = None
        self._temp_files: list[Path] = []

    def __enter__(self) -> "FileProcessor":
        self._file = open(self._path, "r")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Clean up all resources unconditionally."""
        # Close main file
        if self._file is not None:
            self._file.close()

        # Clean up any temporary files
        for temp_file in self._temp_files:
            try:
                temp_file.unlink()
            except OSError:
                pass  # Best effort cleanup

        # Return None/False to propagate any exception
```

## 高级模式

### 模式 5：选择性异常抑制

仅抑制特定的、已记录的异常。

```python
class StreamWriter:
    """Writer that handles broken pipe gracefully."""

    def __init__(self, stream) -> None:
        self._stream = stream

    def __enter__(self) -> "StreamWriter":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Clean up, suppressing BrokenPipeError on shutdown."""
        self._stream.close()

        # Suppress BrokenPipeError (client disconnected)
        # This is expected behavior, not an error
        if exc_type is BrokenPipeError:
            return True  # Exception suppressed

        return False  # Propagate all other exceptions
```

### 模式 6：带累积状态的流式传输

在流式传输期间维护增量块和累积状态。

```python
from collections.abc import Generator
from dataclasses import dataclass, field

@dataclass
class StreamingResult:
    """Accumulated streaming result."""

    chunks: list[str] = field(default_factory=list)
    _finalized: bool = False

    @property
    def content(self) -> str:
        """Get accumulated content."""
        return "".join(self.chunks)

    def add_chunk(self, chunk: str) -> None:
        """Add chunk to accumulator."""
        if self._finalized:
            raise RuntimeError("Cannot add to finalized result")
        self.chunks.append(chunk)

    def finalize(self) -> str:
        """Mark stream complete and return content."""
        self._finalized = True
        return self.content

def stream_with_accumulation(
    response: StreamingResponse,
) -> Generator[tuple[str, str], None, str]:
    """Stream response while accumulating content.

    Yields:
        Tuple of (accumulated_content, new_chunk) for each chunk.

    Returns:
        Final accumulated content.
    """
    result = StreamingResult()

    for chunk in response.iter_content():
        result.add_chunk(chunk)
        yield result.content, chunk

    return result.finalize()
```

### 模式 7：高效的字符串累积

避免累积时的 O(n^2) 字符串拼接。

```python
def accumulate_stream(stream) -> str:
    """Efficiently accumulate stream content."""
    # BAD: O(n²) due to string immutability
    # content = ""
    # for chunk in stream:
    #     content += chunk  # Creates new string each time

    # GOOD: O(n) with list and join
    chunks: list[str] = []
    for chunk in stream:
        chunks.append(chunk)
    return "".join(chunks)  # Single allocation
```

### 模式 8：跟踪流式指标

测量首字节时间和总流式传输时间。

```python
import time
from collections.abc import Generator

def stream_with_metrics(
    response: StreamingResponse,
) -> Generator[str, None, dict]:
    """Stream response while collecting metrics.

    Yields:
        Content chunks.

    Returns:
        Metrics dictionary.
    """
    start = time.perf_counter()
    first_chunk_time: float | None = None
    chunk_count = 0
    total_bytes = 0

    for chunk in response.iter_content():
        if first_chunk_time is None:
            first_chunk_time = time.perf_counter() - start

        chunk_count += 1
        total_bytes += len(chunk.encode())
        yield chunk

    total_time = time.perf_counter() - start

    return {
        "time_to_first_byte_ms": round((first_chunk_time or 0) * 1000, 2),
        "total_time_ms": round(total_time * 1000, 2),
        "chunk_count": chunk_count,
        "total_bytes": total_bytes,
    }
```

### 模式 9：使用 ExitStack 管理多个资源

干净地处理动态数量的资源。

```python
from contextlib import ExitStack, AsyncExitStack
from pathlib import Path

def process_files(paths: list[Path]) -> list[str]:
    """Process multiple files with automatic cleanup."""
    results = []

    with ExitStack() as stack:
        # Open all files - they'll all be closed when block exits
        files = [stack.enter_context(open(p)) for p in paths]

        for f in files:
            results.append(f.read())

    return results

async def process_connections(hosts: list[str]) -> list[dict]:
    """Process multiple async connections."""
    results = []

    async with AsyncExitStack() as stack:
        connections = [
            await stack.enter_async_context(connect_to_host(host))
            for host in hosts
        ]

        for conn in connections:
            results.append(await conn.fetch_data())

    return results
```

## 最佳实践总结

1. **始终使用上下文管理器** - 对于任何需要清理的资源
2. **无条件清理** - 即使发生异常 `__exit__` 也会运行
3. **不要意外抑制** - 除非有意抑制，否则返回 `False`
4. **使用 @contextmanager** - 用于简单的资源模式
5. **实现两种协议** - 支持 `with` 和手动管理
6. **使用 ExitStack** - 用于动态数量的资源
7. **高效累积** - 列表 + join，而不是字符串拼接
8. **跟踪指标** - 首字节时间对流式传输很重要
9. **记录行为** - 特别是异常抑制
10. **测试清理路径** - 验证错误时资源是否被释放
