---
name: hook-development
description: 当用户要求"创建钩子"、"添加 PreToolUse/PostToolUse/Stop 钩子"、"验证工具使用"、"实现基于提示的钩子"、"使用 ${CLAUDE_PLUGIN_ROOT}"、"设置事件驱动自动化"、"阻止危险命令"，或提及钩子事件（PreToolUse、PostToolUse、Stop、SubagentStop、SessionStart、SessionEnd、UserPromptSubmit、PreCompact、Notification）时使用此技能。提供创建和实现 Claude Code 插件钩子的综合指南，重点关注高级基于提示的钩子 API。
version: 0.1.0
---

# Claude Code 插件钩子开发

## 概述

钩子是事件驱动的自动化脚本，响应 Claude Code 事件执行。使用钩子来验证操作、执行策略、添加上下文，并将外部工具集成到工作流中。

**关键能力：**
- 在执行前验证工具调用（PreToolUse）
- 对工具结果做出反应（PostToolUse）
- 执行完成标准（Stop、SubagentStop）
- 加载项目上下文（SessionStart）
- 在开发生命周期中自动化工作流

## 钩子类型

### 基于提示的钩子（推荐）

使用 LLM 驱动的决策进行上下文感知验证：

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is appropriate: $TOOL_INPUT",
  "timeout": 30
}
```

**支持的事件：** Stop、SubagentStop、UserPromptSubmit、PreToolUse

**优势：**
- 基于自然语言推理的上下文感知决策
- 无需 bash 脚本的灵活评估逻辑
- 更好的边缘情况处理
- 更易维护和扩展

### 命令钩子

执行 bash 命令进行确定性检查：

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```

**适用场景：**
- 快速确定性验证
- 文件系统操作
- 外部工具集成
- 性能关键检查

## 钩子配置格式

### 插件 hooks.json 格式

**对于插件钩子**，在 `hooks/hooks.json` 中使用包装格式：

```json
{
  "description": "Brief explanation of hooks (optional)",
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...],
    "SessionStart": [...]
  }
}
```

**要点：**
- `description` 字段是可选的
- `hooks` 字段是必需的包装器，包含实际的钩子事件
- 这是**插件专用格式**

**示例：**
```json
{
  "description": "Validation hooks for code quality",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate.sh"
          }
        ]
      }
    ]
  }
}
```

### 设置格式（直接）

**对于用户设置**，在 `.claude/settings.json` 中使用直接格式：

```json
{
  "PreToolUse": [...],
  "Stop": [...],
  "SessionStart": [...]
}
```

**要点：**
- 无包装器 - 事件直接在顶层
- 无 description 字段
- 这是**设置格式**

**重要：** 下面的示例展示了两种格式中使用的钩子事件结构。对于插件 hooks.json，请用 `{"hooks": {...}}` 包装这些内容。

## 钩子事件

### PreToolUse

在任何工具运行前执行。用于批准、拒绝或修改工具调用。

**示例（基于提示）：**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety. Check: system paths, credentials, path traversal, sensitive content. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

**PreToolUse 输出：**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

### PostToolUse

在工具完成后执行。用于对结果做出反应、提供反馈或记录日志。

**示例：**
```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Analyze edit result for potential issues: syntax errors, security vulnerabilities, breaking changes. Provide feedback."
        }
      ]
    }
  ]
}
```

**输出行为：**
- 退出码 0：stdout 显示在对话记录中
- 退出码 2：stderr 反馈给 Claude
- systemMessage 包含在上下文中

### Stop

当主代理考虑停止时执行。用于验证完整性。

**示例：**
```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Verify task completion: tests run, build succeeded, questions answered. Return 'approve' to stop or 'block' with reason to continue."
        }
      ]
    }
  ]
}
```

**决策输出：**
```json
{
  "decision": "approve|block",
  "reason": "Explanation",
  "systemMessage": "Additional context"
}
```

### SubagentStop

当子代理考虑停止时执行。用于确保子代理完成了其任务。

类似于 Stop 钩子，但针对子代理。

### UserPromptSubmit

当用户提交提示时执行。用于添加上下文、验证或阻止提示。

**示例：**
```json
{
  "UserPromptSubmit": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Check if prompt requires security guidance. If discussing auth, permissions, or API security, return relevant warnings."
        }
      ]
    }
  ]
}
```

### SessionStart

当 Claude Code 会话开始时执行。用于加载上下文和设置环境。

**示例：**
```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh"
        }
      ]
    }
  ]
}
```

