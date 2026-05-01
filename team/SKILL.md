---
name: team
description: N 个协调代理在共享任务列表上协作，使用 Claude Code 原生团队功能
argument-hint: "[N:agent-type] [ralph] <task description>"
aliases: []
level: 4
---

# 团队技能

生成 N 个协调代理在共享任务列表上协作，使用 Claude Code 的原生团队工具。用内置的团队管理、代理间消息传递和任务依赖替代旧版 `/swarm` 技能（基于 SQLite）— 无需外部依赖。

`swarm` 兼容别名在 #1131 中已移除。

## 用法

```
/oh-my-claudecode:team N:agent-type "task description"
/oh-my-claudecode:team "task description"
/oh-my-claudecode:team ralph "task description"
```

### 参数

- **N** — 团队友伴代理数量（1-20）。可选；默认根据任务分解自动调整大小。
- **agent-type** — 用于 `team-exec` 阶段的 OMC 代理（如 executor、debugger、designer、codex、gemini）。可选；默认使用阶段感知路由。使用 `codex` 生成 Codex CLI 工作者或 `gemini` 生成 Gemini CLI 工作者（需要安装相应的 CLI）。参见下方阶段代理路由。
- **task** — 要在团队友伴之间分解和分配的高级任务
- **ralph** — 可选修饰符。当存在时，将团队管道包装在 Ralph 的持久化循环中（失败重试、完成前架构师验证）。参见下方团队 + Ralph 组合。

### 示例

```bash
/team 5:executor "fix all TypeScript errors across the project"
/team 3:debugger "fix build errors in src/"
/team 4:designer "implement responsive layouts for all page components"
/team "refactor the auth module with security review"
/team ralph "build a complete REST API for user management"
# 使用 Codex CLI 工作者（需要：npm install -g @openai/codex）
/team 2:codex "review architecture and suggest improvements"
# 使用 Gemini CLI 工作者（需要：npm install -g @google/gemini-cli）
/team 2:gemini "redesign the UI components"
# 混合：Codex 用于后端分析，Gemini 用于前端（改用 /ccg）
```

## 架构

```
用户: "/team 3:executor fix all TypeScript errors"
              |
              v
      [团队编排器（主控）]
              |
              +-- TeamCreate("fix-ts-errors")
              |       -> 主控成为 team-lead@fix-ts-errors
              |
              +-- 分析并分解任务为子任务
              |       -> explore/architect 生成子任务列表
              |
              +-- TaskCreate x N（每个子任务一个）
              |       -> 任务 #1、#2、#3 及依赖关系
              |
              +-- TaskUpdate x N（预分配所有者）
              |       -> 任务 #1 owner=worker-1，等等
              |
              +-- Task(team_name="fix-ts-errors", name="worker-1") x 3
              |       -> 将队友生成到团队中
              |
              +-- 监控循环
              |       <- 来自队友的 SendMessage（自动送达）
              |       -> TaskList 轮询进度
              |       -> SendMessage 解除阻塞/协调
              |
              +-- 完成
                      -> SendMessage(shutdown_request) 发给每个队友
                      <- SendMessage(shutdown_response, approve: true)
                      -> TeamDelete("fix-ts-errors")
                      -> rm .omc/state/team-state.json
```

**存储布局（由 Claude Code 管理）：**
```
~/.claude/
  teams/fix-ts-errors/
    config.json          # 团队元数据 + 成员数组
  tasks/fix-ts-errors/
    .lock                # 并发访问的文件锁
    1.json               # 子任务 #1
    2.json               # 子任务 #2（可能是内部的）
    3.json               # 子任务 #3
    ...
```

## 分阶段管道（规范团队运行时）

团队执行遵循分阶段管道：

`team-plan -> team-prd -> team-exec -> team-verify -> team-fix（循环）`

### 阶段代理路由

每个管道阶段使用**专门代理** — 而不仅仅是执行器。主控根据阶段和任务特征选择代理。

| 阶段 | 必需代理 | 可选代理 | 选择标准 |
|------|---------|---------|---------|
| **team-plan** | `explore`（haiku）、`planner`（opus） | `analyst`（opus）、`architect`（opus） | 需求不明确时使用 `analyst`。系统边界复杂时使用 `architect`。 |
| **team-prd** | `analyst`（opus） | `critic`（opus） | 使用 `critic` 挑战范围。 |
| **team-exec** | `executor`（sonnet） | `executor`（opus）、`debugger`（sonnet）、`designer`（sonnet）、`writer`（haiku）、`test-engineer`（sonnet） | 匹配代理与子任务类型。复杂自主工作使用 `executor`（model=opus），UI 使用 `designer`，编译问题使用 `debugger`，文档使用 `writer`，测试创建使用 `test-engineer`。 |
| **team-verify** | `verifier`（sonnet） | `test-engineer`（sonnet）、`security-reviewer`（sonnet）、`code-reviewer`（opus） | 始终运行 `verifier`。auth/crypto 变更添加 `security-reviewer`。>20 个文件或架构变更添加 `code-reviewer`。`code-reviewer` 也覆盖风格/格式检查。 |
| **team-fix** | `executor`（sonnet） | `debugger`（sonnet）、`executor`（opus） | 类型/构建错误和回归隔离使用 `debugger`。复杂多文件修复使用 `executor`（model=opus）。 |

**路由规则：**

1. **主控按阶段选择代理，而非用户。** 用户的 `N:agent-type` 参数仅覆盖 `team-exec` 阶段的工作者类型。所有其他阶段使用阶段适当的专家。
2. **专家代理补充执行器代理。** 将分析/审查路由到架构师/批评者 Claude 代理，UI 工作路由到 designer 代理。Tmux CLI 工作者是一次性的，不参与团队通信。
3. **成本模式影响模型层级。** 降级时：`opus` 代理降至 `sonnet`，`sonnet` 降至 `haiku`（质量允许时）。`team-verify` 始终至少使用 `sonnet`。
4. **风险级别升级审查。** 安全敏感或 >20 个文件变更必须在 `team-verify` 中包含 `security-reviewer` + `code-reviewer`（opus）。

### 阶段进入/退出标准

- **team-plan**
  - 进入：团队调用已解析，编排开始。
  - 代理：`explore` 扫描代码库，`planner` 创建任务图，可选 `analyst`/`architect` 处理复杂任务。
  - 退出：分解完成，可运行任务图已准备。
