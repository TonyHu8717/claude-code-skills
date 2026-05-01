---
name: python-background-jobs
description: Python 后台作业模式，包括任务队列、工作进程和事件驱动架构。在实现异步任务处理、作业队列、长时间运行的操作或将工作从请求/响应循环中解耦时使用。
---

# Python 后台作业与任务队列

将长时间运行或不可靠的工作从请求/响应循环中解耦。立即返回给用户，同时后台工作进程异步处理繁重的工作。

## 何时使用此技能

- 处理耗时超过几秒的任务
- 发送电子邮件、通知或 webhook
- 生成报告或导出数据
- 处理上传或媒体转换
- 与不可靠的外部服务集成
- 构建事件驱动架构

## 核心概念

### 1. 任务队列模式

API 接受请求，将作业入队，立即返回作业 ID。工作进程异步处理作业。

### 2. 幂等性

任务在失败时可能会重试。设计为安全的重新执行。

### 3. 作业状态机

作业通过状态转换：pending -> running -> succeeded/failed。

### 4. 至少一次传递

大多数队列保证至少一次传递。你的代码必须处理重复。

## 快速开始

此技能使用 Celery 作为示例，这是一个被广泛采用的任务队列。RQ、Dramatiq 和云原生解决方案（AWS SQS、GCP Tasks）等替代方案同样是有效的选择。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

@app.task
def send_email(to: str, subject: str, body: str) -> None:
    # This runs in a background worker
    email_client.send(to, subject, body)

# In your API handler
send_email.delay("user@example.com", "Welcome!", "Thanks for signing up")
```

## 基础模式

### 模式 1：立即返回作业 ID

对于超过几秒的操作，返回作业 ID 并异步处理。

```python
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

@dataclass
class Job:
    id: str
    status: JobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict | None = None
    error: str | None = None

# API endpoint
async def start_export(request: ExportRequest) -> JobResponse:
    """Start export job and return job ID."""
    job_id = str(uuid4())

    # Persist job record
    await jobs_repo.create(Job(
        id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
    ))

    # Enqueue task for background processing
    await task_queue.enqueue(
        "export_data",
        job_id=job_id,
        params=request.model_dump(),
    )

    # Return immediately with job ID
    return JobResponse(
        job_id=job_id,
        status="pending",
        poll_url=f"/jobs/{job_id}",
    )
```

### 模式 2：Celery 任务配置

使用适当的重试和超时配置 Celery 任务。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

# Global configuration
app.conf.update(
    task_time_limit=3600,          # Hard limit: 1 hour
    task_soft_time_limit=3000,      # Soft limit: 50 minutes
    task_acks_late=True,            # Acknowledge after completion
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,   # Don't prefetch too many tasks
)

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
)
def process_payment(self, payment_id: str) -> dict:
    """Process payment with automatic retry on transient errors."""
    try:
        result = payment_gateway.charge(payment_id)
        return {"status": "success", "transaction_id": result.id}
    except PaymentDeclinedError as e:
        # Don't retry permanent failures
        return {"status": "declined", "reason": str(e)}
    except TransientError as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
```

### 模式 3：使任务幂等

工作进程在崩溃或超时时可能会重试。设计为安全的重新执行。

```python
@app.task(bind=True)
def process_order(self, order_id: str) -> None:
    """Process order idempotently."""
    order = orders_repo.get(order_id)

    # Already processed? Return early
    if order.status == OrderStatus.COMPLETED:
        logger.info("Order already processed", order_id=order_id)
        return

    # Already in progress? Check if we should continue
    if order.status == OrderStatus.PROCESSING:
        # Use idempotency key to avoid double-charging
        pass

    # Process with idempotency key
    result = payment_provider.charge(
        amount=order.total,
        idempotency_key=f"order-{order_id}",  # Critical!
    )

    orders_repo.update(order_id, status=OrderStatus.COMPLETED)
```

**幂等性策略：**

1. **写前检查**：在操作前验证状态
2. **幂等键**：与外部服务使用唯一令牌
3. **Upsert 模式**：`INSERT ... ON CONFLICT UPDATE`
4. **去重窗口**：跟踪已处理的 ID N 小时

### 模式 4：作业状态管理

持久化作业状态转换以实现可见性和调试。

