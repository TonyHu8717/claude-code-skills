---
name: omc-plan
description: 带可选访谈工作流的战略规划
argument-hint: "[--direct|--consensus|--review] [--interactive] [--deliberate] <task description>"
pipeline: [deep-interview, omc-plan, autopilot]
next-skill: autopilot
handoff: .omc/plans/ralplan-*.md
level: 4
---

<Purpose>
Plan 通过智能交互创建全面、可执行的工作计划。它自动检测是访谈用户（宽泛请求）还是直接规划（详细请求），并支持共识模式（迭代的 Planner/Architect/Critic 循环，带 RALPLAN-DR 结构化审议）和审查模式（Critic 对现有计划的评估）。
</Purpose>

<Use_When>
- 用户希望在实现前规划 -- "plan this", "plan the", "let's plan"
- 用户希望为模糊想法进行结构化需求收集
- 用户希望审查现有计划 -- "review this plan", `--review`
- 用户希望对计划进行多视角共识 -- `--consensus`, "ralplan"
- 任务宽泛或模糊，需要在编写任何代码前确定范围
</Use_When>

<Do_Not_Use_When>
- 用户希望自主端到端执行 -- 改用 `autopilot`
- 用户希望立即开始编码，任务明确 -- 使用 `ralph` 或委派给 executor
- 用户提出可以直接回答的简单问题 -- 直接回答
- 任务是范围明确的单一聚焦修复 -- 跳过规划，直接执行
</Do_Not_Use_When>

<Why_This_Exists>
在不理解需求的情况下跳入代码会导致返工、范围蔓延和遗漏边界情况。Plan 提供结构化需求收集、专家分析和质量门控计划，使执行从坚实的基础开始。共识模式为高风险项目添加多视角验证。
</Why_This_Exists>

<Execution_Policy>
- 根据请求具体性自动检测访谈 vs 直接模式
- 访谈时一次问一个问题 -- 绝不批量问多个问题
- 在询问用户之前通过 `explore` 代理收集代码库事实
- 计划必须满足质量标准：80%+ 声明引用文件/行号，90%+ 标准可测试
- 共识模式默认全自动运行；添加 `--interactive` 在草稿审查和最终批准步骤启用用户提示
- 共识模式默认使用 RALPLAN-DR 短模式；使用 `--deliberate` 或请求明确表示高风险（认证/安全、数据迁移、破坏性/不可逆更改、生产事件、合规/PII、公共 API 破坏）时切换到审议模式
</Execution_Policy>

<Steps>

### 模式选择

| 模式 | 触发条件 | 行为 |
|------|---------|----------|
| 访谈 | 宽泛请求的默认模式 | 交互式需求收集 |
| 直接 | `--direct`，或详细请求 | 跳过访谈，直接生成计划 |
| 共识 | `--consensus`, "ralplan" | Planner -> Architect -> Critic 循环直到达成一致，带 RALPLAN-DR 结构化审议（默认短模式，`--deliberate` 用于高风险）；添加 `--interactive` 在草稿和批准步骤启用用户提示 |
| 审查 | `--review`, "review this plan" | Critic 对现有计划的评估 |

### 访谈模式（宽泛/模糊请求）

1. **分类请求**：宽泛（模糊动词、无特定文件、涉及 3+ 领域）触发访谈模式
2. **问一个聚焦问题**：使用 `AskUserQuestion` 询问偏好、范围和约束
3. **先收集代码库事实**：在问"你的代码使用什么模式？"之前，生成一个 `explore` 代理去查找，然后提出有根据的后续问题
4. **基于答案构建**：每个问题基于前一个答案
5. **咨询分析师**（Opus）获取隐藏需求、边界情况和风险
6. **创建计划**：当用户表示准备就绪时："create the plan", "I'm ready", "make it a work plan"

### 直接模式（详细请求）

1. **快速分析**：可选的简要分析师咨询
2. **创建计划**：立即生成全面工作计划
3. **审查**（可选）：如果请求则进行 Critic 审查

### 共识模式（`--consensus` / "ralplan"）

