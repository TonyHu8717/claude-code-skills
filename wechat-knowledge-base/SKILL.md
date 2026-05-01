---
name: wechat-knowledge-base
description: 微信公众号文章爬取与知识库建设。输入公众号名称或文章链接，自动爬取所有文章并整理成结构化知识库。每个公众号单独存储，支持增量更新和全文检索。在需要收集公众号内容、构建垂直领域知识库、研究竞品内容时使用。
---

# 微信公众号知识库构建

自动爬取微信公众号文章，整理成可检索的结构化知识库。

## 核心能力

### 1. 多源输入支持

- **公众号名称**：输入公众号名称，自动搜索并爬取所有历史文章
- **文章链接**：输入任意文章链接，自动识别所属公众号并爬取全部文章
- **混合模式**：同时支持多种输入方式

### 2. 知识库结构

```
knowledge_base/
├── 公众号名称A/
│   ├── meta.json          # 元数据
│   ├── index.md           # 总索引
│   ├── 2024-01/
│   │   ├── 文章标题1.md
│   │   └── ...
│   └── 2024-02/
├── 公众号名称B/
│   └── ...
└── search_index.json      # 全局搜索索引
```

### 3. 文章存储格式

每篇文章存储为独立 Markdown 文件，包含：

- title: 文章标题
- author: 公众号名称
- date: 发布日期
- url: 原文链接
- tags: 标签
- digest: 摘要
- content: 正文

## 技术方案

### 方案一：基于 Wechaty 机器人（推荐）

利用已有的 wechat-bridge.js，通过微信消息交互获取文章。

```javascript
// 扩展 wechat-bridge.js 添加文章爬取功能
const ARTICLE_CRAWLER = {
  async handleArticleRequest(text) {
    const target = this.parseInput(text);
    if (target.type === 'account') {
      const account = await this.searchAccount(target.name);
      return this.crawlAccount(account);
    } else if (target.type === 'link') {
      const account = await this.getAccountFromLink(target.url);
      return this.crawlAccount(account);
    }
  },
  async crawlAccount(account) {
    const articles = await this.getArticleList(account);
    for (const article of articles) {
      const content = await this.fetchArticleContent(article.url);
      await this.saveToKnowledgeBase(account, article, content);
    }
    return `已爬取 ${articles.length} 篇文章`;
  }
};
```

### 方案二：基于公众号平台 API

使用新媒体管家等第三方工具的 API 接口。

```python
class WechatCrawler:
    def __init__(self):
        self.api_key = os.getenv('WECHAT_API_KEY')
    
    def search_account(self, name):
        response = requests.post(
            f"{self.base_url}/api/v1/account/search",
            json={"keyword": name}
        )
        return response.json()
    
    def get_articles(self, account_id, page=1):
        response = requests.get(
            f"{self.base_url}/api/v1/account/articles",
            params={"account_id": account_id, "page": page}
        )
        return response.json()
```

### 方案三：基于 RSS 订阅

部分公众号支持通过 RSS 获取更新。

```yaml
rss_sources:
  - name: 公众号A
    feed_url: https://rsshub.app/wechat/mp/公众号原始ID
update_schedule: "0 */6 * * *"
```

## 实施步骤

### 第一步：环境准备

```bash
# 安装依赖
npm install wechaty wechaty-puppet-wechat qrcode-terminal
pip install requests beautifulsoup4 markdownify

# 确保 wechat-bridge.js 正常运行
node wechat-bridge.js &
```

### 第二步：创建知识库目录

```bash
mkdir -p knowledge_base/{archive,backup,config}
```

### 第三步：初始化配置

```json
// knowledge_base/config/crawler.json
{
  "base_dir": "knowledge_base",
  "max_articles_per_account": 500,
  "update_interval_hours": 24,
  "content_format": "markdown",
  "auto_tag": true,
  "rate_limit_seconds": 3
}
```

### 第四步：执行爬取

**命令行模式：**
```bash
python wechat_crawler.py --account "公众号名称"
python wechat_crawler.py --url "文章链接"
python wechat_crawler.py --batch accounts.txt
```

**微信消息模式：**
```
发送: 爬取公众号 公众号名称
发送: 爬取 https://mp.weixin.qq.com/s/xxx
```

## 核心代码实现

### Python 爬虫脚本

