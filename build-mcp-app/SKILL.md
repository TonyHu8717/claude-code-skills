---
name: build-mcp-app
description: 当用户想要构建"MCP 应用"、为 MCP 服务器添加"交互式 UI"或"组件"、"在聊天中渲染组件"、构建"MCP UI 资源"、制作在对话中内联显示"表单"、"选择器"、"仪表板"或"确认对话框"的工具，或在 MCP 上下文中提到"apps SDK"时，应使用此技能。在 build-mcp-server 技能确定部署模型之后使用，或当用户已知需要 UI 组件时使用。
version: 0.1.0
---

# 构建 MCP 应用（交互式 UI 组件）

MCP 应用是一个标准的 MCP 服务器，**同时服务 UI 资源**——在聊天界面中内联渲染的交互式组件。构建一次，在 Claude *和* ChatGPT 以及任何实现 apps 界面的其他主机中运行。

UI 层是**附加的**。底层仍然是工具、资源和相同的线路协议。如果你之前没有构建过普通的 MCP 服务器，`build-mcp-server` 技能涵盖了基础层。此技能在其上添加组件。

> **在 Claude 中测试：** 将服务器添加为 claude.ai 中的自定义连接器（本地开发通过 Cloudflare 隧道）——这会使用真实的 iframe 沙盒和 `hostContext`。参见 https://claude.com/docs/connectors/building/testing。

## Claude 主机特定说明

| `_meta.ui.*` 键 | 位置 | 效果 |
|---|---|---|
| `resourceUri` | tool | 主机为此工具的结果渲染哪个 `ui://` 资源。 |
| `visibility: ["app"]` | tool | 从 Claude 的工具列表中隐藏仅用于组件的辅助工具（例如通过 `callServerTool` 调用的几何/图像获取器）。 |
| `prefersBorder: false` | resource | 去除主机的外层卡片边框（移动端）。 |
| `csp.{connectDomains, resourceDomains, baseUriDomains}` | resource | 声明外部来源；默认为全部阻止。`frameDomains` 在 Claude 中目前受限。 |

- `hostContext.safeAreaInsets: {top, right, bottom, left}`（像素）——为刘海和 composer 覆盖层遵守这些值。
- 目录提交需要 OAuth 或 **authless**（`none`）——静态 bearer 仅限私有部署且阻止列出——加上工具 `annotations` 和 3-5 张 PNG 截图；参见 `references/directory-checklist.md`。

---

## 何时组件优于纯文本

不要为了 UI 而添加 UI——大多数工具返回文本或 JSON 就够了。当以下情况之一为真时添加组件：

| 信号 | 组件类型 |
|---|---|
| 工具需要 Claude 无法可靠推断的结构化输入 | 表单 |
| 用户必须从 Claude 无法排序的列表中选择（文件、联系人、记录） | 选择器/表格 |
| 破坏性或计费操作需要明确确认 | 确认对话框 |
| 输出是空间性或视觉性的（图表、地图、差异、预览） | 显示组件 |
| 用户想要观看的长时间运行任务 | 进度/实时状态 |

如果都不适用，跳过组件。文本构建更快，对用户也更快。

---

## 组件 vs Elicitation — 正确路由

在构建组件之前，检查 **Elicitation** 是否能覆盖。Elicitation 是规范原生的，零 UI 代码，在任何合规主机中工作。

| 需求 | Elicitation | 组件 |
|---|---|---|
| 确认是/否 | 可以 | 过度 |
| 从短枚举中选择 | 可以 | 过度 |
| 填写扁平表单（姓名、邮箱、日期） | 可以 | 过度 |
| 从大型/可搜索列表中选择 | 不行（无滚动/搜索） | 可以 |
| 选择前的视觉预览 | 不行 | 可以 |
| 图表/地图/差异视图 | 不行 | 可以 |
| 实时更新的进度 | 不行 | 可以 |

如果 Elicitation 能覆盖，就用它。参见 `../build-mcp-server/references/elicitation.md`。

---

## 架构：两种部署形态

### 远程 MCP 应用（最常见）

托管的流式 HTTP 服务器。组件模板作为**资源**服务；工具结果引用它们。主机获取资源，在 iframe 沙盒中渲染，并在组件和 Claude 之间代理消息。

