---
name: plugin-structure
description: 当用户要求"创建插件"、"搭建插件骨架"、"理解插件结构"、"组织插件组件"、"设置 plugin.json"、"使用 ${CLAUDE_PLUGIN_ROOT}"、"添加 commands/agents/skills/hooks"、"配置自动发现"，或需要关于插件目录布局、清单配置、组件组织、文件命名约定或 Claude Code 插件架构最佳实践的指导时，应使用此技能。
version: 0.1.0
---

# Claude Code 插件结构

## 概述

Claude Code 插件遵循标准化的目录结构，支持自动组件发现。理解此结构有助于创建组织良好、易于维护的插件，并与 Claude Code 无缝集成。

**核心概念：**
- 符合约定的目录布局，支持自动发现
- 基于清单的配置，位于 `.claude-plugin/plugin.json`
- 基于组件的组织方式（commands、agents、skills、hooks）
- 使用 `${CLAUDE_PLUGIN_ROOT}` 实现可移植路径引用
- 显式加载与自动发现组件加载

## 目录结构

每个 Claude Code 插件遵循以下组织模式：

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # 必需：插件清单
├── commands/                 # 斜杠命令（.md 文件）
├── agents/                   # 子代理定义（.md 文件）
├── skills/                   # 代理技能（子目录）
│   └── skill-name/
│       └── SKILL.md         # 每个技能必需
├── hooks/
│   └── hooks.json           # 事件处理器配置
├── .mcp.json                # MCP 服务器定义
└── scripts/                 # 辅助脚本和工具
```

**关键规则：**

1. **清单位置**：`plugin.json` 清单必须位于 `.claude-plugin/` 目录中
2. **组件位置**：所有组件目录（commands、agents、skills、hooks）必须位于插件根目录级别，不能嵌套在 `.claude-plugin/` 内
3. **可选组件**：仅为插件实际使用的组件创建目录
4. **命名约定**：所有目录和文件名使用 kebab-case 格式

## 插件清单（plugin.json）

清单定义插件元数据和配置，位于 `.claude-plugin/plugin.json`：

### 必需字段

```json
{
  "name": "plugin-name"
}
```

**名称要求：**
- 使用 kebab-case 格式（小写加连字符）
- 在已安装插件中必须唯一
- 不能包含空格或特殊字符
- 示例：`code-review-assistant`、`test-runner`、`api-docs`

### 推荐的元数据

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "插件用途的简要说明",
  "author": {
    "name": "作者姓名",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/user/plugin-name",
  "license": "MIT",
  "keywords": ["testing", "automation", "ci-cd"]
}
```

**版本格式**：遵循语义化版本控制（MAJOR.MINOR.PATCH）
**关键词**：用于插件发现和分类

### 组件路径配置

为组件指定自定义路径（补充默认目录）：

```json
{
  "name": "plugin-name",
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**重要**：自定义路径是补充而非替换默认目录。默认目录和自定义路径中的组件都会被加载。

**路径规则：**
- 必须相对于插件根目录
- 必须以 `./` 开头
- 不能使用绝对路径
- 支持数组形式的多个位置

## 组件组织

### 命令（Commands）

**位置**：`commands/` 目录
**格式**：带 YAML frontmatter 的 Markdown 文件
**自动发现**：`commands/` 中的所有 `.md` 文件自动加载

**示例结构**：
```
commands/
├── review.md        # /review 命令
├── test.md          # /test 命令
└── deploy.md        # /deploy 命令
```

**文件格式**：
```markdown
---
name: command-name
description: 命令描述
---

命令实现说明...
```

**用法**：命令作为 Claude Code 中的原生斜杠命令集成

### 代理（Agents）

**位置**：`agents/` 目录
**格式**：带 YAML frontmatter 的 Markdown 文件
**自动发现**：`agents/` 中的所有 `.md` 文件自动加载

**示例结构**：
```
agents/
├── code-reviewer.md
├── test-generator.md
└── refactorer.md
```

**文件格式**：
```markdown
---
description: 代理角色和专业领域
capabilities:
  - 具体任务 1
  - 具体任务 2
---

