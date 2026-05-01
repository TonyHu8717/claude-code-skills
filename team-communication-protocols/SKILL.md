---
name: team-communication-protocols
description: 智能体团队通信的结构化消息协议，包括消息类型选择、计划审批、关闭流程和应避免的反模式。适用于为新生成的团队建立通信规范、决定发送直接消息还是广播、团队负责人需要在工作开始前审查和批准实现者的计划、在所有任务完成后协调团队优雅关闭，或调试为何队友在集成点未正确协调时使用。
version: 1.0.2
---

# 团队通信协议

智能体队友之间有效通信的协议，包括消息类型选择、计划审批工作流、关闭流程和常见反模式。

## 何时使用此技能

- 为新团队建立通信规范
- 选择消息类型（message、broadcast、shutdown_request）
- 处理计划审批工作流
- 管理团队优雅关闭
- 发现队友身份和能力

## 消息类型选择

### `message`（直接消息）— 默认选择

发送给单个特定队友：

```json
{
  "type": "message",
  "recipient": "implementer-1",
  "content": "Your API endpoint is ready. You can now build the frontend form.",
  "summary": "API endpoint ready for frontend"
}
```

**用于**：任务更新、协调、问题咨询、集成通知。

### `broadcast` — 谨慎使用

同时发送给所有队友：

```json
{
  "type": "broadcast",
  "content": "Critical: shared types file has been updated. Pull latest before continuing.",
  "summary": "Shared types updated"
}
```

**仅用于**：影响所有人的关键阻碍、共享资源的重大变更。

**为何要谨慎？**：每次广播发送 N 条独立消息（每个队友一条），消耗与团队规模成正比的 API 资源。

### `shutdown_request` — 优雅终止

请求队友关闭：

```json
{
  "type": "shutdown_request",
  "recipient": "reviewer-1",
  "content": "Review complete, shutting down team."
}
```

队友会以 `shutdown_response` 响应（批准或拒绝并附原因）。

## 通信反模式

| 反模式                       | 问题                         | 更好的做法                       |
| ---------------------------- | ---------------------------- | -------------------------------- |
| 广播常规更新                 | 浪费资源，产生噪音           | 直接消息给受影响的队友           |
| 发送 JSON 状态消息           | 不适合结构化数据             | 使用 TaskUpdate 更新任务状态     |
| 在集成点不通信               | 队友基于过时接口构建         | 接口准备好时发送消息             |
| 通过消息进行微管理           | 让队友不堪重负，拖慢进度     | 在里程碑处检查，而非每一步       |
| 使用 UUID 而非名称           | 难以阅读，容易出错           | 始终使用队友名称                 |
| 忽视空闲队友                 | 浪费产能                     | 分配新任务或关闭                 |

## 计划审批工作流

当队友以 `plan_mode_required` 生成时：

1. 队友使用只读探索工具创建计划
2. 队友调用 `ExitPlanMode`，向负责人发送 `plan_approval_request`
3. 负责人审查计划
4. 负责人以 `plan_approval_response` 响应：

**批准**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": true
}
```

**拒绝并附反馈**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": false,
  "content": "Please add error handling for the API calls"
}
```

## 关闭协议

### 优雅关闭流程

1. **负责人向每个队友发送 shutdown_request**
2. **队友接收请求**，以 JSON 消息形式包含 `type: "shutdown_request"`
3. **队友响应** `shutdown_response`：
   - `approve: true` — 队友保存状态并退出
   - `approve: false` + 原因 — 队友继续工作
4. **负责人处理拒绝** — 等待队友完成，然后重试
5. **所有队友关闭后** — 调用 `TeamDelete` 删除团队资源

### 处理拒绝

如果队友拒绝关闭：

- 检查原因（通常是"仍在处理任务"）
- 等待当前任务完成
- 重试关闭请求
- 如有紧急情况，用户可强制关闭

## 队友发现

通过读取配置文件查找团队成员：

**位置**：`~/.claude/teams/{team-name}/config.json`

**结构**：

```json
{
  "members": [
    {
      "name": "security-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    },
    {
      "name": "perf-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    }
  ]
}
```

**始终使用 `name`** 进行消息发送和任务分配。切勿直接使用 `agentId`。

## 故障排除

**队友没有响应消息。**
检查队友的任务状态。如果处于空闲状态，可能已完成任务，等待分配新任务或关闭。如果仍在活跃状态，可能正在执行中，当前操作完成后会处理消息。

**负责人对每个状态更新都发送广播。**
这是常见的反模式。广播成本高昂 — 每次发送 N 条消息。使用直接消息（`type: "message"`）进行点对点更新。将广播保留用于关键的共享资源变更，如更新的接口契约。

**队友意外拒绝了关闭请求。**
队友仍在工作中。检查 `shutdown_response` 内容字段中的拒绝原因，等待工作完成后重试。切勿强制终止有未保存工作的队友。

**收到了 plan_approval_request 但缺少 request_id。**
队友在没有所需请求上下文的情况下调用了 `ExitPlanMode`。让队友重新进入计划模式，完成探索，然后再次调用 `ExitPlanMode`。`request_id` 由计划模式系统自动生成。

**两个队友互相等待，谁都没有进展。**
这是死锁：双方都被阻塞，等待对方先完成。负责人应向其中一个队友发送直接消息，提供存根或部分结果，使其解除阻塞并继续工作。

## 相关技能

- [team-composition-patterns](../team-composition-patterns/SKILL.md) — 在建立通信规范之前选择智能体类型和团队规模
- [parallel-feature-development](../parallel-feature-development/SKILL.md) — 使用通信协议协调并行实现者之间的集成交接
