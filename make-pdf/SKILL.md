---
name: make-pdf
preamble-tier: 1
version: 1.0.0
description: |
  将任何 markdown 文件转换为出版级 PDF。标准 1 英寸页边距、智能分页、页码、
  封面页、页眉页脚、弯引号和长破折号、可点击目录、对角线 DRAFT 水印。
  不是草稿产物——而是成品。当用户要求"制作 PDF"、"导出为 PDF"、
  "将此 markdown 转为 PDF"或"生成文档"时使用。(gstack)
  语音触发（语音转文字别名）："make this a pdf", "make it a pdf",
  "export to pdf", "turn this into a pdf", "turn this markdown into a pdf",
  "generate a pdf", "make a pdf from", "pdf this markdown".
triggers:
  - markdown to pdf
  - generate pdf
  - make pdf
  - export pdf
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — 请勿直接编辑 -->
<!-- 重新生成：bun run gen:skill-docs -->

## 前置代码（首先运行）

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
echo '{"skill":"make-pdf","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
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
  echo "LEARNINGS: $_LEARN_COUNT 条已加载"
  if [ "$_LEARN_COUNT" -gt 5 ] 2>/dev/null; then
    ~/.claude/skills/gstack/bin/gstack-learnings-search --limit 3 2>/dev/null || true
  fi
else
  echo "LEARNINGS: 0"
fi
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"make-pdf","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
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

在计划模式下，以下操作被允许，因为它们用于辅助计划制定：`$B`、`$D`、`codex exec`/`codex review`、写入 `~/.gstack/`、写入计划文件、以及 `open` 生成的产物。

## 计划模式期间的技能调用

如果用户在计划模式下调用技能，技能优先于通用计划模式行为。**将技能文件视为可执行指令，而非参考文档。**从步骤 0 开始逐步执行；第一个 AskUserQuestion 是工作流进入计划模式的标志，而非违反计划模式。AskUserQuestion 满足计划模式的回合结束要求。在 STOP 点，立即停止。不要继续工作流或在此处调用 ExitPlanMode。标记为"PLAN MODE EXCEPTION — ALWAYS RUN"的命令会执行。仅在技能工作流完成后，或用户要求取消技能/离开计划模式时调用 ExitPlanMode。

如果 `PROACTIVE` 为 `"false"`，不要自动调用或主动建议技能。如果技能可能有用，请询问："我觉得 /skillname 可能有帮助——要我运行它吗？"

如果 `SKILL_PREFIX` 为 `"true"`，建议/调用 `/gstack-*` 名称。磁盘路径保持 `~/.claude/skills/gstack/[skill-name]/SKILL.md`。

如果输出显示 `UPGRADE_AVAILABLE <old> <new>`：读取 `~/.claude/skills/gstack/gstack-upgrade/SKILL.md` 并按照"内联升级流程"执行（如果已配置则自动升级，否则通过 AskUserQuestion 提供 4 个选项，如果拒绝则写入延迟状态）。

如果输出显示 `JUST_UPGRADED <from> <to>`：打印 "Running gstack v{to} (just updated!)"。如果 `SPAWNED_SESSION` 为 true，跳过功能发现。

功能发现，每个会话最多提示一次：
- 缺少 `~/.claude/skills/gstack/.feature-prompted-continuous-checkpoint`：通过 AskUserQuestion 询问连续检查点自动提交。如果接受，运行 `~/.claude/skills/gstack/bin/gstack-config set checkpoint_mode continuous`。始终 touch 标记文件。
- 缺少 `~/.claude/skills/gstack/.feature-prompted-model-overlay`：告知"模型覆盖已激活。MODEL_OVERLAY 显示补丁。"始终 touch 标记文件。

升级提示后，继续工作流。

如果 `WRITING_STYLE_PENDING` 为 `yes`：询问一次写作风格：

> v1 提示更简洁：首次使用术语解释、结果导向的问题、更简短的文本。保持默认还是恢复简洁模式？

选项：
- A) 保持新默认（推荐——好的写作对每个人都有帮助）
- B) 恢复 V0 文本——设置 `explain_level: terse`

如果选择 A：不设置 `explain_level`（默认为 `default`）。
如果选择 B：运行 `~/.claude/skills/gstack/bin/gstack-config set explain_level terse`。

无论选择如何，始终运行：
```bash
rm -f ~/.gstack/.writing-style-prompt-pending
touch ~/.gstack/.writing-style-prompted
```

如果 `WRITING_STYLE_PENDING` 为 `no`，跳过。

