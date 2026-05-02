---
name: ai-papers
description: 获取最近7天国际新发表AI论文，按行业影响力排序Top10，下载原文并翻译为详细中文HTML教程，提取引用论文到专门章节
---

# AI论文猎手

> 追踪最新AI论文，深度翻译解读，提取引用，一站式研究助手。
>
> **核心原则**：所有教程内容使用中文编写（原文引用除外），内容详尽，便于深入阅读理解。

---

## 核心更新要求（2026-05-02）

### 内容语言规范

| 内容类型 | 语言要求 |
|---------|---------|
| 标题 | 中文 + 英文原文 |
| 摘要翻译 | 中文（详细，3-5倍于原文） |
| 介绍/背景 | 中文（详细解读） |
| 方法讲解 | 中文（逐步拆解） |
| 实验分析 | 中文（深入分析） |
| 结论总结 | 中文（全面概括） |
| 原文引用 | 英文（保持原貌） |
| 专业术语 | 中文 + 首次英文原文 |

### 内容详尽度要求

**最低标准：内容量为原文的3倍以上**

- 摘要：原文摘要 200 词 → 中文解读 600-1000 字
- 介绍：原文 500 词 → 中文解读 1500-2500 字
- 方法：原文 1000 词 → 中文解读 3000-5000 字
- 实验：原文 800 词 → 中文解读 2400-4000 字

**解读要素：**
1. **背景铺垫**：为什么要研究这个问题？
2. **问题定义**：论文要解决什么？
3. **核心思想**：用通俗语言解释技术方案
4. **关键创新**：相比之前工作的突破点
5. **技术细节**：逐步拆解核心算法/模型
6. **实验分析**：数据集、指标、结果分析
7. **局限讨论**：论文的不足和未来方向
8. **个人思考**：对研究的评价和应用场景

---

## 目录结构

```
D:/claude/AI论文/
├── 2026-05-02/
│   ├── paper-title-slug/
│   │   ├── paper-title-slug.html    # 详细中文教程
│   │   ├── original.pdf             # 原始PDF
│   │   ├── metadata.json             # 论文元信息
│   │   ├── references/              # 引用论文
│   │   │   ├── cited-paper-1.html
│   │   │   └── ...
│   │   └── notes.md                 # 个人笔记
│   └── index.html                  # 当日论文总览
├── papers-database.jsonl             # 论文数据库
└── search-history.jsonl             # 搜索历史
```

---

## 工作流程

### Step 0: 检查已有论文

处理前先检查 `papers-database.jsonl`，避免重复工作：

```bash
grep "arXiv ID" D:/claude/AI论文/papers-database.jsonl
```

**决策规则：**
- 论文不存在 → 新建处理
- 论文存在但内容简略 → 询问是否更新
- 论文存在且内容详细 → 跳过

---

### Step 1: 搜索最新AI论文

**搜索源（按优先级）：**

1. **arXiv API** — 搜索最近7天的CS.AI/CS.LG/CS.CL/CS.CV
2. **Semantic Scholar** — 获取引用数和影响力评分
3. **Papers with Code** — 热度排名参考

**影响力评估权重：**
- GitHub开源 (+30分)
- 顶会接收 (+25分)
- 高引用作者 (+15分)
- 工业界应用 (+10分)

**筛选条件：**
- 最近7天内发表
- AI相关领域
- 英文论文

---

### Step 2: 下载原文

```bash
# 下载PDF
curl -L -o "original.pdf" "https://arxiv.org/pdf/{arxiv-id}.pdf"

# 检查下载成功（文件大小 > 10KB）
```

同时提取论文元信息：
- 标题、作者、机构
- 发表日期、arXiv ID
- 类别、关键词
- 摘要（用于后续翻译）

---

### Step 3: 生成详细HTML教程

**核心原则：中文详解，保留原文引用**

#### 3.1 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{中文标题} - AI论文解读</title>
    <!-- 统一样式 -->
</head>
<body>
    <!-- 阅读进度条 -->
    <div class="progress-bar" id="progress"></div>

    <header>
        <h1>{中文标题}</h1>
        <p class="subtitle">{英文标题}</p>
        <div class="meta">
            <p><strong>作者：</strong>{作者团队}</p>
            <p><strong>机构：</strong>{所属机构}</p>
            <p><strong>发表：</strong>{日期}</p>
            <p><strong>arXiv：</strong>{ID}</p>
            <p><strong>类别：</strong>{研究领域}</p>
        </div>
        <div class="links">
            <a href="original.pdf" class="btn">下载原文PDF</a>
        </div>
    </header>

    <nav class="toc">
        <h2>目录</h2>
        <ul>
            <li><a href="#overview">论文概览</a></li>
            <li><a href="#background">背景与动机</a></li>
            <li><a href="#problem">问题定义</a></li>
            <li><a href="#method">方法详解</a></li>
            <li><a href="#experiment">实验分析</a></li>
            <li><a href="#conclusion">结论与展望</a></li>
            <li><a href="#references">引用论文</a></li>
            <li><a href="#quiz">理解测验</a></li>
        </ul>
    </nav>

    <main>
        <!-- 各章节详细中文内容 -->
    </main>