- **team-prd**
  - 进入：范围模糊或验收标准缺失。
  - 代理：`analyst` 提取需求，可选 `critic`。
  - 退出：验收标准和边界明确。
- **team-exec**
  - 进入：`TeamCreate`、`TaskCreate`、分配和工作者生成完成。
  - 代理：按子任务生成适当专家类型的工作者（见路由表）。
  - 退出：执行任务在当前遍历达到终态。
- **team-verify**
  - 进入：执行遍历完成。
  - 代理：`verifier` + 任务适当审查者（见路由表）。
  - 退出（通过）：验证门通过，无必需后续。
  - 退出（失败）：生成修复任务，控制转移到 `team-fix`。
- **team-fix**
  - 进入：验证发现缺陷/回归/未完成标准。
  - 代理：`executor`/`debugger` 取决于缺陷类型。
  - 退出：修复完成，流程返回 `team-exec` 然后 `team-verify`。

### 验证/修复循环和停止条件

继续 `team-exec -> team-verify -> team-fix` 直到：
1. 验证通过且无必需修复任务剩余，或
2. 工作达到明确的终态阻塞/失败结果并有证据。

`team-fix` 有最大尝试次数限制。如果修复尝试超过配置限制，转为终态 `failed`（无无限循环）。

### 阶段交接约定

阶段间转换时，重要上下文 — 做出的决策、被拒绝的替代方案、识别的风险 — 仅存在于主控的对话历史中。如果主控的上下文压缩或代理重启，这些知识会丢失。

**每个完成阶段必须在转换前生成交接文档。**

主控将交接写入 `.omc/handoffs/<stage-name>.md`。

#### 交接格式

```markdown
## 交接：<当前阶段> → <下一阶段>
- **已决定**：[本阶段做出的关键决策]
- **已拒绝**：[考虑过的替代方案及拒绝原因]
- **风险**：[下一阶段的已识别风险]
- **文件**：[创建或修改的关键文件]
- **剩余**：[留给下一阶段处理的项目]
```

#### 交接规则

1. **主控在生成下一阶段代理之前读取上一阶段交接。** 交接内容包含在下一阶段的代理生成提示中，确保代理从完整上下文开始。
2. **交接累积。** 验证阶段可以读取所有先前交接（plan → prd → exec）以获得完整决策历史。
3. **团队取消时，交接在 `.omc/handoffs/` 中保留**以供会话恢复。它们不会被 `TeamDelete` 删除。
4. **交接是轻量级的。** 最多 10-20 行。它们捕获决策和理由，而非完整规范（那些存在于交付文件中如 DESIGN.md）。

#### 示例

```markdown
## 交接：team-plan → team-exec
- **已决定**：微服务架构，3 个服务（auth、api、worker）。PostgreSQL 持久化。JWT 认证令牌。
- **已拒绝**：单体（扩展问题）、MongoDB（团队专长是 SQL）、会话 cookie（API 优先设计）。
- **风险**：Worker 服务需要 Redis 作任务队列 — 尚未配置。Auth 服务初始设计中无速率限制。
- **文件**：DESIGN.md、TEST_STRATEGY.md
- **剩余**：数据库迁移脚本、CI/CD 管道配置、Redis 配置。
```

### 恢复和取消语义

- **恢复：** 从最后非终态阶段重新开始，使用分阶段状态 + 实时任务状态。读取 `.omc/handoffs/` 恢复阶段转换上下文。
- **取消：** `/oh-my-claudecode:cancel` 请求队友关闭，等待响应（尽力而为），标记阶段为 `cancelled`（`active=false`），捕获取消元数据，然后删除团队资源并按策略清除/保留团队状态。`.omc/handoffs/` 中的交接文件保留以供潜在恢复。
- 终态为 `complete`、`failed` 和 `cancelled`。

## 工作流程

### 阶段 1：解析输入

- 提取 **N**（代理数量），验证 1-20
- 提取 **agent-type**，验证其映射到已知 OMC 子代理
- 提取 **task** 描述

### 阶段 2：分析与分解

使用 `explore` 或 `architect`（通过 MCP 或代理）分析代码库并将任务分解为 N 个子任务：

- 每个子任务应为**文件范围**或**模块范围**以避免冲突
- 子任务必须独立或有清晰的依赖排序
- 每个子任务需要简洁的 `subject` 和详细的 `description`
- 识别子任务之间的依赖关系（如"共享类型必须在消费者之前修复"）

### 阶段 3：创建团队

使用从任务派生的 slug 调用 `TeamCreate`：

```json
{
  "team_name": "fix-ts-errors",
  "description": "Fix all TypeScript errors across the project"
}
```

**响应：**
```json
{
  "team_name": "fix-ts-errors",
  "team_file_path": "~/.claude/teams/fix-ts-errors/config.json",
  "lead_agent_id": "team-lead@fix-ts-errors"
}
```

当前会话成为团队主控（`team-lead@fix-ts-errors`）。

使用 `state_write` MCP 工具写入 OMC 状态以实现适当的会话范围持久化：

```
state_write(mode="team", active=true, current_phase="team-plan", state={
  "team_name": "fix-ts-errors",
  "agent_count": 3,
  "agent_types": "executor",
  "task": "fix all TypeScript errors",
  "fix_loop_count": 0,
  "max_fix_loops": 3,
  "linked_ralph": false,
  "stage_history": "team-plan"
})
```

> **注意：** MCP `state_write` 工具将所有值作为字符串传输。消费者读取状态时必须将 `agent_count`、`fix_loop_count`、`max_fix_loops` 强制转换为数字，将 `linked_ralph` 强制转换为布尔值。

**状态架构字段：**

| 字段 | 类型 | 描述 |
|------|------|------|
| `active` | boolean | 团队模式是否激活 |
| `current_phase` | string | 当前管道阶段：`team-plan`、`team-prd`、`team-exec`、`team-verify`、`team-fix` |
| `team_name` | string | 团队的 slug 名称 |
| `agent_count` | number | 工作者代理数量 |
| `agent_types` | string | team-exec 中使用的代理类型（逗号分隔） |
| `task` | string | 原始任务描述 |
| `fix_loop_count` | number | 当前修复迭代计数 |
| `max_fix_loops` | number | 失败前最大修复迭代次数（默认：3） |
| `linked_ralph` | boolean | 团队是否链接到 ralph 持久化循环 |
| `stage_history` | string | 带时间戳的阶段转换列表（逗号分隔） |

