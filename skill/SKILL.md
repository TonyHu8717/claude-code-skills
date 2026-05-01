---
name: skill
description: 管理本地技能 — 列表、添加、删除、搜索、编辑、设置向导
argument-hint: "<command> [args]"
level: 2
---

# 技能管理 CLI

用于通过类 CLI 命令管理 oh-my-claudecode 技能的元技能。

## 子命令

### /skill list

显示按范围组织的所有可用技能。

**行为：**
1. 扫描插件 `skills/` 目录中的捆绑内置技能（只读）
2. 扫描 `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/omc-learned/` 中的用户技能
3. 扫描 `.omc/skills/` 中的项目技能
4. 解析 YAML 前置数据获取元数据
5. 以有组织的表格格式显示：

```
BUILT-IN SKILLS (bundled with oh-my-claudecode):
| Name              | Description                    | Scope    |
|-------------------|--------------------------------|----------|
| visual-verdict    | Structured visual QA verdicts  | built-in |
| ralph             | Persistence loop               | built-in |

USER SKILLS (~/.claude/skills/omc-learned/):
| Name              | Triggers           | Quality | Usage | Scope |
|-------------------|--------------------|---------|-------|-------|
| error-handler     | fix, error         | 95%     | 42    | user  |
| api-builder       | api, endpoint      | 88%     | 23    | user  |

PROJECT SKILLS (.omc/skills/):
| Name              | Triggers           | Quality | Usage | Scope   |
|-------------------|--------------------|---------|-------|---------|
| test-runner       | test, run          | 92%     | 15    | project |
```

**回退：**如果质量/使用统计不可用，显示 "N/A"

**内置技能说明：**内置技能与 oh-my-claudecode 捆绑，可发现/可读取，但不能通过 `/skill remove` 或 `/skill edit` 移除或编辑。

---

### /skill add [name]

创建新技能的交互式向导。

**行为：**
1. **询问技能名称**（如果命令中未提供）
   - 验证：小写、仅连字符、无空格
2. **询问描述**
   - 清晰、简洁的一行
3. **询问触发器**（逗号分隔的关键词）
   - 示例："error, fix, debug"
4. **询问参数提示**（可选）
   - 示例："<file> [options]"
5. **询问范围：**
   - `user` → `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/omc-learned/<name>/SKILL.md`
   - `project` → `.omc/skills/<name>/SKILL.md`
6. **创建技能文件**使用模板：

```yaml
---
name: <name>
description: <description>
triggers:
  - <trigger1>
  - <trigger2>
argument-hint: "<args>"
---

# <Name> Skill

## Purpose

[Describe what this skill does]

## When to Activate

[Describe triggers and conditions]

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Examples

```
/oh-my-claudecode:<name> example-arg
```

## Notes

[Additional context, edge cases, gotchas]
```

7. **报告成功**及文件路径
8. **建议：**"Edit `/skill edit <name>` to customize content"

**示例：**
```
User: /skill add custom-logger
Assistant: Creating new skill 'custom-logger'...

Description: Enhanced logging with structured output
Triggers (comma-separated): log, logger, logging
Argument hint (optional): <level> [message]
Scope (user/project): user

✓ Created skill at ~/.claude/skills/omc-learned/custom-logger/SKILL.md
→ Edit with: /skill edit custom-logger
```

---

### /skill remove <name>

按名称移除技能。

**行为：**
1. **搜索技能**在两个范围中：
   - `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/omc-learned/<name>/SKILL.md`
   - `.omc/skills/<name>/SKILL.md`
2. **如果找到：**
   - 显示技能信息（name、description、scope）
   - **请求确认：**"Delete '<name>' skill from <scope>? (yes/no)"
3. **如果确认：**
   - 删除整个技能目录（例如 `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/omc-learned/<name>/`）
   - 报告："✓ Removed skill '<name>' from <scope>"
4. **如果未找到：**
   - 报告："✗ Skill '<name>' not found in user or project scope"

**安全：**没有明确用户确认绝不删除。

**示例：**
```
User: /skill remove old-logger
Assistant: Found skill 'old-logger' in user scope:
  Description: Legacy logging utility
  Scope: user (~/.claude/skills/omc-learned/)

Delete 'old-logger' skill? (yes/no)

User: yes
Assistant: ✓ Removed skill 'old-logger' from user scope
```

---

### /skill edit <name>

交互式编辑现有技能。

