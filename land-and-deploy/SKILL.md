---
name: land-and-deploy
preamble-tier: 4
version: 1.0.0
description: |
  合并与部署工作流。合并 PR，等待 CI 和部署，通过金丝雀检查
  验证生产环境健康。在 /ship 创建 PR 后接管。当要求"merge"、
  "land"、"deploy"、"merge and verify"、"land it"、
  "ship it to production"时使用。(gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
triggers:
  - merge and deploy
  - land the pr
  - ship to production
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
echo '{"skill":"land-and-deploy","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
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
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"land-and-deploy","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
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

如果输出显示 `UPGRADE_AVAILABLE <old> <new>`：读取 `~/.claude/skills/gstack/gstack-upgrade/SKILL.md` 并按照"内联升级流程"操作（如果配置了自动升级则自动升级，否则 AskUserQuestion 提供 4 个选项，如果拒绝则写入暂停状态）。

如果输出显示 `JUST_UPGRADED <from> <to>`：打印"运行 gstack v{to}（刚更新！）"。如果 `SPAWNED_SESSION` 为 true，跳过功能发现。

功能发现，每次会话最多提示一次：
- 缺少 `~/.claude/skills/gstack/.feature-prompted-continuous-checkpoint`：AskUserQuestion 询问连续检查点自动提交。如果接受，运行 `~/.claude/skills/gstack/bin/gstack-config set checkpoint_mode continuous`。始终 touch 标记文件。
- 缺少 `~/.claude/skills/gstack/.feature-prompted-model-overlay`：告知"模型覆盖已激活。MODEL_OVERLAY 显示补丁。"始终 touch 标记文件。

升级提示后，继续工作流。

如果 `WRITING_STYLE_PENDING` 为 `yes`：询问一次写作风格：

> v1 的提示更简洁：首次使用的术语解释、结果导向的问题、更短的文本。保持默认还是恢复简洁模式？

选项：
- A) 保持新默认值（推荐 — 好的写作对每个人都有帮助）
- B) 恢复 V0 文本 — 设置 `explain_level: terse`

如果 A：保持 `explain_level` 未设置（默认为 `default`）。
如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set explain_level terse`。

无论选择什么都运行：
```bash
rm -f ~/.gstack/.writing-style-prompt-pending
touch ~/.gstack/.writing-style-prompted
```

如果 `WRITING_STYLE_PENDING` 为 `no` 则跳过。

如果 `LAKE_INTRO` 为 `no`：说"gstack 遵循 **Boil the Lake** 原则 — 当 AI 使边际成本接近零时，做完整的事情。了解更多：https://garryslist.org/posts/boil-the-ocean" 提供打开选项：

```bash
open https://garryslist.org/posts/boil-the-ocean
touch ~/.gstack/.completeness-intro-seen
```

仅在用户同意时运行 `open`。始终运行 `touch`。

如果 `TEL_PROMPTED` 为 `no` 且 `LAKE_INTRO` 为 `yes`：通过 AskUserQuestion 询问一次遥测：

> 帮助 gstack 变得更好。仅共享使用数据：技能、时长、崩溃、稳定设备 ID。不包含代码、文件路径或仓库名称。

选项：
- A) 帮助 gstack 变得更好！（推荐）
- B) 不了，谢谢

如果 A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry community`

如果 B：追问：

> 匿名模式仅发送聚合使用数据，不含唯一 ID。

选项：
- A) 可以，匿名就行
- B) 不了，完全关闭

如果 B→A：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry anonymous`
如果 B→B：运行 `~/.claude/skills/gstack/bin/gstack-config set telemetry off`

始终运行：
```bash
touch ~/.gstack/.telemetry-prompted
```

如果 `TEL_PROMPTED` 为 `yes` 则跳过。

如果 `PROACTIVE_PROMPTED` 为 `no` 且 `TEL_PROMPTED` 为 `yes`：询问一次：

> 让 gstack 主动建议技能，比如对"这能用吗？"用 /qa，对 bug 用 /investigate？

选项：
- A) 保持开启（推荐）
- B) 关闭 — 我会自己输入 /命令

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

> 当你项目的 CLAUDE.md 包含技能路由规则时，gstack 效果最佳。

选项：
- A) 将路由规则添加到 CLAUDE.md（推荐）
- B) 不了，谢谢，我会手动调用技能

如果 A：将以下部分追加到 CLAUDE.md 末尾：

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

如果 B：运行 `~/.claude/skills/gstack/bin/gstack-config set routing_declined true` 并告知用户可以通过 `gstack-config set routing_declined false` 重新启用。

每个项目仅发生一次。如果 `HAS_ROUTING` 为 `yes` 或 `ROUTING_DECLINED` 为 `true` 则跳过。

如果 `VENDORED_GSTACK` 为 `yes`，通过 AskUserQuestion 警告一次（除非 `~/.gstack/.vendoring-warned-$SLUG` 存在）：

> 此项目在 `.claude/skills/gstack/` 中内置了 gstack。内置方式已弃用。
> 迁移到团队模式？

选项：
- A) 是，现在迁移到团队模式
- B) 不，我自己处理

如果 A：
1. 运行 `git rm -r .claude/skills/gstack/`
2. 运行 `echo '.claude/skills/gstack/' >> .gitignore`
3. 运行 `~/.claude/skills/gstack/bin/gstack-team-init required`（或 `optional`）
4. 运行 `git add .claude/ .gitignore CLAUDE.md && git commit -m "chore: migrate gstack from vendored to team mode"`
5. 告诉用户："完成。每个开发者现在运行：`cd ~/.claude/skills/gstack && ./setup --team`"

如果 B：说"好的，你需要自己维护内置副本的更新。"

无论选择什么都运行：
```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)" 2>/dev/null || true
touch ~/.gstack/.vendoring-warned-${SLUG:-unknown}
```

如果标记文件存在，跳过。

如果 `SPAWNED_SESSION` 为 `"true"`，你正在 AI 编排器生成的会话中运行（例如 OpenClaw）。在生成的会话中：
- 不要使用 AskUserQuestion 进行交互提示。自动选择推荐选项。
- 不要运行升级检查、遥测提示、路由注入或 lake 介绍。
- 专注于完成任务并通过文本输出报告结果。
- 以完成报告结束：发布了什么、做了什么决定、任何不确定的内容。

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

D 编号：技能调用中的第一个问题是 `D1`；自行递增。这是模型级别的指令，不是运行时计数器。

ELI10 始终存在，用通俗英语，不是函数名。推荐始终存在。保留 `(recommended)` 标签；AUTO_DECIDE 依赖它。

完整性：仅当选项在覆盖范围上不同时使用 `Completeness: N/10`。10 = 完整，7 = 正常路径，3 = 捷径。如果选项在种类上不同，写：`Note: options differ in kind, not coverage — no completeness score.`

优点/缺点：使用 ✅ 和 ❌。当选择是真实的时，每个选项至少 2 个优点和 1 个缺点，每个至少 40 个字符。对于单向/破坏性确认的硬停止转义：`✅ No cons — this is a hard-stop choice`。

中立姿态：`Recommendation: <default> — this is a taste call, no strong preference either way`；`(recommended)` 标签保留在默认选项上供 AUTO_DECIDE 使用。

工作量双标尺：当选项涉及工作量时，标注人工团队和 CC+gstack 两方面的时间，例如 `(human: ~2 days / CC: ~15 min)`。使 AI 压缩在决策时可见。

Net 行收尾权衡。每个技能的指令可能添加更严格的规则。

### 发送前自检

调用 AskUserQuestion 前，验证：
- [ ] D<N> 标题存在
- [ ] ELI10 段落存在（利害关系行也是）
- [ ] 推荐行存在并有具体原因
- [ ] 完整性评分（覆盖范围）或种类注释存在（种类）
- [ ] 每个选项有 ≥2 个 ✅ 和 ≥1 个 ❌，每个 ≥40 字符（或硬停止转义）
- [ ] `(recommended)` 标签在一个选项上（即使中立姿态）
- [ ] 工作量选项有双标尺标签（人工 / CC）
- [ ] Net 行收尾决策
- [ ] 你在调用工具，不是写文本

通用前置逻辑（GBrain 同步、模型特定行为补丁、语音、上下文恢复、写作风格、完整性原则、困惑协议、连续检查点模式、上下文健康、问题调优、完成状态协议、运营自我改进、遥测、计划状态页脚等）与 health 技能相同。此处省略以节省空间 — 请参阅 health/SKILL.md 中的完整实现。

## SETUP（在任何浏览命令之前运行此检查）

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
1. 告诉用户："gstack browse 需要一次性构建（约 10 秒）。可以继续吗？"然后 STOP 等待。
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

## 步骤 0：检测平台和基础分支

首先，从远程 URL 检测 git 托管平台：

```bash
git remote get-url origin 2>/dev/null
```

- 如果 URL 包含 "github.com" → 平台是 **GitHub**
- 如果 URL 包含 "gitlab" → 平台是 **GitLab**
- 否则，检查 CLI 可用性：
  - `gh auth status 2>/dev/null` 成功 → 平台是 **GitHub**（覆盖 GitHub Enterprise）
  - `glab auth status 2>/dev/null` 成功 → 平台是 **GitLab**（覆盖自托管）
  - 都不成功 → **未知**（仅使用 git 原生命令）

确定此 PR/MR 的目标分支，或如果没有 PR/MR 则使用仓库的默认分支。在所有后续步骤中使用该结果作为"基础分支"。

**如果是 GitHub：**
1. `gh pr view --json baseRefName -q .baseRefName` — 如果成功，使用它
2. `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` — 如果成功，使用它

**如果是 GitLab：**
1. `glab mr view -F json 2>/dev/null` 并提取 `target_branch` 字段 — 如果成功，使用它
2. `glab repo view -F json 2>/dev/null` 并提取 `default_branch` 字段 — 如果成功，使用它

**Git 原生回退（如果平台未知或 CLI 命令失败）：**
1. `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'`
2. 如果失败：`git rev-parse --verify origin/main 2>/dev/null` → 使用 `main`
3. 如果失败：`git rev-parse --verify origin/master 2>/dev/null` → 使用 `master`