```python
class JobRepository:
    """Repository for managing job state."""

    async def create(self, job: Job) -> Job:
        """Create new job record."""
        await self._db.execute(
            """INSERT INTO jobs (id, status, created_at)
               VALUES ($1, $2, $3)""",
            job.id, job.status.value, job.created_at,
        )
        return job

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        **fields,
    ) -> None:
        """Update job status with timestamp."""
        updates = {"status": status.value, **fields}

        if status == JobStatus.RUNNING:
            updates["started_at"] = datetime.utcnow()
        elif status in (JobStatus.SUCCEEDED, JobStatus.FAILED):
            updates["completed_at"] = datetime.utcnow()

        await self._db.execute(
            "UPDATE jobs SET status = $1, ... WHERE id = $2",
            updates, job_id,
        )

        logger.info(
            "Job status updated",
            job_id=job_id,
            status=status.value,
        )
```

## 高级模式

### 模式 5：死信队列

处理永久失败的任务以进行人工检查。

```python
@app.task(bind=True, max_retries=3)
def process_webhook(self, webhook_id: str, payload: dict) -> None:
    """Process webhook with DLQ for failures."""
    try:
        result = send_webhook(payload)
        if not result.success:
            raise WebhookFailedError(result.error)
    except Exception as e:
        if self.request.retries >= self.max_retries:
            # Move to dead letter queue for manual inspection
            dead_letter_queue.send({
                "task": "process_webhook",
                "webhook_id": webhook_id,
                "payload": payload,
                "error": str(e),
                "attempts": self.request.retries + 1,
                "failed_at": datetime.utcnow().isoformat(),
            })
            logger.error(
                "Webhook moved to DLQ after max retries",
                webhook_id=webhook_id,
                error=str(e),
            )
            return

        # Exponential backoff retry
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
```

### 模式 6：状态轮询端点

为客户端提供检查作业状态的端点。

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get current status of a background job."""
    job = await jobs_repo.get(job_id)

    if job is None:
        raise HTTPException(404, f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result=job.result if job.status == JobStatus.SUCCEEDED else None,
        error=job.error if job.status == JobStatus.FAILED else None,
        # Helpful for clients
        is_terminal=job.status in (JobStatus.SUCCEEDED, JobStatus.FAILED),
    )
```

### 模式 7：任务链接和工作流

从简单任务组合复杂工作流。

```python
from celery import chain, group, chord

# Simple chain: A → B → C
workflow = chain(
    extract_data.s(source_id),
    transform_data.s(),
    load_data.s(destination_id),
)

# Parallel execution: A, B, C all at once
parallel = group(
    send_email.s(user_email),
    send_sms.s(user_phone),
    update_analytics.s(event_data),
)

# Chord: Run tasks in parallel, then a callback
# Process all items, then send completion notification
workflow = chord(
    [process_item.s(item_id) for item_id in item_ids],
    send_completion_notification.s(batch_id),
)

workflow.apply_async()
```

### 模式 8：替代任务队列

选择适合你需求的工具。

**RQ（Redis Queue）**：简单，基于 Redis
```python
from rq import Queue
from redis import Redis

queue = Queue(connection=Redis())
job = queue.enqueue(send_email, "user@example.com", "Subject", "Body")
```

**Dramatiq**：现代的 Celery 替代品
```python
import dramatiq
from dramatiq.brokers.redis import RedisBroker

dramatiq.set_broker(RedisBroker())

@dramatiq.actor
def send_email(to: str, subject: str, body: str) -> None:
    email_client.send(to, subject, body)
```

**云原生选项：**
- AWS SQS + Lambda
- Google Cloud Tasks
- Azure Functions

## 最佳实践总结

1. **立即返回** - 不要为长时间操作阻塞请求
2. **持久化作业状态** - 启用状态轮询和调试
3. **使任务幂等** - 任何失败时安全重试
4. **使用幂等键** - 用于外部服务调用
5. **设置超时** - 软限制和硬限制
6. **实现 DLQ** - 捕获永久失败的任务
7. **记录转换** - 跟踪作业状态变更
8. **适当重试** - 瞬态错误使用指数退避
9. **不要重试永久失败** - 验证错误、无效凭据
10. **监控队列深度** - 积压增长时告警
