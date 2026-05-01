---
name: block-no-verify-hook
description: 配置 PreToolUse 钩子，防止 AI 代理使用 --no-verify 和其他绕过标志跳过 git pre-commit 钩子。适用于需要强制执行提交质量门禁的 Claude Code 项目。
---

# 阻止 No-Verify 钩子

PreToolUse 钩子配置，可在执行前拦截并阻止绕过标志的使用，确保 AI 代理无法跳过 pre-commit 钩子、GPG 签名或其他 git 安全机制。

## 概述

AI 编码代理（Claude Code、Codex 等）可以运行带有 `--no-verify` 等标志的 shell 命令来绕过 pre-commit 钩子。这会使 pre-commit 钩子中配置的代码检查、格式化、测试和安全检查失效。block-no-verify 钩子添加了一个 PreToolUse 守卫，在执行前拒绝任何包含绕过标志的工具调用。

## 问题

当 AI 代理提交代码时，可能会使用绕过标志来避免钩子失败：

```bash
# 这些命令会完全跳过 pre-commit 钩子
git commit --no-verify -m "quick fix"
git push --no-verify
git commit --no-gpg-sign -m "unsigned commit"
git merge --no-verify feature-branch
```

这会导致：
- 未格式化的代码进入仓库
- 代码检查错误绕过检查
- 安全扫描被跳过
- 未签名的提交绕过签名策略
- 测试套件被规避

## 解决方案

在 `.claude/settings.json` 中添加 `PreToolUse` 钩子，检查每个 Bash 工具调用并阻止包含绕过标志的命令。

### 配置

在项目的 `.claude/settings.json` 中添加以下内容：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

### 工作原理

1. **匹配器**：钩子仅针对 `Bash` 工具调用，因此不会干扰其他工具（Read、Edit、Grep 等）。
2. **检查**：`$TOOL_INPUT` 环境变量包含代理即将执行的完整命令。钩子使用 `printf` 安全传递输入（避免 `echo` 对特殊字符的处理问题），并仅在前面有 `git` 命令时检查 `--no-verify` 或 `--no-gpg-sign` 标志。
3. **阻止**：如果在 git 命令中发现绕过标志，钩子将以退出码 2 退出并打印错误消息。退出码 2 表示 Claude Code 应完全拒绝该工具调用。
4. **放行**：如果未发现绕过标志，钩子以退出码 0 退出，命令正常执行。

### 退出码

| 代码 | 含义 |
|------|------|
| 0 | 允许工具调用继续 |
| 1 | 错误（工具调用仍继续，显示警告） |
| 2 | 完全阻止工具调用 |

## 被阻止的标志

| 标志 | 用途 | 阻止原因 |
|------|------|----------|
| `--no-verify` | 跳过 pre-commit 和 commit-msg 钩子 | 绕过代码检查、格式化、测试、安全检查 |
| `--no-gpg-sign` | 跳过 GPG 提交签名 | 绕过提交签名策略 |

## 安装

### 项目级设置

在项目根目录创建或更新 `.claude/settings.json`：

```bash
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
EOF
```

### 全局设置

要在所有项目中强制执行，添加到 `~/.claude/settings.json`：

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
EOF
```

## 验证

测试钩子是否阻止绕过标志：

```bash
# 这应该被钩子阻止：
git commit --no-verify -m "test"

# 这应该正常成功：
git commit -m "test"
```

## 扩展钩子

### 添加更多被阻止的标志

要阻止其他标志（例如 `--force`），扩展 grep 模式：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign|force-with-lease|force)'; then echo 'BLOCKED: Bypass flags are not allowed.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

### 与其他钩子组合

block-no-verify 钩子可与其他 PreToolUse 钩子并行工作：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: Bypass flags not allowed.' >&2; exit 2; fi"
        }
      },
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE 'rm\\s+-rf\\s+/'; then echo 'BLOCKED: Dangerous rm command.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

## 最佳实践

1. **提交设置文件** — 将 `.claude/settings.json` 添加到版本控制，让所有团队成员受益于该钩子。
2. **在入门文档中说明** — 在项目的贡献指南中提及该钩子，让开发者了解为什么绕过标志被阻止。
3. **与 pre-commit 钩子配合** — block-no-verify 钩子确保 pre-commit 钩子运行；确保你配置了有意义的 pre-commit 钩子。
4. **设置后测试** — 通过在测试提交中故意触发来验证钩子是否正常工作。
