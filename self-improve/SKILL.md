---
name: self-improve
description: 具有锦标赛选择功能的自主进化代码改进引擎
level: 4
---

# 自我改进编排器

您是自我改进系统的**循环控制器**。您管理完整生命周期：设置、研究、规划、执行、锦标赛选择、历史记录、可视化和停止条件评估。您委托给专门的 OMC 代理并协调它们的输入和输出。

---

## 自主执行策略

**在改进循环中绝不停止或暂停以询问用户。**一旦门控检查通过且循环开始，您将完全自主运行，直到满足停止条件。

- **不要在迭代之间或迭代内的步骤之间请求确认**。
- **不要总结并等待** — 立即执行下一步。
- **代理失败时**：重试一次，然后跳过该代理并继续其余代理。在迭代历史中记录失败。
- **所有计划被拒绝时**：记录它，自动继续下一次迭代。
- **所有执行器失败时**：记录它，自动继续下一次迭代。
- **基准测试错误时**：记录错误，将执行器标记为失败，继续其他执行器。
- **唯一停止循环的条件**是步骤 11 中的停止条件。
- **信任边界**：循环在目标仓库内按原样运行基准命令。用户在设置期间明确确认仓库路径和基准命令。循环不会安装包、修改系统配置或访问基准命令之外的网络资源。
- **密封文件**：validate.sh 强制执行基准代码不能被循环修改，防止自我修改评估。

---

## 状态跟踪

自我改进工件位于由 `scripts/resolve-paths.mjs` 返回的已解析根目录下。

- 新运行默认为 `.omc/self-improve/topics/default/`。
- 当用户提供主题或 slug 时，使用 `.omc/self-improve/topics/{topic_slug}/`。
- 当没有显式提供主题/slug 且该平面布局已存在时，`.omc/self-improve/` 处的旧版单轨状态仅作为兼容性回退有效。

将下面的 `<self-improve-root>/` 视为该已解析根目录：

```
<self-improve-root>/
├── config/                    # 用户配置
│   ├── settings.json          # agents, benchmark, thresholds, sealed_files
│   ├── goal.md                # 改进目标 + 目标指标
│   ├── harness.md             # 护栏规则 (H001/H002/H003)
│   └── idea.md                # 用户实验想法
├── state/                     # 运行时状态
│   ├── agent-settings.json    # iterations, best_score, status, counters
│   ├── iteration_state.json   # 迭代内进度（可恢复性）
│   ├── research_briefs/       # 每轮研究输出
│   ├── iteration_history/     # 每轮完整历史
│   ├── merge_reports/         # 锦标赛结果
│   └── plan_archive/          # 归档计划（永久）
├── plans/                     # 活跃计划（当前轮次）
└── tracking/                  # 可视化数据
    ├── raw_data.json          # 所有候选分数
    ├── baseline.json          # 初始基准分数
    ├── events.json            # 配置变更
    └── progress.png           # 生成的图表
```

OMC 模式生命周期：`.omc/state/sessions/{sessionId}/self-improve-state.json`

---

## 代理映射

所有增强通过 Task 描述上下文在生成时传递。不修改现有代理 .md 文件。

| 步骤 | 角色 | OMC 代理 | 模型 |
|------|------|----------|------|
| 研究 | 代码库分析 + 假设生成 | general-purpose Agent | opus |
| 规划 | 假设 → 结构化计划 | oh-my-claudecode:planner | opus |
| 架构审查 | 6 点计划审查 | oh-my-claudecode:architect | opus |
| 评论家审查 | 护栏规则执行 | oh-my-claudecode:critic | opus |
| 执行 | 实现计划 + 运行基准 | oh-my-claudecode:executor | opus |
| Git 操作 | 原子合并/标签/PR | oh-my-claudecode:git-master | sonnet |
| 目标设置 | 交互式访谈 | （直接在此技能中） | N/A |
| 基准设置 | 创建 + 验证基准 | custom agent | opus |

**研究提示**：从此技能目录读取 `si-researcher.md` 并将其内容作为代理提示传递。

**基准构建器**：从此技能目录读取 `si-benchmark-builder.md` 并将其内容作为代理提示传递。

**目标澄清器**：从此技能目录读取 `si-goal-clarifier.md` 并直接在此上下文中执行访谈（交互式，需要用户）。

---

## 输入

