---
name: skill-development
description: 当用户想要"创建技能"、"向插件添加技能"、"编写新技能"、"改进技能描述"、"组织技能内容"，或需要关于 Claude Code 插件的技能结构、渐进式披露或技能开发最佳实践的指导时，应使用此技能。
version: 0.1.0
---

# Claude Code 插件的技能开发

此技能为创建有效的 Claude Code 插件技能提供指导。

## 关于技能

技能是模块化、自包含的包，通过提供专业知识、工作流和工具来扩展 Claude 的能力。将它们视为特定领域或任务的"入门指南" — 它们将 Claude 从通用代理转变为配备任何模型都无法完全拥有的程序性知识的专业代理。

### 技能提供什么

1. 专业工作流 — 特定领域的多步骤程序
2. 工具集成 — 处理特定文件格式或 API 的指令
3. 领域专业知识 — 公司特定知识、schema、业务逻辑
4. 捆绑资源 — 用于复杂和重复任务的脚本、参考和资产

### 技能剖析

每个技能由必需的 SKILL.md 文件和可选的捆绑资源组成：

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md（必需）

**元数据质量：**YAML 前置数据中的 `name` 和 `description` 决定 Claude 何时使用技能。具体说明技能做什么以及何时使用。使用第三人称（例如"当用户请求...'时应使用此技能"而不是"使用此技能当..."）。

#### 捆绑资源（可选）

##### 脚本（`scripts/`）

用于需要确定性可靠性或反复重写的任务的可执行代码（Python/Bash 等）。

- **何时包含**：当相同代码被反复重写或需要确定性可靠性时
- **示例**：用于 PDF 旋转任务的 `scripts/rotate_pdf.py`
- **好处**：Token 高效、确定性、可以不加载到上下文中执行
- **注意**：脚本可能仍需要被 Claude 读取以进行补丁或环境特定调整

##### 参考（`references/`）

旨在按需加载到上下文中以指导 Claude 的流程和思维的文档和参考资料。

- **何时包含**：用于 Claude 工作时应参考的文档
- **示例**：`references/finance.md` 用于财务 schema，`references/mnda.md` 用于公司 NDA 模板，`references/policies.md` 用于公司政策，`references/api_docs.md` 用于 API 规范
- **用例**：数据库 schema、API 文档、领域知识、公司政策、详细工作流指南
- **好处**：保持 SKILL.md 精简，仅在 Claude 确定需要时加载
- **最佳实践**：如果文件很大（>10k 词），在 SKILL.md 中包含 grep 搜索模式
- **避免重复**：信息应仅存在于 SKILL.md 或参考文件中，而不是两者。对于详细信息优先使用参考文件，除非它确实是技能的核心 — 这保持 SKILL.md 精简，同时使信息可发现而不占用上下文窗口。仅将基本程序指令和工作流指导保留在 SKILL.md 中；将详细参考资料、schema 和示例移到参考文件中。

##### 资产（`assets/`）

不打算加载到上下文中，而是在 Claude 产生的输出中使用的文件。

- **何时包含**：当技能需要在最终输出中使用的文件时
- **示例**：`assets/logo.png` 用于品牌资产，`assets/slides.pptx` 用于 PowerPoint 模板，`assets/frontend-template/` 用于 HTML/React 样板，`assets/font.ttf` 用于排版
- **用例**：模板、图像、图标、样板代码、字体、被复制或修改的示例文档
- **好处**：将输出资源与文档分离，使 Claude 能够使用文件而无需将它们加载到上下文中

### 渐进式披露设计原则

技能使用三级加载系统来高效管理上下文：

1. **元数据（name + description）** — 始终在上下文中（约 100 词）
2. **SKILL.md 正文** — 技能触发时（<5k 词）
3. **捆绑资源** — Claude 按需（无限制*）

*无限制，因为脚本可以不读入上下文窗口即执行。

## 技能创建流程

要创建技能，按顺序遵循"技能创建流程"，仅在有明确理由不适用时跳过步骤。

### 步骤 1：通过具体示例理解技能

仅在技能的使用模式已被清楚理解时跳过此步骤。即使处理现有技能，它仍然有价值。

要创建有效的技能，清楚理解技能将如何被使用的具体示例。这种理解可以来自直接的用户示例或经过用户反馈验证的生成示例。

例如，构建图像编辑器技能时，相关问题包括：

- "图像编辑器技能应该支持什么功能？编辑、旋转，还有别的吗？"
- "您能举一些这个技能将如何被使用的例子吗？"
- "我可以想象用户问诸如'从此图像中移除红眼'或'旋转此图像'的事情。您想象这个技能还有其他使用方式吗？"
- "用户会说什么应该触发这个技能？"