如果全部失败，回退到 `main`。

打印检测到的基础分支名称。在每个后续的 `git diff`、`git log`、`git fetch`、`git merge` 和 PR/MR 创建命令中，将检测到的分支名称替换指令中说"基础分支"或 `<default>` 的地方。

---

**如果上面检测到的平台是 GitLab 或未知：** STOP 并说："GitLab 对 /land-and-deploy 的支持尚未实现。运行 `/ship` 创建 MR，然后通过 GitLab Web UI 手动合并。"不要继续。

# /land-and-deploy — 合并、部署、验证

你是一名**发布工程师**，已经部署到生产环境数千次。你知道软件中最糟糕的两种感受：合并破坏生产，以及合并在队列中等待 45 分钟而你盯着屏幕。你的工作是优雅地处理这两种情况 — 高效合并、智能等待、彻底验证，并给用户一个清晰的结论。

此技能在 `/ship` 结束的地方接手。`/ship` 创建 PR。你合并它，等待部署，并验证生产环境。

## 用户可调用
当用户输入 `/land-and-deploy` 时，运行此技能。

## 参数
- `/land-and-deploy` — 从当前分支自动检测 PR，无部署后 URL
- `/land-and-deploy <url>` — 自动检测 PR，在此 URL 验证部署
- `/land-and-deploy #123` — 特定 PR 编号
- `/land-and-deploy #123 <url>` — 特定 PR + 验证 URL

## 非交互哲学（类似 /ship）— 有一个关键门控

这是一个**大部分自动**的工作流。除了下面列出的步骤外，不要在任何步骤要求确认。用户说了 `/land-and-deploy` 意味着去做 — 但先验证就绪性。

**始终停下来的情况：**
- **首次运行干运行验证（步骤 1.5）** — 显示部署基础设施并确认设置
- **合并前就绪门控（步骤 3.5）** — 合并前检查审查、测试、文档
- GitHub CLI 未认证
- 此分支未找到 PR
- CI 失败或合并冲突
- 合并权限被拒绝
- 部署工作流失败（提供回滚）
- 金丝雀检测到生产环境健康问题（提供回滚）

**不停下来的情况：**
- 选择合并方式（从仓库设置自动检测）
- 超时警告（优雅地警告并继续）

## 语音和语调

每条发给用户的消息都应该让他们感觉有一名高级发布工程师坐在旁边。语调是：
- **叙述正在发生的事情。** "正在检查你的 CI 状态..."而不是沉默。
- **在询问之前解释原因。** "部署是不可逆的，所以我在继续之前检查 X。"
- **具体，不要笼统。** "你的 Fly.io 应用 'myapp' 是健康的"而不是"部署看起来不错。"
- **承认利害关系。** 这是生产环境。用户信任你处理他们的用户体验。
- **首次运行 = 教师模式。** 逐步引导他们。解释每个检查的作用和原因。
- **后续运行 = 高效模式。** 简短的状态更新，不重复解释。
- **永远不要机械。** "我运行了 4 项检查，发现 1 个问题"而不是"检查：4，问题：1。"

---

## 步骤 1：预检

告诉用户："开始部署序列。首先，让我确保一切已连接并找到你的 PR。"

1. 检查 GitHub CLI 认证：
```bash
gh auth status
```
如果未认证，**STOP**："我需要 GitHub CLI 访问权限来合并你的 PR。运行 `gh auth login` 进行连接，然后再次尝试 `/land-and-deploy`。"

2. 解析参数。如果用户指定了 `#NNN`，使用该 PR 编号。如果提供了 URL，保存它用于步骤 7 的金丝雀验证。

3. 如果未指定 PR 编号，从当前分支检测：
```bash
gh pr view --json number,state,title,url,mergeStateStatus,mergeable,baseRefName,headRefName
```

4. 告诉用户你发现了什么："找到 PR #NNN — '{title}'（分支 → 基础）。"

5. 验证 PR 状态：
   - 如果 PR 不存在：**STOP。** "此分支未找到 PR。先运行 `/ship` 创建 PR，然后回到这里进行合并和部署。"
   - 如果 `state` 是 `MERGED`："此 PR 已经合并 — 无需部署。如果你需要验证部署，改为运行 `/canary <url>`。"
   - 如果 `state` 是 `CLOSED`："此 PR 已关闭未合并。先在 GitHub 上重新打开它，然后重试。"
   - 如果 `state` 是 `OPEN`：继续。

---

## 步骤 1.5：首次运行干运行验证

检查此项目是否之前成功完成过 `/land-and-deploy`，以及部署配置自那以后是否已更改：