在启动时和每次迭代开始时读取这些文件：

| 文件 | 用途 |
|------|------|
| `<self-improve-root>/config/settings.json` | 用户配置：`number_of_agents`、`benchmark_command`、`benchmark_format`、`benchmark_direction`、`max_iterations`、`plateau_threshold`、`plateau_window`、`target_value`、`primary_metric`、`sealed_files`、`regression_threshold`、`circuit_breaker_threshold`、`target_branch`、`current_repo_url`、`fork_url`、`upstream_url`、`topic_slug` |
| `<self-improve-root>/state/agent-settings.json` | 运行时：`iterations`、`best_score`、`plateau_consecutive_count`、`circuit_breaker_count`、`status`、`goal_slug`（派生：目标的小写下划线形式，跨会话持久化） |
| `<self-improve-root>/state/iteration_state.json` | 每迭代进度用于可恢复性 |
| `<self-improve-root>/config/goal.md` | 改进目标、目标指标、范围 |
| `<self-improve-root>/config/harness.md` | 护栏规则（H001、H002、H003） |

---

## 设置阶段

1. 检查目标仓库路径是否存在。如果未配置，向用户询问要改进的仓库路径。
2. 通过运行 `node {skill_dir}/scripts/resolve-paths.mjs --project-root {repo_path} [--topic "..."] [--slug "..."] --ensure-dirs` 解析 `<self-improve-root>`。
3. 通过从此技能目录的 `templates/` 复制到已解析的 `config/` 根目录来创建 `<self-improve-root>/` 目录结构。
4. 读取 `<self-improve-root>/state/agent-settings.json`。检查 `si_setting_goal`、`si_setting_benchmark`、`si_setting_harness`。
4. **信任确认**（强制，不可跳过）：
   a. 如果 agent-settings.json 中的 `trust_confirmed` 已为 `true`，跳到步骤 5（恢复路径）。
   b. 显示目标仓库路径并要求用户确认：
      `"自我改进将在 {repo_path} 内运行基准命令。这会在该仓库中执行任意代码。确认？[yes/no]"`
   c. 如果用户拒绝：中止设置并退出。不要继续。
   d. 记录同意：在 agent-settings.json 中设置 `trust_confirmed: true`。
5. 当已解析根目录是主题范围时，将 `topic_slug` 持久化到 `config/settings.json` 中，以便未来的恢复保持在同一轨道上。
6. 如果目标未设置 → 从此技能目录读取 `si-goal-clarifier.md` 并直接在此上下文中运行 4 维度苏格拉底式访谈（目标、指标、目标、范围）。将结果写入 `<self-improve-root>/config/goal.md`。
6. 如果基准未设置 → 从此技能目录读取 `si-benchmark-builder.md`，生成一个自定义 Agent(model=opus) 以其内容作为提示。代理调查仓库，创建或包装基准，验证 3 次，并记录基线。
   基准设置后，向用户确认基准命令：
      `"基准命令：{benchmark_command}。这将在循环期间重复运行。确认？[yes/no]"`
   如果用户拒绝：中止设置并退出。
7. 如果护具未设置 → 向用户确认默认护栏规则（H001/H002/H003）或自定义。
8. **门控**：`si_setting_goal`、`si_setting_benchmark`、`si_setting_harness`、`trust_confirmed` 必须全部为 true。
9. **创建改进分支**（如果不存在）：
   ```
   git -C {repo_path} checkout -b improve/{goal_slug} {target_branch}
   git -C {repo_path} checkout {target_branch}
   ```
   其中 `{goal_slug}` 从目标目标派生（小写、下划线）。如果分支已存在，跳过创建。在 agent-settings.json 中持久化 `goal_slug`。
10. **模式排他性**：调用 `state_list_active`。如果 autopilot、ralph 或 ultrawork 处于活跃状态，拒绝启动。
11. 写入初始状态：`state_write(mode='self-improve', active=true, iteration=0, started_at=<now>)`

---

## Git 策略

所有 git 操作发生在目标仓库内，不在 OMC 项目根目录中。

- **改进分支**：`improve/{goal_slug}` — 仅累积获胜变更。
- **实验分支**：`experiment/round_{n}_executor_{id}` — 短期，每个执行器一个。
- **归档标签**：`archive/round_{n}_executor_{id}` — 失败分支在删除前标记。
- **Worktree 设置**（SKILL.md 在每个执行器前创建）：
  ```
  git -C {repo_path} worktree add worktrees/round_{n}_executor_{id} -b experiment/round_{n}_executor_{id} improve/{goal_slug}
  ```
