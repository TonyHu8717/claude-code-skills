---
name: autoresearch
description: 具有严格评估器契约、markdown 决策日志和最大运行时间停止行为的有状态单任务改进循环
argument-hint: "[--mission-dir <path>] [--max-runtime <duration>] [--cron <spec>] [--resume <run-id>]"
level: 4
---

<Purpose>
Autoresearch 是一个有状态技能，用于有界的、评估器驱动的迭代改进。它一次拥有一个任务，持续迭代直到未通过的结果，将每次评估和决策记录为持久产物，仅在达到显式最大运行时间上限或其他显式终止条件时停止。
</Purpose>

<Use_When>
- 你已有来自 `/deep-interview --autoresearch` 的任务和评估器
- 你想要带有严格评估的持久单任务改进
- 你需要 `.omc/autoresearch/` 下的持久实验日志
- 你想要通过 Claude Code 原生 cron 支持的定期重新运行路径
</Use_When>

<Do_Not_Use_When>
- 你需要在运行时生成评估器 — 请先使用 `/deep-interview --autoresearch`
- 你需要多个任务协调运行 — v1 禁止这样做
- 你想要已弃用的 `omc autoresearch` CLI 流程 — 它不再是权威路径
</Do_Not_Use_When>

<Contract>
- v1 仅支持单任务
- 任务设置/评估器生成保留在 `deep-interview --autoresearch` 中
- 评估器输出必须是结构化 JSON，包含必需的布尔 `pass` 和可选的数值 `score`
- 未通过的迭代**不会**停止运行
- 停止条件是显式且有界的，最大运行时间是主要的严格停止钩子
</Contract>

<Required_Artifacts>
规范的持久存储位于 `.omc/autoresearch/<mission-slug>/` 和/或 `.omc/logs/autoresearch/<run-id>/`。

最低必需产物：
- 任务规范
- 评估器脚本或命令引用
- 每次迭代的评估 JSON
- markdown 决策日志

推荐的规范结构：
```text
.omc/autoresearch/<mission-slug>/
  mission.md
  evaluator.json
  runs/<run-id>/
    evaluations/
      iteration-0001.json
      iteration-0002.json
    decision-log.md
```
尽可能重用现有的运行时产物，而不是不必要地复制它们。
</Required_Artifacts>

<Workflow>
1. 确认单个任务存在且评估器设置已可用。
2. 确保 `autoresearch` 的模式/状态处于活动状态并记录：
   - 任务 slug/目录
   - 评估器引用
   - 迭代计数
   - 开始/更新时间戳
   - 显式最大运行时间或截止时间
3. 每次迭代：
   - 运行恰好一个实验/变更周期
   - 运行评估器
   - 持久化机器可读的评估 JSON
   - 追加人类可读的 markdown 决策日志条目
   - 即使评估未通过也继续
4. 在以下情况停止：
   - 达到最大运行时间上限
   - 用户显式取消
   - 运行时记录了其他显式终止条件
</Workflow>

<Cron_Integration>
Claude Code 原生 cron 是定期任务增强的受支持集成点。在 v1 中，优先记录/配置 cron 输入而不是构建大型调度器 UI。

如果使用 cron：
- 每个计划作业保持一个任务
- 保持相同的任务/评估器契约
- 追加新的运行产物而不是覆盖先前的实验
</Cron_Integration>

<Execution_Policy>
- 不要将执行交回 `omc autoresearch`
- 不要创建多任务协调
- 优先重用 `src/autoresearch/*` 运行时/模式辅助工具，当它们已经匹配更严格的契约时
- 保持日志对人类有用，而不仅仅对机器
</Execution_Policy>
