---
name: ui-ux-pro-max
description: "面向 Web 和移动端的 UI/UX 设计智能。包含 50+ 种风格、161 种配色方案、57 种字体搭配、161 种产品类型、99 条 UX 指南和 25 种图表类型，覆盖 10 个技术栈（React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui 和 HTML/CSS）。操作：规划、构建、创建、设计、实现、审查、修复、改进、优化、增强、重构和检查 UI/UX 代码。项目：网站、落地页、仪表板、管理面板、电商、SaaS、作品集、博客和移动应用。元素：按钮、模态框、导航栏、侧边栏、卡片、表格、表单和图表。风格：玻璃拟态、粘土拟态、极简主义、粗野主义、新拟态、便当网格、深色模式、响应式、拟物化和平面设计。主题：色彩系统、无障碍、动画、布局、排版、字体搭配、间距、交互状态、阴影和渐变。集成：shadcn/ui MCP 用于组件搜索和示例。"
---

# UI/UX Pro Max - 设计智能

面向 Web 和移动应用程序的综合设计指南。包含 50+ 种风格、161 种配色方案、57 种字体搭配、161 种产品类型（附推理规则）、99 条 UX 指南和 25 种图表类型，覆盖 10 个技术栈。可搜索的数据库，提供基于优先级的推荐。

## 何时应用

当任务涉及 **UI 结构、视觉设计决策、交互模式或用户体验质量控制** 时，应使用此技能。

### 必须使用

以下情况必须调用此技能：

- 设计新页面（落地页、仪表板、管理后台、SaaS、移动应用）
- 创建或重构 UI 组件（按钮、模态框、表单、表格、图表等）
- 选择配色方案、排版系统、间距标准或布局系统
- 审查 UI 代码的用户体验、无障碍性或视觉一致性
- 实现导航结构、动画或响应式行为
- 做出产品级设计决策（风格、信息层次、品牌表达）
- 提升界面的感知质量、清晰度或可用性

### 建议使用

以下情况建议使用此技能：

- UI 看起来"不够专业"但原因不明
- 收到可用性或体验方面的反馈
- 发布前的 UI 质量优化
- 跨平台设计对齐（Web / iOS / Android）
- 构建设计系统或可复用组件库

### 跳过

以下情况不需要此技能：

- 纯后端逻辑开发
- 仅涉及 API 或数据库设计
- 与界面无关的性能优化
- 基础设施或 DevOps 工作
- 非视觉脚本或自动化任务

**判断标准**：如果任务会改变功能的 **外观、感觉、动效或交互方式**，则应使用此技能。

## 按优先级排列的规则类别

*供人工/AI 参考：按优先级 1→10 决定首先关注哪个规则类别；需要时使用 `--domain <Domain>` 查询详情。脚本不读取此表。*

| 优先级 | 类别 | 影响 | 域 | 关键检查（必须） | 反模式（避免） |
|--------|------|------|--------|------------------------|------------------------|
| 1 | 无障碍 | 关键 | `ux` | 对比度 4.5:1、Alt 文本、键盘导航、Aria-labels | 移除焦点环、仅图标按钮无标签 |
| 2 | 触控和交互 | 关键 | `ux` | 最小尺寸 44×44px、8px+ 间距、加载反馈 | 仅依赖悬停、即时状态变化（0ms） |
| 3 | 性能 | 高 | `ux` | WebP/AVIF、懒加载、预留空间（CLS < 0.1） | 布局抖动、累积布局偏移 |
| 4 | 风格选择 | 高 | `style`、`product` | 匹配产品类型、一致性、SVG 图标（无表情符号） | 随机混合扁平和拟物化风格、表情符号作为图标 |
| 5 | 布局和响应式 | 高 | `ux` | 移动优先断点、视口 meta、无水平滚动 | 水平滚动、固定 px 容器宽度、禁用缩放 |
| 6 | 排版和颜色 | 中 | `typography`、`color` | 基础 16px、行高 1.5、语义颜色令牌 | 正文 < 12px、灰色文字灰色背景、组件中使用原始十六进制 |
| 7 | 动画 | 中 | `ux` | 持续时间 150–300ms、动效传达意义、空间连续性 | 纯装饰动画、动画宽/高、无减弱动效 |
| 8 | 表单和反馈 | 中 | `ux` | 可见标签、错误靠近字段、辅助文本、渐进式披露 | 仅占位符标签、错误仅在顶部、一开始就信息过载 |
| 9 | 导航模式 | 高 | `ux` | 可预测的返回、底部导航 ≤5、深度链接 | 导航过载、返回行为异常、无深度链接 |
| 10 | 图表和数据 | 低 | `chart` | 图例、工具提示、无障碍颜色 | 仅依赖颜色传达含义 |

## 快速参考

### 1. 无障碍（关键）

- `color-contrast` - 普通文本最小 4.5:1 比率（大文本 3:1）；Material Design
- `focus-states` - 交互元素上可见的焦点环（2–4px；Apple HIG、MD）
- `alt-text` - 有意义图片的描述性 alt 文本
- `aria-labels` - 仅图标按钮使用 aria-label；原生使用 accessibilityLabel（Apple HIG）
- `keyboard-nav` - Tab 顺序与视觉顺序一致；完整的键盘支持（Apple HIG）
- `form-labels` - 使用带 for 属性的 label
- `skip-links` - 为键盘用户提供跳转到主内容的链接
- `heading-hierarchy` - 顺序的 h1→h6，不跳级
- `color-not-only` - 不要仅通过颜色传达信息（添加图标/文本）
- `dynamic-type` - 支持系统文本缩放；避免文本增长时截断（Apple Dynamic Type、MD）
- `reduced-motion` - 尊重 prefers-reduced-motion；请求时减少/禁用动画（Apple Reduced Motion API、MD）
- `voiceover-sr` - 有意义的 accessibilityLabel/accessibilityHint；VoiceOver/屏幕阅读器的逻辑阅读顺序（Apple HIG、MD）
- `escape-routes` - 在模态框和多步骤流程中提供取消/返回（Apple HIG）
- `keyboard-shortcuts` - 保留系统和无障碍快捷键；为拖放提供键盘替代方案（Apple HIG）

