---
name: omc-teams
description: 当你需要基于进程的并行执行时，在 tmux 窗格中为 claude、codex 或 gemini 工作进程提供 CLI 团队运行时
aliases: []
level: 4
---

# OMC 团队技能

在 tmux 窗格中生成 N 个 CLI 工作进程以并行执行任务。支持 `claude`、`codex` 和 `gemini` 代理类型。

`/omc-teams` 是 CLI 优先运行时的遗留兼容技能：使用 `omc team ...` 命令（不推荐使用已弃用的 MCP 运行时工具）。

## 用法

```bash
/oh-my-claudecode:omc-teams N:claude "task description"
/oh-my-claudecode:omc-teams N:codex "task description"
/oh-my-claudecode:omc-teams N:gemini "task description"
```

### 参数

- **N** - CLI 工作进程数量（1-10）
- **agent-type** - `claude`（Claude CLI）、`codex`（OpenAI Codex CLI）或 `gemini`（Google Gemini CLI）
- **task** - 要分配给所有工作进程的任务描述

### 示例

```bash
/omc-teams 2:claude "implement auth module with tests"
/omc-teams 2:codex "review the auth module for security issues"
/omc-teams 3:gemini "redesign UI components for accessibility"
```

## 要求

- **tmux 二进制文件**必须已安装且可发现（`command -v tmux`）
- **经典 tmux 会话可选**用于就地窗格分割（`$TMUX` 已设置）。在 cmux 或普通终端内，`omc team` 会回退到分离的 tmux 会话，而不是分割当前表面。
- **claude** CLI：`npm install -g @anthropic-ai/claude-code`
- **codex** CLI：`npm install -g @openai/codex`
- **gemini** CLI：`npm install -g @google/gemini-cli`

## 工作流

### 阶段 0：验证先决条件

在声称 tmux 缺失之前显式检查：

```bash
command -v tmux >/dev/null 2>&1
```

- 如果失败，报告**tmux 未安装**并停止。
- 如果 `$TMUX` 已设置，`omc team` 可以直接重用当前 tmux 窗口/窗格。
- 如果 `$TMUX` 为空但 `CMUX_SURFACE_ID` 已设置，报告用户在 **cmux** 内运行。不要说 tmux 缺失或他们"不在 tmux 内"；`omc team` 将启动一个**分离的 tmux 会话**用于工作进程，而不是分割 cmux 表面。
- 如果 `$TMUX` 和 `CMUX_SURFACE_ID` 都未设置，报告用户在**普通终端**中。`omc team` 仍然可以启动**分离的 tmux 会话**，但如果他们特别想要就地窗格/窗口拓扑，应首先从经典 tmux 会话开始。
- 如果需要确认活跃的 tmux 会话，使用：

```bash
tmux display-message -p '#S'
```

### 阶段 1：解析 + 验证输入

提取：

- `N` — 工作进程数量（1–10）
- `agent-type` — `claude|codex|gemini`
- `task` — 任务描述

在分解或运行任何内容之前验证：

- 预先拒绝不支持的代理类型。`/omc-teams` 仅支持 **`claude`**、**`codex`** 和 **`gemini`**。
- 如果用户请求不支持的类型如 `expert`，解释 `/omc-teams` 仅启动外部 CLI 工作进程。
- 对于原生 Claude Code 团队代理/角色，引导他们使用 **`/oh-my-claudecode:team`**。

### 阶段 2：分解任务

将工作分解为 N 个独立子任务（按文件或关注点范围），以避免写入冲突。

### 阶段 2.5：为多仓库计划解析工作区根目录

`omc team` 使用一个共享工作目录启动所有工作进程。对于单仓库任务，当前仓库通常是正确的。对于多仓库任务，特别是当计划在一个仓库中但实现涉及兄弟仓库时，在启动前解析工作目录：

- 如果任务引用了一个仓库下的计划产物（例如 `tool/.omc/plans/task-1200-gwd-gifs.md`）和兄弟仓库中的目标路径（例如 `api/` 和 `admin/`），选择包含所有参与仓库的共享工作区根目录（例如父级 `inter/` 目录）。
- 在任务文本中使用**绝对计划路径**，以便工作进程在 `--cwd` 更改启动目录后仍能找到计划。
- 在任务文本和子任务中包含显式的仓库路径或仓库名称。
- 当目标仓库是兄弟仓库时，不要将启动 cwd 仅锚定到包含 `.omc/plans/...` 的仓库；这会将 `codex`、`claude` 和 `gemini` 工作进程困在计划仓库中而不是实现工作区。
- 如果无法识别安全的共享工作区根目录，不要启动 `/omc-teams`。报告单 cwd 约束并询问或从证据中推导预期的工作区根目录。

