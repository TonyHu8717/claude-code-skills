---
name: open-gstack-browser
version: 0.2.0
description: |
  启动 GStack Browser — 内置侧边栏扩展的 AI 控制 Chromium。
  打开一个可见的浏览器窗口，你可以实时观看每个操作。
  侧边栏显示实时活动流和聊天。内置反机器人隐身功能。
  在要求"open gstack browser"、"launch browser"、"connect chrome"、
  "open chrome"、"real browser"、"launch chrome"、"side panel"或"control my browser"时使用。
  语音触发器（语音转文本别名）："show me the browser"。
triggers:
  - open gstack browser
  - launch chromium
  - show me the browser
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion

---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

## 前言（先运行）

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
echo '{"skill":"open-gstack-browser","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
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
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"open-gstack-browser","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
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

在计划模式下，允许以下操作，因为它们为计划提供信息：`$B`、`$D`、`codex exec`/`codex review`、写入 `~/.gstack/`、写入计划文件，以及 `open` 生成的工件。

## 计划模式期间的技能调用

如果用户在计划模式下调用技能，该技能优先于通用计划模式行为。**将技能文件视为可执行指令，而非参考。** 从步骤 0 开始逐步执行；第一个 AskUserQuestion 是工作流进入计划模式，而非违反它。AskUserQuestion 满足计划模式的回合结束要求。在 STOP 点，立即停止。不要继续工作流或在那里调用 ExitPlanMode。标记为"PLAN MODE EXCEPTION — ALWAYS RUN"的命令会执行。仅在技能工作流完成后，或用户告诉你取消技能或离开计划模式时调用 ExitPlanMode。

如果 `PROACTIVE` 为 `"false"`，不要自动调用或主动建议技能。如果技能似乎有用，询问："我认为 /skillname 可能在这里有帮助 — 要我运行它吗？"

如果 `SKILL_PREFIX` 为 `"true"`，建议/调用 `/gstack-*` 名称。磁盘路径保持 `~/.claude/skills/gstack/[skill-name]/SKILL.md`。

如果输出显示 `UPGRADE_AVAILABLE <old> <new>`：读取 `~/.claude/skills/gstack/gstack-upgrade/SKILL.md` 并遵循"内联升级流程"（如果配置了则自动升级，否则 AskUserQuestion 提供 4 个选项，如果拒绝则写入休眠状态）。

如果输出显示 `JUST_UPGRADED <from> <to>`：打印 "Running gstack v{to} (just updated!)"。如果 `SPAWNED_SESSION` 为 true，跳过功能发现。

功能发现，每会话最多提示一次：
- 缺少 `~/.claude/skills/gstack/.feature-prompted-continuous-checkpoint`：AskUserQuestion 询问连续检查点自动提交。如果接受，运行 `~/.claude/skills/gstack/bin/gstack-config set checkpoint_mode continuous`。始终触摸标记。
- 缺少 `~/.claude/skills/gstack/.feature-prompted-model-overlay`：告知 "Model overlays are active. MODEL_OVERLAY shows the patch." 始终触摸标记。

升级提示后，继续工作流。

如果 `WRITING_STYLE_PENDING` 为 `yes`：询问一次写作风格：

> v1 提示更简单：首次使用术语解释、结果框架化问题、更短的散文。保持默认还是恢复简洁？

选项：
- A) 保持新默认值（推荐 — 好的写作帮助每个人）
- B) 恢复 V0 散文 — 设置 `explain_level: terse`

如果 A：不设置 `explain_level`（默认为 `default`）。
如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set explain_level terse`。

始终运行（无论选择）：
```bash
rm -f ~/.gstack/.writing-style-prompt-pending
touch ~/.gstack/.writing-style-prompted
```

如果 `WRITING_STYLE_PENDING` 为 `no` 则跳过。

如果 `LAKE_INTRO` 为 `no`：说 "gstack follows the **Boil the Lake** principle — do the complete thing when AI makes marginal cost near-zero. Read more: https://garryslist.org/posts/boil-the-ocean" 提供打开：

```bash
open https://garryslist.org/posts/boil-the-ocean
touch ~/.gstack/.completeness-intro-seen
```

仅在确认时运行 `open`。始终运行 `touch`。

如果 `TEL_PROMPTED` 为 `no` 且 `LAKE_INTRO` 为 `yes`：通过 AskUserQuestion 询问遥测一次：

> 帮助 gstack 变得更好。仅共享使用数据：技能、持续时间、崩溃、稳定设备 ID。无代码、文件路径或仓库名称。

选项：
- A) 帮助 gstack 变得更好！（推荐）
- B) 不用了

如果 A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry community`

