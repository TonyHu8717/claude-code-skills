---
name: gstack-upgrade
version: 1.1.0
description: |
  升级 gstack 到最新版本。检测全局安装还是本地安装，
  运行升级，并显示更新内容。当要求"升级 gstack"、
  "更新 gstack"或"获取最新版本"时使用。
  语音触发（语音转文字别名）："升级工具"、"更新工具"、"gee stack 升级"、"g stack 升级"。
triggers:
  - upgrade gstack
  - update gstack version
  - get latest gstack
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /gstack-upgrade

升级 gstack 到最新版本并显示更新内容。

## 内联升级流程

当所有技能前置脚本检测到 `UPGRADE_AVAILABLE` 时引用此部分。

### 步骤 1：询问用户（或自动升级）

首先，检查是否启用自动升级：
```bash
_AUTO=""
[ "${GSTACK_AUTO_UPGRADE:-}" = "1" ] && _AUTO="true"
[ -z "$_AUTO" ] && _AUTO=$(~/.claude/skills/gstack/bin/gstack-config get auto_upgrade 2>/dev/null || true)
echo "AUTO_UPGRADE=$_AUTO"
```

**如果 `AUTO_UPGRADE=true` 或 `AUTO_UPGRADE=1`：** 跳过 AskUserQuestion。记录"自动升级 gstack v{old} → v{new}..."并直接进入步骤 2。如果 `./setup` 在自动升级期间失败，从备份（`.bak` 目录）恢复并警告用户："自动升级失败 — 已恢复到之前版本。请手动运行 `/gstack-upgrade` 重试。"

**否则**，使用 AskUserQuestion：
- 问题："gstack **v{new}** 已可用（你当前使用 v{old}）。现在升级吗？"
- 选项：["是，现在升级", "始终保持最新", "暂时不要", "不再询问"]

**如果选择"是，现在升级"：** 进入步骤 2。

**如果选择"始终保持最新"：**
```bash
~/.claude/skills/gstack/bin/gstack-config set auto_upgrade true
```
告诉用户："已启用自动升级。未来的更新将自动安装。"然后进入步骤 2。

**如果选择"暂时不要"：** 写入具有递增退避的暂停状态（第一次暂停 = 24 小时，第二次 = 48 小时，第三次及以后 = 1 周），然后继续当前技能。不再提及升级。
```bash
_SNOOZE_FILE="$HOME/.gstack/update-snoozed"
_REMOTE_VER="{new}"
_CUR_LEVEL=0
if [ -f "$_SNOOZE_FILE" ]; then
  _SNOOZED_VER=$(awk '{print $1}' "$_SNOOZE_FILE")
  if [ "$_SNOOZED_VER" = "$_REMOTE_VER" ]; then
    _CUR_LEVEL=$(awk '{print $2}' "$_SNOOZE_FILE")
    case "$_CUR_LEVEL" in *[!0-9]*) _CUR_LEVEL=0 ;; esac
  fi
fi
_NEW_LEVEL=$((_CUR_LEVEL + 1))
[ "$_NEW_LEVEL" -gt 3 ] && _NEW_LEVEL=3
echo "$_REMOTE_VER $_NEW_LEVEL $(date +%s)" > "$_SNOOZE_FILE"
```
注意：`{new}` 是来自 `UPGRADE_AVAILABLE` 输出的远程版本 — 从更新检查结果中替换。

告诉用户暂停持续时间："下次提醒在 24 小时后"（或 48 小时或 1 周，取决于级别）。提示："在 `~/.gstack/config.yaml` 中设置 `auto_upgrade: true` 以实现自动升级。"

**如果选择"不再询问"：**
```bash
~/.claude/skills/gstack/bin/gstack-config set update_check false
```
告诉用户："已禁用更新检查。运行 `~/.claude/skills/gstack/bin/gstack-config set update_check true` 重新启用。"
继续当前技能。

### 步骤 2：检测安装类型

```bash
if [ -d "$HOME/.claude/skills/gstack/.git" ]; then
  INSTALL_TYPE="global-git"
  INSTALL_DIR="$HOME/.claude/skills/gstack"
elif [ -d "$HOME/.gstack/repos/gstack/.git" ]; then
  INSTALL_TYPE="global-git"
  INSTALL_DIR="$HOME/.gstack/repos/gstack"
elif [ -d ".claude/skills/gstack/.git" ]; then
  INSTALL_TYPE="local-git"
  INSTALL_DIR=".claude/skills/gstack"
elif [ -d ".agents/skills/gstack/.git" ]; then
  INSTALL_TYPE="local-git"
  INSTALL_DIR=".agents/skills/gstack"
elif [ -d ".claude/skills/gstack" ]; then
  INSTALL_TYPE="vendored"
  INSTALL_DIR=".claude/skills/gstack"
elif [ -d "$HOME/.claude/skills/gstack" ]; then
  INSTALL_TYPE="vendored-global"
  INSTALL_DIR="$HOME/.claude/skills/gstack"
else
  echo "ERROR: gstack not found"
  exit 1
fi
echo "Install type: $INSTALL_TYPE at $INSTALL_DIR"
```