**RALPLAN-DR 模式**：**短**（默认，有界结构）和**审议**（用于 `--deliberate` 或明确的高风险请求）。两种模式保持相同的 Planner -> Architect -> Critic 顺序和相同的 `AskUserQuestion` 门控。

**提供者覆盖（在提供者 CLI 已安装时支持）：**
- `--architect codex` — 用 `omc ask codex --agent-prompt architect "..."` 替换 Claude Architect 通道，用于实现密集型架构审查
- `--critic codex` — 用 `omc ask codex --agent-prompt critic "..."` 替换 Claude Critic 通道，用于执行前的外部审查通道
- 如果请求的提供者不可用，简要说明并继续使用默认的 Claude Architect/Critic 步骤

**状态生命周期**：持久模式停止钩子使用 `ralplan-state.json` 在共识循环期间强制继续。技能**必须**管理此状态：
- **进入时**：在步骤 1 之前调用 `state_write(mode="ralplan", active=true, session_id=<current_session_id>)`
- **移交给执行时**（批准 → ralph/team）：调用 `state_write(mode="ralplan", active=false, session_id=<current_session_id>)`。此处不要使用 `state_clear` — `state_clear` 写入 30 秒取消信号，会禁用所有模式的停止钩子强制执行，使新启动的执行模式失去保护。
- **真正退出时**（拒绝、非交互式计划输出、错误/中止）：调用 `state_clear(mode="ralplan", session_id=<current_session_id>)` — 没有后续执行模式，取消信号窗口无害。
- 不要在中间步骤（如 Critic 批准或最大迭代展示）清除，因为用户可能仍会选择"请求更改"。

不清理的话，停止钩子会在共识工作流完成后仍用 `[RALPLAN - CONSENSUS PLANNING]` 强化消息阻止所有后续停止。始终传递 `session_id` 以避免清除其他并发会话的状态。

1. **Planner** 创建初始计划和紧凑的 **RALPLAN-DR 摘要**（在任何 Architect 审查之前）。摘要**必须**包括：
   - **原则**（3-5 条）
   - **决策驱动因素**（前 3 个）
   - **可行选项**（>=2 个），每个选项有界优缺点
   - 如果只剩一个可行选项，对被拒绝的替代方案有明确的**无效化理由**
   - 在**审议模式**下：**预验尸**（3 个失败场景）和**扩展测试计划**，覆盖**单元/集成/e2e/可观测性**
2. **用户反馈** *(仅 --interactive)*：如果使用 `--interactive` 运行，**必须**使用 `AskUserQuestion` 呈现草稿计划**加上 RALPLAN-DR 原则/决策驱动因素/选项摘要，用于早期方向对齐**，选项为：
   - **提交审查** — 发送给 Architect 和 Critic 评估
   - **请求更改** — 返回步骤 1 并纳入用户反馈
   - **跳过审查** — 直接进入最终批准（步骤 7）
   如果未使用 `--interactive`，自动进入审查（步骤 3）。
3. **Architect** 使用 `Task(subagent_type="oh-my-claudecode:architect", ...)` 审查架构合理性。Architect 审查**必须**包括：对首选选项的最强钢铁侠反驳（反题），至少一个有意义的权衡张力，以及（可能的）综合路径。在审议模式下，Architect 应明确标记原则违反。**等待此步骤完成后再进行步骤 4。** 不要并行运行步骤 3 和 4。
4. **Critic** 使用 `Task(subagent_type="oh-my-claudecode:critic", ...)` 根据质量标准评估。Critic **必须**验证原则-选项一致性、公平的替代方案探索、风险缓解清晰度、可测试验收标准和具体验证步骤。Critic **必须**明确拒绝浅薄的替代方案、驱动因素矛盾、模糊风险或弱验证。在审议模式下，Critic **必须**拒绝缺失/弱的预验尸或缺失/弱的扩展测试计划。仅在步骤 3 完成后运行。
5. **重新审查循环**（最多 5 次迭代）：如果 Critic 拒绝，执行此闭环：
   a. 收集 Architect + Critic 的所有拒绝反馈
   b. 将反馈传递给 Planner 以产生修订计划
   c. **返回步骤 3** — Architect 审查修订计划
   d. **返回步骤 4** — Critic 评估修订计划
   e. 重复直到 Critic 批准或达到最大 5 次迭代
   f. 如果达到最大迭代次数仍未批准，通过 `AskUserQuestion` 向用户展示最佳版本，注明未达成专家共识
