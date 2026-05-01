---
name: ccg
description: Claude-Codex-Gemini 三模型编排，通过 /ask codex + /ask gemini，然后 Claude 综合结果
level: 5
---

# CCG - Claude-Codex-Gemini 三模型编排

CCG 通过规范的 `/ask` 技能（`/ask codex` + `/ask gemini`）路由，然后 Claude 将两个输出综合为一个答案。

当你想要并行的外部视角而不需要启动 tmux 团队工作者时使用此技能。

## 使用场景

- 一个请求中的后端/分析 + 前端/UI 工作
- 多视角代码审查（架构 + 设计/用户体验）
- Codex 和 Gemini 可能不同意的交叉验证
- 无需团队运行时编排的快速顾问式并行输入

## 要求

- **Codex CLI**: `npm install -g @openai/codex`（或 `@openai/codex`）
- **Gemini CLI**: `npm install -g @google/gemini-cli`
- `omc ask` 命令可用
- 如果任一 CLI 不可用，继续使用可用的提供者并注明限制

## 工作原理

```text
1. Claude 将请求分解为两个顾问提示：
   - Codex 提示（分析/架构/后端）
   - Gemini 提示（用户体验/设计/文档/替代方案）

2. Claude 通过 CLI 运行（不支持技能嵌套）：
   - `omc ask codex "<codex 提示>"`
   - `omc ask gemini "<gemini 提示>"`

3. 工件写入 `.omc/artifacts/ask/` 下

4. Claude 将两个输出综合为一个最终响应
```

## 执行协议

调用时，Claude 必须遵循此工作流：

### 1. 分解请求
将用户请求拆分为：

- **Codex 提示：** 架构、正确性、后端、风险、测试策略
- **Gemini 提示：** 用户体验/内容清晰度、替代方案、边界情况可用性、文档润色
- **综合计划：** 如何协调冲突

### 2. 通过 CLI 调用顾问

> **注意：** Claude Code 不支持技能嵌套（在活跃技能内调用技能）。始终通过 Bash 工具使用直接 CLI 路径。

运行两个顾问：

```bash
omc ask codex "<codex 提示>"
omc ask gemini "<gemini 提示>"
```

### 3. 收集工件

从以下位置读取最新的 ask 工件：

```text
.omc/artifacts/ask/codex-*.md
.omc/artifacts/ask/gemini-*.md
```

### 4. 综合

返回一个统一的答案，包含：

- 一致的建议
- 冲突的建议（明确指出）
- 选择的最终方向 + 理由
- 行动清单

## 回退方案

如果一个提供者不可用：

- 继续使用可用的提供者 + Claude 综合
- 清楚注明缺失的视角和风险

如果都不可用：

- 回退到仅 Claude 的答案，并说明 CCG 外部顾问不可用

## 调用方式

```bash
/oh-my-claudecode:ccg <任务描述>
```

示例：

```bash
/oh-my-claudecode:ccg Review this PR - architecture/security via Codex and UX/readability via Gemini
```