```
┌──────────┐  tools/call   ┌────────────┐
│  Claude  │─────────────> │ MCP server │
│   host   │<── result ────│  (remote)  │
│          │  + widget ref │            │
│          │               │            │
│          │ resources/read│            │
│          │─────────────> │  widget    │
│ ┌──────┐ │<── template ──│  HTML/JS   │
│ │iframe│ │               └────────────┘
│ │widget│ │
│ └──────┘ │
└──────────┘
```

### MCPB 打包的 MCP 应用（本地 + UI）

相同的组件机制，但服务器在 MCPB 包内本地运行。当组件需要驱动**本地**应用时使用——例如浏览实际本地磁盘的文件选择器、控制桌面应用的对话框。

对于 MCPB 打包机制，交由 **`build-mcpb`** 技能处理。以下所有内容适用于两种形态。

---

## 组件如何附加到工具

启用组件的工具具有**两个独立的注册**：

1. **工具**通过 `_meta.ui.resourceUri` 声明 UI 资源。其处理器返回纯文本/JSON——不是 HTML。
2. **资源**单独注册并服务 HTML。

当 Claude 调用工具时，主机看到 `_meta.ui.resourceUri`，获取该资源，在 iframe 中渲染，并通过 `ontoolresult` 事件将工具的返回值传入 iframe。

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";

const server = new McpServer({ name: "contacts", version: "1.0.0" });

