---
name: cqrs-implementation
description: 实现命令查询职责分离以构建可扩展架构。在分离读写模型、优化查询性能或构建事件溯源系统时使用。
---

# CQRS 实现

实现 CQRS（命令查询职责分离）模式的全面指南。

## 使用场景

- 分离读写关注点
- 独立扩展读和写
- 构建事件溯源系统
- 优化复杂查询场景
- 需要不同的读写数据模型
- 高性能报告需求

## 核心概念

### 1. CQRS 架构

```
                    ┌─────────────┐
                    │   客户端    │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   命令      │          │   查询      │
       │    API      │          │    API      │
       └──────┬──────┘          └──────┬──────┘
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │  命令       │          │   查询      │
       │  处理器     │          │  处理器     │
       └──────┬──────┘          └──────┬──────┘
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   写入      │─────────►│    读取     │
       │   模型      │  事件    │   模型      │
       └─────────────┘          └─────────────┘
```

### 2. 关键组件

| 组件           | 职责                  |
| ------------------- | ------------------------------- |
| **命令**         | 更改状态的意图          |
| **命令处理器** | 验证并执行命令 |
| **事件**           | 状态变更记录          |
| **查询**           | 数据请求                |
| **查询处理器**   | 从读取模型检索数据  |
| **投影器**       | 从事件更新读取模型  |

## 模板

### 模板 1：命令基础设施

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Dict, Any, Type
from datetime import datetime
import uuid

# 命令基类
@dataclass
class Command:
    command_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        self.command_id = self.command_id or str(uuid.uuid4())
        self.timestamp = self.timestamp or datetime.utcnow()


# 具体命令
@dataclass
class CreateOrder(Command):
    customer_id: str
    items: list
    shipping_address: dict


@dataclass
class AddOrderItem(Command):
    order_id: str
    product_id: str
    quantity: int
    price: float


@dataclass
class CancelOrder(Command):
    order_id: str
    reason: str


# 命令处理器基类
T = TypeVar('T', bound=Command)

class CommandHandler(ABC, Generic[T]):
    @abstractmethod
    async def handle(self, command: T) -> Any:
        pass


# 命令总线
class CommandBus:
    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}

    def register(self, command_type: Type[Command], handler: CommandHandler):
        self._handlers[command_type] = handler

    async def dispatch(self, command: Command) -> Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command).__name__}")
        return await handler.handle(command)


# 命令处理器实现
class CreateOrderHandler(CommandHandler[CreateOrder]):
    def __init__(self, order_repository, event_store):
        self.order_repository = order_repository
        self.event_store = event_store

    async def handle(self, command: CreateOrder) -> str:
        # 验证
        if not command.items:
            raise ValueError("订单必须至少包含一个商品")

        # 创建聚合
        order = Order.create(
            customer_id=command.customer_id,
            items=command.items,
            shipping_address=command.shipping_address
        )

        # 持久化事件
        await self.event_store.append_events(
            stream_id=f"Order-{order.id}",
            stream_type="Order",
            events=order.uncommitted_events
        )

        return order.id
```

### 模板 2：查询基础设施

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional

# 查询基类
@dataclass
class Query:
    pass


# 具体查询
@dataclass
class GetOrderById(Query):
    order_id: str


@dataclass
class GetCustomerOrders(Query):
    customer_id: str
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class SearchOrders(Query):
    query: str
    filters: dict = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


# 查询结果类型
@dataclass
class OrderView:
    order_id: str
    customer_id: str
    status: str
    total_amount: float
    item_count: int
    created_at: datetime
    shipped_at: Optional[datetime] = None


@dataclass
class PaginatedResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


# 查询处理器基类
T = TypeVar('T', bound=Query)
R = TypeVar('R')

class QueryHandler(ABC, Generic[T, R]):
    @abstractmethod
    async def handle(self, query: T) -> R:
        pass


# 查询总线
class QueryBus:
    def __init__(self):
        self._handlers: Dict[Type[Query], QueryHandler] = {}

    def register(self, query_type: Type[Query], handler: QueryHandler):
        self._handlers[query_type] = handler

    async def dispatch(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query).__name__}")
        return await handler.handle(query)


# 查询处理器实现
class GetOrderByIdHandler(QueryHandler[GetOrderById, Optional[OrderView]]):
    def __init__(self, read_db):
        self.read_db = read_db

    async def handle(self, query: GetOrderById) -> Optional[OrderView]:
        async with self.read_db.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT order_id, customer_id, status, total_amount,
                       item_count, created_at, shipped_at
                FROM order_views
                WHERE order_id = $1
                """,
                query.order_id
            )
            if row:
                return OrderView(**dict(row))
            return None


class GetCustomerOrdersHandler(QueryHandler[GetCustomerOrders, PaginatedResult[OrderView]]):
    def __init__(self, read_db):
        self.read_db = read_db

    async def handle(self, query: GetCustomerOrders) -> PaginatedResult[OrderView]:
        async with self.read_db.acquire() as conn:
            # 构建带可选状态过滤的查询
            where_clause = "customer_id = $1"
            params = [query.customer_id]

            if query.status:
                where_clause += " AND status = $2"
                params.append(query.status)

            # 获取总数
            total = await conn.fetchval(
                f"SELECT COUNT(*) FROM order_views WHERE {where_clause}",
                *params
            )

            # 获取分页结果
            offset = (query.page - 1) * query.page_size
            rows = await conn.fetch(
                f"""
                SELECT order_id, customer_id, status, total_amount,
                       item_count, created_at, shipped_at
                FROM order_views
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
                """,
                *params, query.page_size, offset
            )

            return PaginatedResult(
                items=[OrderView(**dict(row)) for row in rows],
                total=total,
                page=query.page,
                page_size=query.page_size
            )
```

