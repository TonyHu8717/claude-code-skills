---
name: skill-creator
description: 创建新技能、修改和改进现有技能，以及衡量技能性能。当用户想从零开始创建技能、编辑或优化现有技能、运行评估测试技能、使用方差分析对技能性能进行基准测试，或优化技能描述以提高触发准确性时使用。
---

# 技能创建器

用于创建新技能并迭代改进它们的技能。

从高层次来看，创建技能的过程如下：

- 决定您希望技能做什么以及大致如何做
- 编写技能草稿
- 创建一些测试提示并在具有技能访问权限的 claude 上运行它们
- 帮助用户定性和定量评估结果
  - 当运行在后台进行时，草拟一些定量评估（如果没有任何评估的话）。然后向用户解释它们
  - 使用 `eval-viewer/generate_review.py` 脚本向用户展示结果供他们查看，也让他们查看定量指标
- 根据用户对结果的评估反馈重写技能（以及定量基准中出现的任何明显缺陷）
- 重复直到满意
- 扩展测试集并在更大规模上再次尝试

使用此技能时，您的工作是弄清楚用户在此过程中的位置，然后介入并帮助他们推进这些阶段。例如，也许他们说"我想为 X 做一个技能"。您可以帮助缩小他们的意思，编写草稿，编写测试用例，弄清楚他们想如何评估，运行所有提示，并重复。

另一方面，也许他们已经有技能的草稿。在这种情况下，您可以直接进入评估/迭代循环。

当然，您应该始终保持灵活，如果用户说"我不需要运行一堆评估，只是和我一起感受"，您可以这样做。

然后在技能完成后（但顺序是灵活的），您还可以运行技能描述改进器，我们有一个完全独立的脚本，用于优化技能的触发。

明白了？好的。

## 与用户沟通

技能创建器可能被各种熟悉编程术语的人使用。如果您没听说过（您怎么可能听说过，这是最近才开始的），现在有一个趋势，Claude 的力量正在激励水管工打开他们的终端，父母和祖父母去谷歌"如何安装 npm"。另一方面，大多数用户可能相当精通计算机。

因此请注意上下文线索以了解如何措辞您的沟通！在默认情况下，给您一些想法：

- "evaluation" 和 "benchmark" 处于边缘，但可以
- 对于 "JSON" 和 "assertion"，您需要看到用户的严肃线索表明他们知道这些东西是什么，然后才能不解释地使用它们

如果有疑问，简要解释术语是可以的，如果您不确定用户是否会理解，可以自由地用简短定义澄清术语。

---

## 创建技能

### 捕获意图

首先理解用户的意图。当前对话可能已经包含用户想要捕获的工作流（例如，他们说"把这变成一个技能"）。如果是这样，首先从对话历史中提取答案 — 使用的工具、步骤序列、用户进行的更正、观察到的输入/输出格式。用户可能需要填补空白，并且应该在继续下一步之前确认。

1. 这个技能应该让 Claude 能做什么？
2. 这个技能应该在什么时候触发？（什么用户短语/上下文）
3. 预期的输出格式是什么？
4. 我们是否应该设置测试用例来验证技能有效？具有客观可验证输出的技能（文件转换、数据提取、代码生成、固定工作流步骤）受益于测试用例。具有主观输出的技能（写作风格、艺术）通常不需要它们。根据技能类型建议适当的默认值，但让用户决定。

### 访谈和研究

主动询问边缘情况、输入/输出格式、示例文件、成功标准和依赖关系的问题。等到您把这部分弄清楚后再编写测试提示。

检查可用的 MCP — 如果对研究有用（搜索文档、查找类似技能、查找最佳实践），如果可用则通过子代理并行研究，否则内联研究。准备好上下文以减少用户的负担。

### 编写 SKILL.md

根据用户访谈，填写以下组件：

- **name**：技能标识符
- **description**：何时触发，做什么。这是主要的触发机制 — 包含技能做什么以及何时使用的具体上下文。所有"何时使用"信息放在这里，不在正文中。注意：目前 Claude 有"触发不足"的倾向 — 在有用时不使用它们。为了解决这个问题，请使技能描述稍微"积极"一些。例如，不要写"如何构建一个简单的快速仪表板来显示内部 Anthropic 数据"，而是写"如何构建一个简单的快速仪表板来显示内部 Anthropic 数据。每当用户提到仪表板、数据可视化、内部指标或想要显示任何类型的企业数据时，即使他们没有明确要求'仪表板'，也要确保使用此技能。"
- **compatibility**：所需工具、依赖（可选，很少需要）
- **技能的其余部分 :)**

