---
name: cancel
description: 取消任何活跃的 OMC 模式（autopilot、ralph、ultrawork、ultraqa、swarm、ultrapilot、pipeline、team）
argument-hint: "[--force|--all]"
level: 2
---

# 取消技能

智能取消，检测并取消活跃的 OMC 模式。

**取消技能是完成和退出任何 OMC 模式的标准方式。**
当停止钩子检测到工作完成时，它会指示 LLM 调用此技能进行正确的状态清理。
如果取消失败或被中断，使用 `--force` 标志重试，或等待 2 小时过期超时作为最后手段。

## 功能说明

自动检测哪个模式处于活跃状态并取消它：
- **Autopilot**：停止工作流，保留进度以便恢复
- **Ralph**：停止持久循环，清除关联的 ultrawork（如适用）
- **Ultrawork**：停止并行执行（独立或关联的）
- **UltraQA**：停止 QA 循环工作流
- **Swarm**：停止协调的代理群，释放已认领的任务
- **Ultrapilot**：停止并行 autopilot 工作者
- **Pipeline**：停止顺序代理管道
- **Team**：向所有队友发送 shutdown_request，等待响应，调用 TeamDelete，清除关联的 ralph（如存在）
- **Team+Ralph（关联）**：先取消 team（优雅关闭），然后清除 ralph 状态。取消关联的 ralph 时也会先取消 team。

## 使用方法

```
/oh-my-claudecode:cancel
```

或说："cancelomc"、"stopomc"

## 关键：延迟工具处理

状态管理工具（`state_clear`、`state_read`、`state_write`、`state_list_active`、`state_get_status`）可能被 Claude Code 注册为**延迟工具**。在调用任何状态工具之前，您必须先通过 `ToolSearch` 加载所有工具：

```
ToolSearch(query="select:mcp__plugin_oh-my-claudecode_t__state_clear,mcp__plugin_oh-my-claudecode_t__state_read,mcp__plugin_oh-my-claudecode_t__state_write,mcp__plugin_oh-my-claudecode_t__state_list_active,mcp__plugin_oh-my-claudecode_t__state_get_status")
```

如果 `state_clear` 不可用或失败，使用此 **bash 回退**作为**停止钩子循环的紧急退出**。这不是取消流程的完整替代品——它仅移除状态文件以解除会话阻塞。关联模式（如 ralph→ultrawork、autopilot→ralph/ultraqa）必须通过每个模式运行一次回退来单独清除。

将 `MODE` 替换为特定模式（如 `ralplan`、`ralph`、`ultrawork`、`ultraqa`）。

**警告：** 不要对 `autopilot` 或 `omc-teams` 使用此回退。Autopilot 需要 `state_write(active=false)` 来保留恢复数据。omc-teams 需要 tmux 会话清理，仅通过文件删除无法完成。

