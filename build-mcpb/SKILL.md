---
name: build-mcpb
description: 当用户想要"打包 MCP 服务器"、"捆绑 MCP"、"制作 MCPB"、"发布本地 MCP 服务器"、"分发本地 MCP"、讨论 ".mcpb 文件"、提到将 Node 或 Python 运行时与 MCP 服务器捆绑，或需要一个与本地文件系统、桌面应用或操作系统交互且无需用户安装 Node/Python 即可安装的 MCP 服务器时，应使用此技能。
version: 0.1.0
---

# 构建 MCPB（打包的本地 MCP 服务器）

MCPB 是一个**与其运行时一起打包**的本地 MCP 服务器。用户安装一个文件；它无需在机器上安装 Node、Python 或任何工具链即可运行。这是发布本地 MCP 服务器的官方方式。

> MCPB 是**次要**分发路径。Anthropic 推荐远程 MCP 服务器用于目录列表——参见 https://claude.com/docs/connectors/building/what-to-build。

**当服务器必须在用户机器上运行时使用 MCPB**——读取本地文件、驱动桌面应用、与 localhost 服务通信、操作系统级 API。如果你的服务器只访问云 API，你几乎肯定想要远程 HTTP 服务器（参见 `build-mcp-server`）。不要为一个可以是 URL 的东西付出 MCPB 打包的代价。

---

## MCPB 包的内容

```
my-server.mcpb              (zip 归档)
├── manifest.json           ← 身份、入口点、配置模式、兼容性
├── server/                 ← 你的 MCP 服务器代码
│   ├── index.js
│   └── node_modules/       ← 捆绑的依赖（或供应商化）
└── icon.png
```

主机读取 `manifest.json`，以 **stdio** MCP 服务器方式启动 `server.mcp_config.command`，并通过管道传递消息。从你的代码角度来看，它与本地 stdio 服务器完全相同——唯一的区别是打包方式。

---

## 清单

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/mcpb/main/schemas/mcpb-manifest-v0.4.schema.json",
  "manifest_version": "0.4",
  "name": "local-files",
  "version": "0.1.0",
  "description": "Read, search, and watch files on the local filesystem.",
  "author": { "name": "Your Name" },
  "server": {
    "type": "node",
    "entry_point": "server/index.js",
    "mcp_config": {
      "command": "node",
      "args": ["${__dirname}/server/index.js"],
      "env": {
        "ROOT_DIR": "${user_config.rootDir}"
      }
    }
  },
  "user_config": {
    "rootDir": {
      "type": "directory",
      "title": "Root directory",
      "description": "Directory to expose. Defaults to ~/Documents.",
      "default": "${HOME}/Documents",
      "required": true
    }
  },
  "compatibility": {
    "claude_desktop": ">=1.0.0",
    "platforms": ["darwin", "win32", "linux"]
  }
}
```

**`server.type`** — `node`、`python` 或 `binary`。仅供参考；实际启动来自 `mcp_config`。

**`server.mcp_config`** — 要生成的字面命令/参数/环境变量。使用 `${__dirname}` 表示包相对路径，使用 `${user_config.<key>}` 替换安装时配置。**没有自动前缀**——你的服务器读取的环境变量名称就是你在 `env` 中放入的名称。

**`user_config`** — 在主机 UI 中显示的安装时设置。`type: "directory"` 渲染原生文件夹选择器。`sensitive: true` 存储在操作系统密钥链中。参见 `references/manifest-schema.md` 了解所有字段。

---

## 服务器代码：与本地 stdio 相同

服务器本身是标准的 stdio MCP 服务器。工具逻辑中没有 MCPB 特定的内容。

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";

// ROOT_DIR 来自你在清单的 server.mcp_config.env 中设置的内容——没有自动前缀
const ROOT = (process.env.ROOT_DIR ?? join(homedir(), "Documents"));

const server = new McpServer({ name: "local-files", version: "0.1.0" });

server.registerTool(
  "list_files",
  {
    description: "List files in a directory under the configured root.",
    inputSchema: { path: z.string().default(".") },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const entries = await readdir(join(ROOT, path), { withFileTypes: true });
    const list = entries.map(e => ({ name: e.name, dir: e.isDirectory() }));
    return { content: [{ type: "text", text: JSON.stringify(list, null, 2) }] };
  },
);

server.registerTool(
  "read_file",
  {
    description: "Read a file's contents. Path is relative to the configured root.",
    inputSchema: { path: z.string() },
    annotations: { readOnlyHint: true },
  },
  async ({ path }) => {
    const text = await readFile(join(ROOT, path), "utf8");
    return { content: [{ type: "text", text }] };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

**沙盒化完全由你负责。** 没有清单级沙盒——进程以完整用户权限运行。验证路径，拒绝逃逸 `ROOT`，允许列表生成。参见 `references/local-security.md`。

在从配置环境变量硬编码 `ROOT` 之前，检查主机是否支持 `roots/list`——这是获取用户批准目录的规范原生方式。参见 `references/local-security.md` 了解模式。

---

## 构建流水线

### Node

```bash
npm install
npx esbuild src/index.ts --bundle --platform=node --outfile=server/index.js
# 或者：如果原生依赖抵抗打包，直接复制 node_modules
npx @anthropic-ai/mcpb pack
```

`mcpb pack` 压缩目录并根据模式验证 `manifest.json`。

### Python

```bash
pip install -t server/vendor -r requirements.txt
npx @anthropic-ai/mcpb pack
```

将依赖供应商化到子目录，并在入口脚本中将其前置到 `sys.path`。原生扩展（numpy 等）必须为每个目标平台构建——如果可以的话避免原生依赖。

---

## MCPB 没有沙盒——安全由你负责

与移动应用商店不同，MCPB 不强制执行权限。清单没有 `permissions` 块——服务器以完整用户权限运行。`references/local-security.md` 是必读材料，不是可选的。每个路径都必须验证，每个生成都必须在允许列表中，因为在平台级别没有任何东西阻止你。

如果你来这里期望从清单中获得文件系统/网络范围限定：它不存在。在工具处理器中自己构建。

如果你服务器的唯一任务是访问云 API，停下来——那是穿着 MCPB 外衣的远程服务器。用户从本地运行中得不到任何好处，而你却无故承担了本地安全负担。

---

## MCPB + UI 组件

MCPB 服务器可以像远程 MCP 应用一样服务 UI 资源——组件机制与传输无关。浏览实际磁盘的本地文件选择器、控制原生应用的对话框等。

组件编写在 **`build-mcp-app`** 技能中有介绍；这里的工作方式相同。唯一的区别是服务器运行的位置。

---

## 测试

```bash
# 交互式清单创建（首次）
npx @anthropic-ai/mcpb init

# 直接通过 stdio 运行服务器，使用检查器探测
npx @modelcontextprotocol/inspector node server/index.js

# 根据模式验证清单，然后打包
npx @anthropic-ai/mcpb validate
npx @anthropic-ai/mcpb pack

# 签名以供分发
npx @anthropic-ai/mcpb sign dist/local-files.mcpb

# 安装：将 .mcpb 文件拖到 Claude 桌面版上
```

在发布前在**没有**你的开发工具链的机器上测试。"在我的机器上可以工作"的 MCPB 失败几乎总是追溯到一个实际上没有被打包的依赖。

---

## 参考文件

- `references/manifest-schema.md` — 完整的 `manifest.json` 字段参考
- `references/local-security.md` — 路径遍历、沙盒化、最小权限
