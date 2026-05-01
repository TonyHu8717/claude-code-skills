---
name: wiki
description: LLM Wiki — 跨会话累积的持久化 markdown 知识库（Karpathy 模型）
triggers: ["wiki", "wiki this", "wiki add", "wiki lint", "wiki query"]
---

# Wiki

持久化的、自维护的 markdown 知识库，用于项目和会话知识。受 Karpathy 的 LLM Wiki 概念启发。

## 操作

### 导入
将知识处理为 wiki 页面。一次导入可以涉及多个页面。

```
wiki_ingest({ title: "Auth Architecture", content: "...", tags: ["auth", "architecture"], category: "architecture" })
```

### 查询
按关键词和标签搜索所有 wiki 页面。返回带有摘要的匹配页面——你（LLM）从结果中综合答案并引用。

```
wiki_query({ query: "authentication", tags: ["auth"], category: "architecture" })
```

### 检查
对 wiki 运行健康检查。检测孤立页面、过期内容、损坏的交叉引用、超大页面和结构性矛盾。

```
wiki_lint()
```

### 快速添加
快速添加单个页面（比导入更简单）。

```
wiki_add({ title: "Page Title", content: "...", tags: ["tag1"], category: "decision" })
```

### 列出 / 读取 / 删除
```
wiki_list()           # 显示所有页面（读取 index.md）
wiki_read({ page: "auth-architecture" })  # 读取特定页面
wiki_delete({ page: "outdated-page" })    # 删除页面
```

### 日志
通过读取 `.omc/wiki/log.md` 查看 wiki 操作历史。

## 分类
页面按类别组织：`architecture`、`decision`、`pattern`、`debugging`、`environment`、`session-log`

## 存储
- 页面：`.omc/wiki/*.md`（带 YAML frontmatter 的 markdown）
- 索引：`.omc/wiki/index.md`（自动维护的目录）
- 日志：`.omc/wiki/log.md`（仅追加的操作记录）

## 交叉引用
使用 `[[page-name]]` wiki-link 语法在页面之间创建交叉引用。

## 自动捕获
会话结束时，重要的发现会自动捕获为 session-log 页面。通过 `.omc-config.json` 中的 `wiki.autoCapture` 配置（默认：启用）。

## 硬约束
- 无向量嵌入——查询仅使用关键词 + 标签匹配
- Wiki 页面默认被 git 忽略（`.omc/wiki/` 是项目本地的）
