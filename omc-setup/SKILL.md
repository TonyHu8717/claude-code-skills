---
name: omc-setup
description: 从标准设置流程安装或刷新 oh-my-claudecode，支持插件、npm 和本地开发设置
level: 2
---

# OMC 设置

这是**你唯一需要学习的命令**。运行此命令后，其他一切都是自动的。

**当此技能被调用时，立即执行以下工作流。不要仅向用户复述或总结这些指令。**

注意：本指南中所有 `~/.claude/...` 路径在设置了 `CLAUDE_CONFIG_DIR` 环境变量时会遵循该变量。

## 最佳使用场景

当用户想要**安装、刷新或修复 OMC 本身**时，选择此设置流程。

- 市场/插件安装用户应在 `/plugin install oh-my-claudecode` 后到达此处
- npm 用户应在 `npm i -g oh-my-claude-sisyphus@latest` 后到达此处
- 本地开发和工作树用户应在更新检出的仓库并重新运行设置后到达此处

## 标志解析

检查用户调用中的标志：
- `--help` → 显示帮助文本（如下）并停止
- `--local` → 仅阶段 1（target=local），然后停止
- `--global` → 仅阶段 1（target=global），然后停止
- `--force` → 跳过预设置检查，运行完整设置（阶段 1 → 2 → 3 → 4）
- 无标志 → 运行预设置检查，然后在需要时运行完整设置

## 帮助文本

当用户使用 `--help` 运行时，显示此内容并停止：

```
OMC 设置 - 配置 oh-my-claudecode

用法：
  /oh-my-claudecode:omc-setup           运行初始设置向导（如果已配置则更新）
  /oh-my-claudecode:omc-setup --local   配置本地项目（.claude/CLAUDE.md）
  /oh-my-claudecode:omc-setup --global  配置全局设置（~/.claude/CLAUDE.md）
  /oh-my-claudecode:omc-setup --force   即使已配置也强制运行完整设置向导
  /oh-my-claudecode:omc-setup --help    显示此帮助

模式：
  初始设置（无标志）
    - 首次设置的交互式向导
    - 配置 CLAUDE.md（本地或全局）
    - 设置 HUD 状态行
    - 检查更新
    - 提供 MCP 服务器配置
    - 配置团队模式默认值（代理数量、类型、模型）
    - 如果已配置，提供快速更新选项

  本地配置（--local）
    - 下载新的 CLAUDE.md 到 ./.claude/
    - 将现有 CLAUDE.md 备份到 .claude/CLAUDE.md.backup.YYYY-MM-DD
    - 项目特定设置
    - 在 OMC 升级后使用此选项更新项目配置

  全局配置（--global）
    - 下载新的 CLAUDE.md 到 ~/.claude/
    - 将现有 CLAUDE.md 备份到 ~/.claude/CLAUDE.md.backup.YYYY-MM-DD
    - 默认：显式覆盖 ~/.claude/CLAUDE.md，使普通的 `claude` 也使用 OMC
    - 可选保留模式保留用户的基础 `CLAUDE.md` 并将 OMC 安装到 `CLAUDE-omc.md` 供 `omc` 启动使用
    - 应用于所有 Claude Code 会话
    - 清理遗留钩子
    - 在 OMC 升级后使用此选项更新全局配置

  强制完整设置（--force）
    - 绕过"已配置"检查
    - 从头运行完整的设置向导
    - 当你想重新配置偏好时使用

示例：
  /oh-my-claudecode:omc-setup           # 首次设置（或如果已配置则更新 CLAUDE.md）
  /oh-my-claudecode:omc-setup --local   # 更新此项目
  /oh-my-claudecode:omc-setup --global  # 更新所有项目
  /oh-my-claudecode:omc-setup --force   # 重新运行完整设置向导

更多信息：https://github.com/Yeachan-Heo/oh-my-claudecode
```

## 预设置检查：是否已配置？

**关键**：在做任何其他事情之前，检查设置是否已完成。这可以防止用户在每次更新后都必须重新运行完整的设置向导。