详细的代理指令和知识...
```

**用法**：用户可以手动调用代理，或者 Claude Code 根据任务上下文自动选择

### 技能（Skills）

**位置**：`skills/` 目录，每个技能一个子目录
**格式**：每个技能在自己的目录中，包含 `SKILL.md` 文件
**自动发现**：技能子目录中的所有 `SKILL.md` 文件自动加载

**示例结构**：
```
skills/
├── api-testing/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── test-runner.py
│   └── references/
│       └── api-spec.md
└── database-migrations/
    ├── SKILL.md
    └── examples/
        └── migration-template.sql
```

**SKILL.md 格式**：
```markdown
---
name: Skill Name
description: 何时使用此技能
version: 1.0.0
---

技能指令和指导...
```

**支持文件**：技能可以在子目录中包含脚本、参考资料、示例或资产

**用法**：Claude Code 根据任务上下文与描述的匹配自动激活技能

### 钩子（Hooks）

**位置**：`hooks/hooks.json` 或在 `plugin.json` 中内联
**格式**：定义事件处理器的 JSON 配置
**注册**：插件启用时钩子自动注册

**示例结构**：
```
hooks/
├── hooks.json           # 钩子配置
└── scripts/
    ├── validate.sh      # 钩子脚本
    └── check-style.sh   # 钩子脚本
```

**配置格式**：
```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.sh",
      "timeout": 30
    }]
  }]
}
```

**可用事件**：PreToolUse、PostToolUse、Stop、SubagentStop、SessionStart、SessionEnd、UserPromptSubmit、PreCompact、Notification

**用法**：钩子在 Claude Code 事件触发时自动执行

### MCP 服务器

**位置**：插件根目录的 `.mcp.json` 或在 `plugin.json` 中内联
**格式**：MCP 服务器定义的 JSON 配置
**自动启动**：插件启用时服务器自动启动

**示例格式**：
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**用法**：MCP 服务器与 Claude Code 的工具系统无缝集成

## 可移植路径引用

### ${CLAUDE_PLUGIN_ROOT}

使用 `${CLAUDE_PLUGIN_ROOT}` 环境变量进行所有插件内部路径引用：

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh"
}
```

**为什么重要**：插件的安装位置取决于：
- 用户安装方式（市场、本地、npm）
- 操作系统约定
- 用户偏好

**使用场景**：
- 钩子命令路径
- MCP 服务器命令参数
- 脚本执行引用
- 资源文件路径

**绝不使用**：
- 硬编码绝对路径（`/Users/name/plugins/...`）
- 从工作目录的相对路径（命令中的 `./scripts/...`）
- 主目录快捷方式（`~/plugins/...`）

### 路径解析规则

**在清单 JSON 字段中**（钩子、MCP 服务器）：
```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/tool.sh"
```

**在组件文件中**（命令、代理、技能）：
```markdown
在以下位置引用脚本：${CLAUDE_PLUGIN_ROOT}/scripts/helper.py
```

**在执行的脚本中**：
```bash
#!/bin/bash
# ${CLAUDE_PLUGIN_ROOT} 作为环境变量可用
source "${CLAUDE_PLUGIN_ROOT}/lib/common.sh"
```

## 文件命名约定

### 组件文件

**命令**：使用 kebab-case 的 `.md` 文件
- `code-review.md` → `/code-review`
- `run-tests.md` → `/run-tests`
- `api-docs.md` → `/api-docs`

**代理**：使用描述角色的 kebab-case `.md` 文件
- `test-generator.md`
- `code-reviewer.md`
- `performance-analyzer.md`

**技能**：使用 kebab-case 目录名
- `api-testing/`
- `database-migrations/`
- `error-handling/`

### 支持文件

**脚本**：使用描述性的 kebab-case 名称和适当的扩展名
- `validate-input.sh`
- `generate-report.py`
- `process-data.js`

**文档**：使用 kebab-case 的 markdown 文件
- `api-reference.md`
- `migration-guide.md`
- `best-practices.md`

**配置**：使用标准名称
- `hooks.json`
- `.mcp.json`
- `plugin.json`

## 自动发现机制

Claude Code 自动发现和加载组件：