### 2. 触控和交互（关键）

- `touch-target-size` - 最小 44×44pt（Apple）/ 48×48dp（Material）；需要时将点击区域扩展到视觉边界之外
- `touch-spacing` - 触控目标之间最小 8px/8dp 间距（Apple HIG、MD）
- `hover-vs-tap` - 主要交互使用 click/tap；不要仅依赖悬停
- `loading-buttons` - 异步操作期间禁用按钮；显示加载指示器或进度
- `error-feedback` - 问题附近显示清晰的错误消息
- `cursor-pointer` - 可点击元素添加 cursor-pointer（Web）
- `gesture-conflicts` - 避免在主内容上水平滑动；优先使用垂直滚动
- `tap-delay` - 使用 touch-action: manipulation 减少 300ms 延迟（Web）
- `standard-gestures` - 一致使用平台标准手势；不要重新定义（如滑动返回、捏合缩放）（Apple HIG）
- `system-gestures` - 不要阻止系统手势（控制中心、返回滑动等）（Apple HIG）
- `press-feedback` - 按下时的视觉反馈（涟漪/高亮；MD 状态层）
- `haptic-feedback` - 确认和重要操作使用触觉反馈；避免过度使用（Apple HIG）
- `gesture-alternative` - 不要仅依赖手势交互；始终为关键操作提供可见控件
- `safe-area-awareness` - 主要触控目标远离刘海、灵动岛、手势条和屏幕边缘
- `no-precision-required` - 避免要求对小图标或细边缘进行精确点击
- `swipe-clarity` - 滑动操作必须显示清晰的可操作提示（箭头、标签、教程）
- `drag-threshold` - 开始拖动前使用移动阈值以避免意外拖动

### 3. 性能（高）

- `image-optimization` - 使用 WebP/AVIF、响应式图片（srcset/sizes）、延迟加载非关键资源
- `image-dimension` - 声明 width/height 或使用 aspect-ratio 以防止布局偏移（Core Web Vitals: CLS）
- `font-loading` - 使用 font-display: swap/optional 避免不可见文本（FOIT）；预留空间以减少布局偏移（MD）
- `font-preload` - 仅预加载关键字体；避免对每个变体过度使用预加载
- `critical-css` - 优先加载首屏 CSS（内联关键 CSS 或提前加载样式表）
- `lazy-loading` - 通过动态导入/路由级别拆分延迟加载非首屏组件
- `bundle-splitting` - 按路由/功能拆分代码（React Suspense / Next.js dynamic）以减少初始加载和 TTI
- `third-party-scripts` - 异步/延迟加载第三方脚本；审计并移除不必要的脚本（MD）
- `reduce-reflows` - 避免频繁的布局读写；批量读取 DOM 然后写入
- `content-jumping` - 为异步内容预留空间以避免布局跳动（Core Web Vitals: CLS）
- `lazy-load-below-fold` - 对首屏以下的图片和重型媒体使用 loading="lazy"
- `virtualize-lists` - 对 50+ 项的列表进行虚拟化以提高内存效率和滚动性能
- `main-thread-budget` - 每帧工作保持在 ~16ms 以内以实现 60fps；将重任务移出主线程（HIG、MD）
- `progressive-loading` - 对 >1s 的操作使用骨架屏/微光效果而非长时间阻塞的加载指示器（Apple HIG）
- `input-latency` - 点击/滚动的输入延迟保持在 ~100ms 以内（Material 响应性标准）
- `tap-feedback-speed` - 点击后 100ms 内提供视觉反馈（Apple HIG）
- `debounce-throttle` - 对高频事件（滚动、调整大小、输入）使用防抖/节流
- `offline-support` - 提供离线状态消息和基本回退（PWA / 移动端）
- `network-fallback` - 为慢网络提供降级模式（低分辨率图片、更少动画）

### 4. 风格选择（高）

- `style-match` - 风格与产品类型匹配（使用 `--design-system` 获取推荐）
- `consistency` - 所有页面使用相同风格
- `no-emoji-icons` - 使用 SVG 图标（Heroicons、Lucide），不使用表情符号
- `color-palette-from-product` - 从产品/行业选择调色板（搜索 `--domain color`）
- `effects-match-style` - 阴影、模糊、圆角与所选风格对齐（玻璃/扁平/粘土等）
- `platform-adaptive` - 尊重平台习惯（iOS HIG vs Material）：导航、控件、排版、动效
- `state-clarity` - 使悬停/按下/禁用状态在视觉上清晰可辨，同时保持风格一致（Material 状态层）
- `elevation-consistent` - 对卡片、底部表单、模态框使用一致的海拔/阴影比例；避免随机阴影值
- `dark-mode-pairing` - 同时设计亮/暗变体以保持品牌、对比度和风格一致
- `icon-style-consistent` - 在整个产品中使用一个图标集/视觉语言（描边宽度、圆角半径）
- `system-controls` - 优先使用原生/系统控件而非完全自定义的控件；仅在品牌需要时自定义（Apple HIG）
- `blur-purpose` - 使用模糊表示背景消隐（模态框、底部表单），而非作为装饰（Apple HIG）
- `primary-action` - 每个屏幕应只有一个主要 CTA；次要操作在视觉上从属（Apple HIG）