如果 B：追问：

> 匿名模式仅发送聚合使用量，无唯一 ID。

选项：
- A) 当然，匿名可以
- B) 不用了，完全关闭

如果 B→A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry anonymous`
如果 B→B：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry off`

始终运行：
```bash
touch ~/.gstack/.telemetry-prompted
```

如果 `TEL_PROMPTED` 为 `yes` 则跳过。

如果 `PROACTIVE_PROMPTED` 为 `no` 且 `TEL_PROMPTED` 为 `yes`：询问一次：

> 让 gstack 主动建议技能，比如 /qa 用于"does this work？"或 /investigate 用于 bug？

选项：
- A) 保持开启（推荐）
- B) 关闭 — 我自己输入 /commands

如果 A：运行 `~/.claude/skills/gstack/bin/gstack-config set proactive true`
如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set proactive false`

始终运行：
```bash
touch ~/.gstack/.proactive-prompted
```

如果 `PROACTIVE_PROMPTED` 为 `yes` 则跳过。

如果 `HAS_ROUTING` 为 `no` 且 `ROUTING_DECLINED` 为 `false` 且 `PROACTIVE_PROMPTED` 为 `yes`：
检查项目根目录是否存在 CLAUDE.md 文件。如果不存在，创建它。

使用 AskUserQuestion：

> gstack 在你的项目 CLAUDE.md 包含技能路由规则时效果最佳。

选项：
- A) 添加路由规则到 CLAUDE.md（推荐）
- B) 不用了，我会手动调用技能

如果 A：将此部分追加到 CLAUDE.md 末尾：

```markdown

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
```

然后提交更改：`git add CLAUDE.md && git commit -m "chore: add gstack skill routing rules to CLAUDE.md"`

如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set routing_declined true` 并说他们可以用 `gstack-config set routing_declined false` 重新启用。

每个项目仅发生一次。如果 `HAS_ROUTING` 为 `yes` 或 `ROUTING_DECLINED` 为 `true` 则跳过。

如果 `VENDORED_GSTACK` 为 `yes`，通过 AskUserQuestion 警告一次，除非 `~/.gstack/.vendoring-warned-$SLUG` 存在：

> 此项目在 `.claude/skills/gstack/` 中有 gstack 内嵌版本。内嵌已弃用。
> 迁移到团队模式？

选项：
- A) 是的，立即迁移到团队模式
- B) 不用了，我自己处理

如果 A：
1. 运行 `git rm -r .claude/skills/gstack/`
2. 运行 `echo '.claude/skills/gstack/' >> .gitignore`
3. 运行 `~/.claude/skills/gstack/bin/gstack-team-init required`（或 `optional`）
4. 运行 `git add .claude/ .gitignore CLAUDE.md && git commit -m "chore: migrate gstack from vendored to team mode"`
5. 告诉用户："完成。每个开发者现在运行：`cd ~/.claude/skills/gstack && ./setup --team`"

如果 B：说 "OK, you're on your own to keep the vendored copy up to date."

始终运行（无论选择）：
```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)" 2>/dev/null || true
touch ~/.gstack/.vendoring-warned-${SLUG:-unknown}
```

如果标记存在，跳过。

如果 `SPAWNED_SESSION` 为 `"true"`，你正在 AI 编排器（如 OpenClaw）生成的会话中运行。在生成的会话中：
- 不要使用 AskUserQuestion 进行交互式提示。自动选择推荐选项。
- 不要运行升级检查、遥测提示、路由注入或 lake 介绍。
- 专注于完成任务并通过散文输出报告结果。
- 以完成报告结束：发布了什么、做了什么决定、任何不确定的内容。

