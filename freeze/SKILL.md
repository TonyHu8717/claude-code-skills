---
name: freeze
version: 0.1.0
description: |
  将文件编辑限制在特定目录内。阻止对允许路径之外的文件进行 Edit 和
  Write 操作。在调试时用于防止意外"修复"无关代码，或在需要将更改
  范围限定在一个模块时使用。
  当要求"冻结"、"限制编辑"、"仅编辑此文件夹"或"锁定编辑"时使用。(gstack)
triggers:
  - freeze edits to directory
  - lock editing scope
  - restrict file changes
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /freeze — 将编辑限制在目录内

将文件编辑锁定在特定目录内。任何针对允许路径之外文件的 Edit 或 Write 操作将被**阻止**（不仅仅是警告）。

```bash
mkdir -p ~/.gstack/analytics
echo '{"skill":"freeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 设置

询问用户要将编辑限制到哪个目录。使用 AskUserQuestion：

- 问题："我应该将编辑限制到哪个目录？此路径之外的文件将被阻止编辑。"
- 文本输入（非多选）- 用户输入路径。

一旦用户提供目录路径：

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

告诉用户："编辑现在限制在 `<path>/` 内。此目录之外的任何 Edit 或 Write 将被阻止。要更改边界，请再次运行 `/freeze`。要移除它，请运行 `/unfreeze` 或结束会话。"

## 工作原理

钩子从 Edit/Write 工具输入 JSON 中读取 `file_path`，然后检查路径是否以冻结目录开头。如果不是，它返回 `permissionDecision: "deny"` 来阻止操作。

冻结边界通过状态文件在会话期间持续存在。钩子脚本在每次 Edit/Write 调用时读取它。

## 注意事项

- 冻结目录上的尾部 `/` 防止 `/src` 匹配 `/src-old`
- 冻结仅适用于 Edit 和 Write 工具 - Read、Bash、Glob、Grep 不受影响
- 这防止意外编辑，而不是安全边界 - Bash 命令如 `sed` 仍然可以修改边界之外的文件
- 要停用，请运行 `/unfreeze` 或结束对话
