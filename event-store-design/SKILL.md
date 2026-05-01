---
name: event-store-design
description: 为事件溯源系统设计和实现事件存储。在构建事件溯源基础设施、选择事件存储技术或实现事件持久化模式时使用。
---

# 事件存储设计

事件溯源应用程序事件存储设计的综合指南。

## 何时使用此技能

- 设计事件溯源基础设施
- 选择事件存储技术
- 实现自定义事件存储
- 优化事件存储和检索
- 设置事件存储模式
- 规划事件存储扩展

## 核心概念

### 1. 事件存储架构

```
┌─────────────────────────────────────────────────────┐
│                    事件存储                           │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   流 1       │  │   流 2       │  │   流 3       │ │
│  │ (聚合)       │  │ (聚合)       │  │ (聚合)       │ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤ │
│  │ 事件 1      │  │ 事件 1      │  │ 事件 1      │ │
│  │ 事件 2      │  │ 事件 2      │  │ 事件 2      │ │
│  │ 事件 3      │  │ ...         │  │ 事件 3      │ │
│  │ ...         │  │             │  │ 事件 4      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  全局位置: 1 → 2 → 3 → 4 → 5 → 6 → ...             │
└─────────────────────────────────────────────────────┘
```

### 2. 事件存储要求

| 要求       | 描述                        |
| ----------------- | ---------------------------------- |
| **仅追加**   | 事件不可变，只能追加 |
| **有序**       | 按流和全局排序     |
| **版本化**     | 乐观并发控制     |
| **订阅** | 实时事件通知      |
| **幂等**    | 安全处理重复写入     |

## 技术比较

| 技术       | 最适合                  | 局限性                      |
| ---------------- | ------------------------- | -------------------------------- |
| **EventStoreDB** | 纯事件溯源       | 单一用途                   |
| **PostgreSQL**   | 现有 Postgres 技术栈   | 手动实现            |
| **Kafka**        | 高吞吐量流处理 | 不适合按流查询 |
| **DynamoDB**     | 无服务器，AWS 原生    | 查询局限性                |
| **Marten**       | .NET 生态系统           | .NET 特定                    |

## 模板

### 模板 1：PostgreSQL 事件存储模式

```sql
-- 事件表
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id VARCHAR(255) NOT NULL,
    stream_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version BIGINT NOT NULL,
    global_position BIGSERIAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_stream_version UNIQUE (stream_id, version)
);

-- 流查询索引
CREATE INDEX idx_events_stream_id ON events(stream_id, version);

-- 全局订阅索引
CREATE INDEX idx_events_global_position ON events(global_position);

-- 事件类型查询索引
CREATE INDEX idx_events_event_type ON events(event_type);

-- 时间查询索引
CREATE INDEX idx_events_created_at ON events(created_at);

-- 快照表
CREATE TABLE snapshots (
    stream_id VARCHAR(255) PRIMARY KEY,
    stream_type VARCHAR(255) NOT NULL,
    snapshot_data JSONB NOT NULL,
    version BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 订阅检查点表
CREATE TABLE subscription_checkpoints (
    subscription_id VARCHAR(255) PRIMARY KEY,
    last_position BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 模板 2：Python 事件存储实现

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List
from uuid import UUID, uuid4
import json
import asyncpg

@dataclass
class Event:
    stream_id: str
    event_type: str
    data: dict
    metadata: dict = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    version: Optional[int] = None
    global_position: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class EventStore:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def append_events(
        self,
        stream_id: str,
        stream_type: str,
        events: List[Event],
        expected_version: Optional[int] = None
    ) -> List[Event]:
        """追加事件到流，带乐观并发控制。"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 检查预期版本
                if expected_version is not None:
                    current = await conn.fetchval(
                        "SELECT MAX(version) FROM events WHERE stream_id = $1",
                        stream_id
                    )
                    current = current or 0
                    if current != expected_version:
                        raise ConcurrencyError(
                            f"Expected version {expected_version}, got {current}"
                        )

                # 获取起始版本
                start_version = await conn.fetchval(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM events WHERE stream_id = $1",
                    stream_id
                )

                # 插入事件
                saved_events = []
                for i, event in enumerate(events):
                    event.version = start_version + i
                    row = await conn.fetchrow(
                        """
                        INSERT INTO events (id, stream_id, stream_type, event_type,
                                          event_data, metadata, version, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        RETURNING global_position
                        """,
                        event.event_id,
                        stream_id,
                        stream_type,
                        event.event_type,
                        json.dumps(event.data),
                        json.dumps(event.metadata),
                        event.version,
                        event.created_at
                    )
                    event.global_position = row['global_position']
                    saved_events.append(event)

                return saved_events

    async def read_stream(
        self,
        stream_id: str,
        from_version: int = 0,
        limit: int = 1000
    ) -> List[Event]:
        """从流中读取事件。"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, stream_id, event_type, event_data, metadata,
                       version, global_position, created_at
                FROM events
                WHERE stream_id = $1 AND version >= $2
                ORDER BY version
                LIMIT $3
                """,
                stream_id, from_version, limit
            )
            return [self._row_to_event(row) for row in rows]

    async def read_all(
        self,
        from_position: int = 0,
        limit: int = 1000
    ) -> List[Event]:
        """全局读取所有事件。"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, stream_id, event_type, event_data, metadata,
                       version, global_position, created_at
                FROM events
                WHERE global_position > $1
                ORDER BY global_position
                LIMIT $2
                """,
                from_position, limit
            )
            return [self._row_to_event(row) for row in rows]

    async def subscribe(
        self,
        subscription_id: str,
        handler,
        from_position: int = 0,
        batch_size: int = 100
    ):
        """从位置开始订阅所有事件。"""
        # 获取检查点
        async with self.pool.acquire() as conn:
            checkpoint = await conn.fetchval(
                """
                SELECT last_position FROM subscription_checkpoints
                WHERE subscription_id = $1
                """,
                subscription_id
            )
            position = checkpoint or from_position

        while True:
            events = await self.read_all(position, batch_size)
            if not events:
                await asyncio.sleep(1)  # 轮询间隔
                continue

            for event in events:
                await handler(event)
                position = event.global_position

            # 保存检查点
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO subscription_checkpoints (subscription_id, last_position)
                    VALUES ($1, $2)
                    ON CONFLICT (subscription_id)
                    DO UPDATE SET last_position = $2, updated_at = NOW()
                    """,
                    subscription_id, position
                )

    def _row_to_event(self, row) -> Event:
        return Event(
            event_id=row['id'],
            stream_id=row['stream_id'],
            event_type=row['event_type'],
            data=json.loads(row['event_data']),
            metadata=json.loads(row['metadata']),
            version=row['version'],
            global_position=row['global_position'],
            created_at=row['created_at']
        )


class ConcurrencyError(Exception):
    """当乐观并发检查失败时引发。"""
    pass
```

