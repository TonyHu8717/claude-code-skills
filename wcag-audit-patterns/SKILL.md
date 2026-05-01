---
name: wcag-audit-patterns
description: 使用自动化测试、手动验证和修复指导进行 WCAG 2.2 无障碍审计。适用于审计网站无障碍性、修复 WCAG 违规或实现无障碍设计模式。
---

# WCAG 审计模式

根据 WCAG 2.2 指南审计 Web 内容并提供可操作修复策略的综合指南。

## 何时使用此技能

- 进行无障碍审计
- 修复 WCAG 违规
- 实现无障碍组件
- 为无障碍诉讼做准备
- 满足 ADA/Section 508 要求
- 实现 VPAT 合规

## 核心概念

### 1. WCAG 合规等级

| 等级   | 描述            | 适用场景      |
| ------- | ---------------------- | ----------------- |
| **A**   | 最低无障碍性  | 法律基线    |
| **AA**  | 标准合规   | 大多数法规  |
| **AAA** | 增强无障碍性 |  specialized needs |

### 2. POUR 原则

```
可感知:  用户能否感知内容？
可操作:     用户能否操作界面？
可理解: 用户能否理解内容？
健壮:       是否能与辅助技术配合工作？
```

### 3. 按影响分类的常见违规

```
严重（阻塞）：
├── 功能图片缺少 alt 文本
├── 交互元素无键盘访问
├── 表单缺少标签
└── 自动播放媒体无控件

重大：
├── 颜色对比度不足
├── 缺少跳转链接
├── 不可访问的自定义组件
└── 缺少页面标题

中等：
├── 缺少语言属性
├── 不清晰的链接文本
├── 缺少地标
└── 不当的标题层次
```

## 审计检查清单

### 可感知（原则 1）

````markdown
## 1.1 文本替代

### 1.1.1 非文本内容（A 级）

- [ ] 所有图片有 alt 文本
- [ ] 装饰性图片有 alt=""
- [ ] 复杂图片有长描述
- [ ] 有意义的图标有无障碍名称
- [ ] CAPTCHA 有替代方案

检查：

```html
<!-- 好 -->
<img src="chart.png" alt="Sales increased 25% from Q1 to Q2" />
<img src="decorative-line.png" alt="" />

<!-- 差 -->
<img src="chart.png" />
<img src="decorative-line.png" alt="decorative line" />
```
````

## 1.2 基于时间的媒体

### 1.2.1 仅音频和仅视频（A 级）

- [ ] 音频有文本转录
- [ ] 视频有音频描述或转录

### 1.2.2 字幕（A 级）

- [ ] 所有视频有同步字幕
- [ ] 字幕准确且完整
- [ ] 包含说话人标识

### 1.2.3 音频描述（A 级）

- [ ] 视频有视觉内容的音频描述

## 1.3 可适配

### 1.3.1 信息和关系（A 级）

- [ ] 标题使用正确的标签（h1-h6）
- [ ] 列表使用 ul/ol/dl
- [ ] 表格有表头
- [ ] 表单输入有标签
- [ ] 存在 ARIA 地标

检查：

```html
<!-- 标题层次 -->
<h1>Page Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>
<h2>Another Section</h2>

<!-- 表格表头 -->
<table>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Price</th>
    </tr>
  </thead>
</table>
```

### 1.3.2 有意义的序列（A 级）

- [ ] 阅读顺序是逻辑的
- [ ] CSS 定位不破坏顺序
- [ ] 焦点顺序与视觉顺序匹配

### 1.3.3 感官特征（A 级）

- [ ] 说明不依赖形状/颜色
- "点击红色按钮" → "点击提交（红色按钮）"

## 1.4 可辨别

### 1.4.1 颜色使用（A 级）

- [ ] 颜色不是传达信息的唯一方式
- [ ] 链接无需颜色即可区分
- [ ] 错误状态不仅依赖颜色

### 1.4.3 对比度（最小值）（AA 级）

- [ ] 文本：4.5:1 对比度比率
- [ ] 大文本（18pt+）：3:1 比率
- [ ] UI 组件：3:1 比率

工具：WebAIM Contrast Checker、axe DevTools

### 1.4.4 调整文本大小（AA 级）

- [ ] 文本可调整到 200% 而不丢失
- [ ] 320px 时无水平滚动
- [ ] 内容正确回流

### 1.4.10 回流（AA 级）