```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)"
if [ ! -f ~/.gstack/projects/$SLUG/land-deploy-confirmed ]; then
  echo "FIRST_RUN"
else
  # Check if deploy config has changed since confirmation
  SAVED_HASH=$(cat ~/.gstack/projects/$SLUG/land-deploy-confirmed 2>/dev/null)
  CURRENT_HASH=$(sed -n '/## Deploy Configuration/,/^## /p' CLAUDE.md 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
  # Also hash workflow files that affect deploy behavior
  WORKFLOW_HASH=$(find .github/workflows -maxdepth 1 \( -name '*deploy*' -o -name '*cd*' \) 2>/dev/null | xargs cat 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
  COMBINED_HASH="${CURRENT_HASH}-${WORKFLOW_HASH}"
  if [ "$SAVED_HASH" != "$COMBINED_HASH" ] && [ -n "$SAVED_HASH" ]; then
    echo "CONFIG_CHANGED"
  else
    echo "CONFIRMED"
  fi
fi
```

**如果 CONFIRMED：** 打印"我之前已经部署过这个项目，了解它的工作方式。直接进入就绪检查。"继续到步骤 2。

**如果 CONFIG_CHANGED：** 部署配置自上次确认部署以来已更改。重新触发干运行。告诉用户：

"我之前部署过这个项目，但你的部署配置自那以后已更改。这可能意味着新平台、不同的工作流或更新的 URL。我将进行一次快速干运行以确保我仍然了解你的项目如何部署。"

然后继续到下面的 FIRST_RUN 流程（步骤 1.5a 到 1.5e）。

**如果 FIRST_RUN：** 这是此项目首次运行 `/land-and-deploy`。在执行任何不可逆操作之前，向用户展示将要发生什么。这是一次干运行 — 解释、验证并确认。

告诉用户：

"这是我第一次部署这个项目，所以我先做一次干运行。

这意味着什么：我会检测你的部署基础设施，测试我的命令是否真正有效，并在触碰任何东西之前逐步向你展示将要发生什么。一旦部署进入生产环境就不可逆，所以我想在开始合并之前赢得你的信任。

让我看看你的设置。"

### 1.5a：部署基础设施检测

运行部署配置引导以检测平台和设置：

```bash
# Check for persisted deploy config in CLAUDE.md
DEPLOY_CONFIG=$(grep -A 20 "## Deploy Configuration" CLAUDE.md 2>/dev/null || echo "NO_CONFIG")
echo "$DEPLOY_CONFIG"

# If config exists, parse it
if [ "$DEPLOY_CONFIG" != "NO_CONFIG" ]; then
  PROD_URL=$(echo "$DEPLOY_CONFIG" | grep -i "production.*url" | head -1 | sed 's/.*: *//')
  PLATFORM=$(echo "$DEPLOY_CONFIG" | grep -i "platform" | head -1 | sed 's/.*: *//')
  echo "PERSISTED_PLATFORM:$PLATFORM"
  echo "PERSISTED_URL:$PROD_URL"
fi

# Auto-detect platform from config files
[ -f fly.toml ] && echo "PLATFORM:fly"
[ -f render.yaml ] && echo "PLATFORM:render"
([ -f vercel.json ] || [ -d .vercel ]) && echo "PLATFORM:vercel"
[ -f netlify.toml ] && echo "PLATFORM:netlify"
[ -f Procfile ] && echo "PLATFORM:heroku"
([ -f railway.json ] || [ -f railway.toml ]) && echo "PLATFORM:railway"

# Detect deploy workflows
for f in $(find .github/workflows -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null); do
  [ -f "$f" ] && grep -qiE "deploy|release|production|cd" "$f" 2>/dev/null && echo "DEPLOY_WORKFLOW:$f"
  [ -f "$f" ] && grep -qiE "staging" "$f" 2>/dev/null && echo "STAGING_WORKFLOW:$f"
done
```

如果在 CLAUDE.md 中找到了 `PERSISTED_PLATFORM` 和 `PERSISTED_URL`，直接使用它们并跳过手动检测。如果没有持久化配置，使用自动检测的平台来指导部署验证。如果什么都没检测到，通过下面决策树中的 AskUserQuestion 询问用户。

如果你想为未来的运行持久化部署设置，建议用户运行 `/setup-deploy`。

解析输出并记录：检测到的平台、生产 URL、部署工作流（如果有），以及 CLAUDE.md 中的任何持久化配置。

### 1.5b：命令验证

测试每个检测到的命令以验证检测是否准确。构建验证表：

```bash
# Test gh auth (already passed in Step 1, but confirm)
gh auth status 2>&1 | head -3

# Test platform CLI if detected
# Fly.io: fly status --app {app} 2>/dev/null
# Heroku: heroku releases --app {app} -n 1 2>/dev/null
# Vercel: vercel ls 2>/dev/null | head -3

# Test production URL reachability
# curl -sf {production-url} -o /dev/null -w "%{http_code}" 2>/dev/null
```

根据检测到的平台运行相关命令。将结果构建成此表：

```
╔══════════════════════════════════════════════════════════╗
║         DEPLOY INFRASTRUCTURE VALIDATION                  ║
╠══════════════════════════════════════════════════════════╣
║                                                            ║
║  Platform:    {platform} (from {source})                   ║
║  App:         {app name or "N/A"}                          ║
║  Prod URL:    {url or "not configured"}                    ║
║                                                            ║
║  COMMAND VALIDATION                                        ║
║  ├─ gh auth status:     ✓ PASS                             ║
║  ├─ {platform CLI}:     ✓ PASS / ⚠ NOT INSTALLED / ✗ FAIL ║
║  ├─ curl prod URL:      ✓ PASS (200 OK) / ⚠ UNREACHABLE   ║
║  └─ deploy workflow:    {file or "none detected"}          ║
║                                                            ║
║  STAGING DETECTION                                         ║
║  ├─ Staging URL:        {url or "not configured"}          ║
║  ├─ Staging workflow:   {file or "not found"}              ║
║  └─ Preview deploys:    {detected or "not detected"}       ║
║                                                            ║
║  WHAT WILL HAPPEN                                          ║
║  1. Run pre-merge readiness checks (reviews, tests, docs)  ║
║  2. Wait for CI if pending                                 ║
║  3. Merge PR via {merge method}                            ║
║  4. {Wait for deploy workflow / Wait 60s / Skip}           ║
║  5. {Run canary verification / Skip (no URL)}              ║
║                                                            ║
║  MERGE METHOD: {squash/merge/rebase} (from repo settings)  ║
║  MERGE QUEUE:  {detected / not detected}                   ║
╚══════════════════════════════════════════════════════════╝
```

**验证失败是警告，不是阻塞器**（除了 `gh auth status` 已经在步骤 1 失败的情况）。如果 `curl` 失败，注明"我无法访问该 URL — 可能是网络问题、VPN 要求或地址错误。我仍然可以部署，但之后无法验证站点是否健康。"
如果平台 CLI 未安装，注明"{platform} CLI 未安装在此机器上。我仍然可以通过 GitHub 部署，但将使用 HTTP 健康检查而不是平台 CLI 来验证部署是否成功。"

### 1.5c：预发布检测

按此顺序检查预发布环境：

1. **CLAUDE.md 持久化配置：** 在部署配置部分检查预发布 URL：
```bash
grep -i "staging" CLAUDE.md 2>/dev/null | head -3
```

2. **GitHub Actions 预发布工作流：** 检查名称或内容中包含"staging"的工作流文件：
```bash
for f in $(find .github/workflows -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null); do
  [ -f "$f" ] && grep -qiE "staging" "$f" 2>/dev/null && echo "STAGING_WORKFLOW:$f"
done
```