### 5. 布局和响应式（高）

- `viewport-meta` - width=device-width initial-scale=1（永远不要禁用缩放）
- `mobile-first` - 移动优先设计，然后扩展到平板和桌面
- `breakpoint-consistency` - 使用系统化的断点（如 375 / 768 / 1024 / 1440）
- `readable-font-size` - 移动端最小 16px 正文（避免 iOS 自动缩放）
- `line-length-control` - 移动端每行 35–60 字符；桌面端 60–75 字符
- `horizontal-scroll` - 移动端无水平滚动；确保内容适应视口宽度
- `spacing-scale` - 使用 4pt/8dp 增量间距系统（Material Design）
- `touch-density` - 保持组件间距适合触控：不拥挤，不导致误触
- `container-width` - 桌面端一致的最大宽度（max-w-6xl / 7xl）
- `z-index-management` - 定义分层的 z-index 比例（如 0 / 10 / 20 / 40 / 100 / 1000）
- `fixed-element-offset` - 固定导航栏/底部栏必须为底层内容预留安全内边距
- `scroll-behavior` - 避免干扰主滚动体验的嵌套滚动区域
- `viewport-units` - 移动端优先使用 min-h-dvh 而非 100vh
- `orientation-support` - 在横屏模式下保持布局可读和可操作
- `content-priority` - 移动端优先显示核心内容；折叠或隐藏次要内容
- `visual-hierarchy` - 通过大小、间距、对比度建立层次——不仅靠颜色

### 6. 排版和颜色（中）

- `line-height` - 正文使用 1.5-1.75
- `line-length` - 每行限制在 65-75 个字符
- `font-pairing` - 标题/正文字体个性匹配
- `font-scale` - 一致的字体比例（如 12 14 16 18 24 32）
- `contrast-readability` - 浅色背景上使用深色文本（如白色背景上的 slate-900）
- `text-styles-system` - 使用平台字体系统：iOS 11 Dynamic Type 样式 / Material 5 字体角色（display、headline、title、body、label）（HIG、MD）
- `weight-hierarchy` - 使用 font-weight 强化层次：粗标题（600–700）、常规正文（400）、中等标签（500）（MD）
- `color-semantic` - 定义语义颜色令牌（primary、secondary、error、surface、on-surface），不在组件中使用原始十六进制（Material 色彩系统）
- `color-dark-mode` - 深色模式使用去饱和/更浅的色调变体，而非反转颜色；单独测试对比度（HIG、MD）
- `color-accessible-pairs` - 前景/背景配对必须满足 4.5:1（AA）或 7:1（AAA）；使用工具验证（WCAG、MD）
- `color-not-decorative-only` - 功能性颜色（错误红、成功绿）必须包含图标/文本；避免仅颜色含义（HIG、MD）
- `truncation-strategy` - 优先换行而非截断；截断时使用省略号并通过工具提示/展开提供完整文本（Apple HIG）
- `letter-spacing` - 尊重每个平台的默认字间距；避免正文使用紧凑字距（HIG、MD）
- `number-tabular` - 数据列、价格和计时器使用等宽数字以防止布局偏移
- `whitespace-balance` - 有意使用空白来分组相关项目和分隔区域；避免视觉杂乱（Apple HIG）

### 7. 动画（中）

- `duration-timing` - 微交互使用 150–300ms；复杂过渡 ≤400ms；避免 >500ms（MD）
- `transform-performance` - 仅使用 transform/opacity；避免动画化 width/height/top/left
- `loading-states` - 加载超过 300ms 时显示骨架屏或进度指示器
- `excessive-motion` - 每个视图最多动画 1-2 个关键元素
- `easing` - 进入使用 ease-out，退出使用 ease-in；UI 过渡避免线性
- `motion-meaning` - 每个动画必须表达因果关系，而非纯装饰（Apple HIG）
- `state-transition` - 状态变化（悬停/活动/展开/折叠/模态框）应平滑动画，而非突然切换
- `continuity` - 页面/屏幕过渡应保持空间连续性（共享元素、方向滑动）（Apple HIG）
- `parallax-subtle` - 谨慎使用视差；必须尊重减弱动效且不造成眩晕（Apple HIG）
- `spring-physics` - 优先使用弹簧/基于物理的曲线而非线性或 cubic-bezier 以获得自然感觉（Apple HIG 流体动画）
- `exit-faster-than-enter` - 退出动画比进入短（约进入持续时间的 60–70%）以感觉响应迅速（MD motion）
- `stagger-sequence` - 列表/网格项进入时每个项目延迟 30–50ms；避免一次性或太慢的显示（MD）
- `shared-element-transition` - 使用共享元素/英雄过渡实现屏幕间的视觉连续性（MD、HIG）
- `interruptible` - 动画必须可中断；用户点击/手势立即取消进行中的动画（Apple HIG）
- `no-blocking-animation` - 动画期间永远不要阻止用户输入；UI 必须保持可交互（Apple HIG）
- `fade-crossfade` - 同一容器内的内容替换使用交叉淡入淡出（MD）
- `scale-feedback` - 可点击的卡片/按钮按下时使用微小缩放（0.95–1.05）；释放时恢复（HIG、MD）
- `gesture-feedback` - 拖动、滑动和捏合必须提供实时视觉响应跟踪手指（MD Motion）
- `hierarchy-motion` - 使用平移/缩放方向表达层次：从下方进入 = 更深层，向上退出 = 返回（MD）
- `motion-consistency` - 全局统一持续时间/缓动令牌；所有动画共享相同的节奏和感觉
- `opacity-threshold` - 淡出元素不应在 opacity 0.2 以下停留；要么完全淡出要么保持可见
- `modal-motion` - 模态框/底部表单应从触发源动画（缩放+淡入或滑入）以提供空间上下文（HIG、MD）
- `navigation-direction` - 前进导航向左/上动画；后退向右/下动画——保持方向逻辑一致（HIG）
- `layout-shift-avoid` - 动画不得引起布局回流或 CLS；位置变化使用 transform