**每次阶段转换时更新状态：**

```
state_write(mode="team", current_phase="team-exec", state={
  "stage_history": "team-plan:2026-02-07T12:00:00Z,team-prd:2026-02-07T12:01:00Z,team-exec:2026-02-07T12:02:00Z"
})
```

**读取状态用于恢复检测：**

```
state_read(mode="team")
```

如果 `active=true` 且 `current_phase` 为非终态，从最后未完成阶段恢复而非创建新团队。

### 阶段 4：创建任务

对每个子任务调用 `TaskCreate`。使用 `TaskUpdate` 的 `addBlockedBy` 设置依赖关系。

```json
// 子任务 1 的 TaskCreate
{
  "subject": "Fix type errors in src/auth/",
  "description": "Fix all TypeScript errors in src/auth/login.ts, src/auth/session.ts, and src/auth/types.ts. Run tsc --noEmit to verify.",
  "activeForm": "Fixing auth type errors"
}
```

**响应存储任务文件（如 `1.json`）：**
```json
{
  "id": "1",
  "subject": "Fix type errors in src/auth/",
  "description": "Fix all TypeScript errors in src/auth/login.ts...",
  "activeForm": "Fixing auth type errors",
  "owner": "",
  "status": "pending",
  "blocks": [],
  "blockedBy": []
}
```

有依赖关系的任务，创建后使用 `TaskUpdate`：

```json
// 任务 #3 依赖任务 #1（共享类型必须先修复）
{
  "taskId": "3",
  "addBlockedBy": ["1"]
}
```

**从主控预分配所有者**以避免竞争条件（没有原子声明）：

```json
// 将任务 #1 分配给 worker-1
{
  "taskId": "1",
  "owner": "worker-1"
}
```

### 阶段 5：生成队友

使用 `Task` 的 `team_name` 和 `name` 参数生成 N 个队友。每个队友获得团队工作者前言（见下文）加其特定任务分配。

```json
{
  "subagent_type": "oh-my-claudecode:executor",
  "team_name": "fix-ts-errors",
  "name": "worker-1",
  "prompt": "<worker-preamble + assigned tasks>"
}
```

**响应：**
```json
{
  "agent_id": "worker-1@fix-ts-errors",
  "name": "worker-1",
  "team_name": "fix-ts-errors"
}
```

**副作用：**
- 队友添加到 `config.json` 成员数组
- 自动创建**内部任务**（`metadata._internal: true`）跟踪代理生命周期
- 内部任务出现在 `TaskList` 输出中 — 计算实际任务时过滤它们

**重要：** 并行生成所有队友（它们是后台代理）。不要等一个完成再生成下一个。

### 阶段 6：监控

主控编排器通过两个渠道监控进度：

1. **入站消息** — 队友完成任务或需要帮助时向 `team-lead` 发送 `SendMessage`。这些作为新对话轮次自动到达（无需轮询）。

2. **TaskList 轮询** — 定期调用 `TaskList` 检查整体进度：
   ```
   #1 [completed] Fix type errors in src/auth/ (worker-1)
   #3 [in_progress] Fix type errors in src/api/ (worker-2)
   #5 [pending] Fix type errors in src/utils/ (worker-3)
   ```
   格式：`#ID [status] subject (owner)`

**主控可以采取的协调操作：**

- **解除队友阻塞：** 发送带有指导或缺失上下文的 `message`
- **重新分配工作：** 如果队友提前完成，使用 `TaskUpdate` 将待处理任务分配给他们并通过 `SendMessage` 通知
- **处理失败：** 如果队友报告失败，重新分配任务或生成替代者

#### 任务看门狗策略

监控卡住或失败的队友：

- **最大进行中时间**：如果任务在 `in_progress` 状态超过 5 分钟且无消息，发送状态检查
- **疑似死亡工作者**：无消息 + 卡住任务超过 10 分钟 → 将任务重新分配给其他工作者
- **重新分配阈值**：如果工作者失败 2+ 个任务，停止向其分配新任务

### 阶段 6.5：阶段转换（状态持久化）

每次阶段转换时更新 OMC 状态：

```
// 规划后进入 team-exec
state_write(mode="team", current_phase="team-exec", state={
  "stage_history": "team-plan:T1,team-prd:T2,team-exec:T3"
})

// 执行后进入 team-verify
state_write(mode="team", current_phase="team-verify")

// 验证失败后进入 team-fix
state_write(mode="team", current_phase="team-fix", state={
  "fix_loop_count": 1
})
```

这使得：
- **恢复**：如果主控崩溃，`state_read(mode="team")` 显示最后阶段和团队名称以供恢复
- **取消**：取消技能读取 `current_phase` 以了解需要什么清理
- **Ralph 集成**：Ralph 可以读取团队状态以了解管道是完成还是失败

### 阶段 7：完成

当所有实际任务（非内部）完成或失败时：

1. **验证结果** — 通过 `TaskList` 检查所有子任务标记为 `completed`
2. **关闭队友** — 向每个活跃队友发送 `shutdown_request`：
   ```json
   {
     "type": "shutdown_request",
     "recipient": "worker-1",
     "content": "All work complete, shutting down team"
   }
   ```
3. **等待响应** — 每个队友以 `shutdown_response(approve: true)` 响应并终止
4. **删除团队** — 调用 `TeamDelete` 清理：
   ```json
   { "team_name": "fix-ts-errors" }
   ```
   响应：
   ```json
   {
     "success": true,
     "message": "Cleaned up directories and worktrees for team \"fix-ts-errors\"",
     "team_name": "fix-ts-errors"
   }
   ```
5. **清理 OMC 状态** — 删除 `.omc/state/team-state.json`
6. **报告摘要** — 向用户展示结果

## 代理前言

生成队友时，在提示中包含此前言以建立工作协议。根据每个队友的特定任务分配进行调整。