### 技能编写指南

#### 技能剖析

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### 渐进式披露

技能使用三级加载系统：
1. **元数据**（name + description）— 始终在上下文中（约 100 词）
2. **SKILL.md 正文** — 技能触发时在上下文中（理想 <500 行）
3. **捆绑资源** — 按需（无限制，脚本可以不加载即执行）

这些字数是近似的，如果需要可以自由地写更长。

**关键模式：**
- 将 SKILL.md 保持在 500 行以内；如果接近此限制，添加额外的层次结构层次以及关于使用技能的模型接下来应该去哪里的清晰指针。
- 从 SKILL.md 清晰地引用文件，并提供何时读取它们的指导
- 对于大型引用文件（>300 行），包含目录

**领域组织**：当技能支持多个领域/框架时，按变体组织：
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude 仅读取相关的引用文件。

#### 无惊讶原则

不言而喻，但技能不得包含恶意软件、漏洞利用代码或任何可能损害系统安全的内容。如果被描述，技能的内容不应对用户的意图感到惊讶。不要配合创建误导性技能或旨在促进未授权访问、数据渗出或其他恶意活动的技能的请求。像"角色扮演为 XYZ"这样的东西是可以的。

#### 编写模式

优先使用祈使形式编写指令。

**定义输出格式** — 您可以这样做：
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**示例模式** — 包含示例很有用。您可以这样格式化它们（但如果示例中有"Input"和"Output"，您可能需要稍微偏离）：
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 写作风格

尝试向模型解释为什么事情很重要，而不是沉重的 MUST。使用心理理论并尝试使技能通用，而不是非常狭窄地针对特定示例。首先编写草稿，然后用新鲜的眼光审视并改进它。

### 测试用例

编写技能草稿后，想出 2-3 个真实的测试提示 — 真实用户实际会说的话。与用户分享：[您不必使用这种确切的语言]"这是我想尝试的几个测试用例。这些看起来对吗，还是您想添加更多？"然后运行它们。

将测试用例保存到 `evals/evals.json`。不要编写断言 — 只需提示。您将在运行进行时的下一步中草拟断言。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

完整 schema 请参见 `references/schemas.md`（包括您稍后将添加的 `assertions` 字段）。

## 运行和评估测试用例

本节是一个连续序列 — 不要中途停止。不要使用 `/skill-test` 或任何其他测试技能。

将结果放在 `<skill-name>-workspace/` 中作为技能目录的同级。在工作区内，按迭代组织结果（`iteration-1/`、`iteration-2/` 等），在其中每个测试用例获得一个目录（`eval-0/`、`eval-1/` 等）。不要预先创建所有这些 — 只需在进行时创建目录。

### 步骤 1：在同一轮次中生成所有运行（有技能和基线）

对于每个测试用例，在同一轮次中生成两个子代理 — 一个有技能，一个没有。这很重要：不要先生成有技能的运行，然后再回来做基线。同时启动所有内容，使其大约在同一时间完成。

**有技能运行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**基线运行**（相同提示，但基线取决于上下文）：
- **创建新技能**：完全没有技能。相同提示，无技能路径，保存到 `without_skill/outputs/`。
- **改进现有技能**：旧版本。编辑前，快照技能（`cp -r <skill-path> <workspace>/skill-snapshot/`），然后将基线子代理指向快照。保存到 `old_skill/outputs/`。

为每个测试用例编写 `eval_metadata.json`（断言暂时可以为空）。给每个评估一个描述性名称，基于它测试的内容 — 不仅仅是"eval-0"。也用这个名称作为目录。如果此迭代使用新的或修改的评估提示，为每个新评估目录创建这些文件 — 不要假设它们从先前迭代延续。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步骤 2：运行进行时，草拟断言

不要只是等待运行完成 — 您可以有成效地利用这段时间。为每个测试用例草拟定量断言并向用户解释。如果 `evals/evals.json` 中已有断言，审查它们并解释它们检查什么。