### 8. 表单和反馈（中）

- `input-labels` - 每个输入框有可见标签（不只是占位符）
- `error-placement` - 在相关字段下方显示错误
- `submit-feedback` - 提交时显示加载状态，然后显示成功/错误状态
- `required-indicators` - 标记必填字段（如星号）
- `empty-states` - 无内容时显示有用的消息和操作
- `toast-dismiss` - Toast 在 3-5 秒后自动消失
- `confirmation-dialogs` - 破坏性操作前确认
- `input-helper-text` - 复杂输入下方提供持久的辅助文本，不只是占位符（Material Design）
- `disabled-states` - 禁用元素使用降低的不透明度（0.38–0.5）+ 光标变化 + 语义属性（MD）
- `progressive-disclosure` - 渐进式显示复杂选项；不要一开始就让用户不知所措（Apple HIG）
- `inline-validation` - 在失焦时验证（非按键时）；用户完成输入后才显示错误（MD）
- `input-type-keyboard` - 使用语义输入类型（email、tel、number）以触发正确的移动键盘（HIG、MD）
- `password-toggle` - 密码字段提供显示/隐藏切换（MD）
- `autofill-support` - 使用 autocomplete / textContentType 属性以便系统自动填充（HIG、MD）
- `undo-support` - 允许撤销破坏性或批量操作（如"撤销删除"toast）（Apple HIG）
- `success-feedback` - 用简短的视觉反馈确认完成的操作（勾选、toast、颜色闪烁）（MD）
- `error-recovery` - 错误消息必须包含清晰的恢复路径（重试、编辑、帮助链接）（HIG、MD）
- `multi-step-progress` - 多步骤流程显示步骤指示器或进度条；允许返回导航（MD）
- `form-autosave` - 长表单应自动保存草稿以防止意外关闭时数据丢失（Apple HIG）
- `sheet-dismiss-confirm` - 关闭有未保存更改的底部表单/模态框前确认（Apple HIG）
- `error-clarity` - 错误消息必须说明原因 + 修复方法（不只是"输入无效"）（HIG、MD）
- `field-grouping` - 逻辑分组相关字段（fieldset/legend 或视觉分组）（MD）
- `read-only-distinction` - 只读状态在视觉和语义上应与禁用不同（MD）
- `focus-management` - 提交错误后，自动聚焦第一个无效字段（WCAG、MD）
- `error-summary` - 多个错误时，在顶部显示摘要并提供锚点链接到每个字段（WCAG）
- `touch-friendly-input` - 移动端输入高度 ≥44px 以满足触控目标要求（Apple HIG）
- `destructive-emphasis` - 破坏性操作使用语义危险颜色（红色），并在视觉上与主要操作分离（HIG、MD）
- `toast-accessibility` - Toast 不得抢夺焦点；使用 aria-live="polite" 进行屏幕阅读器公告（WCAG）
- `aria-live-errors` - 表单错误使用 aria-live 区域或 role="alert" 通知屏幕阅读器（WCAG）
- `contrast-feedback` - 错误和成功状态颜色必须满足 4.5:1 对比度比率（WCAG、MD）
- `timeout-feedback` - 请求超时必须显示清晰的反馈并提供重试选项（MD）

### 9. 导航模式（高）

- `bottom-nav-limit` - 底部导航最多 5 个项目；使用带标签的图标（Material Design）
- `drawer-usage` - 使用抽屉/侧边栏进行次要导航，而非主要操作（Material Design）
- `back-behavior` - 返回导航必须可预测且一致；保留滚动/状态（Apple HIG、MD）
- `deep-linking` - 所有关键屏幕必须可通过深度链接/URL 访问，用于分享和通知（Apple HIG、MD）
- `tab-bar-ios` - iOS：使用底部 Tab Bar 进行顶级导航（Apple HIG）
- `top-app-bar-android` - Android：使用带导航图标的应用顶部栏作为主要结构（Material Design）
- `nav-label-icon` - 导航项目必须同时有图标和文本标签；仅图标导航损害可发现性（MD）
- `nav-state-active` - 当前位置必须在导航中视觉高亮（颜色、粗细、指示器）（HIG、MD）
- `nav-hierarchy` - 主要导航（标签/底部栏）与次要导航（抽屉/设置）必须清晰分离（MD）
- `modal-escape` - 模态框和底部表单必须提供清晰的关闭/消隐方式；移动端下滑关闭（Apple HIG）
- `search-accessible` - 搜索必须易于访问（顶部栏或标签页）；提供最近/建议的查询（MD）
- `breadcrumb-web` - Web：对 3+ 层深度层次使用面包屑导航以辅助定位（MD）
- `state-preservation` - 返回时必须恢复之前的滚动位置、筛选状态和输入（HIG、MD）
- `gesture-nav-support` - 支持系统手势导航（iOS 滑动返回、Android 预测性返回）且不冲突（HIG、MD）
- `tab-badge` - 谨慎使用导航项目上的徽章表示未读/待处理；用户访问后清除（HIG、MD）
- `overflow-menu` - 操作超出可用空间时，使用溢出/更多菜单而非拥挤排列（MD）
- `bottom-nav-top-level` - 底部导航仅用于顶级屏幕；永远不要在其中嵌套子导航（MD）
- `adaptive-navigation` - 大屏幕（≥1024px）优先使用侧边栏；小屏幕使用底部/顶部导航（Material Adaptive）
- `back-stack-integrity` - 永远不要静默重置导航栈或意外跳转到首页（HIG、MD）
- `navigation-consistency` - 导航位置在所有页面必须保持一致；不要按页面类型改变
- `avoid-mixed-patterns` - 不要在同一层级混合 Tab + 侧边栏 + 底部导航
- `modal-vs-navigation` - 模态框不得用于主导航流程；它们会打断用户的路径（HIG）
- `focus-on-route-change` - 页面过渡后，将焦点移到主内容区域以方便屏幕阅读器用户（WCAG）
- `persistent-nav` - 核心导航必须从深层页面可访问；不要在子流程中完全隐藏（HIG、MD）
- `destructive-nav-separation` - 危险操作（删除账户、注销）必须在视觉和空间上与普通导航项目分离（HIG、MD）
- `empty-nav-state` - 导航目标不可用时，解释原因而非静默隐藏（MD）

