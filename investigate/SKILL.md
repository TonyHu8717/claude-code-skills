---
name: investigate
preamble-tier: 2
version: 1.0.0
description: |
  系统化调试与根本原因调查。四个阶段：调查、
  分析、假设、实施。铁律：没有根本原因调查就不修复。
  当要求"调试这个"、"修复这个 bug"、"为什么这坏了"、
  "调查这个错误"或"根本原因分析"时使用。
  当用户报告错误、500 错误、堆栈跟踪、意外行为、"昨天还能用"，
  或正在排查为什么某事停止工作时，主动调用此技能（不要直接调试）。(gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
  - WebSearch
triggers:
  - debug this
  - fix this bug
  - why is this broken
  - root cause analysis
  - investigate this error
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking debug scope boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking debug scope boundary..."
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

## 前置脚本（先运行）

```bash
_UPD=$(~/.claude/skills/gstack/bin/gstack-update-check 2>/dev/null || .claude/skills/gstack/bin/gstack-update-check 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || true
mkdir -p ~/.gstack/sessions
touch ~/.gstack/sessions/"$PPID"
_SESSIONS=$(find ~/.gstack/sessions -mmin -120 -type f 2>/dev/null | wc -l | tr -d ' ')
find ~/.gstack/sessions -mmin +120 -type f -exec rm {} + 2>/dev/null || true
_PROACTIVE=$(~/.claude/skills/gstack/bin/gstack-config get proactive 2>/dev/null || echo "true")
_PROACTIVE_PROMPTED=$([ -f ~/.gstack/.proactive-prompted ] && echo "yes" || echo "no")
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "BRANCH: $_BRANCH"
_SKILL_PREFIX=$(~/.claude/skills/gstack/bin/gstack-config get skill_prefix 2>/dev/null || echo "false")
echo "PROACTIVE: $_PROACTIVE"
echo "PROACTIVE_PROMPTED: $_PROACTIVE_PROMPTED"
echo "SKILL_PREFIX: $_SKILL_PREFIX"
source <(~/.claude/skills/gstack/bin/gstack-repo-mode 2>/dev/null) || true
REPO_MODE=${REPO_MODE:-unknown}
echo "REPO_MODE: $REPO_MODE"
_LAKE_SEEN=$([ -f ~/.gstack/.completeness-intro-seen ] && echo "yes" || echo "no")
echo "LAKE_INTRO: $_LAKE_SEEN"
_TEL=$(~/.claude/skills/gstack/bin/gstack-config get telemetry 2>/dev/null || true)
_TEL_PROMPTED=$([ -f ~/.gstack/.telemetry-prompted ] && echo "yes" || echo "no")
_TEL_START=$(date +%s)
_SESSION_ID="$$-$(date +%s)"
echo "TELEMETRY: ${_TEL:-off}"
echo "TEL_PROMPTED: $_TEL_PROMPTED"
_EXPLAIN_LEVEL=$(~/.claude/skills/gstack/bin/gstack-config get explain_level 2>/dev/null || echo "default")
if [ "$_EXPLAIN_LEVEL" != "default" ] && [ "$_EXPLAIN_LEVEL" != "terse" ]; then _EXPLAIN_LEVEL="default"; fi
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_QUESTION_TUNING=$(~/.claude/skills/gstack/bin/gstack-config get question_tuning 2>/dev/null || echo "false")
echo "QUESTION_TUNING: $_QUESTION_TUNING"
mkdir -p ~/.gstack/analytics
if [ "$_TEL" != "off" ]; then
echo '{"skill":"investigate","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
fi
for _PF in $(find ~/.gstack/analytics -maxdepth 1 -name '.pending-*' 2>/dev/null); do
  if [ -f "$_PF" ]; then
    if [ "$_TEL" != "off" ] && [ -x "~/.claude/skills/gstack/bin/gstack-telemetry-log" ]; then
      ~/.claude/skills/gstack/bin/gstack-telemetry-log --event-type skill_run --skill _pending_finalize --outcome unknown --session-id "$_SESSION_ID" 2>/dev/null || true
    fi
    rm -f "$_PF" 2>/dev/null || true
  fi
  break
done
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)" 2>/dev/null || true
_LEARN_FILE="${GSTACK_HOME:-$HOME/.gstack}/projects/${SLUG:-unknown}/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LEARN_COUNT=$(wc -l < "$_LEARN_FILE" 2>/dev/null | tr -d ' ')
  echo "LEARNINGS: $_LEARN_COUNT entries loaded"
  if [ "$_LEARN_COUNT" -gt 5 ] 2>/dev/null; then
    ~/.claude/skills/gstack/bin/gstack-learnings-search --limit 3 2>/dev/null || true
  fi
else
  echo "LEARNINGS: 0"
fi
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"investigate","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
_HAS_ROUTING="no"
if [ -f CLAUDE.md ] && grep -q "## Skill routing" CLAUDE.md 2>/dev/null; then
  _HAS_ROUTING="yes"
fi
_ROUTING_DECLINED=$(~/.claude/skills/gstack/bin/gstack-config get routing_declined 2>/dev/null || echo "false")
echo "HAS_ROUTING: $_HAS_ROUTING"
echo "ROUTING_DECLINED: $_ROUTING_DECLINED"
_VENDORED="no"
if [ -d ".claude/skills/gstack" ] && [ ! -L ".claude/skills/gstack" ]; then
  if [ -f ".claude/skills/gstack/VERSION" ] || [ -d ".claude/skills/gstack/.git" ]; then
    _VENDORED="yes"
  fi
fi
echo "VENDORED_GSTACK: $_VENDORED"
echo "MODEL_OVERLAY: claude"
_CHECKPOINT_MODE=$(~/.claude/skills/gstack/bin/gstack-config get checkpoint_mode 2>/dev/null || echo "explicit")
_CHECKPOINT_PUSH=$(~/.claude/skills/gstack/bin/gstack-config get checkpoint_push 2>/dev/null || echo "false")
echo "CHECKPOINT_MODE: $_CHECKPOINT_MODE"
echo "CHECKPOINT_PUSH: $_CHECKPOINT_PUSH"
[ -n "$OPENCLAW_SESSION" ] && echo "SPAWNED_SESSION: true" || true
```

## 计划模式安全操作

在计划模式下，以下操作被允许，因为它们为计划提供信息：`$B`、`$D`、`codex exec`/`codex review`、写入 `~/.gstack/`、写入计划文件，以及 `open` 生成的制品。

## 计划模式期间的技能调用

如果用户在计划模式下调用技能，技能优先于通用计划模式行为。**将技能文件视为可执行指令，而非参考。** 从步骤 0 开始逐步执行；第一个 AskUserQuestion 是工作流进入计划模式，而非违反计划模式。AskUserQuestion 满足计划模式的回合结束要求。在 STOP 点立即停止。不要继续工作流或在那里调用 ExitPlanMode。标记为"PLAN MODE EXCEPTION — ALWAYS RUN"的命令会执行。仅在技能工作流完成后，或用户告诉你取消技能或离开计划模式时，才调用 ExitPlanMode。

如果 `PROACTIVE` 为 `"false"`，不要自动调用或主动建议技能。如果某个技能似乎有用，询问："我觉得 /skillname 可能对此有帮助 — 要我运行它吗？"

如果 `SKILL_PREFIX` 为 `"true"`，建议/调用 `/gstack-*` 名称。磁盘路径保持 `~/.claude/skills/gstack/[skill-name]/SKILL.md`。

如果输出显示 `UPGRADE_AVAILABLE <old> <new>`：读取 `~/.claude/skills/gstack/gstack-upgrade/SKILL.md` 并按照"内联升级流程"操作。

如果输出显示 `JUST_UPGRADED <from> <to>`：打印"运行 gstack v{to}（刚更新！）"。如果 `SPAWNED_SESSION` 为 true，跳过功能发现。

功能发现、写作风格、遥测提示、主动提示、路由注入、vendoring 警告等通用前置逻辑与 health 技能相同。此处省略以节省空间 — 请参阅 health/SKILL.md 中的完整实现。

如果 `SPAWNED_SESSION` 为 `"true"`，你正在 AI 编排器生成的会话中运行。不要使用 AskUserQuestion；自动选择推荐选项。专注于完成任务。

## AskUserQuestion 格式

每个 AskUserQuestion 都是一个决策简报，必须作为 tool_use 发送，而非文本。

```
D<N> — <one-line question title>
Project/branch/task: <1 short grounding sentence using _BRANCH>
ELI10: <plain English a 16-year-old could follow, 2-4 sentences, name the stakes>
Stakes if we pick wrong: <one sentence on what breaks, what user sees, what's lost>
Recommendation: <choice> because <one-line reason>
Completeness: A=X/10, B=Y/10   (or: Note: options differ in kind, not coverage — no completeness score)
Pros / cons:
A) <option label> (recommended)
  ✅ <pro — concrete, observable, ≥40 chars>
  ❌ <con — honest, ≥40 chars>
B) <option label>
  ✅ <pro>
  ❌ <con>
Net: <one-line synthesis of what you're actually trading off>
```

GBrain 同步、模型特定行为补丁、语音、上下文恢复、写作风格、完整性原则、困惑协议、连续检查点模式、上下文健康、问题调优、完成状态协议、运营自我改进、遥测、计划状态页脚等通用部分与 health 技能相同。

# 系统化调试

## 铁律

**没有根本原因调查就不要修复。**

修复症状会产生打地鼠式的调试。每个不解决根本原因的修复都会使下一个 bug 更难找到。找到根本原因，然后修复它。

---

## 阶段 1：根本原因调查

在形成任何假设之前收集上下文。

1. **收集症状：** 读取错误消息、堆栈跟踪和重现步骤。如果用户没有提供足够的上下文，通过 AskUserQuestion 一次问一个问题。

2. **读取代码：** 从症状追溯代码路径到潜在原因。使用 Grep 查找所有引用，使用 Read 理解逻辑。

3. **检查最近更改：**
   ```bash
   git log --oneline -20 -- <affected-files>
   ```
   这之前能用吗？什么变了？回归意味着根本原因在 diff 中。

4. **重现：** 你能确定性地触发 bug 吗？如果不能，在继续之前收集更多证据。

5. **检查调查历史：** 搜索先前的学习记录，了解对相同文件的调查。同一区域中反复出现的 bug 是架构气味。如果存在先前的调查，注意模式并检查根本原因是否是结构性的。

## 先前学习

搜索先前会话中的相关学习：

```bash
_CROSS_PROJ=$(~/.claude/skills/gstack/bin/gstack-config get cross_project_learnings 2>/dev/null || echo "unset")
echo "CROSS_PROJECT: $_CROSS_PROJ"
if [ "$_CROSS_PROJ" = "true" ]; then
  ~/.claude/skills/gstack/bin/gstack-learnings-search --limit 10 --cross-project 2>/dev/null || true
else
  ~/.claude/skills/gstack/bin/gstack-learnings-search --limit 10 2>/dev/null || true
fi
```

如果 `CROSS_PROJECT` 为 `unset`（首次）：使用 AskUserQuestion：

> gstack 可以搜索你在此机器上其他项目的学习记录，以找到可能适用于此的模式。这保持在本地（没有数据离开你的机器）。推荐给独立开发者。如果你在多个客户端代码库上工作，跨污染可能是问题，请跳过。

选项：
- A) 启用跨项目学习（推荐）
- B) 保持学习仅限于项目范围