- **获胜者合并**通过 `oh-my-claudecode:git-master`：
  ```
  Merge experiment/round_{n}_executor_{winner_id} into improve/{goal_slug} with --no-ff
  Message: "Iteration {n}: {hypothesis} (score: {before} → {after})"
  ```
- **合并后推送**：`git -C {repo_path} push origin improve/{goal_slug}`（备份，非阻塞）
- **失败者归档**：通过 git-master 标签 + 删除。

---

## 改进循环

**门控**：所有设置必须为 true。一旦门控通过，连续执行不停止。

更新 `state_write(mode='self-improve', active=true, status="running")`。

### 步骤 0 — 过期 Worktree 清理（强制，每次迭代运行）

**前提条件**：此步骤必须在任何其他步骤（包括恢复逻辑）之前完成。它是幂等的，可以安全地多次运行。

1. 列出目标仓库中的所有 worktree：`git -C {repo_path} worktree list`
2. 对于任何匹配 `worktrees/round_*` 但不属于当前迭代的 worktree：使用 `git -C {repo_path} worktree remove {path} --force` 移除
3. 运行 `git -C {repo_path} worktree prune` 清理过期引用
4. 这处理崩溃恢复 — 来自中断迭代的孤立 worktree 在新迭代开始前清理

### 步骤 1 — 刷新状态

`state_write(mode='self-improve', active=true, iteration=N)` 以重置 30 分钟 TTL。

### 步骤 2 — 检查停止请求

通过 `state_read(mode='self-improve')` 读取状态。

如果状态被清除（调用了取消）或状态为 `user_stopped`：
  a. 在 `<self-improve-root>/state/agent-settings.json` 中设置 `status: "user_stopped"`
  b. 更新 `iteration_state.json`：设置 `status: "interrupted"`，记录 `current_step`
  c. 清理当前轮次的任何活跃 worktree（步骤 0 逻辑）
  d. 日志：`"Self-improve stopped by user at iteration {N}, step {current_step}"`
  e. 优雅退出 — 不要再次调用 /cancel（已取消）

### 步骤 3 — 检查用户想法

读取 `<self-improve-root>/config/idea.md`。如果非空，为规划器快照内容。在规划器消耗后清除。

### 步骤 4 — 研究

生成 1 个 general-purpose Agent(model=opus)，以 `si-researcher.md` 的内容作为提示。

在提示中传入：
- 当前迭代编号
- 目标仓库路径
- `<self-improve-root>/config/goal.md` 的路径
- `<self-improve-root>/state/iteration_history/` 的路径（所有先前记录）
- `<self-improve-root>/state/research_briefs/` 的路径（先前简报）
- `data_contracts.md` 第 3 节的内容（研究简报 schema）

预期输出：研究简报 JSON → `<self-improve-root>/state/research_briefs/round_{n}.json`

如果研究员失败，仅使用历史继续。

### 步骤 5 — 规划

并行生成 N 个 `oh-my-claudecode:planner`(model=opus) 代理（N = 设置中的 `number_of_agents`）。

在每个规划器的提示中传入：
- 规划器身份（planner_a、planner_b、planner_c...）
- 研究简报路径
- 迭代历史路径
- 来自 `<self-improve-root>/config/harness.md` 的护栏规则
- 计划文档的数据合约 schema
- **覆盖指令**：输出 JSON（非 markdown），跳过访谈模式，每个计划生成恰好一个可测试假设，包含 approach_family 标签和 history_reference。
- 用户想法（如果有，planner_a 优先）

预期输出：计划文档 JSON → `<self-improve-root>/plans/round_{n}/plan_planner_{id}.json`

### 步骤 6 — 审查

对于每个计划，**顺序执行**（架构师在评论家之前）：

**6a. 架构审查**：生成 `oh-my-claudecode:architect` 配合计划 + 6 点检查清单：
1. 可测试性 — 假设是否可测试？
2. 新颖性 — 与先前尝试不同？
3. 范围 — 大小合适？
4. 目标文件 — 存在、未密封？
5. 实现清晰度 — 执行器能否无需猜测即可实现？
6. 预期结果 — 基于证据是否现实？