上面输出的安装类型和目录路径将在所有后续步骤中使用。

### 步骤 3：保存旧版本

使用步骤 2 输出中的安装目录：

```bash
OLD_VERSION=$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "unknown")
```

### 步骤 4：升级

使用步骤 2 检测到的安装类型和目录：

**对于 git 安装**（global-git、local-git）：
```bash
cd "$INSTALL_DIR"
STASH_OUTPUT=$(git stash 2>&1)
git fetch origin
git reset --hard origin/main
./setup
```
如果 `$STASH_OUTPUT` 包含"Saved working directory"，警告用户："注意：本地更改已暂存。在技能目录中运行 `git stash pop` 以恢复它们。"

**对于本地安装**（vendored、vendored-global）：
```bash
PARENT=$(dirname "$INSTALL_DIR")
TMP_DIR=$(mktemp -d)
git clone --depth 1 https://github.com/garrytan/gstack.git "$TMP_DIR/gstack"
mv "$INSTALL_DIR" "$INSTALL_DIR.bak"
mv "$TMP_DIR/gstack" "$INSTALL_DIR"
cd "$INSTALL_DIR" && ./setup
rm -rf "$INSTALL_DIR.bak" "$TMP_DIR"
```

### 步骤 4.5：处理本地副本

使用步骤 2 的安装目录。检查是否还存在本地副本，以及团队模式是否激活：

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
LOCAL_GSTACK=""
if [ -n "$_ROOT" ] && [ -d "$_ROOT/.claude/skills/gstack" ]; then
  _RESOLVED_LOCAL=$(cd "$_ROOT/.claude/skills/gstack" && pwd -P)
  _RESOLVED_PRIMARY=$(cd "$INSTALL_DIR" && pwd -P)
  if [ "$_RESOLVED_LOCAL" != "$_RESOLVED_PRIMARY" ]; then
    LOCAL_GSTACK="$_ROOT/.claude/skills/gstack"
  fi
fi
_TEAM_MODE=$(~/.claude/skills/gstack/bin/gstack-config get team_mode 2>/dev/null || echo "false")
echo "LOCAL_GSTACK=$LOCAL_GSTACK"
echo "TEAM_MODE=$_TEAM_MODE"
```

**如果 `LOCAL_GSTACK` 非空且 `TEAM_MODE` 为 `true`：** 删除本地副本。团队模式使用全局安装作为唯一真实来源。

```bash
cd "$_ROOT"
git rm -r --cached .claude/skills/gstack/ 2>/dev/null || true
if ! grep -qF '.claude/skills/gstack/' .gitignore 2>/dev/null; then
  echo '.claude/skills/gstack/' >> .gitignore
fi
rm -rf "$LOCAL_GSTACK"
```
告诉用户："已删除 `$LOCAL_GSTACK` 处的本地副本（团队模式激活 — 全局安装是唯一真实来源）。准备好后提交 `.gitignore` 更改。"

**如果 `LOCAL_GSTACK` 非空且 `TEAM_MODE` 不为 `true`：** 通过从刚升级的主安装复制来更新它（与 README 本地安装方法相同）：
```bash
mv "$LOCAL_GSTACK" "$LOCAL_GSTACK.bak"
cp -Rf "$INSTALL_DIR" "$LOCAL_GSTACK"
rm -rf "$LOCAL_GSTACK/.git"
cd "$LOCAL_GSTACK" && ./setup
rm -rf "$LOCAL_GSTACK.bak"
```
告诉用户："已更新 `$LOCAL_GSTACK` 处的本地副本 — 准备好后提交 `.claude/skills/gstack/`。"

如果 `./setup` 失败，从备份恢复并警告用户：
```bash
rm -rf "$LOCAL_GSTACK"
mv "$LOCAL_GSTACK.bak" "$LOCAL_GSTACK"
```
告诉用户："同步失败 — 已恢复 `$LOCAL_GSTACK` 处的之前版本。请手动运行 `/gstack-upgrade` 重试。"

### 步骤 4.75：运行版本迁移

`./setup` 完成后，运行旧版本和新版本之间的任何迁移脚本。迁移处理 `./setup` 单独无法覆盖的状态修复（过时配置、孤立文件、目录结构更改）。

```bash
MIGRATIONS_DIR="$INSTALL_DIR/gstack-upgrade/migrations"
if [ -d "$MIGRATIONS_DIR" ]; then
  for migration in $(find "$MIGRATIONS_DIR" -maxdepth 1 -name 'v*.sh' -type f 2>/dev/null | sort -V); do
    # 从文件名提取版本：v0.15.2.0.sh → 0.15.2.0
    m_ver="$(basename "$migration" .sh | sed 's/^v//')"
    # 如果此迁移版本比旧版本更新则运行
    # （对于具有相同段数的点分版本，简单字符串比较有效）
    if [ "$OLD_VERSION" != "unknown" ] && [ "$(printf '%s\n%s' "$OLD_VERSION" "$m_ver" | sort -V | head -1)" = "$OLD_VERSION" ] && [ "$OLD_VERSION" != "$m_ver" ]; then
      echo "Running migration $m_ver..."
      bash "$migration" || echo "  Warning: migration $m_ver had errors (non-fatal)"
    fi
  done