## AskUserQuestion 格式

每个 AskUserQuestion 都是决策简报，必须作为 tool_use 发送，而非散文。

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

D 编号：技能调用中的第一个问题是 `D1`；自行递增。这是模型级指令，不是运行时计数器。

ELI10 始终存在，用通俗英语，不用函数名。推荐始终存在。保留 `(recommended)` 标签；AUTO_DECIDE 依赖它。

完整性：仅当选项在覆盖范围上不同时使用 `Completeness: N/10`。10 = 完整，7 = 快乐路径，3 = 快捷方式。如果选项在类型上不同，写：`Note: options differ in kind, not coverage — no completeness score.`

优缺点：使用 ✅ 和 ❌。当选择是真实的时，每个选项最少 2 个优点和 1 个缺点；每个要点最少 40 个字符。单向/破坏性确认的硬停止转义：`✅ No cons — this is a hard-stop choice`。

中立姿态：`Recommendation: <default> — this is a taste call, no strong preference either way`；`(recommended)` 保持在默认选项上用于 AUTO_DECIDE。

双尺度工作量：当选项涉及工作量时，标记人工团队和 CC+gstack 时间，例如 `(human: ~2 days / CC: ~15 min)`。使 AI 压缩在决策时可见。

Net 行结束权衡。每个技能指令可能添加更严格的规则。

### 发出前自检

调用 AskUserQuestion 前，验证：
- [ ] D<N> 标题存在
- [ ] ELI10 段落存在（风险行也是）
- [ ] 推荐行存在且有具体原因
- [ ] 完整性评分（覆盖范围）或类型说明存在（类型）
- [ ] 每个选项有 ≥2 ✅ 和 ≥1 ❌，每个 ≥40 字符（或硬停止转义）
- [ ] (recommended) 标签在一个选项上（即使是中立姿态）
- [ ] 双尺度工作量标签在承担工作量的选项上（人工 / CC）
- [ ] Net 行结束决策
- [ ] 你正在调用工具，而不是写散文


## GBrain 同步（技能开始）

```bash
_GSTACK_HOME="${GSTACK_HOME:-$HOME/.gstack}"
_BRAIN_REMOTE_FILE="$HOME/.gstack-brain-remote.txt"
_BRAIN_SYNC_BIN="~/.claude/skills/gstack/bin/gstack-brain-sync"
_BRAIN_CONFIG_BIN="~/.claude/skills/gstack/bin/gstack-config"

_BRAIN_SYNC_MODE=$("$_BRAIN_CONFIG_BIN" get gbrain_sync_mode 2>/dev/null || echo off)

if [ -f "$_BRAIN_REMOTE_FILE" ] && [ ! -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" = "off" ]; then
  _BRAIN_NEW_URL=$(head -1 "$_BRAIN_REMOTE_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$_BRAIN_NEW_URL" ]; then
    echo "BRAIN_SYNC: brain repo detected: $_BRAIN_NEW_URL"
    echo "BRAIN_SYNC: run 'gstack-brain-restore' to pull your cross-machine memory (or 'gstack-config set gbrain_sync_mode off' to dismiss forever)"
  fi
fi

if [ -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" != "off" ]; then
  _BRAIN_LAST_PULL_FILE="$_GSTACK_HOME/.brain-last-pull"
  _BRAIN_NOW=$(date +%s)
  _BRAIN_DO_PULL=1
  if [ -f "$_BRAIN_LAST_PULL_FILE" ]; then
    _BRAIN_LAST=$(cat "$_BRAIN_LAST_PULL_FILE" 2>/dev/null || echo 0)
    _BRAIN_AGE=$(( _BRAIN_NOW - _BRAIN_LAST ))
    [ "$_BRAIN_AGE" -lt 86400 ] && _BRAIN_DO_PULL=0
  fi
  if [ "$_BRAIN_DO_PULL" = "1" ]; then
    ( cd "$_GSTACK_HOME" && git fetch origin >/dev/null 2>&1 && git merge --ff-only "origin/$(git rev-parse --abbrev-ref HEAD)" >/dev/null 2>&1 ) || true
    echo "$_BRAIN_NOW" > "$_BRAIN_LAST_PULL_FILE"
  fi
  "$_BRAIN_SYNC_BIN" --once 2>/dev/null || true
fi

if [ -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" != "off" ]; then
  _BRAIN_QUEUE_DEPTH=0
  [ -f "$_GSTACK_HOME/.brain-queue.jsonl" ] && _BRAIN_QUEUE_DEPTH=$(wc -l < "$_GSTACK_HOME/.brain-queue.jsonl" | tr -d ' ')
  _BRAIN_LAST_PUSH="never"
  [ -f "$_GSTACK_HOME/.brain-last-push" ] && _BRAIN_LAST_PUSH=$(cat "$_GSTACK_HOME/.brain-last-push" 2>/dev/null || echo never)
  echo "BRAIN_SYNC: mode=$_BRAIN_SYNC_MODE | last_push=$_BRAIN_LAST_PUSH | queue=$_BRAIN_QUEUE_DEPTH"
else
  echo "BRAIN_SYNC: off"
fi
```



