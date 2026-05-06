# 陷阱——常见失败点

> 本节适用于阶段 3（模块 HTML 编写）和阶段 4（审阅）。在宣布课程完成之前，必须检查以下每个项目。

这些代表课程构建过程中出现的真实问题。在课程被认为完成之前，必须验证所有这些问题。

### 工具提示被裁剪

翻译块依赖 `overflow: hidden` 来换行。使用 `position: absolute` 的工具提示在术语元素内会被容器裁剪。**修复：** 工具提示应使用 `position: fixed` 并附加到 `document.body`，通过 `getBoundingClientRect()` 计算位置。`main.js` 已经处理了这一点，然而它仍然是每个构建中最常见的 bug。

### 工具提示不足

工具提示不足是最普遍的失败。没有技术背景的学习者不会认识诸如 REPL、JSON、flag、入口点、PATH、pip、namespace、function、class、module、PR、E2E 等术语，也不会认识 Blender/GIMP 等软件名称。**指导原则：** 如果一个术语在非技术朋友的日常对话中不会出现，就添加工具提示。过度提示而不是提示不足。但是，避免对学习者已经理解的领域特定术语添加工具提示（例如，对从事 AI 的人来说的 AI/ML 术语）。

### 大段文字

课程最终看起来像教科书而不是信息图——通常是由于编写超过两三句连续句子而没有视觉休息造成的。每个屏幕应该至少一半是视觉内容。3 项以上的列表应变成卡片，序列应变成步骤卡片或流程图，代码解释应使用代码↔英文对照块。

### 重复使用的隐喻

重复使用单个隐喻（如"餐厅"或"厨房"）。每个模块都需要自己的隐喻，有机地适合那个特定概念。如果同一个隐喻出现两次，停下来找一个自然合适的隐喻。

### 代码修改

从实际代码库中修剪、简化或"清理"片段。学习者应该能够打开真实文件并找到相同的代码。不要为了简洁而编辑，而是*选择*代码库中自然简洁的片段（5-10 行）来演示概念。

### 测试记忆的测验问题

诸如"API 代表什么？"或"哪个文件处理 X？"的问题测试的是回忆而不是理解。每个测验问题都应该呈现一个新的场景，并要求学习者*应用*他们所学到的。

### 滚动吸附 Mandatory

设置 `scroll-snap-type: y mandatory` 会将用户困在冗长的模块内。使用 `proximity` 代替。

### 模块质量下降

在单次中编写所有模块会导致后面的模块薄弱且发育不良。一次构建并验证一个模块。对于复杂的代码库，利用带模块简报的并行路径。

### 缺少互动元素

模块只包含文本和代码块，没有互动性。每个模块必须至少包含：测验、数据流动画、群聊、架构图或拖放。这些不是装饰性的——它们是非技术学习者处理和保留信息的主要方式。

### HTML 元素不匹配 JS 引擎约定 — 关键

最常见和最严重的失败模式：HTML 使用的类名、data 属性或按钮结构与 `main.js` 期望的不同。JS 引擎通过扫描特定的 CSS 类选择器和 `data-*` 属性来初始化——如果不匹配，什么都不会发生。没有控制台错误帮助诊断。

**这通常发生在代理凭记忆编写 HTML 而不是从 `references/interactive-elements.md` 复制精确模式时。** 该文件中的 HTML 模式是内容和引擎之间的契约。每个偏差都会破坏某些东西。

**强制性验证清单（检查每个互动元素）：**

| 组件 | 必须有的选择器/属性 | 常见错误 |
|---|---|---|
| **测验** | `.quiz-question-block` 带 `data-correct`、`data-explanation-right`、`data-explanation-wrong`；`.quiz-option` 带 `data-value` 和 `onclick="selectOption(this)"`；`.quiz-feedback` | 使用 `data-answer` 而非 `data-value`；缺少 `onclick`；问题块上缺少 `data-correct` |
| **聊天** | `.chat-window` 带 `id`；`.chat-message` 带 `data-sender` 和 `style="display:none"`；`.chat-typing` 带 `style="display:none"`；`.chat-next-btn`、`.chat-all-btn`、`.chat-reset-btn`；`.chat-progress` | 消息默认可见（没有 `display:none`）；缺少 `data-sender`（角色映射失败）；在控制按钮上用 `id` 而非 class；缺少 `.chat-typing` 元素 |
| **流动画** | `.flow-animation` 带 `data-steps='[...]'`；`.flow-actor` 带 `id="flow-xxx"`；`.flow-next-btn`、`.flow-reset-btn`；`.flow-progress`；`.flow-packet`；`.flow-step-label` | 缺少 `data-steps`（引擎无步骤可运行）；用自定义按钮 `id` 而非 class `.flow-next-btn`；缺少 `.flow-packet` 元素（数据包动画静默失败）；角色 `id` 与 `data-steps` 值不匹配 |
| **Bug 挑战** | `.bug-challenge` 容器；`.bug-line` 带 `onclick="checkBugLine(this, true/false)"`；`.bug-feedback` | 使用 `<pre>` 代码块而非独立的 `.bug-line` 元素；缺少 `checkBugLine` onclick 处理器 |
| **拖放** | `.dnd-container`；`.dnd-chip` 带 `data-answer` 和 `draggable="true"`；`.dnd-zone` 带 `data-correct`；`.dnd-zone-target` | 芯片上缺少 `draggable="true"`；区域的 `data-correct` 与芯片的 `data-answer` 不匹配 |
| **图层切换** | `.layer-demo` 容器；`.layer` 带 `id`；`.layer-tab` 带 `onclick="showLayer('id', this)"` | 缺少 `.layer-demo` 包装器；`showLayer` 调用了错误的 ID |

**黄金法则：** 从 `references/interactive-elements.md` 逐字符复制 HTML 模式，然后只替换内容文本。不要发明替代的类名、data 属性或按钮结构。JS 引擎的选择器是精确字符串——即使是 `quiz-option` 和 `quiz_option` 之间的差异也会破坏功能。

### 聊天消息初始未隐藏

所有 `.chat-message` 元素必须有 `style="display:none"`。如果任何消息在页面加载时可见，聊天将显示为预揭示状态，逐步动画效果将丢失。JS 引擎的 `showNext()` 在下一条消息上设置 `display: flex`，因此预先可见的消息会破坏序列。

### 流动画数据包 ID 冲突

当页面包含多个流动画时，每个 `.flow-packet` 元素创建动画关键帧。如果多个流动画共享同一页面，确保每个 `.flow-animation` 有唯一的上下文——JS 引擎在容器内通过 `.flow-packet` 限定数据包查找范围，但其他元素（角色、标签）上的 `id` 冲突可能导致不可预测的行为。

### 测验反馈文本累积

当使用自定义测验实现（不是标准引擎）时，确保 `resetQuiz()` 恢复原始反馈文本内容。在不保存/恢复原始文本的情况下前置"正确！"或"错误。"会导致每次重置+重新回答循环中反馈文本累积前缀。通过 `data-original-text` 或闭包变量存储原始文本。
