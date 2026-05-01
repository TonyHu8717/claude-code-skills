---
name: unfreeze
version: 0.1.0
description: |
  清除 /freeze 设置的冻结边界，允许再次编辑所有目录。
  当你想在不结束会话的情况下扩大编辑范围时使用。
  当被要求"解冻"、"解锁编辑"、"移除冻结"或"允许所有编辑"时使用。(gstack)
triggers:
  - unfreeze edits
  - unlock all directories
  - remove edit restrictions
allowed-tools:
  - Bash
  - Read
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /unfreeze — 清除冻结边界

移除 `/freeze` 设置的编辑限制，允许编辑所有目录。

```bash
mkdir -p ~/.gstack/analytics
echo '{"skill":"unfreeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 清除边界

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.gstack}"
if [ -f "$STATE_DIR/freeze-dir.txt" ]; then
  PREV=$(cat "$STATE_DIR/freeze-dir.txt")
  rm -f "$STATE_DIR/freeze-dir.txt"
  echo "Freeze boundary cleared (was: $PREV). Edits are now allowed everywhere."
else
  echo "No freeze boundary was set."
fi
```

告知用户结果。请注意，`/freeze` 钩子仍在会话中注册——由于没有状态文件存在，它们将允许所有操作。要重新冻结，请再次运行 `/freeze`。