### 模板 3：FastAPI CQRS 应用

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 请求/响应模型
class CreateOrderRequest(BaseModel):
    customer_id: str
    items: List[dict]
    shipping_address: dict


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    status: str
    total_amount: float
    item_count: int
    created_at: datetime


# 依赖注入
def get_command_bus() -> CommandBus:
    return app.state.command_bus


def get_query_bus() -> QueryBus:
    return app.state.query_bus


# 命令端点（POST, PUT, DELETE）
@app.post("/orders", response_model=dict)
async def create_order(
    request: CreateOrderRequest,
    command_bus: CommandBus = Depends(get_command_bus)
):
    command = CreateOrder(
        customer_id=request.customer_id,
        items=request.items,
        shipping_address=request.shipping_address
    )
    order_id = await command_bus.dispatch(command)
    return {"order_id": order_id}


@app.post("/orders/{order_id}/items")
async def add_item(
    order_id: str,
    product_id: str,
    quantity: int,
    price: float,
    command_bus: CommandBus = Depends(get_command_bus)
):
    command = AddOrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price=price
    )
    await command_bus.dispatch(command)
    return {"status": "item_added"}


@app.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    reason: str,
    command_bus: CommandBus = Depends(get_command_bus)
):
    command = CancelOrder(order_id=order_id, reason=reason)
    await command_bus.dispatch(command)
    return {"status": "cancelled"}


# 查询端点（GET）
@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    query_bus: QueryBus = Depends(get_query_bus)
):
    query = GetOrderById(order_id=order_id)
    result = await query_bus.dispatch(query)
    if not result:
        raise HTTPException(status_code=404, detail="订单未找到")
    return result


@app.get("/customers/{customer_id}/orders")
async def get_customer_orders(
    customer_id: str,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    query_bus: QueryBus = Depends(get_query_bus)
):
    query = GetCustomerOrders(
        customer_id=customer_id,
        status=status,
        page=page,
        page_size=page_size
    )
    return await query_bus.dispatch(query)


@app.get("/orders/search")
async def search_orders(
    q: str,
    sort_by: str = "created_at",
    query_bus: QueryBus = Depends(get_query_bus)
):
    query = SearchOrders(query=q, sort_by=sort_by)
    return await query_bus.dispatch(query)
```

### 模板 4：读取模型同步

```python
class ReadModelSynchronizer:
    """保持读取模型与事件同步。"""

    def __init__(self, event_store, read_db, projections: List[Projection]):
        self.event_store = event_store
        self.read_db = read_db
        self.projections = {p.name: p for p in projections}

    async def run(self):
        """持续同步读取模型。"""
        while True:
            for name, projection in self.projections.items():
                await self._sync_projection(projection)
            await asyncio.sleep(0.1)

    async def _sync_projection(self, projection: Projection):
        checkpoint = await self._get_checkpoint(projection.name)

        events = await self.event_store.read_all(
            from_position=checkpoint,
            limit=100
        )

        for event in events:
            if event.event_type in projection.handles():
                try:
                    await projection.apply(event)
                except Exception as e:
                    # 记录错误，可能重试或跳过
                    logger.error(f"投影错误: {e}")
                    continue

            await self._save_checkpoint(projection.name, event.global_position)

    async def rebuild_projection(self, projection_name: str):
        """从头重建投影。"""
        projection = self.projections[projection_name]

        # 清除现有数据
        await projection.clear()

        # 重置检查点
        await self._save_checkpoint(projection_name, 0)

        # 重建
        while True:
            checkpoint = await self._get_checkpoint(projection_name)
            events = await self.event_store.read_all(checkpoint, 1000)

            if not events:
                break

            for event in events:
                if event.event_type in projection.handles():
                    await projection.apply(event)

            await self._save_checkpoint(
                projection_name,
                events[-1].global_position
            )
```

### 模板 5：最终一致性处理

```python
class ConsistentQueryHandler:
    """可以等待一致性的查询处理器。"""

    def __init__(self, read_db, event_store):
        self.read_db = read_db
        self.event_store = event_store

    async def query_after_command(
        self,
        query: Query,
        expected_version: int,
        stream_id: str,
        timeout: float = 5.0
    ):
        """
        执行查询，确保读取模型达到预期版本。
        用于读取自己写入的一致性。
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 检查读取模型是否已跟上
            projection_version = await self._get_projection_version(stream_id)

            if projection_version >= expected_version:
                return await self.execute_query(query)

            # 等待一会儿再重试
            await asyncio.sleep(0.1)

        # 超时 - 返回过期数据并附带警告
        return {
            "data": await self.execute_query(query),
            "_warning": "数据可能已过期"
        }

    async def _get_projection_version(self, stream_id: str) -> int:
        """获取流的最后处理事件版本。"""
        async with self.read_db.acquire() as conn:
            return await conn.fetchval(
                "SELECT last_event_version FROM projection_state WHERE stream_id = $1",
                stream_id
            ) or 0
```

## 最佳实践

### 应该做

- **分离命令和查询模型** - 不同的需求
- **使用最终一致性** - 接受传播延迟
- **在命令处理器中验证** - 在状态变更之前
- **反规范化读取模型** - 为查询优化
- **版本化事件** - 用于 schema 演进

### 不应该做

- **不要在命令中查询** - 仅用于写入
- **不要耦合读写 schema** - 独立演进
- **不要过度工程** - 从简单开始
- **不要忽略一致性 SLA** - 定义可接受的延迟