好的断言是客观可验证的，并且有描述性名称 — 它们应该在基准查看器中清晰可读，以便查看结果的人立即理解每个断言检查什么。主观技能（写作风格、设计质量）更适合定性评估 — 不要将断言强加到需要人类判断的事物上。

草拟后更新 `eval_metadata.json` 文件和 `evals/evals.json` 的断言。同时向用户解释他们在查看器中会看到什么 — 定性输出和定量基准。

### 步骤 3：运行完成时，捕获计时数据

当每个子代理任务完成时，您会收到包含 `total_tokens` 和 `duration_ms` 的通知。立即将此数据保存到运行目录中的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是捕获此数据的唯一机会 — 它通过任务通知传递，不会在其他地方持久化。在每个通知到达时处理它，而不是尝试批量处理。

### 步骤 4：评分、聚合并启动查看器

所有运行完成后：

1. **评分每个运行** — 生成评分子代理（或内联评分），读取 `agents/grader.md` 并根据输出评估每个断言。将结果保存到每个运行目录中的 `grading.json`。grading.json 的 expectations 数组必须使用 `text`、`passed` 和 `evidence` 字段（不是 `name`/`met`/`details` 或其他变体） — 查看器依赖这些确切的字段名。对于可以编程检查的断言，编写并运行脚本而不是目测 — 脚本更快、更可靠，并且可以跨迭代重用。

2. **聚合为基准** — 从 skill-creator 目录运行聚合脚本：
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   这生成 `benchmark.json` 和 `benchmark.md`，包含每种配置的 pass_rate、时间和 token，以及均值 ± 标准差和 delta。如果手动生成 benchmark.json，请参见 `references/schemas.md` 了解查看器期望的确切 schema。
将每个 with_skill 版本放在其基线对应物之前。

3. **进行分析师审查** — 读取基准数据并揭示聚合统计可能隐藏的模式。参见 `agents/analyzer.md`（"分析基准结果"部分）了解要查找的内容 — 像是无论技能如何都总是通过的断言（非区分性）、高方差评估（可能不稳定）和时间/token 权衡。

4. **启动查看器**，包含定性输出和定量数据：
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   对于迭代 2+，也传递 `--previous-workspace <workspace>/iteration-<N-1>`。

   **Cowork / 无头环境：**如果 `webbrowser.open()` 不可用或环境没有显示，使用 `--static <output_path>` 写入独立 HTML 文件而不是启动服务器。当用户点击"Submit All Reviews"时，反馈将作为 `feedback.json` 文件下载。下载后，将 `feedback.json` 复制到工作区目录供下一次迭代使用。

注意：请使用 generate_review.py 创建查看器；无需编写自定义 HTML。

5. **告诉用户**类似："我已经在浏览器中打开了结果。有两个标签 — 'Outputs' 让您点击每个测试用例并留下反馈，'Benchmark' 显示定量比较。完成后，回到这里告诉我。"

### 用户在查看器中看到什么

"Outputs" 标签一次显示一个测试用例：
- **Prompt**：给定的任务
- **Output**：技能产生的文件，尽可能内联渲染
- **Previous Output**（迭代 2+）：折叠部分显示上次迭代的输出
- **Formal Grades**（如果运行了评分）：折叠部分显示断言通过/失败
- **Feedback**：用户输入时自动保存的文本框
- **Previous Feedback**（迭代 2+）：他们上次的评论，显示在文本框下方

"Benchmark" 标签显示统计摘要：每种配置的通过率、时间和 token 使用，以及每个评估的细分和分析师观察。

导航通过上一个/下一个按钮或箭头键。完成后，他们点击"Submit All Reviews"将所有反馈保存到 `feedback.json`。

### 步骤 5：读取反馈

当用户告诉您他们完成时，读取 `feedback.json`：

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

空反馈意味着用户认为它没问题。将改进重点放在用户有具体投诉的测试用例上。

完成后关闭查看器服务器：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改进技能

这是循环的核心。您已经运行了测试用例，用户已经审查了结果，现在您需要根据他们的反馈使技能变得更好。

### 如何思考改进