为避免压倒用户，避免在单个消息中询问太多问题。从最重要的问题开始，根据需要跟进以获得更好的效果。

当对技能应支持的功能有清晰认识时结束此步骤。

### 步骤 2：规划可复用技能内容

要将具体示例转化为有效技能，通过以下方式分析每个示例：

1. 考虑如何从头执行该示例
2. 识别在反复执行这些工作流时哪些脚本、参考资料和资产会有帮助

示例：构建 `pdf-editor` 技能处理"帮我旋转此 PDF"等查询时，分析显示：

1. 旋转 PDF 每次都需要重写相同的代码
2. `scripts/rotate_pdf.py` 脚本会有助于存储在技能中

示例：设计 `frontend-webapp-builder` 技能处理"为我构建一个 todo 应用"或"为我构建一个仪表板来跟踪我的步数"等查询时，分析显示：

1. 编写前端 webapp 每次都需要相同的样板 HTML/React
2. 包含样板 HTML/React 项目文件的 `assets/hello-world/` 模板会有助于存储在技能中

示例：构建 `big-query` 技能处理"今天有多少用户登录了？"等查询时，分析显示：

1. 查询 BigQuery 每次都需要重新发现表 schema 和关系
2. 记录表 schema 的 `references/schema.md` 文件会有助于存储在技能中

**对于 Claude Code 插件：**构建钩子技能时，分析显示：

1. 开发者反复需要验证 hooks.json 和测试钩子脚本
2. `scripts/validate-hook-schema.sh` 和 `scripts/test-hook.sh` 工具会有帮助
3. `references/patterns.md` 用于详细钩子模式以避免膨胀 SKILL.md

要建立技能的内容，分析每个具体示例以创建要包含的可复用资源列表：脚本、参考资料和资产。

### 步骤 3：创建技能结构

对于 Claude Code 插件，创建技能目录结构：

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

**注意：**与使用 `init_skill.py` 的通用 skill-creator 不同，插件技能直接在插件的 `skills/` 目录中创建，使用更简单的手动结构。

### 步骤 4：编辑技能

编辑（新创建或现有）技能时，请记住技能是为另一个 Claude 实例使用的。专注于包含对 Claude 有益且不明显的信息。考虑什么程序性知识、领域特定细节或可复用资产会帮助另一个 Claude 实例更有效地执行这些任务。

#### 从可复用技能内容开始

要开始实现，从上面识别的可复用资源开始：`scripts/`、`references/` 和 `assets/` 文件。注意此步骤可能需要用户输入。例如，实现 `brand-guidelines` 技能时，用户可能需要提供品牌资产或模板存储在 `assets/` 中，或文档存储在 `references/` 中。

此外，删除技能不需要的任何示例文件和目录。只创建您实际需要的目录（references/、examples/、scripts/）。

#### 更新 SKILL.md

**写作风格：**使用**祈使/不定式形式**（动词优先指令）编写整个技能，而不是第二人称。使用客观、教学语言（例如"To accomplish X, do Y"而不是"You should do X"或"If you need to do X"）。这保持了 AI 消费的一致性和清晰度。

**描述（前置数据）：**使用第三人称格式和特定触发短语：

```yaml
---
name: Skill Name
description: This skill should be used when the user asks to "specific phrase 1", "specific phrase 2", "specific phrase 3". Include exact phrases users would say that should trigger this skill. Be concrete and specific.
version: 0.1.0
---
```

**好描述示例：**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", "implement prompt-based hooks", or mentions hook events (PreToolUse, PostToolUse, Stop).
```

**差描述示例：**
```yaml
description: Use this skill when working with hooks.  # 错误人称，模糊
description: Load when user needs hook help.  # 非第三人称
description: Provides hook guidance.  # 无触发短语
```

要完成 SKILL.md 正文，回答以下问题：

1. 技能的目的是什么，用几句话？
2. 技能应该在什么时候使用？（在前置数据描述中包含具体触发器）
3. 在实践中，Claude 应该如何使用技能？上面开发的所有可复用技能内容都应被引用，以便 Claude 知道如何使用它们。

**保持 SKILL.md 精简：**正文目标 1,500-2,000 词。将详细内容移到 references/：
- 详细模式 → `references/patterns.md`
- 高级技术 → `references/advanced.md`
- 迁移指南 → `references/migration.md`
- API 参考 → `references/api-reference.md`

**在 SKILL.md 中引用资源：**
```markdown
## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:
- **`references/patterns.md`** - Common patterns
- **`references/advanced.md`** - Advanced use cases

### Example Files