```bash
# 回退：当 state_clear MCP 工具不可用时直接移除文件
SESSION_ID="${CLAUDE_SESSION_ID:-${CLAUDECODE_SESSION_ID:-}}"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || { d="$PWD"; while [ "$d" != "/" ] && [ ! -d "$d/.omc" ]; do d="$(dirname "$d")"; done; echo "$d"; })"

# 跨平台 SHA-256（macOS: shasum, Linux: sha256sum）
sha256portable() { printf '%s' "$1" | (sha256sum 2>/dev/null || shasum -a 256) | cut -c1-16; }

# 解析状态目录（支持 OMC_STATE_DIR 集中存储）
if [ -n "${OMC_STATE_DIR:-}" ]; then
  # 镜像 worktree-paths.ts 中的 getProjectIdentifier()
  SOURCE="$(git remote get-url origin 2>/dev/null || echo "$REPO_ROOT")"
  HASH="$(sha256portable "$SOURCE")"
  DIR_NAME="$(basename "$REPO_ROOT" | sed 's/[^a-zA-Z0-9_-]/_/g')"
  OMC_STATE="$OMC_STATE_DIR/${DIR_NAME}-${HASH}/state"
  [ ! -d "$OMC_STATE" ] && { echo "ERROR: State dir not found at $OMC_STATE" >&2; exit 1; }
elif [ "$REPO_ROOT" != "/" ] && [ -d "$REPO_ROOT/.omc" ]; then
  OMC_STATE="$REPO_ROOT/.omc/state"
else
  echo "ERROR: Could not locate .omc state directory" >&2
  exit 1
fi
MODE="ralplan"  # <-- 替换为目标模式

# 清除特定模式的会话范围状态
if [ -n "$SESSION_ID" ] && [ -d "$OMC_STATE/sessions/$SESSION_ID" ]; then
  rm -f "$OMC_STATE/sessions/$SESSION_ID/${MODE}-state.json"
  rm -f "$OMC_STATE/sessions/$SESSION_ID/${MODE}-stop-breaker.json"
  rm -f "$OMC_STATE/sessions/$SESSION_ID/skill-active-state.json"
  # 写入取消信号，让停止钩子检测到取消正在进行
  NOW_ISO="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  EXPIRES_ISO="$(date -u -d "+30 seconds" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || python3 - <<'PY'\nfrom datetime import datetime, timedelta, timezone\nprint((datetime.now(timezone.utc) + timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%SZ'))\nPY\n)"
  printf '{"active":true,"requested_at":"%s","expires_at":"%s","mode":"%s","source":"bash_fallback"}' \
    "$NOW_ISO" "$EXPIRES_ISO" "$MODE" > "$OMC_STATE/sessions/$SESSION_ID/cancel-signal-state.json"
fi

# 仅在没有会话 ID 时清除遗留状态（避免清除其他会话的状态）
if [ -z "$SESSION_ID" ]; then
  rm -f "$OMC_STATE/${MODE}-state.json"
fi
```

## 自动检测

`/oh-my-claudecode:cancel` 遵循会话感知状态契约：
- 默认情况下，命令通过 `state_list_active` 和 `state_get_status` 检查当前会话，导航 `.omc/state/sessions/{sessionId}/…` 以发现哪个模式处于活跃状态。
- 当提供或已知会话 ID 时，该会话范围路径是权威的。仅在会话 ID 缺失或为空时，才将 `.omc/state/*.json` 中的遗留文件作为兼容性回退进行查阅。
- Swarm 是共享的 SQLite/标记模式（`.omc/state/swarm.db` / `.omc/state/swarm-active.marker`），不受会话范围限制。
- 默认清理流程使用会话 ID 调用 `state_clear` 以仅移除匹配的会话文件；模式保持绑定到其原始会话。

活跃模式仍按依赖顺序取消：
1. Autopilot（包括关联的 ralph/ultraqa/ 清理）
2. Ralph（清理其关联的 ultrawork 或）
3. Ultrawork（独立）
4. UltraQA（独立）
5. Swarm（独立）
6. Ultrapilot（独立）
7. Pipeline（独立）
8. Team（Claude Code 原生）
9. OMC Teams（tmux CLI 工作者）
10. Plan Consensus（独立）
11. Self-Improve（独立——清除状态，清理孤立的 worktree，保留 iteration_state 以便恢复，在解析的 `<self-improve-root>/state/agent-settings.json` 中设置 status: "user_stopped"；新运行使用 `.omc/self-improve/topics/<topic-slug>/`，扁平 `.omc/self-improve/` 仅保留用于遗留单轨恢复）

## 强制清除全部

当您需要擦除每个会话及遗留工件时使用 `--force` 或 `--all`，例如完全重置工作区。

```
/oh-my-claudecode:cancel --force
```

```
/oh-my-claudecode:cancel --all
```

底层步骤：
1. `state_list_active` 枚举 `.omc/state/sessions/{sessionId}/…` 以查找每个已知会话。
2. `state_clear` 对每个会话运行一次以删除该会话的文件。
3. 不带 `session_id` 的全局 `state_clear` 移除 `.omc/state/*.json`、`.omc/state/swarm*.db` 和兼容性工件下的遗留文件（见列表）。
4. Team 工件（`~/.claude/teams/*/`、`~/.claude/tasks/*/`、`.omc/state/team-state.json`）作为遗留回退的一部分尽力清理。
   - 原生 team 的取消不影响 omc-teams 状态，反之亦然。

每个 `state_clear` 命令都遵守 `session_id` 参数，因此即使是强制模式也会在删除遗留文件之前先清除会话范围路径。

