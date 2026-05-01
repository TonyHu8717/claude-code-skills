# 微信公众号知识库构建

微信公众号文章爬取与知识库建设技能。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

```bash
# 爬取单篇文章
python wechat_crawler.py --url "https://mp.weixin.qq.com/s/xxxxx"

# 搜索知识库
python wechat_crawler.py --search "关键词"

# 查看已爬取的公众号
python wechat_crawler.py --list
```

## 项目结构

```
wechat-knowledge-base/
├── SKILL.md                    # 技能文档
├── README.md                   # 本文件
├── references/
│   └── implementation-guide.md # 实现指南
│
├── ../../wechat_crawler.py     # 爬虫脚本
├── ../../requirements.txt       # Python 依赖
│
└── ../../knowledge_base/        # 知识库目录
    ├── articles/               # 文章存储
    │   └── {公众号名称}/
    │       └── {文章}.md
    ├── config/                # 配置
    └── search_index.json      # 搜索索引
```

## 功能特性

- 多源输入：公众号名称 / 文章链接
- Markdown 格式存储
- 自动去重
- 全文检索
- 增量更新
- 索引生成