### 10. 图表和数据（低）

- `chart-type` - 图表类型与数据类型匹配（趋势→折线、比较→柱状、比例→饼图/环形图）
- `color-guidance` - 使用无障碍调色板；避免仅红/绿配对以照顾色盲用户（WCAG、MD）
- `data-table` - 提供表格替代方案以保证无障碍；仅图表对屏幕阅读器不友好（WCAG）
- `pattern-texture` - 用图案、纹理或形状补充颜色，使数据在无颜色时也能区分（WCAG、MD）
- `legend-visible` - 始终显示图例；靠近图表放置，不要分离到滚动折叠下方（MD）
- `tooltip-on-interact` - 悬停（Web）或点击（移动端）时提供工具提示/数据标签显示精确值（HIG、MD）
- `axis-labels` - 为坐标轴标注单位和可读刻度；避免移动端截断或旋转标签
- `responsive-chart` - 图表在小屏幕上必须回流或简化（如水平柱状图替代垂直柱状图、更少刻度）
- `empty-data-state` - 无数据时显示有意义的空状态（"暂无数据"+ 引导），而非空白图表（MD）
- `loading-chart` - 图表数据加载时使用骨架屏或微光占位符；不要显示空坐标轴框架
- `animation-optional` - 图表进入动画必须尊重 prefers-reduced-motion；数据应立即可读（HIG）
- `large-dataset` - 1000+ 数据点时，聚合或采样；提供下钻查看详情而非全部渲染（MD）
- `number-formatting` - 坐标轴和标签上的数字、日期、货币使用本地化格式（HIG、MD）
- `touch-target-chart` - 交互式图表元素（点、片段）必须有 ≥44pt 点击区域或触摸时扩展（Apple HIG）
- `no-pie-overuse` - 超过 5 个类别避免使用饼图/环形图；切换到柱状图以提高清晰度
- `contrast-data` - 数据线/柱与背景 ≥3:1；数据文本标签 ≥4.5:1（WCAG）
- `legend-interactive` - 图例应可点击以切换系列可见性（MD）
- `direct-labeling` - 小数据集直接在图表上标注数值以减少视线移动
- `tooltip-keyboard` - 工具提示内容必须可通过键盘访问，不依赖悬停（WCAG）
- `sortable-table` - 数据表格必须支持排序，aria-sort 指示当前排序状态（WCAG）
- `axis-readability` - 坐标轴刻度不得拥挤；保持可读间距，小屏幕上自动跳过
- `data-density` - 限制每个图表的信息密度以避免认知过载；需要时拆分为多个图表
- `trend-emphasis` - 强调数据趋势而非装饰；避免遮挡数据的重渐变/阴影
- `gridline-subtle` - 网格线应低对比度（如 gray-200）以不与数据竞争
- `focusable-elements` - 交互式图表元素（点、柱、切片）必须可键盘导航（WCAG）
- `screen-reader-summary` - 为屏幕阅读器提供描述图表关键洞察的文本摘要或 aria-label（WCAG）
- `error-state-chart` - 数据加载失败必须显示错误消息并提供重试操作，而非损坏/空白图表
- `export-option` - 数据密集型产品提供图表数据的 CSV/图片导出
- `drill-down-consistency` - 下钻交互必须保持清晰的返回路径和层次面包屑
- `time-scale-clarity` - 时间序列图表必须清晰标注时间粒度（日/周/月）并允许切换

## 如何使用

使用下面的 CLI 工具搜索特定域。

---

## 前提条件

检查是否安装了 Python：

```bash
python3 --version || python --version
```

如果未安装 Python，根据用户的操作系统安装：

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## 如何使用此技能

当用户请求以下任何操作时使用此技能：

