---
name: plugin-settings
description: 当用户询问"插件设置"、"存储插件配置"、"用户可配置插件"、".local.md 文件"、"插件状态文件"、"读取 YAML frontmatter"、"按项目设置插件"，或希望使插件行为可配置时，应使用此技能。记录了使用 YAML frontmatter 和 markdown 内容存储插件特定配置的 .claude/plugin-name.local.md 模式。
version: 0.1.0
---

# Claude Code 插件的设置模式

## 概述

插件可以在项目目录中的 `.claude/plugin-name.local.md` 文件中存储用户可配置的设置和状态。此模式使用 YAML frontmatter 存储结构化配置，使用 markdown 内容存储提示或附加上下文。

**关键特性：**
- 文件位置：项目根目录下的 `.claude/plugin-name.local.md`
- 结构：YAML frontmatter + markdown 正文
- 用途：按项目的插件配置和状态
- 用法：从钩子、命令和代理中读取
- 生命周期：用户管理（不在 git 中，应加入 `.gitignore`）

## 文件结构

### 基本模板

```markdown
---
enabled: true
setting1: value1
setting2: value2
numeric_setting: 42
list_setting: ["item1", "item2"]
---

# 附加上下文

此 markdown 正文可以包含：
- 任务描述
- 附加说明
- 反馈给 Claude 的提示
- 文档或笔记
```

### 示例：插件状态文件

**.claude/my-plugin.local.md：**
```markdown
---
enabled: true
strict_mode: false
max_retries: 3
notification_level: info
coordinator_session: team-leader
---

# 插件配置

此插件配置为标准验证模式。
如有问题请联系 @team-lead。
```

## 读取设置文件

### 从钩子读取（Bash 脚本）

**模式：检查存在性并解析 frontmatter**

```bash
#!/bin/bash
set -euo pipefail

# 定义状态文件路径
STATE_FILE=".claude/my-plugin.local.md"

# 如果文件不存在则快速退出
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0  # 插件未配置，跳过
fi

# 解析 YAML frontmatter（在 --- 标记之间）
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# 提取各个字段
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//' | sed 's/^"\(.*\)"$/\1/')
STRICT_MODE=$(echo "$FRONTMATTER" | grep '^strict_mode:' | sed 's/strict_mode: *//' | sed 's/^"\(.*\)"$/\1/')

# 检查是否启用
if [[ "$ENABLED" != "true" ]]; then
  exit 0  # 已禁用
fi

# 在钩子逻辑中使用配置
if [[ "$STRICT_MODE" == "true" ]]; then
  # 应用严格验证
  # ...
fi
```

完整的可工作示例请参见 `examples/read-settings-hook.sh`。

### 从命令读取

命令可以读取设置文件来自定义行为：

```markdown
---
description: 使用插件处理数据
allowed-tools: ["Read", "Bash"]
---

# 处理命令

步骤：
1. 检查设置是否存在 `.claude/my-plugin.local.md`
2. 使用 Read 工具读取配置
3. 解析 YAML frontmatter 提取设置
4. 将设置应用到处理逻辑
5. 使用配置的行为执行
```

### 从代理读取

代理可以在其指令中引用设置：

```markdown
---
name: configured-agent
description: 适应项目设置的代理
---

检查 `.claude/my-plugin/plugin-settings` 中的插件设置。
如果存在，解析 YAML frontmatter 并根据以下字段调整行为：
- enabled：插件是否激活
- mode：处理模式（strict、standard、lenient）
- 其他配置字段
```

## 解析技术

### 提取 Frontmatter

```bash
# 提取 --- 标记之间的所有内容
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")
```

### 读取各个字段

**字符串字段：**
```bash
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//' | sed 's/^"\(.*\)"$/\1/')
```

**布尔字段：**
```bash
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')
# 比较：if [[ "$ENABLED" == "true" ]]; then
```

**数值字段：**
```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')
# 使用：if [[ $MAX -gt 100 ]]; then
```

### 读取 Markdown 正文

提取第二个 `---` 之后的内容：

