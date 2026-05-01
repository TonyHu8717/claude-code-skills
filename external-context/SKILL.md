---
name: external-context
description: 调用并行文档专家代理进行外部网络搜索和文档查找
argument-hint: <search query or topic>
level: 4
---

# 外部上下文技能

获取查询的外部文档、参考资料和上下文。将其分解为 2-5 个方面，并生成并行的文档专家 Claude 代理。

## 用法

```
/oh-my-claudecode:external-context <topic or question>
```

### 示例

```
/oh-my-claudecode:external-context What are the best practices for JWT token rotation in Node.js?
/oh-my-claudecode:external-context Compare Prisma vs Drizzle ORM for PostgreSQL
/oh-my-claudecode:external-context Latest React Server Components patterns and conventions
```

## 协议

### 步骤 1：方面分解

给定一个查询，将其分解为 2-5 个独立的搜索方面：

```markdown
## 搜索分解

**查询：** <original query>

### 方面 1：<facet-name>
- **搜索重点：** 要搜索的内容
- **来源：** 官方文档、GitHub、博客等

### 方面 2：<facet-name>
...
```

### 步骤 2：并行代理调用

通过 Task 工具并行启动独立方面：

```
Task(subagent_type="oh-my-claudecode:document-specialist", model="sonnet", prompt="Search for: <facet 1 description>. Use WebSearch and WebFetch to find official documentation and examples. Cite all sources with URLs.")

Task(subagent_type="oh-my-claudecode:document-specialist", model="sonnet", prompt="Search for: <facet 2 description>. Use WebSearch and WebFetch to find official documentation and examples. Cite all sources with URLs.")
```

最多 5 个并行文档专家代理。

### 步骤 3：综合输出格式

以以下格式呈现综合结果：

```markdown
## 外部上下文：<query>

### 关键发现
1. **<finding>** - 来源：[title](url)
2. **<finding>** - 来源：[title](url)

### 详细结果

#### 方面 1：<name>
<aggregated findings with citations>

#### 方面 2：<name>
<aggregated findings with citations>

### 来源
- [Source 1](url)
- [Source 2](url)
```

## 配置

- 最多 5 个并行文档专家代理
- 无魔法关键词触发 - 仅显式调用