```python
#!/usr/bin/env python3
"""微信公众号知识库爬虫"""

import argparse
import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path

class WechatKnowledgeBase:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.articles_dir = self.base_dir / "articles"
        self.articles_dir.mkdir(exist_ok=True)
        self.index_file = self.base_dir / "search_index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {"accounts": {}, "articles": []}
    
    def _save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def sanitize_filename(self, title: str) -> str:
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        if len(filename) > 100:
            filename = filename[:97] + "..."
        return filename + ".md"
    
    def extract_article_content(self, html: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.find('h1', class_='rich_media_title')
        title = title.text.strip() if title else "未命名文章"
        
        content = soup.find('div', id='js_content')
        if not content:
            content = soup.find('div', class_='rich_media_content')
        
        date_elem = soup.find('em', id='publish_time')
        date = date_elem.text if date_elem else datetime.now().strftime('%Y-%m-%d')
        
        author = soup.find('span', class_='rich_media_meta_nickname')
        author = author.text if author else "未知"
        
        return {
            'title': title,
            'author': author,
            'date': date,
            'content': str(content) if content else "",
            'url': ''
        }
    
    def save_article(self, account: str, article: dict, content_html: str):
        account_dir = self.articles_dir / account
        account_dir.mkdir(exist_ok=True)
        
        article_data = self.extract_article_content(content_html)
        article_data.update(article)
        
        filename = self.sanitize_filename(article_data['title'])
        filepath = account_dir / filename
        
        markdown = self._to_markdown(article_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        self._update_index(account, article_data, str(filepath))
        return filepath
    
    def _to_markdown(self, article: dict) -> str:
        from markdownify import markdownify as md
        
        frontmatter = f"""---
title: {article['title']}
author: {article['author']}
date: {article['date']}
url: {article.get('url', '')}
source: wechat
---

"""
        content_md = md(article['content'], heading_style="ATX")
        return frontmatter + content_md
    
    def _update_index(self, account: str, article: dict, filepath: str):
        if account not in self.index['accounts']:
            self.index['accounts'][account] = {
                'name': account,
                'article_count': 0,
                'last_updated': '',
                'articles': []
            }
        
        article_id = hashlib.md5(article['title'].encode()).hexdigest()[:8]
        
        self.index['accounts'][account]['articles'].append({
            'id': article_id,
            'title': article['title'],
            'date': article['date'],
            'filepath': filepath
        })
        self.index['accounts'][account]['article_count'] += 1
        self.index['accounts'][account]['last_updated'] = datetime.now().isoformat()
        
        self.index['articles'].append({
            'id': article_id,
            'account': account,
            'title': article['title'],
            'date': article['date'],
            'filepath': filepath
        })
        
        self._save_index()
    
    def search(self, query: str) -> list:
        results = []
        query_lower = query.lower()
        for article in self.index['articles']:
            if query_lower in article['title'].lower():
                results.append(article)
        return results

def main():
    parser = argparse.ArgumentParser(description='微信公众号知识库爬虫')
    parser.add_argument('--account', help='公众号名称')
    parser.add_argument('--url', help='文章链接')
    parser.add_argument('--output', default='knowledge_base', help='输出目录')
    
    args = parser.parse_args()
    if not args.account and not args.url:
        parser.print_help()
        return
    
    kb = WechatKnowledgeBase(args.output)
    
    if args.account:
        print(f"开始爬取公众号: {args.account}")
    if args.url:
        print(f"开始爬取文章: {args.url}")

if __name__ == '__main__':
    main()
```

## 使用示例

### 场景1：构建行业知识库

1. 搜索相关公众号列表
2. 批量爬取每个公众号的文章
3. 按时间线整理成行业知识库
4. 生成交叉引用索引

### 场景2：竞品分析

1. 输入竞品公众号名称
2. 自动爬取历史文章
3. 提取关键产品和策略信息
4. 生成竞品分析报告

### 场景3：内容归档

1. 输入公众号名称
2. 爬取全部文章
3. 保存为离线可读的 Markdown
4. 生成年度归档索引

## 高级功能

### 1. 增量更新

```python
def incremental_update(kb, account, last_known_date):
    articles = get_article_list(account)
    new_articles = [a for a in articles if a['date'] > last_known_date]
    
    for article in new_articles:
        content = fetch_article(article['url'])
        kb.save_article(account, article, content)
        time.sleep(RATE_LIMIT)
```

### 2. 自动标签

```python
def auto_tag(content: str) -> list:
    keywords = extract_keywords(content, top_n=5)
    return keywords
```

### 3. 全文检索

```bash
cd knowledge_base
rg "关键词" --type md -l
```

## 注意事项

### 合规使用

- 仅爬取已公开的文章
- 遵守公众号平台的 robots.txt
- 控制请求频率，避免对服务器造成压力
- 尊重版权，注明来源

### 数据存储

- 定期备份知识库
- 敏感内容加密存储
- 定期清理失效链接

### 维护建议

- 设置定时任务自动更新
- 监控爬取成功率
- 定期验证文章可访问性

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 无法搜索到公众号 | 确认公众号名称正确，或尝试使用原始ID |
| 文章内容为空 | 检查是否需要登录，某些文章有访问限制 |
| 爬取被限制 | 降低请求频率，或使用代理池 |
| 图片无法下载 | 配置图片下载功能，或使用图床替换 |

## 扩展方向

- **多语言支持**：同时爬取中英文公众号
- **多平台扩展**：支持知乎、微博等平台
- **AI 增强**：自动摘要、主题分类、情感分析
- **可视化界面**：Web 管理界面查看知识库
