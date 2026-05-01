---
name: omc-reference
description: OMC 代理目录、可用工具、团队管道路由、提交协议和技能注册表。在委派给代理、使用 OMC 工具、编排团队、进行提交或调用技能时自动加载。
user-invocable: false
---

# OMC 参考

当你需要不需要在每个 `CLAUDE.md` 会话中存在的详细 OMC 目录信息时，使用此内置参考。

## 代理目录

前缀：`oh-my-claudecode:`。完整提示请参见 `agents/*.md`。

- `explore`（haiku）— 快速代码库搜索和映射
- `analyst`（opus）— 需求清晰化和隐藏约束
- `planner`（opus）— 排序和执行计划
- `architect`（opus）— 系统设计、边界和长期权衡
- `debugger`（sonnet）— 根因分析和故障诊断
- `executor`（sonnet）— 实现和重构
- `verifier`（sonnet）— 完成证据和验证
- `tracer`（sonnet）— 追踪收集和证据捕获
- `security-reviewer`（sonnet）— 信任边界和漏洞
- `code-reviewer`（opus）— 全面代码审查
- `test-engineer`（sonnet）— 测试策略和回归覆盖
- `designer`（sonnet）— UX 和交互设计
- `writer`（haiku）— 文档和简洁内容工作
- `qa-tester`（sonnet）— 运行时/手动验证
- `scientist`（sonnet）— 数据分析和统计推理
- `document-specialist`（sonnet）— SDK/API/框架文档查找
- `git-master`（sonnet）— 提交策略和历史维护
- `code-simplifier`（opus）— 保持行为的简化
- `critic`（opus）— 计划/设计挑战和审查

## 模型路由

- `haiku` — 快速查找、轻量检查、窄范围文档工作
- `sonnet` — 标准实现、调试和审查
- `opus` — 架构、深度分析、共识规划和高风险审查

## 工具参考

### 外部 AI / 编排
- `/team N:executor "task"`
- `omc team N:codex|gemini "..."`
- `omc ask <claude|codex|gemini>`
- `/ccg`

### OMC 状态
- `state_read`、`state_write`、`state_clear`、`state_list_active`、`state_get_status`

### 团队运行时
- `TeamCreate`、`TeamDelete`、`SendMessage`、`TaskCreate`、`TaskList`、`TaskGet`、`TaskUpdate`

### 记事本
- `notepad_read`、`notepad_write_priority`、`notepad_write_working`、`notepad_write_manual`

### 项目记忆
- `project_memory_read`、`project_memory_write`、`project_memory_add_note`、`project_memory_add_directive`

### 代码智能
- LSP：`lsp_hover`、`lsp_goto_definition`、`lsp_find_references`、`lsp_diagnostics` 及相关辅助工具
- AST：`ast_grep_search`、`ast_grep_replace`
- 工具：`python_repl`

## 技能注册表

通过 `/oh-my-claudecode:<name>` 调用内置工作流。

### 工作流技能
- `autopilot` — 从想法到可工作代码的完整自主执行
- `ralph` — 持续循环直到完成并验证
- `ultrawork` — 高吞吐量并行执行
- `visual-verdict` — 结构化视觉 QA 判定
- `team` — 协调的团队编排
- `ccg` — Codex + Gemini + Claude 综合通道
- `ultraqa` — QA 循环：测试、验证、修复、重复
- `omc-plan` — 规划工作流和 `/plan` 安全别名
- `ralplan` — 共识规划工作流
- `sciomc` — 科学/研究工作流
- `external-context` — 外部文档/研究工作流
- `deepinit` — 层次化 AGENTS.md 生成
- `deep-interview` — 苏格拉底式模糊门控需求工作流
- `ai-slop-cleaner` — 回归安全清理工作流

### 工具技能
- `ask`、`cancel`、`note`、`learner`、`omc-setup`、`mcp-setup`、`hud`、`omc-doctor`、`trace`、`release`、`project-session-manager`、`skill`、`writer-memory`、`configure-notifications`

### CLAUDE.md 中保持紧凑的关键词触发器
- `"autopilot"→autopilot`
- `"ralph"→ralph`
- `"ulw"→ultrawork`
- `"ccg"→ccg`
- `"ralplan"→ralplan`
- `"deep interview"→deep-interview`
- `"deslop" / "anti-slop"→ai-slop-cleaner`
- `"deep-analyze"→分析模式`
- `"tdd"→TDD 模式`
- `"deepsearch"→代码库搜索`
- `"ultrathink"→深度推理`
- `"cancelomc"→cancel`
- 团队编排通过 `/team` 显式调用。

## 团队管道

阶段：`team-plan` → `team-prd` → `team-exec` → `team-verify` → `team-fix`（循环）。

- 使用 `team-fix` 进行有界的修复循环。
- `team ralph` 将团队管道与 Ralph 风格的顺序验证链接。
- 当独立的并行通道证明协调开销合理时，优先使用团队模式。

## 提交协议

使用 git trailer 在每个提交消息中保留决策上下文。

### 格式
- 首先是意图行：为什么进行更改
- 可选的正文，包含上下文和理由
- 适用时使用结构化 trailer

### 常见 trailer
- `Constraint:` 形成决策的活跃约束
- `Rejected:` 考虑的替代方案 | 拒绝原因
- `Directive:` 前瞻性警告或指令
- `Confidence:` `high` | `medium` | `low`
- `Scope-risk:` `narrow` | `moderate` | `broad`
- `Not-tested:` 已知的验证缺口

### 示例
```text
feat(docs): reduce always-loaded OMC instruction footprint

Move reference-only orchestration content into a native Claude skill so
session-start guidance stays small while detailed OMC reference remains available.

Constraint: Preserve CLAUDE.md marker-based installation flow
Rejected: Sync all built-in skills in legacy install | broader behavior change than issue requires
Confidence: high
Scope-risk: narrow
Not-tested: End-to-end plugin marketplace install in a fresh Claude profile
```
