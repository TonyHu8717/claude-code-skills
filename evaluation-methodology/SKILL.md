---
name: evaluation-methodology
description: "PluginEval 质量方法论 — 维度、评分标准、统计方法和评分公式。在理解插件质量如何衡量、解释特定维度的低分、决定如何提高技能的触发准确性或编排适配度、为您的市场校准评分阈值、或向 Neon 等外部合作伙伴解释质量徽章时使用此技能。"
---

# 评估方法论

本文档是 PluginEval 如何衡量插件和技能质量的权威参考。
涵盖三个评估层、所有十个评分维度、组合公式、徽章阈值、反模式标志、Elo 排名和可操作的改进提示。

相关：[完整评分标准锚点](references/rubrics.md)

---

## 三个评估层

PluginEval 堆叠三个互补层。每层对每个适用维度产生 0.0 到 1.0 之间的分数，后续层根据每维度的混合权重覆盖或与早期层混合。

### 层 1 — 静态分析

**速度：** < 2 秒。无 LLM 调用。确定性。

静态分析器（`layers/static.py`）对解析后的 SKILL.md 直接运行六个子检查：

| 子检查 | 测量内容 |
|---|---|
| `frontmatter_quality` | 名称存在、描述长度、触发短语质量 |
| `orchestration_wiring` | 输出/输入文档、代码块数量、编排器反模式 |
| `progressive_disclosure` | 行数 vs 最佳范围（200-600 行）、references/ 和 assets/ 奖励 |
| `structural_completeness` | 标题密度、代码块、示例部分、故障排除部分 |
| `token_efficiency` | MUST/NEVER/ALWAYS 密度、重复行重复率 |
| `ecosystem_coherence` | 对其他技能/代理的交叉引用、"related"/"see also" 提及 |

这六个子检查直接馈入最终十个维度中的六个（通过 `STATIC_TO_DIMENSION` 映射）。其余四个维度 — `output_quality`、`scope_calibration`、`robustness` 和 `triggering_accuracy` 的部分 — 没有静态贡献，完全依赖层 2 和/或层 3。

**反模式惩罚**以乘法方式应用于层 1 分数：

```
penalty = max(0.5, 1.0 − 0.05 × anti_pattern_count)
```

每个额外检测到的反模式使分数降低 5%，最低降至 50%。

### 层 2 — LLM 评审

**速度：** 30-90 秒。一次或多次 LLM 调用（默认 Sonnet）。非确定性。

`eval-judge` 代理读取 SKILL.md 和任何 `references/` 文件，然后使用锚定评分标准（见 [references/rubrics.md](references/rubrics.md)）对四个维度评分：

1. **触发准确性** — 从 10 个心理测试提示派生的 F1 分数
2. **编排适配度** — Worker 纯度评估（0-1 评分标准）
3. **输出质量** — 模拟 3 个真实任务；评估指令质量
4. **范围校准** — 判断相对于技能类别的深度和广度

评审返回结构化 JSON 对象（无 markdown 围栏），评估引擎将其合并到组合中。当 `judges > 1` 时，分数取平均值，并报告 Cohen's kappa 作为评审间一致性指标。

### 层 3 — 蒙特卡洛模拟

**速度：** 5-20 分钟。N=50 次模拟 Agent SDK 调用（默认）。统计性。

蒙特卡洛通过技能运行 `N` 个真实提示并记录：

- **激活率** — 触发技能的提示比例
- **输出一致性** — 质量分数的变异系数（CV）
- **失败率** — 带 Clopper-Pearson 精确置信区间的错误/崩溃比例
- **令牌效率** — 中位令牌数、IQR、异常值数量

层 3 组合公式：

```
mc_score = 0.40 × activation_rate
         + 0.30 × (1 − min(1.0, CV))
         + 0.20 × (1 − failure_rate)
         + 0.10 × efficiency_norm
```

其中 `efficiency_norm = max(0, 1 − median_tokens / 8000)`。

---

## 组合评分公式

最终分数是每维度跨所有三层的加权混合，然后求和：

```
composite = Σ(dimension_weight × blended_dimension_score) × 100 × anti_pattern_penalty
```

### 维度权重