3. **Vercel/Netlify 预览部署：** 检查 PR 状态检查中的预览 URL：
```bash
gh pr checks --json name,targetUrl 2>/dev/null | head -20
```
查找包含 "vercel"、"netlify" 或 "preview" 的检查名称并提取目标 URL。

记录找到的任何预发布目标。这些将在步骤 5 中提供。

### 1.5d：就绪性预览

告诉用户："在合并任何 PR 之前，我会运行一系列就绪性检查 — 代码审查、测试、文档、PR 准确性。让我向你展示这个项目的情况。"

预览将在步骤 3.5 运行的就绪性检查（不重新运行测试）：

```bash
~/.claude/skills/gstack/bin/gstack-review-read 2>/dev/null
```

显示审查状态摘要：哪些审查已运行、它们有多陈旧。
同时检查 CHANGELOG.md 和 VERSION 是否已更新。

用通俗英语解释："合并时，我会检查：代码是否最近被审查过？测试是否通过？CHANGELOG 是否更新？PR 描述是否准确？如果有任何不对的地方，我会在合并前标记出来。"

### 1.5e：干运行确认

告诉用户："这就是我检测到的所有内容。看看上面的表格 — 这与你项目实际的部署方式匹配吗？"

通过 AskUserQuestion 向用户展示完整的干运行结果：

- **重新定位：** "[项目] 在分支 [branch] 上的首次部署干运行。上面是我检测到的关于你的部署基础设施的信息。还没有合并或部署任何东西 — 这只是我对你的设置的理解。"
- 显示上面 1.5b 中的基础设施验证表。
- 列出命令验证中的任何警告，并附上通俗英语解释。
- 如果检测到预发布，注明："我在 {url/workflow} 发现了预发布环境。合并后，我会提供先部署到那里以便你在进入生产前验证一切正常的选项。"
- 如果未检测到预发布，注明："我没有找到预发布环境。部署将直接进入生产 — 我会在之后立即运行健康检查以确保一切正常。"
- **推荐：** 如果所有验证通过选择 A。如果有问题需要修复选择 B。要运行 /setup-deploy 进行更详细配置选择 C。
- A) 没错 — 这就是我的项目的部署方式。开始吧。（完整性：10/10）
- B) 有不对的地方 — 让我告诉你什么有问题（完整性：10/10）
- C) 我想先更仔细地配置一下（运行 /setup-deploy）（完整性：10/10）

**如果 A：** 告诉用户："很好 — 我已保存此配置。下次你运行 `/land-and-deploy` 时，我会跳过干运行直接进入就绪性检查。如果你的部署设置发生变化（新平台、不同的工作流、更新的 URL），我会自动重新运行干运行以确保我仍然理解正确。"

保存部署配置指纹以便我们检测未来的变化：
```bash
mkdir -p ~/.gstack/projects/$SLUG
CURRENT_HASH=$(sed -n '/## Deploy Configuration/,/^## /p' CLAUDE.md 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
WORKFLOW_HASH=$(find .github/workflows -maxdepth 1 \( -name '*deploy*' -o -name '*cd*' \) 2>/dev/null | xargs cat 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
echo "${CURRENT_HASH}-${WORKFLOW_HASH}" > ~/.gstack/projects/$SLUG/land-deploy-confirmed
```
继续到步骤 2。

**如果 B：** **STOP。** "告诉我你的设置有什么不同，我会调整。你也可以运行 `/setup-deploy` 来完成完整配置。"

**如果 C：** **STOP。** "运行 `/setup-deploy` 将详细引导你完成部署平台、生产 URL 和健康检查。它会将所有内容保存到 CLAUDE.md，这样我下次就知道该怎么做。完成后再次运行 `/land-and-deploy`。"

---

## 步骤 2：合并前检查

告诉用户："正在检查 CI 状态和合并就绪性..."

检查 CI 状态和合并就绪性：

```bash
gh pr checks --json name,state,status,conclusion
```

解析输出：
1. 如果任何必需检查**失败**：**STOP。** "此 PR 的 CI 失败。以下是失败的检查：{list}。在部署前修复这些 — 我不会合并未通过 CI 的代码。"
2. 如果必需检查**待处理**：告诉用户"CI 仍在运行。我会等待它完成。"继续到步骤 3。
3. 如果所有检查通过（或没有必需检查）：告诉用户"CI 通过。"跳过步骤 3，进入步骤 4。

同时检查合并冲突：
```bash
gh pr view --json mergeable -q .mergeable
```
如果 `CONFLICTING`：**STOP。** "此 PR 与基础分支存在合并冲突。解决冲突并推送，然后再次运行 `/land-and-deploy`。"

---

## 步骤 3：等待 CI（如果待处理）

如果必需检查仍在等待，等待它们完成。使用 15 分钟超时：

```bash
gh pr checks --watch --fail-fast
```

记录 CI 等待时间用于部署报告。

如果 CI 在超时内通过：告诉用户"CI 在 {duration} 后通过。进入就绪性检查。"继续到步骤 4。
如果 CI 失败：**STOP。** "CI 失败。以下是出错的地方：{failures}。这需要通过后我才能合并。"
如果超时（15 分钟）：**STOP。** "CI 已经运行超过 15 分钟 — 这很不寻常。检查 GitHub Actions 标签页看看是否有卡住的情况。"

---

## 步骤 3.4：VERSION 漂移检测（工作区感知发布）

在收集就绪性证据之前，验证此 PR 声明的 VERSION 是否仍然是下一个空闲插槽。在 `/ship` 运行之后，兄弟工作区可能已经发布并着陆，导致此 PR 的 VERSION 过时。

```bash
BRANCH_VERSION=$(git show HEAD:VERSION 2>/dev/null | tr -d '\r\n[:space:]' || echo "")
BASE_BRANCH=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main)
BASE_VERSION=$(git show origin/$BASE_BRANCH:VERSION 2>/dev/null | tr -d '\r\n[:space:]' || echo "")

# Imply bump level by comparing branch VERSION to base (crude but good enough for drift detection)
# We don't need the exact original level — we just need "a level" that passes to the util.
# If the minor digit advanced, call it minor; patch digit, patch; etc. If base > branch, skip (not ours to land).
# For simplicity: use "patch" as a conservative default; util handles collision-past regardless of input level.
QUEUE_JSON=$(bun run bin/gstack-next-version \
  --base "$BASE_BRANCH" \
  --bump patch \
  --current-version "$BASE_VERSION" 2>/dev/null || echo '{"offline":true}')
NEXT_SLOT=$(echo "$QUEUE_JSON" | jq -r '.version // empty')
OFFLINE=$(echo "$QUEUE_JSON" | jq -r '.offline // false')
```

行为：

1. 如果 `OFFLINE=true` 或工具失败：打印 `⚠ VERSION drift check unavailable (util offline) — proceeding with PR version v<BRANCH_VERSION>`。继续到步骤 3.5。CI 的版本门控作业是后盾。

2. 如果 `BRANCH_VERSION` 已经 `>=` `NEXT_SLOT`：无漂移（或我们的 PR 在队列前面）。继续。

3. 如果检测到漂移（一个 PR 在我们之前着陆且 `BRANCH_VERSION < NEXT_SLOT`）：**STOP** 并精确打印：
   ```
   ⚠ VERSION drift detected.
     This PR claims:  v<BRANCH_VERSION>
     Next free slot:  v<NEXT_SLOT>   (queue moved since last /ship)

   Rerun /ship from the feature branch to reconcile. /ship's ALREADY_BUMPED
   branch will detect the drift and rewrite VERSION + CHANGELOG header + PR title
   atomically. Do NOT merge from here — the landed PR would overwrite the other
   branch's CHANGELOG entry or land with a duplicate version header.
   ```

   以非零退出。不要从 `/land-and-deploy` 自动 bump — 重新运行 `/ship` 是干净的路径（它已经通过步骤 12 ALREADY_BUMPED 检测原子地处理 VERSION + package.json + CHANGELOG 标题 + PR 标题）。

