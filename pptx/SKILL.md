---
name: pptx
description: "只要涉及 .pptx 文件的任何场景都使用此技能 — 作为输入、输出或两者兼有。包括：创建幻灯片、路演或演示文稿；读取、解析或从任何 .pptx 文件提取文本（即使提取的内容将在其他地方使用，如电子邮件或摘要）；编辑、修改或更新现有演示文稿；合并或拆分幻灯片文件；使用模板、布局、演讲者备注或评论。当用户提到「deck」、「slides」、「presentation」或引用 .pptx 文件名时触发，无论他们计划如何处理内容。如果需要打开、创建或操作 .pptx 文件，请使用此技能。"
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX 技能

## 快速参考

| 任务 | 指南 |
|------|-------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 从模板编辑或创建 | 阅读 [editing.md](editing.md) |
| 从头创建 | 阅读 [pptxgenjs.md](pptxgenjs.md) |

---

## 读取内容

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 编辑工作流

**阅读 [editing.md](editing.md) 了解完整详情。**

1. 使用 `thumbnail.py` 分析模板
2. 解包 -> 操作幻灯片 -> 编辑内容 -> 清理 -> 打包

---

## 从头创建

**阅读 [pptxgenjs.md](pptxgenjs.md) 了解完整详情。**

当没有模板或参考演示文稿时使用。

---

## 设计理念

**不要创建无聊的幻灯片。** 白色背景上的普通项目符号不会给任何人留下深刻印象。为每张幻灯片考虑此列表中的想法。

### 开始之前

- **选择大胆、内容相关的配色方案**：配色方案应让人感觉是为这个主题设计的。如果你将颜色换到一个完全不同的演示文稿中仍然「有效」，说明你的选择还不够具体。
- **主导性优于平等性**：一种颜色应占主导地位（60-70% 视觉权重），配合 1-2 种辅助色调和一个鲜明的强调色。永远不要给所有颜色相等的权重。
- **深/浅对比**：标题和结论幻灯片使用深色背景，内容使用浅色（「三明治」结构）。或者全程使用深色以获得高端感。
- **坚持视觉主题**：选择一个独特的元素并重复它 — 圆形图片框架、彩色圆圈中的图标、粗单侧边框。在每张幻灯片中贯穿。

### 配色方案

选择与主题匹配的颜色 — 不要默认使用通用蓝色。使用这些配色方案作为灵感：

| 主题 | 主色 | 辅助色 | 强调色 |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### 每张幻灯片

**每张幻灯片都需要视觉元素** — 图片、图表、图标或形状。纯文本幻灯片容易被遗忘。

**布局选项：**
- 双栏（左侧文本，右侧插图）
- 图标 + 文本行（彩色圆圈中的图标，粗体标题，下方描述）
- 2x2 或 2x3 网格（一侧图片，另一侧内容块网格）
- 半出血图片（完整左侧或右侧）带内容叠加

**数据展示：**
- 大数字标注（60-72pt 大数字配下方小标签）
- 对比列（前后、优缺点、并排选项）
- 时间线或流程图（编号步骤、箭头）

**视觉润色：**
- 章节标题旁的小彩色圆圈中的图标
- 关键统计数据或标语使用斜体强调文本

### 排版

**选择有趣的字体配对** — 不要默认使用 Arial。选择有个性的标题字体并搭配干净的正文字体。

| 标题字体 | 正文字体 |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| 元素 | 大小 |
|---------|------|
| 幻灯片标题 | 36-44pt 粗体 |
| 章节标题 | 20-24pt 粗体 |
| 正文 | 14-16pt |
| 说明文字 | 10-12pt 柔和色 |

### 间距

- 最小边距 0.5 英寸
- 内容块之间 0.3-0.5 英寸
- 留出呼吸空间 — 不要填满每一寸

### 避免（常见错误）

- **不要重复相同的布局** — 在幻灯片之间变化列、卡片和标注
- **不要居中正文** — 段落和列表左对齐；仅标题居中
- **不要吝啬大小对比** — 标题需要 36pt+ 才能从 14-16pt 正文中脱颖而出
- **不要默认蓝色** — 选择反映特定主题的颜色
- **不要随机混合间距** — 选择 0.3 英寸或 0.5 英寸的间隔并一致使用
- **不要样式化一张幻灯片而其余保持普通** — 要么全程投入要么全程保持简单
- **不要创建纯文本幻灯片** — 添加图片、图标、图表或视觉元素；避免普通的标题 + 项目符号
- **不要忘记文本框内边距** — 当将线条或形状与文本边缘对齐时，在文本框上设置 `margin: 0` 或偏移形状以考虑内边距
- **不要使用低对比度元素** — 图标和文本都需要与背景有强对比度；避免浅色背景上的浅色文本或深色背景上的深色文本
- **永远不要在标题下使用强调线** — 这是 AI 生成幻灯片的标志；改用空白或背景色

---

## QA（必需）

**假设有问题。你的工作是找到它们。**

你的第一次渲染几乎从来都不正确。将 QA 作为错误搜索，而不是确认步骤。如果在第一次检查中发现零问题，说明你不够仔细。

### 内容 QA

```bash
python -m markitdown output.pptx
```

检查缺失内容、拼写错误、错误顺序。

**使用模板时，检查残留的占位符文本：**

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|this.*(page|slide).*layout"
```

如果 grep 返回结果，在宣布成功之前修复它们。

### 视觉 QA

**使用子代理** — 即使只有 2-3 张幻灯片。你一直在盯着代码看，会看到你期望的，而不是实际存在的。子代理有新鲜的眼光。

将幻灯片转换为图片（参见[转换为图片](#转换为图片)），然后使用此提示：

```
Visually inspect these slides. Assume there are issues — find them.

Look for:
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Decorative lines positioned for single-line text but title wrapped to two lines
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. /path/to/slide-01.jpg (Expected: [brief description])
2. /path/to/slide-02.jpg (Expected: [brief description])

Report ALL issues found, including minor ones.
```

### 验证循环

1. 生成幻灯片 -> 转换为图片 -> 检查
2. **列出发现的问题**（如果没有发现，以更批判的眼光再看一遍）
3. 修复问题
4. **重新验证受影响的幻灯片** — 一个修复通常会产生另一个问题
5. 重复直到完整检查没有发现新问题

**在完成至少一次修复-验证循环之前，不要宣布成功。**

---

## 转换为图片

将演示文稿转换为单独的幻灯片图片以进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

这会创建 `slide-01.jpg`、`slide-02.jpg` 等。

要在修复后重新渲染特定幻灯片：

```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## 依赖

- `pip install "markitdown[pptx]"` - 文本提取
- `pip install Pillow` - 缩略图网格
- `npm install -g pptxgenjs` - 从头创建
- LibreOffice (`soffice`) - PDF 转换（通过 `scripts/office/soffice.py` 为沙盒环境自动配置）
- Poppler (`pdftoppm`) - PDF 转图片
