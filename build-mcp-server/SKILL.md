---
name: build-mcp-server
description: 当用户要求"构建 MCP 服务器"、"创建 MCP"、"制作 MCP 集成"、"为 Claude 封装 API"、"向 Claude 暴露工具"、"制作 MCP 应用"或讨论使用模型上下文协议构建内容时，应使用此技能。它是 MCP 服务器开发的入口点——会询问用户的用例，确定正确的部署模型（远程 HTTP、MCPB、本地 stdio），选择工具设计模式，并移交给专业技能处理。
version: 0.1.0
---

# 构建 MCP 服务器

你正在引导开发者设计和构建一个能与 Claude 无缝协作的 MCP 服务器。MCP 服务器有多种形式——早期选错形态会导致后期痛苦的重写。你的首要任务是**调研，而非编码**。

**首先加载 Claude 特定的上下文。** MCP 规范是通用的；Claude 有额外的认证类型、审查标准和限制。在回答问题或搭建脚手架之前，获取 `https://claude.com/docs/llms-full.txt`（Claude 连接器文档的完整导出），以确保你的指导反映 Claude 的实际约束。

在获得第1阶段问题的答案之前，不要开始搭建脚手架。如果用户的开场消息已经回答了这些问题，确认后直接跳到推荐部分。

---

## 第1阶段——调研用例

以对话方式提出以下问题（将它们批量放在一条消息中，不要逐个询问）。根据用户已告知的内容调整措辞。

### 1. 它连接什么？

| 如果连接的是… | 可能的方向 |
|---|---|
| 云 API（SaaS、REST、GraphQL） | 远程 HTTP 服务器 |
| 本地进程、文件系统或桌面应用 | MCPB 或本地 stdio |
| 硬件、操作系统级 API 或用户特定状态 | MCPB |
| 无外部连接——纯逻辑/计算 | 两者皆可——默认远程 |

### 2. 谁会使用它？

- **仅我自己/我的团队，在我们的机器上** → 本地 stdio 可接受（最容易原型化）
- **任何安装它的人** → 远程 HTTP（强烈推荐）或 MCPB（如果*必须*本地运行）
- **希望有 UI 组件的 Claude 桌面用户** → MCP 应用（远程或 MCPB）

### 3. 它暴露多少个不同的操作？

这决定了工具设计模式——见第3阶段。

- **少于约15个操作** → 每个操作一个工具
- **数十到数百个操作**（例如封装大型 API 表面） → 搜索 + 执行模式

### 4. 工具是否需要调用中途的用户输入或富显示？

- **简单结构化输入**（从列表选择、输入值、确认） → **Elicitation**——规范原生，零 UI 代码。*主机支持正在推出*（Claude Code >=2.1.76）——始终配合能力检查和回退方案。参见 `references/elicitation.md`。
- **富/视觉 UI**（图表、带搜索的自定义选择器、实时仪表板） → **MCP 应用组件**——基于 iframe，需要 `@modelcontextprotocol/ext-apps`。参见 `build-mcp-app` 技能。
- **都不需要** → 返回文本/JSON 的普通工具。

### 5. 上游服务使用什么认证？

- 无/API 密钥 → 简单直接
- OAuth 2.0 → 你需要一个支持 CIMD（推荐）或 DCR 的远程服务器；参见 `references/auth.md`

---

## 第2阶段——推荐部署模型

根据答案推荐**一条**路径。要有主见。排名选项：

### 远程流式 HTTP MCP 服务器（默认推荐）

托管服务通过流式 HTTP 使用 MCP 协议。这是封装云 API 的**推荐路径**。

**为什么它胜出：**
- 零安装摩擦——用户添加一个 URL 即可
- 一次部署服务所有用户；你控制升级
- OAuth 流程正常工作（服务器可以处理重定向、DCR、令牌存储）
- 跨 Claude 桌面版、Claude Code、Claude.ai 和第三方 MCP 主机工作

**除非**服务器*必须*访问用户的本地机器，否则选择此方案。

→ **最快部署：** Cloudflare Workers — `references/deploy-cloudflare-workers.md`（两条命令从零到线上 URL）
→ **可移植的 Node/Python：** `references/remote-http-scaffold.md`（Express 或 FastMCP，可在任何主机上运行）