**特殊能力：** 使用 `$CLAUDE_ENV_FILE` 持久化环境变量：
```bash
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

完整示例见 `examples/load-context.sh`。

### SessionEnd

当会话结束时执行。用于清理、日志记录和状态保存。

### PreCompact

在上下文压缩前执行。用于添加需要保留的关键信息。

### Notification

当 Claude 发送通知时执行。用于对用户通知做出反应。

## 钩子输出格式

### 标准输出（所有钩子）

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

- `continue`：如果为 false，停止处理（默认 true）
- `suppressOutput`：从对话记录中隐藏输出（默认 false）
- `systemMessage`：显示给 Claude 的消息

### 退出码

- `0` - 成功（stdout 显示在对话记录中）
- `2` - 阻塞错误（stderr 反馈给 Claude）
- 其他 - 非阻塞错误

## 钩子输入格式

所有钩子通过 stdin 接收 JSON，包含通用字段：

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

**事件特定字段：**

- **PreToolUse/PostToolUse：** `tool_name`、`tool_input`、`tool_result`
- **UserPromptSubmit：** `user_prompt`
- **Stop/SubagentStop：** `reason`

在提示中使用 `$TOOL_INPUT`、`$TOOL_RESULT`、`$USER_PROMPT` 等访问字段。

## 环境变量

在所有命令钩子中可用：

- `$CLAUDE_PROJECT_DIR` - 项目根路径
- `$CLAUDE_PLUGIN_ROOT` - 插件目录（用于可移植路径）
- `$CLAUDE_ENV_FILE` - 仅 SessionStart：在此持久化环境变量
- `$CLAUDE_CODE_REMOTE` - 如果在远程上下文中运行则设置

**始终在钩子命令中使用 ${CLAUDE_PLUGIN_ROOT} 以确保可移植性：**

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

## 插件钩子配置

在插件中，在 `hooks/hooks.json` 中定义钩子：

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Verify task completion"
        }
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

插件钩子与用户钩子合并并并行运行。

## 匹配器

### 工具名称匹配

**精确匹配：**
```json
"matcher": "Write"
```

**多个工具：**
```json
"matcher": "Read|Write|Edit"
```

**通配符（所有工具）：**
```json
"matcher": "*"
```

**正则表达式模式：**
```json
"matcher": "mcp__.*__delete.*"  // 所有 MCP 删除工具
```

**注意：** 匹配器区分大小写。

### 常见模式

```json
// 所有 MCP 工具
"matcher": "mcp__.*"

// 特定插件的 MCP 工具
"matcher": "mcp__plugin_asana_.*"

// 所有文件操作
"matcher": "Read|Write|Edit"

// 仅 Bash 命令
"matcher": "Bash"
```

## 安全最佳实践

### 输入验证

始终在命令钩子中验证输入：

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# 验证工具名称格式
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"decision": "deny", "reason": "Invalid tool name"}' >&2
  exit 2
fi
```

### 路径安全

检查路径遍历和敏感文件：

```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 拒绝路径遍历
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# 拒绝敏感文件
if [[ "$file_path" == *".env"* ]]; then
  echo '{"decision": "deny", "reason": "Sensitive file"}' >&2
  exit 2
fi
```

完整示例见 `examples/validate-write.sh` 和 `examples/validate-bash.sh`。

### 引用所有变量

```bash
# 正确：引用
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"

# 错误：未引用（注入风险）
echo $file_path
cd $CLAUDE_PROJECT_DIR
```

### 设置适当的超时

```json
{
  "type": "command",
  "command": "bash script.sh",
  "timeout": 10
}
```

**默认值：** 命令钩子（60 秒），提示钩子（30 秒）

## 性能考虑

### 并行执行

所有匹配的钩子**并行**运行：

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {"type": "command", "command": "check1.sh"},  // 并行
        {"type": "command", "command": "check2.sh"},  // 并行
        {"type": "prompt", "prompt": "Validate..."}   // 并行
      ]
    }
  ]
}
```

**设计影响：**
- 钩子看不到彼此的输出
- 非确定性排序
- 为独立性而设计

### 优化

1. 对快速确定性检查使用命令钩子
2. 对复杂推理使用提示钩子
3. 在临时文件中缓存验证结果
4. 最小化热路径中的 I/O

## 临时激活钩子

通过检查标志文件或配置创建条件激活的钩子：

**模式：标志文件激活**
```bash
#!/bin/bash
# 仅在标志文件存在时激活
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  # 标志不存在，跳过验证
  exit 0
fi

# 标志存在，运行验证
input=$(cat)
# ... 验证逻辑 ...
```

**模式：基于配置的激活**
```bash
#!/bin/bash
# 检查配置以确定是否激活
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/plugin-config.json"

if [ -f "$CONFIG_FILE" ]; then
  enabled=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$enabled" != "true" ]; then
    exit 0  # 未启用，跳过
  fi
fi

