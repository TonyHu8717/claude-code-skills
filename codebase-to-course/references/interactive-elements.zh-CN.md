# 互动元素参考

课程中使用的每种互动元素的实现模式。选择最能服务于每个模块教学目标的元素。

> **架构说明：** 所有 CSS 和 JavaScript 都存在于 `references/styles.css` 和 `references/main.js` 中，它们被逐字复制到每个课程目录中。编写模块 HTML 文件时，只使用下面的 HTML 模式——不要为这些元素内联 `<style>` 或 `<script>` 标签。`main.js` 中的引擎通过扫描这里描述的相关类名和 `data-*` 属性在页面加载时自动初始化。

## 目录
1. [代码 ↔ 英文对照块](#代码--英文对照块)
2. [多项选择测验](#多项选择测验)
3. [拖放匹配](#拖放匹配)
4. [群聊动画](#群聊动画)
5. [消息流/数据流动画](#消息流数据流动画)
6. [交互式架构图](#交互式架构图)
7. [层切换演示](#层切换演示)
8. ["找 Bug"挑战](#找-bug-挑战)
9. [场景测验](#场景测验)
10. [提示框](#提示框)
11. [模式/功能卡片](#模式功能卡片)
12. [流程图](#流程图)
13. [权限/配置徽章](#权限配置徽章)
14. [术语提示](#术语提示)
15. [可视化文件树](#可视化文件树)
16. [图标标签行](#图标标签行)
17. [编号步骤卡片](#编号步骤卡片)

---

## 代码 ↔ 英文对照块

最重要的教学元素。左侧显示项目中的真实代码，右侧逐行提供通俗英文翻译。

**HTML：**
```html
<div class="translation-block animate-in">
  <div class="translation-code">
    <span class="translation-label">代码</span>
    <pre><code>
<span class="code-line"><span class="code-keyword">const</span> response = <span class="code-keyword">await</span> <span class="code-function">fetch</span>(url, {</span>
<span class="code-line">  <span class="code-property">method</span>: <span class="code-string">'POST'</span>,</span>
<span class="code-line">  <span class="code-property">headers</span>: { <span class="code-string">'Authorization'</span>: apiKey }</span>
<span class="code-line">});</span>
    </code></pre>
  </div>
  <div class="translation-english">
    <span class="translation-label">通俗英文</span>
    <div class="translation-lines">
      <p class="tl">发送请求到 URL 并等待响应...</p>
      <p class="tl">我们正在发送数据（POST），而不只是查询（GET）...</p>
      <p class="tl">包含我们的 API 密钥，这样服务器就知道我们是谁...</p>
      <p class="tl">请求设置完毕。</p>
    </div>
  </div>
</div>
```

**规则：**
- 每个英文行应该对应 1-2 行代码
- 使用会话语言，不用技术术语
- 突出"为什么"而不仅仅是"是什么"——例如，"包含我们的 API 密钥，这样服务器就知道我们是谁"而不是"设置 Authorization 头"

---

## 多项选择测验

用于即时反馈的理解测试。每个问题有选项、一个正确答案和每个问题的解释。

**连接：** `main.js` 暴露 `window.selectOption(btn)`、`window.checkQuiz(containerId)` 和 `window.resetQuiz(containerId)`。通过 `onclick` 调用它们。每个问题的解释放在 `.quiz-question-block` 上的 `data-explanation-right` 和 `data-explanation-wrong` 中。

**HTML：**
```html
<div class="quiz-container" id="quiz-module3">
  <div class="quiz-question-block"
       data-correct="option-b"
       data-explanation-right="正确——因为在这个架构中，X 负责 Y。"
       data-explanation-wrong="不太对。想想 Y 在代码库中的位置...">
    <h3 class="quiz-question">问题文本在这里？</h3>
    <div class="quiz-options">
      <button class="quiz-option" data-value="option-a" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>选项 A</span>
      </button>
      <button class="quiz-option" data-value="option-b" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>选项 B（正确）</span>
      </button>
      <button class="quiz-option" data-value="option-c" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>选项 C</span>
      </button>
    </div>
    <div class="quiz-feedback"></div>
  </div>

  <button class="quiz-check-btn" onclick="checkQuiz('quiz-module3')">检查答案</button>
  <button class="quiz-reset-btn" onclick="resetQuiz('quiz-module3')">再试一次</button>
</div>
```

---

## 拖放匹配

用于将概念与描述匹配。支持鼠标（HTML5 拖放 API）和触摸。

**HTML：**
```html
<div class="dnd-container" id="dnd-module2">
  <div class="dnd-chips">
    <div class="dnd-chip" draggable="true" data-answer="actor-a">角色 A</div>
    <div class="dnd-chip" draggable="true" data-answer="actor-b">角色 B</div>
    <div class="dnd-chip" draggable="true" data-answer="actor-c">角色 C</div>
  </div>
  <div class="dnd-zones">
    <div class="dnd-zone" data-correct="actor-a">
      <p class="dnd-zone-label">角色 A 的描述</p>
      <div class="dnd-zone-target">拖放到这里</div>
    </div>
    <!-- 更多区域 -->
  </div>
  <button onclick="checkDnD('dnd-module2')">检查匹配</button>
  <button onclick="resetDnD('dnd-module2')">重置</button>
</div>
```

---

## 群聊动画

iMessage/微信风格的聊天，显示组件之间"对话"。消息逐一出现，带打字指示器。

**连接：** `main.js` 在页面加载时自动初始化每个 `.chat-window`。给每个聊天窗口一个唯一的 `id`。控制按钮需要这些类：`.chat-next-btn`、`.chat-all-btn`、`.chat-reset-btn`。打字指示器头像元素应该有 `id="{chatWindowId}-typing-avatar"`，或者简单的是 `.chat-typing` 内的第一个 `.chat-avatar`。

**HTML：**
```html
<div class="chat-window" id="chat-module2">
  <div class="chat-messages">
    <div class="chat-message" data-msg="0" data-sender="actor-a" style="display:none">
      <div class="chat-avatar" style="background: var(--color-actor-1)">A</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-1)">角色 A</span>
        <p>嘿后台，我需要这个项目的数据。</p>
      </div>
    </div>
    <!-- 更多消息... -->
  </div>

  <div class="chat-typing" id="chat-typing" style="display:none">
    <div class="chat-avatar" id="typing-avatar">?</div>
    <div class="chat-typing-dots">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  </div>

  <div class="chat-controls">
    <button class="btn chat-next-btn">下一条消息</button>
    <button class="btn chat-all-btn">播放全部</button>
    <button class="btn chat-reset-btn">重播</button>
    <span class="chat-progress"></span>
  </div>
</div>
```

---

## 消息流/数据流动画

组件之间数据移动的逐步可视化。用户点击"下一步"前进。

**连接：** `main.js` 在页面加载时自动初始化每个 `.flow-animation`。通过 `data-steps` 传递 JSON 作为步骤。每个步骤对象：`{ highlight: "flow-actor-id", label: "描述", packet: true, from: "actor-id-suffix", to: "actor-id-suffix" }`。角色元素 ID 必须是 `flow-actor-1`、`flow-actor-2` 等。控制按钮需要类 `.flow-next-btn` 和 `.flow-reset-btn`。

> **⚠️ 步骤标签中的单引号会破坏解析。** `data-steps` 属性由单引号分隔（`data-steps='[...]'`），所以标签内的任何单引号（例如 `"the user's request"`）会提前终止属性，导致 `JSON.parse` 静默失败——整个动画将停止工作。避免标签中的撇号，用 `&apos;` 替换它们，或使用双引号分隔符和转义内部引号重写属性（`data-steps="[{\"label\":\"...\"}]"`）。

**HTML：**
```html
<div class="flow-animation" data-steps='[
  {"highlight":"flow-actor-1","label":"用户点击按钮"},
  {"highlight":"flow-actor-1","label":"前端发送请求","packet":true,"from":"actor-1","to":"actor-2"},
  {"highlight":"flow-actor-2","label":"后端调用数据库","packet":true,"from":"actor-2","to":"actor-3"}
]'>
  <div class="flow-actors">
    <div class="flow-actor" id="flow-actor-1">
      <div class="flow-actor-icon">A</div>
      <span>角色 1</span>
    </div>
    <div class="flow-actor" id="flow-actor-2">
      <div class="flow-actor-icon">B</div>
      <span>角色 2</span>
    </div>
    <div class="flow-actor" id="flow-actor-3">
      <div class="flow-actor-icon">C</div>
      <span>角色 3</span>
    </div>
  </div>

  <div class="flow-packet" id="flow-packet"></div>

  <div class="flow-step-label" id="flow-label">点击"下一步"开始</div>

  <div class="flow-controls">
    <button class="btn flow-next-btn">下一步</button>
    <button class="btn flow-reset-btn">重新开始</button>
    <span class="flow-progress"></span>
  </div>
</div>
```

---

## 交互式架构图

悬停/点击组件显示描述提示的完整系统图。

**HTML：**
```html
<div class="arch-diagram">
  <div class="arch-zone arch-zone-browser">
    <h4 class="arch-zone-label">浏览器</h4>
    <div class="arch-component" data-desc="将 UI 注入网页，读取 DOM，捕获用户操作"
         onclick="showArchDesc(this)">
      <div class="arch-icon">📄</div>
      <span>组件 A</span>
    </div>
    <!-- 更多组件 -->
  </div>
  <div class="arch-zone arch-zone-external">
    <h4 class="arch-zone-label">外部服务</h4>
    <!-- API 卡片 -->
  </div>
  <div class="arch-description" id="arch-desc">点击任何组件了解其功能</div>
</div>
```

---

## 层切换演示

显示不同层（例如 HTML/CSS/JS，或数据/逻辑/UI）如何相互构建。三个标签在视图之间切换。

**HTML：**
```html
<div class="layer-demo">
  <div class="layer-tabs">
    <button class="layer-tab active" onclick="showLayer('html', this)">HTML</button>
    <button class="layer-tab" onclick="showLayer('css', this)">+ CSS</button>
    <button class="layer-tab" onclick="showLayer('js', this)">+ JS</button>
  </div>
  <div class="layer-viewport">
    <div class="layer" id="layer-html" style="display:block">
      <!-- 原始无样式版本 -->
    </div>
    <div class="layer" id="layer-css" style="display:none">
      <!-- 样式化版本 -->
    </div>
    <div class="layer" id="layer-js" style="display:none">
      <!-- 交互版本 -->
    </div>
  </div>
  <p class="layer-description" id="layer-desc">这是原始 HTML...</p>
</div>
```

---

## "找 Bug"挑战

显示带有故意 bug 的代码。用户点击有 bug 的行。揭示解释问题。

**HTML：**
```html
<div class="bug-challenge">
  <h3>找出这段代码中的 bug：</h3>
  <div class="bug-code">
    <div class="bug-line" data-line="1" onclick="checkBugLine(this, false)">
      <span class="line-num">1</span>
      <code>chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {</code>
    </div>
    <div class="bug-line" data-line="2" onclick="checkBugLine(this, false)">
      <span class="line-num">2</span>
      <code>  if (msg.action === 'fetchData') {</code>
    </div>
    <div class="bug-line bug-target" data-line="3" onclick="checkBugLine(this, true)"
         data-explanation="监听器使用异步操作（fetch）但不返回 true。Chrome 在响应发送之前关闭消息通道。">
      <span class="line-num">3</span>
      <code>    fetch(url).then(r => r.json()).then(data => sendResponse(data));</code>
    </div>
    <div class="bug-line" data-line="4" onclick="checkBugLine(this, false)">
      <span class="line-num">4</span>
      <code>  }</code>
    </div>
    <div class="bug-line" data-line="5" onclick="checkBugLine(this, false)">
      <span class="line-num">5</span>
      <code>});</code>
    </div>
  </div>
  <div class="bug-feedback" id="bug-feedback"></div>
</div>
```

---

## 场景测验

"高级工程师会怎么做？"——情境问题与解释。

与多项选择测验相同的 HTML/CSS/JS 模式，但带有更长的场景描述和更详细的解释。将每个问题包装在场景上下文块中：

```html
<div class="scenario-block">
  <div class="scenario-context">
    <span class="scenario-label">场景</span>
    <p>你的应用处理一个 3 小时的播客转录。API 有 16,000 个 token 的限制。你怎么做？</p>
  </div>
  <!-- quiz-options 在这里 -->
</div>
```

---

## 提示框

"啊哈！"时刻——通用计算机科学见解。每个模块最多 2 个。

```html
<div class="callout callout-accent">
  <div class="callout-icon">💡</div>
  <div class="callout-content">
    <strong class="callout-title">关键见解</strong>
    <p>这个模式——将职责分离到专注的角色中——是软件工程中最重要的想法之一。工程师称之为"关注点分离"。</p>
  </div>
</div>
```

**变体：**
- `callout-accent`：朱红色左边框，浅强调色背景（用于计算机科学见解）
- `callout-info`：青色左边框，浅信息背景（用于"好知道吗"）
- `callout-warning`：红色左边框，浅错误背景（用于常见错误）

---

## 模式/功能卡片

突出工程模式、技术栈组件或关键概念的卡片网格。

```html
<div class="pattern-cards">
  <div class="pattern-card" style="border-top: 3px solid var(--color-actor-1)">
    <div class="pattern-icon" style="background: var(--color-actor-1)">🔄</div>
    <h4 class="pattern-title">缓存</h4>
    <p class="pattern-desc">存储结果以避免冗余工作——就像保留剩菜而不是每次都重新做饭一样。</p>
  </div>
  <!-- 更多卡片 -->
</div>
```

---

## 流程图

**水平流程（桌面）：**
```html
<div class="flow-steps">
  <div class="flow-step">
    <div class="flow-step-num">1</div>
    <p>用户点击按钮</p>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="flow-step-num">2</div>
    <p>组件 A 检测到点击</p>
  </div>
  <div class="flow-arrow">→</div>
  <!-- 更多步骤 -->
</div>
```

在移动端，箭头通过 CSS 变换旋转为 `↓`。

---

## 权限/配置徽章

用于注释配置文件、权限或设置：

```html
<div class="badge-list">
  <div class="badge-item">
    <code class="badge-code">storage</code>
    <span class="badge-desc">在会话之间保存数据（就像浏览器书签一样）</span>
  </div>
  <div class="badge-item">
    <code class="badge-code">activeTab</code>
    <span class="badge-desc">访问当前打开的标签页（仅在用户点击时）</span>
  </div>
</div>
```

---

## 术语提示

非技术学习者最重要的可访问性功能。课程文本中的任何技术术语都应该被包装在一个提示中，在悬停（桌面）或点击（移动）时显示通俗英文定义。学习者永远不必离开页面或搜索任何东西。

**HTML——内联标记术语：**
```html
<p>扩展使用
  <span class="term" data-definition="服务工作者是在网页后台独立运行的脚本——就像一个幕后助手，始终在线，即使你不看页面。">service worker</span>
  来处理 API 调用。
</p>
```

**规则：**
- 在每个模块的首次使用时标记每个技术术语（API、DOM、callback、async、endpoint、middleware 等）
- 将定义保持在最多 1-2 句话，用日常语言
- 在定义中使用隐喻当它有帮助时——例如，"**回调**就像在餐厅留下你的电话号码，这样他们准备好时可以打电话通知你"
- 不要在同一屏幕内对同一术语标记两次——只在每个模块的首次出现时标记
- 虚线下划线应该足够微妙以免分心，但也要足够明显，以便好奇的学习者发现它

---

## 可视化文件树

用它代替列出"这个文件夹做 X，那个文件夹做 Y"的段落。更容易扫描。

```html
<div class="file-tree">
  <div class="ft-folder open">
    <span class="ft-name">app/</span>
    <span class="ft-desc">页面和 API 路由</span>
    <div class="ft-children">
      <div class="ft-folder">
        <span class="ft-name">api/</span>
        <span class="ft-desc">前端调用的后端端点</span>
      </div>
      <div class="ft-file">
        <span class="ft-name">layout.tsx</span>
        <span class="ft-desc">包装每个页面的外壳</span>
      </div>
    </div>
  </div>
  <div class="ft-folder">
    <span class="ft-name">components/</span>
    <span class="ft-desc">可复用的 UI 构建块</span>
  </div>
  <div class="ft-folder">
    <span class="ft-name">lib/</span>
    <span class="ft-desc">共享逻辑和工具</span>
  </div>
</div>
```

---

## 图标标签行

用于视觉列出组件、功能或概念。取代要点段落。

```html
<div class="icon-rows">
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-1)">🖥️</div>
    <div>
      <strong>前端 (Next.js)</strong>
      <p>用户看到并与之交互的内容</p>
    </div>
  </div>
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-2)">⚡</div>
    <div>
      <strong>API 路由</strong>
      <p>在服务器上运行的后端逻辑</p>
    </div>
  </div>
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-3)">🗄️</div>
    <div>
      <strong>数据库 (Supabase)</strong>
      <p>所有数据永久存储的地方</p>
    </div>
  </div>
</div>
```

---

## 编号步骤卡片

用于否则会成为编号段落列表的序列。视觉化、可扫描，每个步骤独立。

```html
<div class="step-cards">
  <div class="step-card">
    <div class="step-num">1</div>
    <div class="step-body">
      <strong>用户粘贴 YouTube URL</strong>
      <p>前端捕获 URL 并提取视频 ID</p>
    </div>
  </div>
  <div class="step-card">
    <div class="step-num">2</div>
    <div class="step-body">
      <strong>API 获取转录</strong>
      <p>服务器端路由调用外部服务获取视频文本</p>
    </div>
  </div>
  <div class="step-card">
    <div class="step-num">3</div>
    <div class="step-body">
      <strong>AI 分析内容</strong>
      <p>转录被发送到 AI 模型，提取关键时刻</p>
    </div>
  </div>
</div>
```