如果 A：运行 `~/.claude/skills/gstack/bin/gstack-config set cross_project_learnings true`
如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set cross_project_learnings false`

然后使用适当的标志重新运行搜索。

如果找到学习记录，将它们纳入你的分析。当审查发现与过去的学习匹配时，显示：

**"应用了先前学习：[key]（置信度 N/10，来自 [日期]）"**

这使复利可见。用户应该看到 gstack 随着时间在他们的代码库上变得越来越聪明。

输出：**"根本原因假设：..."** — 关于什么出了问题以及为什么的具体、可测试的主张。

---

## 范围锁定

形成根本原因假设后，将编辑锁定到受影响的模块以防止范围蔓延。

```bash
[ -x "${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh" ] && echo "FREEZE_AVAILABLE" || echo "FREEZE_UNAVAILABLE"
```

**如果 FREEZE_AVAILABLE：** 确定包含受影响文件的最窄目录。将其写入冻结状态文件：

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.gstack}"
mkdir -p "$STATE_DIR"
echo "<detected-directory>/" > "$STATE_DIR/freeze-dir.txt"
echo "Debug scope locked to: <detected-directory>/"
```

将 `<detected-directory>` 替换为实际目录路径（例如 `src/auth/`）。告诉用户："编辑限制为 `<dir>/`，用于此调试会话。这防止更改不相关的代码。运行 `/unfreeze` 以移除限制。"