6. **应用改进**：当审查者批准并附带改进建议时，在继续之前将所有接受的改进合并到计划文件中。最终共识输出**必须**包含一个 **ADR** 部分：**决策**、**驱动因素**、**考虑的替代方案**、**选择原因**、**后果**、**后续行动**。具体地：
   a. 收集 Architect 和 Critic 响应中的所有改进建议
   b. 去重和分类建议
   c. 使用接受的改进更新 `.omc/plans/` 中的计划文件（添加缺失细节、细化步骤、加强验收标准、ADR 更新等）
   d. 在计划末尾的简要变更日志部分注明应用了哪些改进
7. 在 Critic 批准（改进已应用）后：*(仅 --interactive)* 如果使用 `--interactive`，使用 `AskUserQuestion` 呈现计划，选项为：
   - **批准并通过团队实现**（推荐） — 通过协调的并行团队代理（`/team`）进行实现。自 v4.1.7 起，团队是规范的编排界面。
   - **批准并通过 ralph 执行** — 通过 ralph+ultrawork（带验证的顺序执行）进行实现
   - **清除上下文并实现** — 先压缩上下文窗口（在规划后上下文较大时推荐），然后使用保存的计划文件通过 ralph 开始全新实现
   - **请求更改** — 返回步骤 1 并纳入用户反馈
   - **拒绝** — 完全丢弃计划
   如果未使用 `--interactive`，输出最终批准的计划，调用 `state_clear(mode="ralplan", session_id=<current_session_id>)`，然后停止。不要自动执行。
8. *(仅 --interactive)* 用户通过结构化 `AskUserQuestion` UI 选择（绝不用纯文本询问批准）。如果用户选择**拒绝**，调用 `state_clear(mode="ralplan", session_id=<current_session_id>)` 并停止。
9. 用户批准后（仅 --interactive）：在调用执行技能（ralph/team）**之前**调用 `state_write(mode="ralplan", active=false, session_id=<current_session_id>)`，这样停止钩子不会干扰执行模式自身的强制执行。此处不要使用 `state_clear` — 它会写入取消信号，禁用新启动模式的强制执行。
   - **批准并通过团队实现**：**必须**调用 `Skill("oh-my-claudecode:team")`，以 `.omc/plans/` 中的批准计划路径作为上下文。不要直接实现。团队技能在分阶段管道中协调并行代理，用于大型任务的更快执行。这是推荐的默认执行路径。
   - **批准并通过 ralph 执行**：**必须**调用 `Skill("oh-my-claudecode:ralph")`，以 `.omc/plans/` 中的批准计划路径作为上下文。不要直接实现。不要在规划代理中编辑源代码文件。ralph 技能通过 ultrawork 并行代理处理执行。
   - **清除上下文并实现**：先调用 `Skill("compact")` 压缩上下文窗口（减少规划期间累积的 token 使用），然后调用 `Skill("oh-my-claudecode:ralph")`，以 `.omc/plans/` 中的批准计划路径作为上下文。当规划会话后上下文窗口 50%+ 满时推荐此路径。

### 审查模式（`--review`）

1. 从 `.omc/plans/` 读取计划文件
2. 使用 `Task(subagent_type="oh-my-claudecode:critic", ...)` 通过 Critic 评估
3. 返回裁定：APPROVED、REVISE（附具体反馈）或 REJECT（需要重新规划）

### 计划输出格式