### 阶段 3：启动 CLI 团队运行时

激活模式状态（推荐）：

```text
state_write(mode="team", current_phase="team-exec", active=true)
```

通过 CLI 启动工作进程：

```bash
omc team <N>:<claude|codex|gemini> "<task>"
```

对于阶段 2.5 中解析的多仓库情况，从共享工作区根目录启动，使用现有的 `--cwd` 约定并保持计划引用为绝对路径：

```bash
omc team <N>:<claude|codex|gemini> "<task with absolute plan path and explicit repo paths>" --cwd <workspace-root>
```

团队名称默认为任务文本的 slug（例如：`review-auth-flow`）。

启动后，验证命令是否实际执行，而不是假设 Enter 已触发。检查窗格输出并确认命令或工作进程引导文本出现在窗格历史中：

```bash
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_id} #{pane_current_command}'
tmux capture-pane -pt <pane-id> -S -20
```

除非窗格输出显示命令已提交，否则不要声称团队已成功启动。

### 阶段 4：监控 + 生命周期 API

```bash
omc team status <team-name>
omc team api list-tasks --input '{"team_name":"<team-name>"}' --json
```

使用 `omc team api ...` 进行任务认领、任务转换、邮箱传递和工作进程状态更新。

### 阶段 5：关闭（仅在需要时）

```bash
omc team shutdown <team-name>
omc team shutdown <team-name> --force
```

使用关闭进行有意的取消或过期状态清理。优先使用非强制关闭。

### 阶段 6：报告 + 状态关闭

报告任务结果，包含完成/失败摘要和任何剩余风险。

```text
state_write(mode="team", current_phase="complete", active=false)
```

## 已弃用的运行时说明

遗留 MCP 运行时工具已弃用用于执行：

- `omc_run_team_start`
- `omc_run_team_status`
- `omc_run_team_wait`
- `omc_run_team_cleanup`

如果遇到，切换到 `omc team ...` CLI 命令。

## 错误参考

| 错误                           | 原因                                     | 修复                                                                                      |
| ------------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------------------- |
| `not inside tmux`              | 从非 tmux 表面请求就地窗格拓扑           | 启动 tmux 并重新运行，或让 `omc team` 使用其分离会话回退                                   |
| `cmux surface detected`        | 在没有 `$TMUX` 的 cmux 内运行            | 使用正常的 `omc team ...` 流程；OMC 将启动分离的 tmux 会话                                 |
| `Unsupported agent type`       | 请求的代理不是 claude/codex/gemini       | 使用 `claude`、`codex` 或 `gemini`；对于原生 Claude Code 代理使用 `/oh-my-claudecode:team` |
| `codex: command not found`     | Codex CLI 未安装                         | `npm install -g @openai/codex`                                                            |
| `gemini: command not found`    | Gemini CLI 未安装                        | `npm install -g @google/gemini-cli`                                                       |
| `Team <name> is not running`   | 过期或缺失的运行时状态                   | `omc team status <team-name>` 然后如果过期则 `omc team shutdown <team-name> --force`      |
| `status: failed`               | 工作进程退出但工作未完成                 | 检查运行时输出，缩小范围，重新运行                                                        |

## 与 `/team` 的关系

| 方面       | `/team`                                   | `/omc-teams`                                         |
| ---------- | ----------------------------------------- | ---------------------------------------------------- |
| 工作进程类型 | Claude Code 原生团队代理                 | tmux 中的 claude / codex / gemini CLI 进程           |
| 调用方式   | `TeamCreate` / `Task` / `SendMessage`     | `omc team [N:agent]` + `status` + `shutdown` + `api` |
| 协调方式   | 原生团队消息和分阶段管道                 | tmux 工作进程运行时 + CLI API 状态文件               |
| 使用场景   | 你想要 Claude 原生团队编排               | 你想要外部 CLI 工作进程执行                          |