| 场景 | 触发示例 | 起始步骤 |
|----------|-----------------|------------|
| **新项目/页面** | "构建落地页"、"构建仪表板" | 步骤 1 → 步骤 2（设计系统） |
| **新组件** | "创建定价卡片"、"添加模态框" | 步骤 3（域搜索：style、ux） |
| **选择风格/颜色/字体** | "什么风格适合金融科技应用？"、"推荐配色方案" | 步骤 2（设计系统） |
| **审查现有 UI** | "审查此页面的 UX 问题"、"检查无障碍性" | 上方快速参考检查清单 |
| **修复 UI 缺陷** | "按钮悬停坏了"、"加载时布局偏移" | 快速参考 → 相关部分 |
| **改进/优化** | "让这个更快"、"改善移动端体验" | 步骤 3（域搜索：ux、react） |
| **实现深色模式** | "添加深色模式支持" | 步骤 3（域：style "dark mode"） |
| **添加图表/数据可视化** | "添加分析仪表板图表" | 步骤 3（域：chart） |
| **技术栈最佳实践** | "React 性能技巧"、"SwiftUI 导航" | 步骤 4（技术栈搜索） |

遵循此工作流：

### 步骤 1：分析用户需求

从用户请求中提取关键信息：
- **产品类型**：娱乐（社交、视频、音乐、游戏）、工具（扫描器、编辑器、转换器）、生产力（任务管理、笔记、日历）或混合
- **目标受众**：C 端消费者用户；考虑年龄段、使用场景（通勤、休闲、工作）
- **风格关键词**：活泼、鲜艳、极简、深色模式、内容优先、沉浸式等
- **技术栈**：React Native（本项目的唯一技术栈）

### 步骤 2：生成设计系统（必需）

**始终从 `--design-system` 开始** 以获取带推理的综合推荐：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

此命令：
1. 并行搜索域（product、style、color、landing、typography）
2. 应用 `ui-reasoning.csv` 中的推理规则选择最佳匹配
3. 返回完整设计系统：模式、风格、颜色、排版、效果
4. 包含需要避免的反模式

**示例：**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 步骤 2b：持久化设计系统（主控 + 覆盖模式）

要保存设计系统以实现**跨会话的分层检索**，添加 `--persist`：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

这将创建：
- `design-system/MASTER.md` — 包含所有设计规则的全局真实来源
- `design-system/pages/` — 页面特定覆盖的文件夹

**带页面特定覆盖：**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

这还将创建：
- `design-system/pages/dashboard.md` — 页面特定的偏离主控规则

**分层检索工作方式：**
1. 构建特定页面（如"结账"）时，首先检查 `design-system/pages/checkout.md`
2. 如果页面文件存在，其规则**覆盖**主控文件
3. 如果不存在，则完全使用 `design-system/MASTER.md`

**上下文感知检索提示：**
```
I am building the [Page Name] page. Please read design-system/MASTER.md.
Also check if design-system/pages/[page-name].md exists.
If the page file exists, prioritize its rules.
If not, use the Master rules exclusively.
Now, generate the code...
```

### 步骤 3：按需补充详细搜索

获取设计系统后，使用域搜索获取额外详情：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**何时使用详细搜索：**

| 需求 | 域 | 示例 |
|------|--------|---------|
| 产品类型模式 | `product` | `--domain product "entertainment social"` |
| 更多样式选项 | `style` | `--domain style "glassmorphism dark"` |
| 配色方案 | `color` | `--domain color "entertainment vibrant"` |
| 字体搭配 | `typography` | `--domain typography "playful modern"` |
| 图表推荐 | `chart` | `--domain chart "real-time dashboard"` |
| UX 最佳实践 | `ux` | `--domain ux "animation accessibility"` |
| 替代字体 | `typography` | `--domain typography "elegant luxury"` |
| 单个 Google Fonts | `google-fonts` | `--domain google-fonts "sans serif popular variable"` |
| 落地页结构 | `landing` | `--domain landing "hero social-proof"` |
| React Native 性能 | `react` | `--domain react "rerender memo list"` |
| 应用界面无障碍 | `web` | `--domain web "accessibilityLabel touch safe-areas"` |
| AI 提示 / CSS 关键词 | `prompt` | `--domain prompt "minimalism"` |

### 步骤 4：技术栈指南（React Native）

获取 React Native 实现特定的最佳实践：

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack react-native
```

---

## 搜索参考

### 可用域

| 域 | 用途 | 示例关键词 |
|--------|---------|------------------|
| `product` | 产品类型推荐 | SaaS、电商、作品集、医疗、美容、服务 |
| `style` | UI 风格、颜色、效果 | 玻璃拟态、极简、深色模式、粗野主义 |
| `typography` | 字体搭配、Google Fonts | 优雅、活泼、专业、现代 |
| `color` | 按产品类型的配色方案 | saas、ecommerce、healthcare、beauty、fintech、service |
| `landing` | 页面结构、CTA 策略 | hero、hero-centric、testimonial、pricing、social-proof |
| `chart` | 图表类型、库推荐 | 趋势、比较、时间线、漏斗、饼图 |
| `ux` | 最佳实践、反模式 | 动画、无障碍、z-index、加载 |
| `google-fonts` | 单个 Google Fonts 查找 | sans serif、monospace、japanese、variable font、popular |
| `react` | React/Next.js 性能 | waterfall、bundle、suspense、memo、rerender、cache |
| `web` | 应用界面指南（iOS/Android/React Native） | accessibilityLabel、touch targets、safe areas、Dynamic Type |
| `prompt` | AI 提示、CSS 关键词 | （风格名称） |

### 可用技术栈

| 技术栈 | 重点 |
|-------|-------|
| `react-native` | 组件、导航、列表 |

---

## 示例工作流

**用户请求：** "做一个 AI 搜索首页。"

### 步骤 1：分析需求
- 产品类型：工具（AI 搜索引擎）
- 目标受众：寻求快速、智能搜索的 C 端用户
- 风格关键词：现代、极简、内容优先、深色模式
- 技术栈：React Native

### 步骤 2：生成设计系统（必需）

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "AI search tool modern minimal" --design-system -p "AI Search"
```