</body>
</html>
```

#### 3.2 各章节内容要求

**【论文概览】**
- 一句话概括论文核心贡献
- 研究领域标签
- 与哪些经典工作相关

**【背景与动机】**（中文1500-2500字）
- 这个研究问题为什么重要？
- 之前的工作有哪些不足？
- 本文要解决什么核心矛盾？

**【问题定义】**（中文500-1000字）
- 形式化定义研究问题
- 输入输出是什么？
- 关键约束和假设条件

**【方法详解】**（中文3000-5000字）
- 核心算法/模型架构图解
- 逐步拆解技术方案
- 关键公式的中文解释
- 与之前方法的对比

**【实验分析】**（中文2000-4000字）
- 使用的数据集介绍
- 评估指标说明
- 主要结果表格分析
- 消融实验分析
- 异常情况讨论

**【结论与展望】**（中文800-1500字）
- 核心贡献总结
- 研究局限性
- 未来改进方向
- 潜在应用场景

**【原文引用】**（保持英文）
- 完整英文摘要
- 关键英文原文段落

#### 3.3 术语处理

```html
<span class="term" data-en="Transformer" title="Transformer架构">
    Transformer（变换器）
</span>
```

首次出现时附英文原文，hover显示解释。

---

### Step 4: 提取引用论文

对论文中引用的核心文献：

1. 提取：标题、作者、年份、引用上下文
2. 在 `references/` 创建条目
3. 如为arXiv论文，递归获取并生成简明教程

---

### Step 5: 更新数据库

```jsonl
{"arxiv_id": "2605.XXXXX", "title": "论文标题", "date": "2026-05-01",
 "authors": ["Author1", "Author2"], "impact_score": 95, "status": "completed",
 "path": "AI论文/2026-05-01/paper-slug/", "chinese_level": "详细",
 "references": ["ref1", "ref2"]}
```

---

## 交互元素规范

教程必须包含：

| 元素 | 说明 |
|------|------|
| 阅读进度条 | 滚动条显示当前阅读位置 |
| 目录导航 | 可点击跳转至各章节 |
| 术语提示 | 专业术语hover显示英文原文 |
| 关键公式 | 数学公式清晰展示 |
| 对比表格 | 与其他方法的性能对比 |
| 架构图示 | 模型/算法结构可视化 |
| 小测验 | 3-5道选择题检验理解 |

---

## 示例输出格式

```
📚 已获取最近7天Top10 AI论文

1. HERMES++: 统一驾驶世界模型
   arXiv: 2604.28196 | 领域: 计算机视觉
   ✅ 原文PDF已下载
   ✅ 详细中文教程已生成（8000字）
   📚 引用论文: 12篇已提取

...

共计: 10篇论文已处理
总字数: 约80,000字
保存位置: D:/claude/AI论文/
```

---

## 搜索策略

### arXiv API

```bash
# 搜索最近7天AI相关论文
curl "https://export.arxiv.org/api/query?\
  search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV&\
  start=0&max_results=100&\
  sortBy=submittedDate&sortOrder=descending"
```

### 影响力度量

```python
impact_score = (
    base_score(50)
    + github_bonus(30 if has_code else 0)
    + conference_bonus(25 if top_conference else 0)
    + author_citation_bonus(min(len(authors)*2, 10))
    + category_popularity_bonus({'cs.CL': 20, 'cs.LG': 15, ...})
)
```

---

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| PDF下载失败 | 保存摘要信息，继续处理 |
| 翻译质量不足 | 标记"待完善"，后续可更新 |
| 引用论文获取失败 | 仅保存引用信息 |
| 目录已存在 | 检查内容完整度后决策 |

---

## 依赖工具

- `curl` — 下载PDF
- `python3` — 数据处理和HTML生成
- Web Search — 搜索论文信息
- WebFetch — 获取论文页面内容
- arXiv API — 论文元数据

---

## 使用示例

```
用户：获取最近AI论文
助手：正在搜索arXiv... 找到50篇候选论文
      按影响力排序，取Top10
      正在下载PDF并生成详细中文教程...
      完成！10篇论文已处理，总计约80,000字
      保存位置：D:/claude/AI论文/2026-05-02/
```