| 维度 | 权重 | 重要性 |
|---|---|---|
| `triggering_accuracy` | 0.25 | 从不触发或错误触发的技能没有价值 |
| `orchestration_fitness` | 0.20 | 技能必须是纯 worker；监督逻辑属于代理 |
| `output_quality` | 0.15 | 正确、完整的输出是主要交付物 |
| `scope_calibration` | 0.12 | 既不是存根也不是臃肿的怪物 |
| `progressive_disclosure` | 0.10 | SKILL.md 精简；详细内容在 references/ 中 |
| `token_efficiency` | 0.06 | 每次调用的最小上下文浪费 |
| `robustness` | 0.05 | 处理边缘情况而不崩溃 |
| `structural_completeness` | 0.03 | 正确的部分按正确顺序排列 |
| `code_template_quality` | 0.02 | 可工作、可复制粘贴的示例 |
| `ecosystem_coherence` | 0.02 | 交叉引用；与兄弟技能无重复 |

### 层混合权重

每维度从不同层以不同比例提取。当所有三层都激活时（`--depth deep` 或 `certify`）：

| 维度 | 静态 | 评审 | 蒙特卡洛 |
|---|---|---|---|
| `triggering_accuracy` | 0.15 | 0.25 | 0.60 |
| `orchestration_fitness` | 0.10 | 0.70 | 0.20 |
| `output_quality` | 0.00 | 0.40 | 0.60 |
| `scope_calibration` | 0.30 | 0.55 | 0.15 |
| `progressive_disclosure` | 0.80 | 0.20 | 0.00 |
| `token_efficiency` | 0.40 | 0.10 | 0.50 |
| `robustness` | 0.00 | 0.20 | 0.80 |
| `structural_completeness` | 0.90 | 0.10 | 0.00 |
| `code_template_quality` | 0.30 | 0.70 | 0.00 |
| `ecosystem_coherence` | 0.85 | 0.15 | 0.00 |

在 `--depth standard`（仅静态 + 评审）时，混合权重重新标准化以去除蒙特卡洛列。在 `--depth quick`（仅静态）时，所有权重落在层 1 上。

### 混合分数计算

对于给定深度，维度 `d` 的混合分数为：

```
blended[d] = Σ( layer_weight[d][layer] × layer_score[d][layer] )
             ─────────────────────────────────────────────────────
             Σ( layer_weight[d][layer] for available layers )
```

此标准化确保在标准深度跳过蒙特卡洛不会人为降低分数。

---

## 解释维度分数

每个维度分数是 `[0.0, 1.0]` 中的浮点数。CLI 将其转换为字母等级：

| 等级 | 分数范围 | 含义 |
|---|---|---|
| A | 0.90 – 1.00 | 优秀 — 无需实质性改进 |
| B | 0.80 – 0.89 | 良好 — 仅有轻微差距 |
| C | 0.70 – 0.79 | 足够 — 一两个明确改进领域 |
| D | 0.60 – 0.69 | 勉强 — 需要有针对性的工作 |
| F | < 0.60 | 不及格 — 需要重大补救 |

阅读报告时，首先关注权重最高的最低等级维度。`triggering_accuracy`（权重 0.25）的 D 比 `ecosystem_coherence`（权重 0.02）的 D 代价大得多。

当层 2 或层 3 运行时，报告中会出现**置信区间**。窄置信区间（± < 5 分）表示分数稳定。宽置信区间表示不一致 — 通常由模糊描述或对某些提示风格有效但对其他风格无效的指令引起。

---

## 质量徽章

徽章需要组合分数阈值和 Elo 阈值（当 Elo 可用时）。`Badge.from_scores()` 逻辑首先检查组合分数，然后在提供时检查 Elo：

| 徽章 | 组合分数 | Elo | 含义 |
|---|---|---|---|
| 白金 ★★★★★ | ≥ 90 | ≥ 1600 | 参考质量 — 适合金标准语料库 |
| 金 ★★★★ | ≥ 80 | ≥ 1500 | 生产就绪 |
| 银 ★★★ | ≥ 70 | ≥ 1400 | 功能性，有改进机会 |
| 铜 ★★ | ≥ 60 | ≥ 1300 | 最低可行 — 尚不推荐给用户 |
| — | < 60 | 任何 | 未达到最低标准 |

当 Elo 尚未计算时（即在 quick 或 standard 深度且未使用 `certify` 时），跳过 Elo 阈值。在这些情况下，技能可以仅凭组合分数获得徽章。

---

## 反模式标志

静态分析器检测五种反模式。每种都带有严重性乘数，用于惩罚公式。

### 过度约束（OVER_CONSTRAINED）

**触发条件：** SKILL.md 中 MUST、ALWAYS 或 NEVER 出现超过 15 次。

**问题：** 过于规范的指令减少模型灵活性，增加令牌开销，并表明作者试图微管理每个输出而不是提供原则性指导。