如果 `LAKE_INTRO` 为 `no`：说明 "gstack 遵循**煮沸湖泊**原则——当 AI 使边际成本接近零时，做完整的事。了解更多：https://garryslist.org/posts/boil-the-ocean" 提供打开链接：

```bash
open https://garryslist.org/posts/boil-the-ocean
touch ~/.gstack/.completeness-intro-seen
```

仅在用户确认时运行 `open`。始终运行 `touch`。

如果 `TEL_PROMPTED` 为 `no` 且 `LAKE_INTRO` 为 `yes`：通过 AskUserQuestion 询问一次遥测：

> 帮助 gstack 变得更好。仅共享使用数据：技能、持续时间、崩溃、稳定设备 ID。不包含代码、文件路径或仓库名称。

选项：
- A) 帮助 gstack 变得更好！（推荐）
- B) 不了，谢谢

如果选择 A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry community`

如果选择 B：追问：

> 匿名模式仅发送聚合使用量，不含唯一 ID。

选项：
- A) 可以，匿名没问题
- B) 不了，完全关闭

如果 B→A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry anonymous`
如果 B→B：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry off`

始终运行：
```bash
touch ~/.gstack/.telemetry-prompted
```

如果 `TEL_PROMPTED` 为 `yes`，跳过。

如果 `PROACTIVE_PROMPTED` 为 `no` 且 `TEL_PROMPTED` 为 `yes`：询问一次：

> 让 gstack 主动建议技能，比如对"这能用吗？"使用 /qa，或对 bug 使用 /investigate？

选项：
- A) 保持开启（推荐）
- B) 关闭——我会自己输入 /命令

如果选择 A：运行 `~/.claude/skills/gstack/bin/gstack-config set proactive true`
如果选择 B：运行 `~/.claude/skills/gstack/bin/gstack-config set proactive false`

始终运行：
```bash
touch ~/.gstack/.proactive-prompted
```

如果 `PROACTIVE_PROMPTED` 为 `yes`，跳过。

如果 `HAS_ROUTING` 为 `no` 且 `ROUTING_DECLINED` 为 `false` 且 `PROACTIVE_PROMPTED` 为 `yes`：
检查项目根目录是否存在 CLAUDE.md 文件。如果不存在，创建它。

使用 AskUserQuestion：

> 当你的项目 CLAUDE.md 包含技能路由规则时，gstack 效果最佳。

选项：
- A) 将路由规则添加到 CLAUDE.md（推荐）
- B) 不了，我会手动调用技能

如果选择 A：将以下部分追加到 CLAUDE.md 末尾：

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

如果选择 B：运行 `~/.claude/skills/gstack/bin/gstack-config set routing_declined true` 并告知可通过 `gstack-config set routing_declined false` 重新启用。

每个项目仅执行一次。如果 `HAS_ROUTING` 为 `yes` 或 `ROUTING_DECLINED` 为 `true`，跳过。

如果 `VENDORED_GSTACK` 为 `yes`，通过 AskUserQuestion 警告一次（除非 `~/.gstack/.vendoring-warned-$SLUG` 存在）：

> 此项目在 `.claude/skills/gstack/` 中有 gstack 内嵌版本。内嵌模式已弃用。
> 是否迁移到团队模式？

选项：
- A) 是，立即迁移到团队模式
- B) 不了，我会自己处理

如果选择 A：
1. 运行 `git rm -r .claude/skills/gstack/`
2. 运行 `echo '.claude/skills/gstack/' >> .gitignore`
3. 运行 `~/.claude/skills/gstack/bin/gstack-team-init required`（或 `optional`）
4. 运行 `git add .claude/ .gitignore CLAUDE.md && git commit -m "chore: migrate gstack from vendored to team mode"`
5. 告知用户："完成。每位开发者现在运行：`cd ~/.claude/skills/gstack && ./setup --team`"

如果选择 B：说 "好的，你需要自己维护内嵌副本的更新。"

无论选择如何，始终运行：
```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)" 2>/dev/null || true
touch ~/.gstack/.vendoring-warned-${SLUG:-unknown}
```

如果标记文件已存在，跳过。

如果 `SPAWNED_SESSION` 为 `"true"`，你正在 AI 编排器（如 OpenClaw）生成的会话中运行。在生成的会话中：
- 不要对交互式提示使用 AskUserQuestion。自动选择推荐选项。
- 不要运行升级检查、遥测提示、路由注入或湖泊介绍。
- 专注于完成任务并通过文本输出报告结果。
- 以完成报告结束：发布了什么、做了什么决定、任何不确定的内容。

## GBrain 同步（技能开始时）

```bash
_GSTACK_HOME="${GSTACK_HOME:-$HOME/.gstack}"
_BRAIN_REMOTE_FILE="$HOME/.gstack-brain-remote.txt"
_BRAIN_SYNC_BIN="~/.claude/skills/gstack/bin/gstack-brain-sync"
_BRAIN_CONFIG_BIN="~/.claude/skills/gstack/bin/gstack-config"