1. **从反馈中泛化。**这里正在发生的宏观事情是，我们试图创建可以在许多不同提示中使用一百万次（也许字面上，也许甚至更多谁知道）的技能。在这里，您和用户只在少数示例上反复迭代，因为它有助于更快地推进。用户深入了解这些示例，他们可以快速评估新输出。但是，如果您和用户共同开发的技能仅适用于那些示例，它是无用的。与其投入繁琐的过度拟合更改，或压抑性的限制性 MUST，如果有某些顽固的问题，您可以尝试扩展并使用不同的隐喻，或推荐不同的工作模式。尝试成本相对较低，也许您会发现很棒的东西。

2. **保持提示精简。**移除不起作用的东西。确保阅读转录，而不仅仅是最终输出 — 如果看起来技能正在使模型浪费大量时间做无生产力的事情，您可以尝试摆脱使它这样做的技能部分，看看会发生什么。

3. **解释原因。**努力解释您要求模型做的一切背后的**原因**。今天的 LLM 很*聪明*。它们有良好的心理理论，当给定良好的工具时，可以超越死记硬背的指令并真正实现目标。即使用户的反馈简短或沮丧，也要尝试真正理解任务以及用户为什么写他们写的东西，以及他们实际写了什么，然后将这种理解传递到指令中。如果您发现自己在写全大写的 ALWAYS 或 NEVER，或使用超僵化的结构，那是黄色警告 — 如果可能，重新表述并解释推理，以便模型理解为什么您要求的东西很重要。这是一种更人道、更强大、更有效的方法。

4. **寻找跨测试用例的重复工作。**阅读测试运行的转录，注意子代理是否都独立编写了类似的辅助脚本或对某事采用了相同的多步骤方法。如果所有 3 个测试用例都导致子代理编写 `create_docx.py` 或 `build_chart.py`，这是一个强烈的信号，表明技能应该捆绑该脚本。编写一次，放在 `scripts/` 中，并告诉技能使用它。这节省了每次未来调用重新发明轮子。

这个任务非常重要（我们正试图在这里创造每年数十亿美元的经济价值！），您的思考时间不是瓶颈；花时间真正深思熟虑。我建议编写修订草稿，然后用新鲜的眼光审视并做出改进。真正尽最大努力进入用户的头脑，理解他们想要和需要什么。

### 迭代循环

改进技能后：

1. 将您的改进应用到技能
2. 将所有测试用例重新运行到新的 `iteration-<N+1>/` 目录，包括基线运行。如果您正在创建新技能，基线始终是 `without_skill`（无技能） — 这在迭代间保持不变。如果您正在改进现有技能，请使用您的判断什么作为基线有意义：用户带来的原始版本，还是上一次迭代。
3. 使用 `--previous-workspace` 指向上一次迭代启动审查器
4. 等待用户审查并告诉您他们完成
5. 读取新反馈，再次改进，重复

继续直到：
- 用户说他们满意
- 反馈全部为空（一切看起来都好）
- 您没有取得有意义的进展

---

## 高级：盲比较

对于您想要更严格地比较两个版本技能的情况（例如，用户问"新版本真的更好吗？"），有一个盲比较系统。读取 `agents/comparator.md` 和 `agents/analyzer.md` 了解详情。基本思想是：将两个输出给独立代理，不告诉它是哪个，让它判断质量。然后分析为什么获胜者获胜。

这是可选的，需要子代理，大多数用户不需要它。人工审查循环通常足够。

---

## 描述优化

SKILL.md 前置数据中的 description 字段是决定 Claude 是否调用技能的主要机制。创建或改进技能后，提供优化描述以获得更好的触发准确性。

### 步骤 1：生成触发评估查询

创建 20 个评估查询 — 应触发和不应触发的混合。保存为 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

查询必须是真实的，是 Claude Code 或 Claude.ai 用户实际会输入的。不是抽象请求，而是具体和详细的好请求。例如，文件路径、用户工作或情况的个人上下文、列名和值、公司名称、URL。一些背景故事。有些可能是小写或包含缩写或错别字或随意的语音。使用不同长度的混合，专注于边缘情况而不是让它们清晰（用户将有机会签字确认）。

差：`"Format this data"`、`"Extract text from PDF"`、`"Create a chart"`

好：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