- [ ] 400% 缩放时内容回流
- [ ] 无二维滚动
- [ ] 320px 宽度下所有内容可访问

### 1.4.11 非文本对比度（AA 级）

- [ ] UI 组件有 3:1 对比度
- [ ] 焦点指示器可见
- [ ] 图形对象可辨别

### 1.4.12 文本间距（AA 级）

- [ ] 增加间距时无内容丢失
- [ ] 行高 1.5 倍字体大小
- [ ] 段落间距 2 倍字体大小
- [ ] 字间距 0.12 倍字体大小
- [ ] 词间距 0.16 倍字体大小

````

### 可操作（原则 2）

```markdown
## 2.1 键盘可访问

### 2.1.1 键盘（A 级）
- [ ] 所有功能键盘可访问
- [ ] 无键盘陷阱
- [ ] Tab 顺序逻辑
- [ ] 自定义组件键盘可操作

检查：
```javascript
// 自定义按钮必须键盘可访问
<div role="button" tabindex="0"
     onkeydown="if(event.key === 'Enter' || event.key === ' ') activate()">
````

### 2.1.2 无键盘陷阱（A 级）

- [ ] 焦点可以从所有组件移开
- [ ] 模态对话框正确捕获焦点
- [ ] 模态关闭后焦点返回

## 2.2 充足时间

### 2.2.1 时间可调（A 级）

- [ ] 会话超时可延长
- [ ] 超时前警告用户
- [ ] 可禁用自动刷新

### 2.2.2 暂停、停止、隐藏（A 级）

- [ ] 移动内容可暂停
- [ ] 自动更新内容可暂停
- [ ] 动画尊重 prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

## 2.3 癫痫和身体反应

### 2.3.1 三次闪烁（A 级）

- [ ] 内容每秒闪烁不超过 3 次
- [ ] 闪烁区域小（<25% 视口）

## 2.4 可导航

### 2.4.1 跳过区块（A 级）

- [ ] 存在跳转到主内容的链接
- [ ] 定义了地标区域
- [ ] 正确的标题结构

```html
<a href="#main" class="skip-link">Skip to main content</a>
<main id="main">...</main>
```

### 2.4.2 页面标题（A 级）

- [ ] 唯一、描述性的页面标题
- [ ] 标题反映页面内容

### 2.4.3 焦点顺序（A 级）

- [ ] 焦点顺序与视觉顺序匹配
- [ ] 正确使用 tabindex

### 2.4.4 链接目的（上下文中）（A 级）

- [ ] 链接在上下文外有意义
- [ ] 不要单独使用"点击这里"或"阅读更多"

```html
<!-- 差 -->
<a href="report.pdf">Click here</a>

<!-- 好 -->
<a href="report.pdf">Download Q4 Sales Report (PDF)</a>
```

### 2.4.6 标题和标签（AA 级）

- [ ] 标题描述内容
- [ ] 标签描述用途

### 2.4.7 焦点可见（AA 级）

- [ ] 所有元素上焦点指示器可见
- [ ] 自定义焦点样式满足对比度

```css
:focus {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
}
```

### 2.4.11 焦点不被遮挡（AA 级）- WCAG 2.2

- [ ] 聚焦的元素不被完全隐藏
- [ ] 粘性标题不遮挡焦点

````

### 可理解（原则 3）

```markdown
## 3.1 可读

### 3.1.1 页面语言（A 级）
- [ ] 设置了 HTML lang 属性
- [ ] 语言对内容正确

```html
<html lang="en">
````

### 3.1.2 部分语言（AA 级）

- [ ] 标记了语言变化

```html
<p>The French word <span lang="fr">bonjour</span> means hello.</p>
```

## 3.2 可预测

### 3.2.1 聚焦时（A 级）

- [ ] 仅聚焦时不改变上下文
- [ ] 聚焦时无意外弹出

### 3.2.2 输入时（A 级）

- [ ] 无自动表单提交
- [ ] 上下文变化前警告用户

### 3.2.3 一致的导航（AA 级）

- [ ] 跨页面导航一致
- [ ] 重复组件顺序相同

### 3.2.4 一致的标识（AA 级）

- [ ] 相同功能 = 相同标签
- [ ] 图标使用一致

## 3.3 输入辅助

### 3.3.1 错误识别（A 级）

- [ ] 错误被清晰识别
- [ ] 错误消息描述问题
- [ ] 错误与字段关联