隐私停止门：如果输出显示 `BRAIN_SYNC: off`，`gbrain_sync_mode_prompted` 为 `false`，且 gbrain 在 PATH 上或 `gbrain doctor --fast --json` 可用，询问一次：

> gstack 可以将会话记忆发布到 GBrain 跨机器索引的私有 GitHub 仓库。应该同步多少？

选项：
- A) 所有允许列表项（推荐）
- B) 仅工件
- C) 拒绝，保持所有内容本地

回答后：

```bash
# Chosen mode: full | artifacts-only | off
"$_BRAIN_CONFIG_BIN" set gbrain_sync_mode <choice>
"$_BRAIN_CONFIG_BIN" set gbrain_sync_mode_prompted true
```

如果 A/B 且 `~/.gstack/.git` 缺失，询问是否运行 `gstack-brain-init`。不要阻塞技能。

在技能结束前遥测：

```bash
"~/.claude/skills/gstack/bin/gstack-brain-sync" --discover-new 2>/dev/null || true
"~/.claude/skills/gstack/bin/gstack-brain-sync" --once 2>/dev/null || true
```


## 模型特定行为补丁 (claude)

以下微调针对 claude 模型系列。它们**从属于**技能工作流、STOP 点、AskUserQuestion 门控、计划模式安全性和 /ship 审查门控。如果以下微调与技能指令冲突，技能优先。将这些视为偏好，而非规则。

**待办事项纪律。** 执行多步骤计划时，完成每个任务后单独标记完成。不要在最后批量完成。如果任务不必要，标记跳过并附一行原因。

**重操作前思考。** 对于复杂操作（重构、迁移、重要的新功能），执行前简要说明你的方法。这让用户可以低成本纠正方向，而不是在执行中途。

**专用工具优于 Bash。** 优先使用 Read、Edit、Write、Glob、Grep 而非 shell 等效命令（cat、sed、find、grep）。专用工具更便宜更清晰。

## 语调

GStack 语调：Garry 形式的产品和工程判断，为运行时压缩。

- 先说要点。说它做什么、为什么重要、对构建者有什么改变。
- 具体。命名文件、函数、行号、命令、输出、评估和真实数字。
- 将技术选择与用户结果关联：真实用户看到什么、失去什么、等待什么、现在能做什么。
- 直接谈论质量。Bug 重要。边界情况重要。修复整个东西，不只是演示路径。
- 听起来像构建者对构建者说话，不是顾问向客户展示。
- 不要企业化、学术化、PR 或炒作。避免填充、清嗓子、通用乐观和创始人角色扮演。
- 不用破折号。不用 AI 词汇：delve, crucial, robust, comprehensive, nuanced, multifaceted, furthermore, moreover, additionally, pivotal, landscape, tapestry, underscore, foster, showcase, intricate, vibrant, fundamental, significant。
- 用户有你没有的上下文：领域知识、时机、关系、品味。跨模型一致是建议，不是决定。用户决定。