### Elicitation（结构化输入，无需 UI 构建）

如果工具只需要用户确认、选择选项或填写简短表单，**Elicitation** 可以零 UI 代码完成。服务器发送扁平 JSON 模式；主机渲染原生表单。规范原生，无需额外包。

**注意：** 主机支持是新的（Claude Code 在 v2.1.76 中发布；桌面版未确认）。如果客户端不声明该能力，SDK 会抛出异常。始终先检查 `clientCapabilities.elicitation` 并准备回退方案——参见 `references/elicitation.md` 了解规范模式。这是正确的规范合规方法；主机覆盖率会逐步跟进。

当需要以下功能时，升级到 `build-mcp-app` 组件：嵌套/复杂数据、可滚动/可搜索列表、视觉预览、实时更新。

### MCP 应用（远程 HTTP + 交互式 UI）

与上述相同，加上 **UI 资源**——在聊天中渲染的交互式组件。带搜索的富选择器、图表、实时仪表板、视觉预览。构建一次，在 Claude *和* ChatGPT 中渲染。

**当** Elicitation 的扁平表单约束不适用时选择此方案——你需要自定义布局、大型可搜索列表、视觉内容或实时更新。

通常是远程的，但如果 UI 需要驱动本地应用，可以作为 MCPB 发布。

→ 移交给 **`build-mcp-app`** 技能。

### MCPB（打包的本地服务器）

**与其运行时一起打包**的本地 MCP 服务器，这样用户无需安装 Node/Python。这是发布本地服务器的官方方式。

**当**服务器*必须*在用户机器上运行时选择此方案——读取本地文件、驱动桌面应用、与 localhost 服务通信或需要操作系统级访问。

→ 移交给 **`build-mcpb`** 技能。

### 本地 stdio（npx / uvx）——*不推荐用于分发*

通过 `npx` / `uvx` 在用户机器上启动的脚本。适合**个人工具和原型**。分发痛苦：用户需要正确的运行时，你无法推送更新，唯一的分发渠道是 Claude Code 插件。

仅作为过渡方案推荐。如果用户坚持，搭建脚手架但注明 MCPB 升级路径。

---

## 第3阶段——选择工具设计模式

每个 MCP 服务器都暴露工具。你如何划分它们比大多数人预期的更重要——工具模式直接落入 Claude 的上下文窗口。

### 模式 A：每个操作一个工具（小型表面）

当操作空间较小（< 约15个操作）时，为每个操作提供一个专用工具，带有精确的描述和模式。

```
create_issue    — 创建新议题。参数：title, body, labels[]
update_issue    — 更新现有议题。参数：id, title?, body?, state?
search_issues   — 按查询字符串搜索议题。参数：query, limit?
add_comment     — 为议题添加评论。参数：issue_id, body
```

**为什么有效：** Claude 读取一次工具列表就确切知道有什么功能。无需发现往返。每个工具的模式精确验证输入。

**特别适合**一个或多个工具附带交互式组件（MCP 应用）的场景——每个组件自然绑定到一个工具。

### 模式 B：搜索 + 执行（大型表面）

当封装大型 API（数十到数百个端点）时，将每个操作列为工具会淹没上下文窗口并降低模型性能。相反，暴露**两个**工具：

```
search_actions  — 给定自然语言意图，返回匹配的操作
                  及其 ID、描述和参数模式。
execute_action  — 通过 ID 和参数对象运行操作。
```

服务器在内部持有完整目录。Claude 搜索、选择、执行。上下文保持精简。

**混合方案：** 将最常用的 3-5 个操作提升为专用工具，其余保留在搜索/执行后面。

→ 参见 `references/tool-design.md` 了解模式示例和描述编写指南。

---

## 第4阶段——选择框架

推荐以下两个之一。其他框架存在，但这两个具有最佳的 MCP 规范覆盖率和 Claude 兼容性。