**行为：**
1. **查找技能**按名称（搜索两个范围）
2. **读取当前内容**通过 Read 工具
3. **显示当前值：**
   ```
   Current skill 'custom-logger':
   - Description: Enhanced logging with structured output
   - Triggers: log, logger, logging
   - Argument hint: <level> [message]
   - Scope: user
   ```
4. **询问要更改什么：**
   - `description` - 更新描述
   - `triggers` - 更新触发关键词
   - `argument-hint` - 更新参数提示
   - `content` - 编辑完整 markdown 内容
   - `rename` - 重命名技能（移动文件）
   - `cancel` - 退出不更改
5. **对于选定字段：**
   - 显示当前值
   - 询问新值
   - 更新 YAML 前置数据或内容
   - 写回文件
6. **报告成功**及变更摘要

**示例：**
```
User: /skill edit custom-logger
Assistant: Current skill 'custom-logger':
  - Description: Enhanced logging with structured output
  - Triggers: log, logger, logging
  - Argument hint: <level> [message]

What would you like to edit? (description/triggers/argument-hint/content/rename/cancel)

User: triggers
Assistant: Current triggers: log, logger, logging
New triggers (comma-separated): log, logger, logging, trace

✓ Updated triggers for 'custom-logger'
```

---

### /skill search <query>

按内容、触发器、名称或描述搜索技能。

**行为：**
1. **扫描所有技能**在两个范围中
2. **匹配查询**（不区分大小写）对：
   - 技能名称
   - 描述
   - 触发器
   - 完整 markdown 内容
3. **显示匹配**及上下文：

```
Found 3 skills matching "typescript error":

1. typescript-fixer (user)
   Description: Fix common TypeScript errors
   Match: "typescript error handling patterns"

2. error-handler (user)
   Description: Generic error handling utilities
   Match: "Supports TypeScript and JavaScript errors"

3. lint-fix (project)
   Description: Auto-fix linting errors
   Match: "TypeScript ESLint error resolution"
```

**排名：**优先 name/triggers 中的匹配而不是内容匹配

**示例：**
```
User: /skill search api endpoint
Assistant: Found 2 skills matching "api endpoint":

1. api-builder (user)
   Description: Generate REST API endpoints
   Triggers: api, endpoint, rest

2. backend-scaffold (project)
   Description: Scaffold backend services
   Match: "Creates API endpoint boilerplate"
```

---

### /skill info <name>

显示技能的详细信息。

**行为：**
1. **查找技能**按名称（搜索两个范围）
2. **解析 YAML 前置数据**和内容
3. **显示完整详情：**

```
Skill: custom-logger
Scope: user (~/.claude/skills/omc-learned/custom-logger/)
Description: Enhanced logging with structured output
Triggers: log, logger, logging
Argument Hint: <level> [message]
Quality: 95% (if available)
Usage Count: 42 times (if available)
File Path: /home/user/.claude/skills/omc-learned/custom-logger/SKILL.md

--- FULL CONTENT ---
[entire markdown content]
```

**如果未找到：**报告错误并建议使用 `/skill search`

**示例：**
```
User: /skill info custom-logger
Assistant: Skill: custom-logger
Scope: user
Description: Enhanced logging with structured output
Triggers: log, logger, logging
File: ~/.claude/skills/omc-learned/custom-logger/SKILL.md

--- CONTENT ---
# Custom Logger Skill

## Purpose
Enhanced logging with structured JSON output...
[rest of content]
```

---

### /skill sync

在用户和项目范围之间同步技能。

**行为：**
1. **扫描两个范围：**
   - 用户技能：`${CLAUDE_CONFIG_DIR:-~/.claude}/skills/omc-learned/`
   - 项目技能：`.omc/skills/`
2. **比较和分类：**
   - 仅用户技能（不在项目中）
   - 仅项目技能（不在用户中）
   - 公共技能（两者都有）
3. **显示同步机会：**

```
SYNC REPORT:

User-only skills (5):
  - error-handler
  - api-builder
  - custom-logger
  - test-generator
  - deploy-helper

Project-only skills (2):
  - test-runner
  - backend-scaffold

Common skills (3):
  - frontend-ui-ux
  - git-master
  - planner

Options:
  [1] Copy user skill to project
  [2] Copy project skill to user
  [3] View differences
  [4] Cancel
```

4. **处理用户选择：**
   - 选项 1：选择要复制到项目的技能
   - 选项 2：选择要复制到用户的技能
   - 选项 3：为公共技能显示并排差异
   - 选项 4：退出

**安全：**没有确认绝不覆盖

