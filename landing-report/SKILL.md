---
name: landing-report
version: 0.1.0
description: |
  工作区感知发布的只读队列仪表板。显示哪些 VERSION 插槽
  目前被打开的 PR 占用，哪些兄弟 Conductor 工作区有
  可能即将发布的 WIP 工作，以及 /ship 接下来会选择哪个插槽。无
  变更 — 只是快照。当要求"landing report"、"队列中有什么"、
  "显示打开的 PR"或"我接下来声明哪个版本"时使用。(gstack)
triggers:
  - landing report
  - version queue
  - ship queue
  - what version comes next
  - show open PR versions
allowed-tools:
  - Bash
  - Read
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /landing-report — 版本队列仪表板

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
echo '{"skill":"landing-report","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
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
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"landing-report","event":"started","branch":"'"$_BRANCH"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null &
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

通用前置逻辑（计划模式、功能发现、写作风格、遥测提示、主动提示、路由注入、vendoring 警告等）与 health 技能相同。

## 为什么存在此技能

当你运行 5-10 个并行 Conductor 工作区时，一眼看到哪些版本号被占用、被谁占用、以及你的下一个 `/ship` 会落在哪个插槽是很有帮助的。此技能是对 `/ship` 使用的同一 `bin/gstack-next-version` 工具的只读调用，但没有任何变更。可以把它看作是 VERSION 号的 `gh pr list`。

---

## 步骤 1：检测平台和基础分支

与其他 gstack 技能相同的检测。

```bash
BASE_BRANCH=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || \
              gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || \
              echo main)
echo "Base branch: $BASE_BRANCH"
```

---

## 步骤 2：读取当前状态

```bash
CURRENT_VERSION=$(cat VERSION 2>/dev/null | tr -d '[:space:]' || echo "0.0.0.0")
git fetch origin "$BASE_BRANCH" --quiet 2>/dev/null || true
BASE_VERSION=$(git show "origin/$BASE_BRANCH:VERSION" 2>/dev/null | tr -d '[:space:]' || echo "$CURRENT_VERSION")
echo "origin/$BASE_BRANCH VERSION: $BASE_VERSION"
echo "branch HEAD VERSION: $CURRENT_VERSION"
```

---

## 步骤 3：查询队列

调用工具三次 — 每个 bump 级别一次 — 以便用户看到他们为 micro/patch/minor/major 会声明什么。廉价（由 bun 缓存的相同 gh 调用）。

```bash
for LEVEL in micro patch minor major; do
  bun run bin/gstack-next-version \
    --base "$BASE_BRANCH" \
    --bump "$LEVEL" \
    --current-version "$BASE_VERSION" \
    > "/tmp/landing-$LEVEL.json" 2>/dev/null || echo '{"offline":true}' > "/tmp/landing-$LEVEL.json"
done
```

---

## 步骤 4：渲染仪表板

构建单表输出。使用 `patch` 级别 JSON 作为队列 + 兄弟的规范（它们在 bump 级别间相同；只有 `.version` 不同）。

使用 `jq` 提取：
- `.host` — github | gitlab | unknown
- `.offline` — 查询是否失败？
- `.claimed` — {pr, branch, version, url} 数组
- `.siblings` — 找到的所有兄弟工作树
- `.active_siblings` — 可能即将发布的子集

以以下精确格式渲染：

```
╔══════════════════════════════════════════════════════════════════╗
║                     GSTACK LANDING REPORT                        ║
╠══════════════════════════════════════════════════════════════════╣
║ Repo:    <owner/repo>                                            ║
║ Base:    <base> @ v<base-version>                                ║
║ Host:    <github|gitlab|unknown>                                 ║
║ Status:  <ONLINE|OFFLINE: queue-awareness unavailable>           ║
╚══════════════════════════════════════════════════════════════════╝

在 <base> 上声明版本的打开 PR：
  #1152  alpha-branch         → v1.7.0.0
  #1153  beta-branch          → v1.7.0.0  ⚠ 与 #1152 冲突
  #1151  gamma-branch         → v1.6.5.0

兄弟 Conductor 工作树（<workspace_root>）：
  path                        branch                 VERSION      last commit   PR
  ──────────────────────────────────────────────────────────────────────────────────
  ../tokyo-v2                 feat/dashboard         v1.7.1.0    3h ago         none  ★ active
  ../melbourne                feat/review            v1.6.0.0    12d ago        none
  ../osaka                    feat/payments          v1.8.0.0    5h ago         #1155

★ active = VERSION 领先于基础分支 且 最后提交 < 24h 且 没有打开的 PR。
  这些是可能即将发布的。

如果你现在运行 /ship，你会声明：
  micro bump:  v1.6.3.1   (queue-advance: none)
  patch bump:  v1.7.1.0   (bumped past claimed 1.7.0.0)
  minor bump:  v1.8.0.0   (bumped past claimed 1.7.0.0)
  major bump:  v2.0.0.0   (no major collisions)
```

对于离线/未知主机输出，打印更短的块：

```
╔══════════════════════════════════════════════════════════════════╗
║                     GSTACK LANDING REPORT                        ║
╠══════════════════════════════════════════════════════════════════╣
║ Status:  OFFLINE — queue-awareness unavailable                   ║
║ Reason:  <offline reason from warnings>                          ║
╚══════════════════════════════════════════════════════════════════╝

回退：本地 VERSION bump 仍然有效，但无法检测冲突。
```

---

## 步骤 5：建议下一步操作

渲染表格后，建议以下之一：

1. **如果队列中有冲突**（两个打开的 PR 声明相同版本）：
   "⚠ 两个打开的 PR 在 v<X> 上冲突。第二个合并的人要么会覆盖第一个的 CHANGELOG 条目，要么会发布重复版本。考虑让一个作者重新运行 /ship 以选择下一个空闲插槽。"

2. **如果活跃的兄弟排名高于用户分支版本：**
   "兄弟工作树 <path> 有 v<X>，提交于 <N> 小时前，还没有发 PR。如果那个工作先发布，你的分支在 land 时需要重新 bump。"

3. **如果一切看起来干净：**
   "队列干净。下一个 /ship 将无冲突地声明一个插槽。"

---

## 计划模式

PLAN MODE EXCEPTION — ALWAYS RUN。此技能完全是只读的：无文件写入、无 git 变更、无网络状态更改。在计划模式下安全运行。