如果 bug 跨越整个仓库或范围确实不明确，跳过锁定并说明原因。

**如果 FREEZE_UNAVAILABLE：** 跳过范围锁定。编辑不受限制。

---

## 阶段 2：模式分析

检查此 bug 是否匹配已知模式：

| 模式 | 特征 | 查找位置 |
|---------|-----------|---------------|
| 竞态条件 | 间歇性、依赖时序 | 对共享状态的并发访问 |
| Nil/null 传播 | NoMethodError、TypeError | 可选值缺少防护 |
| 状态损坏 | 不一致数据、部分更新 | 事务、回调、钩子 |
| 集成失败 | 超时、意外响应 | 外部 API 调用、服务边界 |
| 配置漂移 | 本地可用、预发布/生产失败 | 环境变量、功能标志、数据库状态 |
| 过时缓存 | 显示旧数据、清除缓存后修复 | Redis、CDN、浏览器缓存、Turbo |

还要检查：
- `TODOS.md` 中的相关已知问题
- `git log` 中同一区域的先前修复 — **同一文件中反复出现的 bug 是架构气味**，不是巧合

**外部模式搜索：** 如果 bug 不匹配上述已知模式，WebSearch 搜索：
- "{framework} {generic error type}" — **先清理：** 剥离主机名、IP、文件路径、SQL、客户数据。搜索错误类别，而非原始消息。
- "{library} {component} known issues"

