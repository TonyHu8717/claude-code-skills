---
name: aaos-reader
description: |
  阅读 AAOS (Android Automotive OS) 本地代码目录，生成交互式 HTML 教程并保存到 aaos 目录下。适用于用户给出一个本地绝对路径（如 Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger），要求阅读代码、生成教程/课程/学习资料的场景。触发词：aaos reader, aaos 教程, aaos 代码阅读, 阅读这个模块, 分析这个代码, 生成教程, 代码教程。当用户提供一个包含 aaos 的绝对路径并要求生成教程时自动触发。
---

# AAOS Code Reader

将 AAOS 代码目录转化为精美的交互式 HTML 教程，帮助开发者深入理解模块的架构和实现。所有界面文字为中文，代码保留英文原文。

## 输入输出规范

### 输入
用户给出一个本地绝对路径，指向 AAOS 源码中的某个模块目录，例如：
- `Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger`
- `Y:\GuaMaster\aaos\frameworks\base\services\core\java\com\android\server\wm`

### 输出路径映射
将源路径中的 AAOS 根目录前缀替换为 `D:\claude\aaos\`，后续路径保持不变：

| 源路径 | 输出路径 |
|--------|----------|
| `Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger` | `D:\claude\aaos\frameworks\native\services\surfaceflinger` |
| `Y:\GuaMaster\aaos\frameworks\base\services\core\...` | `D:\claude\aaos\frameworks\base\services\core\...` |

提取模块名（路径最后一级目录名）用于课程标题，如 `surfaceflinger` → "SurfaceFlinger 深度解析"。

### 输出目录结构
```
D:\claude\aaos\{镜像路径}\styles.css
D:\claude\aaos\{镜像路径}\main.js
D:\claude\aaos\{镜像路径}\_base.html
D:\claude\aaos\{镜像路径}\_footer.html
D:\claude\aaos\{镜像路径}\build.sh
D:\claude\aaos\{镜像路径}\modules\
  01-overview.html
  02-xxx.html
  ...
D:\claude\aaos\{镜像路径}\index.html    ← build.sh 组装生成
```

## 工作流程

### 阶段 1：解析与准备

1. **解析输入路径** — 从用户输入中提取：
   - 源码绝对路径（`src_path`）
   - AAOS 根目录前缀（通常是 `Y:\GuaMaster\aaos\` 或类似路径）
   - 模块相对路径（去掉根目录前缀后的部分）
   - 模块名（路径最后一级）

2. **映射输出路径** — 拼接 `D:\claude\aaos\` + 模块相对路径 = `output_path`

3. **检查已有内容** — 如果 `output_path` 已存在：
   - 读取 `modules/` 下所有现有模块文件，了解已有内容
   - 读取 `_base.html` 获取现有课程标题和配色
   - 在已有内容基础上增量更新，不丢失已有的好内容
   - 如果 `output_path` 不存在，创建完整目录结构

4. **初始化课程目录** — 从 `references/` 复制以下文件到 `output_path/`（已存在则跳过）：
   - `styles.css` — 原样复制
   - `main.js` — 原样复制
   - `_footer.html` — 原样复制
   - `build.sh` — 原样复制

### 阶段 2：代码深度分析

使用 Agent 并行分析代码目录。根据模块复杂度，启动 2-3 个 Agent 分工分析：

**分析维度：**
- **架构全景** — 模块的整体职责、在 AAOS 系统中的位置、与其他模块的关系
- **核心组件** — 主要类/结构体/接口、它们的职责和协作关系
- **数据流与调用链** — 关键请求/事件从入口到出口的完整路径
- **设计模式** — 使用的架构模式（Binder IPC、HIDL/AIDL、生产者-消费者、观察者等）
- **关键代码片段** — 5-10 行的精炼代码段，展示核心逻辑，包含文件路径和行号

**AAOS 领域知识重点：**
- Native 层：Binder IPC、SurfaceFlinger 合成流程、BufferQueue、HWC HAL、libbinder
- Framework 层：SystemServer、WMS/AMS/InputManager、AIDL 接口、Handler/Looper 消息机制
- HAL 层：HIDL/AIDL HAL、HwBinder、passthrough/binderized 模式
- 通用：进程间通信、共享内存（ashmem/ion/dmabuf）、SELinux 策略、init.rc 服务配置

**输出：** 将分析结果保存为 `output_path/analysis.md`，供后续模块编写参考。

### 阶段 3：课程设计

根据代码分析结果，设计 4-6 个模块的教学大纲。

**课程弧线（从用户可见行为到底层实现）：**

| 模块位置 | 内容方向 | 示例（以 SurfaceFlinger 为例） |
|----------|----------|-------------------------------|
| 1 | 模块全景 — 这个模块做什么，在系统中扮演什么角色 | "你看到的每一帧画面，背后都是 SurfaceFlinger 在工作" |
| 2 | 核心组件 — 主要的类和它们的职责 | SurfaceFlinger、Layer、BufferQueue、HWComposer |
| 3 | 关键流程 — 一个核心操作的完整数据流 | "从 App 提交一帧到屏幕显示的完整旅程" |
| 4 | 通信机制 — 模块如何与其他组件交互 | Binder IPC、VSync 信号、事务处理 |
| 5 | 设计精妙 — 巧妙的工程设计和优化策略 | 双缓冲/三缓冲、FrameTimeline、HWC 合成策略 |
| 6 | 调试与排错 — 常见问题和调试方法 | dumpsys、perfetto trace、常见卡顿原因 |

这是一个菜单而非清单。根据模块复杂度选择 4-6 个最合适的模块。

**每个模块应包含：**
- 3-6 个屏幕（模块内的子章节）
- 至少一个代码↔中文翻译块
- 至少一个交互元素（测验、动画或可视化）
- 1-2 个 callout 框，分享 AAOS 领域洞察
- 一个贴切的比喻来帮助理解（不要重复使用同一个比喻）

**必须包含的交互元素（整个课程）：**
- **群聊动画** — 组件间的 iMessage 风格对话（至少 1 个）
- **数据流动画** — 步骤化的数据包动画（至少 1 个）
- **代码↔中文翻译块** — 每个模块至少 1 个
- **测验题** — 每个模块至少 1 道（场景题 > 追踪题 > 概念题）
- **术语工具提示** — 每个模块中首次出现的技术术语

**不要向用户展示课程大纲征求意见 — 直接构建。** 如果用户想修改，看完结果后会告知。

### 阶段 4：构建教程

#### 步骤 1：定制 `_base.html`

从 `references/_base.html` 读取模板，写入 `output_path/_base.html`，替换三处：
- `lang="en"` → `lang="zh-CN"`
- `COURSE_TITLE` → 实际课程标题（两处，nav 和 title）
- `ACCENT_COLOR` / `ACCENT_HOVER` / `ACCENT_LIGHT` / `ACCENT_MUTED` → 选择一个配色方案（推荐 teal `#2A7B9B` 系列适合系统级模块，vermillion `#D94F30` 系列适合核心服务模块）
- `NAV_DOTS` → 每个模块一个 `<button class="nav-dot" ...>`