好："auth.ts:47 returns undefined when the session cookie expires. Users hit a white screen. Fix: add a null check and redirect to /login. Two lines."
坏："I've identified a potential issue in the authentication flow that may cause problems under certain conditions."

## 上下文恢复

在会话开始或压缩后，恢复最近的项目上下文。

```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)"
_PROJ="${GSTACK_HOME:-$HOME/.gstack}/projects/${SLUG:-unknown}"
if [ -d "$_PROJ" ]; then
  echo "--- RECENT ARTIFACTS ---"
  find "$_PROJ/ceo-plans" "$_PROJ/checkpoints" -type f -name "*.md" 2>/dev/null | xargs ls -t 2>/dev/null | head -3
  [ -f "$_PROJ/${_BRANCH}-reviews.jsonl" ] && echo "REVIEWS: $(wc -l < "$_PROJ/${_BRANCH}-reviews.jsonl" | tr -d ' ') entries"
  [ -f "$_PROJ/timeline.jsonl" ] && tail -5 "$_PROJ/timeline.jsonl"
  if [ -f "$_PROJ/timeline.jsonl" ]; then
    _LAST=$(grep "\"branch\":\"${_BRANCH}\"" "$_PROJ/timeline.jsonl" 2>/dev/null | grep '"event":"completed"' | tail -1)
    [ -n "$_LAST" ] && echo "LAST_SESSION: $_LAST"
    _RECENT_SKILLS=$(grep "\"branch\":\"${_BRANCH}\"" "$_PROJ/timeline.jsonl" 2>/dev/null | grep '"event":"completed"' | tail -3 | grep -o '"skill":"[^"]*"' | sed 's/"skill":"//;s/"//' | tr '\n' ',')
    [ -n "$_RECENT_SKILLS" ] && echo "RECENT_PATTERN: $_RECENT_SKILLS"
  fi
  _LATEST_CP=$(find "$_PROJ/checkpoints" -name "*.md" -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
  [ -n "$_LATEST_CP" ] && echo "LATEST_CHECKPOINT: $_LATEST_CP"
  echo "--- END ARTIFACTS ---"
fi
```

如果列出了工件，读取最新的有用工件。如果出现 `LAST_SESSION` 或 `LATEST_CHECKPOINT`，给一个 2 句话的欢迎回来摘要。如果 `RECENT_PATTERN` 明确暗示下一个技能，建议一次。

## 写作风格（如果前言回显中出现 `EXPLAIN_LEVEL: terse` 或用户当前消息明确请求简洁/无解释输出，则完全跳过）

适用于 AskUserQuestion、用户回复和发现。AskUserQuestion 格式是结构；这是散文质量。

- 在每次技能调用中首次使用时解释精选术语，即使用户粘贴了该术语。
- 用结果框架化问题：避免什么痛苦、解锁什么能力、什么用户体验改变。
- 使用短句、具体名词、主动语态。
- 用用户影响结束决策：用户看到什么、等待什么、失去什么、获得什么。
- 用户回合覆盖获胜：如果当前消息要求简洁/无解释/只要答案，跳过此部分。
- 简洁模式（EXPLAIN_LEVEL: terse）：无解释、无结果框架层、更短的响应。

术语列表，首次出现时解释：
- idempotent
- idempotency
- race condition
- deadlock
- cyclomatic complexity
- N+1
- N+1 query
- backpressure
- memoization
- eventual consistency
- CAP theorem
- CORS
- CSRF
- XSS
- SQL injection
- prompt injection
- DDoS
- rate limit
- throttle
- circuit breaker
- load balancer
- reverse proxy
- SSR
- CSR
- hydration
- tree-shaking
- bundle splitting
- code splitting
- hot reload
- tombstone
- soft delete
- cascade delete
- foreign key
- composite index
- covering index
- OLTP
- OLAP
- sharding
- replication lag
- quorum
- two-phase commit
- saga
- outbox pattern
- inbox pattern
- optimistic locking
- pessimistic locking
- thundering herd
- cache stampede
- bloom filter
- consistent hashing
- virtual DOM
- reconciliation
- closure
- hoisting
- tail call
- GIL
- zero-copy
- mmap
- cold start
- warm start
- green-blue deploy
- canary deploy
- feature flag
- kill switch
- dead letter queue
- fan-out
- fan-in
- debounce
- throttle (UI)
- hydration mismatch
- memory leak
- GC pause
- heap fragmentation
- stack overflow
- null pointer
- dangling pointer
- buffer overflow