对于**应触发**查询（8-10），考虑覆盖范围。您需要相同意图的不同措辞 — 一些正式，一些随意。包括用户没有明确命名技能或文件类型但显然需要它的情况。加入一些不常见用例以及此技能与另一个竞争但应该获胜的情况。

对于**不应触发**查询（8-10），最有价值的是接近错过 — 与技能共享关键词或概念但实际上需要不同东西的查询。考虑相邻领域、模糊措辞（朴素关键词匹配会触发但不应该），以及查询涉及技能所做但在其他工具更合适的上下文中的情况。

要避免的关键事情：不要使不应触发查询明显不相关。"Write a fibonacci function"作为 PDF 技能的负面测试太容易 — 它不测试任何东西。负面情况应该真正棘手。

### 步骤 2：与用户审查

使用 HTML 模板向用户呈现评估集供审查：

1. 从 `assets/eval_review.html` 读取模板
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → 评估项的 JSON 数组（不要用引号括起来 — 它是 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → 技能的名称
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → 技能的当前描述
3. 写入临时文件（例如 `/tmp/eval_review_<skill-name>.html`）并打开它：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以编辑查询、切换应触发、添加/删除条目，然后点击"Export Eval Set"
5. 文件下载到 `~/Downloads/eval_set.json` — 检查 Downloads 文件夹中最新的版本，以防有多个（例如 `eval_set (1).json`）

这一步很重要 — 差的评估查询导致差的描述。

### 步骤 3：运行优化循环

告诉用户："这需要一些时间 — 我将在后台运行优化循环并定期检查。"

将评估集保存到工作区，然后在后台运行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用系统提示中的模型 ID（驱动当前会话的那个），以便触发测试与用户实际体验匹配。

运行时，定期尾部输出以向用户提供它在哪个迭代以及分数看起来如何的更新。

这自动处理完整的优化循环。它将评估集分为 60% 训练和 40% 保留测试，评估当前描述（运行每个查询 3 次以获得可靠的触发率），然后调用 Claude 根据失败的内容提出改进。它在训练和测试上重新评估每个新描述，最多迭代 5 次。完成后，它在浏览器中打开 HTML 报告，显示每个迭代的结果，并返回包含 `best_description` 的 JSON — 通过测试分数而不是训练分数选择，以避免过度拟合。

### 技能触发如何工作

理解触发机制有助于设计更好的评估查询。技能出现在 Claude 的 `available_skills` 列表中，带有名称 + 描述，Claude 根据该描述决定是否咨询技能。重要的是要知道 Claude 只为它无法轻松自行处理的任务咨询技能 — 简单的单步查询如"read this PDF"可能不会触发技能，即使描述完美匹配，因为 Claude 可以用基本工具直接处理它们。复杂、多步骤或专业查询在描述匹配时可靠地触发技能。

这意味着您的评估查询应该足够实质性，使 Claude 实际上会从咨询技能中受益。像"read file X"这样的简单查询是差的测试用例 — 无论描述质量如何，它们都不会触发技能。

### 步骤 4：应用结果

从 JSON 输出中获取 `best_description` 并更新技能的 SKILL.md 前置数据。向用户展示前后对比并报告分数。

---

### 打包和呈现（仅当 `present_files` 工具可用时）

检查您是否有权访问 `present_files` 工具。如果没有，跳过此步骤。如果有，打包技能并向用户呈现 .skill 文件：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包后，指导用户到生成的 `.skill` 文件路径，以便他们可以安装。

---

## Claude.ai 特定指令

在 Claude.ai 中，核心工作流相同（草稿 → 测试 → 审查 → 改进 → 重复），但因为 Claude.ai 没有子代理，一些机制发生变化。以下是需要调整的：

**运行测试用例**：没有子代理意味着没有并行执行。对于每个测试用例，读取技能的 SKILL.md，然后按照其指令自己完成测试提示。一次做一个。这不如独立子代理严格（您编写了技能，也在运行它，所以您有完整上下文），但它是有用的健全检查 — 人工审查步骤补偿。跳过基线运行 — 只需使用技能按要求完成任务。

