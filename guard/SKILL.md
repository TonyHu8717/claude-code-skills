---
name: guard
version: 0.1.0
description: |
  完整安全模式：破坏性命令警告 + 目录范围编辑限制。
  结合 /careful（在 rm -rf、DROP TABLE、force-push 等操作前发出警告）和
  /freeze（阻止指定目录外的编辑）。在接触生产环境或调试线上系统时使用，
  以获得最大安全性。当用户要求"guard mode"、"full safety"、"lock it down"
  或"maximum safety"时使用。(gstack)
triggers:
  - full safety mode
  - guard against mistakes
  - maximum safety
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../careful/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /guard — 完整安全模式

同时激活破坏性命令警告和目录范围编辑限制。
这是 `/careful` + `/freeze` 的组合，通过单个命令启用。

**依赖说明：** 此技能引用了兄弟目录 `/careful` 和 `/freeze` 技能中的钩子脚本。两者都必须已安装（它们由 gstack 安装脚本一起安装）。

```bash
mkdir -p ~/.gstack/analytics
echo '{"skill":"guard","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 设置

询问用户要将编辑限制在哪个目录。使用 AskUserQuestion：

- 问题："Guard mode：编辑应限制在哪个目录？破坏性命令警告始终开启。选定路径外的文件将被阻止编辑。"
- 文本输入（非多选）——用户输入路径。

用户提供目录路径后：

1. 将其解析为绝对路径：
```bash
FREEZE_DIR=$(cd "<user-provided-path>" 2>/dev/null && pwd)
echo "$FREEZE_DIR"
```

2. 确保尾部斜杠并保存到冻结状态文件：
```bash
FREEZE_DIR="${FREEZE_DIR%/}/"
STATE_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.gstack}"
mkdir -p "$STATE_DIR"
echo "$FREEZE_DIR" > "$STATE_DIR/freeze-dir.txt"
echo "Freeze boundary set: $FREEZE_DIR"
```

告知用户：
- "**Guard mode 已激活。** 现在运行两项保护："
- "1. **破坏性命令警告** — rm -rf、DROP TABLE、force-push 等操作执行前会发出警告（你可以覆盖）"
- "2. **编辑边界** — 文件编辑限制在 `<path>/` 内。此目录外的编辑将被阻止。"
- "要移除编辑边界，请运行 `/unfreeze`。要完全停用，请结束会话。"

## 受保护内容

参见 `/careful` 了解破坏性命令模式和安全例外的完整列表。
参见 `/freeze` 了解编辑边界强制执行的工作原理。
