---
name: academic-papers
description: 获取最近7天国际新发表论文，按行业影响力排序Top10，支持全学科领域，下载原文并翻译为详细中文HTML教程。调用时必须指定领域，默认AI领域。支持的领域：AI(cs.AI/cs.LG/cs.CL/cs.CV)、计算机(cs.CY/cs.ET/cs.NE)、物理(physics)、数学(math)、生物(q-bio)、金融(q-fin)、统计(stat)、医学(q-med)、经济(q-econ)等。
---

# 学术论文猎手

> 追踪最新学术论文，深度翻译解读，提取引用，一站式研究助手。
>
> **核心原则**：所有教程内容使用中文编写（原文引用除外），内容详尽，便于深入阅读理解。

---

## 激活方式

**必须指定领域范围，未指定时默认AI领域：**

```
/academic-papers                    # 默认：AI领域
/academic-papers AI                 # AI领域（默认）
/academic-papers cs.CL              # 计算语言学
/academic-papers physics:cond-mat   # 凝聚态物理
/academic-papers math              # 数学
/academic-papers q-bio             # 量子生物
/academic-papers all               # 所有学科
```

### 支持的领域代码

| 领域代码 | 说明 | arXiv类别 |
|---------|------|----------|
| AI | 人工智能（默认） | cs.AI, cs.LG, cs.CL, cs.CV |
| CS | 计算机科学 | cs.CY, cs.ET, cs.NE, cs.PL, cs.SE |
| PHYSICS | 物理学 | physics, cond-mat, quant-ph, hep-*, astro-ph |
| MATH | 数学 | math |
| BIO | 生物科学 | q-bio, bio |
| MED | 医学 | q-med |
| FIN | 金融 | q-fin |
| STAT | 统计学 | stat |
| ECON | 经济学 | q-econ |
| ENG | 工程学 | eess, epi, nlin |
| ALL | 全学科 | 所有类别 |

---

## 核心更新要求

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
D:/claude/论文/
└── {领域}/
    ├── {论文标题中文slug}/
    │   ├── {论文标题中文slug}.html    # 详细中文教程
    │   ├── 原文.pdf                  # 原始PDF
    │   ├── 元信息.json               # 论文元信息
    │   ├── 引用论文/                  # 引用论文
    │   │   ├── 被引论文1.html
    │   │   └── ...
    │   └── 笔记.md                  # 个人笔记
    ├── 论文数据库.jsonl                # 论文数据库（含更新时间）
    ├── 领域索引.html                   # 该领域所有论文的HTML索引
    └── 搜索历史.jsonl                  # 搜索历史
```

**重要变化：**
- 论文直接放在 `{领域}/` 下，不再有 `YYYY-MM-DD/` 中间目录
- 每个论文独占一个子目录
- 每个领域根目录有 `领域索引.html`

---

## 更新策略

### 智能更新规则

| 情况 | 处理方式 |
|------|---------|
| 首次获取（无本地数据） | 搜索历史Top20论文 |
| 7天内已更新过 | 直接返回本地数据，跳过重复搜索 |
| 7天外首次更新 | 搜索最新Top10论文 |
| 增量更新 | 搜索自上次更新后的新论文 |

### 更新状态记录

在 `论文数据库.jsonl` 中记录：

```jsonl
{"last_updated": "2026-05-02", "domain": "AI", "paper_count": 10}
```

---

## 工作流程

### Step 0: 检查更新状态

检查 `论文数据库.jsonl` 的 `last_updated` 字段：

```bash
# 检查领域是否存在及更新时间
cat D:/claude/论文/{领域}/论文数据库.jsonl | tail -1
```

**决策规则：**
- 数据库不存在 → 历史Top20论文
- 距今≤7天 → 返回本地数据
- 距今>7天 → 搜索最新Top10论文

---

### Step 1: 搜索论文

**首次获取（历史Top20）：**
- 按引用数/影响力排序
- 取历史排名前20

**增量更新（最新Top10）：**
- 搜索最近7天新发表的论文
- 按影响力排序取Top10

**搜索源：**
1. **arXiv API** — 论文元数据
2. **Semantic Scholar** — 引用数和影响力评分

**arXiv API 调用方式：**

```bash
# AI领域（默认）
curl "https://export.arxiv.org/api/query?\
  search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV&\
  start=0&max_results=100&\
  sortBy=submittedDate&sortOrder=descending"