```
你是团队 "{team_name}" 中的团队工作者。你的名字是 "{worker_name}"。
你向团队主控（"team-lead"）汇报。
你不是领导者，不得执行领导者编排操作。

== 工作协议 ==

1. 声明：调用 TaskList 查看你的分配任务（owner = "{worker_name}"）。
   选择分配给你的第一个状态为 "pending" 的任务。
   调用 TaskUpdate 设置状态 "in_progress"：
   {"taskId": "ID", "status": "in_progress", "owner": "{worker_name}"}

2. 工作：使用你的工具（Read、Write、Edit、Bash）执行任务。
   不要生成子代理。不要委托。直接工作。

3. 完成：完成后，标记任务为已完成：
   {"taskId": "ID", "status": "completed"}

4. 报告：通过 SendMessage 通知主控：
   {"type": "message", "recipient": "team-lead", "content": "Completed task #ID: <summary of what was done>", "summary": "Task #ID complete"}

5. 下一个：检查 TaskList 是否有更多分配任务。如果有更多待处理任务，回到步骤 1。
   如果没有更多任务分配给你，通知主控：
   {"type": "message", "recipient": "team-lead", "content": "All assigned tasks complete. Standing by.", "summary": "All tasks done, standing by"}

6. 关闭：当收到 shutdown_request 时，响应：
   {"type": "shutdown_response", "request_id": "<from the request>", "approve": true}

== 阻塞任务 ==
如果任务有 blockedBy 依赖，跳过它直到那些任务完成。
定期检查 TaskList 以查看阻塞是否已解决。

== 错误 ==
如果无法完成任务，向主控报告失败：
{"type": "message", "recipient": "team-lead", "content": "FAILED task #ID: <reason>", "summary": "Task #ID failed"}
不要将任务标记为已完成。保持 in_progress 状态以便主控重新分配。

== 规则 ==
- 绝不生成子代理或使用 Task 工具
- 绝不运行 tmux 窗格/会话编排命令（例如 `tmux split-window`、`tmux new-session`）
- 绝不运行团队生成/编排技能或命令（例如 `$team`、`$ultrawork`、`$autopilot`、`$ralph`、`omc team ...`、`omx team ...`）
- 始终使用绝对文件路径
- 始终通过 SendMessage 向 "team-lead" 报告进度
- 仅使用 type "message" 的 SendMessage — 绝不使用 "broadcast"
```

### 代理类型提示注入（工作者特定附录）

组合队友提示时，根据工作者类型追加简短附录：

- `claude_worker`：强调严格的 TaskList/TaskUpdate/SendMessage 循环和无编排命令。
- `codex_worker`：强调 CLI API 生命周期（`omc team api ... --json`）和显式失败 ACK（含 stderr）。
- `gemini_worker`：强调有界文件所有权和每个完成子步骤后的里程碑 ACK。

此附录必须保留核心规则：**工作者 = 仅执行器，绝不做领导者/编排器**。

## 通信模式

### 队友到主控（任务完成报告）

```json
{
  "type": "message",
  "recipient": "team-lead",
  "content": "Completed task #1: Fixed 3 type errors in src/auth/login.ts and 2 in src/auth/session.ts. All files pass tsc --noEmit.",
  "summary": "Task #1 complete"
}
```

### 主控到队友（重新分配或指导）

```json
{
  "type": "message",
  "recipient": "worker-2",
  "content": "Task #3 is now unblocked. Also pick up task #5 which was originally assigned to worker-1.",
  "summary": "New task assignment"
}
```

### 广播（谨慎使用 — 发送 N 条单独消息）

```json
{
  "type": "broadcast",
  "content": "STOP: shared types in src/types/index.ts have changed. Pull latest before continuing.",
  "summary": "Shared types changed"
}
```

### 关闭协议（阻塞式）

**关键：步骤必须按精确顺序执行。在确认关闭之前绝不调用 TeamDelete。**

**步骤 1：验证完成**
```
调用 TaskList — 验证所有实际任务（非内部）已完成或失败。
```

**步骤 2：向每个队友请求关闭**

**主控发送：**
```json
{
  "type": "shutdown_request",
  "recipient": "worker-1",
  "content": "All work complete, shutting down team"
}
```

**步骤 3：等待响应（阻塞式）**
- 每个队友等待最多 30 秒的 `shutdown_response`
- 跟踪哪些队友已确认 vs 超时
- 如果队友在 30 秒内未响应：记录警告，标记为无响应

**队友接收并响应：**
```json
{
  "type": "shutdown_response",
  "request_id": "shutdown-1770428632375@worker-1",
  "approve": true
}
```

批准后：
- 队友进程终止
- 队友从 `config.json` 成员数组自动移除
- 该队友的内部任务完成

**步骤 4：TeamDelete — 仅在所有队友确认或超时后**
```json
{ "team_name": "fix-ts-errors" }
```

**步骤 5：孤儿扫描**

检查 TeamDelete 后存活的代理进程：
```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/cleanup-orphans.mjs" --team-name fix-ts-errors
```

扫描匹配团队名称但配置已不存在的进程，并终止它们（SIGTERM → 5 秒等待 → SIGKILL）。支持 `--dry-run` 进行检查。

**关闭序列是阻塞式的：** 在所有队友都已确认关闭（`shutdown_response` 且 `approve: true`）或超时（30 秒无响应）之前，不要继续执行 TeamDelete。

**重要：** `request_id` 在队友收到的关闭请求消息中提供。队友必须提取它并传回。不要伪造 request ID。

## CLI 工作者（Codex 和 Gemini）

团队技能支持**混合执行**，将 Claude 代理队友与外部 CLI 工作者（Codex CLI 和 Gemini CLI）结合。两种类型都可以进行代码更改 — 它们在能力和成本上有所不同。这些是独立的 CLI 工具，不是 MCP 服务器。

### 执行模式

任务在分解时标记执行模式：

| 执行模式 | 提供者 | 能力 |
|---------|--------|------|
| `claude_worker` | Claude 代理 | 完整 Claude Code 工具访问（Read/Write/Edit/Bash/Task）。最适合需要 Claude 推理 + 迭代工具使用的任务。 |
| `codex_worker` | Codex CLI（tmux 窗格） | working_directory 中的完整文件系统访问。通过 tmux 窗格自主运行。最适合代码审查、安全分析、重构、架构。需要 `npm install -g @openai/codex`。 |
| `gemini_worker` | Gemini CLI（tmux 窗格） | working_directory 中的完整文件系统访问。通过 tmux 窗格自主运行。最适合 UI/设计工作、文档、大上下文任务。需要 `npm install -g @google/gemini-cli`。 |

