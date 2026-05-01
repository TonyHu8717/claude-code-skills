# 微信公众号知识库实现指南

## 环境配置

### 必需依赖

```bash
# Python 依赖
pip install requests beautifulsoup4 markdownify lxml

# Node.js 依赖 (可选，用于Wechaty集成)
npm install wechaty wechaty-puppet-wechat
```

### 目录结构

```
project/
├── knowledge_base/
│   ├── config/
│   │   └── crawler.json
│   ├── articles/
│   │   └── {公众号名称}/
│   │       └── {文章标题}.md
│   ├── archive/
│   ├── backup/
│   └── search_index.json
├── wechat_crawler.py
└── requirements.txt
```

## 快速开始

### 1. 初始化知识库

```python
from wechat_crawler import WechatKnowledgeBase

kb = WechatKnowledgeBase('./knowledge_base')
```

### 2. 爬取单个公众号

```python
# 通过名称爬取
kb.crawl_by_account_name('公众号名称')

# 通过文章链接爬取
kb.crawl_by_article_url('https://mp.weixin.qq.com/s/xxx')
```

### 3. 搜索内容

```python
results = kb.search('关键词')
for r in results:
    print(f"{r['title']} - {r['account']}")
```

## API 参考

### WechatKnowledgeBase 类

#### `__init__(base_dir: str)`
初始化知识库管理器。

#### `save_article(account: str, article: dict, content_html: str) -> Path`
保存单篇文章。

#### `search(query: str) -> List[dict]`
全文搜索。

#### `get_account_articles(account: str) -> List[dict]`
获取指定公众号的所有文章。

#### `update_account(account: str)`
增量更新指定公众号。

#### `export_markdown(account: str, output_dir: str)`
导出为离线 Markdown。