# 全学科（历史Top20按引用排序）
curl "https://export.arxiv.org/api/query?\
  search_query=all&\
  start=0&max_results=100&\
  sortBy=submittedDate&sortOrder=descending"
```

---

### Step 2: 下载原文

```bash
# 下载PDF
curl -L -o "D:/claude/论文/{领域}/{论文标题中文slug}/原文.pdf" \
     "https://arxiv.org/pdf/{arxiv-id}.pdf"

# 检查下载成功（文件大小 > 10KB）
```

---

### Step 3: 生成详细HTML教程

#### 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{中文标题} - 论文解读</title>
    <style>
        :root {
            --bg: #faf8f5;
            --card: #fff;
            --text: #2d3436;
            --accent: #3498db;
            --accent2: #2c3e50;
        }
        body {
            font-family: -apple-system, "Microsoft YaHei", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.8;
        }
        .progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: var(--accent); width: 0%; }
        header { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; padding: 30px; border-radius: 0 0 30px 30px; }
        h1 { font-size: 1.8em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; }
        .meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }
        .meta-item { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; }
        nav.toc { background: var(--card); padding: 20px; border-radius: 12px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        nav.toc ul { list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        nav.toc a { color: var(--accent); text-decoration: none; padding: 8px 16px; display: block; border-radius: 6px; transition: background 0.2s; }
        nav.toc a:hover { background: #e8f4fd; }
        main { max-width: 900px; margin: 0 auto; padding: 20px; }
        section { background: var(--card); padding: 30px; border-radius: 12px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h2 { color: var(--accent); border-bottom: 2px solid var(--accent); padding-bottom: 10px; margin-bottom: 20px; }
        h3 { color: var(--accent2); margin: 20px 0 10px; }
        .term { background: #e8f4fd; padding: 2px 8px; border-radius: 4px; color: #2980b9; }
        .quiz { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .quiz-option { display: block; padding: 10px; margin: 5px 0; background: var(--card); border: 1px solid #ddd; border-radius: 6px; cursor: pointer; }
        .quiz-option:hover { border-color: var(--accent); }
        footer { text-align: center; padding: 40px; opacity: 0.6; }
    </style>
</head>
<body>
    <div class="progress-bar" id="progress"></div>

    <header>
        <h1>{中文标题}</h1>
        <p class="subtitle">{英文标题}</p>
        <div class="meta">
            <div class="meta-item"><strong>作者：</strong>{作者团队}</div>
            <div class="meta-item"><strong>机构：</strong>{所属机构}</div>
            <div class="meta-item"><strong>发表：</strong>{日期}</div>
            <div class="meta-item"><strong>arXiv：</strong>{ID}</div>
            <div class="meta-item"><strong>领域：</strong>{研究领域}</div>
        </div>
        <a href="原文.pdf" class="btn" style="display:inline-block;padding:10px 20px;background:#fff;color:var(--accent);border-radius:8px;text-decoration:none;margin-top:10px;">下载原文PDF</a>
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
        <section id="overview">
            <h2>论文概览</h2>
        </section>
        <section id="background">
            <h2>背景与动机</h2>
        </section>
        <section id="problem">
            <h2>问题定义</h2>
        </section>
        <section id="method">
            <h2>方法详解</h2>
        </section>
        <section id="experiment">
            <h2>实验分析</h2>
        </section>
        <section id="conclusion">
            <h2>结论与展望</h2>
        </section>
        <section id="references">
            <h2>原文引用</h2>
        </section>
        <section id="quiz" class="quiz">
            <h2>理解测验</h2>
        </section>
    </main>

    <footer>
        <p>论文解读 | {领域} | 生成日期：{日期}</p>
    </footer>

    <script>
        window.addEventListener('scroll', () => {
            const scrollTop = document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            document.getElementById('progress').style.width = (scrollTop / scrollHeight * 100) + '%';
        });
    </script>
</body>
</html>
```