| 框架 | 语言 | 适用场景 |
|---|---|---|
| **官方 TypeScript SDK** (`@modelcontextprotocol/sdk`) | TS/JS | 默认选择。最佳规范覆盖率，最先获得新功能。 |
| **FastMCP 3.x** (`fastmcp` on PyPI) | Python | 用户偏好 Python，或封装 Python 库。基于装饰器，极少样板代码。这是 jlowin 的包——不是官方 `mcp` SDK 中捆绑的冻结版 FastMCP 1.0。 |

如果用户已有语言/技术栈偏好，跟随即可——两者产生相同的线路协议。

---

## 第5阶段——搭建脚手架并移交

一旦确定了四个决策（部署模型、工具模式、框架、认证），执行以下**之一**：

1. **远程 HTTP，无 UI** → 使用 `references/remote-http-scaffold.md`（可移植）或 `references/deploy-cloudflare-workers.md`（最快部署）内联搭建脚手架。此技能可以完成工作。
2. **MCP 应用（UI 组件）** → 总结迄今为止的决策，然后加载 **`build-mcp-app`** 技能。
3. **MCPB（打包的本地服务器）** → 总结迄今为止的决策，然后加载 **`build-mcpb`** 技能。
4. **本地 stdio 原型** → 内联搭建脚手架（最简单情况），标注 MCPB 升级路径。

移交时，用一段话重述设计简报，以便下一个技能不会重复询问。

---

## 超越工具——其他原语

工具是三个服务器原语之一。大多数服务器从工具开始且永远不需要其他原语，但了解它们的存在可以避免重复造轮子：

| 原语 | 谁触发它 | 适用场景 |
|---|---|---|
| **Resources** | 主机应用（非 Claude） | 将文档/文件/数据作为可浏览上下文暴露 |
| **Prompts** | 用户（斜杠命令） | 预设工作流（"/summarize-thread"） |
| **Elicitation** | 服务器，工具调用中途 | 无需构建 UI 即可向用户请求输入 |
| **Sampling** | 服务器，工具调用中途 | 在工具逻辑中需要 LLM 推理 |

→ `references/resources-and-prompts.md`、`references/elicitation.md`、`references/server-capabilities.md`

---

## 第6阶段——在 Claude 中测试并发布

服务器运行后：

1. **针对真实 Claude 测试**，通过在设置 → 连接器中将服务器 URL 添加为自定义连接器（本地服务器使用 Cloudflare 隧道）。Claude 在初始化时通过 `clientInfo.name: "claude-ai"` 标识自己。→ https://claude.com/docs/connectors/building/testing
2. **运行提交前检查清单**——读/写工具分离、必需的注解、名称限制、提示注入规则。→ https://claude.com/docs/connectors/building/review-criteria
3. **提交到 Anthropic 目录。** → https://claude.com/docs/connectors/building/submission
4. **建议发布一个插件**，用技能封装此 MCP——大多数合作伙伴同时发布两者。→ https://claude.com/docs/connectors/building/what-to-build

---

## 快速参考：决策矩阵

| 场景 | 部署 | 工具模式 |
|---|---|---|
| 封装小型 SaaS API | 远程 HTTP | 每操作一个 |
| 封装大型 SaaS API（50+ 端点） | 远程 HTTP | 搜索 + 执行 |
| 带富表单/选择器的 SaaS API | MCP 应用（远程） | 每操作一个 |
| 驱动本地桌面应用 | MCPB | 每操作一个 |
| 带聊天内 UI 的本地桌面应用 | MCP 应用（MCPB） | 每操作一个 |
| 读写本地文件系统 | MCPB | 取决于表面 |
| 个人原型 | 本地 stdio | 最快的方式 |

---

## 参考文件

- `references/remote-http-scaffold.md` — 使用 TS SDK 和 FastMCP 的最小远程服务器
- `references/deploy-cloudflare-workers.md` — 最快部署路径（Workers 原生脚手架）
- `references/tool-design.md` — 编写 Claude 能良好理解的工具描述和模式
- `references/auth.md` — OAuth、CIMD、DCR、令牌存储模式
- `references/resources-and-prompts.md` — 两个非工具原语
- `references/elicitation.md` — 规范原生的工具调用中途用户输入（能力检查 + 回退）
- `references/server-capabilities.md` — 指令、采样、根目录、日志、进度、取消
- `references/versions.md` — 版本敏感声明账本（更新时检查）
