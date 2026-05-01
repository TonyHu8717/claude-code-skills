---
name: mcp-integration
description: 当用户要求"添加 MCP 服务器"、"集成 MCP"、"在插件中配置 MCP"、"使用 .mcp.json"、"设置模型上下文协议"、"连接外部服务"、提到 "${CLAUDE_PLUGIN_ROOT} 与 MCP"，或讨论 MCP 服务器类型（SSE、stdio、HTTP、WebSocket）时使用此技能。提供将模型上下文协议服务器集成到 Claude Code 插件中以连接外部工具和服务的全面指导。
version: 0.1.0
---

# Claude Code 插件的 MCP 集成

## 概述

模型上下文协议（MCP）使 Claude Code 插件能够通过提供结构化的工具访问来与外部服务和 API 集成。使用 MCP 集成将外部服务功能暴露为 Claude Code 中的工具。

**核心能力：**
- 连接外部服务（数据库、API、文件系统）
- 从单个服务提供 10+ 个相关工具
- 处理 OAuth 和复杂的身份验证流程
- 将 MCP 服务器与插件捆绑，实现自动设置

## MCP 服务器配置方法

插件可以通过两种方式捆绑 MCP 服务器：

### 方法 1：专用 .mcp.json（推荐）

在插件根目录创建 `.mcp.json`：

```json
{
  "database-tools": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

**优势：**
- 关注点清晰分离
- 更易维护
- 适合多服务器场景

### 方法 2：内联在 plugin.json 中

在 plugin.json 中添加 `mcpServers` 字段：

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**优势：**
- 单一配置文件
- 适合简单的单服务器插件

## MCP 服务器类型

### stdio（本地进程）

将本地 MCP 服务器作为子进程执行。最适合本地工具和自定义服务器。

**配置：**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": {
      "LOG_LEVEL": "debug"
    }
  }
}
```

**使用场景：**
- 文件系统访问
- 本地数据库连接
- 自定义 MCP 服务器
- NPM 打包的 MCP 服务器

**进程管理：**
- Claude Code 生成并管理进程
- 通过 stdin/stdout 通信
- Claude Code 退出时终止

### SSE（服务器发送事件）

连接到支持 OAuth 的托管 MCP 服务器。最适合云服务。

**配置：**
```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

**使用场景：**
- 官方托管的 MCP 服务器（Asana、GitHub 等）
- 具有 MCP 端点的云服务
- 基于 OAuth 的身份验证
- 无需本地安装

**身份验证：**
- OAuth 流程自动处理
- 首次使用时提示用户
- Token 由 Claude Code 管理

### HTTP（REST API）

连接到使用 Token 身份验证的 RESTful MCP 服务器。

**配置：**
```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Custom-Header": "value"
    }
  }
}
```

**使用场景：**
- 基于 REST API 的 MCP 服务器
- 基于 Token 的身份验证
- 自定义 API 后端
- 无状态交互

### WebSocket（实时）

连接到 WebSocket MCP 服务器，实现实时双向通信。

**配置：**
```json
{
  "realtime-service": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}"
    }
  }
}
```

**使用场景：**
- 实时数据流
- 持久连接
- 服务器推送通知
- 低延迟需求

## 环境变量展开

所有 MCP 配置支持环境变量替换：

**${CLAUDE_PLUGIN_ROOT}** — 插件目录（始终使用以保证可移植性）：
```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server"
}
```

**用户环境变量** — 来自用户的 shell：
```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}",
    "DATABASE_URL": "${DB_URL}"
  }
}
```

**最佳实践：**在插件 README 中记录所有必需的环境变量。

## MCP 工具命名

当 MCP 服务器提供工具时，它们会自动添加前缀：

**格式：**`mcp__plugin_<plugin-name>_<server-name>__<tool-name>`

**示例：**
- 插件：`asana`
- 服务器：`asana`
- 工具：`create_task`
- **全名：**`mcp__plugin_asana_asana__asana_create_task`

### 在命令中使用 MCP 工具

在命令 frontmatter 中预先允许特定的 MCP 工具：

```markdown
---
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task",
  "mcp__plugin_asana_asana__asana_search_tasks"
]
---
```

**通配符（谨慎使用）：**
```markdown
---
allowed-tools: ["mcp__plugin_asana_asana__*"]
---
```

**最佳实践：**为安全起见，预先允许特定工具，而非通配符。

## 生命周期管理

**自动启动：**
- 插件启用时 MCP 服务器启动
- 首次使用工具前建立连接
- 配置更改后需要重启

**生命周期：**
1. 插件加载
2. MCP 配置解析
3. 服务器进程启动（stdio）或连接建立（SSE/HTTP/WS）
4. 工具发现并注册
5. 工具以 `mcp__plugin_...__...` 形式可用

**查看服务器：**
使用 `/mcp` 命令查看所有服务器，包括插件提供的服务器。

## 身份验证模式

### OAuth（SSE/HTTP）

OAuth 由 Claude Code 自动处理：

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse"
}
```

