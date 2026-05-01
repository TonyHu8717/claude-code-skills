---
name: setup
description: 首次使用时进行安装/更新路由 — 将 setup、doctor 或 MCP 请求发送到正确的 OMC 设置流程
level: 2
---

# Setup

使用 `/oh-my-claudecode:setup` 作为统一的设置/配置入口。

## 用法

```bash
/oh-my-claudecode:setup                # 完整设置向导
/oh-my-claudecode:setup doctor         # 安装诊断
/oh-my-claudecode:setup mcp            # MCP 服务器配置
/oh-my-claudecode:setup wizard --local # 明确的向导路径
```

## 路由

仅根据**第一个参数**处理请求，以便安装/设置问题立即进入正确的流程：

- 无参数、`wizard`、`local`、`global` 或 `--force` -> 路由到 `/oh-my-claudecode:omc-setup`，保留相同剩余参数
- `doctor` -> 路由到 `/oh-my-claudecode:omc-doctor`，传递 `doctor` 之后的所有内容
- `mcp` -> 路由到 `/oh-my-claudecode:mcp-setup`，传递 `mcp` 之后的所有内容

示例：

```bash
/oh-my-claudecode:setup --local          # => /oh-my-claudecode:omc-setup --local
/oh-my-claudecode:setup doctor --json    # => /oh-my-claudecode:omc-doctor --json
/oh-my-claudecode:setup mcp github       # => /oh-my-claudecode:mcp-setup github
```

## 备注

- `/oh-my-claudecode:omc-setup`、`/oh-my-claudecode:omc-doctor` 和 `/oh-my-claudecode:mcp-setup` 仍然是有效的兼容入口。
- 在新文档和用户指南中优先使用 `/oh-my-claudecode:setup`。

Task: {{ARGUMENTS}}