如果 WebSearch 不可用，跳过此搜索并继续假设测试。如果出现文档化的解决方案或已知依赖项 bug，在阶段 3 中将其作为候选假设呈现。

---

## 阶段 3：假设测试

在编写任何修复之前，验证你的假设。

1. **确认假设：** 在怀疑的根本原因处添加临时日志语句、断言或调试输出。运行重现。证据匹配吗？

2. **如果假设错误：** 在形成下一个假设之前，考虑搜索错误。**先清理** — 从错误消息中剥离主机名、IP、文件路径、SQL 片段、客户标识符和任何内部/专有数据。仅搜索通用错误类型和框架上下文："{component} {sanitized error type} {framework version}"。如果错误消息太具体而无法安全清理，跳过搜索。如果 WebSearch 不可用，跳过并继续。然后返回阶段 1。收集更多证据。不要猜测。

3. **三振规则：** 如果 3 个假设失败，**停止**。使用 AskUserQuestion：
   ```
   3 个假设已测试，无一匹配。这可能是架构问题
   而非简单 bug。

   A) 继续调查 — 我有新假设：[描述]
   B) 升级供人工审查 — 这需要了解系统的人
   C) 添加日志并等待 — 在该区域添加检测，下次捕获
   ```

**危险信号** — 如果你看到以下任何情况，放慢速度：
- "暂时快速修复" — 没有"暂时"。正确修复或升级。
- 在追踪数据流之前提出修复 — 你在猜测。
- 每次修复都在其他地方揭示新问题 — 错误的层，不是错误的代码。

