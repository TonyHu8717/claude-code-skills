---
name: ultraqa
description: QA 循环工作流 - 测试、验证、修复、重复直到达到目标
argument-hint: "[--tests|--build|--lint|--typecheck|--custom <pattern>] [--interactive]"
level: 3
---

# UltraQA 技能

[ULTRAQA 已激活 - 自主 QA 循环]

## 概述

你现在处于 **ULTRAQA** 模式 - 一种自主 QA 循环工作流，会持续运行直到达到你的质量目标。

**循环**: qa-tester → 架构师验证 → 修复 → 重复

## 目标解析

从参数解析目标。支持的格式：

| 调用方式 | 目标类型 | 检查内容 |
|------------|-----------|---------------|
| `/oh-my-claudecode:ultraqa --tests` | 测试 | 所有测试套件通过 |
| `/oh-my-claudecode:ultraqa --build` | 构建 | 构建成功，退出码为 0 |
| `/oh-my-claudecode:ultraqa --lint` | 代码检查 | 无 lint 错误 |
| `/oh-my-claudecode:ultraqa --typecheck` | 类型检查 | 无 TypeScript 错误 |
| `/oh-my-claudecode:ultraqa --custom "pattern"` | 自定义 | 输出中的自定义成功模式 |

如果未提供结构化目标，将参数解释为自定义目标。

## 循环工作流

### 循环 N（最多 5 次）

1. **运行 QA**：根据目标类型执行验证
   - `--tests`：运行项目的测试命令
   - `--build`：运行项目的构建命令
   - `--lint`：运行项目的 lint 命令
   - `--typecheck`：运行项目的类型检查命令
   - `--custom`：运行适当的命令并检查模式
   - `--interactive`：使用 qa-tester 进行交互式 CLI/服务测试：
     ```
     Task(subagent_type="oh-my-claudecode:qa-tester", model="sonnet", prompt="TEST:
     Goal: [describe what to verify]
     Service: [how to start]
     Test cases: [specific scenarios to verify]")
     ```

2. **检查结果**：目标是否通过？
   - **是** → 退出并显示成功消息
   - **否** → 继续到步骤 3

3. **架构师诊断**：生成架构师分析失败原因
   ```
   Task(subagent_type="oh-my-claudecode:architect", model="opus", prompt="DIAGNOSE FAILURE:
   Goal: [goal type]
   Output: [test/build output]
   Provide root cause and specific fix recommendations.")
   ```

4. **修复问题**：应用架构师的建议
   ```
   Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="FIX:
   Issue: [architect diagnosis]
   Files: [affected files]
   Apply the fix precisely as recommended.")
   ```

5. **重复**：回到步骤 1

## 退出条件

| 条件 | 操作 |
|-----------|--------|
| **目标达成** | 退出并显示成功："ULTRAQA COMPLETE: Goal met after N cycles" |
| **达到第 5 次循环** | 退出并显示诊断："ULTRAQA STOPPED: Max cycles. Diagnosis: ..." |
| **相同失败 3 次** | 提前退出："ULTRAQA STOPPED: Same failure detected 3 times. Root cause: ..." |
| **环境错误** | 退出："ULTRAQA ERROR: [tmux/port/dependency issue]" |

## 可观测性

每次循环输出进度：
```
[ULTRAQA Cycle 1/5] Running tests...
[ULTRAQA Cycle 1/5] FAILED - 3 tests failing
[ULTRAQA Cycle 1/5] Architect diagnosing...
[ULTRAQA Cycle 1/5] Fixing: auth.test.ts - missing mock
[ULTRAQA Cycle 2/5] Running tests...
[ULTRAQA Cycle 2/5] PASSED - All 47 tests pass
[ULTRAQA COMPLETE] Goal met after 2 cycles
```

## 状态跟踪

在 `.omc/ultraqa-state.json` 中跟踪状态：
```json
{
  "active": true,
  "goal_type": "tests",
  "goal_pattern": null,
  "cycle": 1,
  "max_cycles": 5,
  "failures": ["3 tests failing: auth.test.ts"],
  "started_at": "2024-01-18T12:00:00Z",
  "session_id": "uuid"
}
```

## 取消

用户可以使用 `/oh-my-claudecode:cancel` 取消，这会清除状态文件。

## 重要规则

1. **尽可能并行** - 在准备潜在修复的同时运行诊断
2. **跟踪失败** - 记录每次失败以检测模式
3. **模式匹配时提前退出** - 相同失败 3 次 = 停止并浮现
4. **清晰输出** - 用户应始终知道当前循环和状态
5. **清理** - 完成或取消时清除状态文件

## 完成时的状态清理

**重要：完成时删除状态文件 - 不要仅设置 `active: false`**

当目标达成或达到最大循环次数或提前退出时：

```bash
# 删除 ultraqa 状态文件
rm -f .omc/state/ultraqa-state.json
```

这确保未来会话的干净状态。不应留下带有 `active: false` 的过期状态文件。

---

立即开始 ULTRAQA 循环。解析目标并开始第 1 次循环。