Working examples in `examples/`:
- **`example-script.sh`** - Working example
```

### 步骤 5：验证和测试

**对于插件技能，验证与通用技能不同：**

1. **检查结构**：`plugin-name/skills/skill-name/` 中的技能目录
2. **验证 SKILL.md**：有包含 name 和 description 的前置数据
3. **检查触发短语**：描述包含特定用户查询
4. **验证写作风格**：正文使用祈使/不定式形式，非第二人称
5. **测试渐进式披露**：SKILL.md 精简（约 1,500-2,000 词），详细内容在 references/ 中
6. **检查引用**：所有引用文件存在
7. **验证示例**：示例完整且正确
8. **测试脚本**：脚本可执行且工作正确

**使用 skill-reviewer 代理：**
```
Ask: "Review my skill and check if it follows best practices"
```

skill-reviewer 代理将检查描述质量、内容组织和渐进式披露。

### 步骤 6：迭代

测试技能后，用户可能要求改进。通常这在使用技能后立即发生，具有技能如何执行的新鲜上下文。

**迭代工作流：**
1. 在真实任务上使用技能
2. 注意困难或低效之处
3. 识别 SKILL.md 或捆绑资源应如何更新
4. 实现更改并再次测试

**常见改进：**
- 加强描述中的触发短语
- 将长部分从 SKILL.md 移到 references/
- 添加缺失的示例或脚本
- 澄清模糊指令
- 添加边缘情况处理

## 插件特定考虑

### 插件中的技能位置

插件技能位于插件的 `skills/` 目录中：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
└── skills/
    └── my-skill/
        ├── SKILL.md
        ├── references/
        ├── examples/
        └── scripts/
```

### 自动发现

Claude Code 自动发现技能：
- 扫描 `skills/` 目录
- 查找包含 `SKILL.md` 的子目录
- 始终加载技能元数据（name + description）
- 技能触发时加载 SKILL.md 正文
- 需要时加载 references/examples

### 无需打包

插件技能作为插件的一部分分发，而不是单独的 ZIP 文件。用户安装插件时获得技能。

### 在插件中测试

通过本地安装插件测试技能：

```bash
# Test with --plugin-dir
cc --plugin-dir /path/to/plugin

# Ask questions that should trigger the skill
# Verify skill loads correctly
```

## Plugin-Dev 中的示例

研究此插件中的技能作为最佳实践示例：

**hook-development 技能：**
- 优秀的触发短语："create a hook"、"add a PreToolUse hook" 等
- 精简的 SKILL.md（1,651 词）
- 3 个 references/ 文件用于详细内容
- 3 个 examples/ 工作钩子
- 3 个 scripts/ 工具

**agent-development 技能：**
- 强触发器："create an agent"、"agent frontmatter" 等
- 聚焦的 SKILL.md（1,438 词）
- 参考包含 Claude Code 的 AI 生成提示
- 完整的代理示例

**plugin-settings 技能：**
- 特定触发器："plugin settings"、".local.md files"、"YAML frontmatter"
- 参考显示真实实现（multi-agent-swarm、ralph-loop）
- 工作解析脚本

每个都展示了渐进式披露和强触发。

## 实践中的渐进式披露

### 什么放在 SKILL.md 中

**包含（技能触发时始终加载）：**
- 核心概念和概览
- 基本程序和工作流
- 快速参考表
- 指向 references/examples/scripts 的指针
- 最常见用例

**保持在 3,000 词以内，理想 1,500-2,000 词**

### 什么放在 references/ 中

**移到 references/（按需加载）：**
- 详细模式和高级技术
- 全面的 API 文档
- 迁移指南
- 边缘情况和故障排除
- 大量示例和演练

**每个参考文件可以很大（2,000-5,000+ 词）**

### 什么放在 examples/ 中

**工作代码示例：**
- 完整、可运行的脚本
- 配置文件
- 模板文件
- 真实世界使用示例

**用户可以直接复制和调整这些**

### 什么放在 scripts/ 中

**工具脚本：**
- 验证工具
- 测试辅助器
- 解析工具
- 自动化脚本

**应该可执行且有文档**

## 写作风格要求

### 祈使/不定式形式

使用动词优先指令编写，而不是第二人称：