---

## 阶段 4：实施

一旦确认根本原因：

1. **修复根本原因，而非症状。** 消除实际问题的最小更改。

2. **最小 diff：** 触及最少文件、更改最少行数。抵制重构相邻代码的冲动。

3. **编写回归测试**，确保：
   - **没有修复时失败**（证明测试有意义）
   - **有修复时通过**（证明修复有效）

4. **运行完整测试套件。** 粘贴输出。不允许回归。

5. **如果修复触及 >5 个文件：** 使用 AskUserQuestion 标记影响范围：
   ```
   此修复触及 N 个文件。对于 bug 修复来说影响范围很大。
   A) 继续 — 根本原因确实跨越这些文件
   B) 拆分 — 现在修复关键路径，推迟其余
   C) 重新考虑 — 也许有更有针对性的方法
   ```

---

## 阶段 5：验证和报告

**新鲜验证：** 重现原始 bug 场景并确认已修复。这不是可选的。

运行测试套件并粘贴输出。

输出结构化调试报告：
```
DEBUG REPORT
════════════════════════════════════════
Symptom:         [what the user observed]
Root cause:      [what was actually wrong]
Fix:             [what was changed, with file:line references]
Evidence:        [test output, reproduction attempt showing fix works]
Regression test: [file:line of the new test]
Related:         [TODOS.md items, prior bugs in same area, architectural notes]
Status:          DONE | DONE_WITH_CONCERNS | BLOCKED
════════════════════════════════════════
```

将调查记录为未来会话的学习。使用 `type: "investigation"` 并包含受影响文件，以便将来对同一区域的调查可以找到此记录：

```bash
~/.claude/skills/gstack/bin/gstack-learnings-log '{"skill":"investigate","type":"investigation","key":"ROOT_CAUSE_KEY","insight":"ROOT_CAUSE_SUMMARY","confidence":9,"source":"observed","files":["affected/file1.ts","affected/file2.ts"]}'
```

## 捕获学习

如果你在此会话中发现了非显而易见的模式、陷阱或架构洞察，记录它供未来会话使用：

```bash
~/.claude/skills/gstack/bin/gstack-learnings-log '{"skill":"investigate","type":"TYPE","key":"SHORT_KEY","insight":"DESCRIPTION","confidence":N,"source":"SOURCE","files":["path/to/relevant/file"]}'
```

**类型：** `pattern`（可重用方法）、`pitfall`（不该做什么）、`preference`（用户陈述）、`architecture`（结构性决定）、`tool`（库/框架洞察）、`operational`（项目环境/CLI/工作流知识）。

**来源：** `observed`（你在代码中发现）、`user-stated`（用户告诉你）、`inferred`（AI 推断）、`cross-model`（Claude 和 Codex 都同意）。

**置信度：** 1-10。诚实。你在代码中验证的观察模式是 8-9。你不确定的推断是 4-5。用户明确陈述的偏好是 10。

**files：** 包含此学习引用的特定文件路径。这启用了过时检测：如果这些文件后来被删除，学习可以被标记。

**只记录真正的发现。** 不要记录显而易见的事情。不要记录用户已经知道的事情。一个好的测试：这个洞察会在未来的会话中节省时间吗？如果是，记录它。



---

## 重要规则

- **3+ 次失败修复尝试 → 停止并质疑架构。** 错误的架构，不是失败的假设。
- **永远不要应用你无法验证的修复。** 如果你无法重现和确认，不要发布它。
- **永远不要说"这应该能修复它。"** 验证并证明它。运行测试。
- **如果修复触及 >5 个文件 → AskUserQuestion** 询问影响范围后再继续。
- **完成状态：**
  - DONE — 找到根本原因，应用修复，编写回归测试，所有测试通过
  - DONE_WITH_CONCERNS — 已修复但无法完全验证（例如间歇性 bug，需要预发布环境）
  - BLOCKED — 调查后根本原因不明确，已升级
