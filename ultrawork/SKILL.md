---
name: ultrawork
description: 用于高吞吐量任务完成的并行执行引擎
argument-hint: "<task description with parallel work items>"
level: 4
---

<Purpose>
Ultrawork 是一个并行执行引擎和独立工作的执行协议。它强调意图锚定、并行上下文收集、非平凡工作的依赖感知任务图，以及简洁的、有证据支持的执行摘要。它是一个组件，不是独立的持久化模式——它提供并行性和路由指导，但不提供持久化、验证循环或长期状态管理。
</Purpose>

<Use_When>
- 多个独立任务可以同时运行
- 用户说 "ulw"、"ultrawork" 或想要并行执行
- 你需要将工作委托给多个代理
- 任务受益于并发执行，但用户会自行管理完成
</Use_When>

<Do_Not_Use_When>
- 任务需要带验证的保证完成——使用 `ralph` 代替（ralph 包含 ultrawork）
- 任务需要完整的自主管道——使用 `autopilot` 代替（autopilot 包含 ralph，ralph 包含 ultrawork）
- 只有一个顺序任务，没有并行机会——直接委托给执行器代理
- 用户需要会话持久化以恢复——使用 `ralph`，它在 ultrawork 之上添加持久化
</Do_Not_Use_When>

<Why_This_Exists>
当任务独立时，顺序执行浪费时间。Ultrawork 能够同时启动多个代理并将每个代理路由到正确的模型层级，在控制 token 成本的同时减少总执行时间。它被设计为 ralph 和 autopilot 在其上层叠加的可组合组件。
</Why_This_Exists>

<Execution_Policy>
- 同时启动所有独立的代理调用——永远不要序列化独立工作
- 委托时始终显式传递 `model` 参数
- 首次委托前阅读 `docs/shared/agent-tiers.md` 以获取代理选择指导
- 对超过约 30 秒的操作使用 `run_in_background: true`（安装、构建、测试）
- 在前台运行快速命令（git status、文件读取、简单检查）
- 在实现前解决意图和不确定性；先探索，只在仍被阻塞时才提问
- 对非平凡任务，在执行前生成带并行波次的依赖感知计划
- 保持委托任务报告简洁：简短摘要、涉及的文件、验证状态、阻塞因素
- 已实现的行为需要手动 QA，而不仅仅是诊断
</Execution_Policy>

<Steps>
1. **读取代理参考**：加载 `docs/shared/agent-tiers.md` 以选择层级
2. **先锚定意图**：确认请求是实现、调查、评估还是研究；在明确之前不要编码
3. **并行收集上下文**：
   - 直接工具用于快速读取/搜索
   - 探索/文档代理用于广泛上下文
4. **按独立性分类任务**：识别哪些任务可以并行运行，哪些有依赖
5. **为非平凡工作创建任务图**：
   - 并行执行波次
   - 依赖矩阵
   - 每个任务的验收标准和验证步骤
6. **路由到正确层级**：
   - 简单查找/定义：LOW 层级（Haiku）
   - 标准实现：MEDIUM 层级（Sonnet）
   - 复杂分析/重构：HIGH 层级（Opus）
7. **同时启动独立任务**：一次启动所有并行安全的任务
8. **顺序运行依赖任务**：等待前置条件完成后再启动依赖工作
9. **后台长时间运行操作**：构建、安装和测试套件使用 `run_in_background: true`
10. **所有任务完成后验证**（轻量级）：
    - 构建/类型检查通过
    - 受影响的测试通过
    - 已实现行为的手动 QA 完成
    - 未引入新错误
</Steps>

<Tool_Usage>
- 使用 `Task(subagent_type="oh-my-claudecode:executor", model="haiku", ...)` 处理简单更改
- 使用 `Task(subagent_type="oh-my-claudecode:executor", model="sonnet", ...)` 处理标准工作
- 使用 `Task(subagent_type="oh-my-claudecode:executor", model="opus", ...)` 处理复杂工作
- 对包安装、构建和测试套件使用 `run_in_background: true`
- 对快速状态检查和文件操作使用前台执行
</Tool_Usage>

<Examples>
<Good>
三个独立任务同时启动：
```
Task(subagent_type="oh-my-claudecode:executor", model="haiku", prompt="Add missing type export for Config interface")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="Implement the /api/users endpoint with validation")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="Add integration tests for the auth middleware")
```
为什么好：独立任务在适当层级，全部同时启动。
</Good>

<Good>
正确使用后台执行：
```
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="npm install && npm run build", run_in_background=true)
Task(subagent_type="oh-my-claudecode:executor", model="haiku", prompt="Update the README with new API endpoints")
```
为什么好：长时间构建在后台运行，短任务在前台运行。
</Good>

<Bad>
独立工作的顺序执行：
```
result1 = Task(executor, "Add type export")  # 等待...
result2 = Task(executor, "Implement endpoint")     # 等待...
result3 = Task(executor, "Add tests")              # 等待...
```
为什么差：这些任务是独立的。顺序运行浪费时间。
</Bad>

<Bad>
错误的层级选择：
```
Task(subagent_type="oh-my-claudecode:executor", model="opus", prompt="Add a missing semicolon")
```
为什么差：对于简单修复，Opus 是昂贵的浪费。改用 Haiku 的 executor。
</Bad>
</Examples>

<Escalation_And_Stop_Conditions>
- 当 ultrawork 直接调用（非通过 ralph）时，仅应用轻量级验证——构建通过、测试通过、无新错误
- 要获得完整持久化和全面的架构师验证，建议切换到 `ralph` 模式
- 如果任务在重试中反复失败，报告问题而非无限重试
- 当任务有不明确的依赖或冲突的需求时，上报给用户
</Escalation_And_Stop_Conditions>

<Final_Checklist>
- [ ] 所有并行任务已完成
- [ ] 构建/类型检查通过
- [ ] 受影响的测试通过
- [ ] 未引入新错误
</Final_Checklist>

<Advanced>
## 与其他模式的关系

```
ralph（持久化包装器）
 \-- 包含：ultrawork（此技能）
     \-- 提供：仅并行执行

autopilot（自主执行）
 \-- 包含：ralph
     \-- 包含：ultrawork（此技能）
```

Ultrawork 是并行层。Ralph 添加持久化和验证。Autopilot 添加完整的生命周期管道。
</Advanced>