1. **插件清单**：插件启用时读取 `.claude-plugin/plugin.json`
2. **命令**：扫描 `commands/` 目录中的 `.md` 文件
3. **代理**：扫描 `agents/` 目录中的 `.md` 文件
4. **技能**：扫描 `skills/` 中包含 `SKILL.md` 的子目录
5. **钩子**：从 `hooks/hooks.json` 或清单加载配置
6. **MCP 服务器**：从 `.mcp.json` 或清单加载配置

**发现时机**：
- 插件安装：组件注册到 Claude Code
- 插件启用：组件变得可用
- 无需重启：更改在下次 Claude Code 会话时生效

**覆盖行为**：`plugin.json` 中的自定义路径补充（而非替换）默认目录

## 最佳实践

### 组织

1. **逻辑分组**：将相关组件分组
   - 将测试相关的命令、代理和技能放在一起
   - 在 `scripts/` 中为不同用途创建子目录

2. **精简清单**：保持 `plugin.json` 简洁
   - 仅在必要时指定自定义路径
   - 依赖标准布局的自动发现
   - 仅在简单情况下使用内联配置

3. **文档**：包含 README 文件
   - 插件根目录：整体目的和用法
   - 组件目录：具体指导
   - 脚本目录：用法和要求

### 命名

1. **一致性**：在组件间使用一致的命名
   - 如果命令是 `test-runner`，相关代理命名为 `test-runner-agent`
   - 技能目录名与其用途匹配

2. **清晰性**：使用表明用途的描述性名称
   - 好：`api-integration-testing/`、`code-quality-checker.md`
   - 避免：`utils/`、`misc.md`、`temp.sh`

3. **长度**：在简洁和清晰之间平衡
   - 命令：2-3 个词（`review-pr`、`run-ci`）
   - 代理：清楚描述角色（`code-reviewer`、`test-generator`）
   - 技能：主题聚焦（`error-handling`、`api-design`）

### 可移植性

1. **始终使用 ${CLAUDE_PLUGIN_ROOT}**：绝不硬编码路径
2. **在多系统上测试**：在 macOS、Linux、Windows 上验证
3. **记录依赖**：列出所需工具和版本
4. **避免系统特定功能**：使用可移植的 bash/Python 构造

### 维护

1. **一致的版本控制**：在 plugin.json 中更新版本
2. **优雅弃用**：移除前明确标记旧组件
3. **记录破坏性更改**：注意影响现有用户的更改
4. **彻底测试**：更改后验证所有组件正常工作

## 常见模式

### 最小插件

没有依赖的单个命令：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # 仅 name 字段
└── commands/
    └── hello.md       # 单个命令
```

### 功能完整的插件

包含所有组件类型的完整插件：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # 面向用户的命令
├── agents/            # 专业子代理
├── skills/            # 自动激活的技能
├── hooks/             # 事件处理器
│   ├── hooks.json
│   └── scripts/
├── .mcp.json          # 外部集成
└── scripts/           # 共享工具
```

### 技能聚焦的插件

仅提供技能的插件：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    └── skill-two/
        └── SKILL.md
```

## 故障排除

**组件未加载**：
- 验证文件位于正确目录且具有正确扩展名
- 检查 YAML frontmatter 语法（命令、代理、技能）
- 确保技能有 `SKILL.md`（不是 `README.md` 或其他名称）
- 确认插件在 Claude Code 设置中已启用

**路径解析错误**：
- 将所有硬编码路径替换为 `${CLAUDE_PLUGIN_ROOT}`
- 验证清单中的路径是相对路径且以 `./` 开头
- 检查引用的文件是否存在于指定路径
- 在钩子脚本中使用 `echo $CLAUDE_PLUGIN_ROOT` 测试

**自动发现不工作**：
- 确认目录位于插件根目录（不在 `.claude-plugin/` 内）
- 检查文件命名是否遵循约定（kebab-case、正确扩展名）
- 验证清单中的自定义路径是否正确
- 重启 Claude Code 以重新加载插件配置

**插件间冲突**：
- 使用唯一、描述性的组件名称
- 如需要，用插件名称为命令命名空间
- 在插件 README 中记录潜在冲突
- 考虑为相关功能使用命令前缀

---

有关详细示例和高级模式，请参阅 `references/` 和 `examples/` 目录中的文件。