**输出：** 包含模式、风格、颜色、排版、效果和反模式的完整设计系统。

### 步骤 3：按需补充详细搜索

```bash
# 获取现代工具产品的风格选项
python3 skills/ui-ux-pro-max/scripts/search.py "minimalism dark mode" --domain style

# 获取搜索交互和加载的 UX 最佳实践
python3 skills/ui-ux-pro-max/scripts/search.py "search loading animation" --domain ux
```

### 步骤 4：技术栈指南

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "list performance navigation" --stack react-native
```

**然后：** 综合设计系统 + 详细搜索，实现设计。

---

## 输出格式

`--design-system` 标志支持两种输出格式：

```bash
# ASCII 框（默认）- 最适合终端显示
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system

# Markdown - 最适合文档
python3 skills/ui-ux-pro-max/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## 获得更好结果的技巧

### 查询策略

- 使用**多维关键词** — 结合产品 + 行业 + 语气 + 密度：`"entertainment social vibrant content-dense"` 而非仅 `"app"`
- 对同一需求尝试不同关键词：`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`
- 先使用 `--design-system` 获取完整推荐，然后用 `--domain` 深入了解不确定的维度
- 始终添加 `--stack react-native` 以获取实现特定的指导

### 常见卡点

| 问题 | 解决方案 |
|---------|------------|
| 无法决定风格/颜色 | 用不同关键词重新运行 `--design-system` |
| 深色模式对比度问题 | 快速参考 §6：`color-dark-mode` + `color-accessible-pairs` |
| 动画感觉不自然 | 快速参考 §7：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单 UX 差 | 快速参考 §8：`inline-validation` + `error-clarity` + `focus-management` |
| 导航令人困惑 | 快速参考 §9：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏幕布局崩溃 | 快速参考 §5：`mobile-first` + `breakpoint-consistency` |
| 性能/卡顿 | 快速参考 §3：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

### 交付前检查清单

- 实现前运行 `--domain ux "animation accessibility z-index loading"` 作为 UX 验证
- 快速参考 **§1–§3**（关键 + 高）作为最终审查
- 在 375px（小手机）和横屏方向上测试
- 启用**减弱动效**和最大**动态字体**大小下验证行为
- 独立检查深色模式对比度（不要假设亮色模式值有效）
- 确认所有触控目标 ≥44pt 且无内容隐藏在安全区域后面

---

## 专业 UI 常见规则

这些是经常被忽视的问题，会让 UI 看起来不专业：
范围说明：以下规则适用于应用 UI（iOS/Android/React Native/Flutter），而非桌面 Web 交互模式。

### 图标和视觉元素

| 规则 | 标准 | 避免 | 重要原因 |
|------|----------|--------|----------------|
| **不要使用表情符号作为结构图标** | 使用基于矢量的图标（如 Lucide、react-native-vector-icons、@expo/vector-icons）。 | 使用表情符号（🎨 🚀 ⚙️）进行导航、设置或系统控制。 | 表情符号依赖字体，跨平台不一致，且无法通过设计令牌控制。 |
| **仅使用矢量资源** | 使用 SVG 或平台矢量图标，可清晰缩放并支持主题化。 | 模糊或像素化的光栅 PNG 图标。 | 确保可扩展性、清晰渲染和亮/暗模式适应性。 |
| **稳定的交互状态** | 使用颜色、不透明度或海拔变化表示按下状态，不改变布局边界。 | 移动周围内容或触发视觉抖动的布局偏移变换。 | 防止不稳定的交互，保持移动端的平滑运动/感知质量。 |
| **正确的品牌标志** | 使用官方品牌资源并遵循其使用指南（间距、颜色、净空间）。 | 猜测标志路径、非官方重新着色或修改比例。 | 防止品牌误用，确保法律/平台合规。 |
| **一致的图标尺寸** | 将图标尺寸定义为设计令牌（如 icon-sm、icon-md = 24pt、icon-lg）。 | 随机混合任意值如 20pt / 24pt / 28pt。 | 保持界面的节奏和视觉层次。 |
| **描边一致性** | 在同一视觉层内使用一致的描边宽度（如 1.5px 或 2px）。 | 任意混合粗细描边样式。 | 不一致的描边降低感知的精致度和凝聚力。 |
| **填充 vs 轮廓规范** | 每个层级使用一种图标样式。 | 在同一层级混合填充和轮廓图标。 | 保持语义清晰和风格连贯。 |
| **触控目标最小值** | 最小 44×44pt 交互区域（图标较小时使用 hitSlop）。 | 小图标无扩展点击区域。 | 满足无障碍和平台可用性标准。 |
| **图标对齐** | 图标与文本基线对齐并保持一致的内边距。 | 图标错位或周围间距不一致。 | 防止降低感知质量的微妙视觉失衡。 |
| **图标对比度** | 遵循 WCAG 对比度标准：小元素 4.5:1，较大 UI 符号最小 3:1。 | 与背景融合的低对比度图标。 | 确保亮暗模式下的无障碍性。 |


### 交互（应用）

