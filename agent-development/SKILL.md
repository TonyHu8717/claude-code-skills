---
name: agent-development
description: 当用户要求"创建代理"、"添加代理"、"编写子代理"、"代理前置信息"、"何时使用description"、"代理示例"、"代理工具"、"代理颜色"、"自主代理"，或需要关于代理结构、系统提示词、触发条件或Claude Code插件代理开发最佳实践的指导时，使用此技能。
version: 0.1.0
---

# Claude Code 插件代理开发

## 概述

代理是自主子进程，能够独立处理复杂的多步骤任务。理解代理结构、触发条件和系统提示词设计，可以创建强大的自主功能。

**核心概念：**
- 代理用于自主工作，命令用于用户发起的操作
- Markdown 文件格式，带有 YAML 前置信息
- 通过 description 字段触发，附带示例
- 系统提示词定义代理行为
- 模型和颜色自定义

## 代理文件结构

### 完整格式

```markdown
---
name: agent-identifier
description: Use this agent when [triggering conditions]. Typical triggers include [scenario 1 in prose], [scenario 2 in prose], and [scenario 3 in prose]. See "When to invoke" in the agent body for worked scenarios.
model: inherit
color: blue
tools: ["Read", "Write", "Grep"]
---

You are [agent role description]...

## When to invoke

[Two to four representative scenarios written as prose, e.g.:]
- **[Scenario name].** [What the situation looks like and what the agent should do.]
- **[Scenario name].** [Same.]

**Your Core Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]

**Analysis Process:**
[Step-by-step workflow]

**Output Format:**
[What to return]
```

## 前置信息字段

### name（必需）

代理标识符，用于命名空间和调用。

**格式：** 仅限小写字母、数字、连字符
**长度：** 3-50 个字符
**模式：** 必须以字母数字开头和结尾

**正确示例：**
- `code-reviewer`
- `test-generator`
- `api-docs-writer`
- `security-analyzer`

**错误示例：**
- `helper`（过于通用）
- `-agent-`（以连字符开头/结尾）
- `my_agent`（不允许下划线）
- `ag`（太短，少于 3 个字符）

### description（必需）

定义 Claude 何时触发此代理。**这是最关键的字段** —— 它会在代理注册时加载到上下文中，以便系统决定何时调度。

**必须包含：**
1. 触发条件（"Use this agent when..."）
2. 典型触发场景的简短文字描述
3. 指向代理正文中"When to invoke"部分的指引，以获取详细的工作场景

**格式：**
```
Use this agent when [conditions]. Typical triggers include [scenario 1 in prose], [scenario 2 in prose], and [scenario 3 in prose]. See "When to invoke" in the agent body for worked scenarios.
```

**最佳实践：**
- 在文字描述中列出 2-4 个触发场景
- 覆盖主动触发（助手自行调用）和被动触发（用户请求）
- 覆盖相同意图的不同表述方式
- 明确说明何时不应使用该代理
- 将详细场景放在正文中"When to invoke"部分，作为文字描述的项目列表

### model（必需）

代理应使用的模型。

**选项：**
- `inherit` - 使用与父级相同的模型（推荐）
- `sonnet` - Claude Sonnet（均衡型）
- `opus` - Claude Opus（最强能力，成本最高）
- `haiku` - Claude Haiku（快速，低成本）

**建议：** 除非代理需要特定模型能力，否则使用 `inherit`。

### color（必需）

代理在 UI 中的视觉标识符。

**选项：** `blue`、`cyan`、`green`、`yellow`、`magenta`、`red`

**指南：**
- 同一插件中的不同代理选择不同的颜色
- 相似类型的代理使用一致的颜色
- 蓝色/青色：分析、审查
- 绿色：面向成功的任务
- 黄色：警告、验证
- 红色：关键、安全
- 品红色：创意、生成

### tools（可选）

限制代理使用特定工具。

**格式：** 工具名称数组

```yaml
tools: ["Read", "Write", "Grep", "Bash"]
```

**默认：** 如果省略，代理可访问所有工具

**最佳实践：** 将工具限制为最少需要的数量（最小权限原则）

**常用工具集：**
- 只读分析：`["Read", "Grep", "Glob"]`
- 代码生成：`["Read", "Write", "Grep"]`
- 测试：`["Read", "Bash", "Grep"]`
- 完全访问：省略字段或使用 `["*"]`

## 系统提示词设计

Markdown 正文将成为代理的系统提示词。使用第二人称，直接对代理进行指示。

### 结构

**标准模板：**
```markdown
You are [role] specializing in [domain].

**Your Core Responsibilities:**
1. [Primary responsibility]
2. [Secondary responsibility]
3. [Additional responsibilities...]

**Analysis Process:**
1. [Step one]
2. [Step two]
3. [Step three]
[...]

**Quality Standards:**
- [Standard 1]
- [Standard 2]

**Output Format:**
Provide results in this format:
- [What to include]
- [How to structure]

**Edge Cases:**
Handle these situations:
- [Edge case 1]: [How to handle]
- [Edge case 2]: [How to handle]
```

### 最佳实践

**应该做的：**
- 使用第二人称写作（"You are..."、"You will..."）
- 明确说明职责
- 提供分步流程
- 定义输出格式
- 包含质量标准
- 处理边界情况
- 保持在 10,000 个字符以内

**不应该做的：**
- 使用第一人称写作（"I am..."、"I will..."）
- 含糊或通用
- 省略流程步骤
- 输出格式未定义
- 跳过质量指导
- 忽略错误情况

## 创建代理

### 方法 1：AI 辅助生成

