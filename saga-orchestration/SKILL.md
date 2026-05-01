---
name: saga-orchestration
description: 为分布式事务和跨聚合工作流实现 saga 模式。当在微服务间实现分布式事务（2PC 不可用）、为跨越库存/支付/配送服务的失败订单工作流设计补偿操作、为旅行预订系统构建事件驱动的 saga 协调器（需原子性回滚酒店/航班/租车预订）、或调试生产环境中补偿步骤未完成的 saga 卡住状态时使用。
---

# Saga 编排

管理分布式事务和长时间运行业务流程的模式，无需两阶段提交。

## 输入和输出

**您需要提供：**
- 服务边界和所有权（哪个服务拥有哪个步骤）
- 事务要求（哪些步骤必须是原子性的，哪些可以是最终一致的）
- 每个步骤的故障模式（瞬时 vs. 永久，重试策略）
- 每个步骤的 SLA 要求（影响超时配置）
- 现有的事件/消息基础设施（Kafka、RabbitMQ、SQS 等）

**此技能将产生：**
- 包含有序步骤、操作命令和补偿命令的 saga 定义
- 适用于您所选模式的编排器或编排实现
- 每个参与服务的补偿逻辑（幂等的，总是成功的）
- 步骤超时配置，包含每步截止时间
- 监控设置：状态机指标、saga 卡住检测、DLQ 恢复

---

## 何时使用此技能

- 在没有分布式锁的情况下协调多服务事务
- 为部分失败实现补偿事务
- 管理长时间运行的业务工作流（分钟到小时）
- 处理需要原子性的分布式系统中的失败
- 构建订单履行、审批或预订流程
- 用异步补偿替代脆弱的两阶段提交

---

## 核心概念

### Saga 模式类型

```text
编排 (Choreography)                    协调 (Orchestration)
┌─────┐  ┌─────┐  ┌─────┐         ┌─────────────┐
│Svc A│─►│Svc B│─►│Svc C│         │ Orchestrator│
└─────┘  └─────┘  └─────┘         └──────┬──────┘
   │        │        │                   │
   ▼        ▼        ▼             ┌─────┼─────┐
 Event    Event    Event           ▼     ▼     ▼
                                ┌────┐┌────┐┌────┐
每个服务对前一个               │Svc1││Svc2││Svc3│
服务的事件做出反应。           └────┘└────┘└────┘
没有中央协调器。          中央协调器发送命令并跟踪状态。
```

**选择协调模式的场景：** 需要显式的步骤跟踪、重试和集中可见性。更容易调试。

**选择编排模式的场景：** 需要松耦合且服务可以独立演进。更难追踪。

### Saga 执行状态

| 状态            | 描述                                       |
| --------------- | ------------------------------------------ |
| **Started**     | Saga 已启动，第一个步骤已分派              |
| **Pending**     | 等待参与者的步骤回复                       |
| **Compensating** | 某个步骤失败；正在回滚已完成的步骤        |
| **Completed**   | 所有前进步骤成功                           |
| **Failed**      | Saga 失败且所有补偿已完成                  |

### 补偿规则

| 场景                                 | 处理方式                                          |
| ------------------------------------ | ------------------------------------------------- |
| 步骤从未启动                         | 无需补偿（跳过）                                  |
| 步骤成功完成                         | 运行补偿命令                                      |
| 步骤在完成前失败                     | 无需补偿；标记为失败                              |
| 补偿本身失败                         | 带退避重试 → DLQ → 人工干预告警                  |
| 步骤结果不再存在                     | 将补偿视为成功（幂等性）                          |

---

## 模板

### 模板 1：订单履行 Saga（协调模式）

基础协调器的具体子类。定义跨越库存、支付、配送和通知的四个步骤。完整的抽象 `SagaOrchestrator` 基类请参见 `references/advanced-patterns.md`。