| 规则 | 做 | 不做 |
|------|----|----- |
| **点击反馈** | 80-150ms 内提供清晰的按下反馈（涟漪/不透明度/海拔） | 点击无视觉响应 |
| **动画时间** | 微交互保持约 150-300ms，使用平台原生缓动 | 即时过渡或慢动画（>500ms） |
| **无障碍焦点** | 确保屏幕阅读器焦点顺序与视觉顺序一致，标签具有描述性 | 未标记的控件或混乱的焦点遍历 |
| **禁用状态清晰度** | 使用禁用语义（`disabled`/原生禁用属性）、降低强调且无点击操作 | 看起来可点击但无响应的控件 |
| **触控目标最小值** | 点击区域 >=44x44pt（iOS）或 >=48x48dp（Android），图标较小时扩展点击区域 | 小点击目标或仅图标无内边距的点击区域 |
| **手势冲突预防** | 每个区域保持一个主要手势，避免嵌套的点击/拖动冲突 | 重叠手势导致意外操作 |
| **语义原生控件** | 优先使用原生交互原语（`Button`、`Pressable`、平台等效物）并带正确的无障碍角色 | 用作主要控件但无语义的通用容器 |

### 亮/暗模式对比度

| 规则 | 做 | 不做 |
|------|----|----- |
| **表面可读性（亮色）** | 卡片/表面与背景保持清晰分离，有足够的不透明度/海拔 | 过度透明的表面模糊层次 |
| **文本对比度（亮色）** | 正文文本对比度 >=4.5:1（亮色表面） | 低对比度灰色正文 |
| **文本对比度（暗色）** | 主要文本对比度 >=4.5:1，次要文本 >=3:1（暗色表面） | 深色模式文本与背景融合 |
| **边框和分隔线可见性** | 确保分隔线在两个主题中可见（不只是亮色模式） | 特定主题的边框在一个模式中消失 |
| **状态对比度对等** | 保持按下/聚焦/禁用状态在亮暗主题中同样可辨 | 仅为一个主题定义交互状态 |
| **令牌驱动主题** | 使用跨应用表面/文本/图标的语义颜色令牌映射每个主题 | 每个屏幕硬编码十六进制值 |
| **遮罩和模态框可读性** | 使用足够强的模态框遮罩以隔离前景内容（通常 40-60% 黑色） | 弱遮罩使背景在视觉上竞争 |

### 布局和间距

| 规则 | 做 | 不做 |
|------|----|----- |
| **安全区域合规** | 所有固定标题、标签栏和 CTA 栏尊重顶部/底部安全区域 | 将固定 UI 放在刘海、状态栏或手势区域下 |
| **系统栏清除** | 为状态/导航栏和手势主页指示器添加间距 | 可点击内容与操作系统界面冲突 |
| **一致的内容宽度** | 每个设备类别（手机/平板）保持可预测的内容宽度 | 屏幕间混合任意宽度 |
| **8dp 间距节奏** | 使用一致的 4/8dp 间距系统用于内边距/间隙/区域间距 | 无节奏的随机间距增量 |
| **可读文本度量** | 大设备上保持长文本可读（避免平板上边到边的段落） | 全宽长文本损害可读性 |
| **区域间距层次** | 定义清晰的垂直节奏层级（如 16/24/32/48）按层次 | 相似 UI 层级间距不一致 |
| **自适应沟槽按断点** | 较大宽度和横屏时增加水平内边距 | 所有设备尺寸/方向使用相同窄沟槽 |
| **滚动和固定元素共存** | 添加底部/顶部内容内边距使列表不被固定栏隐藏 | 滚动内容被粘性标题/页脚遮挡 |

---

## 交付前检查清单

在交付 UI 代码之前，验证以下项目：
范围说明：此检查清单适用于应用 UI（iOS/Android/React Native/Flutter）。

### 视觉质量
- [ ] 未使用表情符号作为图标（使用 SVG 替代）
- [ ] 所有图标来自一致的图标系列和风格
- [ ] 使用正确的比例和净空间的官方品牌资源
- [ ] 按下状态视觉不偏移布局边界或引起抖动
- [ ] 一致使用语义主题令牌（无临时的每个屏幕硬编码颜色）

### 交互
- [ ] 所有可点击元素提供清晰的按下反馈（涟漪/不透明度/海拔）
- [ ] 触控目标满足最小尺寸（>=44x44pt iOS、>=48x48dp Android）
- [ ] 微交互时间保持在 150-300ms 范围内，使用原生感觉的缓动
- [ ] 禁用状态视觉上清晰且不可交互
- [ ] 屏幕阅读器焦点顺序与视觉顺序一致，交互标签具有描述性
- [ ] 手势区域避免嵌套/冲突的交互（点击/拖动/返回滑动冲突）

### 亮/暗模式
- [ ] 主要文本对比度在亮暗模式下 >=4.5:1
- [ ] 次要文本对比度在亮暗模式下 >=3:1
- [ ] 分隔线/边框和交互状态在两种模式下可辨
- [ ] 模态框/抽屉遮罩不透明度足够强以保持前景可读性（通常 40-60% 黑色）
- [ ] 交付前测试了两种主题（非从单一主题推断）

### 布局
- [ ] 标题、标签栏和底部 CTA 栏尊重安全区域
- [ ] 滚动内容不被固定/粘性栏隐藏
- [ ] 在小手机、大手机和平板上验证（纵向 + 横向）
- [ ] 水平内边距/沟槽按设备尺寸和方向正确适配
- [ ] 4/8dp 间距节奏在组件、区域和页面级别保持一致
- [ ] 长文本度量在大设备上保持可读（无边到边段落）

### 无障碍
- [ ] 所有有意义的图片/图标有无障碍标签
- [ ] 表单字段有标签、提示和清晰的错误消息
- [ ] 颜色不是唯一指标
- [ ] 支持减弱动效和动态文本大小且不破坏布局
- [ ] 无障碍特性/角色/状态（选中、禁用、展开）正确公告