```bash
# 检查设置是否已完成
CONFIG_FILE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.omc-config.json"

if [ -f "$CONFIG_FILE" ]; then
  SETUP_COMPLETED=$(jq -r '.setupCompleted // empty' "$CONFIG_FILE" 2>/dev/null)
  SETUP_VERSION=$(jq -r '.setupVersion // empty' "$CONFIG_FILE" 2>/dev/null)

  if [ -n "$SETUP_COMPLETED" ] && [ "$SETUP_COMPLETED" != "null" ]; then
    echo "OMC setup was already completed on: $SETUP_COMPLETED"
    [ -n "$SETUP_VERSION" ] && echo "Setup version: $SETUP_VERSION"
    ALREADY_CONFIGURED="true"
  fi
fi
```

### 如果已配置（且无 --force 标志）

如果 `ALREADY_CONFIGURED` 为 true 且用户未传递 `--force`、`--local` 或 `--global` 标志：

使用 AskUserQuestion 提示：

**问题：** "OMC 已经配置。你想做什么？"

**选项：**
1. **仅更新 CLAUDE.md** - 下载最新的 CLAUDE.md，不重新运行完整设置
2. **重新运行完整设置** - 完成完整的设置向导
3. **取消** - 退出不做更改

**如果用户选择"仅更新 CLAUDE.md"：**
- 检测是否存在本地（.claude/CLAUDE.md）或全局（~/.claude/CLAUDE.md）配置
- 如果存在本地配置，运行：`bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-claude-md.sh" local`
- 如果仅存在全局配置，运行：`bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-claude-md.sh" global`
- 跳过所有其他步骤
- 报告成功并退出

**如果用户选择"重新运行完整设置"：**
- 继续下面的恢复检测

**如果用户选择"取消"：**
- 退出不做任何更改

### 强制标志覆盖

如果用户传递 `--force` 标志，跳过此检查直接进入设置。

## 恢复检测

在开始任何阶段之前，检查现有状态：

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-progress.sh" resume
```

如果状态存在（输出不是"fresh"），使用 AskUserQuestion 提示：

**问题：** "找到之前的设置会话。你想恢复还是重新开始？"

**选项：**
1. **从步骤 $LAST_STEP 恢复** - 从中断处继续
2. **重新开始** - 从头开始（清除保存的状态）

如果用户选择"重新开始"：
```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-progress.sh" clear
```

## 阶段执行

### 对于 `--local` 或 `--global` 标志：
读取 `${CLAUDE_PLUGIN_ROOT}/skills/omc-setup/phases/01-install-claude-md.md` 文件并按照其指令操作。
（阶段文件处理标志模式的提前退出。）

### 对于完整设置（默认或 --force）：
按顺序执行阶段。对于每个阶段，读取相应文件并按照其指令操作：

1. **阶段 1 - 安装 CLAUDE.md**：读取 `${CLAUDE_PLUGIN_ROOT}/skills/omc-setup/phases/01-install-claude-md.md` 并按照其指令操作。

2. **阶段 2 - 环境配置**：读取 `${CLAUDE_PLUGIN_ROOT}/skills/omc-setup/phases/02-configure.md` 并按照其指令操作。阶段 2 必须将 HUD/statusLine 设置委托给 `hud` 技能；不要在此内联生成或修补 `statusLine` 路径。

3. **阶段 3 - 集成设置**：读取 `${CLAUDE_PLUGIN_ROOT}/skills/omc-setup/phases/03-integrations.md` 并按照其指令操作。

4. **阶段 4 - 完成**：读取 `${CLAUDE_PLUGIN_ROOT}/skills/omc-setup/phases/04-welcome.md` 并按照其指令操作。

## 优雅的中断处理

**重要**：此设置过程通过 `${CLAUDE_PLUGIN_ROOT}/scripts/setup-progress.sh` 在每个阶段后保存进度。如果中断（Ctrl+C 或连接丢失），设置可以从中断处恢复。

## 保持最新

安装 oh-my-claudecode 更新后（通过 npm 或插件更新）：

**自动**：只需运行 `/oh-my-claudecode:omc-setup` - 它会检测你已经配置过，并提供快速"仅更新 CLAUDE.md"选项，跳过完整向导。

**手动选项**：
- `/oh-my-claudecode:omc-setup --local` 仅更新项目配置
- `/oh-my-claudecode:omc-setup --global` 仅更新全局配置
- `/oh-my-claudecode:omc-setup --force` 重新运行完整向导（重新配置偏好）

这确保你拥有最新的功能和代理配置，而无需承担重复完整设置的 token 成本。