### CLI 工作者如何运作

Tmux CLI 工作者在具有文件系统访问权限的专用 tmux 窗格中运行。它们是**自主执行器**，而不仅仅是分析师：

1. 主控将任务说明写入提示文件
2. 主控生成 tmux CLI 工作者，`working_directory` 设置为项目根目录
3. 工作者读取文件、进行更改、运行命令 — 全部在工作目录内
4. 结果/摘要写入输出文件
5. 主控读取输出，标记任务完成，并将结果提供给依赖任务

**与 Claude 队友的关键区别：**
- CLI 工作者通过 tmux 运行，而非 Claude Code 的工具系统
- 它们不能使用 TaskList/TaskUpdate/SendMessage（无团队感知）
- 它们作为一次性自主作业运行，而非持久队友
- 主控管理它们的生命周期（生成、监控、收集结果）

### 路由决策

| 任务类型 | 最佳路由 | 原因 |
|---------|---------|------|
| 迭代多步骤工作 | Claude 队友 | 需要工具介导的迭代 + 团队通信 |
| 代码审查/安全审计 | CLI 工作者或专家代理 | 自主执行，擅长结构化分析 |
| 架构分析/规划 | architect Claude 代理 | 强分析推理能力，可访问代码库 |
| 重构（范围明确） | CLI 工作者或执行器代理 | 自主执行，擅长结构化转换 |
| UI/前端实现 | designer Claude 代理 | 设计专长，框架惯用法 |
| 大规模文档 | writer Claude 代理 | 写作专长 + 大上下文保持一致性 |
| 构建/测试迭代循环 | Claude 队友 | 需要 Bash 工具 + 迭代修复循环 |
| 需要团队协调的任务 | Claude 队友 | 需要 SendMessage 进行状态更新 |

### 示例：带 CLI 工作者的混合团队

```
/team 3:executor "refactor auth module with security review"

任务分解：
#1 [codex_worker] 当前 auth 代码的安全审查 -> 输出到 .omc/research/auth-security.md
#2 [codex_worker] 重构 auth/login.ts 和 auth/session.ts（使用 #1 发现）
#3 [claude_worker:designer] 重新设计 auth UI 组件（登录表单、会话指示器）
#4 [claude_worker] 更新 auth 测试 + 修复集成问题
#5 [gemini_worker] 所有变更的最终代码审查
```

主控运行 #1（Codex 安全分析），然后 #2 和 #3 并行（Codex 重构后端，designer 代理重新设计前端），然后 #4（Claude 队友处理测试迭代），然后 #5（Gemini 最终审查）。

### 预飞分析（可选）

对于大型模糊任务，在团队创建前运行分析：

1. 使用任务描述 + 代码库上下文生成 `Task(subagent_type="oh-my-claudecode:planner", ...)`
2. 使用分析产生更好的任务分解
3. 使用丰富上下文创建团队和任务

当任务范围不明确且在承诺特定分解之前受益于外部推理时，这特别有用。

## 监控增强：发件箱自动摄取

主控可以使用发件箱读取工具主动从 CLI 工作者摄取发件箱消息，实现事件驱动监控，而不完全依赖 `SendMessage` 传递。

### 发件箱读取函数

**`readNewOutboxMessages(teamName, workerName)`** — 使用字节偏移游标读取单个工作者的新发件箱消息。每次调用推进游标，因此后续调用仅返回自上次读取以来写入的消息。镜像 `readNewInboxMessages()` 的收件箱游标模式。

**`readAllTeamOutboxMessages(teamName)`** — 读取团队中所有工作者的新发件箱消息。返回 `{ workerName, messages }` 条目数组，跳过无新消息的工作者。适用于监控循环中的批量轮询。

**`resetOutboxCursor(teamName, workerName)`** — 将工作者的发件箱游标重置回字节 0。适用于主控重启后重新读取历史消息或调试。

### 在监控阶段使用 `getTeamStatus()`

`getTeamStatus(teamName, workingDirectory, heartbeatMaxAgeMs?)` 函数提供统一快照，结合：

- **工作者注册** — 哪些 MCP 工作者已注册（来自影子注册表 / config.json）
- **心跳新鲜度** — 每个工作者是否基于心跳年龄存活
- **任务进度** — 每个工作者和团队范围的任务计数（pending、in_progress、completed）
- **当前任务** — 每个工作者正在执行哪个任务
- **近期发件箱消息** — 自上次状态检查以来的新消息

监控循环中的示例用法：

```typescript
const status = getTeamStatus('fix-ts-errors', workingDirectory);

for (const worker of status.workers) {
  if (!worker.isAlive) {
    // 工作者已死亡 — 重新分配其进行中任务
  }
  for (const msg of worker.recentMessages) {
    if (msg.type === 'task_complete') {
      // 标记任务完成，解除依赖阻塞
    } else if (msg.type === 'task_failed') {
      // 处理失败，可能重试或重新分配
    } else if (msg.type === 'error') {
      // 记录错误，检查工作者是否需要干预
    }
  }
}

if (status.taskSummary.pending === 0 && status.taskSummary.inProgress === 0) {
  // 所有工作完成 — 继续关闭
}
```

### 基于事件的发件箱消息操作

| 消息类型 | 操作 |
|---------|------|
| `task_complete` | 标记任务完成，检查阻塞任务是否现在解除，通知依赖工作者 |
| `task_failed` | 增加失败侧车，决定重试 vs 重新分配 vs 跳过 |
| `idle` | 工作者无分配任务 — 分配待处理工作或开始关闭 |
| `error` | 记录错误，检查心跳中的 `consecutiveErrors` 是否达到隔离阈值 |
| `shutdown_ack` | 工作者确认关闭 — 可安全从团队移除 |
| `heartbeat` | 更新活跃性跟踪（与心跳文件冗余但对延迟监控有用 |

此方法补充了现有的基于 `SendMessage` 的通信，为无法使用 Claude Code 团队消息工具的 MCP 工作者提供基于拉取的机制。

## 错误处理

### 队友任务失败