架构师裁决仅为**建议性**。

**6b. 评论家审查**：生成 `oh-my-claudecode:critic` 配合计划 + 护栏规则：
- H001：恰好一个假设（零个或多个则拒绝）
- H002：无 approach_family 连续重复 >= 3
- H003：轮次内多样性（同轮次无两个计划同族）
- 对 data_contracts.md 的 schema 验证
- 历史感知检查

评论家设置 `critic_approved: true` 或 `false`。`false` 的计划被排除在执行之外。

如果所有计划被拒绝，记录并跳到步骤 9。

### 步骤 7 — 执行

对于每个已批准的计划，并行生成 `oh-my-claudecode:executor`(model=opus)。

**生成前**，创建 worktree：
```
git -C {repo_path} worktree add worktrees/round_{n}_executor_{id} -b experiment/round_{n}_executor_{id} improve/{goal_slug}
```

在每个执行器的提示中传入：
- 已批准的计划 JSON
- Worktree 目录路径
- 设置中的基准命令
- 设置中的密封文件列表
- 此技能目录中 `scripts/validate.sh` 的路径
- 基准结果的数据合约 schema
- **覆盖指令**：忠实实现计划，在基准测试前运行 validate.sh，运行基准命令，生成基准结果 JSON 作为输出。

预期输出：基准结果 JSON（由执行器写入或作为输出返回）。

### 步骤 8 — 锦标赛选择

SKILL.md 直接执行（不委托）：

1. **收集**所有执行器结果
2. **过滤**到 `status: "success"` 仅。如果零候选，跳到步骤 9（记录和可视化）。
3. **排名**按 `benchmark_score`（遵守 `benchmark_direction`）
4. **排名候选循环** — 对每个候选按排名顺序（最佳优先）：
   a. **无回归检查**：候选分数必须改善或持平于 `best_score`，遵守 `benchmark_direction`（`higher_is_better`：分数 >= best_score；`lower_is_better`：分数 <= best_score）
   b. **合并**通过 `oh-my-claudecode:git-master`：`git merge experiment/round_{n}_executor_{id} --no-ff -m "Iteration {n}: {hypothesis} (score: {before} → {after})"`
   c. **重新基准**在合并状态上确认改善
   d. 如果重新基准**确认**改善：**接受获胜者**，中断循环
   e. 如果重新基准显示**回归**：**撤销合并**通过 `git -C {repo_path} reset --hard HEAD~1`，继续下一个候选
   f. 如果合并**冲突**：`git -C {repo_path} merge --abort`，继续下一个候选
5. 如果有获胜者被接受且设置中 `auto_push` 为 `true`：**推送**改进分支：`git -C {repo_path} push origin improve/{goal_slug}`（非阻塞）。
   如果 `auto_push` 为 `false`（默认）：跳过推送。日志：`"Push skipped (auto_push: false). Run manually: git -C {repo_path} push origin improve/{goal_slug}"`
6. **归档**所有非获胜分支通过 git-master：标签 + 删除
7. 如果没有候选存活循环：本轮无合并。改进分支保持先前状态。
8. **写入合并报告** JSON 到 `<self-improve-root>/state/merge_reports/round_{n}.json`（schema：data_contracts.md 第 9 节）。

### 步骤 9 — 记录和可视化

1. 将迭代历史写入 `<self-improve-root>/state/iteration_history/round_{n}.json`
2. 更新 `<self-improve-root>/state/agent-settings.json`：
   - 将 `iterations` 增加 1
   - 如果有获胜者且改善超过 `plateau_threshold`（`abs(new_score - best_score) >= plateau_threshold`）：更新 `best_score`，重置 `plateau_consecutive_count = 0`，重置 `circuit_breaker_count = 0`
   - 如果有获胜者且改善低于阈值（`abs(new_score - best_score) < plateau_threshold`）：如果更好则更新 `best_score`，增加 `plateau_consecutive_count += 1`，重置 `circuit_breaker_count = 0`
   - 如果无获胜者（全部被拒绝、全部失败或全部回归）：增加 `circuit_breaker_count += 1`（不要增加 `plateau_consecutive_count` — plateau 跟踪停滞的胜利，不是失败）
