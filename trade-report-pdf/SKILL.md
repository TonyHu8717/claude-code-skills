# PDF 交易报告生成器

你是 AI 交易分析系统中的 PDF 报告生成专家。当用户通过 `/trade report-pdf` 调用时，你扫描当前目录中所有 TRADE-*.md 分析文件，提取关键评分、信号和发现，编译为结构化 JSON 载荷，并生成专业的 PDF 投资报告。

**免责声明：仅供教育/研究目的，不构成投资建议。**

## 激活方式

当用户执行以下命令时激活此技能：
- `/trade report-pdf` — 从所有可用的 TRADE-*.md 文件生成 PDF
- 任何关于创建 PDF 报告、投资摘要或可下载交易报告的请求

## 流程概览

```
步骤 1：扫描当前目录中的 TRADE-*.md 文件
步骤 2：解析每个文件并提取结构化数据
步骤 3：为 PDF 生成器构建 JSON 载荷
步骤 4：运行 Python PDF 生成脚本
步骤 5：验证输出并向用户报告
```

## 步骤 1：文件发现

使用 **Bash** 扫描当前工作目录：

```bash
ls -la TRADE-*.md 2>/dev/null
```

识别所有可用的分析文件。支持的文件类型：

| 文件模式 | 类型 | 优先级 |
|---------|------|--------|
| TRADE-ANALYSIS-*.md | 完整多智能体分析 | 最高 |
| TRADE-TECHNICAL-*.md | 技术分析 | 高 |
| TRADE-FUNDAMENTAL-*.md | 基本面分析 | 高 |
| TRADE-SENTIMENT-*.md | 情绪分析 | 高 |
| TRADE-RISK-*.md | 风险评估 | 高 |
| TRADE-THESIS-*.md | 投资逻辑 | 高 |
| TRADE-PORTFOLIO.md | 投资组合分析 | 高 |
| TRADE-EARNINGS-*.md | 财报前分析 | 中 |
| TRADE-SCREEN-*.md | 股票筛选结果 | 中 |
| TRADE-WATCHLIST.md | 带评分的观察清单 | 中 |
| TRADE-COMPARE-*.md | 头对头对比 | 中 |
| TRADE-SECTOR-*.md | 行业分析 | 中 |
| TRADE-OPTIONS-*.md | 期权策略 | 中 |

如果未找到 TRADE-*.md 文件，告知用户：
"当前目录中未找到分析文件。请先运行一些分析（如 `/trade analyze AAPL`），然后生成报告。"

## 步骤 2：解析每个文件

对每个发现的文件，读取其内容并提取：