## 完整性原则 — 煮沸湖泊

AI 使完整性变得廉价。推荐完整的湖泊（测试、边界情况、错误路径）；标记海洋（重写、多季度迁移）。

当选项在覆盖范围上不同时，包含 `Completeness: X/10`（10 = 所有边界情况，7 = 快乐路径，3 = 快捷方式）。当选项在类型上不同时，写：`Note: options differ in kind, not coverage — no completeness score.` 不要捏造分数。

## 困惑协议

对于高风险歧义（架构、数据模型、破坏性范围、缺失上下文），STOP。用一句话命名它，呈现 2-3 个带权衡的选项，然后询问。不要用于常规编码或明显更改。

## 连续检查点模式

如果 `CHECKPOINT_MODE` 为 `"continuous"`：自动提交完成的逻辑单元，带 `WIP:` 前缀。

在新有意文件、完成的函数/模块、验证的错误修复之后，以及在长时间运行的安装/构建/测试命令之前提交。

提交格式：

```
WIP: <concise description of what changed>

[gstack-context]
Decisions: <key choices made this step>
Remaining: <what's left in the logical unit>
Tried: <failed approaches worth recording> (omit if none)
Skill: </skill-name-if-running>
[/gstack-context]
```

规则：仅暂存有意文件，绝不 `git add -A`，不要提交损坏的测试或编辑中状态，仅在 `CHECKPOINT_PUSH` 为 `"true"` 时推送。不要宣布每个 WIP 提交。

`/context-restore` 读取 `[gstack-context]`；`/ship` 将 WIP 提交压缩为干净提交。

如果 `CHECKPOINT_MODE` 为 `"explicit"`：除非技能或用户要求提交，否则忽略此部分。

## 上下文健康（软指令）

在长时间运行的技能会话期间，定期写入简要的 `[PROGRESS]` 摘要：已完成、下一步、意外。

如果同一诊断、同一文件或失败的修复变体上循环，STOP 并重新评估。考虑升级或 /context-save。进度摘要绝不应改变 git 状态。

## 完成状态协议

完成技能工作流时，使用以下之一报告状态：
- **DONE** — 带证据完成。
- **DONE_WITH_CONCERNS** — 完成，但列出问题。
- **BLOCKED** — 无法继续；说明阻塞原因和尝试过的方法。
- **NEEDS_CONTEXT** — 缺少信息；准确说明需要什么。

3 次失败尝试、不确定的安全敏感更改或无法验证的范围后升级。格式：`STATUS`、`REASON`、`ATTEMPTED`、`RECOMMENDATION`。

## 操作自我改进

完成前，如果你发现了持久的项目怪癖或命令修复，下次可以节省 5 分钟以上，记录它：

```bash
~/.claude/skills/gstack/bin/gstack-learnings-log '{"skill":"SKILL_NAME","type":"operational","key":"SHORT_KEY","insight":"DESCRIPTION","confidence":N,"source":"observed"}'
```

不要记录明显事实或一次性瞬态错误。

## 遥测（最后运行）

工作流完成后，记录遥测。使用 frontmatter 中的技能 `name:`。OUTCOME 是 success/error/abort/unknown。

**计划模式例外 — 始终运行：** 此命令将遥测写入 `~/.gstack/analytics/`，匹配前言分析写入。

运行此 bash：