使用此提示词模式（从 Claude Code 中提取）：

```
Create an agent configuration based on this request: "[YOUR DESCRIPTION]"

Requirements:
1. Extract core intent and responsibilities
2. Design expert persona for the domain
3. Create comprehensive system prompt with:
   - Clear behavioral boundaries
   - Specific methodologies
   - Edge case handling
   - Output format
   - A "When to invoke" section listing 2-4 trigger scenarios as prose bullets
4. Create identifier (lowercase, hyphens, 3-50 chars)
5. Write description with triggering conditions and a short prose summary of trigger scenarios

Return JSON with:
{
  "identifier": "agent-name",
  "whenToUse": "Use this agent when... Typical triggers include [...]. See \"When to invoke\" in the agent body.",
  "systemPrompt": "You are..."
}
```

然后转换为带前置信息的代理文件格式。

完整模板请参见 `examples/agent-creation-prompt.md`。

### 方法 2：手动创建

1. 选择代理标识符（3-50 个字符，小写字母、连字符）
2. 编写带示例的 description
3. 选择模型（通常为 `inherit`）
4. 选择颜色用于视觉识别
5. 定义工具（如需限制访问）
6. 按上述结构编写系统提示词
7. 保存为 `agents/agent-name.md`

## 验证规则

### 标识符验证

```
✅ 有效: code-reviewer, test-gen, api-analyzer-v2
❌ 无效: ag (太短), -start (以连字符开头), my_agent (包含下划线)
```

**规则：**
- 3-50 个字符
- 仅限小写字母、数字、连字符
- 必须以字母数字开头和结尾
- 不允许下划线、空格或特殊字符

### description 验证

**长度：** 10-5,000 个字符
**必须包含：** 触发条件和示例
**最佳：** 200-1,000 个字符，包含 2-4 个示例

### 系统提示词验证

**长度：** 20-10,000 个字符
**最佳：** 500-3,000 个字符
**结构：** 明确的职责、流程、输出格式

## 代理组织

### 插件代理目录

```
plugin-name/
└── agents/
    ├── analyzer.md
    ├── reviewer.md
    └── generator.md
```

`agents/` 目录中的所有 `.md` 文件都会被自动发现。

### 命名空间

代理会自动分配命名空间：
- 单个插件：`agent-name`
- 含子目录：`plugin:subdir:agent-name`

## 测试代理

### 测试触发

创建测试场景以验证代理是否正确触发：

1. 编写带有特定触发示例的代理
2. 在测试中使用与示例相似的措辞
3. 检查 Claude 是否加载了该代理
4. 验证代理是否提供预期功能

### 测试系统提示词

确保系统提示词完整：

1. 给代理一个典型任务
2. 检查它是否遵循流程步骤
3. 验证输出格式是否正确
4. 测试提示词中提到的边界情况
5. 确认满足质量标准

## 快速参考

### 最小代理

```markdown
---
name: simple-agent
description: Use this agent when [condition]. Typical triggers include [trigger 1] and [trigger 2]. See "When to invoke" in the agent body.
model: inherit
color: blue
---

You are an agent that [does X].

## When to invoke

- **[Scenario A].** [Description.]
- **[Scenario B].** [Description.]

Process:
1. [Step 1]
2. [Step 2]

Output: [What to provide]
```

### 前置信息字段汇总

| 字段 | 必需 | 格式 | 示例 |
|-------|------|------|---------|
| name | 是 | lowercase-hyphens | code-reviewer |
| description | 是 | 文字触发描述 | Use when... Typical triggers include... |
| model | 是 | inherit/sonnet/opus/haiku | inherit |
| color | 是 | 颜色名称 | blue |
| tools | 否 | 工具名称数组 | ["Read", "Grep"] |

### 最佳实践

**应该做的：**
- 在 description 中列出 2-4 个触发场景（文字形式）
- 将详细的工作场景放在正文的"When to invoke"部分，作为文字项目列表
- 编写明确的触发条件
- 除非有特定需求，否则使用 `inherit` 作为模型
- 选择适当的工具（最小权限）
- 编写清晰、结构化的系统提示词
- 彻底测试代理触发

**不应该做的：**
- 使用没有触发场景的通用描述
- 省略触发条件
- 给所有代理相同的颜色
- 授予不必要的工具访问权限
- 编写模糊的系统提示词
- 跳过测试

## 附加资源

### 参考文件

详细指导请查阅：

- **`references/system-prompt-design.md`** - 完整的系统提示词模式
- **`references/triggering-examples.md`** - 示例格式和最佳实践
- **`references/agent-creation-system-prompt.md`** - Claude Code 中的精确提示词

### 示例文件

`examples/` 中的工作示例：

- **`agent-creation-prompt.md`** - AI 辅助代理生成模板
- **`complete-agent-examples.md`** - 不同用例的完整代理示例

### 实用脚本

`scripts/` 中的开发工具：

- **`validate-agent.sh`** - 验证代理文件结构
- **`test-agent-trigger.sh`** - 测试代理是否正确触发

## 实现工作流程

为插件创建代理：

1. 定义代理目的和触发条件
2. 选择创建方法（AI 辅助或手动）
3. 创建 `agents/agent-name.md` 文件
4. 编写包含所有必需字段的前置信息
5. 按照最佳实践编写系统提示词
6. 在 description 中列出 2-4 个触发场景（文字形式），并在正文的"When to invoke"部分详细说明
7. 使用 `scripts/validate-agent.sh` 进行验证
8. 使用真实场景测试触发
9. 在插件 README 中记录代理

专注于明确的触发条件和全面的系统提示词，以实现自主运行。