// 1. 工具 — 返回数据，声明要显示的 UI
registerAppTool(server, "pick_contact", {
  description: "Open an interactive contact picker",
  annotations: { title: "Pick Contact", readOnlyHint: true },
  inputSchema: { filter: z.string().optional() },
  _meta: { ui: { resourceUri: "ui://widgets/contact-picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter);
  // 纯 JSON — 组件通过 ontoolresult 接收此数据
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

// 2. 资源 — 服务 HTML
registerAppResource(
  server,
  "Contact Picker",
  "ui://widgets/contact-picker.html",
  {},
  async () => ({
    contents: [{
      uri: "ui://widgets/contact-picker.html",
      mimeType: RESOURCE_MIME_TYPE,
      text: pickerHtml,  // 你的 HTML 字符串
    }],
  }),
);
```

URI 方案 `ui://` 是约定。MIME 类型必须是 `RESOURCE_MIME_TYPE`（`"text/html;profile=mcp-app"`）——这是主机知道将其作为交互式 iframe 渲染而不是仅显示源代码的方式。

---

## 组件运行时 — `App` 类

在 iframe 内，你的脚本通过 `@modelcontextprotocol/ext-apps` 中的 `App` 类与主机通信。这是一个**持久的双向连接**——组件在对话活跃期间保持存活，接收新的工具结果并发送用户操作。

```html
<script type="module">
  /* ext-apps 包在构建时内联 → globalThis.ExtApps */
  /*__EXT_APPS_BUNDLE__*/
  const { App } = globalThis.ExtApps;

  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});

  // 在连接之前设置处理器
  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    render(contacts);
  };

  await app.connect();

  // 稍后，当用户点击某物时：
  function onPick(contact) {
    app.sendMessage({
      role: "user",
      content: [{ type: "text", text: `Selected contact: ${contact.id}` }],
    });
  }
</script>
```

`/*__EXT_APPS_BUNDLE__*/` 占位符在启动时被服务器替换为 `@modelcontextprotocol/ext-apps/app-with-deps` 的内容——参见 `references/iframe-sandbox.md` 了解为什么这是必要的以及重写代码片段。**不要** `import { App } from "https://esm.sh/..."`；iframe 的 CSP 会阻止传递依赖获取，组件会渲染为空白。

| 方法 | 方向 | 用途 |
|---|---|---|
| `app.ontoolresult = fn` | 主机 → 组件 | 接收工具的返回值 |
| `app.ontoolinput = fn` | 主机 → 组件 | 接收工具的输入参数（Claude 传递的） |
| `app.sendMessage({...})` | 组件 → 主机 | 向对话注入消息 |
| `app.updateModelContext({...})` | 组件 → 主机 | 静默更新上下文（无可见消息） |
| `app.callServerTool({name, arguments})` | 组件 → 服务器 | 调用服务器上的另一个工具 |
| `app.openLink({url})` | 组件 → 主机 | 在新标签页中打开 URL（沙盒阻止 `window.open`） |
| `app.getHostContext()` / `app.onhostcontextchanged` | 主机 → 组件 | 主题、主机 CSS 变量、`containerDimensions`、`displayMode`、`deviceCapabilities` |
| `app.requestDisplayMode({mode})` | 组件 → 主机 | 请求 `inline` / `pip` / `fullscreen` |
| `app.downloadFile({name, mimeType, content})` | 组件 → 主机 | 主机代理下载（base64 内容） |
| `new App(info, caps, {autoResize: true})` | — | iframe 高度跟踪渲染内容 |

`sendMessage` 是典型的"用户选择了某物，告诉 Claude"路径。`updateModelContext` 用于 Claude 应该知道但不应 clutter 聊天的状态。`openLink` 对于任何出站导航都是**必需的**——`window.open` 和 `<a target="_blank">` 被沙盒属性阻止。

**组件不能做的事：**
- 访问主机页面的 DOM、cookie 或存储
- 向任意来源发起网络调用（CSP 限制——通过 `callServerTool` 路由）
- 打开弹出窗口或直接导航——使用 `app.openLink({url})`
- 可靠地加载远程图像——在服务器端内联为 `data:` URL

保持组件**小而专注**。选择器选择。图表显示。不要在 iframe 内构建整个子应用——将其拆分为多个带有聚焦组件的工具。

---

## 脚手架：最小选择器组件

**安装：**

```bash
npm install @modelcontextprotocol/sdk @modelcontextprotocol/ext-apps zod express
```

**服务器 (`src/server.ts`)：**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import express from "express";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { z } from "zod";

const require = createRequire(import.meta.url);
const server = new McpServer({ name: "contact-picker", version: "1.0.0" });

// 将 ext-apps 浏览器包内联到组件 HTML 中。
// iframe CSP 阻止 CDN 脚本获取——打包是强制的。
const bundle = readFileSync(
  require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8",
).replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
  "globalThis.ExtApps={" +
  body.split(",").map((p) => {
    const [local, exported] = p.split(" as ").map((s) => s.trim());
    return `${exported ?? local}:${local}`;
  }).join(",") + "};",
);
const pickerHtml = readFileSync("./widgets/picker.html", "utf8")
  .replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);

registerAppTool(server, "pick_contact", {
  description: "Open an interactive contact picker. User selects one contact.",
  annotations: { title: "Pick Contact", readOnlyHint: true },
  inputSchema: { filter: z.string().optional().describe("Name/email prefix filter") },
  _meta: { ui: { resourceUri: "ui://widgets/picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter ?? "");
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

registerAppResource(server, "Contact Picker", "ui://widgets/picker.html", {},
  async () => ({
    contents: [{ uri: "ui://widgets/picker.html", mimeType: RESOURCE_MIME_TYPE, text: pickerHtml }],
  }),
);

const app = express();
app.use(express.json());
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
app.listen(process.env.PORT ?? 3000);
```

对于仅本地的组件应用（驱动桌面应用、读取本地文件），将传输替换为 `StdioServerTransport` 并通过 `build-mcpb` 技能打包。

**组件 (`widgets/picker.html`)：**

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 0; }
  ul { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; }
  li { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #eee; }
  li:hover { background: #f5f5f5; }
  .sub { color: #666; font-size: 12px; }
</style>
<ul id="list"></ul>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});
  const ul = document.getElementById("list");

  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    ul.innerHTML = "";
    for (const c of contacts) {
      const li = document.createElement("li");
      li.innerHTML = `<div>${c.name}</div><div class="sub">${c.email}</div>`;
      li.addEventListener("click", () => {
        app.sendMessage({
          role: "user",
          content: [{ type: "text", text: `Selected contact: ${c.id} (${c.name})` }],
        });
      });
      ul.append(li);
    }
  };

  await app.connect();
})();
</script>
```

参见 `references/widget-templates.md` 了解更多组件形态。

---

## 节省重写的设计注意事项

**每个工具一个组件。** 抵制构建一个做所有事的超级组件的冲动。一个工具 → 一个聚焦的组件 → 一个清晰的结果形态。Claude 对此推理效果好得多。

**工具描述必须提到组件。** Claude 在决定调用什么时只看到工具描述。描述中的"打开交互式选择器"是让 Claude 使用它而不是猜测 ID 的原因。

**组件在运行时是可选的。** 不支持 apps 界面的主机会忽略 `_meta.ui` 并正常渲染工具的文本内容。由于你的工具处理器已经返回有意义的文本/JSON（组件的数据），降级是自动的——Claude 直接看到数据而不是通过组件。

**不要为只读工具阻塞组件结果。** 仅*显示*数据的组件（图表、预览）不应要求用户操作来完成。在同一结果中返回显示组件*和*文本摘要，这样 Claude 可以继续推理而无需等待。

**按项目数量而非工具数量进行布局分支。** 如果一个用例是"详细显示一个结果"而另一个是"并排显示多个结果"，不要创建两个工具——创建一个接受 `items[]` 的工具，让组件选择布局：`items.length === 1` → 详情视图，`> 1` → 轮播。保持服务器模式简单，让 Claude 自然决定数量。

**将 Claude 的推理放入载荷中。** 每个项目上的简短 `note` 字段（Claude 为什么选择它）作为卡片上的标注渲染，将推理内联显示在选择旁边。在工具描述中提到此字段以便 Claude 填充它。

**在服务器端规范化图像形状。** 如果你的数据源返回宽高比差异很大的图像，在获取 data-URL 内联*之前*重写为可预测的变体（例如方形约束）。然后给组件的图像容器固定的 `aspect-ratio` + `object-fit: contain`，使所有内容居中。

**遵循主机主题。** `app.getHostContext()?.theme`（`connect()` 之后）加上 `app.onhostcontextchanged` 用于实时更新。在 `<html>` 上切换 `.dark` 类，将颜色保持在带有 `:root.dark {}` 覆盖块的 CSS 自定义属性中，设置 `color-scheme`。在暗色模式下禁用 `mix-blend-mode: multiply`——它会使图像消失。

---

## 测试

**Claude 桌面版**——当前构建仍然需要 `command`/`args` 配置形式（不支持原生 `"type": "http"`）。使用 `mcp-remote` 包装并强制 `http-only` 传输，这样 SSE 探测不会吞噬组件能力协商：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/mcp",
               "--allow-http", "--transport", "http-only"]
    }
  }
}
```

桌面版积极缓存 UI 资源。编辑组件 HTML 后，**完全退出**（Cmd+Q / Alt+F4，不是关闭窗口）并重新启动以强制冷资源重新获取。

**无头 JSON-RPC 循环**——无需点击桌面版即可快速迭代：

```bash
# test.jsonl — 每行一条 JSON-RPC 消息
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"your_tool","arguments":{...}}}

