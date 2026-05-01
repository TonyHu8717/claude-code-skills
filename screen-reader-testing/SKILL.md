---
name: screen-reader-testing
description: 使用屏幕阅读器（包括 VoiceOver、NVDA 和 JAWS）测试 Web 应用程序。在验证屏幕阅读器兼容性、调试辅助功能问题或确保辅助技术支持时使用。
---

# 屏幕阅读器测试

使用屏幕阅读器测试 Web 应用程序的实用指南，用于综合辅助功能验证。

## 何时使用此技能

- 验证屏幕阅读器兼容性
- 测试 ARIA 实现
- 调试辅助技术问题
- 验证表单辅助功能
- 测试动态内容公告
- 确保导航辅助功能

## 核心概念

### 1. 主要屏幕阅读器

| 屏幕阅读器    | 平台      | 浏览器         | 使用率 |
| ------------- | --------- | -------------- | ------ |
| **VoiceOver** | macOS/iOS | Safari         | ~15%   |
| **NVDA**      | Windows   | Firefox/Chrome | ~31%   |
| **JAWS**      | Windows   | Chrome/IE      | ~40%   |
| **TalkBack**  | Android   | Chrome         | ~10%   |
| **Narrator**  | Windows   | Edge           | ~4%    |

### 2. 测试优先级

```
最低覆盖：
1. NVDA + Firefox（Windows）
2. VoiceOver + Safari（macOS）
3. VoiceOver + Safari（iOS）

综合覆盖：
+ JAWS + Chrome（Windows）
+ TalkBack + Chrome（Android）
+ Narrator + Edge（Windows）
```

### 3. 屏幕阅读器模式

| 模式               | 用途                | 使用场景         |
| ------------------ | ------------------- | ---------------- |
| **Browse/Virtual** | 阅读内容            | 默认阅读         |
| **Focus/Forms**    | 与控件交互          | 填写表单         |
| **Application**    | 自定义小部件        | ARIA 应用        |

## VoiceOver（macOS）

### 设置

```
启用：系统偏好设置 → 辅助功能 → VoiceOver
切换：Cmd + F5
快速切换：三次按 Touch ID
```

### 基本命令

```
导航：
VO = Ctrl + Option（VoiceOver 修饰键）

VO + 右箭头        下一个元素
VO + 左箭头        上一个元素
VO + Shift + 下    进入组
VO + Shift + 上    退出组

阅读：
VO + A             从光标位置全部朗读
Ctrl               停止朗读
VO + B             朗读当前段落

交互：
VO + Space         激活元素
VO + Shift + M     打开菜单
Tab                下一个可聚焦元素
Shift + Tab        上一个可聚焦元素

转子（VO + U）：
导航方式：标题、链接、表单、地标
左/右箭头          更改转子类别
上/下箭头          在类别内导航
Enter              跳转到项目

Web 特定：
VO + Cmd + H       下一个标题
VO + Cmd + J       下一个表单控件
VO + Cmd + L       下一个链接
VO + Cmd + T       下一个表格
```

### 测试检查清单

```markdown
## VoiceOver 测试检查清单

### 页面加载

- [ ] 页面标题已公告
- [ ] 找到主地标
- [ ] 跳转链接有效

### 导航

- [ ] 所有标题可通过转子发现
- [ ] 标题级别逻辑正确（H1 → H2 → H3）
- [ ] 地标正确标记
- [ ] 跳转链接功能正常

### 链接和按钮

- [ ] 链接目的清晰
- [ ] 按钮操作已描述
- [ ] 新窗口/标签页已公告

### 表单

- [ ] 所有标签与输入关联朗读
- [ ] 必填字段已公告
- [ ] 错误消息已朗读
- [ ] 说明可用
- [ ] 焦点移动到错误处

### 动态内容

- [ ] 警报立即公告
- [ ] 加载状态已传达
- [ ] 内容更新已公告
- [ ] 模态框正确捕获焦点

### 表格

- [ ] 标题与单元格关联
- [ ] 表格导航有效
- [ ] 复杂表格有标题
```

### 常见问题和修复