遗留兼容性列表（仅在 `--force`/`--all` 下移除）：
- `.omc/state/autopilot-state.json`
- `.omc/state/ralph-state.json`
- `.omc/state/ralph-plan-state.json`
- `.omc/state/ralph-verification.json`
- `.omc/state/ultrawork-state.json`
- `.omc/state/ultraqa-state.json`
- `.omc/state/swarm.db`
- `.omc/state/swarm.db-wal`
- `.omc/state/swarm.db-shm`
- `.omc/state/swarm-active.marker`
- `.omc/state/swarm-tasks.db`
- `.omc/state/ultrapilot-state.json`
- `.omc/state/ultrapilot-ownership.json`
- `.omc/state/pipeline-state.json`
- `.omc/state/omc-teams-state.json`
- `.omc/state/plan-consensus.json`
- `.omc/state/ralplan-state.json`
- `.omc/state/boulder.json`
- `.omc/state/hud-state.json`
- `.omc/state/subagent-tracking.json`
- `.omc/state/subagent-tracker.lock`
- `.omc/state/rate-limit-daemon.pid`
- `.omc/state/rate-limit-daemon.log`
- `.omc/state/checkpoints/`（目录）
- `.omc/state/sessions/`（清除会话后的空目录清理）

## 实施步骤

调用此技能时：

### 1. 解析参数

```bash
# 检查 --force 或 --all 标志
FORCE_MODE=false
if [[ "$*" == *"--force"* ]] || [[ "$*" == *"--all"* ]]; then
  FORCE_MODE=true
fi
```

### 2. 检测活跃模式

该技能现在依赖会话感知状态契约而非硬编码文件路径：
1. 调用 `state_list_active` 枚举 `.omc/state/sessions/{sessionId}/…` 并发现每个活跃会话。
2. 对每个会话 ID，调用 `state_get_status` 了解哪个模式正在运行（`autopilot`、`ralph`、`ultrawork` 等）以及是否存在依赖模式。
3. 如果向 `/oh-my-claudecode:cancel` 提供了 `session_id`，则完全跳过遗留回退，仅在该会话路径内操作；否则，仅在状态工具报告无活跃会话时才查阅 `.omc/state/*.json` 中的遗留文件。Swarm 仍是会话范围外的共享 SQLite/标记模式。
4. 本文档中的任何取消逻辑都镜像通过状态工具发现的依赖顺序（autopilot → ralph → …）。

### 3A. 强制模式（如果 --force 或 --all）

使用强制模式通过 `state_clear` 清除每个会话及遗留工件。直接文件移除仅在状态工具报告无活跃会话时用于遗留清理。

### 3B. 智能取消（默认）

#### 如果 Team 活跃（Claude Code 原生）

通过检查 `${CLAUDE_CONFIG_DIR:-~/.claude}/teams/` 中的配置文件来检测 Team：

```bash
# 检查活跃的 team
TEAM_CONFIGS=$(find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/teams -name config.json -maxdepth 2 2>/dev/null)
```

**两遍取消协议：**

**第一遍：优雅关闭**
```
对于在 ${CLAUDE_CONFIG_DIR:-~/.claude}/teams/ 中找到的每个 team：
  1. 读取 config.json 获取 team_name 和成员列表
  2. 对每个非负责人成员：
     a. 通过 SendMessage 发送 shutdown_request
     b. 等待最多 15 秒获取 shutdown_response
     c. 如果收到响应：成员终止并自动移除
     d. 如果超时：标记成员为无响应，继续下一个
  3. 记录："优雅关闭：X/Y 成员响应"
```

**第二遍：协调**
```
优雅关闭后：
  1. 重新读取 config.json 检查剩余成员
  2. 如果只剩负责人（或配置为空）：继续 TeamDelete
  3. 如果无响应成员仍存在：
     a. 再等待 5 秒（它们可能仍在处理）
     b. 再次重新读取 config.json
     c. 如果仍卡住：尝试 TeamDelete
     d. 如果 TeamDelete 失败：报告手动清理路径
```

**TeamDelete + 清理：**
```
  1. 调用 TeamDelete() — 移除 ~/.claude/teams/{name}/ 和 ~/.claude/tasks/{name}/
  2. 清除 team 状态：state_clear(mode="team")
  3. 检查关联的 ralph：state_read(mode="ralph") — 如果 linked_team 为 true：
     a. 清除 ralph 状态：state_clear(mode="ralph")
     b. 清除关联的 ultrawork（如存在）：state_clear(mode="ultrawork")
  4. 运行孤立扫描（见下文）
  5. 发出结构化取消报告
```