每个计划包含：
- 需求摘要
- 验收标准（可测试）
- 实现步骤（带文件引用）
- 风险和缓解措施
- 验证步骤
- 对于共识/ralplan：**RALPLAN-DR 摘要**（原则、决策驱动因素、选项）
- 对于共识/ralplan 最终输出：**ADR**（决策、驱动因素、考虑的替代方案、选择原因、后果、后续行动）
- 对于审议共识模式：**预验尸（3 个场景）** 和**扩展测试计划**（单元/集成/e2e/可观测性）

计划保存到 `.omc/plans/`。草稿保存到 `.omc/drafts/`。
</Steps>

<Tool_Usage>
- 使用 `AskUserQuestion` 询问偏好问题（范围、优先级、时间线、风险容忍度）— 提供可点击 UI
- 使用纯文本询问需要具体值的问题（端口号、名称、后续澄清）
- 使用 `explore` 代理（Haiku，30 秒超时）在询问用户之前收集代码库事实
- 使用 `Task(subagent_type="oh-my-claudecode:planner", ...)` 对大范围计划进行规划验证
- 使用 `Task(subagent_type="oh-my-claudecode:analyst", ...)` 进行需求分析
- 使用 `Task(subagent_type="oh-my-claudecode:critic", ...)` 在共识和审查模式下进行计划审查
- **关键 — 共识模式代理调用必须是顺序的，绝不能并行。** 始终等待 Architect Task 结果后再发出 Critic Task。
- 在共识模式下，默认使用 RALPLAN-DR 短模式；在 `--deliberate` 或明确的高风险信号（认证/安全、迁移、破坏性更改、生产事件、合规/PII、公共 API 破坏）时启用审议模式
- 在共识模式下使用 `--interactive`：使用 `AskUserQuestion` 进行用户反馈步骤（步骤 2）和最终批准步骤（步骤 7）— 绝不用纯文本询问批准。不使用 `--interactive` 时，跳过两个提示并输出最终计划。
- 在共识模式下使用 `--interactive`，用户批准后**必须**调用 `Skill("oh-my-claudecode:ralph")` 进行执行（步骤 9）— 绝不在规划代理中直接实现
- 当用户在步骤 7 中选择"清除上下文并实现"时（仅 --interactive）：先调用 `state_write(mode="ralplan", active=false, session_id=<current_session_id>)`，然后调用 `Skill("compact")` 压缩累积的规划上下文，然后立即调用 `Skill("oh-my-claudecode:ralph")` 并传入计划路径 — 压缩步骤对于在实现循环开始前释放上下文至关重要
- **关键 — 共识模式状态生命周期**：始终在停止或移交给执行前停用 ralplan 状态。移交路径（批准 → ralph/team）使用 `state_write(active=false)`，真正退出（拒绝、错误）使用 `state_clear`。启动执行模式前绝不使用 `state_clear` — 其取消信号会禁用 30 秒的停止钩子强制执行。
</Tool_Usage>

<Examples>
<Good>
自适应访谈（在询问前收集事实）：
```
Planner: [生成 explore 代理: "find authentication implementation"]
Planner: [收到: "Auth is in src/auth/ using JWT with passport.js"]
Planner: "我看到你在 src/auth/ 中使用 JWT 认证和 passport.js。
         对于这个新功能，我们应该扩展现有认证还是添加单独的认证流程？"
```
好的原因：先自己回答代码库问题，然后提出有根据的偏好问题。
</Good>

<Good>
一次一个问题：
```
Q1: "主要目标是什么？"
A1: "提高性能"
Q2: "对于性能，延迟和吞吐量哪个更重要？"
A2: "延迟"
Q3: "对于延迟，我们是优化 p50 还是 p99？"
```
好的原因：每个问题基于前一个答案。聚焦且渐进。
</Good>

<Bad>
询问可以查找的内容：
```
Planner: "认证在你的代码库中哪里实现？"
User: "呃，我觉得在 src/auth 的某个地方？"
```
坏的原因：planner 应该生成 explore 代理去查找，而不是问用户。
</Bad>

<Bad>
批量问多个问题：
```
"范围是什么？时间线呢？受众是谁？"
```
坏的原因：一次三个问题导致浅层回答。一次问一个。
</Bad>