```python
from saga_orchestrator import SagaOrchestrator, SagaStep
from typing import Dict, List


class OrderFulfillmentSaga(SagaOrchestrator):
    """跨越四个参与服务编排订单履行。"""

    @property
    def saga_type(self) -> str:
        return "OrderFulfillment"

    def define_steps(self, data: Dict) -> List[SagaStep]:
        return [
            SagaStep(
                name="reserve_inventory",
                action="InventoryService.ReserveItems",
                compensation="InventoryService.ReleaseReservation"
            ),
            SagaStep(
                name="process_payment",
                action="PaymentService.ProcessPayment",
                compensation="PaymentService.RefundPayment"
            ),
            SagaStep(
                name="create_shipment",
                action="ShippingService.CreateShipment",
                compensation="ShippingService.CancelShipment"
            ),
            SagaStep(
                name="send_confirmation",
                action="NotificationService.SendOrderConfirmation",
                compensation="NotificationService.SendCancellationNotice"
            ),
        ]


# 启动 saga
async def create_order(order_data: Dict, saga_store, event_publisher):
    saga = OrderFulfillmentSaga(saga_store, event_publisher)
    return await saga.start({
        "order_id": order_data["order_id"],
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        "payment_method": order_data["payment_method"],
        "shipping_address": order_data["shipping_address"],
    })


# 参与服务 — 处理命令并发布回复
class InventoryService:
    async def handle_reserve_items(self, command: Dict):
        try:
            reservation = await self.reserve(command["items"], command["order_id"])
            await self.event_publisher.publish("SagaStepCompleted", {
                "saga_id": command["saga_id"],
                "step_name": "reserve_inventory",
                "result": {"reservation_id": reservation.id}
            })
        except InsufficientInventoryError as e:
            await self.event_publisher.publish("SagaStepFailed", {
                "saga_id": command["saga_id"],
                "step_name": "reserve_inventory",
                "error": str(e)
            })

    async def handle_release_reservation(self, command: Dict):
        """补偿 — 幂等的，总是发布完成事件。"""
        try:
            await self.release_reservation(
                command["original_result"]["reservation_id"]
            )
        except ReservationNotFoundError:
            pass  # 已释放 — 视为成功
        await self.event_publisher.publish("SagaCompensationCompleted", {
            "saga_id": command["saga_id"],
            "step_name": "reserve_inventory"
        })
```

### 模板 2：基于编排的 Saga

每个服务监听前一个服务的事件并做出反应。没有中央协调器。补偿由失败事件向后传播触发。

```python
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SagaContext:
    """在编排的 saga 中通过所有事件传递。"""
    saga_id: str
    step: int
    data: Dict[str, Any]
    completed_steps: list


class OrderChoreographySaga:
    """基于编排的 saga — 服务对彼此的事件做出反应。"""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._register_handlers()

    def _register_handlers(self):
        # 前进路径
        self.event_bus.subscribe("OrderCreated",       self._on_order_created)
        self.event_bus.subscribe("InventoryReserved",  self._on_inventory_reserved)
        self.event_bus.subscribe("PaymentProcessed",   self._on_payment_processed)
        self.event_bus.subscribe("ShipmentCreated",    self._on_shipment_created)
        # 补偿路径
        self.event_bus.subscribe("PaymentFailed",      self._on_payment_failed)
        self.event_bus.subscribe("ShipmentFailed",     self._on_shipment_failed)

    async def _on_order_created(self, event: Dict):
        await self.event_bus.publish("ReserveInventory", {
            "saga_id": event["order_id"],
            "order_id": event["order_id"],
            "items": event["items"],
        })

    async def _on_inventory_reserved(self, event: Dict):
        await self.event_bus.publish("ProcessPayment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "amount": event["total_amount"],
            "reservation_id": event["reservation_id"],
        })

    async def _on_payment_processed(self, event: Dict):
        await self.event_bus.publish("CreateShipment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "payment_id": event["payment_id"],
        })

    async def _on_shipment_created(self, event: Dict):
        await self.event_bus.publish("OrderFulfilled", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "tracking_number": event["tracking_number"],
        })

    # 补偿处理器
    async def _on_payment_failed(self, event: Dict):
        """支付失败 — 释放库存并标记订单失败。"""
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"],
            "reservation_id": event["reservation_id"],
        })
        await self.event_bus.publish("OrderFailed", {
            "order_id": event["order_id"],
            "reason": "Payment failed",
        })

    async def _on_shipment_failed(self, event: Dict):
        """配送失败 — 退款并释放库存。"""
        await self.event_bus.publish("RefundPayment", {
            "saga_id": event["saga_id"],
            "payment_id": event["payment_id"],
        })
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"],
            "reservation_id": event["reservation_id"],
        })
```

### 模板 3：幂等步骤守卫

每个参与者必须防止重复的命令投递。在执行前存储幂等键，并在重放时返回缓存的结果。