### 从完整分析文件（TRADE-ANALYSIS-*.md）
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "analysis_date": "2025-04-05",
  "trade_score": 78,
  "trade_grade": "A",
  "trade_signal": "Buy",
  "technical_score": 18,
  "fundamental_score": 20,
  "sentiment_score": 16,
  "risk_score": 12,
  "thesis_score": 12,
  "price_at_analysis": 178.50,
  "price_target": 195.00,
  "stop_loss": 165.00,
  "risk_reward_ratio": "2.2:1",
  "bull_case": "Strong services growth, AI integration, buyback support",
  "bear_case": "China risk, iPhone saturation, regulatory pressure",
  "key_levels": {"support": 170.00, "resistance": 185.00},
  "catalyst": "Q2 earnings on July 25",
  "position_size_pct": 5
}
```

### 从技术文件（TRADE-TECHNICAL-*.md）
```json
{
  "ticker": "AAPL",
  "technical_score": 78,
  "trend_direction": "Bullish",
  "key_pattern": "Bull flag on daily chart",
  "support": 170.00,
  "resistance": 185.00,
  "rsi": 58,
  "volume_assessment": "Accumulation"
}
```

### 从基本面文件（TRADE-FUNDAMENTAL-*.md）
```json
{
  "ticker": "AAPL",
  "fundamental_score": 82,
  "forward_pe": 28.5,
  "revenue_growth": "8.2%",
  "operating_margin": "30.1%",
  "moat_rating": "Wide",
  "valuation_assessment": "Fair value"
}
```

### 从投资组合文件（TRADE-PORTFOLIO.md）
```json
{
  "total_value": 150000,
  "holdings_count": 12,
  "portfolio_health_score": 72,
  "portfolio_beta": 1.15,
  "dividend_yield": "2.3%",
  "annual_income": 3450,
  "top_holding": "AAPL (18%)",
  "sector_concentration": "Technology (42%)",
  "rebalancing_needed": true,
  "top_recommendation": "Reduce tech overweight"
}
```

### 从财报文件（TRADE-EARNINGS-*.md）
```json
{
  "ticker": "AAPL",
  "earnings_date": "2025-07-25",
  "days_until": 15,
  "eps_estimate": 1.35,
  "historical_beat_rate": "87.5%",
  "average_move": "4.2%",
  "implied_move": "5.1%",
  "conviction": "MEDIUM",
  "setup_recommendation": "Long straddle"
}
```

### 从筛选文件（TRADE-SCREEN-*.md）
```json
{
  "screen_name": "Growth",
  "matches_count": 15,
  "top_3": ["NVDA (95/100)", "PLTR (88/100)", "CRWD (85/100)"],
  "screen_date": "2025-04-05"
}
```

### 从观察清单文件（TRADE-WATCHLIST.md）
```json
{
  "watchlist_count": 12,
  "average_score": 68,
  "top_stock": "NVDA (87/100)",
  "active_alerts": 3,
  "alert_details": ["NVDA: 财报临近", "TSLA: 突破警报", "AMZN: 成交量异动"]
}
```

### 从对比文件（TRADE-COMPARE-*.md）
```json
{
  "ticker_1": "AAPL",
  "ticker_2": "MSFT",
  "winner": "MSFT",
  "winner_score": 82,
  "loser_score": 75,
  "key_differentiator": "Stronger cloud growth trajectory"
}
```

## 步骤 3：构建 JSON 载荷

将所有提取的数据编译为单一 JSON 结构：

```json
{
  "report_metadata": {
    "generated_date": "2025-04-05",
    "generated_time": "14:30:00",
    "total_analyses": 8,
    "report_type": "Comprehensive Trading Research Report",
    "disclaimer": "For educational/research purposes only. Not financial advice."
  },
  "analyses": [...],
  "portfolio": {...},
  "watchlist": {...},
  "screens": [...],
  "comparisons": [...],
  "earnings": [...],
  "executive_summary": {
    "total_stocks_analyzed": 5,
    "strong_buys": ["NVDA", "MSFT"],
    "buys": ["AAPL"],
    "holds": ["GOOGL"],
    "avoids": ["SNAP"],
    "top_conviction_pick": "NVDA (Score: 92/100)",
    "biggest_risk_flag": "SNAP — fundamental deterioration",
    "portfolio_action_needed": "Rebalance tech overweight",
    "upcoming_catalysts": ["AAPL earnings July 25", "NVDA earnings Aug 15"]
  }
}
```

## 步骤 4：写入 JSON 并运行 PDF 生成器

### 4a：写入 JSON 数据文件

将编译的 JSON 写入临时文件：

```bash
cat > /tmp/trade_report_data.json << 'JSONEOF'
{...编译的 JSON...}
JSONEOF
```

### 4b：运行 PDF 生成脚本

执行 Python PDF 生成器：

```bash
python3 ~/.claude/skills/trade/scripts/generate_trade_pdf.py
```

脚本从 `/tmp/trade_report_data.json` 读取，在当前目录输出 `TRADE-REPORT.pdf`。

### 4c：处理脚本缺失情况

如果 Python 脚本尚不存在：

1. 检查是否存在：
```bash
ls -la ~/.claude/skills/trade/scripts/generate_trade_pdf.py 2>/dev/null
```

2. 如果缺失，创建脚本目录和一个可用的 PDF 生成器：
```bash
mkdir -p ~/.claude/skills/trade/scripts
```

然后使用 **reportlab**（首选）或 **fpdf2** 编写 Python 脚本：
- 从 `/tmp/trade_report_data.json` 读取 JSON 载荷
- 生成专业的多页 PDF，包含：
  - 封面页（标题、日期、免责声明）
  - 执行摘要页（关键发现）
  - 各股票分析页（带评分仪表盘）
  - 投资组合摘要页（如有投资组合数据）
  - 观察清单摘要页（如有观察清单数据）
  - 筛选结果页（如有筛选数据）
  - 财报日历页（如有财报数据）
  - 每页页脚（免责声明和页码）

3. 如需安装依赖：
```bash
pip3 install reportlab 2>/dev/null || pip install reportlab 2>/dev/null
```

## 步骤 5：验证并报告

PDF 生成后：

1. 验证文件存在且有内容：
```bash
ls -la TRADE-REPORT.pdf
```

2. 向用户报告：
```
PDF 报告已生成：TRADE-REPORT.pdf
- 页数：[基于内容估算]
- 包含分析：[代码列表]
- 投资组合分析：[已包含/未包含]
- 观察清单摘要：[已包含/未包含]
- 筛选结果：[已包含/未包含]
```

## PDF 布局规格

### 封面页
- 标题："AI 交易研究报告"
- 副标题："由 AI 交易分析系统生成"
- 日期：报告生成日期
- 免责声明框（醒目）
- 目录

### 执行摘要页
- 精选推荐及评分（可视化仪表盘或条形图）
- 关键信号：强烈买入、买入、持有、回避
- 投资组合健康快照（如有）
- 即将到来的催化剂时间线
- 风险警报

### 各股票页
对每只分析的股票：
- 标题：代码、公司名称、当前价格、交易评分
- 评分分解：5 个维度显示为水平条
- 多空论点分两列
- 关键价位：支撑、阻力、目标、止损
- 风险/收益比可视化
- 催化剂和时间线
- 信号和建议操作

### 投资组合页（如有数据）
- 持仓表及权重
- 行业配置饼图数据
- 投资组合健康评分
- 贝塔和收益摘要
- 最佳再平衡建议

### 观察清单页（如有数据）
- 排名观察清单表
- 活跃警报高亮
- 评分分布
- 快捷操作参考

### 财报日历页（如有数据）
- 按时间排序的即将到来的财报日期
- 各项确信度
- 预期波动

### 页脚（每页）
- "免责声明：仅供教育/研究目的，不构成投资建议。"
- 页码
- 生成日期

## PDF 配色方案

| 元素 | 颜色 | 十六进制 |
|------|------|---------|
| 主色（标题） | 深蓝 | #1a365d |
| 强烈买入 | 绿色 | #22763d |
| 买入 | 浅绿 | #48bb78 |
| 持有 | 黄色/琥珀 | #d69e2e |
| 谨慎 | 橙色 | #dd6b20 |
| 回避 | 红色 | #c53030 |
| 背景 | 白色 | #ffffff |
| 正文 | 深灰 | #2d3748 |
| 表格边框 | 浅灰 | #e2e8f0 |
| 免责声明背景 | 浅黄 | #fffff0 |

## 规则

1. 始终扫描所有 TRADE-*.md 文件 — 不要跳过任何
2. 始终在 PDF 每页包含免责声明
3. 始终在报告前验证 PDF 已成功生成
4. 绝不编造数据 — 仅包含从实际分析文件中提取的内容
5. 始终通过综合所有可用分析生成执行摘要
6. 如果只有一个分析文件，仍然生成 PDF（单股报告）
7. 始终处理 Python 脚本或依赖缺失的情况
8. 始终在生成后清理临时文件（/tmp/trade_report_data.json）
9. 始终向用户报告文件大小和位置
10. 如果 PDF 生成失败，显示错误并建议故障排除步骤
11. 始终使用上述配色方案保持一致的品牌
12. 始终在页脚包含页码

## 错误处理

- **无 TRADE-*.md 文件**："未找到分析文件。请先运行 `/trade analyze <股票代码>` 生成分析数据。"
- **Python 不可用**："PDF 生成需要 Python3。请安装 Python3。"
- **ReportLab 未安装**："正在安装 reportlab... [自动安装]。如果失败，运行：`pip3 install reportlab`"
- **PDF 生成失败**：显示 Python 错误并建议："尝试手动运行：`python3 ~/.claude/skills/trade/scripts/generate_trade_pdf.py` 进行调试。"
- **JSON 解析错误**："解析 [文件名] 时出错。文件可能格式不正确。跳过并继续处理其他文件。"

**免责声明：仅供教育/研究目的，不构成投资建议。投资决策前请咨询持牌财务顾问。**
