---
name: aaos-reader
description: |
  阅读 AAOS (Android Automotive OS) 本地代码目录，生成交互式 HTML 教程并保存到 aaos 目录下。适用于用户给出一个本地绝对路径（如 Y:\GuaMaster\aaos\frameworks\native\services\surfaceflinger），要求阅读代码、生成教程/课程/学习资料的场景。触发词：aaos reader, aaos 教程, aaos 代码阅读, 阅读这个模块, 分析这个代码, 生成教程, 代码教程。当用户提供一个包含 aaos 的绝对路径并要求生成教程时自动触发。支持多级子模块、Java 包识别、Android.bp 依赖分析。
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
D:\claude\aaos\{镜像路径}\
  styles.css
  main.js
  _base.html
  _footer.html
  build.sh
  modules\
    01-overview.html
    02-xxx.html
    ...
  submodules\                    ← 子模块目录（如果有子目录）
    CompositionEngine\
      index.html                 ← 子模块入口
      modules\...
      submodules\...             ← 子模块的子模块
    DisplayHardware\
      index.html
      modules\...
    Scheduler\
      index.html
      modules\...
  index.html                     ← build.sh 组装生成
```

### 多级目录支持

如果输入目录包含子目录，每个子目录生成一个子模块教程，形成树状导航结构：

**导航规则：**
- 父模块的模块索引中包含指向各子模块的链接卡片（子模块入口）
- 子模块的模块索引中包含指回父模块的链接
- 子模块如果有子子模块，同样形成三级导航
- 点击子模块卡片跳转到 `submodules/{子模块名}/index.html`

**子模块生成规则：**

**目录过滤规则（按名称）：**
- 排除包含 `test` 的目录（不区分大小写，如 `tests`、`Test`、`unit_test` 等）
- 排除固定目录：`.git`、`fuzzer`、`include`、`generated`、`out`、`obj`

**Java 包识别规则（优先级高于目录）：**
- 如果目录下有 `Android.bp` 或 `AndroidManifest.xml`，扫描所有 `.java` 文件
- 按 Java 包名（`package com.android.server.wm`）分组
- 每个唯一包名生成一个子模块，包名转换为路径：`com/android/server/wm` → `submodules/com_android_server_wm/`
- 如果 Java 包有对应的 JNI 实现（`com_android_server_wm.cpp/h`），纳入同一子模块
- 剩余的 C++ 目录按原有规则处理（每个目录一个子模块）

**子模块数量限制：**
- ≤ 6 个时，全部生成
- > 6 个时，选择最重要的（文件数量最多的或被其他模块依赖最多的）

### 子模块教程深度要求

**目标**：初学者学完子模块教程后，能够：
1. 理解该子模块的职责和在整体系统中的位置
2. 找到需要修改的源代码文件（路径精确到文件名）
3. 理解关键函数/方法的签名和调用方式
4. 在指导下完成简单的代码修改（如添加一个状态标志、修改一个返回值、扩展一个分支）

**每个子模块应包含 4-6 个模块**（而非父模块的 3-6 个屏幕），内容覆盖：

| 模块类型 | 内容重点 |
|----------|----------|
| **全景模块** | 职责定位、上下游依赖、文件速览（file-tree） |
| **数据结构模块** | 核心结构体/类的完整定义（带行号）、成员变量含义、常见访问模式 |
| **核心流程模块** | 关键函数的完整调用链（带行号）、入参/返回值含义、调用者与被调用者 |
| **扩展修改模块** | 常见扩展点的代码示例、"在这里加新分支"的具体操作步骤 |
| **测验/练习模块** | 场景题：给出一个需求，问应该改哪个文件的哪一行 |

**每个子模块模块必须包含：**
- **文件定位图**：精确文件路径 + 行号范围，标明每个文件/方法的职责
- **完整代码块**：关键函数/类保留完整签名和注释，不做截断
- **行号标注**：重要代码行前加行号，便于初学者定位
- **修改点标记**：在代码中用 `// [EDIT HERE]` 注释标注常见扩展点
- **新手练习题**：至少 1 道"如果要实现 X 功能，你应该修改哪个文件的哪一行"类型的练习
- **常见错误提醒**：callout 说明初学者常犯的错误（如忘记加 break、参数传错顺序）

**子模块入口设计：**
子模块入口页面（`index.html`）的模块索引区显示：
1. 本模块的导航点（模块内章节）
2. 子模块卡片（点击跳转 `submodules/{name}/index.html`）
3. 返回父模块链接（如果有父模块）

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

5. **扫描子目录** — 检查源目录是否有直接子目录：
   - 排除目录：`.git`、`tests`、`fuzzer`、`include`、`generated`、`out`、`obj`
   - 有效子目录列表保存到 `output_path/.submodules`
   - 每个有效子目录创建 `output_path/submodules/{子模块名}/` 目录结构
   - 如果有子模块，阶段 3 设计中包含"子模块索引"屏幕

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

**Android.bp 依赖分析：**
- 读取所有 `Android.bp` 文件（每个子模块至少一个）
- 提取 `shared_libs`、`static_libs`、`header_libs`、`exports` 字段
- 提取 `srcs` 中引用的本地库（如 `libsurfaceflinger`、`libbinder` 等）
- 生成依赖图，标注关键依赖
- 依赖分析结果保存到 `output_path/dependencies.md`

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
| 6 | 依赖关系 — 模块引用了哪些其他模块 | Android.bp 中的 shared_libs、static_libs 等 |
| 7 | 调试与排错 — 常见问题和调试方法 | dumpsys、perfetto trace、常见卡顿原因 |

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
- **代码↔中文翻译块** — 每个模块至少 1 个（带行号）
- **测验题** — 每个模块至少 1 道（场景题 > 追踪题 > 概念题）
- **术语工具提示** — 每个模块中首次出现的技术术语
- **Bug 挑战** — "找 Bug"练习（子模块必须有，初学者修改代码时常犯的错误）
- **新手练习题** — "如果要实现 X，应该改哪个文件的哪一行"类型的实践题

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

**关键 — HTML/JS 契约：** `main.js` 引擎完全通过扫描特定的 CSS 类名和 `data-*` 属性来初始化。每个互动元素的 HTML 必须在结构属性上与参考模式逐字节匹配。这是互动功能失效的第一大原因：

- **测验：** 选项必须使用 `data-value`（不是 `data-answer`）和 `onclick="selectOption(this)"`。`.quiz-question-block` 必须有 `data-correct`、`data-explanation-right`、`data-explanation-wrong`。
- **聊天窗口：** 消息必须有 `data-sender` 和 `style="display:none"`。控制按钮必须使用类 `.chat-next-btn`、`.chat-all-btn`、`.chat-reset-btn`（不是自定义 `id` 值）。
- **流动画：** 按钮必须使用类 `.flow-next-btn` 和 `.flow-reset-btn`（不是自定义 `id` 值）。需要 `.flow-packet` 元素才能实现数据包移动动画。
- **Bug 挑战：** 使用带有 `onclick="checkBugLine(this, true/false)"` 的独立 `.bug-line` 元素——纯 `<pre>` 代码块不是互动的。

**在编写任何模块 HTML 之前阅读 `references/gotchas.md`**——它记录了真实课程构建中发现的失败模式。最常见的失败列在"HTML 元素不匹配 JS 引擎约定"下。

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