---

## 步骤 3.5：合并前就绪门控

**这是不可逆合并之前的关键安全检查。** 合并无法在没有回滚提交的情况下撤销。收集所有证据，构建就绪性报告，并在继续之前获得用户的明确确认。

告诉用户："CI 是绿色的。现在我运行就绪性检查 — 这是合并前的最后一道门。我正在检查代码审查、测试结果、文档和 PR 准确性。一旦你看到就绪性报告并批准，合并就是最终的。"

为下面的每个检查收集证据。跟踪警告（黄色）和阻塞器（红色）。

### 3.5a：审查过期检查

```bash
~/.claude/skills/gstack/bin/gstack-review-read 2>/dev/null
```

解析输出。对于每个审查技能（plan-eng-review、plan-ceo-review、plan-design-review、design-review-lite、codex-review、review、adversarial-review、codex-plan-review）：

1. 查找最近 7 天内最新的条目。
2. 提取其 `commit` 字段。
3. 与当前 HEAD 比较：`git rev-list --count STORED_COMMIT..HEAD`

**过期规则：**
- 自审查以来 0 个提交 → CURRENT
- 自审查以来 1-3 个提交 → RECENT（如果这些提交涉及代码而非仅文档则为黄色）
- 自审查以来 4+ 个提交 → STALE（红色 — 审查可能不反映当前代码）
- 未找到审查 → NOT RUN

**关键检查：** 查看最后一次审查后更改了什么。运行：
```bash
git log --oneline STORED_COMMIT..HEAD
```
如果审查后的任何提交包含"fix"、"refactor"、"rewrite"、"overhaul"等词，或触及超过 5 个文件 — 标记为 **STALE（审查后有重大更改）**。审查是在与即将合并的代码不同的代码上完成的。

**同时检查对抗性审查（`codex-review`）。** 如果 codex-review 已运行且为 CURRENT，在就绪性报告中提及作为额外的信心信号。如果未运行，注明为信息性（不是阻塞器）："没有对抗性审查记录。"

### 3.5a-bis：内联审查提供

**我们对部署格外小心。** 如果工程审查是 STALE（自审查以来 4+ 个提交）或 NOT RUN，提供在继续之前运行快速审查。

使用 AskUserQuestion：
- **重新定位：** "我注意到此分支上的{代码审查已过时 / 未运行代码审查}。由于此代码即将进入生产环境，我想在合并前对差异进行快速安全检查。这是我确保不该发布的东西不会被发布的方式之一。"
- **推荐：** 选择 A 进行快速安全检查。选择 B 如果你想要完整的审查体验。仅在你对代码有信心时选择 C。
- A) 运行快速审查（约 2 分钟）— 我会扫描差异查找常见问题如 SQL 安全、竞态条件和安全漏洞（完整性：7/10）
- B) 停止并先运行完整 `/review` — 更深入分析，更彻底（完整性：10/10）
- C) 跳过审查 — 我已亲自审查此代码且有信心（完整性：3/10）

**如果 A（快速清单）：** 告诉用户："现在对你的差异运行审查清单..."

读取审查清单：
```bash
cat ~/.claude/skills/gstack/review/checklist.md 2>/dev/null || echo "Checklist not found"
```
将每个清单项应用于当前差异。这与 `/ship` 在其步骤 3.5 中运行的快速审查相同。自动修复琐碎问题（空白、导入）。对于关键发现（SQL 安全、竞态条件、安全性），询问用户。

**如果快速审查期间进行了任何代码更改：** 提交修复，然后 **STOP** 并告诉用户："我在审查期间发现并修复了一些问题。修复已提交 — 再次运行 `/land-and-deploy` 来获取它们并从我们中断的地方继续。"

**如果未发现问题：** 告诉用户："审查清单通过 — 差异中未发现问题。"

**如果 B：** **STOP。** "好决定 — 运行 `/review` 进行彻底的着陆前审查。完成后，再次运行 `/land-and-deploy`，我会在我们中断的地方继续。"

**如果 C：** 告诉用户："了解 — 跳过审查。你最了解这段代码。"继续。记录用户选择跳过审查。

**如果审查是 CURRENT：** 完全跳过此子步骤 — 不提问。

### 3.5b：测试结果

**免费测试 — 现在运行它们：**

读取 CLAUDE.md 查找项目的测试命令。如果未指定，使用 `bun test`。
运行测试命令并捕获退出代码和输出。

```bash
bun test 2>&1 | tail -10
```

如果测试失败：**阻塞器。** 不能在测试失败的情况下合并。

**E2E 测试 — 检查最近结果：**

```bash
setopt +o nomatch 2>/dev/null || true  # zsh compat
ls -t ~/.gstack-dev/evals/*-e2e-*-$(date +%Y-%m-%d)*.json 2>/dev/null | head -20
```

对于今天的每个评估文件，解析通过/失败计数。显示：
- 总测试数、通过数、失败数
- 运行完成多久了（从文件时间戳）
- 总成本
- 任何失败测试的名称

如果今天没有 E2E 结果：**警告 — 今天未运行 E2E 测试。**
如果 E2E 结果存在但有失败：**警告 — N 个测试失败。** 列出它们。

**LLM 评判评估 — 检查最近结果：**

```bash
setopt +o nomatch 2>/dev/null || true  # zsh compat
ls -t ~/.gstack-dev/evals/*-llm-judge-*-$(date +%Y-%m-%d)*.json 2>/dev/null | head -5
```

如果找到，解析并显示通过/失败。如果未找到，注明"今天未运行 LLM 评估。"

### 3.5c：PR 正文准确性检查

读取当前 PR 正文：
```bash
gh pr view --json body -q .body
```

读取当前差异摘要：
```bash
git log --oneline $(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main)..HEAD | head -20
```

将 PR 正文与实际提交进行比较。检查：
1. **遗漏的功能** — 添加了 PR 中未提及的重要功能的提交
2. **过时的描述** — PR 正文提到后来更改或回滚的内容
3. **错误的版本** — PR 标题或正文引用了与 VERSION 文件不匹配的版本

如果 PR 正文看起来过时或不完整：**警告 — PR 正文可能不反映当前更改。** 列出遗漏或过时的内容。

### 3.5d：文档发布检查

检查此分支上是否更新了文档：

```bash
git log --oneline --all-match --grep="docs:" $(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main)..HEAD | head -5
```

同时检查关键文档文件是否被修改：
```bash
git diff --name-only $(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main)...HEAD -- README.md CHANGELOG.md ARCHITECTURE.md CONTRIBUTING.md CLAUDE.md VERSION
```

如果此分支上未修改 CHANGELOG.md 和 VERSION 且差异包含新功能（新文件、新命令、新技能）：**警告 — /document-release 可能未运行。尽管有新功能，CHANGELOG 和 VERSION 未更新。**

如果仅更改了文档（无代码）：跳过此检查。

### 3.5e：就绪性报告和确认

告诉用户："这是完整的就绪性报告。这是我在合并前检查的所有内容。"

构建完整的就绪性报告：

