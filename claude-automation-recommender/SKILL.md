---
name: claude-automation-recommender
description: 分析代码库并推荐 Claude Code 自动化（钩子、子代理、技能、插件、MCP 服务器）。当用户要求自动化推荐、想优化 Claude Code 设置、提到改进 Claude Code 工作流、询问如何为项目首次设置 Claude Code 或想知道应该使用哪些 Claude Code 功能时使用。
tools: Read, Glob, Grep, Bash
---

# Claude 自动化推荐器

分析代码库模式以推荐量身定制的 Claude Code 自动化，涵盖所有可扩展性选项。

**此技能为只读。** 它分析代码库并输出推荐。它不创建或修改任何文件。用户自行实施推荐或要求 Claude 协助构建。

## 输出指南

- **每种类型推荐 1-2 个**：不要压倒用户 — 每个类别只展示最有价值的 1-2 个自动化
- **如果用户要求特定类型**：仅关注该类型并提供更多选项（3-5 个推荐）
- **超越参考列表**：参考文件包含常见模式，但使用网络搜索查找特定于代码库工具、框架和库的推荐
- **告诉用户可以要求更多**：最后说明他们可以请求任何特定类别的更多推荐

## 自动化类型概述

| 类型 | 最适合 |
|------|--------|
| **钩子** | 工具事件的自动操作（格式化保存、lint、阻止编辑） |
| **子代理** | 专门的审查器/分析器，可并行运行 |
| **技能** | 打包的专业知识、工作流和可重复任务（由 Claude 或用户通过 `/skill-name` 调用） |
| **插件** | 可安装的技能集合 |
| **MCP 服务器** | 外部工具集成（数据库、API、浏览器、文档） |

## 工作流程

### 阶段 1：代码库分析

收集项目上下文：

```bash
# 检测项目类型和工具
ls -la package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null
cat package.json 2>/dev/null | head -50

# 检查依赖以获取 MCP 服务器推荐
cat package.json 2>/dev/null | grep -E '"(react|vue|angular|next|express|fastapi|django|prisma|supabase|stripe)"'

# 检查现有 Claude Code 配置
ls -la .claude/ CLAUDE.md 2>/dev/null

# 分析项目结构
ls -la src/ app/ lib/ tests/ components/ pages/ api/ 2>/dev/null
```

**要捕获的关键指标：**

| 类别 | 要查找的内容 | 为推荐提供信息 |
|------|-------------|----------------|
| 语言/框架 | package.json、pyproject.toml、导入模式 | 钩子、MCP 服务器 |
| 前端栈 | React、Vue、Angular、Next.js | Playwright MCP、前端技能 |
| 后端栈 | Express、FastAPI、Django | API 文档工具 |
| 数据库 | Prisma、Supabase、原生 SQL | 数据库 MCP 服务器 |
| 外部 API | Stripe、OpenAI、AWS SDK | context7 MCP 获取文档 |
| 测试 | Jest、pytest、Playwright 配置 | 测试钩子、子代理 |
| CI/CD | GitHub Actions、CircleCI | GitHub MCP 服务器 |
| 问题跟踪 | Linear、Jira 引用 | 问题跟踪器 MCP |
| 文档模式 | OpenAPI、JSDoc、docstring | 文档技能 |

### 阶段 2：生成推荐

基于分析，生成所有类别的推荐：

#### A. MCP 服务器推荐

参见 [references/mcp-servers.md](references/mcp-servers.md) 获取详细模式。

| 代码库信号 | 推荐的 MCP 服务器 |
|-----------|-------------------|
| 使用流行库（React、Express 等） | **context7** — 实时文档查询 |
| 带 UI 测试需求的前端 | **Playwright** — 浏览器自动化/测试 |
| 使用 Supabase | **Supabase MCP** — 直接数据库操作 |
| PostgreSQL/MySQL 数据库 | **Database MCP** — 查询和 schema 工具 |
| GitHub 仓库 | **GitHub MCP** — Issues、PR、actions |
| 使用 Linear 管理问题 | **Linear MCP** — 问题管理 |
| AWS 基础设施 | **AWS MCP** — 云资源管理 |
| Slack 工作区 | **Slack MCP** — 团队通知 |
| 记忆/上下文持久化 | **Memory MCP** — 跨会话记忆 |
| Sentry 错误跟踪 | **Sentry MCP** — 错误调查 |
| Docker 容器 | **Docker MCP** — 容器管理 |

#### B. 技能推荐

参见 [references/skills-reference.md](references/skills-reference.md) 获取详情。

在 `.claude/skills/<name>/SKILL.md` 中创建技能。某些也可通过插件获得：

| 代码库信号 | 技能 | 插件 |
|-----------|------|------|
| 构建插件 | skill-development | plugin-dev |
| Git 提交 | commit | commit-commands |
| React/Vue/Angular | frontend-design | frontend-design |
| 自动化规则 | writing-rules | hookify |
| 功能规划 | feature-dev | feature-dev |

**要创建的自定义技能**（带模板、脚本、示例）：

| 代码库信号 | 要创建的技能 | 调用方式 |
|-----------|-------------|----------|
| API 路由 | **api-doc**（带 OpenAPI 模板） | 两者 |
| 数据库项目 | **create-migration**（带验证脚本） | 仅用户 |
| 测试套件 | **gen-test**（带示例测试） | 仅用户 |
| 组件库 | **new-component**（带模板） | 仅用户 |
| PR 工作流 | **pr-check**（带清单） | 仅用户 |
| 发布 | **release-notes**（带 git 上下文） | 仅用户 |
| 代码风格 | **project-conventions** | 仅 Claude |
| 入门 | **setup-dev**（带前置脚本） | 仅用户 |