首次使用时用户在浏览器中进行身份验证。无需额外配置。

### 基于 Token（Headers）

静态或环境变量 Token：

```json
{
  "type": "http",
  "url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

在 README 中记录所需的环境变量。

### 环境变量（stdio）

将配置传递给 MCP 服务器：

```json
{
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "DATABASE_URL": "${DB_URL}",
    "API_KEY": "${API_KEY}",
    "LOG_LEVEL": "info"
  }
}
```

## 集成模式

### 模式 1：简单工具包装

命令使用 MCP 工具并配合用户交互：

```markdown
# 命令：create-item.md
---
allowed-tools: ["mcp__plugin_name_server__create_item"]
---

步骤：
1. 从用户收集项目详情
2. 使用 mcp__plugin_name_server__create_item
3. 确认创建
```

**适用于：**在 MCP 调用前添加验证或预处理。

### 模式 2：自主 Agent

Agent 自主使用 MCP 工具：

```markdown
# Agent：data-analyzer.md

分析流程：
1. 通过 mcp__plugin_db_server__query 查询数据
2. 处理和分析结果
3. 生成洞察报告
```

**适用于：**无需用户交互的多步骤 MCP 工作流。

### 模式 3：多服务器插件

集成多个 MCP 服务器：

```json
{
  "github": {
    "type": "sse",
    "url": "https://mcp.github.com/sse"
  },
  "jira": {
    "type": "sse",
    "url": "https://mcp.jira.com/sse"
  }
}
```

**适用于：**跨多个服务的工作流。

## 安全最佳实践

### 使用 HTTPS/WSS

始终使用安全连接：

```json
✅ "url": "https://mcp.example.com/sse"
❌ "url": "http://mcp.example.com/sse"
```

### Token 管理

**应该做：**
- ✅ 使用环境变量存储 Token
- ✅ 在 README 中记录所需的环境变量
- ✅ 让 OAuth 流程处理身份验证

**不应该做：**
- ❌ 在配置中硬编码 Token
- ❌ 将 Token 提交到 git
- ❌ 在文档中分享 Token

### 权限范围

预先仅允许必要的 MCP 工具：

```markdown
✅ allowed-tools: [
  "mcp__plugin_api_server__read_data",
  "mcp__plugin_api_server__create_item"
]

❌ allowed-tools: ["mcp__plugin_api_server__*"]
```

## 错误处理

### 连接失败

处理 MCP 服务器不可用：
- 在命令中提供回退行为
- 告知用户连接问题
- 检查服务器 URL 和配置

### 工具调用错误

处理失败的 MCP 操作：
- 调用 MCP 工具前验证输入
- 提供清晰的错误消息
- 检查速率限制和配额

### 配置错误

验证 MCP 配置：
- 开发期间测试服务器连接性
- 验证 JSON 语法
- 检查必需的环境变量

## 性能考量

### 延迟加载

MCP 服务器按需连接：
- 并非所有服务器在启动时连接
- 首次使用工具时触发连接
- 连接池自动管理

### 批量处理

尽可能批量处理类似请求：

```
# 好：带过滤器的单次查询
tasks = search_tasks(project="X", assignee="me", limit=50)

# 避免：多次单独查询
for id in task_ids:
    task = get_task(id)