### 模板 3：EventStoreDB 用法

```python
from esdbclient import EventStoreDBClient, NewEvent, StreamState
import json

# 连接
client = EventStoreDBClient(uri="esdb://localhost:2113?tls=false")

# 追加事件
def append_events(stream_name: str, events: list, expected_revision=None):
    new_events = [
        NewEvent(
            type=event['type'],
            data=json.dumps(event['data']).encode(),
            metadata=json.dumps(event.get('metadata', {})).encode()
        )
        for event in events
    ]

    if expected_revision is None:
        state = StreamState.ANY
    elif expected_revision == -1:
        state = StreamState.NO_STREAM
    else:
        state = expected_revision

    return client.append_to_stream(
        stream_name=stream_name,
        events=new_events,
        current_version=state
    )

# 读取流
def read_stream(stream_name: str, from_revision: int = 0):
    events = client.get_stream(
        stream_name=stream_name,
        stream_position=from_revision
    )
    return [
        {
            'type': event.type,
            'data': json.loads(event.data),
            'metadata': json.loads(event.metadata) if event.metadata else {},
            'stream_position': event.stream_position,
            'commit_position': event.commit_position
        }
        for event in events
    ]

# 订阅所有
async def subscribe_to_all(handler, from_position: int = 0):
    subscription = client.subscribe_to_all(commit_position=from_position)
    async for event in subscription:
        await handler({
            'type': event.type,
            'data': json.loads(event.data),
            'stream_id': event.stream_name,
            'position': event.commit_position
        })

# 类别投影（$ce-Category）
def read_category(category: str):
    """使用系统投影读取类别所有事件。"""
    return read_stream(f"$ce-{category}")
```

### 模板 4：DynamoDB 事件存储

```python
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import json
import uuid

class DynamoEventStore:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def append_events(self, stream_id: str, events: list, expected_version: int = None):
        """带条件写入的并发追加事件。"""
        with self.table.batch_writer() as batch:
            for i, event in enumerate(events):
                version = (expected_version or 0) + i + 1
                item = {
                    'PK': f"STREAM#{stream_id}",
                    'SK': f"VERSION#{version:020d}",
                    'GSI1PK': 'EVENTS',
                    'GSI1SK': datetime.utcnow().isoformat(),
                    'event_id': str(uuid.uuid4()),
                    'stream_id': stream_id,
                    'event_type': event['type'],
                    'event_data': json.dumps(event['data']),
                    'version': version,
                    'created_at': datetime.utcnow().isoformat()
                }
                batch.put_item(Item=item)
        return events

    def read_stream(self, stream_id: str, from_version: int = 0):
        """从流中读取事件。"""
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f"STREAM#{stream_id}") &
                                  Key('SK').gte(f"VERSION#{from_version:020d}")
        )
        return [
            {
                'event_type': item['event_type'],
                'data': json.loads(item['event_data']),
                'version': item['version']
            }
            for item in response['Items']
        ]

# 表定义（CloudFormation/Terraform）
"""
DynamoDB 表:
  - PK（分区键）: String
  - SK（排序键）: String
  - GSI1PK、GSI1SK 用于全局排序

容量: 基于吞吐量需求的按需或预置容量
"""
```

## 最佳实践

### 应该做

- **在流 ID 中包含聚合类型** - `Order-{uuid}`
- **包含关联/因果 ID** - 用于追踪
- **从第一天开始版本化事件** - 为模式演进做规划
- **实现幂等性** - 使用事件 ID 进行去重
- **适当建立索引** - 根据查询模式

### 不应该做

- **不要更新或删除事件** - 它们是不可变的事实
- **不要存储大负载** - 保持事件小
- **不要跳过乐观并发** - 防止数据损坏
- **不要忽视背压** - 处理慢消费者