```bash
# 获取闭合 --- 之后的所有内容
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

## 常见模式

### 模式 1：临时激活的钩子

使用设置文件控制钩子激活：

```bash
#!/bin/bash
STATE_FILE=".claude/security-scan.local.md"

# 如果未配置则快速退出
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# 读取 enabled 标志
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

if [[ "$ENABLED" != "true" ]]; then
  exit 0  # 已禁用
fi

# 运行钩子逻辑
# ...
```

**用例：** 无需编辑 hooks.json 即可启用/禁用钩子（需要重启）。

### 模式 2：代理状态管理

存储代理特定的状态和配置：

**.claude/multi-agent-swarm.local.md：**
```markdown
---
agent_name: auth-agent
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
---

# 任务分配

为 API 实现 JWT 身份验证。

**成功标准：**
- 身份验证端点已创建
- 测试通过
- PR 已创建且 CI 绿灯
```

从钩子读取以协调代理：

```bash
AGENT_NAME=$(echo "$FRONTMATTER" | grep '^agent_name:' | sed 's/agent_name: *//')
COORDINATOR=$(echo "$FRONTMATTER" | grep '^coordinator_session:' | sed 's/coordinator_session: *//')

# 向协调器发送通知
tmux send-keys -t "$COORDINATOR" "代理 $AGENT_NAME 完成任务" Enter
```

### 模式 3：配置驱动的行为

**.claude/my-plugin.local.md：**
```markdown
---
validation_level: strict
max_file_size: 1000000
allowed_extensions: [".js", ".ts", ".tsx"]
enable_logging: true
---

# 验证配置

此项目启用了严格模式。
所有写入都经过安全策略验证。
```

在钩子或命令中使用：

```bash
LEVEL=$(echo "$FRONTMATTER" | grep '^validation_level:' | sed 's/validation_level: *//')

case "$LEVEL" in
  strict)
    # 应用严格验证
    ;;
  standard)
    # 应用标准验证
    ;;
  lenient)
    # 应用宽松验证
    ;;
esac
```

## 创建设置文件

### 从命令创建

命令可以创建设置文件：

```markdown
# 设置命令

步骤：
1. 询问用户配置偏好
2. 创建 `.claude/my-plugin.local.md`，包含 YAML frontmatter
3. 根据用户输入设置适当的值
4. 通知用户设置已保存
5. 提醒用户重启 Claude Code 以使更改生效
```

### 模板生成

在插件 README 中提供模板：

```markdown
## 配置

在项目中创建 `.claude/my-plugin.local.md`：

\`\`\`markdown
---
enabled: true
mode: standard
max_retries: 3
---

# 插件配置

您的设置已激活。
\`\`\`

创建或编辑后，重启 Claude Code 以使更改生效。
```

## 最佳实践

### 文件命名

**推荐：**
- 使用 `.claude/plugin-name.local.md` 格式
- 完全匹配插件名称
- 使用 `.local.md` 后缀表示用户本地文件

**避免：**
- 使用不同目录（不是 `.claude/`）
- 使用不一致的命名
- 使用不带 `.local` 的 `.md`（可能会被提交）

### Gitignore

始终添加到 `.gitignore`：

```gitignore
.claude/*.local.md
.claude/*.local.json
```

在插件 README 中记录这一点。

### 默认值

当设置文件不存在时提供合理的默认值：

```bash
if [[ ! -f "$STATE_FILE" ]]; then
  # 使用默认值
  ENABLED=true
  MODE=standard
else
  # 从文件读取
  # ...
fi
```

### 验证

验证设置值：

```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')

# 验证数值范围
if ! [[ "$MAX" =~ ^[0-9]+$ ]] || [[ $MAX -lt 1 ]] || [[ $MAX -gt 100 ]]; then
  echo "⚠️  设置中的 max_value 无效（必须为 1-100）" >&2
  MAX=10  # 使用默认值
fi
```

### 重启要求

**重要：** 设置更改需要重启 Claude Code。

在 README 中记录：