**孤立检测（清理后）：**

TeamDelete 后，验证没有代理进程残留：
```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/cleanup-orphans.mjs" --team-name "{team_name}"
```

孤立扫描器：
1. 检查 `ps aux`（Unix）或 `tasklist`（Windows）中具有匹配已删除 team 的 `--team-name` 的进程
2. 对每个 team 配置不再存在的孤立进程：发送 SIGTERM，等待 5 秒，如果仍存活则发送 SIGKILL
3. 以 JSON 格式报告清理结果

使用 `--dry-run` 检查而不终止。扫描器可安全多次运行。

**结构化取消报告：**
```
Team "{team_name}" 已取消：
  - 信号发送成员数：N
  - 收到响应数：M
  - 无响应：K（如有则列出名称）
  - TeamDelete：成功/失败
  - 需要手动清理：是/否
    路径：~/.claude/teams/{name}/ 和 ~/.claude/tasks/{name}/
```

**实施说明：** 取消技能由 LLM 执行，而非作为 bash 脚本。当您检测到活跃的 team 时：
1. 读取 `${CLAUDE_CONFIG_DIR:-~/.claude}/teams/*/config.json` 查找活跃的 team
2. 如果存在多个 team，先取消最旧的（按 `createdAt`）
3. 对每个非负责人成员，调用 `SendMessage(type: "shutdown_request", recipient: member-name, content: "Cancelling")`
4. 短暂等待关闭响应（每个成员 15 秒超时）
5. 重新读取 config.json 检查剩余成员（协调遍）
6. 调用 `TeamDelete()` 进行清理
7. 清除 team 状态：`state_clear(mode="team", session_id)`
8. 向用户报告结构化摘要

#### 如果 Autopilot 活跃

Autopilot 处理自己的清理，包括关联的 ralph 和 ultraqa。

1. 通过 `state_read(mode="autopilot", session_id)` 读取 autopilot 状态获取当前阶段
2. 通过 `state_read(mode="ralph", session_id)` 检查关联的 ralph：
   - 如果 ralph 活跃且有 `linked_ultrawork: true`，先清除 ultrawork：`state_clear(mode="ultrawork", session_id)`
   - 清除 ralph：`state_clear(mode="ralph", session_id)`
3. 通过 `state_read(mode="ultraqa", session_id)` 检查关联的 ultraqa：
   - 如果活跃，清除它：`state_clear(mode="ultraqa", session_id)`
4. 通过 `state_write(mode="autopilot", session_id, state={active: false, ...existing})` 将 autopilot 标记为非活跃（保留状态以便恢复）

#### 如果 Ralph 活跃（但不是 Autopilot）

1. 通过 `state_read(mode="ralph", session_id)` 读取 ralph 状态检查关联的 ultrawork
2. 如果 `linked_ultrawork: true`：
   - 读取 ultrawork 状态验证 `linked_to_ralph: true`
   - 如果关联，清除 ultrawork：`state_clear(mode="ultrawork", session_id)`
3. 清除 ralph：`state_clear(mode="ralph", session_id)`

#### 如果 Ultrawork 活跃（独立，未关联）

1. 通过 `state_read(mode="ultrawork", session_id)` 读取 ultrawork 状态
2. 如果 `linked_to_ralph: true`，警告用户改为取消 ralph（会级联取消）
3. 否则清除：`state_clear(mode="ultrawork", session_id)`

#### 如果 UltraQA 活跃（独立）

直接清除：`state_clear(mode="ultraqa", session_id)`

#### 无活跃模式

报告："未检测到活跃的 OMC 模式。使用 --force 强制清除所有状态文件。"

## 实施说明