# 已启用，运行钩子逻辑
input=$(cat)
# ... 钩子逻辑 ...
```

**用例：**
- 仅在需要时启用严格验证
- 临时调试钩子
- 项目特定的钩子行为
- 钩子的功能标志

**最佳实践：** 在插件 README 中记录激活机制，以便用户了解如何启用/禁用临时钩子。

## 钩子生命周期和限制

### 钩子在会话启动时加载

**重要：** 钩子在 Claude Code 会话启动时加载。更改钩子配置需要重启 Claude Code。

**无法热替换钩子：**
- 编辑 `hooks/hooks.json` 不会影响当前会话
- 添加新钩子脚本不会被识别
- 更改钩子命令/提示不会更新
- 必须重启 Claude Code：退出并再次运行 `claude`

**测试钩子更改：**
1. 编辑钩子配置或脚本
2. 退出 Claude Code 会话
3. 重启：`claude` 或 `cc`
4. 新钩子配置加载
5. 使用 `claude --debug` 测试钩子

### 启动时的钩子验证

钩子在 Claude Code 启动时验证：
- hooks.json 中的无效 JSON 导致加载失败
- 缺失的脚本导致警告
- 语法错误在调试模式下报告

使用 `/hooks` 命令查看当前会话中已加载的钩子。

## 调试钩子

### 启用调试模式

```bash
claude --debug
```

查找钩子注册、执行日志、输入/输出 JSON 和计时信息。

### 测试钩子脚本

直接测试命令钩子：

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

echo "Exit code: $?"
```

### 验证 JSON 输出

确保钩子输出有效的 JSON：

```bash
output=$(./your-hook.sh < test-input.json)
echo "$output" | jq .
```

## 快速参考

### 钩子事件摘要

| 事件 | 时机 | 用途 |
|-------|------|---------|
| PreToolUse | 工具执行前 | 验证、修改 |
| PostToolUse | 工具执行后 | 反馈、日志 |
| UserPromptSubmit | 用户输入时 | 上下文、验证 |
| Stop | 代理停止时 | 完整性检查 |
| SubagentStop | 子代理完成时 | 任务验证 |
| SessionStart | 会话开始时 | 上下文加载 |
| SessionEnd | 会话结束时 | 清理、日志 |
| PreCompact | 压缩前 | 保留上下文 |
| Notification | 用户收到通知时 | 日志、反应 |

### 最佳实践

**推荐：**
- 对复杂逻辑使用基于提示的钩子
- 使用 ${CLAUDE_PLUGIN_ROOT} 确保可移植性
- 在命令钩子中验证所有输入
- 引用所有 bash 变量
- 设置适当的超时
- 返回结构化 JSON 输出
- 彻底测试钩子

**避免：**
- 使用硬编码路径
- 信任未经验证的用户输入
- 创建长时间运行的钩子
- 依赖钩子执行顺序
- 不可预测地修改全局状态
- 记录敏感信息

## 附加资源

### 参考文件

有关详细模式和高级技术，请查阅：

- **`references/patterns.md`** - 常见钩子模式（8+ 经过验证的模式）
- **`references/migration.md`** - 从基础到高级钩子的迁移
- **`references/advanced.md`** - 高级用例和技术

### 钩子脚本示例

`examples/` 中的工作示例：

- **`validate-write.sh`** - 文件写入验证示例
- **`validate-bash.sh`** - Bash 命令验证示例
- **`load-context.sh`** - SessionStart 上下文加载示例

### 实用脚本

`scripts/` 中的开发工具：

- **`validate-hook-schema.sh`** - 验证 hooks.json 结构和语法
- **`test-hook.sh`** - 在部署前使用示例输入测试钩子
- **`hook-linter.sh`** - 检查钩子脚本的常见问题和最佳实践

### 外部资源

- **官方文档**: https://docs.claude.com/en/docs/claude-code/hooks
- **示例**: 见市场中的 security-guidance 插件
- **测试**: 使用 `claude --debug` 获取详细日志
- **验证**: 使用 `jq` 验证钩子 JSON 输出

## 实现工作流

在插件中实现钩子：

1. 确定要挂钩的事件（PreToolUse、Stop、SessionStart 等）
2. 决定使用基于提示的（灵活）还是命令（确定性）钩子
3. 在 `hooks/hooks.json` 中编写钩子配置
4. 对于命令钩子，创建钩子脚本
5. 对所有文件引用使用 ${CLAUDE_PLUGIN_ROOT}
6. 使用 `scripts/validate-hook-schema.sh hooks/hooks.json` 验证配置
7. 部署前使用 `scripts/test-hook.sh` 测试钩子
8. 在 Claude Code 中使用 `claude --debug` 测试
9. 在插件 README 中记录钩子

对于大多数用例，重点关注基于提示的钩子。将命令钩子保留用于性能关键或确定性检查。