**正确（祈使）：**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
```

**不正确（第二人称）：**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

### 描述中的第三人称

前置数据描述必须使用第三人称：

**正确：**
```yaml
description: This skill should be used when the user asks to "create X", "configure Y"...
```

**不正确：**
```yaml
description: Use this skill when you want to create X...
description: Load this skill when user asks...
```

### 客观、教学语言

专注于做什么，而不是谁应该做：

**正确：**
```
Parse the frontmatter using sed.
Extract fields with grep.
Validate values before use.
```

**不正确：**
```
You can parse the frontmatter...
Claude should extract fields...
The user might validate values...
```

## 验证检查清单

最终确定技能前：

**结构：**
- [ ] SKILL.md 文件存在且有有效的 YAML 前置数据
- [ ] 前置数据有 `name` 和 `description` 字段
- [ ] Markdown 正文存在且有实质内容
- [ ] 引用文件实际存在

**描述质量：**
- [ ] 使用第三人称（"当用户请求...'时应使用此技能"）
- [ ] 包含用户会说的特定触发短语
- [ ] 列出具体场景（"create X"、"configure Y"）
- [ ] 不模糊或泛泛

**内容质量：**
- [ ] SKILL.md 正文使用祈使/不定式形式
- [ ] 正文聚焦且精简（理想 1,500-2,000 词，<5k 最大）
- [ ] 详细内容移到 references/
- [ ] 示例完整且可用
- [ ] 脚本可执行且有文档

**渐进式披露：**
- [ ] 核心概念在 SKILL.md 中
- [ ] 详细文档在 references/ 中
- [ ] 工作代码在 examples/ 中
- [ ] 工具在 scripts/ 中
- [ ] SKILL.md 引用这些资源

**测试：**
- [ ] 技能在预期用户查询上触发
- [ ] 内容对预期任务有帮助
- [ ] 跨文件无重复信息
- [ ] 需要时加载引用

## 常见错误避免

### 错误 1：弱触发描述

**差：**
```yaml
description: Provides guidance for working with hooks.
```

**为什么差：**模糊，无特定触发短语，非第三人称

**好：**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```

**为什么好：**第三人称，特定短语，具体场景

### 错误 2：SKILL.md 中内容过多

**差：**
```
skill-name/
└── SKILL.md  (8,000 words - everything in one file)
```

**为什么差：**技能加载时膨胀上下文，详细内容始终加载

**好：**
```
skill-name/
├── SKILL.md  (1,800 words - core essentials)
└── references/
    ├── patterns.md (2,500 words)
    └── advanced.md (3,700 words)
```

**为什么好：**渐进式披露，详细内容仅在需要时加载

### 错误 3：第二人称写作

**差：**
```markdown
You should start by reading the configuration file.
You need to validate the input.
You can use the grep tool to search.
```

**为什么差：**第二人称，非祈使形式

**好：**
```markdown
Start by reading the configuration file.
Validate the input before processing.
Use the grep tool to search for patterns.
```

**为什么好：**祈使形式，直接指令

### 错误 4：缺少资源引用

**差：**
```markdown
# SKILL.md

[Core content]

[No mention of references/ or examples/]
```

**为什么差：**Claude 不知道引用存在

**好：**
```markdown
# SKILL.md

[Core content]

## Additional Resources

### Reference Files
- **`references/patterns.md`** - Detailed patterns
- **`references/advanced.md`** - Advanced techniques

### Examples
- **`examples/script.sh`** - Working example
```

**为什么好：**Claude 知道在哪里找到额外信息

## 快速参考

### 最小技能

```
skill-name/
└── SKILL.md
```

适用于：简单知识，不需要复杂资源

### 标准技能（推荐）

```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

适用于：大多数具有详细文档的插件技能

### 完整技能

```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```

适用于：具有验证工具的复杂领域

## 最佳实践总结

**应该做的：**
- 描述中使用第三人称（"当用户请求...'时应使用此技能"）
- 包含特定触发短语（"create X"、"configure Y"）
- 保持 SKILL.md 精简（1,500-2,000 词）
- 使用渐进式披露（将详细内容移到 references/）
- 使用祈使/不定式形式编写
- 清晰引用支持文件
- 提供工作示例
- 为常见操作创建工具脚本
- 研究 plugin-dev 的技能作为模板

**不应该做的：**
- 在任何地方使用第二人称
- 有模糊的触发条件
- 将所有内容放在 SKILL.md 中（>3,000 词无 references/）
- 使用第二人称编写（"You should..."）
- 不引用资源
- 包含损坏或不完整的示例
- 跳过验证

## 实现工作流

为插件创建技能：

1. **理解用例**：识别技能使用的具体示例
2. **规划资源**：确定需要什么 scripts/references/examples
3. **创建结构**：`mkdir -p skills/skill-name/{references,examples,scripts}`
4. **编写 SKILL.md**：
   - 前置数据包含第三人称描述和触发短语
   - 精简正文（1,500-2,000 词）使用祈使形式
   - 引用支持文件
5. **添加资源**：根据需要创建 references/、examples/、scripts/
6. **验证**：检查描述、写作风格、组织
7. **测试**：验证技能在预期触发器上加载
8. **迭代**：基于使用进行改进

专注于强触发描述、渐进式披露和祈使写作风格，以创建在需要时加载并提供针对性指导的有效技能。
