---
name: mcp-setup
description: 配置常用的 MCP 服务器以增强代理能力
level: 2
---

# MCP 设置

配置模型上下文协议（MCP）服务器，通过外部工具（如网页搜索、文件系统访问和 GitHub 集成）扩展 Claude Code 的能力。

## 概述

MCP 服务器提供 Claude Code 代理可以使用的额外工具。此技能帮助你使用 `claude mcp add` 命令行界面配置常用的 MCP 服务器。

## 步骤 1：选择设置路径

使用 **AskUserQuestion**，**一次一个问题**，**每个问题不超过 3 个选项**。最近的 Claude Code 构建版本会拒绝较大的选项负载作为无效工具参数，因此保持 MCP 选择流程分阶段进行。

### 步骤 1.1：第一个菜单

**问题：** "你想要哪种 MCP 设置？"

**选项：**
1. **推荐入门设置** - 最常见 OMC MCP 附加组件的快速路径
2. **单个常用服务器** - 从简短的后续菜单中选择一个内置服务器
3. **自定义服务器** - 添加你自己的 stdio 或 HTTP MCP 服务器

### 步骤 1.2：如果用户选择"推荐入门设置"

询问后续 **AskUserQuestion**：

**问题：** "我应该配置哪个推荐的 MCP 包？"

**选项：**
1. **仅 Context7（推荐）** - 零配置文档/上下文服务器
2. **Context7 + Exa** - 文档/上下文加增强网页搜索
3. **完整推荐包** - Context7、Exa、Filesystem 和 GitHub

将该选择映射到你将配置的服务器列表。

### 步骤 1.3：如果用户选择"单个常用服务器"

询问后续 **AskUserQuestion**：

**问题：** "我应该先配置哪个服务器？"

**选项：**
1. **Context7（推荐）** - 来自流行库的文档和代码上下文
2. **Exa 网页搜索** - 增强网页搜索（替代内置 websearch）
3. **更多服务器选择** - Filesystem、GitHub 或完整推荐包

如果用户选择**更多服务器选择**，再询问一个 **AskUserQuestion**：

**问题：** "你想要哪个额外的 MCP 选项？"

**选项：**
1. **Filesystem（推荐）** - 具有额外能力的扩展文件系统访问
2. **GitHub** - 用于 issues、PRs 和仓库管理的 GitHub API 集成
3. **完整推荐包** - 同时配置 Context7、Exa、Filesystem 和 GitHub

### 步骤 1.4：如果用户选择"自定义服务器"

直接跳转到下方的**自定义 MCP 服务器**部分。

## 步骤 2：收集所需信息

### 对于 Context7：
无需 API 密钥。可立即使用。

### 对于 Exa 网页搜索：
询问 API 密钥：
```
你有 Exa API 密钥吗？
- 在此获取：https://exa.ai
- 输入你的 API 密钥，或输入 'skip' 稍后配置
```

### 对于 Filesystem：
询问允许的目录：
```
Filesystem MCP 应该访问哪些目录？
默认：当前工作目录
输入逗号分隔的路径，或按 Enter 使用默认值
```

### 对于 GitHub：
询问 token：
```
你有 GitHub 个人访问令牌吗？
- 在此创建：https://github.com/settings/tokens
- 推荐权限：repo、read:org
- 输入你的令牌，或输入 'skip' 稍后配置
```

## 步骤 3：使用 CLI 添加 MCP 服务器

使用 `claude mcp add` 命令配置每个 MCP 服务器。CLI 自动处理 settings.json 更新和合并。

### Context7 配置：
```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

### Exa 网页搜索配置：
```bash
claude mcp add -e EXA_API_KEY=<user-provided-key> exa -- npx -y exa-mcp-server
```

### Filesystem 配置：
```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem <allowed-directories>
```

### GitHub 配置：

**选项 1：Docker（本地）**
```bash
claude mcp add -e GITHUB_PERSONAL_ACCESS_TOKEN=<user-provided-token> github -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