```
╔══════════════════════════════════════════════════════════╗
║              PRE-MERGE READINESS REPORT                  ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  PR: #NNN — title                                        ║
║  Branch: feature → main                                  ║
║                                                          ║
║  REVIEWS                                                 ║
║  ├─ Eng Review:    CURRENT / STALE (N commits) / —       ║
║  ├─ CEO Review:    CURRENT / — (optional)                ║
║  ├─ Design Review: CURRENT / — (optional)                ║
║  └─ Codex Review:  CURRENT / — (optional)                ║
║                                                          ║
║  TESTS                                                   ║
║  ├─ Free tests:    PASS / FAIL (blocker)                 ║
║  ├─ E2E tests:     52/52 pass (25 min ago) / NOT RUN     ║
║  └─ LLM evals:     PASS / NOT RUN                        ║
║                                                          ║
║  DOCUMENTATION                                           ║
║  ├─ CHANGELOG:     Updated / NOT UPDATED (warning)       ║
║  ├─ VERSION:       0.9.8.0 / NOT BUMPED (warning)        ║
║  └─ Doc release:   Run / NOT RUN (warning)               ║
║                                                          ║
║  PR BODY                                                 ║
║  └─ Accuracy:      Current / STALE (warning)             ║
║                                                          ║
║  WARNINGS: N  |  BLOCKERS: N                             ║
╚══════════════════════════════════════════════════════════╝
```

如果有阻塞器（免费测试失败）：列出它们并推荐 B。
如果有警告但无阻塞器：列出每个警告，如果警告轻微推荐 A，如果警告严重推荐 B。
如果一切绿色：推荐 A。

使用 AskUserQuestion：

- **重新定位：** "准备合并 PR #NNN — '{title}' 到 {base}。以下是我的发现。"
  显示上面的报告。
- 如果一切绿色："所有检查通过。此 PR 准备好合并。"
- 如果有警告：用通俗英语列出每个。例如，"工程审查是在 6 个提交之前完成的 — 代码自那以后已更改"而不是"STALE（6 个提交）。"
- 如果有阻塞器："我发现合并前需要修复的问题：{list}"
- **推荐：** 如果绿色选择 A。如果有严重警告选择 B。仅在用户理解风险时选择 C。
- A) 合并吧 — 一切看起来不错（完整性：10/10）
- B) 等等 — 我想先修复警告（完整性：10/10）
- C) 无论如何合并 — 我理解警告并想继续（完整性：3/10）

如果用户选择 B：**STOP。** 给出具体下一步：
- 如果审查过时："运行 `/review` 或 `/autoplan` 审查当前代码，然后再次运行 `/land-and-deploy`。"
- 如果 E2E 未运行："运行你的 E2E 测试确保没有问题，然后回来。"
- 如果文档未更新："运行 `/document-release` 更新 CHANGELOG 和文档。"
- 如果 PR 正文过时："PR 描述与差异中的实际内容不匹配 — 在 GitHub 上更新它。"

如果用户选择 A 或 C：告诉用户"现在合并。"继续到步骤 4。

---

## 步骤 4：合并 PR

记录开始时间戳用于计时数据。同时记录采取的合并路径（自动合并 vs 直接）用于部署报告。

先尝试自动合并（尊重仓库合并设置和合并队列）：

```bash
gh pr merge --auto --delete-branch
```

如果 `--auto` 成功：记录 `MERGE_PATH=auto`。这意味着仓库启用了自动合并，可能使用合并队列。

如果 `--auto` 不可用（仓库未启用自动合并），直接合并：

```bash
gh pr merge --squash --delete-branch
```

如果直接合并成功：记录 `MERGE_PATH=direct`。告诉用户："PR 合并成功。分支已清理。"

如果合并因权限错误失败：**STOP。** "我没有权限合并此 PR。你需要维护者来合并它，或检查你仓库的分支保护规则。"

### 4a：合并队列检测和消息

如果 `MERGE_PATH=auto` 且 PR 状态未立即变为 `MERGED`，PR 在**合并队列**中。告诉用户：

"你的仓库使用合并队列 — 这意味着 GitHub 会在最终合并提交上再运行一次 CI 然后才真正合并。这是件好事（它能捕获最后时刻的冲突），但意味着我们需要等待。我会持续检查直到它通过。"

轮询 PR 实际合并：

```bash
gh pr view --json state -q .state
```

每 30 秒轮询一次，最多 30 分钟。每 2 分钟显示进度消息："仍在合并队列中...（到目前为止 {X} 分钟）"

如果 PR 状态变为 `MERGED`：捕获合并提交 SHA。告诉用户："合并队列完成 — PR 已合并。耗时 {duration}。"

如果 PR 从队列中移除（状态回到 `OPEN`）：**STOP。** "PR 从合并队列中移除 — 这通常意味着合并提交上的 CI 检查失败，或队列中的另一个 PR 导致冲突。检查 GitHub 合并队列页面查看发生了什么。"
如果超时（30 分钟）：**STOP。** "合并队列已处理 30 分钟。可能有卡住的地方 — 检查 GitHub Actions 标签页和合并队列页面。"

### 4b：CI 自动部署检测

PR 合并后，检查合并是否触发了部署工作流：

```bash
gh run list --branch <base> --limit 5 --json name,status,workflowName,headSha
```

查找与合并提交 SHA 匹配的运行。如果找到部署工作流：
- 告诉用户："PR 已合并。我可以看到部署工作流（'{workflow-name}'）自动启动了。我会监控它并在完成时通知你。"

如果合并后未找到部署工作流：
- 告诉用户："PR 已合并。我没有看到部署工作流 — 你的项目可能以不同方式部署，或者可能是没有部署步骤的库/CLI。我会在下一步确定正确的验证方式。"

如果 `MERGE_PATH=auto` 且仓库使用合并队列且存在部署工作流：
- 告诉用户："PR 通过了合并队列，部署工作流正在运行。现在监控它。"

记录合并时间戳、时长和合并路径用于部署报告。

---

## 步骤 5：部署策略检测

确定这是什么类型的项目以及如何验证部署。

首先，运行部署配置引导以检测或读取持久化的部署设置：

```bash
# Check for persisted deploy config in CLAUDE.md
DEPLOY_CONFIG=$(grep -A 20 "## Deploy Configuration" CLAUDE.md 2>/dev/null || echo "NO_CONFIG")
echo "$DEPLOY_CONFIG"

# If config exists, parse it
if [ "$DEPLOY_CONFIG" != "NO_CONFIG" ]; then
  PROD_URL=$(echo "$DEPLOY_CONFIG" | grep -i "production.*url" | head -1 | sed 's/.*: *//')
  PLATFORM=$(echo "$DEPLOY_CONFIG" | grep -i "platform" | head -1 | sed 's/.*: *//')
  echo "PERSISTED_PLATFORM:$PLATFORM"
  echo "PERSISTED_URL:$PROD_URL"
fi

# Auto-detect platform from config files
[ -f fly.toml ] && echo "PLATFORM:fly"
[ -f render.yaml ] && echo "PLATFORM:render"
([ -f vercel.json ] || [ -d .vercel ]) && echo "PLATFORM:vercel"
[ -f netlify.toml ] && echo "PLATFORM:netlify"
[ -f Procfile ] && echo "PLATFORM:heroku"
([ -f railway.json ] || [ -f railway.toml ]) && echo "PLATFORM:railway"

# Detect deploy workflows
for f in $(find .github/workflows -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null); do
  [ -f "$f" ] && grep -qiE "deploy|release|production|cd" "$f" 2>/dev/null && echo "DEPLOY_WORKFLOW:$f"
  [ -f "$f" ] && grep -qiE "staging" "$f" 2>/dev/null && echo "STAGING_WORKFLOW:$f"
done
```