**示例：**
```
User: /skill sync
Assistant: Found 5 user-only skills and 2 project-only skills.

Copy 'error-handler' from user to project? (yes/no/skip)
User: yes
Assistant: ✓ Copied 'error-handler' to .omc/skills/

Copy 'api-builder' from user to project? (yes/no/skip)
User: skip
...
```

---

### /skill setup

用于设置和管理本地技能的交互式向导（原 local-skills-setup）。

**行为：**

#### 步骤 1：目录检查和设置

首先，检查技能目录是否存在，如果需要则创建：

```bash
# Check and create user-level skills directory
USER_SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/omc-learned"
if [ -d "$USER_SKILLS_DIR" ]; then
  echo "User skills directory exists: $USER_SKILLS_DIR"
else
  mkdir -p "$USER_SKILLS_DIR"
  echo "Created user skills directory: $USER_SKILLS_DIR"
fi

# Check and create project-level skills directory
PROJECT_SKILLS_DIR=".omc/skills"
if [ -d "$PROJECT_SKILLS_DIR" ]; then
  echo "Project skills directory exists: $PROJECT_SKILLS_DIR"
else
  mkdir -p "$PROJECT_SKILLS_DIR"
  echo "Created project skills directory: $PROJECT_SKILLS_DIR"
fi
```

#### 步骤 2：技能扫描和清单

扫描两个目录并显示全面清单：

```bash
# Scan user-level skills
echo "=== USER-LEVEL SKILLS (~/.claude/skills/omc-learned/) ==="
if [ -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/omc-learned" ]; then
  USER_COUNT=$(find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/omc-learned" -name "*.md" 2>/dev/null | wc -l)
  echo "Total skills: $USER_COUNT"

  if [ $USER_COUNT -gt 0 ]; then
    echo ""
    echo "Skills found:"
    find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/omc-learned" -name "*.md" -type f -exec sh -c '
      FILE="$1"
      NAME=$(grep -m1 "^name:" "$FILE" 2>/dev/null | sed "s/name: //")
      DESC=$(grep -m1 "^description:" "$FILE" 2>/dev/null | sed "s/description: //")
      MODIFIED=$(stat -c "%y" "$FILE" 2>/dev/null || stat -f "%Sm" "$FILE" 2>/dev/null)
      echo "  - $NAME"
      [ -n "$DESC" ] && echo "    Description: $DESC"
      echo "    Modified: $MODIFIED"
      echo ""
    ' sh {} \;
  fi
else
  echo "Directory not found"
fi

echo ""
echo "=== PROJECT-LEVEL SKILLS (.omc/skills/) ==="
if [ -d ".omc/skills" ]; then
  PROJECT_COUNT=$(find ".omc/skills" -name "*.md" 2>/dev/null | wc -l)
  echo "Total skills: $PROJECT_COUNT"

  if [ $PROJECT_COUNT -gt 0 ]; then
    echo ""
    echo "Skills found:"
    find ".omc/skills" -name "*.md" -type f -exec sh -c '
      FILE="$1"
      NAME=$(grep -m1 "^name:" "$FILE" 2>/dev/null | sed "s/name: //")
      DESC=$(grep -m1 "^description:" "$FILE" 2>/dev/null | sed "s/description: //")
      MODIFIED=$(stat -c "%y" "$FILE" 2>/dev/null || stat -f "%Sm" "$FILE" 2>/dev/null)
      echo "  - $NAME"
      [ -n "$DESC" ] && echo "    Description: $DESC"
      echo "    Modified: $MODIFIED"
      echo ""
    ' sh {} \;
  fi
else
  echo "Directory not found"
fi

# Summary
TOTAL=$((USER_COUNT + PROJECT_COUNT))
echo "=== SUMMARY ==="
echo "Total skills across all directories: $TOTAL"
```

#### 步骤 3：快速操作菜单

扫描后，使用 AskUserQuestion 工具提供这些选项：

**问题：**"What would you like to do with your local skills?"

**选项：**
1. **添加新技能** — 启动技能创建向导（调用 `/skill add`）
2. **列出所有技能详情** — 显示全面技能清单（调用 `/skill list`）
3. **扫描对话寻找模式** — 分析当前对话寻找适合技能的模式
4. **导入技能** — 从 URL 导入技能或粘贴内容
5. **完成** — 退出向导

**选项 3：扫描对话寻找模式**

分析当前对话上下文以识别潜在的适合技能的模式。查找：
- 具有非明显解决方案的最近调试会话
- 需要调查的棘手错误
- 发现的代码库特定解决方法
- 花时间解决的错误模式

报告发现并询问用户是否想提取任何作为技能（如果是则调用 `/learner`）。

