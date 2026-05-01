---
name: ask
description: 通过 `omc ask` 为 Claude、Codex 或 Gemini 提供流程优先的顾问路由，支持产物捕获，无需手动组装 CLI 命令
---

# Ask

使用 OMC 的标准顾问技能，通过本地 Claude、Codex 或 Gemini CLI 路由提示，并将结果持久化为 ask 产物。

## 用法

```bash
/oh-my-claudecode:ask <claude|codex|gemini> <question or task>
```

示例：

```bash
/oh-my-claudecode:ask codex "review this patch from a security perspective"
/oh-my-claudecode:ask gemini "suggest UX improvements for this flow"
/oh-my-claudecode:ask claude "draft an implementation plan for issue #123"
```

## 路由

**必需的执行路径 — 始终使用此命令：**

```bash
omc ask {{ARGUMENTS}}
```

**不要手动构建原始提供商 CLI 命令。** 永远不要直接运行 `codex`、`claude` 或 `gemini` 来执行此技能。`omc ask` 封装器会自动处理正确的标志选择、产物持久化和提供商版本兼容性。手动组装提供商 CLI 标志会产生不正确或过时的调用。

## 要求

- 所选的本地 CLI 必须已安装并完成身份验证。
- 使用以下命令验证可用性：

```bash
claude --version
codex --version
gemini --version
```

## 产物

`omc ask` 将产物写入：

```text
.omc/artifacts/ask/<provider>-<slug>-<timestamp>.md
```

Task: {{ARGUMENTS}}