**修复：** 审计每个 MUST/ALWAYS/NEVER。尽可能用解释性框架替代指令性语言。仅为真正的安全或正确性要求保留硬约束。目标每 100 行少于 10 个此类指令。

### 空描述（EMPTY_DESCRIPTION）

**触发条件：** 前置元数据 `description` 字段去除空白后少于 20 个字符。

**问题：** 没有意义的描述，Claude Code 插件系统无法确定何时调用该技能。该技能对自动调用不可见。

**修复：** 编写至少 60-120 个字符的描述，包括：
- "Use this skill when..." 或 "Use when..." 触发子句
- 两个或更多用逗号或 "or" 分隔的具体上下文

### 缺少触发器（MISSING_TRIGGER）

**触发条件：** 描述不包含 "use when"、"use this skill when"、"use proactively" 或 "trigger when"（不区分大小写）。

**问题：** 即使是长描述，如果不包含明确的触发信号，对自动调用也无用。系统的路由模型需要明确的提示。

**修复：** 在描述前加上 "Use this skill when..."，后跟具体场景。
示例："Use this skill when measuring plugin quality, interpreting score reports, or explaining badge thresholds to a team."

### 臃肿技能（BLOATED_SKILL）

**触发条件：** SKILL.md 超过 800 行且技能没有 `references/` 目录。

**问题：** 单体 SKILL.md 在每次调用时强制将整个文档加载到上下文中，浪费令牌在仅在边缘情况下需要的内容上。

**修复：** 创建 `references/` 目录并将支持材料移到那里：
- 详细评分标准 -> `references/rubrics.md`
- 扩展示例 -> `references/examples.md`
- 配置参考 -> `references/config.md`

SKILL.md 应使用 `[text](references/filename.md)` 链接到这些文件，以便模型可以按需获取。

### 孤立引用（ORPHAN_REFERENCE）

**触发条件：** SKILL.md 包含 markdown 链接 `[text](references/filename)`，其中 `filename` 在 `references/` 目录中不存在。

**问题：** 死链接浪费令牌在永远不会解析的上下文中，并使模型困惑。

**修复：** 创建缺失的引用文件或删除死链接。

### 断裂交叉引用（DEAD_CROSS_REF）

**触发条件：** SKILL.md 通过相对路径引用另一个技能或代理，且该路径无法从 skills/ 目录解析。

**问题：** 断裂的生态系统链接削弱插件的连贯性分数，并可能导致模型尝试导航到不存在的文件。

**修复：** 验证引用的技能存在。更新路径或删除引用。

---

## Elo 排名

PluginEval 使用 Elo/Bradley-Terry 评级系统将技能与金标准语料库进行排名。

**起始评级：** 1500（按惯例为语料库中位数）。

**K 因子：** 32（中等风险评级的标准值）。

**期望分数公式**（标准 Elo）：

```
E(A vs B) = 1 / (1 + 10^((B_rating − A_rating) / 400))
```

**每次对战后的评级更新：**

```
new_rating = old_rating + 32 × (actual_score − expected_score)
```

其中 `actual_score` 胜为 1.0，平为 0.5，负为 0.0。

**置信区间**通过 500 样本自助法计算，报告为 95% 置信区间。
**语料库百分位数**反映与金标准语料库的成对胜率。
**位置偏差检查：** 成对以两种顺序评估；不一致被标记。

`plugin-eval init` 命令从插件目录构建语料库索引：

```bash
plugin-eval init ./plugins --corpus-dir ~/.plugineval/corpus
```

---

## CLI 参考

### 对技能评分（仅快速静态分析）

```bash
plugin-eval score ./path/to/skill --depth quick
```

在 < 2 秒内返回层 1 结果。适用于编写时的快速反馈。

### 使用 LLM 评审评分（默认）

```bash
plugin-eval score ./path/to/skill
```

运行静态 + LLM 评审（标准深度）。需要 30-90 秒。

### 以 JSON 格式输出完整评分

```bash
plugin-eval score ./path/to/skill --output json
```

发出结构化 JSON，包括 `composite.score`、`composite.dimensions` 和 `layers[0].anti_patterns`。适合 CI 集成：

```bash
plugin-eval score ./path/to/skill --depth quick --output json --threshold 70
# 如果分数 < 70 则以代码 1 退出
```

### 完整认证（所有三层 + Elo）

```bash
plugin-eval certify ./path/to/skill
```

运行静态 + LLM 评审 + 蒙特卡洛（50 次模拟）+ Elo 排名。需要 15-20 分钟。
分配质量徽章。在将技能发布到市场之前使用。