**选项 4：导入技能**

要求用户提供：
- **URL**：从 URL 下载技能（例如 GitHub gist）
- **粘贴内容**：直接粘贴技能 markdown 内容

然后询问范围：
- **用户级**（~/.claude/skills/omc-learned/）— 跨所有项目可用
- **项目级**（.omc/skills/）— 仅用于此项目

验证技能格式并保存到选定位置。

---

### /skill scan

扫描两个技能目录的快速命令（`/skill setup` 的子集）。

**行为：**
运行 `/skill setup` 步骤 2 的扫描，不带交互式向导。

---

## 技能模板

通过 `/skill add` 或 `/skill setup` 创建技能时，为常见技能类型提供快速模板：

### 错误解决方案模板

```markdown
---
id: error-[unique-id]
name: [Error Name]
description: Solution for [specific error in specific context]
source: conversation
triggers: ["error message fragment", "file path", "symptom"]
quality: high
---

# [Error Name]

## The Insight
What is the underlying cause of this error? What principle did you discover?

## Why This Matters
What goes wrong if you don't know this? What symptom led here?

## Recognition Pattern
How do you know when this applies? What are the signs?
- Error message: "[exact error]"
- File: [specific file path]
- Context: [when does this occur]

## The Approach
Step-by-step solution:
1. [Specific action with file/line reference]
2. [Specific action with file/line reference]
3. [Verification step]

## Example
\`\`\`typescript
// Before (broken)
[problematic code]

// After (fixed)
[corrected code]
\`\`\`
```

### 工作流技能模板

```markdown
---
id: workflow-[unique-id]
name: [Workflow Name]
description: Process for [specific task in this codebase]
source: conversation
triggers: ["task description", "file pattern", "goal keyword"]
quality: high
---

# [Workflow Name]

## The Insight
What makes this workflow different from the obvious approach?

## Why This Matters
What fails if you don't follow this process?

## Recognition Pattern
When should you use this workflow?
- Task type: [specific task]
- Files involved: [specific patterns]
- Indicators: [how to recognize]

## The Approach
1. [Step with specific commands/files]
2. [Step with specific commands/files]
3. [Verification]

## Gotchas
- [Common mistake and how to avoid it]
- [Edge case and how to handle it]
```

### 代码模式模板

```markdown
---
id: pattern-[unique-id]
name: [Pattern Name]
description: Pattern for [specific use case in this codebase]
source: conversation
triggers: ["code pattern", "file type", "problem domain"]
quality: high
---

# [Pattern Name]

## The Insight
What's the key principle behind this pattern?

## Why This Matters
What problems does this pattern solve in THIS codebase?

## Recognition Pattern
When do you apply this pattern?
- File types: [specific files]
- Problem: [specific problem]
- Context: [codebase-specific context]

## The Approach
Decision-making heuristic, not just code:
1. [Principle-based step]
2. [Principle-based step]

## Example
\`\`\`typescript
[Illustrative example showing the principle]
\`\`\`

## Anti-Pattern
What NOT to do and why:
\`\`\`typescript
[Common mistake to avoid]
\`\`\`
```

### 集成技能模板

```markdown
---
id: integration-[unique-id]
name: [Integration Name]
description: How [system A] integrates with [system B] in this codebase
source: conversation
triggers: ["system name", "integration point", "config file"]
quality: high
---

# [Integration Name]

## The Insight
What's non-obvious about how these systems connect?

## Why This Matters
What breaks if you don't understand this integration?

## Recognition Pattern
When are you working with this integration?
- Files: [specific integration files]
- Config: [specific config locations]
- Symptoms: [what indicates integration issues]

## The Approach
How to work with this integration correctly:
1. [Configuration step with file paths]
2. [Setup step with specific details]
3. [Verification step]

## Gotchas
- [Integration-specific pitfall #1]
- [Integration-specific pitfall #2]
```

---

## 错误处理

**所有命令必须处理：**
- 文件/目录不存在
- 权限错误
- 无效的 YAML 前置数据
- 重复的技能名称
- 无效的技能名称（空格、特殊字符）

**错误格式：**
```
✗ Error: <clear message>
→ Suggestion: <helpful next step>
```

---

## 使用示例

```bash
# List all skills
/skill list

# Create a new skill
/skill add my-custom-skill

# Remove a skill
/skill remove old-skill

# Edit existing skill
/skill edit error-handler

# Search for skills
/skill search typescript error

# Get detailed info
/skill info my-custom-skill

# Sync between scopes
/skill sync

# Run setup wizard
/skill setup

# Quick scan
/skill scan
```

