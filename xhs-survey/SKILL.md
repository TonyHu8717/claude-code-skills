---
name: xhs-survey
version: 2.0.0
description: "小红书话题影响力调研：模拟真人浏览方式，打开浏览器 → 搜索话题 → 上下滑动浏览 → 点击进入笔记 → 读取详情内容 → 汇总分析。当用户需要调研某个话题在小红书上的表现、影响力、讨论度时使用本技能。"
---

# xhs-survey

小红书话题影响力调研技能。通过模拟真人浏览行为采集数据。

## 1. 何时使用本 Skill

### 1.1 触发条件

- 用户要求调研某个话题/品牌/事件在小红书上的影响力
- 用户要求抓取小红书上的笔记数据
- 用户要求分析小红书话题热度
- 用户给出关键词并要求"看看小红书上怎么说"

### 1.2 核心原理

本技能模拟真人浏览小红书的完整行为链：

```
打开浏览器 → 访问小红书 → 输入关键词搜索 → 上下滑动浏览 → 点击感兴趣的笔记 → 阅读笔记内容 → 返回继续浏览 → 汇总分析
```

**关键设计：**
- 使用 **非无头模式**（浏览器窗口可见），降低被检测概率
- **模拟人类操作**：随机滚动速度、随机停留时间、鼠标移动、点击进入笔记
- **逐条读取**：点击进入每篇笔记，读取完整内容后返回
- **API 拦截**：在浏览过程中自动捕获 API 返回的结构化数据

## 2. 工作流程

### 2.1 第一步：加载 Cookie

从 `D:/claude/xhs_cookie.txt` 读取已保存的 Cookie。如果不存在或过期，引导用户从 Edge 浏览器获取。

### 2.2 第二步：模拟浏览采集

核心脚本：`D:/claude/.agents/skills/xhs-survey/xhs_survey_collector.py`

**浏览行为模拟：**

| 行为 | 实现方式 | 目的 |
|------|---------|------|
| 打开浏览器 | `headless=False`，设置真实 viewport | 降低反爬检测 |
| 搜索 | 填入关键词，按 Enter | 触发搜索 |
| 上下滑动 | `window.scrollBy()` + 随机距离 + 随机延迟 | 模拟人类浏览 |
| 停留阅读 | 随机等待 2-5 秒 | 模拟阅读时间 |
| 点击笔记 | `element.click()` 进入笔记详情页 | 获取完整内容 |
| 返回 | `page.go_back()` 或点击关闭 | 继续浏览下一篇 |
| 读取详情 | 从笔记详情页 DOM 提取标题、正文、互动数据 | 获取核心数据 |

**采集流程（每个关键词）：**

```
1. 打开搜索页面（最热排序）
2. 等待页面加载（5-8秒）
3. 循环：
   a. 向下滚动 300-800px（随机距离）
   b. 等待 1-3 秒（随机时间）
   c. 扫描当前可见区域的笔记卡片
   d. 逐个点击进入笔记详情页
   e. 读取：标题、作者、正文、点赞、收藏、评论、标签
   f. 返回搜索结果页
   g. 继续滚动
4. 重复步骤3，直到采集到足够笔记或没有更多内容
5. 切换到最新排序，重复上述流程
```

### 2.3 第三步：数据解析

**笔记详情页 DOM 选择器：**

```
标题: #detail-title, [class*="title"]
正文: #detail-desc, .note-text, [class*="desc"]
作者: .author-wrapper .username, [class*="author"] [class*="name"]
点赞: [class*="like-wrapper"] .count, [class*="like"] [class*="count"]
收藏: [class*="collect-wrapper"] .count, [class*="collect"] [class*="count"]
评论数: [class*="chat-wrapper"] .count, [class*="comment"] [class*="count"]
标签: .tag a, [class*="hash-tag"]
视频: video, [class*="video-player"]
```

**搜索结果页 DOM 选择器：**

```
笔记卡片: section.note-item, a[href*="/explore/"]
标题: [class*="title"] span
作者: [class*="name"], [class*="nickname"]
点赞: [class*="like"] span, [class*="count"]
```

### 2.4 第四步：分析与报告

**基础指标：**
- 笔记总数、独立作者数
- 内容类型分布（图文 vs 视频）
- 总互动量（点赞 + 收藏 + 评论 + 转发）
- 平均互动量、收藏率（收藏/点赞）

**深度分析：**
- 最热笔记 TOP 10（按互动量排序）
- 最新笔记 TOP 10
- 活跃作者排行
- 热门标签
- 内容摘要（从笔记正文中提取关键信息）

**影响力评分：**
- 内容体量分 = min(10, 笔记数/10)
- 互动质量分 = min(10, 平均互动/300)
- 内容多样分 = 视频占比×10 + 图文占比×6
- 综合影响力 = 质量×0.5 + 体量×0.3 + 多样×0.2

## 3. 降级策略

1. **API 拦截优先**：通过 `page.on('response')` 捕获搜索 API 的结构化数据
2. **DOM 提取**：从页面 DOM 中提取可见内容
3. **详情页读取**：点击进入笔记页面读取完整内容
4. **手动辅助**：引导用户在控制台执行 JS 代码复制数据

## 4. 文件结构

```
D:/claude/
├── xhs_cookie.txt                          # Cookie 存储
├── .agents/skills/xhs-survey/
│   ├── SKILL.md                            # 技能定义
│   └── xhs_survey_collector.py             # 数据采集脚本
├── xhs_data_[timestamp].json               # 原始数据
└── xhs_report_[timestamp].txt              # 分析报告
```

## 5. 依赖

- Python 3.12+
- playwright (`pip install playwright`)
- Edge 浏览器（已安装）

## 6. 使用示例

用户输入：
> 帮我调研"地平线星空芯片"在小红书上的影响力

执行：
1. 读取 Cookie
2. 运行 `python xhs_survey_collector.py "地平线星空芯片"`
3. 浏览器打开，自动搜索、滑动、点击、读取
4. 生成报告