---

### Step 4: 生成领域索引页

每个领域的 `领域索引.html` 结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{领域}论文索引</title>
    <style>
        body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #faf8f5; color: #2d3436; line-height: 1.8; padding: 20px; }
        header { background: linear-gradient(135deg, #3498db, #2c3e50); color: #fff; padding: 30px; border-radius: 0 0 30px 30px; margin-bottom: 30px; }
        h1 { margin: 0; }
        .update-info { opacity: 0.9; margin-top: 10px; }
        .paper-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .paper-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .paper-card:hover { transform: translateY(-4px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .paper-card h2 { color: #3498db; font-size: 1.2em; margin-bottom: 10px; }
        .paper-card .meta { font-size: 0.9em; color: #666; margin-bottom: 10px; }
        .paper-card .summary { margin-bottom: 15px; }
        .paper-card a { display: inline-block; padding: 8px 16px; background: #3498db; color: #fff; border-radius: 6px; text-decoration: none; }
        .paper-card a:hover { background: #2980b9; }
        footer { text-align: center; padding: 40px; opacity: 0.6; }
    </style>
</head>
<body>
    <header>
        <h1>{领域}论文索引</h1>
        <p class="update-info">更新时间：{最后更新日期} | 共{论文数量}篇论文</p>
    </header>

    <main>
        <div class="paper-grid">
            <!-- 每篇论文一个卡片 -->
            <article class="paper-card">
                <h2>{论文标题}</h2>
                <p class="meta">arXiv: {ID} | {日期}</p>
                <p class="summary">{一句话摘要}</p>
                <a href="{论文标题中文slug}/{论文标题中文slug}.html">阅读详解</a>
            </article>
            <!-- 更多论文卡片... -->
        </div>
    </main>

    <footer>
        <p>学术论文猎手 | 自动更新</p>
    </footer>
</body>
</html>
```

---

### Step 5: 更新数据库

```jsonl
{"arxiv_id": "2605.XXXXX", "title": "论文标题", "domain": "AI", "date": "2026-05-01",
 "authors": ["Author1", "Author2"], "impact_score": 95, "status": "completed",
 "path": "论文/AI/{论文标题中文slug}/", "chinese_level": "详细",
 "references": ["ref1", "ref2"]}
{"last_updated": "2026-05-02", "domain": "AI", "paper_count": 10}
```

---

## 示例输出格式

```
学术论文猎手 | 领域: AI

📚 首次获取历史Top20论文

1. HERMES++: 统一驾驶世界模型
   arXiv: 2604.28196 | 影响分数: 95
   ✅ 原文PDF已下载
   ✅ 详细中文教程已生成（8000字）

...

共计: 20篇论文已处理
总字数: 约160,000字
保存位置: D:/claude/论文/AI/
索引页: D:/claude/论文/AI/领域索引.html
```

或增量更新模式：

```
学术论文猎手 | 领域: AI

📚 距上次更新(2026-04-25)已超过7天，执行增量更新

正在搜索最近7天新论文... 找到15篇
按影响力排序，取Top10
✅ 3篇新论文已添加

共计: 13篇论文
保存位置: D:/claude/论文/AI/
```

---

## 影响力度量

```python
impact_score = (
    base_score(50)
    + github_bonus(30 if has_code else 0)
    + conference_bonus(25 if top_conference else 0)
    + author_citation_bonus(min(len(authors)*2, 10))
    + category_popularity_bonus({'cs.CL': 20, 'cs.LG': 15, 'math': 10, ...})
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