#### C. 钩子推荐

参见 [references/hooks-patterns.md](references/hooks-patterns.md) 获取配置。

| 代码库信号 | 推荐的钩子 |
|-----------|-----------|
| 配置了 Prettier | PostToolUse：编辑时自动格式化 |
| 配置了 ESLint/Ruff | PostToolUse：编辑时自动 lint |
| TypeScript 项目 | PostToolUse：编辑时类型检查 |
| 存在 tests 目录 | PostToolUse：运行相关测试 |
| 存在 `.env` 文件 | PreToolUse：阻止 `.env` 编辑 |
| 存在锁文件 | PreToolUse：阻止锁文件编辑 |
| 安全敏感代码 | PreToolUse：要求确认 |

#### D. 子代理推荐

参见 [references/subagent-templates.md](references/subagent-templates.md) 获取模板。

| 代码库信号 | 推荐的子代理 |
|-----------|-------------|
| 大型代码库（>500 文件） | **code-reviewer** — 并行代码审查 |
| 认证/支付代码 | **security-reviewer** — 安全审计 |
| API 项目 | **api-documenter** — OpenAPI 生成 |
| 性能关键 | **performance-analyzer** — 瓶颈检测 |
| 前端密集 | **ui-reviewer** — 无障碍审查 |
| 需要更多测试 | **test-writer** — 测试生成 |

#### E. 插件推荐

参见 [references/plugins-reference.md](references/plugins-reference.md) 获取可用插件。

| 代码库信号 | 推荐的插件 |
|-----------|-----------|
| 通用生产力 | **anthropic-agent-skills** — 核心技能包 |
| 文档工作流 | 安装 docx、xlsx、pdf 技能 |
| 前端开发 | **frontend-design** 插件 |
| 构建 AI 工具 | **mcp-builder** 用于 MCP 开发 |

### 阶段 3：输出推荐报告

清晰格式化推荐。**每类仅包含 1-2 个推荐** — 对此代码库最有价值的。跳过不相关的类别。

```markdown
## Claude Code 自动化推荐

我已分析您的代码库并为每个类别确定了顶级自动化。以下是我每种类型的前 1-2 个推荐：

### 代码库概况
- **类型**：[检测到的语言/运行时]
- **框架**：[检测到的框架]
- **关键库**：[检测到的相关库]

---

### MCP 服务器

#### context7
**原因**：[基于检测到的库的具体原因]
**安装**：`claude mcp add context7`

---

### 技能

#### [技能名称]
**原因**：[具体原因]
**创建**：`.claude/skills/[name]/SKILL.md`
**调用方式**：仅用户 / 两者 / 仅 Claude
**也可在**：[plugin-name] 插件中获得（如适用）
```yaml
---
name: [skill-name]
description: [功能描述]
disable-model-invocation: true  # 仅用户
---
```

---

### 钩子

#### [钩子名称]
**原因**：[基于检测到的配置的具体原因]
**位置**：`.claude/settings.json`

---

### 子代理

#### [代理名称]
**原因**：[基于代码库模式的具体原因]
**位置**：`.claude/agents/[name].md`

---

**想要更多？** 请求任何特定类别的更多推荐（例如"显示更多 MCP 服务器选项"或"还有哪些钩子会有帮助？"）。

**想要帮助实施任何这些？** 只需询问，我可以帮助您设置上述任何推荐。
```

## 决策框架

### 何时推荐 MCP 服务器
- 需要外部服务集成（数据库、API）
- 库/SDK 的文档查询
- 浏览器自动化或测试
- 团队工具集成（GitHub、Linear、Slack）
- 云基础设施管理

### 何时推荐技能

- 文档生成（docx、xlsx、pptx、pdf — 也在插件中）
- 频繁重复的提示或工作流
- 带参数的项目特定任务
- 将模板或脚本应用于任务（技能可打包支持文件）
- 通过 `/skill-name` 调用的快速操作
- 应在隔离中运行的工作流（`context: fork`）

**调用控制：**
- `disable-model-invocation: true` — 仅用户（用于副作用：部署、提交、发送）
- `user-invocable: false` — 仅 Claude（用于后台知识）
- 默认（省略两者） — 两者都可调用

### 何时推荐钩子
- 重复的编辑后操作（格式化、lint）
- 保护规则（阻止敏感文件编辑）
- 验证检查（测试、类型检查）

### 何时推荐子代理
- 需要专业知识（安全、性能）
- 并行审查工作流
- 后台质量检查

### 何时推荐插件
- 需要多个相关技能
- 想要预打包的自动化包
- 团队范围的标准化

---

## 配置提示

### MCP 服务器设置

**团队共享**：将 `.mcp.json` 检入仓库，使整个团队获得相同的 MCP 服务器

**调试**：使用 `--mcp-debug` 标志识别配置问题

**推荐的前置条件：**
- GitHub CLI（`gh`）— 启用原生 GitHub 操作
- Puppeteer/Playwright CLI — 用于浏览器 MCP 服务器

### 无头模式（用于 CI/自动化）

为自动化管道推荐无头 Claude：

```bash
# 预提交钩子示例
claude -p "fix lint errors in src/" --allowedTools Edit,Write

# 带结构化输出的 CI 管道
claude -p "<prompt>" --output-format stream-json | your_command
```

### 钩子权限

在 `.claude/settings.json` 中配置允许的工具：

```json
{
  "permissions": {
    "allow": ["Edit", "Write", "Bash(npm test:*)", "Bash(git commit:*)"]
  }
}
```
