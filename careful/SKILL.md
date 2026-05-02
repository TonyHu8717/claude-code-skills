---
name: careful
version: 0.1.0
description: |
  破坏性命令安全防护栏。在 rm -rf、DROP TABLE、force-push、git reset --hard、
  kubectl delete 及类似破坏性操作前发出警告。用户可以覆盖每个警告。
  在操作生产环境、调试在线系统或在共享环境中工作时使用。
  当用户要求"小心"、"安全模式"、"生产模式"或"谨慎模式"时触发。(gstack)
triggers:
  - be careful
  - warn before destructive
  - safety mode
allowed-tools:
  - Bash
  - Read
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /careful — 破坏性命令防护栏

安全模式现已**激活**。每条 bash 命令在运行前都会检查破坏性模式。
如果检测到破坏性命令，您将收到警告并可以选择继续或取消。

```bash
mkdir -p ~/.gstack/analytics
echo '{"skill":"careful","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 受保护的模式

| 模式 | 示例 | 风险 |
|------|------|------|
| `rm -rf` / `rm -r` / `rm --recursive` | `rm -rf /var/data` | 递归删除 |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | 数据丢失 |
| `TRUNCATE` | `TRUNCATE orders;` | 数据丢失 |
| `git push --force` / `-f` | `git push -f origin master` | 历史重写 |
| `git reset --hard` | `git reset --hard HEAD~3` | 未提交工作丢失 |
| `git checkout .` / `git restore .` | `git checkout .` | 未提交工作丢失 |
| `kubectl delete` | `kubectl delete pod` | 生产影响 |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | 容器/镜像丢失 |

## 安全例外

以下模式允许无警告执行：
- `rm -rf node_modules` / `.next` / `dist` / `__pycache__` / `.cache` / `build` / `.turbo` / `coverage`

## 工作原理

钩子从工具输入 JSON 中读取命令，根据上述模式进行检查，
如果匹配则返回 `permissionDecision: "ask"` 及警告信息。
您始终可以覆盖警告继续执行。

要停用，请结束对话或开始新对话。钩子仅在会话范围内有效。