1. 队友向主控发送 `SendMessage` 报告失败
2. 主控决定：重试（将同一任务重新分配给同一或不同工作者）或跳过
3. 重新分配：`TaskUpdate` 设置新所有者，然后 `SendMessage` 通知新所有者

### 队友卡住（无消息）

1. 主控通过 `TaskList` 检测 — 任务在 `in_progress` 状态时间过长
2. 主控向队友发送 `SendMessage` 询问状态
3. 如果无响应，认为队友已死亡
4. 通过 `TaskUpdate` 将任务重新分配给其他工作者

### 依赖阻塞

1. 如果阻塞任务失败，主控必须决定：
   - 重试阻塞者
   - 移除依赖（使用修改后的 blockedBy 的 `TaskUpdate`）
   - 完全跳过被阻塞任务
2. 通过 `SendMessage` 向受影响队友传达决策

### 队友崩溃

1. 该队友的内部任务将显示意外状态
2. 队友从 `config.json` 成员中消失
3. 主控将孤立任务重新分配给剩余工作者
4. 如需要，使用 `Task(team_name, name)` 生成替代队友

## 团队 + Ralph 组合

当用户调用 `/team ralph`、说"team ralph"或组合两个关键词时，团队模式将自身包装在 Ralph 的持久化循环中。这提供：

- **团队编排** — 多代理分阶段管道，每阶段有专门代理
- **Ralph 持久化** — 失败重试、完成前架构师验证、迭代跟踪

### 激活

团队+Ralph 在以下情况激活：
1. 用户调用 `/team ralph "task"` 或 `/oh-my-claudecode:team ralph "task"`
2. 关键词检测器在提示中发现 `team` 和 `ralph`
3. Hook 检测到 `MAGIC KEYWORD: RALPH` 与团队上下文并存

### 状态链接

两种模式都写入各自的状态文件并相互引用：

```
// 团队状态（通过 state_write）
state_write(mode="team", active=true, current_phase="team-plan", state={
  "team_name": "build-rest-api",
  "linked_ralph": true,
  "task": "build a complete REST API"
})

// Ralph 状态（通过 state_write）
state_write(mode="ralph", active=true, iteration=1, max_iterations=10, current_phase="execution", state={
  "linked_team": true,
  "team_name": "build-rest-api"
})
```

### 执行流程

1. Ralph 外循环开始（迭代 1）
2. 团队管道运行：`team-plan -> team-prd -> team-exec -> team-verify`
3. 如果 `team-verify` 通过：Ralph 运行架构师验证（STANDARD 层级最低）
4. 如果架构师批准：两种模式完成，运行 `/oh-my-claudecode:cancel`
5. 如果 `team-verify` 失败或架构师拒绝：团队进入 `team-fix`，然后循环回 `team-exec -> team-verify`
6. 如果修复循环超过 `max_fix_loops`：Ralph 增加迭代并重试完整管道
7. 如果 Ralph 超过 `max_iterations`：终态 `failed`

### 取消

取消任一模式即取消两者：
- **取消 Ralph（链接）：** 先取消团队（优雅关闭），然后清除 Ralph 状态
- **取消团队（链接）：** 清除团队，标记 Ralph 迭代取消，停止循环

详情参见下方取消部分。

## 幂等恢复

如果主控在运行中崩溃，团队技能应检测现有状态并恢复：

1. 检查 `${CLAUDE_CONFIG_DIR:-~/.claude}/teams/` 中匹配任务 slug 的团队
2. 如果找到，读取 `config.json` 发现活跃成员
3. 恢复监控模式而非创建重复团队
4. 调用 `TaskList` 确定当前进度
5. 从监控阶段继续

这防止重复团队并允许从主控失败中优雅恢复。

## 对比：团队 vs 旧版 Swarm

| 方面 | 团队（原生） | Swarm（旧版 SQLite） |
|------|------------|---------------------|
| **存储** | `~/.claude/teams/` 和 `~/.claude/tasks/` 中的 JSON 文件 | `.omc/state/swarm.db` 中的 SQLite |
| **依赖** | 不需要 `better-sqlite3` | 需要 `better-sqlite3` npm 包 |
| **任务声明** | `TaskUpdate(owner + in_progress)` — 主控预分配 | SQLite IMMEDIATE 事务 — 原子 |
| **竞争条件** | 如果两个代理声明同一任务可能发生（通过预分配缓解） | 无（SQLite 事务） |
| **通信** | `SendMessage`（DM、广播、关闭） | 无（即发即忘代理） |
| **任务依赖** | 内置 `blocks` / `blockedBy` 数组 | 不支持 |
| **心跳** | Claude Code 的自动空闲通知 | 手动心跳表 + 轮询 |
| **关闭** | 优雅请求/响应协议 | 基于信号的终止 |
| **代理生命周期** | 通过内部任务 + 配置成员自动跟踪 | 通过心跳表手动跟踪 |
| **进度可见性** | `TaskList` 显示带所有者的实时状态 | SQL 查询任务表 |
| **冲突预防** | Owner 字段（主控分配） | 基于租约的声明（含超时） |
| **崩溃恢复** | 主控通过缺失消息检测，重新分配 | 5 分钟租约超时后自动释放 |
| **状态清理** | `TeamDelete` 删除所有内容 | 手动 `rm` SQLite 数据库 |

**何时使用团队而非 Swarm：** 新工作始终优先使用 `/team`。它使用 Claude Code 的内置基础设施，无需外部依赖，支持代理间通信，并有任务依赖管理。

## 取消

`/oh-my-claudecode:cancel` 技能处理团队清理：

1. 通过 `state_read(mode="team")` 读取团队状态获取 `team_name` 和 `linked_ralph`
2. 向所有活跃队友（来自 `config.json` 成员）发送 `shutdown_request`
3. 等待每个的 `shutdown_response`（每个成员 15 秒超时）
4. 调用 `TeamDelete` 删除团队和任务目录
5. 通过 `state_clear(mode="team")` 清除状态
6. 如果 `linked_ralph` 为 true，也清除 ralph：`state_clear(mode="ralph")`

### 链接模式取消（团队 + Ralph）

当团队链接到 ralph 时，取消遵循依赖顺序：