### 正面对比

```bash
plugin-eval compare ./skill-a ./skill-b
```

以快速深度评估两个技能并打印逐维度比较表。
适用于在两个实现之间选择或衡量重写前后的改进。

### 初始化 Elo 语料库

```bash
plugin-eval init ./plugins
```

在 `~/.plugineval/corpus` 构建本地语料库索引。Elo 排名工作前必需。

### 组合公式的脚本化

离线复现组合分数（pre-commit hook、CI 门控）：

```python
def composite_score(dimension_scores: dict, anti_pattern_count: int = 0) -> float:
    """复现 PluginEval 组合公式。"""
    WEIGHTS = {
        "triggering_accuracy":    0.25,
        "orchestration_fitness":  0.20,
        "output_quality":         0.15,
        "scope_calibration":      0.12,
        "progressive_disclosure": 0.10,
        "token_efficiency":       0.06,
        "robustness":             0.05,
        "structural_completeness":0.03,
        "code_template_quality":  0.02,
        "ecosystem_coherence":    0.02,
    }
    raw = sum(WEIGHTS[d] * s for d, s in dimension_scores.items())
    penalty = max(0.5, 1.0 - 0.05 * anti_pattern_count)
    return round(raw * 100 * penalty, 2)

# 示例：触发分数较弱的技能
scores = {
    "triggering_accuracy":    0.65,  # D — 需要改进描述
    "orchestration_fitness":  0.85,
    "output_quality":         0.80,
    # … 填写剩余 7 个维度 …
}
# composite_score(scores, anti_pattern_count=1) → ~76.5
```

### JSON 输出格式

`--output json` 的顶层结构：

```json
{
  "composite": { "score": 76.5, "badge": "Silver", "elo": null },
  "dimensions": {
    "triggering_accuracy": { "score": 0.65, "grade": "D", "ci_low": 0.60, "ci_high": 0.70 },
    "orchestration_fitness": { "score": 0.85, "grade": "B", "ci_low": 0.80, "ci_high": 0.90 }
  },
  "layers": [
    { "name": "static", "duration_ms": 1243, "anti_patterns": ["OVER_CONSTRAINED"] },
    { "name": "judge", "duration_ms": 48200, "judges": 1, "kappa": null }
  ]
}
```

在 CI 中解析 `composite.score` 以设置部署门控：

```bash
score=$(plugin-eval score ./my-skill --output json | python3 -c "import sys,json; print(json.load(sys.stdin)['composite']['score'])")
if (( $(echo "$score < 70" | bc -l) )); then
  echo "Quality gate failed: score $score < 70"
  exit 1
fi
```

---

## 提高技能分数的提示

按权重顺序处理维度。最大的收益来自首先修复最高权重的维度。

### 先改进哪个维度

当分数报告显示多个 D/F 等级且需要优先安排工作时使用此表。

| 维度 | 权重 | 典型修复工作量 | 每小时分数影响 | 先修复如果… |
|---|---|---|---|---|
| `triggering_accuracy` | 0.25 | 低 — 描述重写 | 高 | 总分 < 70 |
| `orchestration_fitness` | 0.20 | 中 — 重组部分 | 高 | 技能混合了 worker + 监督逻辑 |
| `output_quality` | 0.15 | 中 — 添加示例 | 中 | 评审分数 < 0.70 |
| `scope_calibration` | 0.12 | 低 — 将内容移至 references/ | 中 | 文件 < 100 或 > 800 行 |
| `progressive_disclosure` | 0.10 | 低 — 创建 references/ 目录 | 中 | 不存在 references/ 目录 |
| `token_efficiency` | 0.06 | 低 — 减少 MUST/ALWAYS/NEVER | 低 | 反模式计数 ≥ 3 |
| `robustness` | 0.05 | 低 — 添加故障排除部分 | 低 | 未记录边缘情况处理 |
| `structural_completeness` | 0.03 | 非常低 — 添加标题/代码块 | 低 | 少于 4 个 H2 标题 |
| `code_template_quality` | 0.02 | 非常低 — 添加语言标签 | 非常低 | 代码块缺少语言标签 |
| `ecosystem_coherence` | 0.02 | 非常低 — 添加相关部分 | 非常低 | 完全没有交叉引用 |

**经验法则：** 先修复 `triggering_accuracy` — 以 0.25 的权重，它每小时带来的组合分数增益比所有低权重维度加起来还多。

### 触发准确性（权重 0.25）