_BRAIN_SYNC_MODE=$("$_BRAIN_CONFIG_BIN" get gbrain_sync_mode 2>/dev/null || echo off)

if [ -f "$_BRAIN_REMOTE_FILE" ] && [ ! -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" = "off" ]; then
  _BRAIN_NEW_URL=$(head -1 "$_BRAIN_REMOTE_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$_BRAIN_NEW_URL" ]; then
    echo "BRAIN_SYNC: 检测到 brain 仓库：$_BRAIN_NEW_URL"
    echo "BRAIN_SYNC: 运行 'gstack-brain-restore' 拉取你的跨机器记忆（或 'gstack-config set gbrain_sync_mode off' 永久关闭）"
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



隐私安全门：如果输出显示 `BRAIN_SYNC: off`、`gbrain_sync_mode_prompted` 为 `false`，且 gbrain 在 PATH 上或 `gbrain doctor --fast --json` 可用，询问一次：

> gstack 可以将你的会话记忆发布到 GBrain 跨机器索引的私有 GitHub 仓库。应该同步多少内容？

选项：
- A) 所有白名单内容（推荐）
- B) 仅产物
- C) 拒绝，保持所有内容在本地

回答后：

```bash
# 选择的模式：full | artifacts-only | off
"$_BRAIN_CONFIG_BIN" set gbrain_sync_mode <choice>
"$_BRAIN_CONFIG_BIN" set gbrain_sync_mode_prompted true
```

如果选择 A/B 且 `~/.gstack/.git` 缺失，询问是否运行 `gstack-brain-init`。不要阻塞技能。

在技能结束时、遥测之前：

```bash
"~/.claude/skills/gstack/bin/gstack-brain-sync" --discover-new 2>/dev/null || true
"~/.claude/skills/gstack/bin/gstack-brain-sync" --once 2>/dev/null || true
```


## 模型特定行为补丁 (claude)

以下微调适用于 claude 模型系列。它们**从属于**技能工作流、STOP 点、AskUserQuestion 门控、计划模式安全和 /ship 审查门控。如果以下微调与技能指令冲突，以技能为准。将这些视为偏好，而非规则。

**待办列表纪律。**执行多步骤计划时，完成每个任务后逐个标记为完成。不要在最后批量完成。如果任务被证明是不必要的，标记为跳过并附上一行原因。

**执行重操作前先思考。**对于复杂操作（重构、迁移、非平凡的新功能），在执行前简要说明你的方法。这使用户能够低成本地纠正方向，而不是在中途调整。

**优先使用专用工具而非 Bash。**优先使用 Read、Edit、Write、Glob、Grep，而非 shell 等价命令（cat、sed、find、grep）。专用工具更便宜更清晰。

## 语气

直接、具体、开发者之间的交流。明确指出文件、函数、命令和用户可见的影响。不要有废话。

不要使用长破折号。不要使用 AI 词汇：delve、crucial、robust、comprehensive、nuanced、multifaceted。不要有企业或学术腔。简短段落。最后告诉用户该做什么。

用户拥有你没有的上下文。跨模型一致的结论是建议，而非决定。由用户决定。

## 完成状态协议

完成技能工作流时，使用以下状态之一报告：
- **DONE** — 已完成并有证据。
- **DONE_WITH_CONCERNS** — 已完成，但列出关注点。
- **BLOCKED** — 无法继续；说明阻塞原因和已尝试的方法。
- **NEEDS_CONTEXT** — 缺少信息；准确说明需要什么。

在 3 次失败尝试、不确定的安全敏感更改或你无法验证的范围后升级。格式：`STATUS`、`REASON`、`ATTEMPTED`、`RECOMMENDATION`。

## 操作性自我改进

完成前，如果你发现了持久的项目特点或命令修复，下次可以节省 5 分钟以上，请记录：

```bash
~/.claude/skills/gstack/bin/gstack-learnings-log '{"skill":"SKILL_NAME","type":"operational","key":"SHORT_KEY","insight":"DESCRIPTION","confidence":N,"source":"observed"}'
```