#### 步骤 2：编写模块 HTML

读取以下参考文件：
- `references/content-philosophy.md` — 内容写作规则
- `references/interactive-elements.md` — 交互元素 HTML 模式
- `references/design-system.md` — 视觉规范
- `references/gotchas.md` — 常见问题清单

对于每个模块，写入 `output_path/modules/0N-slug.html`，仅包含 `<section class="module" id="module-N">` 块及其内容。不要包含 `<html>`、`<head>`、`<body>`、`<style>` 或 `<script>` 标签。

**对于复杂模块（代码量大、逻辑复杂），使用并行路径：**
1. 为每个模块编写简报（brief），保存到 `output_path/briefs/0N-slug.md`
2. 启动 Agent 并行编写各模块，每个 Agent 接收：模块简报 + 相关参考文件
3. 主上下文做最终一致性检查

**对于简单模块（代码量小），直接在主上下文顺序编写。**

**代码翻译规则：**
- 代码保留英文原文，不做任何修改或简化
- 翻译块的中文解释面向 AAOS 开发者，不需要解释基础概念（如什么是 Binder、什么是 HAL）
- 重点解释这段代码在模块中的作用和设计意图
- 使用 `span class="code-keyword"` 等 CSS 类为代码添加语法高亮

**中文内容规则：**
- 所有 UI 文字、解释、测验题目和反馈均为中文
- 技术术语首次出现时添加术语工具提示，使用中文定义
- 代码中的注释如果是英文，保留原文，翻译块中用中文解释
- 比喻应贴近中国开发者的日常经验

#### 步骤 3：组装

```bash
cd output_path && bash build.sh
```

生成 `index.html`。在浏览器中打开。

### 阶段 5：检查与报告

组装完成后，检查以下项目：
- [ ] 导航点数量与模块数量一致
- [ ] 模块间过渡自然连贯
- [ ] 每个模块至少有 1 个交互元素
- [ ] 术语工具提示覆盖所有首次出现的技术术语
- [ ] 代码片段与实际源码一致（未被修改或简化）
- [ ] 测验题目是场景应用题而非记忆题
- [ ] 没有水平滚动条
- [ ] 群聊动画和数据流动画可正常运行

向用户报告：
- 课程概览（模块数量和主题）
- `index.html` 的路径
- 请求反馈

## 增量更新

当输出目录已存在时：

1. 读取现有 `modules/` 下的所有文件
2. 分析现有内容覆盖了哪些知识点
3. 对比代码分析结果，识别缺失或过时的内容
4. 保留现有内容中质量好的部分
5. 新增缺失的模块或屏幕
6. 更新过时的代码片段（如果源码有变化）
7. 重新运行 `build.sh` 组装

**原则：增量改进，不推倒重来。**

## 设计风格

整体风格应像一本精美的开发者笔记 — 温暖、舒适、有辨识度。

- **温暖色调**：米白色背景（如旧纸张），暖灰色调，不用冷白或冷蓝
- **大胆的强调色**：选择一个自信的强调色（teal 适合系统级模块，vermillion 适合核心服务）
- **独特字体**：Bricolage Grotesque（标题）、DM Sans（正文）、JetBrains Mono（代码）
- **充裕留白**：每个屏幕最多 2-3 段短文字
- **交替背景**：奇偶模块交替使用两种暖色背景
- **深色代码块**：IDE 风格，Catppuccin 语法高亮

## 参考文件

`references/` 目录包含详细规范。**只在到达相关阶段时才读取** — 不要提前加载。

- `references/content-philosophy.md` — 内容写作规则，在编写模块时读取
- `references/gotchas.md` — 常见问题清单，在编写和检查时读取
- `references/design-system.md` — CSS 设计系统，编写模块 HTML 时读取
- `references/interactive-elements.md` — 交互元素 HTML 模式，编写模块时读取
- `references/styles.css` — 预构建样式表，直接复制使用
- `references/main.js` — 预构建 JavaScript，直接复制使用
- `references/_base.html` — HTML 外壳模板，定制后使用
- `references/_footer.html` — 页脚模板，直接复制使用
- `references/build.sh` — 组装脚本，直接复制使用