```html
<!-- 问题：按钮未公告用途 -->
<button><svg>...</svg></button>

<!-- 修复 -->
<button aria-label="关闭对话框"><svg aria-hidden="true">...</svg></button>

<!-- 问题：动态内容未公告 -->
<div id="results">已加载新结果</div>

<!-- 修复 -->
<div id="results" role="status" aria-live="polite">已加载新结果</div>

<!-- 问题：表单错误未朗读 -->
<input type="email" />
<span class="error">无效邮箱</span>

<!-- 修复 -->
<input type="email" aria-invalid="true" aria-describedby="email-error" />
<span id="email-error" role="alert">无效邮箱</span>
```

## NVDA（Windows）

### 设置

```
下载：nvaccess.org
启动：Ctrl + Alt + N
停止：Insert + Q
```

### 基本命令

```
导航：
Insert = NVDA 修饰键

下箭头             下一行
上箭头             上一行
Tab                下一个可聚焦元素
Shift + Tab        上一个可聚焦元素

阅读：
NVDA + 下箭头      全部朗读
Ctrl               停止朗读
NVDA + 上箭头      当前行

标题：
H                  下一个标题
Shift + H          上一个标题
1-6                标题级别 1-6

表单：
F                  下一个表单字段
B                  下一个按钮
E                  下一个编辑字段
X                  下一个复选框
C                  下一个组合框

链接：
K                  下一个链接
U                  下一个未访问链接
V                  下一个已访问链接

地标：
D                  下一个地标
Shift + D          上一个地标

表格：
T                  下一个表格
Ctrl + Alt + 箭头  导航单元格

元素列表（NVDA + F7）：
显示所有链接、标题、表单字段、地标
```

### 浏览模式 vs 焦点模式

```
NVDA 自动切换模式：
- 浏览模式：箭头键导航内容
- 焦点模式：箭头键控制交互元素

手动切换：NVDA + Space

注意：
- 导航时听到"浏览模式"公告
- 进入表单字段时听到"焦点模式"
- application 角色强制表单模式
```

### 测试脚本

```markdown
## NVDA 测试脚本

### 初始加载

1. 导航到页面
2. 等待页面加载完成
3. 按 Insert + Down 全部朗读
4. 注意：页面标题、主内容是否已识别？

### 地标导航

1. 反复按 D
2. 检查：所有主要区域可达？
3. 检查：地标正确标记？

### 标题导航

1. 按 Insert + F7 → 标题
2. 检查：标题结构逻辑正确？
3. 按 H 导航标题
4. 检查：所有部分可发现？

### 表单测试

1. 按 F 查找第一个表单字段
2. 检查：标签已朗读？
3. 填写无效数据
4. 提交表单
5. 检查：错误已公告？
6. 检查：焦点移动到错误处？

### 交互元素

1. Tab 遍历所有交互元素
2. 检查：每个都公告角色和状态
3. 用 Enter/Space 激活按钮
4. 检查：结果已公告？

### 动态内容

1. 触发内容更新
2. 检查：变更已公告？
3. 打开模态框
4. 检查：焦点被捕获？
5. 关闭模态框
6. 检查：焦点返回？
```

## JAWS（Windows）

### 基本命令

```
启动：桌面快捷方式或 Ctrl + Alt + J
虚拟光标：在浏览器中自动启用

导航：
箭头键             导航内容
Tab                下一个可聚焦元素
Insert + Down      全部朗读
Ctrl               停止朗读

快捷键：
H                  下一个标题
T                  下一个表格
F                  下一个表单字段
B                  下一个按钮
G                  下一个图形
L                  下一个列表
;                  下一个地标

表单模式：
Enter              进入表单模式
Numpad +           退出表单模式
F5                 列出表单字段

列表：
Insert + F7        链接列表
Insert + F6        标题列表
Insert + F5        表单字段列表

表格：
Ctrl + Alt + 箭头  表格导航
```

## TalkBack（Android）

### 设置

```
启用：设置 → 辅助功能 → TalkBack
切换：同时按住两个音量键 3 秒
```

### 手势