```html
<input aria-describedby="email-error" aria-invalid="true" />
<span id="email-error" role="alert">Please enter valid email</span>
```

### 3.3.2 标签或说明（A 级）

- [ ] 所有输入有可见标签
- [ ] 标记必填字段
- [ ] 提供格式提示

### 3.3.3 错误建议（AA 级）

- [ ] 错误包含纠正建议
- [ ] 建议是具体的

### 3.3.4 错误预防（AA 级）

- [ ] 法律/财务表单可逆
- [ ] 提交前检查数据
- [ ] 用户可在提交前审查

````

### 健壮（原则 4）

```markdown
## 4.1 兼容

### 4.1.1 解析（A 级）- WCAG 2.2 中已废弃
- [ ] 有效的 HTML（良好实践）
- [ ] 无重复 ID
- [ ] 完整的开始/结束标签

### 4.1.2 名称、角色、值（A 级）
- [ ] 自定义组件有无障碍名称
- [ ] ARIA 角色正确
- [ ] 状态变化被公告

```html
<!-- 无障碍自定义复选框 -->
<div role="checkbox"
     aria-checked="false"
     tabindex="0"
     aria-labelledby="label">
</div>
<span id="label">Accept terms</span>
````

### 4.1.3 状态消息（AA 级）

- [ ] 状态更新被公告
- [ ] 正确使用实时区域

```html
<div role="status" aria-live="polite">3 items added to cart</div>

<div role="alert" aria-live="assertive">Error: Form submission failed</div>
```

````

## 自动化测试

```javascript
// axe-core 集成
const axe = require('axe-core');

async function runAccessibilityAudit(page) {
  await page.addScriptTag({ path: require.resolve('axe-core') });

  const results = await page.evaluate(async () => {
    return await axe.run(document, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']
      }
    });
  });

  return {
    violations: results.violations,
    passes: results.passes,
    incomplete: results.incomplete
  };
}

// Playwright 测试示例
test('should have no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await runAccessibilityAudit(page);

  expect(results.violations).toHaveLength(0);
});
````

```bash
# CLI 工具
npx @axe-core/cli https://example.com
npx pa11y https://example.com
lighthouse https://example.com --only-categories=accessibility
```

## 修复模式

### 修复：缺少表单标签

```html
<!-- 之前 -->
<input type="email" placeholder="Email" />

<!-- 之后：选项 1 - 可见标签 -->
<label for="email">Email address</label>
<input id="email" type="email" />

<!-- 之后：选项 2 - aria-label -->
<input type="email" aria-label="Email address" />

<!-- 之后：选项 3 - aria-labelledby -->
<span id="email-label">Email</span>
<input type="email" aria-labelledby="email-label" />
```

### 修复：颜色对比度不足

```css
/* 之前：2.5:1 对比度 */
.text {
  color: #767676;
}

/* 之后：4.5:1 对比度 */
.text {
  color: #595959;
}

/* 或添加背景 */
.text {
  color: #767676;
  background: #000;
}
```

### 修复：键盘导航

```javascript
// 使自定义元素键盘可访问
class AccessibleDropdown extends HTMLElement {
  connectedCallback() {
    this.setAttribute("tabindex", "0");
    this.setAttribute("role", "combobox");
    this.setAttribute("aria-expanded", "false");

    this.addEventListener("keydown", (e) => {
      switch (e.key) {
        case "Enter":
        case " ":
          this.toggle();
          e.preventDefault();
          break;
        case "Escape":
          this.close();
          break;
        case "ArrowDown":
          this.focusNext();
          e.preventDefault();
          break;
        case "ArrowUp":
          this.focusPrevious();
          e.preventDefault();
          break;
      }
    });
  }
}
```

## 最佳实践

### 应该做的

- **尽早开始** - 从设计阶段就考虑无障碍
- **与真实用户测试** - 残障用户提供最好的反馈
- **自动化能自动化的** - 30-50% 的问题可被检测
- **使用语义化 HTML** - 减少 ARIA 需求
- **记录模式** - 构建无障碍组件库

### 不应该做的

- **不要仅依赖自动化测试** - 需要手动测试
- **不要将 ARIA 作为首选方案** - 先用原生 HTML
- **不要隐藏焦点轮廓** - 键盘用户需要它们
- **不要禁用缩放** - 用户需要调整大小
- **不要仅用颜色** - 需要多种指标