- **从 Ralph 上下文触发取消：** 先取消团队（优雅关闭所有队友），然后清除 Ralph 状态。这确保工作者在持久化循环退出前停止。
- **从团队上下文触发取消：** 清除团队状态，然后标记 Ralph 为已取消。Ralph 的停止钩子将检测缺失的团队并停止迭代。
- **强制取消（`--force`）：** 通过 `state_clear` 无条件清除 `team` 和 `ralph` 状态。

如果队友无响应，`TeamDelete` 可能失败。在这种情况下，取消技能应短暂等待后重试，或告知用户手动清理 `~/.claude/teams/{team_name}/` 和 `~/.claude/tasks/{team_name}/`。

## 运行时 V2（事件驱动）

当设置 `OMC_RUNTIME_V2=1` 时，团队运行时使用事件驱动架构替代旧版 done.json 轮询看门狗：

- **无 done.json**：任务完成通过 CLI API 生命周期转换检测（claim-task、transition-task-status）
- **基于快照的监控**：每个轮询周期对任务和工作者进行时间点快照，计算增量，并发出事件
- **事件日志**：所有团队事件追加到 `.omc/state/team/{teamName}/events.jsonl`
- **工作者状态文件**：工作者将状态写入 `.omc/state/team/{teamName}/workers/{name}/status.json`
- **保留**：哨兵门（阻止过早完成）、断路器（死亡工作者检测）、失败侧车

V2 运行时是功能标记的，可以按会话启用。旧版 V1 运行时仍是默认。

## 动态扩展

当设置 `OMC_TEAM_SCALING_ENABLED=1` 时，团队支持会话中扩展：

- **scale_up**：向运行中的团队添加工作者（遵守 max_workers 限制）
- **scale_down**：移除空闲工作者（优雅排空 — 工作者在移除前完成当前任务）
- 基于文件的扩展锁防止并发扩展操作
- 单调工作者索引计数器确保跨扩展事件的唯一工作者名称

## 配置

可选设置位于 `.claude/omc.jsonc`（项目）或 `~/.config/claude-omc/config.jsonc`（用户）。项目值覆盖用户值；`OMC_TEAM_ROLE_OVERRIDES`（环境 JSON）优先于两者。

```jsonc
{
  "team": {
    "ops": {
      "maxAgents": 20,
      "defaultAgentType": "claude",
      "monitorIntervalMs": 30000,
      "shutdownTimeoutMs": 15000
    }
  }
}
```

- **ops.maxAgents** — 最大队友数（默认：20）
- **ops.defaultAgentType** — `/team` 调用未指定时的 CLI 提供者（`claude` | `codex` | `gemini`，默认：`claude`）
- **ops.monitorIntervalMs** — 轮询 `TaskList` 的频率（默认：30 秒）
- **ops.shutdownTimeoutMs** — 等待关闭响应的时间（默认：15 秒）

> **注意：** 团队成员没有硬编码的模型默认值。每个队友是独立的 Claude Code 会话，继承用户配置的模型。由于队友可以生成自己的子代理，会话模型充当编排层，而子代理可以使用任何模型层级。

## 按角色提供者和模型路由

> **范围：** 仅适用于 `/team`。基于任务的委托使用 `delegationRouting`（参见单独文档）。两个系统按设计共存。

声明哪个提供者（`claude`、`codex`、`gemini`）和哪个模型层级应支持每个规范角色。路由在团队创建时**解析一次**并持久化在 `TeamConfig.resolved_routing` 中 — 生成、扩展和重启都从快照读取，因此角色的工作者 CLI 和模型在团队生命周期内稳定。

### 示例 — 用户目标映射

```jsonc
// .claude/omc.jsonc
{
  "team": {
    "roleRouting": {
      "orchestrator":  { "model": "inherit" },
      "planner":       { "provider": "claude", "model": "HIGH" },
      "analyst":       { "provider": "claude", "model": "HIGH" },
      "executor":      { "provider": "claude", "model": "MEDIUM" },
      "critic":        { "provider": "codex" },
      "code-reviewer": { "provider": "gemini" },
      "test-engineer": { "provider": "gemini", "model": "MEDIUM" }
    }
  }
}
```

| 角色 | 提供者 | 模型 |
|------|--------|------|
| `orchestrator` | claude（固定） | 继承调用会话 |
| `planner` | claude | `HIGH`（opus） |
| `analyst` | claude | `HIGH`（opus） |
| `executor` | claude | `MEDIUM`（sonnet） |
| `critic` | codex | codex 默认 |
| `code-reviewer` | gemini | gemini 默认 |
| `test-engineer` | gemini | `MEDIUM`（sonnet） |

### 规范角色

`orchestrator`、`planner`、`analyst`、`architect`、`executor`、`debugger`、`critic`、`code-reviewer`、`security-reviewer`、`test-engineer`、`designer`、`writer`、`code-simplifier`、`explore`、`document-specialist`。

用户友好别名通过 `normalizeDelegationRole()` 规范化 — 如 `reviewer` → `code-reviewer`、`quality-reviewer` → `code-reviewer`、`harsh-critic` → `critic`、`build-fixer` → `debugger`。已接受的别名键在解析快照创建和后续阶段路由中被尊重，不仅仅是验证。未知角色在解析时验证失败。

### 规范字段（`TeamRoleAssignmentSpec`）

- **provider** — `"claude" | "codex" | "gemini"`。省略 → 默认 `claude`。
- **model** — 层级名称（`"HIGH" | "MEDIUM" | "LOW"`）或显式模型 ID。层级通过 `routing.tierModels` 解析。
- **agent** — 可选 Claude 代理名称（如 `"critic"`、`"executor"`）。仅在解析的提供者为 `claude` 时被尊重。

`orchestrator` 固定为 `claude`；仅 `model` 可由用户配置。`orchestrator` 上的任何其他键被验证器拒绝。

### 环境覆盖

```bash
OMC_TEAM_ROLE_OVERRIDES='{"critic":{"provider":"codex"},"code-reviewer":{"provider":"gemini"}}'
```

优先级：`OMC_TEAM_ROLE_OVERRIDES` > `.claude/omc.jsonc`（项目）> `~/.config/claude-omc/config.jsonc`（用户）> 内置默认值。无效 JSON 记录警告并被忽略 — 环境覆盖是尽力而为的，绝不中止运行。