## 使用模式

### 直接命令模式

带参数调用时，跳过交互式向导：

- `/oh-my-claudecode:skill list` — 显示详细技能清单
- `/oh-my-claudecode:skill add` — 启动技能创建（调用 learner）
- `/oh-my-claudecode:skill scan` — 扫描两个技能目录

### 交互模式

不带参数调用时，运行完整引导向导。

---

## 本地技能的好处

**自动应用**：Claude 检测触发器并自动应用技能 — 无需记住或搜索解决方案。

**版本控制**：项目级技能（`.omc/skills/`）旨在与代码一起提交，使整个团队受益。在链接的 worktree 中，未提交的技能保持在该 worktree 本地，如果移除则消失。

**演进知识**：随着您发现更好的方法和完善触发器，技能随时间改进。

**减少 Token 使用**：Claude 不是重新解决相同的问题，而是高效地应用已知模式。

**代码库记忆**：保留否则会在对话历史中丢失的机构知识。

---

## 技能质量指南

好的技能是：

1. **不可谷歌搜索** — 不能轻易通过搜索找到
   - 差："How to read files in TypeScript"
   - 好："This codebase uses custom path resolution requiring fileURLToPath"

2. **上下文特定** — 引用此代码库的实际文件/错误
   - 差："Use try/catch for error handling"
   - 好："The aiohttp proxy in server.py:42 crashes on ClientDisconnectedError"

3. **精确可操作** — 准确告诉做什么和在哪里
   - 差："Handle edge cases"
   - 好："When seeing 'Cannot find module' in dist/, check tsconfig.json moduleResolution"

4. **来之不易** — 需要大量的调试努力
   - 差：通用编程模式
   - 好："Race condition in worker.ts - Promise.all at line 89 needs await"

---

## 相关技能

- `/oh-my-claudecode:learner` — 从当前对话提取技能
- `/oh-my-claudecode:note` — 保存快速笔记（不如技能正式）
- `/oh-my-claudecode:deepinit` — 生成 AGENTS.md 代码库层次结构

---

## 示例会话

```
> /oh-my-claudecode:skill list

Checking skill directories...
✓ User skills directory exists: ~/.claude/skills/omc-learned/
✓ Project skills directory exists: .omc/skills/

Scanning for skills...

=== USER-LEVEL SKILLS ===
Total skills: 3
  - async-network-error-handling
    Description: Pattern for handling independent I/O failures in async network code
    Modified: 2026-01-20 14:32:15

  - esm-path-resolution
    Description: Custom path resolution in ESM requiring fileURLToPath
    Modified: 2026-01-19 09:15:42

=== PROJECT-LEVEL SKILLS ===
Total skills: 5
  - session-timeout-fix
    Description: Fix for sessionId undefined after restart in session.ts
    Modified: 2026-01-22 16:45:23

  - build-cache-invalidation
    Description: When to clear TypeScript build cache to fix phantom errors
    Modified: 2026-01-21 11:28:37

=== SUMMARY ===
Total skills: 8

What would you like to do?
1. Add new skill
2. List all skills with details
3. Scan conversation for patterns
4. Import skill
5. Done
```

---

## 用户提示

- 定期运行 `/oh-my-claudecode:skill list` 以审查技能库
- 解决棘手错误后，立即运行 learner 捕获它
- 使用项目级技能存储代码库特定知识
- 使用用户级技能存储通用模式
- 随时间审查和完善触发器以提高匹配准确性

---

## 实现说明

1. **YAML 解析：**使用前置数据提取获取元数据
2. **文件操作：**使用 Read/Write 工具，新文件绝不使用 Edit
3. **用户确认：**始终确认破坏性操作
4. **清晰反馈：**使用勾号（✓）、叉号（✗）、箭头（→）提高清晰度
5. **范围解析：**始终检查用户和项目两个范围
6. **验证：**强制命名约定（小写、仅连字符）

---

## 相关技能

- `/oh-my-claudecode:learner` — 从当前对话提取技能
- `/oh-my-claudecode:note` — 保存快速笔记（不如技能正式）
- `/oh-my-claudecode:deepinit` — 生成 AGENTS.md 代码库层次结构

---

## 未来增强

- `/skill export <name>` — 将技能导出为可共享文件
- `/skill import <file>` — 从文件导入技能
- `/skill stats` — 显示所有技能的使用统计
- `/skill validate` — 检查所有技能的格式错误
- `/skill template <type>` — 从预定义模板创建