```markdown
## 更改设置

编辑 `.claude/my-plugin.local.md` 后：
1. 保存文件
2. 退出 Claude Code
3. 重启：`claude` 或 `cc`
4. 新设置将被加载
```

钩子无法在会话内热切换。

## 安全注意事项

### 清理用户输入

从用户输入写入设置文件时：

```bash
# 转义用户输入中的引号
SAFE_VALUE=$(echo "$USER_INPUT" | sed 's/"/\\"/g')

# 写入文件
cat > "$STATE_FILE" <<EOF
---
user_setting: "$SAFE_VALUE"
---
EOF
```

### 验证文件路径

如果设置包含文件路径：

```bash
FILE_PATH=$(echo "$FRONTMATTER" | grep '^data_file:' | sed 's/data_file: *//')

# 检查路径遍历
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "⚠️  设置中的路径无效（路径遍历）" >&2
  exit 2
fi
```

### 权限

设置文件应该：
- 仅用户可读（`chmod 600`）
- 不提交到 git
- 不在用户间共享

## 实际示例

### multi-agent-swarm 插件

**.claude/multi-agent-swarm.local.md：**
```markdown
---
agent_name: auth-implementation
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
additional_instructions: 使用 JWT 令牌，不要使用会话
---

# 任务：实现身份验证

为 REST API 构建基于 JWT 的身份验证。
与 auth-agent 协调共享类型。
```

**钩子用法（agent-stop-notification.sh）：**
- 检查文件是否存在（第 15-18 行：如果不存在则快速退出）
- 解析 frontmatter 获取 coordinator_session、agent_name、enabled
- 如果启用则向协调器发送通知
- 允许通过 `enabled: true/false` 快速激活/停用

### ralph-loop 插件

**.claude/ralph-loop.local.md：**
```markdown
---
iteration: 1
max_iterations: 10
completion_promise: "所有测试通过且构建成功"
---

修复项目中的所有 linting 错误。
确保每次修复后测试通过。
```

**钩子用法（stop-hook.sh）：**
- 检查文件是否存在（第 15-18 行：如果不活动则快速退出）
- 读取迭代次数和 max_iterations
- 提取 completion_promise 用于循环终止
- 读取正文作为反馈提示
- 每次循环更新迭代次数

## 快速参考

### 文件位置

```
project-root/
└── .claude/
    └── plugin-name.local.md
```

### Frontmatter 解析

```bash
# 提取 frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# 读取字段
VALUE=$(echo "$FRONTMATTER" | grep '^field:' | sed 's/field: *//' | sed 's/^"\(.*\)"$/\1/')
```

### 正文解析

```bash
# 提取正文（第二个 --- 之后）
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

### 快速退出模式

```bash
if [[ ! -f ".claude/my-plugin.local.md" ]]; then
  exit 0  # 未配置
fi
```

## 附加资源

### 参考文件

详细的实现模式：

- **`references/parsing-techniques.md`** - 解析 YAML frontmatter 和 markdown 正文的完整指南
- **`references/real-world-examples.md`** - multi-agent-swarm 和 ralph-loop 实现的深入分析

### 示例文件

`examples/` 中的可工作示例：

- **`read-settings-hook.sh`** - 读取和使用设置的钩子
- **`create-settings-command.md`** - 创建设置文件的命令
- **`example-settings.md`** - 设置文件模板

### 工具脚本

`scripts/` 中的开发工具：

- **`validate-settings.sh`** - 验证设置文件结构
- **`parse-frontmatter.sh`** - 提取 frontmatter 字段

## 实现工作流程

要向插件添加设置：

1. 设计设置模式（哪些字段、类型、默认值）
2. 在插件文档中创建模板文件
3. 为 `.claude/*.local.md` 添加 gitignore 条目
4. 在钩子/命令中实现设置解析
5. 使用快速退出模式（检查文件存在、检查 enabled 字段）
6. 在插件 README 中使用模板记录设置
7. 提醒用户更改需要重启 Claude Code

重点是保持设置简单，并在设置文件不存在时提供良好的默认值。