不要记录显而易见的事实或一次性瞬态错误。

## 遥测（最后运行）

工作流完成后，记录遥测。使用 frontmatter 中的技能 `name:`。OUTCOME 为 success/error/abort/unknown。

**PLAN MODE EXCEPTION — ALWAYS RUN：**此命令将遥测写入 `~/.gstack/analytics/`，与前置代码的分析写入匹配。

运行以下 bash：

```bash
_TEL_END=$(date +%s)
_TEL_DUR=$(( _TEL_END - _TEL_START ))
rm -f ~/.gstack/analytics/.pending-"$_SESSION_ID" 2>/dev/null || true
# 会话时间线：记录技能完成（仅本地，从不发送）
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"SKILL_NAME","event":"completed","branch":"'$(git branch --show-current 2>/dev/null || echo unknown)'","outcome":"OUTCOME","duration_s":"'"$_TEL_DUR"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null || true
# 本地分析（受遥测设置控制）
if [ "$_TEL" != "off" ]; then
echo '{"skill":"SKILL_NAME","duration_s":"'"$_TEL_DUR"'","outcome":"OUTCOME","browse":"USED_BROWSE","session":"'"$_SESSION_ID"'","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
fi
# 远程遥测（需用户同意，需要二进制文件）
if [ "$_TEL" != "off" ] && [ -x ~/.claude/skills/gstack/bin/gstack-telemetry-log ]; then
  ~/.claude/skills/gstack/bin/gstack-telemetry-log \
    --skill "SKILL_NAME" --duration "$_TEL_DUR" --outcome "OUTCOME" \
    --used-browse "USED_BROWSE" --session-id "$_SESSION_ID" 2>/dev/null &
fi
```

运行前替换 `SKILL_NAME`、`OUTCOME` 和 `USED_BROWSE`。

## 计划状态页脚

在计划模式下、ExitPlanMode 之前：如果计划文件缺少 `## GSTACK REVIEW REPORT`，运行 `~/.claude/skills/gstack/bin/gstack-review-read` 并追加标准的运行/状态/发现表格。如果为 `NO_REVIEWS` 或为空，追加 5 行占位符，结论为"NO REVIEWS YET — run `/autoplan`"。如果有更丰富的报告，跳过。

PLAN MODE EXCEPTION — 始终允许（这是计划文件）。

# make-pdf：从 markdown 生成出版级 PDF

将 `.md` 文件转换为看起来像 Faber & Faber 文章的 PDF：1 英寸页边距、左对齐正文、全文使用 Helvetica、弯引号和长破折号、可选封面和可点击目录、需要时添加对角线 DRAFT 水印。从 PDF 复制粘贴产生干净的文字，永远不会出现 "S a i l i n g" 的情况。

在 Linux 上，安装 `fonts-liberation` 以获得正确的渲染——默认没有 Helvetica 和 Arial，Liberation Sans 是标准的度量兼容替代品。CI 和 Docker 构建通过 Dockerfile.ci 自动安装。