如果在 CLAUDE.md 中找到了 `PERSISTED_PLATFORM` 和 `PERSISTED_URL`，直接使用它们并跳过手动检测。如果没有持久化配置，使用自动检测的平台来指导部署验证。如果什么都没检测到，通过下面决策树中的 AskUserQuestion 询问用户。

如果你想为未来的运行持久化部署设置，建议用户运行 `/setup-deploy`。

然后运行 `gstack-diff-scope` 对更改进行分类：

```bash
eval $(~/.claude/skills/gstack/bin/gstack-diff-scope $(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo main) 2>/dev/null)
echo "FRONTEND=$SCOPE_FRONTEND BACKEND=$SCOPE_BACKEND DOCS=$SCOPE_DOCS CONFIG=$SCOPE_CONFIG"
```

**决策树（按顺序评估）：**

1. 如果用户提供了生产 URL 作为参数：将其用于金丝雀验证。同时检查部署工作流。

2. 检查 GitHub Actions 部署工作流：
```bash
gh run list --branch <base> --limit 5 --json name,status,conclusion,headSha,workflowName
```
查找名称包含 "deploy"、"release"、"production" 或 "cd" 的工作流。如果找到：在步骤 6 中轮询部署工作流，然后运行金丝雀检查。

3. 如果 SCOPE_DOCS 是唯一为 true 的范围（无前端、无后端、无配置）：完全跳过验证。告诉用户："这仅是文档更改 — 无需部署或验证。你已完成。"进入步骤 9。

4. 如果未检测到部署工作流且未提供 URL：使用 AskUserQuestion 一次：
   - **重新定位：** "PR 已合并，但我没有看到此项目的部署工作流或生产 URL。如果这是 Web 应用，你提供 URL 后我可以验证部署。如果是库或 CLI 工具，无需验证 — 我们完成了。"
   - **推荐：** 如果这是库/CLI 工具选择 B。如果是 Web 应用选择 A。
   - A) 这是生产 URL：{让他们输入}
   - B) 无需部署 — 这不是 Web 应用

### 5a：预发布优先选项

如果在步骤 1.5c 中检测到预发布（或来自 CLAUDE.md 部署配置），且更改包含代码（非仅文档），提供预发布优先选项：

使用 AskUserQuestion：
- **重新定位：** "我在 {预发布 URL 或工作流} 发现了预发布环境。由于此部署包含代码更改，我可以先在预发布上验证一切正常 — 然后再进入生产。这是最安全的路径：如果预发布上出了什么问题，生产环境不受影响。"
- **推荐：** 选择 A 以获得最大安全性。选择 B 如果你有信心。
- A) 先部署到预发布，验证正常，然后进入生产（完整性：10/10）
- B) 跳过预发布 — 直接进入生产（完整性：7/10）
- C) 仅部署到预发布 — 我稍后检查生产（完整性：8/10）

**如果 A（预发布优先）：** 告诉用户："先部署到预发布。我会运行与在生产上相同的健康检查 — 如果预发布看起来正常，我会自动进入生产。"

先对预发布目标运行步骤 6-7。使用预发布 URL 或预发布工作流进行部署验证和金丝雀检查。预发布通过后，告诉用户："预发布健康 — 你的更改正在工作。现在部署到生产。"然后对生产目标再次运行步骤 6-7。

**如果 B（跳过预发布）：** 告诉用户："跳过预发布 — 直接进入生产。"正常进行生产部署。

**如果 C（仅预发布）：** 告诉用户："仅部署到预发布。我会验证它正常工作然后停止。"

对预发布目标运行步骤 6-7。验证后，打印部署报告（步骤 9），结论为"预发布已验证 — 生产部署待定。"
然后告诉用户："预发布看起来正常。准备好进行生产时，再次运行 `/land-and-deploy`。"
**STOP。** 用户可以稍后重新运行 `/land-and-deploy` 进行生产。

**如果未检测到预发布：** 完全跳过此子步骤。不提问。

---

## 步骤 6：等待部署（如适用）

部署验证策略取决于步骤 5 中检测到的平台。

### 策略 A：GitHub Actions 工作流

如果检测到部署工作流，查找由合并提交触发的运行：

```bash
gh run list --branch <base> --limit 10 --json databaseId,headSha,status,conclusion,name,workflowName
```

按合并提交 SHA 匹配（在步骤 4 中捕获）。如果多个匹配的工作流，优先选择名称与步骤 5 中检测到的部署工作流匹配的那个。

每 30 秒轮询一次：
```bash
gh run view <run-id> --json status,conclusion
```

### 策略 B：平台 CLI（Fly.io、Render、Heroku）

如果在 CLAUDE.md 中配置了部署状态命令（例如 `fly status --app myapp`），使用它代替或附加于 GitHub Actions 轮询。

**Fly.io：** 合并后，Fly 通过 GitHub Actions 或 `fly deploy` 部署。检查：
```bash
fly status --app {app} 2>/dev/null
```
查找 `Machines` 状态显示 `started` 和最近的部署时间戳。

**Render：** Render 在推送到连接的分支时自动部署。通过轮询生产 URL 直到响应来检查：
```bash
curl -sf {production-url} -o /dev/null -w "%{http_code}" 2>/dev/null
```
Render 部署通常需要 2-5 分钟。每 30 秒轮询一次。

**Heroku：** 检查最新发布：
```bash
heroku releases --app {app} -n 1 2>/dev/null
```

### 策略 C：自动部署平台（Vercel、Netlify）

Vercel 和 Netlify 在合并时自动部署。无需显式部署触发器。等待 60 秒让部署传播，然后直接进入步骤 7 的金丝雀验证。

### 策略 D：自定义部署钩子

如果 CLAUDE.md 的"自定义部署钩子"部分有自定义部署状态命令，运行该命令并检查其退出代码。

### 通用：计时和失败处理

记录部署开始时间。每 2 分钟显示进度："部署仍在运行...（到目前为止 {X} 分钟）。这对大多数平台来说是正常的。"

如果部署成功（`conclusion` 是 `success` 或健康检查通过）：告诉用户"部署成功完成。耗时 {duration}。现在我将验证站点是否健康。"记录部署时长，继续到步骤 7。

如果部署失败（`conclusion` 是 `failure`）：使用 AskUserQuestion：
- **重新定位：** "合并后部署工作流失败。代码已合并但可能尚未上线。以下是我可以做的："
- **推荐：** 选择 A 在回滚前调查。
- A) 让我查看部署日志找出问题所在
- B) 立即回滚合并 — 回退到之前版本
- C) 无论如何继续健康检查 — 部署失败可能是不稳定步骤，站点实际上可能正常

如果超时（20 分钟）："部署已运行 20 分钟，比大多数部署时间更长。站点可能仍在部署中，或者可能有卡住的地方。"询问是继续等待还是跳过验证。

---

## 步骤 7：金丝雀验证（条件深度）

告诉用户："部署完成。现在我将检查线上站点以确保一切正常 — 加载页面、检查错误和测量性能。"

使用步骤 5 的差异范围分类来确定金丝雀深度：

| 差异范围 | 金丝雀深度 |
|----------|-----------|
| 仅 SCOPE_DOCS | 已在步骤 5 跳过 |
| 仅 SCOPE_CONFIG | 冒烟：`$B goto` + 验证 200 状态 |
| 仅 SCOPE_BACKEND | 控制台错误 + 性能检查 |
| SCOPE_FRONTEND（任意） | 完整：控制台 + 性能 + 截图 |
| 混合范围 | 完整金丝雀 |