```python
async def handle_reserve_items(self, command: Dict):
    """带幂等保护的预留步骤。"""
    idempotency_key = f"reserve-{command['order_id']}"
    existing = await self.reservation_store.find_by_key(idempotency_key)
    if existing:
        # 已执行 — 返回之前的结果，不产生副作用
        await self.event_publisher.publish("SagaStepCompleted", {
            "saga_id": command["saga_id"],
            "step_name": "reserve_inventory",
            "result": {"reservation_id": existing.id}
        })
        return

    # 首次执行
    reservation = await self.reserve(
        items=command["items"],
        order_id=command["order_id"],
        idempotency_key=idempotency_key
    )
    await self.event_publisher.publish("SagaStepCompleted", {
        "saga_id": command["saga_id"],
        "step_name": "reserve_inventory",
        "result": {"reservation_id": reservation.id}
    })
```

---

## 最佳实践

### 应该做的

- **使每个步骤幂等** — 命令可能在 broker 重连时被重放
- **仔细设计补偿** — 它们是最关键的代码路径
- **使用关联 ID** — `saga_id` 必须流经每个事件和日志
- **实现每步超时** — 永远不要无限期等待参与者回复
- **记录状态转换** — 每次变更时记录 `saga_id`、`step_name`、`old_state → new_state`
- **显式测试补偿路径** — 在集成测试中对每个步骤索引注入失败

### 不应该做的

- **不要假设即时完成** — Saga 是异步的，可能需要几分钟
- **不要跳过补偿测试** — 回滚路径是最难正确实现的
- **不要直接耦合服务** — 使用异步消息，不要在 saga 步骤内使用同步调用
- **不要忽略部分失败** — 部分执行的步骤仍然需要补偿
- **不要使用全局超时** — 每个步骤有不同的延迟特性

---

## 故障排除

### Saga 卡在 COMPENSATING 状态

Saga 进入补偿但永远不会到达 FAILED 状态。这意味着补偿处理器抛出了未处理的异常，从未发布 `SagaCompensationCompleted`。为补偿消费者添加死信队列（DLQ）处理，并确保每个补偿操作即使在底层操作已回滚时也发布结果事件。

```python
async def handle_release_reservation(self, command: Dict):
    try:
        await self.release_reservation(command["original_result"]["reservation_id"])
    except ReservationNotFoundError:
        pass  # 已释放 — 视为成功
    # 无论结果如何，总是发布完成事件
    await self.event_publisher.publish("SagaCompensationCompleted", {
        "saga_id": command["saga_id"],
        "step_name": "reserve_inventory"
    })
```

### 重启时重复执行 saga

如果您的协调器服务在 saga 中途重启，它可能会重放事件并重新执行已完成的步骤。用幂等键保护每个步骤操作 — 参见上面的**模板 3**。

### 编排 saga 丢失事件

在基于编排的 saga 中，如果下游服务在事件发布时离线，它可能会错过事件。使用持久消息 broker（带复制的 Kafka、带持久化的 RabbitMQ），并将当前 saga 状态存储在专用的 `saga_log` 表中，以便从最后已知的良好步骤重放。

### 超时在缓慢但有效的步骤完成前触发

像 `create_shipment` 这样的步骤在高峰期可能需要长达 15 分钟，但您的全局超时是 5 分钟，导致虚假补偿。使步骤超时可按步骤类型配置 — 参见 `references/advanced-patterns.md` 中的 `TimeoutSagaOrchestrator` 实现和 `STEP_TIMEOUTS` 字典模式。

### 补偿顺序与执行顺序不匹配

当两个步骤在检测到失败之前都已完成时，补偿必须按严格逆序运行，否则数据会处于不一致状态。验证 `_compensate()` 从 `current_step - 1` 向下迭代到 `0`，并添加一个集成测试，在每个步骤索引处故意失败以确认正确的回滚顺序。

---

## 高级模式

`references/` 目录包含大多数 saga 不需要的生产级实现：

- **`references/advanced-patterns.md`** — 完整的 `SagaOrchestrator` 抽象基类、带每步截止时间的 `TimeoutSagaOrchestrator`、详细的银行转账补偿事务链、Prometheus 检测、saga 卡住 PromQL 告警和 DLQ 恢复工作器。

---

## 相关技能

- `cqrs-implementation` — 将 saga 与 CQRS 配对，在每步完成后更新读模型
- `event-store-design` — 将 saga 事件存储在事件存储中，实现完整审计跟踪和重放能力
- `workflow-orchestration-patterns` — 构建在 saga 概念之上的更高级工作流引擎（Temporal、Conductor）
