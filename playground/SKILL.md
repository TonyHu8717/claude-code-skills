---
name: playground
description: 创建交互式 HTML 游乐场 — 自包含的单文件探索器，让用户通过控件进行视觉配置、查看实时预览，并复制输出提示。当用户要求为某个主题制作游乐场、探索器或交互式工具时使用。
---

# 游乐场构建器

游乐场是一个自包含的 HTML 文件，一侧是交互式控件，另一侧是实时预览，底部是提示输出和复制按钮。用户调整控件、进行视觉探索，然后将生成的提示复制回 Claude。

## 何时使用此技能

当用户要求为某个主题创建交互式游乐场、探索器或视觉工具时 — 尤其是当输入空间很大、具有视觉性或结构性，难以用纯文本表达时。

## 如何使用此技能

1. **确定游乐场类型**，根据用户的请求
2. **加载匹配的模板**，从 `templates/` 目录：
   - `templates/design-playground.md` — 视觉设计决策（组件、布局、间距、颜色、排版）
   - `templates/data-explorer.md` — 数据和查询构建（SQL、API、管道、正则表达式）
   - `templates/concept-map.md` — 学习和探索（概念图、知识缺口、范围映射）
   - `templates/document-critique.md` — 文档审查（带批准/拒绝/评论工作流的建议）
   - `templates/diff-review.md` — 代码审查（git 差异、提交、PR，带逐行评论）
   - `templates/code-map.md` — 代码库架构（组件关系、数据流、层次图）
3. **按照模板**构建游乐场。如果主题与任何模板都不完全匹配，使用最接近的模板并进行调整。
4. **在浏览器中打开。** 写入 HTML 文件后，运行 `open <filename>.html` 在用户默认浏览器中打开。

## 核心要求（每个游乐场）

- **单个 HTML 文件。** 内联所有 CSS 和 JS。无外部依赖。
- **实时预览。** 每次控件更改时立即更新。不需要"应用"按钮。
- **提示输出。** 自然语言，不是值的转储。仅提及非默认选择。包含足够的上下文以便在不查看游乐场的情况下执行。实时更新。
- **复制按钮。** 剪贴板复制，带简短的"已复制！"反馈。
- **合理的默认值 + 预设。** 首次加载时看起来不错。包含 3-5 个命名预设，将所有控件设置为有凝聚力的组合。
- **深色主题。** UI 使用系统字体，代码/值使用等宽字体。最小化装饰。

## 状态管理模式

保持单个状态对象。每个控件写入它，每个渲染读取它。

```javascript
const state = { /* 所有可配置的值 */ };

function updateAll() {
  renderPreview(); // 更新视觉效果
  updatePrompt();  // 重建提示文本
}
// 每个控件在更改时调用 updateAll()
```

## 提示输出模式

```javascript
function updatePrompt() {
  const parts = [];

  // 仅提及非默认值
  if (state.borderRadius !== DEFAULTS.borderRadius) {
    parts.push(`border-radius of ${state.borderRadius}px`);
  }

  // 在数字旁使用定性语言
  if (state.shadowBlur > 16) parts.push('a pronounced shadow');
  else if (state.shadowBlur > 0) parts.push('a subtle shadow');

  prompt.textContent = `Update the card to use ${parts.join(', ')}.`;
}
```

## 应避免的常见错误

- 提示输出只是值的转储 → 将其写为自然指令
- 一次控件太多 → 按关注点分组，将高级选项隐藏在可折叠部分中
- 预览不立即更新 → 每次控件更改必须触发立即重新渲染
- 没有默认值或预设 → 首次加载时为空或损坏
- 外部依赖 → 如果 CDN 宕机，游乐场就无法使用
- 提示缺少上下文 → 包含足够的信息以便在没有游乐场的情况下可执行
