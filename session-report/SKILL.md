---
name: session-report
description: 从 ~/.claude/projects 转录生成可浏览的 Claude Code 会话使用 HTML 报告（token、缓存、子代理、技能、高消耗提示）。
---

# 会话报告

生成独立的 Claude Code 使用 HTML 报告并保存到当前工作目录。

## 步骤

1. **获取数据。** 运行内置分析器（默认窗口：最近 7 天；如果用户传入不同范围则遵守，例如 `24h`、`30d` 或 `all`）。脚本 `analyze-sessions.mjs` 与此 SKILL.md 位于同一目录 — 使用其绝对路径：
   ```sh
   node <skill-dir>/analyze-sessions.mjs --json --since 7d > /tmp/session-report.json
   ```
   如需全部历史数据，省略 `--since`。

2. **读取** `/tmp/session-report.json`。浏览 `overall`、`by_project`、`by_subagent_type`、`by_skill`、`cache_breaks`、`top_prompts`。

3. **复制模板**（也与此 SKILL.md 一起捆绑）到当前工作目录的输出路径：
   ```sh
   cp <skill-dir>/template.html ./session-report-$(date +%Y%m%d-%M%M).html
   ```

4. **编辑输出文件**（使用 Edit 而非 Write — 保留模板的 JS/CSS）：
   - 将 `<script id="report-data" type="application/json">` 的内容替换为步骤 1 中的完整 JSON。页面的 JS 会自动从这个数据块渲染总览、所有表格、条形图和下钻分析。
   - 在 `<!-- AGENT: anomalies -->` 块中填写 **3-5 条一行发现**。尽可能将数字表示为**总 token 的百分比**（总计 = `overall.input_tokens.total + overall.output_tokens`）。每个发现一行，精确标记：
     ```html
     <div class="take bad"><div class="fig">41.2%</div><div class="txt"><b>cc-monitor</b> 消耗了本周 41% 的 token，仅用了 3 个会话</div></div>
     ```
     类：`.take bad` 表示浪费/异常（红色），`.take good` 表示健康信号（绿色），`.take info` 表示中性事实（蓝色）。`.fig` 是一个简短数字（百分比、计数或倍数如 `12x`）。`.txt` 是一句简洁的英文句子，指出项目/技能/提示；用 `<b>` 包裹主题。查找：项目或技能消耗不成比例的份额、缓存命中率 <85%、单个提示 >2% 总量、子代理类型平均 >1M token/次调用、缓存中断聚集。
   - 在 `<!-- AGENT: optimizations -->` 块（页面**底部**）填写 1-4 个 `<div class="callout">` 建议，关联到具体行（例如 "`/weekly-status` 生成了 7 个子代理，占总量的 8.1% — 将其限制为更少的并行代理"）。
   - 不要重构现有部分。

5. **报告**保存的文件路径给用户。不要打开或渲染它。

## 备注

- 模板是交互性的来源（排序、展开/折叠、块字符条形图）。您的工作是数据 + 叙述，不是标记。
- 保持评论简洁具体 — 引用实际项目名称、数字、JSON 中的时间戳。
- `top_prompts` 已包含子代理 token，并将任务通知续接合并到原始提示中。
- 如果 JSON >2MB，在嵌入前将 `top_prompts` 裁剪到 100 条，`cache_breaks` 裁剪到 100 条（它们应该已经被限制了）。