```

## 测试 MCP 集成

### 本地测试

1. 在 `.mcp.json` 中配置 MCP 服务器
2. 在本地安装插件（`.claude-plugin/`）
3. 运行 `/mcp` 验证服务器出现
4. 在命令中测试工具调用
5. 检查 `claude --debug` 日志中的连接问题

### 验证清单

- [ ] MCP 配置是有效的 JSON
- [ ] 服务器 URL 正确且可访问
- [ ] 已记录所需的环境变量
- [ ] 工具出现在 `/mcp` 输出中
- [ ] 身份验证工作正常（OAuth 或 Token）
- [ ] 命令中的工具调用成功
- [ ] 错误情况处理得当

## 调试

### 启用调试日志

```bash
claude --debug
```

关注：
- MCP 服务器连接尝试
- 工具发现日志
- 身份验证流程
- 工具调用错误

### 常见问题

**服务器无法连接：**
- 检查 URL 是否正确
- 验证服务器正在运行（stdio）
- 检查网络连接
- 审查身份验证配置

**工具不可用：**
- 验证服务器连接成功
- 检查工具名称是否完全匹配
- 运行 `/mcp` 查看可用工具
- 配置更改后重启 Claude Code

**身份验证失败：**
- 清除缓存的认证 Token
- 重新进行身份验证
- 检查 Token 范围和权限
- 验证环境变量已设置

## 快速参考

### MCP 服务器类型

| 类型   | 传输方式 | 最适合                 | 身份验证   |
| ------ | -------- | ---------------------- | ---------- |
| stdio  | 进程     | 本地工具、自定义服务器 | 环境变量   |
| SSE    | HTTP     | 托管服务、云 API       | OAuth      |
| HTTP   | REST     | API 后端、Token 认证   | Token      |
| ws     | WebSocket| 实时、流式传输         | Token      |

### 配置清单

- [ ] 指定服务器类型（stdio/SSE/HTTP/ws）
- [ ] 类型特定字段完整（command 或 url）
- [ ] 已配置身份验证
- [ ] 已记录环境变量
- [ ] 使用 HTTPS/WSS（而非 HTTP/WS）
- [ ] 路径使用 ${CLAUDE_PLUGIN_ROOT}

### 最佳实践

**应该做：**
- ✅ 使用 ${CLAUDE_PLUGIN_ROOT} 实现可移植路径
- ✅ 记录所需的环境变量
- ✅ 使用安全连接（HTTPS/WSS）
- ✅ 在命令中预先允许特定的 MCP 工具
- ✅ 发布前测试 MCP 集成
- ✅ 优雅地处理连接和工具错误

**不应该做：**
- ❌ 硬编码绝对路径
- ❌ 将凭据提交到 git
- ❌ 使用 HTTP 代替 HTTPS
- ❌ 用通配符预先允许所有工具
- ❌ 跳过错误处理
- ❌ 忘记记录设置

## 附加资源

### 参考文件

详细信息请查阅：

- **`references/server-types.md`** — 每种服务器类型的深入说明
- **`references/authentication.md`** — 身份验证模式和 OAuth
- **`references/tool-usage.md`** — 在命令和 Agent 中使用 MCP 工具

### 示例配置

`examples/` 中的工作示例：

- **`stdio-server.json`** — 本地 stdio MCP 服务器
- **`sse-server.json`** — 带 OAuth 的托管 SSE 服务器
- **`http-server.json`** — 带 Token 认证的 REST API

### 外部资源

- **官方 MCP 文档**：https://modelcontextprotocol.io/
- **Claude Code MCP 文档**：https://docs.claude.com/en/docs/claude-code/mcp
- **MCP SDK**：@modelcontextprotocol/sdk
- **测试**：使用 `claude --debug` 和 `/mcp` 命令

## 实现工作流

要为插件添加 MCP 集成：

1. 选择 MCP 服务器类型（stdio、SSE、HTTP、ws）
2. 在插件根目录创建 `.mcp.json` 配置
3. 所有文件引用使用 ${CLAUDE_PLUGIN_ROOT}
4. 在 README 中记录所需的环境变量
5. 使用 `/mcp` 命令进行本地测试
6. 在相关命令中预先允许 MCP 工具
7. 处理身份验证（OAuth 或 Token）
8. 测试错误情况（连接失败、认证错误）
9. 在插件 README 中记录 MCP 集成

对于自定义/本地服务器优先使用 stdio，对于带 OAuth 的托管服务优先使用 SSE。