<Bad>
一次呈现所有设计选项：
```
"这里有 4 种方法：选项 A... 选项 B... 选项 C... 选项 D... 你偏好哪个？"
```
坏的原因：决策疲劳。一次呈现一个选项及权衡，获得反应，然后呈现下一个。
</Bad>
</Examples>

<Escalation_And_Stop_Conditions>
- 当需求足够清晰可以规划时停止访谈 — 不要过度访谈
- 在共识模式下，5 次 Planner/Architect/Critic 迭代后停止并展示最佳版本。不要在此清除 ralplan 状态 — 用户可能仍会在后续步骤中选择"请求更改"。状态仅在用户的最终选择（批准/拒绝）或非交互模式输出计划时清除。
- 不使用 `--interactive` 的共识模式输出最终计划并停止；使用 `--interactive` 时，需要用户明确批准后才开始实现。停止前**始终**调用 `state_clear(mode="ralplan", session_id=<current_session_id>)`。
- 如果用户说"just do it"或"skip planning"，调用 `state_write(mode="ralplan", active=false, session_id=<current_session_id>)` 然后**必须**调用 `Skill("oh-my-claudecode:ralph")` 转换到执行模式。不要在规划代理中直接实现。
- 当存在需要业务决策的不可调和权衡时升级给用户
</Escalation_And_Stop_Conditions>

<Final_Checklist>
- [ ] 计划有可测试的验收标准（90%+ 具体）
- [ ] 计划引用具体文件/行号（80%+ 声明）
- [ ] 所有风险都有识别的缓解措施
- [ ] 无无指标的模糊术语（"fast" -> "p99 < 200ms"）
- [ ] 计划保存到 `.omc/plans/`
- [ ] 共识模式下：RALPLAN-DR 摘要包含 3-5 条原则、前 3 个驱动因素和 >=2 个可行选项（或明确的无效化理由）
- [ ] 共识模式最终输出：包含 ADR 部分（决策/驱动因素/考虑的替代方案/选择原因/后果/后续行动）
- [ ] 审议共识模式：包含预验尸（3 个场景）+ 扩展测试计划（单元/集成/e2e/可观测性）
- [ ] 共识模式使用 `--interactive`：用户在任何执行前明确批准；不使用 `--interactive`：仅输出计划，无自动执行
- [ ] 共识模式下：ralplan 状态在每个退出路径上停用 — 移交到执行使用 `state_write(active=false)`，真正退出（拒绝、错误、非交互式停止）使用 `state_clear`
</Final_Checklist>

<Advanced>
## 设计选项呈现

在访谈期间呈现设计选择时，分块呈现：

1. **概述**（2-3 句话）
2. **选项 A** 及权衡
3. [等待用户反应]
4. **选项 B** 及权衡
5. [等待用户反应]
6. **推荐**（仅在讨论选项后）

每个选项的格式：
```
### 选项 A: [名称]
**方法:** [1 句话]
**优点:** [要点]
**缺点:** [要点]

你对这个方法有什么看法？
```

## 问题分类

在问任何访谈问题之前，分类它：

| 类型 | 示例 | 操作 |
|------|----------|--------|
| 代码库事实 | "存在什么模式？", "X 在哪里？" | 先探索，不问用户 |
| 用户偏好 | "优先级？", "时间线？" | 通过 AskUserQuestion 问用户 |
| 范围决策 | "包含功能 Y 吗？" | 问用户 |
| 需求 | "性能约束？" | 问用户 |

## 审查质量标准

| 标准 | 要求 |
|-----------|----------|
| 清晰度 | 80%+ 声明引用文件/行号 |
| 可测试性 | 90%+ 标准具体 |
| 验证 | 所有文件引用存在 |
| 具体性 | 无模糊术语 |

## 弃用通知

单独的 `/planner`、`/ralplan` 和 `/review` 技能已合并到 `/plan`。所有工作流（访谈、直接、共识、审查）都可通过 `/plan` 使用。
</Advanced>