取消技能按以下方式运行：
1. 解析 `--force` / `--all` 标志，跟踪清理是否应跨越每个会话还是保持在当前会话 ID 范围内。
2. 使用 `state_list_active` 枚举已知会话 ID，使用 `state_get_status` 了解每个会话的活跃模式（`autopilot`、`ralph`、`ultrawork` 等）。
3. 在默认模式下操作时，使用该 session_id 调用 `state_clear` 以仅移除会话的文件，然后根据状态工具信号运行模式特定清理（autopilot → ralph → …）。
4. 在强制模式下，遍历每个活跃会话，对每个会话调用 `state_clear`，然后运行不带 `session_id` 的全局 `state_clear` 以删除遗留文件（`.omc/state/*.json`、兼容性工件）并报告成功。Swarm 仍是会话范围外的共享 SQLite/标记模式。
5. Team 工件（`~/.claude/teams/*/`、`~/.claude/tasks/*/`、`.omc/state/team-state.json`）在遗留/全局遍期间作为尽力清理项调用。
6. **始终**在最后一步清除 skill-active 状态，无论哪个模式处于活跃状态或是否使用了 `--force`：
   ```
   state_clear(mode="skill-active", session_id)
   ```
   这确保停止钩子不会因过期的 `skill-active-state.json` 在取消后继续触发技能保护加固。参见 issue #2118。

状态工具始终遵守 `session_id` 参数，因此即使是强制模式也会在删除仅兼容的遗留状态之前先清除会话范围路径。

下面的模式特定子节描述了每个处理器在状态范围操作完成后执行的额外清理。

## 消息参考

| 模式 | 成功消息 |
|------|----------|
| Autopilot | "Autopilot 已在阶段 {phase} 取消。进度已保留以便恢复。" |
| Ralph | "Ralph 已取消。持久模式已停用。" |
| Ultrawork | "Ultrawork 已取消。并行执行模式已停用。" |
| UltraQA | "UltraQA 已取消。QA 循环工作流已停止。" |
| Swarm | "Swarm 已取消。协调的代理已停止。" |
| Ultrapilot | "Ultrapilot 已取消。并行 autopilot 工作者已停止。" |
| Pipeline | "Pipeline 已取消。顺序代理链已停止。" |
| Team | "Team 已取消。队友已关闭并清理。" |
| Plan Consensus | "Plan Consensus 已取消。规划会话已结束。" |
| Force | "所有 OMC 模式已清除。您可以重新开始。" |
| None | "未检测到活跃的 OMC 模式。" |

## 保留内容

| 模式 | 保留状态 | 恢复命令 |
|------|----------|----------|
| Autopilot | 是（阶段、文件、规格、计划、判定） | `/oh-my-claudecode:autopilot` |
| Ralph | 否 | N/A |
| Ultrawork | 否 | N/A |
| UltraQA | 否 | N/A |
| Swarm | 否 | N/A |
| Ultrapilot | 否 | N/A |
| Pipeline | 否 | N/A |
| Plan Consensus | 是（保留计划文件路径） | N/A |

## 说明

- **依赖感知**：Autopilot 取消会清理 Ralph 和 UltraQA
- **关联感知**：Ralph 取消会清理关联的 Ultrawork
- **安全**：仅清除关联的 Ultrawork，保留独立的 Ultrawork
- **仅本地**：清除 `.omc/state/` 目录中的状态文件
- **恢复友好**：Autopilot 状态保留以便无缝恢复
- **Team 感知**：检测原生 Claude Code team 并执行优雅关闭

## MCP 工作者清理

当取消可能生成了 MCP 工作者（team bridge 守护进程）的模式时，取消技能还应：

1. **检查活跃的 MCP 工作者**：查找 `.omc/state/team-bridge/{team}/*.heartbeat.json` 中的心跳文件
2. **发送关闭信号**：为每个活跃工作者写入关闭信号文件
3. **终止 tmux 会话**：对每个工作者运行 `tmux kill-session -t omc-team-{team}-{worker}`
4. **清理心跳文件**：移除该 team 的所有心跳文件
5. **清理影子注册表**：移除 `.omc/state/team-mcp-workers.json`

### 强制清除附加项

使用 `--force` 时，同时清理：
```bash
rm -rf .omc/state/team-bridge/       # 心跳文件
rm -f .omc/state/team-mcp-workers.json  # 影子注册表
# 终止所有 omc-team-* tmux 会话
tmux list-sessions -F '#{session_name}' 2>/dev/null | grep '^omc-team-' | while read s; do tmux kill-session -t "$s" 2>/dev/null; done
```
