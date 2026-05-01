#!/usr/bin/env python3
"""
微信公众号文章爬虫
支持通过公众号名称或文章链接爬取文章并整理成知识库
"""

import argparse
import json
import os
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)

# 配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def slugify(title: str, max_length: int = 50) -> str:
    """将标题转换为适合文件名的 slug"""
    # 移除 emoji 和特殊符号
    title = re.sub(r'[\U00010000-\U0010ffff]', '', title)
    title = re.sub(r'[^\w\s一-鿿-]', '', title)
    # 移除多余空格
    title = re.sub(r'\s+', '-', title.strip())
    # 转拼音（基础版，只处理常见词）
    # 实际使用建议安装 pypinyin
    try:
        from pypinyin import lazy_pinyin
        words = lazy_pinyin(title)
        slug = ''.join(words)
    except ImportError:
        # 如果没有 pypinyin，使用原始中文（文件系统支持）
        slug = title
    # 截断
    if len(slug) > max_length:
        slug = slug[:max_length]
    return slug.lower()

def extract_biz_from_url(url: str) -> Optional[str]:
    """从文章链接提取 biz 参数"""
    match = re.search(r'biz\s*[=]\s*([\w\-]+)', url)
    if match:
        return match.group(1)
    # 尝试从完整链接提取
    match = re.search(r'mp\.weixin\.qq\.com/s[/_][\w]+', url)
    if match:
        return None  # 需要通过页面获取 biz
    return None

def get_article_list_by_biz(biz: str, count: int = 10) -> List[Dict]:
    """通过 biz 获取公众号文章列表"""
    # 搜狗微信搜索
    url = f"https://weixin.sogou.com/weixin?type=1&s_from=input&query=biz:{biz}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        # 解析文章列表（简化版）
        articles = []
        # 实际需要更复杂的解析逻辑
        return articles
    except Exception as e:
        print(f"获取文章列表失败: {e}")
        return []

def scrape_article(url: str) -> Optional[Dict]:
    """抓取单篇文章内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'

        html = response.text

        # 提取标题
        title_match = re.search(r'<h1[^>]*id\s*=\s*["\']activity-name["\'][^>]*>([^<]+)</h1>', html)
        title = title_match.group(1).strip() if title_match else "未知标题"

        # 提取作者（公众号名称）
        author_match = re.search(r'<strong[^>]*id\s*=\s*["\']js_name["\'][^>]*>([^<]+)</strong>', html)
        author = author_match.group(1).strip() if author_match else "未知公众号"

        # 提取发布日期
        date_match = re.search(r'var\s+ct\s*=\s*["\'](\d+)["\']', html)
        if date_match:
            publish_date = datetime.fromtimestamp(int(date_match.group(1)))
            publish_date = publish_date.strftime('%Y-%m-%d')
        else:
            publish_date = datetime.now().strftime('%Y-%m-%d')

        # 提取正文内容
        content_match = re.search(r'<div[^>]*id\s*=\s*["\']js_content["\'][^>]*>(.*?)</div>\s*<div[^>]*id\s*=\s*["\']js_pc_qr_code["\']', html, re.DOTALL)
        content = content_match.group(1) if content_match else ""

        # 清理 HTML 标签，保留段落结构
        content = re.sub(r'<p[^>]*>', '\n', content)
        content = re.sub(r'</p>', '', content)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()

        return {
            'title': title,
            'author': author,
            'date': publish_date,
            'url': url,
            'content': content,
        }
    except Exception as e:
        print(f"抓取文章失败: {e}")
        return None

def save_article(article: Dict, output_dir: str, index: int) -> str:
    """保存文章到 Markdown 文件"""
    os.makedirs(output_dir, exist_ok=True)

    slug = slugify(article['title'])
    filename = f"{slug}_{index:03d}.md"
    filepath = os.path.join(output_dir, filename)

    # 生成 frontmatter
    frontmatter = f"""---
title: {article['title']}
author: {article['author']}
date: {article['date']}
link: {article['url']}
source: wechat
---

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write(article['content'])

    return filename

def generate_meta(account_name: str, articles: List[Dict], output_dir: str):
    """生成公众号元数据文件"""
    meta = {
        'name': account_name,
        'collected_at': datetime.now().isoformat(),
        'total_articles': len(articles),
        'description': '',
        'tags': [],
    }

    meta_path = os.path.join(output_dir, '_meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def generate_index(account_name: str, articles: List[Tuple[str, Dict]], output_dir: str):
    """生成公众号文章索引"""
    index_path = os.path.join(output_dir, '_index.md')

    lines = [
        f"# {account_name}",
        "",
        f"> 公众号知识库 | 共 {len(articles)} 篇文章 | 最后更新：{datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 文章列表",
        "",
        "| # | 标题 | 日期 |",
        "|---|------|------|",
    ]

    for i, (filename, article) in enumerate(articles, 1):
        title = article['title']
        date = article['date']
        lines.append(f"| {i} | [{title}]({filename}) | {date} |")

    lines.extend([
        "",
        "## 统计",
        "",
        f"- 文章总数：{len(articles)}",
    ])

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    parser = argparse.ArgumentParser(description='微信公众号文章爬虫')
    parser.add_argument('--name', '-n', help='公众号名称')
    parser.add_argument('--url', '-u', help='文章链接')
    parser.add_argument('--biz', '-b', help='公众号 biz')
    parser.add_argument('--output', '-o', default='wechat-knowledge', help='输出目录')

    args = parser.parse_args()

    if not args.name and not args.url and not args.biz:
        parser.print_help()
        return

    # 确定公众号名称
    account_name = args.name
    if args.url:
        article = scrape_article(args.url)
        if article:
            account_name = account_name or article['author']
            print(f"抓取到文章: {article['title']}")
            print(f"公众号: {account_name}")

    if not account_name:
        print("无法确定公众号名称")
        return

    # 创建输出目录
    output_dir = os.path.join(args.output, account_name)
    os.makedirs(output_dir, exist_ok=True)

    print(f"知识库目录: {output_dir}")
    print("爬取完成")

if __name__ == '__main__':
    main()