**选项 2：HTTP（远程）**
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

> 注意：Docker 选项需要安装 Docker。HTTP 选项更简单但可能有不同的能力。

## 步骤 4：验证安装

配置后，验证 MCP 服务器是否正确设置：

```bash
# 列出已配置的 MCP 服务器
claude mcp list
```

这将显示所有已配置的 MCP 服务器及其状态。

## 步骤 5：显示完成消息

```
MCP 服务器配置完成！

已配置的服务器：
[列出已配置的服务器]

后续步骤：
1. 重启 Claude Code 使更改生效
2. 配置的 MCP 工具将对所有代理可用
3. 运行 `claude mcp list` 验证配置

使用提示：
- Context7：询问库文档（例如，"如何使用 React hooks？"）
- Exa：用于网页搜索（例如，"搜索最新的 TypeScript 特性"）
- Filesystem：超越工作目录的扩展文件操作
- GitHub：与 GitHub 仓库、issues 和 PRs 交互

故障排除：
- 如果 MCP 服务器未出现，运行 `claude mcp list` 检查状态
- 确保已安装 Node.js 18+ 以使用基于 npx 的服务器
- 对于 GitHub Docker 选项，确保 Docker 已安装并运行
- 运行 /oh-my-claudecode:omc-doctor 诊断问题

管理 MCP 服务器：
- 添加更多服务器：/oh-my-claudecode:mcp-setup 或 `claude mcp add ...`
- 列出服务器：`claude mcp list`
- 移除服务器：`claude mcp remove <server-name>`
```

## 自定义 MCP 服务器

如果用户选择"自定义"：

询问：
1. 服务器名称（标识符）
2. 传输类型：`stdio`（默认）或 `http`
3. 对于 stdio：命令和参数（例如，`npx my-mcp-server`）
4. 对于 http：URL（例如，`https://example.com/mcp`）
5. 环境变量（可选，key=value 对）
6. HTTP 头部（可选，仅用于 http 传输）

然后构造并运行适当的 `claude mcp add` 命令：

**对于 stdio 服务器：**
```bash
# 不带环境变量
claude mcp add <server-name> -- <command> [args...]

# 带环境变量
claude mcp add -e KEY1=value1 -e KEY2=value2 <server-name> -- <command> [args...]
```

**对于 HTTP 服务器：**
```bash
# 基本 HTTP 服务器
claude mcp add --transport http <server-name> <url>

# 带头部的 HTTP 服务器
claude mcp add --transport http --header "Authorization: Bearer <token>" <server-name> <url>
```

### 公司上下文约定

如果自定义服务器旨在为 OMC 工作流提供组织特定的参考材料，优先使用名为 `get_company_context` 的单个工具，通过 `{ context: string }` 返回 Markdown。

本地注册示例：

```bash
claude mcp add company-context -- node examples/vendor-mcp-server/server.mjs
```

然后在 `.claude/omc.jsonc` 或 `~/.config/claude-omc/config.jsonc` 中将 OMC 指向完整工具名称：

```jsonc
{
  "companyContext": {
    "tool": "mcp__company-context__get_company_context",
    "onError": "warn"
  }
}
```

这仍然是建议性提示上下文，而非运行时强制执行。

## 常见问题

### MCP 服务器未加载
- 确保已安装 Node.js 18+
- 检查 npx 是否在 PATH 中可用
- 运行 `claude mcp list` 验证服务器状态
- 检查服务器日志中的错误

### API 密钥问题
- Exa：在 https://dashboard.exa.ai 验证密钥
- GitHub：确保令牌具有所需权限（repo、read:org）
- 如有需要，使用正确凭据重新运行 `claude mcp add`

### 代理仍使用内置工具
- 配置后重启 Claude Code
- 配置 exa 后，内置 websearch 将被降低优先级
- 运行 `claude mcp list` 确认服务器处于活动状态

### 移除或更新服务器
- 移除：`claude mcp remove <server-name>`
- 更新：移除旧服务器，然后使用新配置重新添加