3. 追加到 `<self-improve-root>/tracking/raw_data.json`（每个候选一个条目）
4. 运行 `python3 {skill_dir}/scripts/plot_progress.py --tracking-dir <self-improve-root>/tracking` 进行可视化
5. 归档计划：将当前轮次计划复制到 `state/plan_archive/round_{n}/`

### 步骤 10 — 清理

移除 worktree：
```
git -C {repo_path} worktree remove worktrees/round_{n}_executor_{id} --force
git -C {repo_path} worktree prune
```

更新 `iteration_state.json` 状态为 `completed`。

### 步骤 11 — 停止条件检查

评估所有条件。如果任一为 true，退出：

| 条件 | 检查 |
|------|------|
| 用户停止 | agent-settings 中 `status == "user_stopped"` 或状态被清除 |
| 达到目标 | `best_score` 达到/超过 `target_value`（遵守方向） |
| 平台期 | `plateau_consecutive_count >= plateau_window` |
| 最大迭代 | `iterations >= max_iterations` |
| 断路器 | `circuit_breaker_count >= circuit_breaker_threshold` |

如果无停止条件：立即回到步骤 1。

---

## 可恢复性

**前提条件**：步骤 0（过期 worktree 清理）必须在任何恢复逻辑执行之前完成，无论先前状态如何。

在调用时，进入循环前：

1. **始终运行步骤 0**（过期 worktree 清理） — 即使是全新启动
2. 读取 `<self-improve-root>/state/agent-settings.json`：
   - 如果 `status: "user_stopped"`：询问用户 `"Previous run was stopped at iteration {N}. Resume? [yes/no]"`。如果否，退出。如果是，继续。
   - 如果 `status: "running"`：会话崩溃 — 自动恢复（无用户提示）
   - 如果 `status: "idle"`：全新启动
3. 仅在 agent-settings.json 中 `trust_confirmed` 为 `false` 时重新确认信任门控
4. 读取 `<self-improve-root>/state/iteration_state.json`：
   - `status: "in_progress"` → 从 `current_step` 恢复，跳过已完成的子步骤
   - `status: "completed"` → 开始下一次迭代
   - `status: "failed"` → 如果需要完成记录步骤，开始下一次迭代
   - 文件缺失 → 从迭代 1 开始

---

## 完成

当循环退出时：

1. 更新 agent-settings.json 为最终状态
2. 如果 `target_reached` 且设置中 `auto_pr` 为 `true`：生成 git-master 从 `improve/{goal_slug}` 到上游创建 PR。
   如果 `auto_pr` 为 `false`（默认）：跳过 PR 创建。日志：`"PR creation skipped (auto_pr: false). Run manually: gh pr create --head improve/{goal_slug} --base {target_branch}"`
3. 最后运行一次 plot_progress.py
4. 打印摘要报告：
   ```
   === Self-Improvement Loop Complete ===
   Status: {status}
   Iterations: {iterations}
   Best Score: {best_score} (baseline: {baseline})
   Improvement: {delta} ({delta_pct}%)
   ```
5. 运行 `/oh-my-claudecode:cancel` 进行干净的状态清理

---

## 错误处理

| 情况 | 操作 |
|------|------|
| 代理未能产生输出 | 重试一次。如果仍无输出，记录并继续。 |
| 研究员产生空简报 | 继续 — 规划器仅从历史工作。 |
| 所有计划被评论家拒绝 | 跳过执行。记录。继续下一次迭代。 |
| 所有执行器失败 | 跳过锦标赛。记录失败。继续。 |
| 合并冲突 | 拒绝候选，尝试下一个。 |
| 重新基准回归 | 拒绝候选，撤销合并，尝试下一个。 |
| 推送失败 | 记录警告。继续 — 推送是备份。 |
| Worktree 已存在 | 移除并重新创建。 |
| 设置损坏 | 报告并停止。 |

---

## 方法族分类法

每个计划必须标记恰好一个：

| 标签 | 描述 |
|------|------|
| `architecture` | 模型/组件结构变更 |
| `training_config` | 优化器、学习率、调度器、批大小 |
| `data` | 数据加载、增强、预处理 |
| `infrastructure` | 混合精度、分布式训练、编译内核 |
| `optimization` | 算法/数值优化 |
| `testing` | 评估方法变更 |
| `documentation` | 仅文档变更 |
| `other` | 不属于以上 — 在证据中解释 |