```
探索：在屏幕上拖动手指
下一个：向右滑动
上一个：向左滑动
激活：双击
滚动：双指滑动

阅读控制（先向上再向右滑动）：
- 标题
- 链接
- 控件
- 字符
- 单词
- 行
- 段落
```

## 常见测试场景

### 1. 模态对话框

```html
<!-- 无障碍模态框结构 -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">确认删除</h2>
  <p id="dialog-desc">此操作无法撤销。</p>
  <button>取消</button>
  <button>删除</button>
</div>
```

```javascript
// 焦点管理
function openModal(modal) {
  // 存储最后聚焦的元素
  lastFocus = document.activeElement;

  // 将焦点移到模态框
  modal.querySelector("h2").focus();

  // 捕获焦点
  modal.addEventListener("keydown", trapFocus);
}

function closeModal(modal) {
  // 返回焦点
  lastFocus.focus();
}

function trapFocus(e) {
  if (e.key === "Tab") {
    const focusable = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      last.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === last) {
      first.focus();
      e.preventDefault();
    }
  }

  if (e.key === "Escape") {
    closeModal(modal);
  }
}
```

### 2. 实时区域

```html
<!-- 状态消息（礼貌） -->
<div role="status" aria-live="polite" aria-atomic="true">
  <!-- 内容更新将在当前朗读后公告 -->
</div>

<!-- 警报（强制） -->
<div role="alert" aria-live="assertive">
  <!-- 内容更新会打断当前朗读 -->
</div>

<!-- 进度更新 -->
<div
  role="progressbar"
  aria-valuenow="75"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-label="上传进度"
></div>

<!-- 日志（仅添加） -->
<div role="log" aria-live="polite" aria-relevant="additions">
  <!-- 新消息公告，移除不公告 -->
</div>
```

### 3. 标签页界面

```html
<div role="tablist" aria-label="产品信息">
  <button role="tab" id="tab-1" aria-selected="true" aria-controls="panel-1">
    描述
  </button>
  <button
    role="tab"
    id="tab-2"
    aria-selected="false"
    aria-controls="panel-2"
    tabindex="-1"
  >
    评价
  </button>
</div>

<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  产品描述内容...
</div>

<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
  评价内容...
</div>
```

```javascript
// 标签页键盘导航
tablist.addEventListener("keydown", (e) => {
  const tabs = [...tablist.querySelectorAll('[role="tab"]')];
  const index = tabs.indexOf(document.activeElement);

  let newIndex;
  switch (e.key) {
    case "ArrowRight":
      newIndex = (index + 1) % tabs.length;
      break;
    case "ArrowLeft":
      newIndex = (index - 1 + tabs.length) % tabs.length;
      break;
    case "Home":
      newIndex = 0;
      break;
    case "End":
      newIndex = tabs.length - 1;
      break;
    default:
      return;
  }

  tabs[newIndex].focus();
  activateTab(tabs[newIndex]);
  e.preventDefault();
});
```

## 调试技巧

```javascript
// 记录屏幕阅读器看到的内容
function logAccessibleName(element) {
  const computed = window.getComputedStyle(element);
  console.log({
    role: element.getAttribute("role") || element.tagName,
    name:
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby") ||
      element.textContent,
    state: {
      expanded: element.getAttribute("aria-expanded"),
      selected: element.getAttribute("aria-selected"),
      checked: element.getAttribute("aria-checked"),
      disabled: element.disabled,
    },
    visible: computed.display !== "none" && computed.visibility !== "hidden",
  });
}
```

## 最佳实践

### 应该做的

- **使用真实屏幕阅读器测试** — 不仅仅是模拟器
- **优先使用语义 HTML** — ARIA 是补充
- **在浏览和焦点模式下测试** — 不同的体验
- **验证焦点管理** — 特别是对于 SPA
- **先测试纯键盘** — 屏幕阅读器测试的基础

### 不应该做的

- **不要假设一种屏幕阅读器足够** — 测试多种
- **不要忽略移动端** — 用户群在增长
- **不要只测试快乐路径** — 测试错误状态
- **不要跳过动态内容** — 最常见的问题
- **不要依赖视觉测试** — 不同的体验