- 包含 "Use this skill when..." 后跟 3-4 个逗号分隔的具体上下文。
- 如果技能应在没有明确用户请求时自动激活，添加 "proactively"。
- 心理测试：编写 5 个应该触发它的提示和 5 个不应该的 — 您的描述是否能区分？如果不能，添加或收紧上下文短语。

### 编排适配度（权重 0.20）

- 记录技能*接收*什么和*返回*什么 — 而非它编排什么。
- 在 SKILL.md 中避免 "orchestrate"、"coordinate"、"dispatch"、"manage workflow"。
- 包含 "Output format" 部分和 2+ 个展示具体 worker 行为的代码块。

### 输出质量（权重 0.15）

- 给出具体、可操作的指令 — 而非仅仅是目标。
- 明确覆盖至少一个边缘情况（空输入、格式错误数据等）。
- 包含展示代表性输入和预期输出的示例部分。
- 指令越具体，评审在此维度的评分越高。

### 范围校准（权重 0.12）

- 目标 200-600 行。低于 100 是存根；超过 800 且无 `references/` 是臃肿。
- 将背景阅读、扩展示例和参考表移至 `references/`。
- 非常窄的技能应与兄弟技能合并；非常广的应拆分。

### 渐进式披露（权重 0.10）

- 添加 `references/` 目录（获得 0.15-0.25 奖励）并将 SKILL.md 聚焦于执行路径。`assets/` 目录增加额外奖励。

### 令牌效率（权重 0.06）

- 审计 MUST/ALWAYS/NEVER 数量。目标每 10 行 < 1 个。
- 合并近似重复的项目符号和重复结构的表。

### 健壮性（权重 0.05）

- 添加覆盖至少 3 种故障模式的 "Troubleshooting" 或 "Edge Cases" 部分。
- 说明技能无法完成任务时返回什么。

### 结构完整性（权重 0.03）

- 确保至少 4 个 H2/H3 标题、3 个代码块、一个示例部分和一个故障排除部分。

### 代码模板质量（权重 0.02）

- 所有代码块必须语法有效且可复制粘贴，带有语言标签。

### 生态系统连贯性（权重 0.02）

- 添加列出兄弟技能或代理（带相对路径）的 "## Related" 部分。
- 避免复制已存在于另一个技能中的内容 — 改为链接到它。

---

## 故障排除

### "添加内容后分数大幅低于预期"

反模式惩罚是复合的。使用 `--output json` 运行并检查 `layers[0].anti_patterns`。如果有 5+ 个反模式，乘数可以将分数降低到原始值的 75%，无论内容有多好。先修复标志。

### "尽管描述详细，triggering_accuracy 仍然很低"

`_description_pushiness` 评分器寻找特定的语法模式，而非仅仅是长度。
验证您的描述包含短语 "Use this skill when" 或 "Use when"（精确措辞很重要 — 这是正则匹配）。还要检查您是否有多个用逗号或 "or" 分隔的用例以获得特异性奖励。

### "LLM 评审分数在不同运行间差异显著"

这对模糊技能是预期的。评审以非确定性方式生成 10 个心理测试提示。通过收紧描述和添加具体示例来提高分数稳定性。当 `judges > 1` 时，平均分数会更稳定。使用 `--depth deep` 配合 `certify` 运行蒙特卡洛以获得统计约束的分数。

### "文件长度正确但 progressive_disclosure 分数很低"

检查文件是否在 200-600 行的最佳范围内。短于 100 行的文件在此子检查上仅得 0.20 分。还要确认 `references/` 文件不是空的 — 评分器检查非空的引用文件，而非仅仅是目录。

### "compare 显示我的重写分数低于原始版本"

快速深度（`--depth quick`）仅运行静态分析。如果重写将内容移至 `references/` 并显著缩短 SKILL.md，结构完整性的静态分数可能会下降，即使整体质量有所提高。运行 `--depth standard` 以获得更公平的比较，包括 LLM 评审对内容质量的评估。

---

## 参考

- [完整评分标准锚点 — 所有 4 个评审维度](references/rubrics.md)

### 相关代理

- **eval-judge**（`../../agents/eval-judge.md`）— 评分层 2 维度（`triggering_accuracy`、`orchestration_fitness`、`output_quality`、`scope_calibration`）的 LLM 评审。当您需要仅重新运行评审层或检查其推理时直接调用。
- **eval-orchestrator**（`../../agents/eval-orchestrator.md`）— 顶层编排器，排序所有三层、合并结果、分配徽章并编写最终报告。在运行完整认证或正面对比两个技能时调用。