fi
```

迁移是 `gstack-upgrade/migrations/` 中的幂等 bash 脚本。每个命名为
`v{VERSION}.sh`，仅在从旧版本升级时运行。有关如何添加新迁移，请参阅 CONTRIBUTING.md。

### 步骤 5：写入标记 + 清除缓存

```bash
mkdir -p ~/.gstack
echo "$OLD_VERSION" > ~/.gstack/just-upgraded-from
rm -f ~/.gstack/last-update-check
rm -f ~/.gstack/update-snoozed
```

### 步骤 6：显示更新内容

读取 `$INSTALL_DIR/CHANGELOG.md`。查找旧版本和新版本之间的所有版本条目。按主题分组总结为 5-7 个要点。不要过多 — 重点关注面向用户的更改。除非非常重要，否则跳过内部重构。

格式：
```
gstack v{new} — upgraded from v{old}!

What's new:
- [bullet 1]
- [bullet 2]
- ...

Happy shipping!
```

### 步骤 7：继续

显示更新内容后，继续用户最初调用的技能。升级完成 — 无需进一步操作。

---

## 独立使用

当直接作为 `/gstack-upgrade` 调用时（不是从前置脚本）：

1. 强制进行新的更新检查（绕过缓存）：
```bash
~/.claude/skills/gstack/bin/gstack-update-check --force 2>/dev/null || \
.claude/skills/gstack/bin/gstack-update-check --force 2>/dev/null || true
```
使用输出确定是否有可用升级。

2. 如果 `UPGRADE_AVAILABLE <old> <new>`：按照上面的步骤 2-6 操作。

3. 如果没有输出（主安装是最新的）：检查是否存在过时的本地副本。

运行上面步骤 2 的 bash 块以检测主安装类型和目录（`INSTALL_TYPE` 和 `INSTALL_DIR`）。然后运行上面步骤 4.5 的检测 bash 块以检查本地副本（`LOCAL_GSTACK`）和团队模式状态（`TEAM_MODE`）。

**如果 `LOCAL_GSTACK` 为空**（没有本地副本）：告诉用户"你已经在最新版本上（v{version}）。"

**如果 `LOCAL_GSTACK` 非空且 `TEAM_MODE` 为 `true`：** 使用上面步骤 4.5 的团队模式删除 bash 块删除本地副本。告诉用户："全局 v{version} 已是最新。已删除过时的本地副本（团队模式激活）。准备好后提交 `.gitignore` 更改。"

**如果 `LOCAL_GSTACK` 非空且 `TEAM_MODE` 不为 `true`**，比较版本：
```bash
PRIMARY_VER=$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "unknown")
LOCAL_VER=$(cat "$LOCAL_GSTACK/VERSION" 2>/dev/null || echo "unknown")
echo "PRIMARY=$PRIMARY_VER LOCAL=$LOCAL_VER"
```

**如果版本不同：** 按照上面步骤 4.5 的同步 bash 块从主安装更新本地副本。告诉用户："全局 v{PRIMARY_VER} 已是最新。已将本地副本从 v{LOCAL_VER} 更新到 v{PRIMARY_VER}。准备好后提交 `.claude/skills/gstack/`。"

**如果版本相同：** 告诉用户"你已在最新版本上（v{PRIMARY_VER}）。全局和本地副本都是最新的。"