### CLI 缺失时的回退

如果配置提供者的 CLI 在生成时不存在于 `PATH` 中，`buildLaunchArgs()` 抛出异常，团队主控发出可见的 `SendMessage` 警告，运行时回退到由 `buildResolvedRoutingSnapshot` 预计算的确定性 Claude 分配（相同层级 + 相同代理，`provider: "claude"`）。回退是有意可见的 — 静默回退是测试失败。使用 `omc doctor --team-routing` 探测提供者可用性。

### 粘性 — 解析一次，到处复用

解析的路由在每个团队中不可变。团队生命周期中编辑配置不影响运行中的团队；新的 `/team` 调用获取新映射。这保证生成、扩展和工作者重启都看到相同的路由，包括跨 worktree 分离（快照随 `TeamConfig` 传播）。

### 零配置行为

空的 `team.roleRouting` 保留补丁前行为：每个工作者是 Claude，模型层级遵循 `routing.tierModels`，`/team 3:executor ...` 仍然生成三个 Claude Sonnet 执行器。

## 状态清理

成功完成时：

1. `TeamDelete` 处理所有 Claude Code 状态：
   - 删除 `~/.claude/teams/{team_name}/`（配置）
   - 删除 `~/.claude/tasks/{team_name}/`（所有任务文件 + 锁）
2. 通过 MCP 工具清理 OMC 状态：
   ```
   state_clear(mode="team")
   ```
   如果链接到 Ralph：
   ```
   state_clear(mode="ralph")
   ```
3. 或运行 `/oh-my-claudecode:cancel` 自动处理所有清理。

**重要：** 仅在所有队友关闭后调用 `TeamDelete`。如果配置中仍有活跃成员（除主控外），`TeamDelete` 将失败。

## Git Worktree 集成

MCP 工作者可以在隔离的 git worktree 中操作，以防止并发工作者之间的文件冲突。

### 工作原理

1. **Worktree 创建**：生成工作者前，调用 `createWorkerWorktree(teamName, workerName, repoRoot)` 在 `.omc/worktrees/{team}/{worker}` 创建隔离 worktree，分支为 `omc-team/{teamName}/{workerName}`。

2. **工作者隔离**：将 worktree 路径作为工作者 `BridgeConfig` 中的 `workingDirectory` 传递。工作者专门在自己的 worktree 中操作。

3. **合并协调**：工作者完成任务后，使用 `checkMergeConflicts()` 验证分支可以干净合并，然后使用 `mergeWorkerBranch()` 以 `--no-ff` 合并以获得清晰历史。

4. **团队清理**：团队关闭时，调用 `cleanupTeamWorktrees(teamName, repoRoot)` 删除所有 worktree 及其分支。

### API 参考

| 函数 | 描述 |
|------|------|
| `createWorkerWorktree(teamName, workerName, repoRoot, baseBranch?)` | 创建隔离 worktree |
| `removeWorkerWorktree(teamName, workerName, repoRoot)` | 删除 worktree 和分支 |
| `listTeamWorktrees(teamName, repoRoot)` | 列出所有团队 worktree |
| `cleanupTeamWorktrees(teamName, repoRoot)` | 删除所有团队 worktree |
| `checkMergeConflicts(workerBranch, baseBranch, repoRoot)` | 非破坏性冲突检查 |
| `mergeWorkerBranch(workerBranch, baseBranch, repoRoot)` | 合并工作者分支（--no-ff） |
| `mergeAllWorkerBranches(teamName, repoRoot, baseBranch?)` | 合并所有已完成工作者 |

### 重要说明

- `tmux-session.ts` 中的 `createSession()` 不处理 worktree 创建 — worktree 生命周期通过 `git-worktree.ts` 单独管理
- Worktree 不在单个工作者关闭时清理 — 仅在团队关闭时清理，以允许事后检查
- 分支名称通过 `sanitizeName()` 净化以防止注入
- 所有路径都经过目录遍历验证

## 注意事项

1. **内部任务污染 TaskList** — 当队友生成时，系统自动创建 `metadata._internal: true` 的内部任务。这些出现在 `TaskList` 输出中。计算实际任务进度时过滤它们。内部任务的主题是队友的名称。

2. **无原子声明** — 不像 SQLite swarm，`TaskUpdate` 没有事务保证。两个队友可能竞争声明同一任务。**缓解措施：** 主控应在生成队友前通过 `TaskUpdate(taskId, owner)` 预分配所有者。队友应仅处理分配给他们的任务。

3. **任务 ID 是字符串** — ID 是自增字符串（"1"、"2"、"3"），不是整数。始终向 `taskId` 字段传递字符串值。

4. **TeamDelete 需要空团队** — 调用 `TeamDelete` 前所有队友必须关闭。主控（唯一剩余成员）被排除在此检查之外。

5. **消息自动送达** — 队友消息作为新对话轮次到达主控。入站消息无需轮询或收件箱检查。但是，如果主控正在处理中（处理中），消息会排队并在轮次结束时送达。

6. **队友提示存储在配置中** — 完整提示文本存储在 `config.json` 成员数组中。不要在队友提示中放置密钥或敏感数据。

7. **关闭时成员自动移除** — 队友批准关闭并终止后，自动从 `config.json` 移除。不要重新读取配置期望找到已关闭的队友。

8. **shutdown_response 需要 request_id** — 队友必须从传入的关闭请求 JSON 中提取 `request_id` 并传回。格式为 `shutdown-{timestamp}@{worker-name}`。伪造此 ID 将导致关闭静默失败。

9. **团队名称必须是有效的 slug** — 使用小写字母、数字和连字符。从任务描述派生（如"fix TypeScript errors"变为"fix-ts-errors"）。

10. **广播成本高** — 每次广播向每个队友发送单独消息。默认使用 `message`（DM）。仅在真正的团队范围关键警报时广播。

11. **CLI 工作者是一次性的，不是持久的** — Tmux CLI 工作者有完整文件系统访问权限，可以进行代码更改。但是，它们作为自主一次性作业运行 — 不能使用 TaskList/TaskUpdate/SendMessage。主控必须管理它们的生命周期：写入 prompt_file，生成 CLI 工作者，读取 output_file，标记任务完成。它们不像 Claude 队友那样参与团队通信。