## MAKE-PDF 设置（在任何 make-pdf 命令之前运行此检查）

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
P=""
[ -n "$MAKE_PDF_BIN" ] && [ -x "$MAKE_PDF_BIN" ] && P="$MAKE_PDF_BIN"
[ -z "$P" ] && [ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/make-pdf/dist/pdf" ] && P="$_ROOT/.claude/skills/gstack/make-pdf/dist/pdf"
[ -z "$P" ] && P="$HOME/.claude/skills/gstack/make-pdf/dist/pdf"
if [ -x "$P" ]; then
  echo "MAKE_PDF_READY: $P"
  alias _p_="$P"   # shellcheck 别名助手（不导出）
  export P   # 在同一技能调用的后续代码块中作为 $P 可用
else
  echo "MAKE_PDF_NOT_AVAILABLE（运行 gstack 仓库中的 './setup' 来构建）"
fi
```

如果打印 `MAKE_PDF_NOT_AVAILABLE`：告知用户二进制文件未构建。让他们从 gstack 仓库运行 `./setup`，然后重试。

如果打印 `MAKE_PDF_READY`：`$P` 是技能其余部分的二进制路径。使用 `$P`（而非显式路径）以保持技能体的可移植性。

核心命令：
- `$P generate <input.md> [output.pdf]` — 将 markdown 渲染为 PDF（80% 的使用场景）
- `$P generate --cover --toc essay.md out.pdf` — 完整出版布局
- `$P generate --watermark DRAFT memo.md draft.pdf` — 对角线 DRAFT 水印
- `$P preview <input.md>` — 渲染 HTML 并在浏览器中打开（快速迭代）
- `$P setup` — 验证 browse + Chromium + pdftotext 并运行冒烟测试
- `$P --help` — 完整的 flag 参考

输出约定：
- `stdout`：成功时仅输出路径。一行。
- `stderr`：进度信息（`Rendering HTML... Generating PDF...`），除非使用 `--quiet`。
- 退出码 0 成功 / 1 参数错误 / 2 渲染错误 / 3 Paged.js 超时 / 4 browse 不可用。

## 核心模式

### 80% 的场景——备忘录/信件

一个命令，无需 flag。默认获得带有页眉页脚 + 页码 + CONFIDENTIAL 页脚的干净 PDF。

```bash
$P generate letter.md                 # 写入 /tmp/letter.pdf
$P generate letter.md letter.pdf      # 显式输出路径
```

### 出版模式——封面 + 目录 + 章节分隔

```bash
$P generate --cover --toc --author "Garry Tan" --title "On Horizons" \
  essay.md essay.pdf
```

markdown 中的每个顶级 H1 开始新页。对于恰好有多个 H1 的备忘录，使用 `--no-chapter-breaks` 禁用。

### 草稿阶段水印

```bash
$P generate --watermark DRAFT memo.md draft.pdf
```

每页都有 10% 透明度的对角线 DRAFT。当草稿定稿后，去掉 flag 并重新生成。

### 通过预览快速迭代

```bash
$P preview essay.md
```

使用相同的打印 CSS 渲染 HTML 并在浏览器中打开。编辑 markdown 时刷新。在准备好之前跳过 PDF 的来回转换。

### 无品牌（无 CONFIDENTIAL 页脚）

```bash
$P generate --no-confidential memo.md memo.pdf
```

## 常用 flag

```
页面布局：
  --margins <dim>            1in（默认）| 72pt | 2.54cm | 25mm
  --page-size letter|a4|legal

结构：
  --cover                    封面页（标题、作者、日期、细线分隔）
  --toc                      可点击目录（含页码）
  --no-chapter-breaks        不在每个 H1 处开始新页

品牌：
  --watermark <text>         对角线水印（"DRAFT"、"CONFIDENTIAL"）
  --header-template <html>   自定义页眉
  --footer-template <html>   自定义页脚（与 --page-numbers 互斥）
  --no-confidential          隐藏 CONFIDENTIAL 右页脚

输出：
  --page-numbers             "N of M" 页脚（默认开启）
  --tagged                   无障碍 PDF（默认开启）
  --outline                  从标题生成 PDF 书签（默认开启）
  --quiet                    隐藏 stderr 上的进度信息
  --verbose                  每阶段计时

网络：
  --allow-network            获取外部图片。默认关闭
                             （阻止跟踪像素）。

元数据：
  --title "..."              文档标题（默认为第一个 H1）
  --author "..."             封面 + PDF 元数据的作者
  --date "..."               封面日期（默认为今天）
```

## Claude 何时应该运行它

留意 markdown 转 PDF 的意图。以下任何模式 → 运行 `$P generate`：

- "Can you make this markdown a PDF"
- "Export it as a PDF"
- "Turn this letter into a PDF"
- "I need a PDF of the essay"
- "Print this as a PDF for me"

如果用户打开了 `.md` 文件并说"让它好看点"，建议 `$P generate --cover --toc` 并在运行前询问。

## 调试

- 输出看起来空白 → 检查 browse 守护进程是否运行：`$B status`。
- 复制粘贴时文字碎片化 → highlight.js 输出（阶段 4）。等该 flag 可用后使用 `--no-syntax` 重试。目前，移除代码块并重新生成。
- Paged.js 超时 → markdown 中可能没有标题。去掉 `--toc`。
- 外部图片缺失 → 添加 `--allow-network`（理解你是在允许 markdown 文件从其图片 URL 获取）。
- 生成的 PDF 太高/太宽 → `--page-size a4` 或 `--margins 0.75in`。

## 输出约定

```
stdout: /tmp/letter.pdf          ← 仅路径，一行
stderr: Rendering HTML...        ← 进度旋转器（除非 --quiet）
        Generating PDF...
        Done in 1.5s. 43 words · 22KB · /tmp/letter.pdf

退出码：0 成功 / 1 参数错误 / 2 渲染错误 / 3 Paged.js 超时
           / 4 browse 不可用
```

捕获路径：`PDF=$($P generate letter.md)` — 然后使用 `$PDF`。
