---
name: 中文教程索引更新
description: |
  遍历 .\中文教程\ 下所有课程，生成或更新教程索引页。只在有新教程加入时才重新生成索引 HTML，纯内容更新不触发重建。触发词：更新教程索引、重建教程索引、教程索引更新、刷新索引、index tutorials、教程导航。
---

# 中文教程索引更新

维护 `.\中文教程\index.html` — 一个美观的中文导航页，汇集所有已生成的交互式教程。

## 核心原则

- **仅在新教程加入时重建** — 扫描所有 `index.html`，与 manifest 对比。只有出现新路径（之前未记录的教程）才重新生成索引 HTML。纯内容更新（manifest 中已有路径的时间戳变化）不触发重建。
- **索引以中文呈现** — 所有分类名、描述、导航文字均为中文。
- **每个教程有概要描述** — 从教程的 `<title>` 或 `<span class="nav-title">` 中提取标题，并结合路径和模块信息生成一句话中文概要。

## 工作流程

### 步骤 1：扫描教程

遍历 `.\中文教程\` 下所有名为 `index.html` 的文件（排除 `.\中文教程\index.html` 自身）。

```powershell
Get-ChildItem -Path ".\中文教程" -Recurse -Filter "index.html" -Depth 10 |
  Where-Object { $_.FullName -ne ".\中文教程\index.html" } |
  ForEach-Object { ... }
```

对每个教程文件，提取：
- **相对路径**：相对于 `.\中文教程\` 的路径（如 `ai-study/01-ollama/index.html`）
- **标题**：从 `<title>` 标签内容提取；若为空则从 `<span class="nav-title">` 提取
- **分类**：路径第一级目录名（`aaos`、`ai-study`、`SmartPerfetto`、`study`）
- **最后修改时间**：文件的 `LastWriteTime`
- **模块数**：`nav-dot` 按钮的数量（`data-tooltip` 属性给出模块名）
- **语言**：`<html lang="...">` 属性值

### 步骤 2：对比 Manifest

读取 `.\中文教程\.index-manifest.json`。

对比扫描结果与 manifest：
- 扫描到的路径集合 vs manifest 中记录的路径集合
- **如果出现了新路径**（扫描到但 manifest 中没有的教程）→ 需要重建索引
- **如果路径集合完全一致**（只是时间戳变化或无变化）→ 跳过，报告无需更新

### 步骤 3：生成索引（仅在需要时）

基于参考模板 `references/index-template.html` 生成 `.\中文教程\index.html`。

**生成规则：**

1. **分类排序**：按以下固定顺序排列分类区块：
   - AI 学习（`ai-study`）
   - 通用学习（`study`）
   - AAOS 源码（`aaos`）
   - 性能工具（`SmartPerfetto`）
   - 其他分类按字母序排在后面

2. **分类中文名映射**：
   | 路径分类 | 中文名 | 图标 |
   |----------|--------|------|
   | `ai-study` | AI 学习 | 🤖 |
   | `study` | 通用学习 | 📚 |
   | `aaos` | AAOS 源码 | 🚗 |
   | `SmartPerfetto` | 性能工具 | 📊 |

3. **教程卡片**：每个教程生成一个卡片，包含：
   - 教程标题（从 `<title>` 提取）
   - 一句话描述（从标题的副标题部分（`—` 之后）提取，或根据模块名生成）
   - 模块数量标签
   - 链接到 `{相对路径}`（相对于索引页的路径）
   - 颜色标记：根据教程自身的 `--color-accent` 颜色

4. **嵌套教程处理**：如果教程路径深度 > 2（如 `aaos/frameworks/native/services/surfaceflinger/index.html`），在卡片上显示完整路径面包屑。

5. **统计摘要**：页面顶部显示：
   - 教程总数
   - 最后更新时间
   - 分类分布

### 步骤 4：更新 Manifest

将扫描结果写入 `.\中文教程\.index-manifest.json`：

```json
{
  "generatedAt": "2026-05-06T20:30:00+08:00",
  "totalCount": 39,
  "tutorials": {
    "ai-study/01-ollama/index.html": {
      "title": "Ollama 从内到外",
      "category": "ai-study",
      "lastModified": "2026-05-06T12:00:00",
      "moduleCount": 5,
      "lang": "en"
    }
  }
}
```

### 步骤 5：报告

向用户报告：
- 是否进行了重建
- 教程总数和分类分布
- 新增的教程（如果有）
- 索引文件路径：`.\中文教程\index.html`

## 设计风格

索引页应与教程风格一致：
- 温暖色调：米白色背景，暖灰色文字
- 大胆强调色：teal（`#2A7B9B`）作为主色调
- 字体：Bricolage Grotesque（标题）、DM Sans（正文）
- 卡片式布局：教程卡片带有微妙的阴影和圆角
- 响应式：桌面端 3-4 列，平板 2 列，手机 1 列

## 参考文件

- `references/index-template.html` — 索引页 HTML 模板，按需读取