(cat test.jsonl; sleep 10) | npx mcp-remote http://localhost:3000/mcp --allow-http
```

`sleep` 保持 stdin 足够长时间以收集所有响应。使用 `jq` 或 Python 单行代码解析 jsonl 输出。

**组件开发循环**——完全避免 Cmd+Q 重启循环，通过在普通 GET 路由上提供内联组件 HTML，并使用从查询参数触发 `ontoolresult` 的假 `ExtApps` shim：

```ts
app.get("/widget-preview", (_req, res) => {
  const shim = `globalThis.ExtApps={applyHostStyleVariables:()=>{},App:class{
    constructor(){this.h={}} ontoolresult;onhostcontextchanged;
    async connect(){const p=new URLSearchParams(location.search).get("payload");
      if(p)this.ontoolresult?.({content:[{type:"text",text:p}]});}
    getHostContext(){return{theme:"light"}}
    sendMessage(m){console.log("sendMessage",m)} updateModelContext(){}
    callServerTool(){return Promise.resolve({content:[]})} openLink(){} downloadFile(){}
  }};`;
  res.type("html").send(widgetHtml.replace("/*__EXT_APPS_BUNDLE__*/", shim));
});
```

在普通浏览器标签页中打开 `http://localhost:3000/widget-preview?payload={"rows":[...]}` 并使用普通 devtools 迭代。

**主机回退**——使用不支持 apps 界面的主机（或 MCP Inspector）并确认工具的文本内容优雅降级。

**CSP 调试**——打开 iframe 自己的 devtools 控制台。CSP 违规是组件静默失败（空白矩形，主控制台无错误）的头号原因。参见 `references/iframe-sandbox.md`。

---

## 参考文件

- `references/iframe-sandbox.md` — CSP/沙盒约束、包内联模式、图像处理、主机主题
- `references/widget-templates.md` — 选择器/确认/进度/显示的可复用 HTML 脚手架
- `references/apps-sdk-messages.md` — `App` 类 API：组件 ↔ 主机 ↔ 服务器消息传递、生命周期与替代
- `references/payload-budgeting.md` — 主机工具结果大小限制、先修剪后截断、通过 `callServerTool` 处理重型资产
- `references/abuse-protection.md` — Anthropic 出口 CIDR、分层速率限制、`trust proxy`、响应缓存
- `references/directory-checklist.md` — 连接器目录提交前的预检