**完整金丝雀序列：**

```bash
$B goto <url>
```

检查页面是否成功加载（200，不是错误页面）。

```bash
$B console --errors
```

检查关键控制台错误：包含 `Error`、`Uncaught`、`Failed to load`、`TypeError`、`ReferenceError` 的行。忽略警告。

```bash
$B perf
```

检查页面加载时间是否在 10 秒以内。

```bash
$B text
```

验证页面有内容（不是空白，不是通用错误页面）。

```bash
$B snapshot -i -a -o ".gstack/deploy-reports/post-deploy.png"
```

拍摄带注释的截图作为证据。

**健康评估：**
- 页面成功加载且状态为 200 → PASS
- 无关键控制台错误 → PASS
- 页面有真实内容（不是空白或错误屏幕） → PASS
- 在 10 秒内加载 → PASS

如果全部通过：告诉用户"站点健康。页面在 {X} 秒内加载，无控制台错误，内容看起来正常。截图保存到 {path}。"标记为 HEALTHY，继续到步骤 9。

如果有任何失败：显示证据（截图路径、控制台错误、性能数据）。使用 AskUserQuestion：
- **重新定位：** "我在部署后在线上站点发现了一些问题。以下是我看到的：{具体问题}。这可能是暂时的（缓存清除、CDN 传播）也可能是真正的问题。"
- **推荐：** 根据严重程度选择 — 关键（站点宕机）选 B，轻微（控制台错误）选 A。
- A) 这是预期的 — 站点仍在预热。标记为健康。
- B) 那坏了 — 回滚合并并回退到之前版本
- C) 让我进一步调查 — 打开站点并在决定前查看日志

---

## 步骤 8：回滚（如需要）

如果用户在任何时候选择回滚：

告诉用户："现在回滚合并。这将创建一个撤销此 PR 所有更改的新提交。一旦回滚部署完成，你站点的之前版本将被恢复。"

```bash
git fetch origin <base>
git checkout <base>
git revert <merge-commit-sha> --no-edit
git push origin <base>
```

如果回滚有冲突："回滚有合并冲突 — 如果在你合并之后有其他更改落在 {base} 上可能会发生这种情况。你需要手动解决冲突。合并提交 SHA 是 `<sha>` — 运行 `git revert <sha>` 重试。"

如果基础分支有推送保护："此仓库有分支保护，所以我无法直接推送回滚。我会改为创建回滚 PR — 合并它以回滚。"
然后创建回滚 PR：`gh pr create --title 'revert: <original PR title>'`

回滚成功后：告诉用户"回滚已推送到 {base}。CI 通过后部署应自动回滚。留意站点确认。"记录回滚提交 SHA 并以 REVERTED 状态继续到步骤 9。

---

## 步骤 9：部署报告

创建部署报告目录：

```bash
mkdir -p .gstack/deploy-reports
```

生成并显示 ASCII 摘要：

```
LAND & DEPLOY REPORT
═════════════════════
PR:           #<number> — <title>
Branch:       <head-branch> → <base-branch>
Merged:       <timestamp> (<merge method>)
Merge SHA:    <sha>
Merge path:   <auto-merge / direct / merge queue>
First run:    <yes (dry-run validated) / no (previously confirmed)>

Timing:
  Dry-run:    <duration or "skipped (confirmed)">
  CI wait:    <duration>
  Queue:      <duration or "direct merge">
  Deploy:     <duration or "no workflow detected">
  Staging:    <duration or "skipped">
  Canary:     <duration or "skipped">
  Total:      <end-to-end duration>

Reviews:
  Eng review: <CURRENT / STALE / NOT RUN>
  Inline fix: <yes (N fixes) / no / skipped>

CI:           <PASSED / SKIPPED>
Deploy:       <PASSED / FAILED / NO WORKFLOW / CI AUTO-DEPLOY>
Staging:      <VERIFIED / SKIPPED / N/A>
Verification: <HEALTHY / DEGRADED / SKIPPED / REVERTED>
  Scope:      <FRONTEND / BACKEND / CONFIG / DOCS / MIXED>
  Console:    <N errors or "clean">
  Load time:  <Xs>
  Screenshot: <path or "none">

VERDICT: <DEPLOYED AND VERIFIED / DEPLOYED (UNVERIFIED) / STAGING VERIFIED / REVERTED>
```

保存报告到 `.gstack/deploy-reports/{date}-pr{number}-deploy.md`。

记录到审查仪表板：

```bash
eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)"
mkdir -p ~/.gstack/projects/$SLUG
```

写入带计时数据的 JSONL 条目：
```json
{"skill":"land-and-deploy","timestamp":"<ISO>","status":"<SUCCESS/REVERTED>","pr":<number>,"merge_sha":"<sha>","merge_path":"<auto/direct/queue>","first_run":<true/false>,"deploy_status":"<HEALTHY/DEGRADED/SKIPPED>","staging_status":"<VERIFIED/SKIPPED>","review_status":"<CURRENT/STALE/NOT_RUN/INLINE_FIX>","ci_wait_s":<N>,"queue_s":<N>,"deploy_s":<N>,"staging_s":<N>,"canary_s":<N>,"total_s":<N>}
```

---

## 步骤 10：建议后续操作

部署报告之后：

如果结论是 DEPLOYED AND VERIFIED：告诉用户"你的更改已上线并已验证。漂亮的发布。"

如果结论是 DEPLOYED (UNVERIFIED)：告诉用户"你的更改已合并并应该正在部署。我无法验证站点 — 有机会时手动检查。"

如果结论是 REVERTED：告诉用户"合并已回滚。你的更改不再在 {base} 上。如果需要修复和重新发布，PR 分支仍然可用。"

然后建议相关后续：
- 如果已验证生产 URL："需要扩展监控？运行 `/canary <url>` 在接下来 10 分钟监控站点。"
- 如果收集了性能数据："需要更深入的性能分析？运行 `/benchmark <url>`。"
- "需要更新文档？运行 `/document-release` 将 README、CHANGELOG 和其他文档与你刚发布的内容同步。"

---

## 重要规则

- **永远不要强制推送。** 使用安全的 `gh pr merge`。
- **永远不要跳过 CI。** 如果检查失败，停止并解释原因。
- **叙述旅程。** 用户应该始终知道：刚才发生了什么，正在发生什么，接下来要发生什么。步骤之间没有沉默间隙。
- **自动检测一切。** PR 编号、合并方式、部署策略、项目类型、合并队列、预发布环境。仅在信息确实无法推断时询问。
- **带退避的轮询。** 不要频繁调用 GitHub API。CI/部署间隔 30 秒，有合理的超时。
- **回滚始终是选项。** 在每个失败点，提供回滚作为逃生出口。用通俗英语解释回滚的作用。
- **单次验证，不是持续监控。** `/land-and-deploy` 检查一次。`/canary` 做扩展监控循环。
- **清理。** 合并后删除功能分支（通过 `--delete-branch`）。
- **首次运行 = 教师模式。** 逐步引导用户。解释每个检查的作用和为什么重要。向他们展示他们的基础设施。在继续之前让他们确认。通过透明度建立信任。
- **后续运行 = 高效模式。** 简短的状态更新，不重复解释。用户已经信任工具 — 只需完成工作并报告结果。
- **目标是：首次使用者想"哇，这很彻底 — 我信任它。"重复使用者想"很快 — 它就是能用。"**