**审查结果**：如果无法打开浏览器（例如 Claude.ai 的 VM 没有显示，或您在远程服务器上），完全跳过浏览器审查器。相反，直接在对话中呈现结果。对于每个测试用例，显示提示和输出。如果输出是用户需要查看的文件（如 .docx 或 .xlsx），将其保存到文件系统并告诉他们位置，以便他们可以下载和检查。内联请求反馈："这看起来怎么样？有什么要改的吗？"

**基准测试**：跳过定量基准 — 它依赖于基线比较，没有子代理没有意义。专注于用户的定性反馈。

**迭代循环**：与之前相同 — 改进技能，重新运行测试用例，请求反馈 — 只是没有中间的浏览器审查器。如果文件系统可用，您仍然可以将结果组织到迭代目录中。

**描述优化**：此部分需要 `claude` CLI 工具（特别是 `claude -p`），仅在 Claude Code 中可用。如果您在 Claude.ai 上，跳过它。

**盲比较**：需要子代理。跳过它。

**打包**：`package_skill.py` 脚本在任何有 Python 和文件系统的地方都能工作。在 Claude.ai 上，您可以运行它，用户可以下载生成的 `.skill` 文件。

**更新现有技能**：用户可能要求您更新现有技能，而不是创建新的。在这种情况下：
- **保留原始名称。**注意技能的目录名称和 `name` 前置数据字段 — 不变使用它们。例如，如果安装的技能是 `research-helper`，输出 `research-helper.skill`（不是 `research-helper-v2`）。
- **复制到可写位置再编辑。**安装的技能路径可能只读。复制到 `/tmp/skill-name/`，在那里编辑，从副本打包。
- **如果手动打包，先在 `/tmp/` 中暂存**，然后复制到输出目录 — 直接写入可能因权限失败。

---

## Cowork 特定指令

如果您在 Cowork 中，主要需要知道的是：

- 您有子代理，所以主要工作流（并行生成测试用例，运行基线，评分等）都有效。（但是，如果遇到严重的超时问题，可以串行运行测试提示而不是并行。）
- 您没有浏览器或显示，所以在生成评估查看器时，使用 `--static <output_path>` 写入独立 HTML 文件而不是启动服务器。然后提供一个链接，用户可以点击在浏览器中打开 HTML。
- 无论出于什么原因，Cowork 设置似乎使 Claude 在运行测试后不愿生成评估查看器，所以重申一下：无论您在 Cowork 还是 Claude Code 中，运行测试后，您应该始终使用 `generate_review.py`（不是编写自己的精品 html 代码）生成评估查看器供人类查看示例，然后自己修改技能并尝试更正。提前抱歉但我要大写：在自己评估输入之前生成评估查看器！您想尽快将它们呈现在人类面前！
- 反馈工作方式不同：由于没有运行服务器，查看器的"Submit All Reviews"按钮将下载 `feedback.json` 文件。然后您可以从那里读取（您可能需要先请求访问）。
- 打包有效 — `package_skill.py` 只需要 Python 和文件系统。
- 描述优化（`run_loop.py` / `run_eval.py`）应该在 Cowork 中正常工作，因为它通过子进程使用 `claude -p`，而不是浏览器，但请在完全完成技能制作且用户同意它状态良好后再使用。
- **更新现有技能**：用户可能要求您更新现有技能，而不是创建新的。遵循上面 claude.ai 部分的更新指导。

---

## 参考文件

agents/ 目录包含专门子代理的指令。在您需要生成相关子代理时读取它们。

- `agents/grader.md` — 如何根据输出评估断言
- `agents/comparator.md` — 如何在两个输出之间进行盲 A/B 比较
- `agents/analyzer.md` — 如何分析为什么一个版本击败另一个

references/ 目录有额外文档：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构

---

再次强调核心循环：

- 弄清楚技能是关于什么的
- 草拟或编辑技能
- 在测试提示上运行具有技能访问权限的 claude
- 与用户一起评估输出：
  - 创建 benchmark.json 并运行 `eval-viewer/generate_review.py` 帮助用户审查
  - 运行定量评估
- 重复直到您和用户满意
- 打包最终技能并返回给用户。

请将步骤添加到您的 TodoList（如果您有这样的东西），以确保不会忘记。如果您在 Cowork 中，请特别将"创建评估 JSON 并运行 `eval-viewer/generate_review.py` 以便人类可以审查测试用例"放入 TodoList 以确保它发生。

祝您好运！
