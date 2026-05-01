---
name: ckm:slides
description: 使用 Chart.js、设计 token、响应式布局、文案公式和上下文幻灯片策略创建战略性 HTML 演示文稿。
argument-hint: "[topic] [slide-count]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Slides

带数据可视化的战略性 HTML 演示文稿设计。

<args>$ARGUMENTS</args>

## 何时使用

- 营销演示文稿和推介资料
- 使用 Chart.js 的数据驱动幻灯片
- 使用布局模式的战略性幻灯片设计
- 文案优化的演示内容

## 子命令

| 子命令 | 描述 | 参考 |
|--------|------|------|
| `create` | 创建战略性演示幻灯片 | `references/create.md` |

## 参考（知识库）

| 主题 | 文件 |
|------|------|
| 布局模式 | `references/layout-patterns.md` |
| HTML 模板 | `references/html-template.md` |
| 文案公式 | `references/copywriting-formulas.md` |
| 幻灯片策略 | `references/slide-strategies.md` |

## 路由

1. 从 `$ARGUMENTS`（第一个词）解析子命令
2. 加载对应的 `references/{subcommand}.md`
3. 使用剩余参数执行