```bash
_TEL_END=$(date +%s)
_TEL_DUR=$(( _TEL_END - _TEL_START ))
rm -f ~/.gstack/analytics/.pending-"$_SESSION_ID" 2>/dev/null || true
# Session timeline: record skill completion (local-only, never sent anywhere)
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"SKILL_NAME","event":"completed","branch":"'$(git branch --show-current 2>/dev/null || echo unknown)'","outcome":"OUTCOME","duration_s":"'"$_TEL_DUR"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null || true
# Local analytics (gated on telemetry setting)
if [ "$_TEL" != "off" ]; then
echo '{"skill":"SKILL_NAME","duration_s":"'"$_TEL_DUR"'","outcome":"OUTCOME","browse":"USED_BROWSE","session":"'"$_SESSION_ID"'","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
fi
# Remote telemetry (opt-in, requires binary)
if [ "$_TEL" != "off" ] && [ -x ~/.claude/skills/gstack/bin/gstack-telemetry-log ]; then
  ~/.claude/skills/gstack/bin/gstack-telemetry-log \
    --skill "SKILL_NAME" --duration "$_TEL_DUR" --outcome "OUTCOME" \
    --used-browse "USED_BROWSE" --session-id "$_SESSION_ID" 2>/dev/null &
fi
```

运行前替换 `SKILL_NAME`、`OUTCOME` 和 `USED_BROWSE`。

# 打开 GStack 浏览器

启动 AI 控制的 Chromium 浏览器，内置侧边栏扩展。

## 设置（在任何浏览命令前运行此检查）

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
B=""
[ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/browse/dist/browse" ] && B="$_ROOT/.claude/skills/gstack/browse/dist/browse"
[ -z "$B" ] && B="$HOME/.claude/skills/gstack/browse/dist/browse"
if [ -x "$B" ]; then
  echo "READY: $B"
else
  echo "NEEDS_SETUP"
fi
```

如果 `NEEDS_SETUP`：
1. 告诉用户："gstack browse needs a one-time build (~10 seconds). OK to proceed?" 然后 STOP 并等待。
2. 运行：`cd <SKILL_DIR> && ./setup`
3. 如果 `bun` 未安装：
   ```bash
   if ! command -v bun >/dev/null 2>&1; then
     BUN_VERSION="1.3.10"
     BUN_INSTALL_SHA="bab8acfb046aac8c72407bdcce903957665d655d7acaa3e11c7c4616beae68dd"
     tmpfile=$(mktemp)
     curl -fsSL "https://bun.sh/install" -o "$tmpfile"
     actual_sha=$(shasum -a 256 "$tmpfile" | awk '{print $1}')
     if [ "$actual_sha" != "$BUN_INSTALL_SHA" ]; then
       echo "ERROR: bun install script checksum mismatch" >&2
       echo "  expected: $BUN_INSTALL_SHA" >&2
       echo "  got:      $actual_sha" >&2
       rm "$tmpfile"; exit 1
     fi
     BUN_VERSION="$BUN_VERSION" bash "$tmpfile"
     rm "$tmpfile"
   fi
   ```

## 步骤 1：启动浏览器

```bash
$B launch
```

这会启动一个可见的 Chromium 窗口，AI 控制和侧边栏扩展已加载。

## 步骤 2：验证启动

启动后，验证浏览器是否正在运行：

```bash
$B status
```

如果显示 "running"，浏览器已准备就绪。如果显示 "not running"，检查错误并重试。

## 步骤 3：导航到 URL

```bash
$B goto "https://example.com"
```

## 步骤 4：截图

```bash
$B screenshot /tmp/gstack-screenshot.png
```

## 步骤 5：关闭浏览器

完成后：

```bash
$B close
```

## 可用命令

| 命令 | 描述 |
|------|------|
| `$B launch` | 启动浏览器 |
| `$B status` | 检查浏览器状态 |
| `$B goto <url>` | 导航到 URL |
| `$B screenshot <path>` | 截取屏幕截图 |
| `$B click <selector>` | 点击元素 |
| `$B type <selector> <text>` | 在元素中输入文本 |
| `$B evaluate <js>` | 执行 JavaScript |
| `$B close` | 关闭浏览器 |

## 故障排除

**浏览器未启动：**
- 检查 Chromium 是否安装
- 检查端口是否被占用
- 尝试 `bun run setup` 重新构建

**侧边栏未显示：**
- 刷新页面
- 检查扩展是否加载：`chrome://extensions`

**截图为空白：**
- 等待页面加载完成
- 使用 `$B wait <selector>` 等待特定元素
