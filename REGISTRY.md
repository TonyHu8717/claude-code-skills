# Claude Code Skills Registry

> 统一技能目录 - 共 329 个技能，分类管理，同步至 GitHub 进行版本控制。

## 目录结构

```
.claude/skills/
|-- REGISTRY.md          # 本文件：技能索引
|-- .gitignore           # Git 忽略规则
|-- {skill-name}/        # 每个技能一个目录
|   |-- SKILL.md         # 技能定义（必需）
|   `-- ...              # 附加资源（参考文档、模板、示例等）
```

---

### AI/LLM 开发

| 技能名 | 说明 |
|--------|------|
| [agent-builder](agent-builder/SKILL.md) | 为任何领域设计和构建 AI 代理。当用户： (1) 要求"创建代理"、"构建助手"或"设计 AI 系统" (2) 想要理解代理架构、代理模式或自主 AI (3) 需要帮助理解能力、子代理、规划或技能机 |
| [agent-development](agent-development/SKILL.md) | 当用户要求"创建代理"、"添加代理"、"编写子代理"、"代理前置信息"、"何时使用description"、"代理示例"、"代理工具"、"代理颜色"、"自主代理"，或需要关于代理结构、系统提示词、触发 |
| [autoresearch](autoresearch/SKILL.md) | 具有严格评估器契约、markdown 决策日志和最大运行时间停止行为的有状态单任务改进循环 |
| [benchmark-models](benchmark-models/SKILL.md) | 跨模型基准测试，用于 gstack 技能。将相同的提示词通过 Claude、 GPT（通过 Codex CLI）和 Gemini 并行运行——比较延迟、令牌、成本， 并可选地通过 LLM 裁判评估质量 |
| [claude-api](claude-api/SKILL.md) | "构建、调试和优化 Claude API / Anthropic SDK 应用。使用此技能构建的应用应包含提示缓存。还处理现有 Claude API 代码在 Claude 模型版本之间的迁移（4.5  |
| [embedding-strategies](embedding-strategies/SKILL.md) | 为语义搜索和 RAG 应用选择和优化嵌入模型。在选择嵌入模型、实现分块策略或为特定领域优化嵌入质量时使用。 |
| [llm-evaluation](llm-evaluation/SKILL.md) | 实现全面的 LLM 应用评估策略，涵盖自动化指标、人工反馈和基准测试。用于测试 LLM 性能、衡量 AI 应用质量或建立评估框架。 |
| [mcp-builder](mcp-builder/SKILL.md) | 构建 MCP（模型上下文协议）服务器，为 Claude 提供新能力。当用户想要创建 MCP 服务器、为 Claude 添加工具或集成外部服务时使用。 |
| [prompt-engineering-patterns](prompt-engineering-patterns/SKILL.md) | 掌握高级提示工程技术，以最大化 LLM 在生产环境中的性能、可靠性和可控性。在优化提示、改进 LLM 输出或设计生产提示模板时使用。 |
| [rag-implementation](rag-implementation/SKILL.md) | 为 LLM 应用构建带向量数据库和语义搜索的检索增强生成（RAG）系统。在实现知识驱动的 AI、构建文档问答系统或将 LLM 与外部知识库集成时使用。 |
| [self-improve](self-improve/SKILL.md) | 具有锦标赛选择功能的自主进化代码改进引擎 |
| [skill-creator](skill-creator/SKILL.md) | 创建新技能、修改和改进现有技能，以及衡量技能性能。当用户想从零开始创建技能、编辑或优化现有技能、运行评估测试技能、使用方差分析对技能性能进行基准测试，或优化技能描述以提高触发准确性时使用。 |

### Agent/自动化

| 技能名 | 说明 |
|--------|------|
| [autopilot](autopilot/SKILL.md) | 从想法到工作代码的完全自主执行 |
| [autoplan](autoplan/SKILL.md) | 自动审查流水线 — 从磁盘读取完整的 CEO、设计、工程和 DX 审查技能， 使用 6 个决策原则依次运行并自动决策。在最终审批门控处呈现品味决策 （接近方案、边界范围、codex 分歧）。一个命令， |
| [autoresearch](autoresearch/SKILL.md) | 具有严格评估器契约、markdown 决策日志和最大运行时间停止行为的有状态单任务改进循环 |
| [browse](browse/SKILL.md) | 用于 QA 测试和站点体验的快速无头浏览器。导航任意 URL、与元素交互、验证页面状态、 对操作前后进行差异对比、拍摄带注释的截图、检查响应式布局、测试表单和上传、 处理对话框以及断言元素状态。每条命 |
| [cancel](cancel/SKILL.md) | 取消任何活跃的 OMC 模式（autopilot、ralph、ultrawork、ultraqa、swarm、ultrapilot、pipeline、team） |
| [careful](careful/SKILL.md) | 破坏性命令安全防护栏。在 rm -rf、DROP TABLE、force-push、git reset --hard、 kubectl delete 及类似破坏性操作前发出警告。用户可以覆盖每个警告。 |
| [codex](codex/SKILL.md) | OpenAI Codex CLI 包装器——三种模式。代码审查：通过 codex review 进行独立的 diff 审查， 带有通过/失败门禁。挑战：对抗模式，尝试破坏你的代码。 咨询：向 code |
| [configure-notifications](configure-notifications/SKILL.md) | 通过自然语言配置通知集成（Telegram、Discord、Slack） |
| [deepinit](deepinit/SKILL.md) | 使用分层 AGENTS.md 文档进行深度代码库初始化 |
| [external-context](external-context/SKILL.md) | 调用并行文档专家代理进行外部网络搜索和文档查找 |
| [freeze](freeze/SKILL.md) | 将文件编辑限制在特定目录内。阻止对允许路径之外的文件进行 Edit 和 Write 操作。在调试时用于防止意外"修复"无关代码，或在需要将更改 范围限定在一个模块时使用。 当要求"冻结"、"限制编辑" |
| [guard](guard/SKILL.md) | 完整安全模式：破坏性命令警告 + 目录范围编辑限制。 结合 /careful（在 rm -rf、DROP TABLE、force-push 等操作前发出警告）和 /freeze（阻止指定目录外的编辑） |
| [hud](hud/SKILL.md) | 配置 HUD 显示选项（布局、预设、显示元素） |
| [investigate](investigate/SKILL.md) | 系统化调试与根本原因调查。四个阶段：调查、 分析、假设、实施。铁律：没有根本原因调查就不修复。 当要求"调试这个"、"修复这个 bug"、"为什么这坏了"、 "调查这个错误"或"根本原因分析"时使用。 |
| [openapi-spec-generation](openapi-spec-generation/SKILL.md) | 从代码生成和维护 OpenAPI 3.1 规范，支持设计优先规范和验证模式。在创建 API 文档、生成 SDK 或确保 API 合约合规时使用。 |
| [plan](plan/SKILL.md) | 带可选访谈工作流的战略规划 |
| [plan-ceo-review](plan-ceo-review/SKILL.md) | CEO/创始人模式计划审查。重新思考问题，寻找 10 星产品，挑战前提假设， 在能创造更好产品时扩展范围。四种模式：范围扩展（大胆梦想）、选择性扩展 （保持范围 + 精选扩展）、保持范围（最大严谨度） |
| [plan-design-review](plan-design-review/SKILL.md) | 设计师之眼计划审查——交互式，类似 CEO 和工程审查。 对每个设计维度评分 0-10，解释什么能让它达到 10 分，然后修改计划以达到目标。 在计划模式下工作。对于线上站点视觉审计，使用 /desi |
| [plan-devex-review](plan-devex-review/SKILL.md) | 交互式开发者体验计划审查。探索开发者画像，与竞争对手基准对比，设计魔法时刻， 在评分前追踪摩擦点。三种模式：DX 扩展（竞争优势）、DX 打磨（让每个触点无懈可击）、 DX 分诊（仅关键缺口）。 当用 |
| [plan-eng-review](plan-eng-review/SKILL.md) | 工程经理模式计划审查。锁定执行计划——架构、数据流、图表、边界情况、测试覆盖、性能。 以有主见的建议交互式地逐步审查问题。当用户要求"审查架构"、"工程审查"或"锁定计划"时使用。 当用户有计划或设计 |
| [plan-tune](plan-tune/SKILL.md) | gstack 自调优问题灵敏度 + 开发者心理画像（v1：观察模式）。 审查哪些 AskUserQuestion 提示在 gstack 技能中触发，设置每个问题的偏好 （永不询问 / 总是询问 / 仅 |
| [plugin-settings](plugin-settings/SKILL.md) | 当用户询问"插件设置"、"存储插件配置"、"用户可配置插件"、".local.md 文件"、"插件状态文件"、"读取 YAML frontmatter"、"按项目设置插件"，或希望使插件行为可配置时， |
| [plugin-structure](plugin-structure/SKILL.md) | 当用户要求"创建插件"、"搭建插件骨架"、"理解插件结构"、"组织插件组件"、"设置 plugin.json"、"使用 ${CLAUDE_PLUGIN_ROOT}"、"添加 commands/agen |
| [release](release/SKILL.md) | 通用发布助手 -- 分析仓库发布规则，缓存到 .omc/RELEASE_RULE.md，然后引导发布流程 |
| [remember](remember/SKILL.md) | 审查可复用的项目知识，决定哪些内容应存入项目记忆、记事本或持久化文档 |
| [scrape](scrape/SKILL.md) | 从网页提取数据。首次调用新意图时通过 $B 基元原型化流程并返回 JSON。 后续匹配意图的调用会路由到已编码的 browser-skill，约 200ms 返回。 只读 — 对于变更性流程（表单填写 |
| [ship](ship/SKILL.md) | 发布工作流：检测并合并基础分支、运行测试、审查 diff、升级 VERSION、 更新 CHANGELOG、提交、推送、创建 PR。当用户要求 "ship"、"deploy"、 "push to ma |
| [unfreeze](unfreeze/SKILL.md) | 清除 /freeze 设置的冻结边界，允许再次编辑所有目录。 当你想在不结束会话的情况下扩大编辑范围时使用。 当被要求"解冻"、"解锁编辑"、"移除冻结"或"允许所有编辑"时使用。(gstack) t |
| [verify](verify/SKILL.md) | 在声称完成之前验证更改是否真正有效 |

### Init/内置

| 技能名 | 说明 |
|--------|------|
| [review](review/SKILL.md) | 着陆前 PR 审查。分析相对于基础分支的 diff，检查 SQL 安全、LLM 信任 边界违规、条件副作用和其他结构性问题。当被要求"审查此 PR"、"代码审查"、 "着陆前审查"或"检查我的 dif |

### Memory/记忆

| 技能名 | 说明 |
|--------|------|
| [memory-forensics](memory-forensics/SKILL.md) | 掌握内存取证技术，包括内存获取、进程分析和使用 Volatility 及相关工具进行工件提取。当分析内存转储、调查事件或从 RAM 捕获中进行恶意软件分析时使用。 |
| [memory-safety-patterns](memory-safety-patterns/SKILL.md) | 跨 Rust、C++ 和 C 实现内存安全编程，涵盖 RAII、所有权、智能指针和资源管理。当编写安全的系统代码、管理资源或防止内存 bug 时使用。 |
| [session-report](session-report/SKILL.md) | 从 ~/.claude/projects 转录生成可浏览的 Claude Code 会话使用 HTML 报告（token、缓存、子代理、技能、高消耗提示）。 |
| [writer-memory](writer-memory/SKILL.md) | 作家的代理记忆系统 - 跟踪角色、关系、场景和主题 |

### 交易/金融

| 技能名 | 说明 |
|--------|------|
| [billing-automation](billing-automation/SKILL.md) | 构建自动化计费系统，用于循环支付、发票生成、订阅生命周期和催收管理。用于实现订阅计费、自动化发票生成或管理循环支付系统时使用。 |
| [excel-dcf-modeler](excel-dcf-modeler/SKILL.md) | 在 Excel 中构建折现现金流 (DCF) 估值模型，包含自由现金流预测、 WACC 计算和敏感性分析。面向投资银行和企业金融工作流。 当要求创建 DCF 模型、计算企业价值、对公司估值或构建估值模 |
| [excel-lbo-modeler](excel-lbo-modeler/SKILL.md) | 在 Excel 中创建杠杆收购 (LBO) 模型，包含资金来源与用途、债务计划、 现金流瀑布和 IRR 计算。面向私募股权和投资银行工作流。 当要求创建 LBO 模型、构建收购模型、计算 PE 回报或 |
| [excel-pivot-wizard](excel-pivot-wizard/SKILL.md) | 使用自然语言命令从原始数据生成数据透视表和图表。 面向在 Excel 中工作的业务分析师和数据团队。 当要求创建数据透视表、按类别汇总数据、按区域分析销售、 显示收入分解或构建交叉表分析时使用。 使用 |
| [excel-variance-analyzer](excel-variance-analyzer/SKILL.md) | 在 Excel 中自动执行预算与实际差异分析，包含标记、评注和执行摘要。 面向 FP&A 团队和财务报告工作流。 当要求分析预算差异、比较实际与预测、创建差异报告或解释预算差异时使用。 使用"分析预算 |
| [paypal-integration](paypal-integration/SKILL.md) | 集成 PayPal 支付处理，支持快速结账、订阅和退款管理。在实现 PayPal 支付、处理在线交易或构建电子商务结账流程时使用。 |
| [risk-metrics-calculation](risk-metrics-calculation/SKILL.md) | 计算投资组合风险指标，包括 VaR、CVaR、Sharpe、Sortino 和回撤分析。在衡量投资组合风险、实施风险限制或构建风险监控系统时使用。 |
| [startup-financial-modeling](startup-financial-modeling/SKILL.md) | 为早期创业公司构建包含收入预测、成本结构、现金流分析和情景规划的综合 3-5 年财务模型。在创建财务预测、计算烧钱率或融资跑道、模拟融资场景或为种子轮/A 轮融资准备投资者级财务数据时使用此技能。 |
| [startup-metrics-framework](startup-metrics-framework/SKILL.md) | 跟踪、计算和优化 SaaS、市场、消费和 B2B 创业公司从种子轮到 A 轮的关键绩效指标，包括单位经济性、增长效率和现金管理。在定义指标框架、计算 CAC/LTV/烧钱倍数、对标业务健康度或为投资者 |
| [stock-deep-analysis](stock-deep-analysis/SKILL.md) | 六维个股深度分析 — 从赛道判断、行业结构、竞争格局、商业模式、估值与预期、风险分析六个维度全面评估个股投资价值 |
| [stripe-integration](stripe-integration/SKILL.md) | 实现 Stripe 支付处理，构建健壮的、PCI 合规的支付流程，包括结账、订阅和 Webhook。适用于集成 Stripe 支付、构建订阅系统或实现安全结账流程。 |
| [trade-analyze](trade-analyze/SKILL.md) | 完整股票分析编排器 — 启动 5 个并行子代理进行全面多维度股票分析，生成综合交易评分 |
| [trade-compare](trade-compare/SKILL.md) | 股票头对头对比 — 接受两只股票代码，从估值、成长性、盈利能力、技术面、情绪、风险画像和分析师共识等多个维度进行对比，输出评分比较表和总体推荐。 |
| [trade-earnings](trade-earnings/SKILL.md) |  |
| [trade-fundamental](trade-fundamental/SKILL.md) | 基本面分析代理 — 估值、增长、盈利能力、资产负债表、竞争护城河和管理质量分析，提供基本面评分（0-100） |
| [trade-options](trade-options/SKILL.md) | 期权策略顾问 — 分析隐含波动率、IV 排名/百分比、预期波动、看跌/看涨比率、最大痛点、异常活动，并根据交易者的方向性观点推荐具有风险/收益特征的具体期权策略。 |
| [trade-portfolio](trade-portfolio/SKILL.md) |  |
| [trade-quick](trade-quick/SKILL.md) | 60 秒股票快照 — 快速评估信号、关键因素和价位，无需启动子代理 |
| [trade-report-pdf](trade-report-pdf/SKILL.md) |  |
| [trade-risk](trade-risk/SKILL.md) | 风险评估与仓位管理 — 分析波动率、回撤情景、相关性、流动性，提供多种仓位计算器（凯利准则、固定百分比、波动率调整），并对任何公开交易股票给出综合风险评分（0-100）。 |
| [trade-screen](trade-screen/SKILL.md) |  |
| [trade-sector](trade-sector/SKILL.md) | 行业轮动与分析 — 分析行业动量排名、资金流向、经济周期定位、相对强度、各行业顶级股票、估值和轮动信号，识别机构资本的流向。 |
| [trade-sentiment](trade-sentiment/SKILL.md) | 情绪与动量分析代理 — 新闻情绪、社交媒体热度、分析师评级、机构活动、内部人交易和做空比例，提供情绪评分（0-100） |
| [trade-technical](trade-technical/SKILL.md) | 技术分析代理 — 价格行为、指标、图表形态、支撑/阻力和动量分析，提供技术评分（0-100） |
| [trade-thesis](trade-thesis/SKILL.md) | 投资论点生成器 — 构建完整的结构化投资论点，包含多空论点、催化剂时间线、入场/退出策略、仓位规模和不对称性评估，适用于任何公开交易股票。 |
| [trade-watchlist](trade-watchlist/SKILL.md) |  |

### 代码/开发

| 技能名 | 说明 |
|--------|------|
| [angular-migration](angular-migration/SKILL.md) | 使用混合模式、增量组件重写和依赖注入更新从 AngularJS 迁移到 Angular。在升级 AngularJS 应用、规划框架迁移或现代化旧版 Angular 代码时使用。 |
| [bash-defensive-patterns](bash-defensive-patterns/SKILL.md) | 掌握生产级脚本的防御性 Bash 编程技术。用于编写健壮的 Shell 脚本、CI/CD 流水线或需要容错和安全性的系统工具时使用。 |
| [build-mcp-app](build-mcp-app/SKILL.md) | 当用户想要构建"MCP 应用"、为 MCP 服务器添加"交互式 UI"或"组件"、"在聊天中渲染组件"、构建"MCP UI 资源"、制作在对话中内联显示"表单"、"选择器"、"仪表板"或"确认对话框" |
| [build-mcp-server](build-mcp-server/SKILL.md) | 当用户要求"构建 MCP 服务器"、"创建 MCP"、"制作 MCP 集成"、"为 Claude 封装 API"、"向 Claude 暴露工具"、"制作 MCP 应用"或讨论使用模型上下文协议构建内容 |
| [build-mcpb](build-mcpb/SKILL.md) | 当用户想要"打包 MCP 服务器"、"捆绑 MCP"、"制作 MCPB"、"发布本地 MCP 服务器"、"分发本地 MCP"、讨论 ".mcpb 文件"、提到将 Node 或 Python 运行时与  |
| [code-review](code-review/SKILL.md) | 执行全面的代码审查，涵盖安全性、性能和可维护性分析。当用户要求审查代码、检查 bug 或审计代码库时使用。 |
| [database-migration](database-migration/SKILL.md) | 跨 ORM 和平台执行数据库迁移，包含零停机策略、数据转换和回滚程序。在迁移数据库、更改 schema、执行数据转换或实施零停机部署策略时使用。 |
| [debug](debug/SKILL.md) | 使用日志、追踪、状态和聚焦复现来诊断当前 OMC 会话或仓库状态 |
| [debugging-strategies](debugging-strategies/SKILL.md) | 掌握系统化调试技术、性能分析工具和根本原因分析，以高效追踪任何代码库或技术栈中的 bug。在调查 bug、性能问题或意外行为时使用。 |
| [dependency-upgrade](dependency-upgrade/SKILL.md) | 管理主要依赖版本升级，包括兼容性分析、分阶段发布和全面测试。在升级框架版本、更新主要依赖或处理库中的破坏性变更时使用。 |
| [dotnet-backend-patterns](dotnet-backend-patterns/SKILL.md) | 掌握 C#/.NET 后端开发模式，用于构建稳健的 API、MCP 服务器和企业应用。涵盖 async/await、依赖注入、Entity Framework Core、Dapper、配置、缓存和使用 |
| [example-command](example-command/SKILL.md) | 一个示例用户调用技能，演示 frontmatter 选项和 skills/<name>/SKILL.md 布局 |
| [example-skill](example-skill/SKILL.md) | 当用户要求"演示技能"、"展示技能格式"、"创建技能模板"或讨论技能开发模式时使用此技能。提供创建 Claude Code 插件技能的参考模板。 |
| [fastapi-templates](fastapi-templates/SKILL.md) | 创建生产就绪的 FastAPI 项目，包含异步模式、依赖注入和全面的错误处理。在构建新的 FastAPI 项目或设置后端 API 项目时使用。 |
| [go-concurrency-patterns](go-concurrency-patterns/SKILL.md) | 掌握 Go 并发编程，包括 goroutine、channel、同步原语和 context。在构建并发 Go 应用、实现工作池或调试竞态条件时使用。 |
| [javascript-testing-patterns](javascript-testing-patterns/SKILL.md) | 使用 Jest、Vitest 和 Testing Library 实现全面的测试策略，包括单元测试、集成测试和端到端测试，支持 mock、fixture 和测试驱动开发。在编写 JavaScript/ |
| [monorepo-management](monorepo-management/SKILL.md) | 掌握使用 Turborepo、Nx 和 pnpm 工作区进行 monorepo 管理，构建高效的、可扩展的多包仓库，实现优化的构建和依赖管理。在设置 monorepo、优化构建或管理共享依赖时使用。 |
| [nextjs-app-router-patterns](nextjs-app-router-patterns/SKILL.md) | 掌握 Next.js 14+ App Router，包括服务器组件、流式传输、并行路由和高级数据获取。在构建 Next.js 应用、实现 SSR/SSG 或优化 React 服务器组件时使用。 |
| [nodejs-backend-patterns](nodejs-backend-patterns/SKILL.md) | 使用 Express/Fastify 构建生产就绪的 Node.js 后端服务，实现中间件模式、错误处理、身份验证、数据库集成和 API 设计最佳实践。在创建 Node.js 服务器、REST API |
| [nx-workspace-patterns](nx-workspace-patterns/SKILL.md) | 配置和优化 Nx monorepo 工作区。在设置 Nx、配置项目边界、优化构建缓存或实现受影响命令时使用。 |
| [parallel-debugging](parallel-debugging/SKILL.md) | 使用竞争假设进行并行调查、证据收集和根因仲裁来调试复杂问题。在调试具有多个潜在原因的错误、执行根因分析或组织并行调查工作流时使用此技能。 |
| [postgresql](postgresql/SKILL.md) | 在设计或审查 PostgreSQL 特定模式时使用此技能。涵盖最佳实践、数据类型、索引、约束、性能模式和高级功能。 |
| [python-anti-patterns](python-anti-patterns/SKILL.md) | 在审查 Python 代码中应避免的常见反模式时使用此技能。在审查代码、最终确定实现或调试可能源于已知不良实践的问题时，将其作为检查清单使用。 |
| [python-background-jobs](python-background-jobs/SKILL.md) | Python 后台作业模式，包括任务队列、工作进程和事件驱动架构。在实现异步任务处理、作业队列、长时间运行的操作或将工作从请求/响应循环中解耦时使用。 |
| [python-code-style](python-code-style/SKILL.md) | Python 代码风格、代码检查、格式化、命名规范和文档标准。在编写新代码、审查风格、配置代码检查工具、编写文档字符串或制定项目标准时使用。 |
| [python-configuration](python-configuration/SKILL.md) | 通过环境变量和类型化设置进行 Python 配置管理。在外部化配置、设置 pydantic-settings、管理密钥或实现环境特定行为时使用。 |
| [python-design-patterns](python-design-patterns/SKILL.md) | Python 设计模式，包括 KISS、关注点分离、单一职责和组合优于继承。在从头设计新服务或组件并选择如何分层职责时、在重构增长过大的上帝类或单体函数时、在决定是添加新抽象还是接受重复时、在评估拉取 |
| [python-error-handling](python-error-handling/SKILL.md) | Python 错误处理模式，包括输入验证、异常层次结构和部分失败处理。在实现验证逻辑、设计异常策略、处理批量处理失败或构建健壮的 API 时使用。 |
| [python-observability](python-observability/SKILL.md) | Python 可观测性模式，包括结构化日志、指标和分布式追踪。在添加日志、实现指标收集、设置追踪或调试生产系统时使用。 |
| [python-packaging](python-packaging/SKILL.md) | 创建可分发的 Python 包，包含适当的项目结构、setup.py/pyproject.toml，以及发布到 PyPI。在打包 Python 库、创建 CLI 工具或分发 Python 代码时使用。 |
| [python-performance-optimization](python-performance-optimization/SKILL.md) | 使用 cProfile、内存分析器和性能最佳实践来分析和优化 Python 代码。在调试缓慢的 Python 代码、优化瓶颈或提高应用程序性能时使用。 |
| [python-project-structure](python-project-structure/SKILL.md) | Python 项目组织、模块架构和公共 API 设计。在设置新项目、组织模块、使用 __all__ 定义公共接口或规划目录布局时使用。 |
| [python-resilience](python-resilience/SKILL.md) | Python 弹性模式，包括自动重试、指数退避、超时和容错装饰器。在添加重试逻辑、实现超时、构建容错服务或处理瞬态故障时使用。 |
| [python-resource-management](python-resource-management/SKILL.md) | 使用上下文管理器、清理模式和流式传输进行 Python 资源管理。在管理连接、文件句柄、实现清理逻辑或构建带累积状态的流式响应时使用。 |
| [python-testing-patterns](python-testing-patterns/SKILL.md) | 使用 pytest、fixtures、模拟和测试驱动开发实现全面的测试策略。在编写 Python 测试、设置测试套件或实现测试最佳实践时使用。 |
| [python-type-safety](python-type-safety/SKILL.md) | 使用类型提示、泛型、协议和严格类型检查实现 Python 类型安全。在添加类型注解、实现泛型类、定义结构化接口或配置 mypy/pyright 时使用。 |
| [react-modernization](react-modernization/SKILL.md) | 升级 React 应用到最新版本，从类组件迁移到 hooks，并采用并发特性。在现代化 React 代码库、迁移到 React Hooks 或升级到最新 React 版本时使用。 |
| [react-native-architecture](react-native-architecture/SKILL.md) | 使用 Expo、导航、原生模块、离线同步和跨平台模式构建生产级 React Native 应用。在开发移动应用、实现原生集成或架构 React Native 项目时使用。 |
| [react-state-management](react-state-management/SKILL.md) | 掌握现代 React 状态管理，包括 Redux Toolkit、Zustand、Jotai 和 React Query。在设置全局状态、管理服务器状态或选择状态管理方案时使用。 |
| [rust-async-patterns](rust-async-patterns/SKILL.md) | 掌握 Rust 异步编程，包括 Tokio、异步 trait、错误处理和并发模式。在构建异步 Rust 应用、实现并发系统或调试异步代码时使用。 |
| [shellcheck-configuration](shellcheck-configuration/SKILL.md) | 掌握 ShellCheck 静态分析配置和使用，提升 Shell 脚本质量。在设置代码检查基础设施、修复代码问题或确保脚本可移植性时使用。 |
| [sql-optimization-patterns](sql-optimization-patterns/SKILL.md) | 掌握 SQL 查询优化、索引策略和 EXPLAIN 分析，大幅提升数据库性能并消除慢查询。用于调试慢查询、设计数据库架构或优化应用性能时。 |
| [typescript-advanced-types](typescript-advanced-types/SKILL.md) | 掌握 TypeScript 的高级类型系统，包括泛型、条件类型、映射类型、模板字面量和工具类型，用于构建类型安全的应用程序。适用于实现复杂类型逻辑、创建可复用的类型工具，或在 TypeScript 项 |
| [web-artifacts-builder](web-artifacts-builder/SKILL.md) | 使用现代前端 Web 技术（React、Tailwind CSS、shadcn/ui）创建精巧的多组件 claude.ai HTML 工件的工具套件。适用于需要状态管理、路由或 shadcn/ui 组 |
| [webapp-testing](webapp-testing/SKILL.md) | 使用 Playwright 与本地 Web 应用程序交互和测试的工具包。支持验证前端功能、调试 UI 行为、捕获浏览器截图和查看浏览器日志。 |

### 写作/内容

| 技能名 | 说明 |
|--------|------|
| [changelog-automation](changelog-automation/SKILL.md) | 从提交、PR 和发布自动生成变更日志，遵循 Keep a Changelog 格式。在设置发布工作流、生成发布说明或标准化提交规范时使用。 |
| [document-release](document-release/SKILL.md) | 发布后文档更新。读取所有项目文档，交叉引用 差异，更新 README/ARCHITECTURE/CONTRIBUTING/CLAUDE.md 以匹配已发布内容， 润色 CHANGELOG 语气，清理  |
| [employment-contract-templates](employment-contract-templates/SKILL.md) | 创建遵循法律最佳实践的雇佣合同、录用通知书和人力资源政策文档。在起草雇佣协议、创建人力资源政策或标准化雇佣文档时使用。 |
| [writer-memory](writer-memory/SKILL.md) | 作家的代理记忆系统 - 跟踪角色、关系、场景和主题 |
| [writing-rules](writing-rules/SKILL.md) | 当用户要求"创建 hookify 规则"、"编写 hook 规则"、"配置 hookify"、"添加 hookify 规则"或需要 hookify 规则语法和模式指导时使用此技能。 |

### 前端/设计

| 技能名 | 说明 |
|--------|------|
| [algorithmic-art](algorithmic-art/SKILL.md) | 使用 p5.js 创建算法艺术，包含种子随机性和交互式参数探索。当用户请求使用代码创建艺术、生成艺术、算法艺术、流场或粒子系统时使用。创建原创算法艺术而非复制现有艺术家作品以避免版权侵犯。 |
| [banner-design](banner-design/SKILL.md) | "为社交媒体、广告、网站首屏、创意素材和印刷品设计横幅。提供多种艺术方向选项和 AI 生成的视觉元素。操作：设计、创建、生成横幅。平台：Facebook、Twitter/X、LinkedIn、YouT |
| [brand-guidelines](brand-guidelines/SKILL.md) | 将 Anthropic 官方品牌色彩和排版应用于任何可能受益于 Anthropic 外观风格的产物。当需要应用品牌色彩或样式指南、视觉格式或公司设计标准时使用。 |
| [canvas-design](canvas-design/SKILL.md) | 使用设计哲学创建精美的视觉艺术作品，输出 .png 和 .pdf 文档。当用户要求创建海报、艺术作品、设计或其他静态作品时使用此技能。创建原创视觉设计，切勿抄袭现有艺术家作品以避免版权侵权。 |
| [design-system](design-system/SKILL.md) | 令牌架构、组件规范和幻灯片生成。三层令牌（原始→语义→组件）、CSS 变量、间距/排版比例、组件规范、策略性幻灯片创建。用于设计令牌、系统化设计、品牌合规演示文稿。 |
| [design-system-patterns](design-system-patterns/SKILL.md) | 使用设计令牌、主题基础设施和组件架构模式构建可扩展的设计系统。在创建设计令牌、实现主题切换、构建组件库或建立设计系统基础时使用。 |
| [frontend-design](frontend-design/SKILL.md) | 创建独特的、生产级的前端界面，具有高设计质量。当用户要求构建网页组件、页面、工件、海报或应用程序（包括网站、着陆页、仪表板、React 组件、HTML/CSS 布局，或在美化任何 Web UI 时）时 |
| [interaction-design](interaction-design/SKILL.md) | 设计和实现微交互、动效设计、过渡动画和用户反馈模式。在为 UI 交互添加打磨效果、实现加载状态或创建令人愉悦的用户体验时使用。 |
| [responsive-design](responsive-design/SKILL.md) | 使用容器查询、流体排版、CSS Grid 和移动优先断点策略实现现代响应式布局。在构建自适应界面、实现流体布局或创建组件级响应行为时使用。 |
| [slack-gif-creator](slack-gif-creator/SKILL.md) | 为 Slack 创建优化的动画 GIF 的知识和工具。提供约束、验证工具和动画概念。当用户请求为 Slack 创建动画 GIF（如"为 Slack 做一个 X 做 Y 的 GIF"）时使用。 |
| [theme-factory](theme-factory/SKILL.md) | 用于为各类产出物（如幻灯片、文档、报告、HTML 落地页等）应用主题样式的工具集。内置 10 种预设主题（含配色与字体），可应用于已创建的任何产出物，也可即时生成新主题。 |
| [ui-styling](ui-styling/SKILL.md) | 使用 shadcn/ui 组件（基于 Radix UI + Tailwind 构建）、Tailwind CSS 实用优先样式和基于 Canvas 的视觉设计创建美观、无障碍的用户界面。适用于构建用户界 |
| [ui-ux-pro-max](ui-ux-pro-max/SKILL.md) | "面向 Web 和移动端的 UI/UX 设计智能。包含 50+ 种风格、161 种配色方案、57 种字体搭配、161 种产品类型、99 条 UX 指南和 25 种图表类型，覆盖 10 个技术栈（Rea |
| [visual-design-foundations](visual-design-foundations/SKILL.md) | 应用排版、色彩理论、间距系统和图标设计原则来创建连贯的视觉设计。适用于建立设计令牌、构建样式指南或改善视觉层次和一致性。 |

### 协作/流程

| 技能名 | 说明 |
|--------|------|
| [context-driven-development](context-driven-development/SKILL.md) | >- |
| [context-restore](context-restore/SKILL.md) | 恢复之前由 /context-save 保存的工作上下文。加载最近保存的状态 （默认跨所有分支），这样你可以从中断处继续——甚至跨 Conductor 工作区移交。 适用场景："resume"、"re |
| [context-save](context-save/SKILL.md) | 保存工作上下文。捕获 git 状态、已做出的决策和剩余工作， 以便任何未来的会话都能无缝接续。 当被要求"保存进度"、"保存状态"、"上下文保存"或"保存我的工作"时使用。 配合 /context-r |
| [office-hours](office-hours/SKILL.md) | YC 办公时间——两种模式。创业模式：六个强制性问题，揭示需求现实、现状、 迫切 specificity、最窄切入点、观察和未来适应性。构建者模式：为副业项目、 黑客马拉松、学习和开源的设计思维头脑风 |
| [pair-agent](pair-agent/SKILL.md) | 将远程 AI 代理与你的浏览器配对。一条命令生成设置密钥并打印另一代理可遵循的连接指令。 支持 OpenClaw、Hermes、Codex、Cursor 或任何能发起 HTTP 请求的代理。远程代理获 |
| [parallel-feature-development](parallel-feature-development/SKILL.md) | 通过文件所有权策略、冲突避免规则和多代理实现的集成模式来协调并行功能开发。在将大型功能分解为独立工作流、两个或更多代理需要同时实现同一系统的不同层、建立文件所有权以防止共享代码库中的合并冲突、设计接口 |
| [project-session-manager](project-session-manager/SKILL.md) | 以工作树为先的开发环境管理器，用于 issues、PRs 和功能，可选 tmux 会话 |
| [task-coordination-strategies](task-coordination-strategies/SKILL.md) | 分解复杂任务、设计依赖图、协调多智能体工作，包括任务描述编写和工作负载平衡。适用于为智能体团队拆分任务、管理任务依赖或监控团队进度时使用。 |
| [team](team/SKILL.md) | N 个协调代理在共享任务列表上协作，使用 Claude Code 原生团队功能 |
| [team-communication-protocols](team-communication-protocols/SKILL.md) | 智能体团队通信的结构化消息协议，包括消息类型选择、计划审批、关闭流程和应避免的反模式。适用于为新生成的团队建立通信规范、决定发送直接消息还是广播、团队负责人需要在工作开始前审查和批准实现者的计划、在所 |
| [team-composition-analysis](team-composition-analysis/SKILL.md) | 为从种子前到 A 轮的早期创业公司设计最优团队结构、招聘计划、薪酬策略和股权分配。在规划人员编制、确定下一个招聘角色、设定薪酬或股权范围、设计组织架构或构建与融资里程碑对齐的招聘预算时使用此技能。 |

### 学习/研究

| 技能名 | 说明 |
|--------|------|
| [benchmark](benchmark/SKILL.md) | 使用浏览守护进程进行性能回归检测。建立页面加载时间、Core Web Vitals 和资源大小的基线。在每个 PR 前后进行比较。随时间跟踪性能趋势。 适用场景："performance"、"benc |
| [book-reader-tony](book-reader-tony/SKILL.md) | 从正版在线来源阅读书籍并生成交互式 HTML 教程（全中文界面）。用户给出书名或主题，skill 搜索 Google Books、Open Library、Project Gutenberg 等正版来 |
| [competitive-landscape](competitive-landscape/SKILL.md) | 分析竞争格局，识别差异化机会，并使用波特五力模型、蓝海战略和定位图制定制胜的市场定位策略。在评估竞争对手、评估市场定位、识别可持续竞争优势或为初创企业或投资者路演准备竞争战略分析时使用此技能。 |
| [deep-dive](deep-dive/SKILL.md) | "2 阶段流水线：追踪（因果调查）-> 深度访谈（需求结晶），带 3 点注入" |
| [deep-interview](deep-interview/SKILL.md) | 苏格拉底式深度访谈，带数学模糊度门控，在自主执行前使用 |
| [evaluation-methodology](evaluation-methodology/SKILL.md) | "PluginEval 质量方法论 — 维度、评分标准、统计方法和评分公式。在理解插件质量如何衡量、解释特定维度的低分、决定如何提高技能的触发准确性或编排适配度、为您的市场校准评分阈值、或向 Neon |
| [learn](learn/SKILL.md) | 管理项目学习记录。查看、搜索、清理和导出 gstack 在各会话中积累的经验。当用户询问"我们学到了什么"、"展示学习记录"、"清理过期学习记录"或"导出学习记录"时使用。当用户询问过去的模式或疑惑" |
| [learner](learner/SKILL.md) | 从当前对话中提取学习到的技能 |
| [math-olympiad](math-olympiad/SKILL.md) | "解决竞赛数学问题（IMO、Putnam、USAMO、AIME），通过对抗性验证 |
| [self-improve](self-improve/SKILL.md) | 具有锦标赛选择功能的自主进化代码改进引擎 |

### 安全/合规

| 技能名 | 说明 |
|--------|------|
| [anti-reversing-techniques](anti-reversing-techniques/SKILL.md) | 理解软件分析中遇到的反逆向、混淆和保护技术。在分析恶意软件规避技术、为 CTF 挑战实现反调试保护、逆向工程加壳二进制文件或构建需要检测虚拟化环境的安全研究工具时使用此技能。 |
| [attack-tree-construction](attack-tree-construction/SKILL.md) | 构建全面的攻击树以可视化威胁路径。在映射攻击场景、识别防御缺口或向利益相关者沟通安全风险时使用。 |
| [auth-implementation-patterns](auth-implementation-patterns/SKILL.md) | 掌握认证和授权模式，包括 JWT、OAuth2、会话管理和 RBAC，构建安全、可扩展的访问控制系统。用于实现认证系统、保护 API 安全或调试安全问题时使用。 |
| [binary-analysis-patterns](binary-analysis-patterns/SKILL.md) | 掌握二进制分析模式，包括反汇编、反编译、控制流分析和代码模式识别。适用于分析可执行文件、理解编译后的代码或对二进制文件进行静态分析。 |
| [gdpr-data-handling](gdpr-data-handling/SKILL.md) | 实现符合 GDPR 的数据处理，包括同意管理、数据主体权利和隐私设计。在构建处理欧盟个人数据的系统、实现隐私控制或进行 GDPR 合规审查时使用。 |
| [k8s-security-policies](k8s-security-policies/SKILL.md) | 实现 Kubernetes 安全策略，包括 NetworkPolicy、PodSecurityPolicy 和 RBAC，用于生产级安全。在保护 Kubernetes 集群、实现网络隔离或强制执行 P |
| [memory-forensics](memory-forensics/SKILL.md) | 掌握内存取证技术，包括内存获取、进程分析和使用 Volatility 及相关工具进行工件提取。当分析内存转储、调查事件或从 RAM 捕获中进行恶意软件分析时使用。 |
| [mtls-configuration](mtls-configuration/SKILL.md) | 为零信任服务间通信配置双向 TLS（mTLS）。在实现零信任网络、证书管理或保护内部服务通信时使用。 |
| [pci-compliance](pci-compliance/SKILL.md) | 实现 PCI DSS 合规要求，用于安全处理支付卡数据和支付系统。在保护支付处理、实现 PCI 合规或实施支付卡安全措施时使用。 |
| [protocol-reverse-engineering](protocol-reverse-engineering/SKILL.md) | 掌握网络协议逆向工程，包括数据包分析、协议解析和自定义协议文档。在分析网络流量、理解专有协议或调试网络通信时使用。 |
| [sast-configuration](sast-configuration/SKILL.md) | 配置静态应用安全测试（SAST）工具以自动检测应用代码中的漏洞。在设置安全扫描、实施 DevSecOps 实践或自动化代码漏洞检测时使用。 |
| [secrets-management](secrets-management/SKILL.md) | 使用 Vault、AWS Secrets Manager 或原生平台解决方案为 CI/CD 管道实施安全的密钥管理。在处理敏感凭据、轮换密钥或保护 CI/CD 环境时使用。 |
| [security-requirement-extraction](security-requirement-extraction/SKILL.md) | 从威胁模型和业务上下文中推导安全需求。在将威胁转化为可操作需求、创建安全用户故事或构建安全测试用例时使用。 |

### 搜索/上下文

| 技能名 | 说明 |
|--------|------|
| [hybrid-search-implementation](hybrid-search-implementation/SKILL.md) | 结合向量和关键词搜索以提高检索效果。在实现 RAG 系统、构建搜索引擎，或当单一方法无法提供足够召回率时使用。 |
| [similarity-search-patterns](similarity-search-patterns/SKILL.md) | 使用向量数据库实现高效的相似性搜索。在构建语义搜索、实现最近邻查询或优化检索性能时使用。 |
| [writer-memory](writer-memory/SKILL.md) | 作家的代理记忆系统 - 跟踪角色、关系、场景和主题 |

### 数据/分析

| 技能名 | 说明 |
|--------|------|
| [backtesting-frameworks](backtesting-frameworks/SKILL.md) | 构建稳健的回测系统，正确处理前视偏差、幸存者偏差和交易成本。用于开发交易算法、验证策略或构建回测基础设施时使用。 |
| [data-storytelling](data-storytelling/SKILL.md) | 使用可视化、上下文和说服性结构将数据转化为引人入胜的叙述。在向利益相关者展示分析、创建数据报告或制作高管演示文稿时使用。 |
| [dbt-transformation-patterns](dbt-transformation-patterns/SKILL.md) | 掌握 dbt（数据构建工具）用于分析工程，包括模型组织、测试、文档和增量策略。在构建数据转换、创建数据模型或实施分析工程最佳实践时使用。 |
| [market-sizing-analysis](market-sizing-analysis/SKILL.md) | 使用自上而下、自下而上和价值理论方法计算市场机会的 TAM/SAM/SOM。在评估市场规模、估算可寻址收入、验证新企业的市场机会，或为创业融资演讲稿或商业计划构建投资者就绪的市场分析时使用此技能。 |
| [sector-analysis](sector-analysis/SKILL.md) | 五维赛道深度评估 — 从市场空间、增长速度、壁垒、利润集中度、预期差五个维度系统评估行业赛道价值，并筛选赛道内精选标的 |

### 文档/Office

| 技能名 | 说明 |
|--------|------|
| [docx](docx/SKILL.md) | "当用户想要创建、读取、编辑或操作 Word 文档（.docx 文件）时使用此技能。触发条件包括：任何提到 'Word doc'、'word document'、'.docx' 的情况，或需要生成带有 |
| [make-pdf](make-pdf/SKILL.md) | 将任何 markdown 文件转换为出版级 PDF。标准 1 英寸页边距、智能分页、页码、 封面页、页眉页脚、弯引号和长破折号、可点击目录、对角线 DRAFT 水印。 不是草稿产物——而是成品。当用户 |
| [pdf](pdf/SKILL.md) | 处理 PDF 文件 - 提取文本、创建 PDF、合并文档。在用户要求读取 PDF、创建 PDF 或处理 PDF 文件时使用。 |
| [pptx](pptx/SKILL.md) | "只要涉及 .pptx 文件的任何场景都使用此技能 — 作为输入、输出或两者兼有。包括：创建幻灯片、路演或演示文稿；读取、解析或从任何 .pptx 文件提取文本（即使提取的内容将在其他地方使用，如电子 |
| [xlsx](xlsx/SKILL.md) | "当电子表格文件是主要输入或输出时使用此技能。这意味着用户想要：打开、读取、编辑或修复现有 .xlsx、.xlsm、.csv 或 .tsv 文件（如添加列、计算公式、格式化、制图、清理杂乱数据）的任何 |

### 架构/系统工程

| 技能名 | 说明 |
|--------|------|
| [architecture-decision-records](architecture-decision-records/SKILL.md) | 按照技术决策文档的最佳实践编写和维护架构决策记录（ADR）。在记录重要技术决策、审查过去的架构选择或建立决策流程时使用。 |
| [architecture-patterns](architecture-patterns/SKILL.md) | 实现经过验证的后端架构模式，包括清洁架构、六边形架构和领域驱动设计。在为新微服务设计清洁架构、在重构单体应用使用限界上下文、在实现六边形或洋葱架构模式或在调试应用层之间的依赖循环时使用此技能。 |
| [bazel-build-optimization](bazel-build-optimization/SKILL.md) | 优化大规模单仓库的 Bazel 构建。用于配置 Bazel、实现远程执行或优化企业代码库的构建性能时使用。 |
| [cqrs-implementation](cqrs-implementation/SKILL.md) | 实现命令查询职责分离以构建可扩展架构。在分离读写模型、优化查询性能或构建事件溯源系统时使用。 |
| [deployment-pipeline-design](deployment-pipeline-design/SKILL.md) | 设计包含审批门控、安全检查和部署编排的多阶段 CI/CD 流水线。在设计零停机部署流水线、实现金丝雀发布策略、设置多环境晋升工作流或调试 CI/CD 中失败的部署门控时使用此技能。 |
| [distributed-tracing](distributed-tracing/SKILL.md) | 使用 Jaeger 和 Tempo 实现分布式追踪，跟踪跨微服务的请求并识别性能瓶颈。在调试微服务、分析请求流或为分布式系统实现可观测性时使用。 |
| [event-store-design](event-store-design/SKILL.md) | 为事件溯源系统设计和实现事件存储。在构建事件溯源基础设施、选择事件存储技术或实现事件持久化模式时使用。 |
| [gitops-workflow](gitops-workflow/SKILL.md) | 使用 ArgoCD 和 Flux 实现 GitOps 工作流，用于自动化、声明式的 Kubernetes 部署和持续协调。在实现 GitOps 实践、自动化 Kubernetes 部署或设置声明式基础 |
| [grafana-dashboards](grafana-dashboards/SKILL.md) | 创建和管理生产级 Grafana 仪表板，用于系统和应用指标的实时可视化。在构建监控仪表板、可视化指标或创建运维可观测性界面时使用。 |
| [helm-chart-scaffolding](helm-chart-scaffolding/SKILL.md) | 设计、组织和管理 Helm chart，用于模板化和打包 Kubernetes 应用，支持可复用配置。在创建 Helm chart、打包 Kubernetes 应用或实现模板化部署时使用。 |
| [hybrid-cloud-networking](hybrid-cloud-networking/SKILL.md) | 使用 VPN 和专用连接配置本地基础设施与云平台之间安全、高性能的连接。在构建混合云架构、将数据中心连接到云或实现安全的跨本地网络时使用。 |
| [istio-traffic-management](istio-traffic-management/SKILL.md) | 配置 Istio 流量管理，包括路由、负载均衡、熔断器和金丝雀部署。在实现服务网格流量策略、渐进式交付或弹性模式时使用。 |
| [linkerd-patterns](linkerd-patterns/SKILL.md) | 实现 Linkerd 服务网格模式，用于轻量级、安全优先的服务网格部署。在设置 Linkerd、配置流量策略或以最小开销实现零信任网络时使用。 |
| [microservices-patterns](microservices-patterns/SKILL.md) | 设计微服务架构，涵盖服务边界、事件驱动通信和弹性模式。当构建分布式系统、拆分单体应用或实现微服务时使用。 |
| [multi-cloud-architecture](multi-cloud-architecture/SKILL.md) | 使用决策框架设计多云架构，在 AWS、Azure、GCP 和 OCI 之间选择和集成服务。在构建多云系统、避免供应商锁定或利用多个供应商的最佳服务时使用。 |
| [prometheus-configuration](prometheus-configuration/SKILL.md) | 设置 Prometheus 以全面收集、存储和监控基础设施和应用程序的指标。在实现指标收集、设置监控基础设施或配置告警系统时使用。 |
| [saga-orchestration](saga-orchestration/SKILL.md) | 为分布式事务和跨聚合工作流实现 saga 模式。当在微服务间实现分布式事务（2PC 不可用）、为跨越库存/支付/配送服务的失败订单工作流设计补偿操作、为旅行预订系统构建事件驱动的 saga 协调器（需 |
| [service-mesh-observability](service-mesh-observability/SKILL.md) | 为服务网格实现全面的可观测性，包括分布式跟踪、指标和可视化。在设置网格监控、调试延迟问题或实现服务通信的 SLO 时使用。 |
| [terraform-module-library](terraform-module-library/SKILL.md) | 为 AWS、Azure、GCP 和 OCI 基础设施构建可复用的 Terraform 模块，遵循基础设施即代码最佳实践。适用于创建基础设施模块、标准化云资源配置或实现可复用的 IaC 组件时使用。 |
| [turborepo-caching](turborepo-caching/SKILL.md) | 配置 Turborepo 以实现高效的 monorepo 构建，支持本地和远程缓存。适用于设置 Turborepo、优化构建管道或实现分布式缓存。 |
| [uv-package-manager](uv-package-manager/SKILL.md) | 掌握 uv 包管理器，用于快速 Python 依赖管理、虚拟环境和现代 Python 项目工作流。适用于设置 Python 项目、管理依赖或使用 uv 优化 Python 开发工作流。 |

### 测试/质量

| 技能名 | 说明 |
|--------|------|
| [accessibility-compliance](accessibility-compliance/SKILL.md) | 实现符合 WCAG 2.2 的界面，包含移动无障碍、包容性设计模式和辅助技术支持。在审计无障碍性、实现 ARIA 模式、为屏幕阅读器构建或确保包容性用户体验时使用。 |
| [bats-testing-patterns](bats-testing-patterns/SKILL.md) | 掌握 Bash 自动化测试系统（Bats），用于全面的 Shell 脚本测试。用于编写 Shell 脚本的测试、CI/CD 流水线或需要测试驱动开发 Shell 工具时使用。 |
| [data-quality-frameworks](data-quality-frameworks/SKILL.md) | 使用 Great Expectations、dbt 测试和数据合约实现数据质量验证。在构建数据质量管道、实施验证规则或建立数据合约时使用。 |
| [e2e-testing-patterns](e2e-testing-patterns/SKILL.md) | 掌握使用 Playwright 和 Cypress 进行端到端测试，构建可靠的测试套件以捕获错误、提高信心并实现快速部署。在实现 E2E 测试、调试不稳定测试或建立测试标准时使用。 |
| [qa](qa/SKILL.md) | 系统化 QA 测试 Web 应用程序并修复发现的 bug。运行 QA 测试， 然后迭代修复源代码中的 bug，原子性地提交每个修复并 重新验证。使用场景："qa"、"QA"、"test this si |
| [qa-only](qa-only/SKILL.md) | 仅报告的 QA 测试。系统化测试 Web 应用程序并生成 包含健康分数、截图和复现步骤的结构化报告——但绝不 修复任何内容。使用场景："just report bugs"、"qa report onl |
| [screen-reader-testing](screen-reader-testing/SKILL.md) | 使用屏幕阅读器（包括 VoiceOver、NVDA 和 JAWS）测试 Web 应用程序。在验证屏幕阅读器兼容性、调试辅助功能问题或确保辅助技术支持时使用。 |
| [wcag-audit-patterns](wcag-audit-patterns/SKILL.md) | 使用自动化测试、手动验证和修复指导进行 WCAG 2.2 无障碍审计。适用于审计网站无障碍性、修复 WCAG 违规或实现无障碍设计模式。 |

### 游戏/创意

| 技能名 | 说明 |
|--------|------|
| [ai-slop-cleaner](ai-slop-cleaner/SKILL.md) | 使用回归安全、删除优先的工作流清理 AI 生成的代码垃圾，支持可选的仅审查模式 |
| [design](design/SKILL.md) | "综合设计技能：品牌标识、设计令牌、UI 样式、标志生成（55 种风格，Gemini AI）、企业形象计划（50 种交付物，CIP 模型）、HTML 演示文稿（Chart.js）、横幅设计（22 种风 |
| [design-consultation](design-consultation/SKILL.md) | 设计咨询：理解您的产品，研究行业格局，提出 完整的设计系统（美学、排版、色彩、布局、间距、动效），并 生成字体+颜色预览页面。创建 DESIGN.md 作为您项目的设计 真实来源。对于现有站点，请使用 |
| [design-html](design-html/SKILL.md) | 设计定稿：生成生产级 Pretext 原生 HTML/CSS。 可与 /design-shotgun 的已批准模型、/plan-ceo-review 的 CEO 计划、 /plan-design-re |
| [design-review](design-review/SKILL.md) | Designer's eye QA: finds visual inconsistency, spacing issues, hierarchy problems, AI slop patterns, |
| [design-shotgun](design-shotgun/SKILL.md) | 设计散弹枪：生成多个 AI 设计变体，打开比较面板， 收集结构化反馈并迭代。可随时运行的独立设计探索。 使用场景："explore designs"、"show me options"、"design |
| [godot-gdscript-patterns](godot-gdscript-patterns/SKILL.md) | 掌握 Godot 4 GDScript 模式，包括信号、场景、状态机和优化。在构建 Godot 游戏、实现游戏系统或学习 GDScript 最佳实践时使用。 |
| [gstack-upgrade](gstack-upgrade/SKILL.md) | 升级 gstack 到最新版本。检测全局安装还是本地安装， 运行升级，并显示更新内容。当要求"升级 gstack"、 "更新 gstack"或"获取最新版本"时使用。 语音触发（语音转文字别名）："升 |
| [omc-doctor](omc-doctor/SKILL.md) | 诊断和修复 oh-my-claudecode 安装问题 |
| [omc-reference](omc-reference/SKILL.md) | OMC 代理目录、可用工具、团队管道路由、提交协议和技能注册表。在委派给代理、使用 OMC 工具、编排团队、进行提交或调用技能时自动加载。 |
| [omc-setup](omc-setup/SKILL.md) | 从标准设置流程安装或刷新 oh-my-claudecode，支持插件、npm 和本地开发设置 |
| [omc-teams](omc-teams/SKILL.md) | 当你需要基于进程的并行执行时，在 tmux 窗格中为 claude、codex 或 gemini 工作进程提供 CLI 团队运行时 |
| [open-gstack-browser](open-gstack-browser/SKILL.md) | 启动 GStack Browser — 内置侧边栏扩展的 AI 控制 Chromium。 打开一个可见的浏览器窗口，你可以实时观看每个操作。 侧边栏显示实时活动流和聊天。内置反机器人隐身功能。 在要求 |
| [setup](setup/SKILL.md) | 首次使用时进行安装/更新路由 — 将 setup、doctor 或 MCP 请求发送到正确的 OMC 设置流程 |
| [setup-browser-cookies](setup-browser-cookies/SKILL.md) | 将您真实 Chromium 浏览器的 cookie 导入到无头浏览会话中。 打开一个交互式选择器界面，让您选择要导入哪些域名的 cookie。 在 QA 测试需要认证的页面之前使用。当被要求"导入 c |
| [setup-deploy](setup-deploy/SKILL.md) | 为 /land-and-deploy 配置部署设置。检测您的部署平台 （Fly.io、Render、Vercel、Netlify、Heroku、GitHub Actions、自定义）、 生产 URL、 |
| [setup-gbrain](setup-gbrain/SKILL.md) | 为此编码代理设置 gbrain：安装 CLI、初始化本地 PGLite 或 Supabase brain、 注册 MCP、捕获每个远程的信任策略。一条命令从零到"gbrain 正在运行， 此代理可以调 |
| [unity-ecs-patterns](unity-ecs-patterns/SKILL.md) | 掌握 Unity ECS（实体组件系统）以及 DOTS、Jobs 和 Burst，用于高性能游戏开发。适用于构建数据导向的游戏、优化性能或处理大量实体。 |
| [visual-verdict](visual-verdict/SKILL.md) | 用于截图与参考图比较的结构化视觉 QA 判定 |

### 演示/展示

| 技能名 | 说明 |
|--------|------|
| [devex-review](devex-review/SKILL.md) | 实时开发者体验审计。使用浏览工具实际测试 开发者体验：导航文档、尝试入门流程、测量 TTHW、截图错误消息、评估 CLI 帮助文本。生成带有 证据的 DX 记分卡。与 /plan-devex-revi |
| [doc-coauthoring](doc-coauthoring/SKILL.md) | 引导用户完成协作编写文档的结构化工作流。当用户想要编写文档、提案、技术规范、决策文档或类似结构化内容时使用。此工作流帮助用户高效传递上下文、通过迭代优化内容，并验证文档对读者是否有效。当用户提到编写文 |
| [internal-comms](internal-comms/SKILL.md) | 一套帮助撰写各类内部沟通文档的资源，使用公司偏好的格式。当被要求撰写某种内部沟通文档（状态报告、领导层更新、三方更新、公司简报、FAQ、事故报告、项目更新等）时，应使用此技能。 |
| [postmortem-writing](postmortem-writing/SKILL.md) | 编写有效的无责事后分析报告，包含根本原因分析、时间线和行动项。在进行事件审查、编写事后分析文档或改进事件响应流程时使用。 |
| [retro](retro/SKILL.md) | 每周工程回顾。分析提交历史、工作模式和代码质量指标，带有持久历史和趋势跟踪。 支持团队感知：按人分解贡献，包含表扬和成长领域。 在用户要求"每周回顾"、"我们发布了什么"或"工程回顾"时使用。 在工作 |
| [session-report](session-report/SKILL.md) | 从 ~/.claude/projects 转录生成可浏览的 Claude Code 会话使用 HTML 报告（token、缓存、子代理、技能、高消耗提示）。 |
| [slides](slides/SKILL.md) | 使用 Chart.js、设计 token、响应式布局、文案公式和上下文幻灯片策略创建战略性 HTML 演示文稿。 |

### 贡献/社区

| 技能名 | 说明 |
|--------|------|
| [code-review-excellence](code-review-excellence/SKILL.md) | 掌握有效的代码审查实践，提供建设性反馈、尽早发现 bug 并促进知识共享，同时保持团队士气。在审查拉取请求、建立审查标准或指导开发者时使用。 |
| [hook-development](hook-development/SKILL.md) | 当用户要求"创建钩子"、"添加 PreToolUse/PostToolUse/Stop 钩子"、"验证工具使用"、"实现基于提示的钩子"、"使用 ${CLAUDE_PLUGIN_ROOT}"、"设置事 |
| [multi-reviewer-patterns](multi-reviewer-patterns/SKILL.md) | 跨多个质量维度协调并行代码审查，实现发现去重、严重性校准和合并报告。在组织多审查者代码审查、校准发现严重性或合并审查结果时使用此技能。 |
| [review-agent-setup](review-agent-setup/SKILL.md) | 在 Claude Code 中为 AI 代理审查操作配置人工审批门控。当设置一个代理可能发布 PR 审查、评论、合并或编辑 CI 配置的项目时使用，并且您需要具有密码学可审计审批跟踪和 Cedar 强 |
| [skill](skill/SKILL.md) | 管理本地技能 — 列表、添加、删除、搜索、编辑、设置向导 |
| [skill-development](skill-development/SKILL.md) | 当用户想要"创建技能"、"向插件添加技能"、"编写新技能"、"改进技能描述"、"组织技能内容"，或需要关于 Claude Code 插件的技能结构、渐进式披露或技能开发最佳实践的指导时，应使用此技能。 |
| [skillify](skillify/SKILL.md) | 将当前会话中的可重复工作流转换为可复用的 OMC 技能草稿 |

### 运维/基础设施

| 技能名 | 说明 |
|--------|------|
| [git-advanced-workflows](git-advanced-workflows/SKILL.md) | 掌握高级 Git 工作流，包括变基、拣选、二分查找、工作树和引用日志，以维护干净的历史记录并从任何情况中恢复。在管理复杂的 Git 历史、在功能分支上协作或排查仓库问题时使用。 |
| [github-actions-templates](github-actions-templates/SKILL.md) | 创建生产就绪的 GitHub Actions 工作流，用于自动化测试、构建和部署应用。在使用 GitHub Actions 设置 CI/CD、自动化开发工作流或创建可复用的工作流模板时使用。 |
| [gitlab-ci-patterns](gitlab-ci-patterns/SKILL.md) | 使用多阶段工作流、缓存和分布式运行器构建可扩展的 GitLab CI/CD 管道。在实现 GitLab CI/CD、优化管道性能或设置自动化测试和部署时使用。 |
| [health](health/SKILL.md) | 代码质量仪表板。包装现有项目工具（类型检查器、代码检查器、 测试运行器、死代码检测器、shell 检查器），计算加权综合 0-10 分数，并跟踪随时间的趋势。使用场景："健康检查"、 "代码质量"、" |
| [incident-runbook-templates](incident-runbook-templates/SKILL.md) | 创建结构化的事件响应手册，包含分步流程、升级路径和恢复操作。在为支付处理系统构建服务中断手册、创建涵盖连接池耗尽、复制延迟和磁盘空间告警的数据库事件流程、为需要在凌晨 3 点也能理解的分步恢复指南培训 |
| [k8s-manifest-generator](k8s-manifest-generator/SKILL.md) | 创建生产就绪的 Kubernetes 清单，包括 Deployment、Service、ConfigMap 和 Secret，遵循最佳实践和安全标准。在生成 Kubernetes YAML 清单、创建 |
| [mcp-integration](mcp-integration/SKILL.md) | 当用户要求"添加 MCP 服务器"、"集成 MCP"、"在插件中配置 MCP"、"使用 .mcp.json"、"设置模型上下文协议"、"连接外部服务"、提到 "${CLAUDE_PLUGIN_ROOT |
| [mcp-setup](mcp-setup/SKILL.md) | 配置常用的 MCP 服务器以增强代理能力 |
| [on-call-handoff-patterns](on-call-handoff-patterns/SKILL.md) | 掌握值班交接，包括上下文传递、升级程序和文档。在工程师之间交接值班职责并确保接班响应者具有完整的态势感知时、在编写捕获活跃事件、持续调查和近期更改的班次摘要时、在事件中途交接以便新工程师可以在不丢失上 |
| [protect-mcp-setup](protect-mcp-setup/SKILL.md) | 为 Claude Code 工具调用配置 Cedar 策略执行和 Ed25519 签名收据。在设置需要加密审计跟踪、策略门控工具执行或合规就绪的代理操作证据的项目时使用。 |

### 飞书/Lark 集成

| 技能名 | 说明 |
|--------|------|
| [lark-approval](lark-approval/SKILL.md) | "飞书审批 API：审批实例、审批任务管理。" |
| [lark-attendance](lark-attendance/SKILL.md) | "飞书考勤打卡：查询自己的考勤打卡记录" |
| [lark-base](lark-base/SKILL.md) | "当需要用 lark-cli 操作飞书多维表格（Base）时调用：适用于建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / |
| [lark-calendar](lark-calendar/SKILL.md) | "飞书日历（calendar）：提供日历与日程（会议）的全面管理能力。核心场景包括：查看/搜索日程、创建/更新日程、管理参会人、查询忙闲状态及推荐空闲时段、查询/搜索与预定会议室。注意：涉及【预约日程 |
| [lark-contact](lark-contact/SKILL.md) | "飞书 / Lark 通讯录,用于按姓名 / 邮箱把员工解析成 open_id,以及按 open_id 反查员工的姓名 / 部门 / 邮箱 / 联系方式。当用户说出某人姓名而下一步需要发消息 / 加群 |
| [lark-doc](lark-doc/SKILL.md) | "飞书云文档：创建和编辑飞书文档。默认使用 DocxXML 格式（也支持 Markdown）。创建文档、获取文档内容（支持 simple/with-ids/full 三种导出详细度，以及 full/o |
| [lark-drive](lark-drive/SKILL.md) | "飞书云空间：管理云空间中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件、修改文件标题（docx、sheet、bit |
| [lark-event](lark-event/SKILL.md) | "飞书/Lark 实时事件监听/订阅/消费：通过 `lark-cli event consume <EventKey>` 以 NDJSON 格式流式接收事件（涵盖即时通讯消息接收、表情回复、群成员变更 |
| [lark-im](lark-im/SKILL.md) | "飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件（支持大文件分片下载）、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成 |
| [lark-mail](lark-mail/SKILL.md) | "飞书邮箱 — draft, compose, send, reply, forward, read, and search emails; manage drafts, folders, label |
| [lark-minutes](lark-minutes/SKILL.md) | "飞书妙记：妙记相关基本功能。1.查询妙记列表（按关键词/所有者/参与者/时间范围）；2.获取妙记基础信息（标题、封面、时长 等）；3.下载妙记音视频文件；4.获取妙记相关 AI 产物（总结、待办、章 |
| [lark-okr](lark-okr/SKILL.md) | "飞书 OKR：管理目标与关键结果。查看和编辑 OKR 周期、目标（Objective）、关键结果（Key Result）、对齐关系、量化指标和进展记录。当用户需要查看或创建 OKR、管理目标和关键结 |
| [lark-openapi-explorer](lark-openapi-explorer/SKILL.md) | "飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足， |
| [lark-shared](lark-shared/SKILL.md) | "飞书/Lark CLI 共享基础：应用配置初始化、认证登录（auth login）、身份切换（--as user/bot）、权限与 scope 管理、Permission denied 错误处理、安 |
| [lark-sheets](lark-sheets/SKILL.md) | "飞书电子表格：创建和操作电子表格。创建表格并写入表头和数据、读取和写入单元格、追加行数据、在已知电子表格中查找单元格内容、导出表格文件。当用户需要创建电子表格、批量读写数据、在已知表格中查找内容、导 |
| [lark-skill-maker](lark-skill-maker/SKILL.md) | "创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。" |
| [lark-slides](lark-slides/SKILL.md) | "飞书幻灯片：创建和编辑幻灯片，接口通过 XML 协议通信。创建演示文稿、读取幻灯片内容、管理幻灯片页面（创建、删除、读取、局部替换）。当用户需要创建或编辑幻灯片、读取或修改单个页面时使用。" |
| [lark-task](lark-task/SKILL.md) | "飞书任务：管理任务和清单。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务时使用。" |
| [lark-vc](lark-vc/SKILL.md) | "飞书视频会议：查询会议记录、获取会议纪要产物（总结、待办、章节、逐字稿）。1. 查询已经结束的会议数量或详情时使用本技能(如历史日期｜ 昨天 \| 上周 \| 今天已经开过的会议等场景)，查询未开始 |
| [lark-whiteboard](lark-whiteboard/SKILL.md) | > |
| [lark-wiki](lark-wiki/SKILL.md) | "飞书知识库：管理知识空间、空间成员和文档节点。创建和查询知识空间、查看和管理空间成员、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、查看或管理 |
| [lark-workflow-meeting-summary](lark-workflow-meeting-summary/SKILL.md) | "会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。" |
| [lark-workflow-standup-report](lark-workflow-standup-report/SKILL.md) | "日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。" |

### 其他

| 技能名 | 说明 |
|--------|------|
| [airflow-dag-patterns](airflow-dag-patterns/SKILL.md) | 使用操作器、传感器、测试和部署的最佳实践构建生产级 Apache Airflow DAG。在创建数据管道、编排工作流或调度批处理作业时使用。 |
| [api-design-principles](api-design-principles/SKILL.md) | 掌握 REST 和 GraphQL API 设计原则，构建直观、可扩展且可维护的 API，让开发者满意。在设计新 API、审查 API 规范或建立 API 设计标准时使用。 |
| [ask](ask/SKILL.md) | 通过 `omc ask` 为 Claude、Codex 或 Gemini 提供流程优先的顾问路由，支持产物捕获，无需手动组装 CLI 命令 |
| [async-python-patterns](async-python-patterns/SKILL.md) | 掌握 Python asyncio、并发编程和 async/await 模式，用于高性能应用。在构建异步 API、并发系统或需要非阻塞操作的 I/O 密集型应用时使用。 |
| [block-no-verify-hook](block-no-verify-hook/SKILL.md) | 配置 PreToolUse 钩子，防止 AI 代理使用 --no-verify 和其他绕过标志跳过 git pre-commit 钩子。适用于需要强制执行提交质量门禁的 Claude Code 项目。 |
| [brand](brand/SKILL.md) | 品牌声音、视觉形象、消息框架、资产管理、品牌一致性。用于品牌内容、语气、营销资产、品牌合规、风格指南。 |
| [canary](canary/SKILL.md) | 部署后金丝雀监控。使用浏览守护进程监视线上应用的控制台错误、 性能回退和页面故障。定期截屏，与部署前基线对比， 发现异常时报警。适用场景："monitor deploy"、"canary"、"post |
| [caveman](caveman/SKILL.md) | > |
| [ccg](ccg/SKILL.md) | Claude-Codex-Gemini 三模型编排，通过 /ask codex + /ask gemini，然后 Claude 综合结果 |
| [claude-automation-recommender](claude-automation-recommender/SKILL.md) | 分析代码库并推荐 Claude Code 自动化（钩子、子代理、技能、插件、MCP 服务器）。当用户要求自动化推荐、想优化 Claude Code 设置、提到改进 Claude Code 工作流、询问 |
| [claude-md-improver](claude-md-improver/SKILL.md) | 审计和改进仓库中的 CLAUDE.md 文件。当用户要求检查、审计、更新、改进或修复 CLAUDE.md 文件时使用。扫描所有 CLAUDE.md 文件，根据模板评估质量，输出质量报告，然后进行有针对 |
| [command-development](command-development/SKILL.md) | 当用户要求"创建斜杠命令"、"添加命令"、"编写自定义命令"、"定义命令参数"、"使用命令 frontmatter"、"组织命令"、"创建带文件引用的命令"、"交互式命令"、"在命令中使用 AskUs |
| [commit-commands](commit-commands/SKILL.md) |  |
| [connect-chrome](connect-chrome/SKILL.md) | 启动 GStack Browser — 内置侧边栏扩展的 AI 控制 Chromium。 打开一个可见的浏览器窗口，你可以实时观看每个操作。 侧边栏显示实时活动流和聊天。内置反机器人隐身功能。 适用场 |
| [cost-optimization](cost-optimization/SKILL.md) | 通过资源合理化、标签策略、预留实例和支出分析优化 AWS、Azure、GCP 和 OCI 的云成本。在降低云费用、分析基础设施成本或实施成本治理策略时使用。 |
| [cso](cso/SKILL.md) | 首席安全官模式。基础设施优先的安全审计：密钥考古学、 依赖供应链、CI/CD 管道安全、LLM/AI 安全、技能供应链 扫描，加上 OWASP Top 10、STRIDE 威胁建模和主动验证。 两种模 |
| [defi-protocol-templates](defi-protocol-templates/SKILL.md) | 使用生产就绪模板实施 DeFi 协议，包括质押、AMM、治理和借贷系统。在构建去中心化金融应用或智能合约协议时使用。 |
| [error-handling-patterns](error-handling-patterns/SKILL.md) | 掌握跨语言的错误处理模式，包括异常、Result 类型、错误传播和优雅降级，以构建弹性应用。在实现错误处理、设计 API 或提高应用可靠性时使用。 |
| [hackernews-frontpage](hackernews-frontpage/SKILL.md) | 抓取 Hacker News 首页（标题、分数、评论数）。 |
| [hads](hads/SKILL.md) | 在编写需要同时被人类和 AI 模型阅读的技术文档时使用，将现有文档转换为 HADS 格式，验证 HADS 文档，或优化文档以实现 token 高效的 AI 消费。 |
| [karpathy-guidelines](karpathy-guidelines/SKILL.md) | 减少常见 LLM 编码错误的行为准则。在编写、审查或重构代码时使用，以避免过度复杂化、进行精确修改、暴露假设并定义可验证的成功标准。 |
| [kpi-dashboard-design](kpi-dashboard-design/SKILL.md) | 设计有效的 KPI 仪表板，包括指标选择、可视化最佳实践和实时监控模式。在构建跟踪 MRR、流失率和 LTV/CAC 比率的高管 SaaS 指标仪表板、设计具有实时服务健康和请求吞吐量的运营中心、为产 |
| [land-and-deploy](land-and-deploy/SKILL.md) | 合并与部署工作流。合并 PR，等待 CI 和部署，通过金丝雀检查 验证生产环境健康。在 /ship 创建 PR 后接管。当要求"merge"、 "land"、"deploy"、"merge and v |
| [landing-report](landing-report/SKILL.md) | 工作区感知发布的只读队列仪表板。显示哪些 VERSION 插槽 目前被打开的 PR 占用，哪些兄弟 Conductor 工作区有 可能即将发布的 WIP 工作，以及 /ship 接下来会选择哪个插槽。 |
| [langchain-architecture](langchain-architecture/SKILL.md) | 使用 LangChain 1.x 和 LangGraph 设计 LLM 应用，支持代理、记忆和工具集成。在构建 LangChain 应用、实现 AI 代理或创建复杂 LLM 工作流时使用。 |
| [ml-pipeline-workflow](ml-pipeline-workflow/SKILL.md) | 构建从数据准备到模型训练、验证和生产部署的端到端 MLOps 管道。当创建 ML 管道、实现 MLOps 实践或自动化模型训练和部署工作流时使用。 |
| [mobile-android-design](mobile-android-design/SKILL.md) | 掌握 Material Design 3 和 Jetpack Compose 模式，用于构建原生 Android 应用。当设计 Android 界面、实现 Compose UI 或遵循 Google  |
| [mobile-ios-design](mobile-ios-design/SKILL.md) | 掌握 iOS 人机界面指南和 SwiftUI 模式，用于构建原生 iOS 应用。当设计 iOS 界面、实现 SwiftUI 视图或确保应用遵循 Apple 设计原则时使用。 |
| [modern-javascript-patterns](modern-javascript-patterns/SKILL.md) | 掌握 ES6+ 特性，包括 async/await、解构、展开运算符、箭头函数、Promise、模块、迭代器、生成器和函数式编程模式，用于编写清晰高效的 JavaScript 代码。在重构遗留代码、实 |
| [nft-standards](nft-standards/SKILL.md) | 实现 NFT 标准（ERC-721、ERC-1155），包含适当的元数据处理、铸造策略和市场集成。在创建 NFT 合约、构建 NFT 市场或实现数字资产系统时使用。 |
| [playground](playground/SKILL.md) | 创建交互式 HTML 游乐场 — 自包含的单文件探索器，让用户通过控件进行视觉配置、查看实时预览，并复制输出提示。当用户要求为某个主题制作游乐场、探索器或交互式工具时使用。 |
| [projection-patterns](projection-patterns/SKILL.md) | 从事件流构建读模型和投影。在实现 CQRS 读端、构建物化视图或优化事件溯源系统中的查询性能时使用。 |
| [ralph](ralph/SKILL.md) | 自引用循环直到任务完成，带有可配置的验证审查员 |
| [ralplan](ralplan/SKILL.md) | 共识规划入口，在执行前自动门控模糊的 ralph/autopilot/team 请求 |
| [react-native-design](react-native-design/SKILL.md) | 掌握 React Native 样式、导航和 Reanimated 动画，用于跨平台移动开发。在构建 React Native 应用、实现导航模式或创建高性能动画时使用。 |
| [sciomc](sciomc/SKILL.md) | 编排并行科学家代理进行综合分析，支持 AUTO 模式 |
| [signed-audit-trails-recipe](signed-audit-trails-recipe/SKILL.md) | 为 Claude Code 工具调用设置加密签名审计跟踪的分步指南。在解释、评估或演示该模式（在承诺使用 protect-mcp 运行时钩子之前）时使用。涵盖 Cedar 策略、Ed25519 收据、 |
| [skills-sync](skills-sync/SKILL.md) | 同步 Claude Code 技能目录到 GitHub 仓库。支持三种模式：upload（本地覆盖远程）、download（远程覆盖本地）、merge（双向合并，冲突时提示用户确认）。触发词："ski |
| [slo-implementation](slo-implementation/SKILL.md) | 定义和实现服务水平指标（SLI）和服务水平目标（SLO），包含错误预算和告警。在建立可靠性目标、实现 SRE 实践或衡量服务性能时使用。 |
| [solidity-security](solidity-security/SKILL.md) | 掌握智能合约安全最佳实践，预防常见漏洞并实现安全的 Solidity 模式。在编写智能合约、审计现有合约或为区块链应用程序实现安全措施时使用。 |
| [spark-optimization](spark-optimization/SKILL.md) | 使用分区、缓存、shuffle 优化和内存调优优化 Apache Spark 作业。在提升 Spark 性能、调试慢作业或扩展数据处理管道时使用。 |
| [stride-analysis-patterns](stride-analysis-patterns/SKILL.md) | 应用 STRIDE 方法论系统性地识别威胁。适用于分析系统安全、进行威胁建模会议或创建安全文档。 |
| [tailwind-design-system](tailwind-design-system/SKILL.md) | 使用 Tailwind CSS v4 构建可扩展的设计系统，包括设计令牌、组件库和响应式模式。适用于创建组件库、实现设计系统或标准化 UI 模式。 |
| [team-composition-patterns](team-composition-patterns/SKILL.md) | 设计最优的智能体团队组成，包括规模启发式规则、预设配置和智能体类型选择。适用于决定为任务生成多少智能体、选择审查团队/功能团队/调试团队、为每个角色选择正确的 subagent_type 以确保智能体 |
| [temporal-python-testing](temporal-python-testing/SKILL.md) | 使用 pytest、时间跳过和模拟策略测试 Temporal 工作流。涵盖单元测试、集成测试、重放测试和本地开发环境搭建。适用于实现 Temporal 工作流测试或调试测试失败时使用。 |
| [threat-mitigation-mapping](threat-mitigation-mapping/SKILL.md) | 将已识别的威胁映射到适当的安全控制和缓解措施。适用于优先安排安全投资、创建修复计划或验证控制有效性。 |
| [trace](trace/SKILL.md) | 证据驱动的追踪通道，在 Claude 内置团队模式中编排竞争性追踪假设 |
| [track-management](track-management/SKILL.md) | 在创建、管理或使用 Conductor 轨道时使用此技能 — 轨道是功能、缺陷和重构的逻辑工作单元。适用于 spec.md、plan.md 和轨道生命周期操作。 |
| [ultraqa](ultraqa/SKILL.md) | QA 循环工作流 - 测试、验证、修复、重复直到达到目标 |
| [ultrawork](ultrawork/SKILL.md) | 用于高吞吐量任务完成的并行执行引擎 |
| [vector-index-tuning](vector-index-tuning/SKILL.md) | 优化向量索引性能，包括延迟、召回率和内存。适用于调优 HNSW 参数、选择量化策略或扩展向量搜索基础设施。 |
| [web-component-design](web-component-design/SKILL.md) | 掌握 React、Vue 和 Svelte 组件模式，包括 CSS-in-JS、组合策略和可复用组件架构。适用于构建 UI 组件库、设计组件 API 或实现前端设计系统。 |
| [web3-testing](web3-testing/SKILL.md) | 使用 Hardhat 和 Foundry 全面测试智能合约，包括单元测试、集成测试和主网分叉。适用于测试 Solidity 合约、设置区块链测试套件或验证 DeFi 协议。 |
| [wiki](wiki/SKILL.md) | LLM Wiki — 跨会话累积的持久化 markdown 知识库（Karpathy 模型） |
| [workflow-orchestration-patterns](workflow-orchestration-patterns/SKILL.md) | 使用 Temporal 为分布式系统设计持久化工作流。涵盖工作流与活动分离、saga 模式、状态管理和确定性约束。适用于构建长时间运行的进程、分布式事务或微服务编排。 |
| [workflow-patterns](workflow-patterns/SKILL.md) | 当按照 Conductor 的 TDD 工作流实现任务、处理阶段检查点、管理任务的 git 提交或理解验证协议时使用此技能。 |
| [xhs-survey](xhs-survey/SKILL.md) | "小红书话题影响力调研：模拟真人浏览方式，打开浏览器 → 搜索话题 → 上下滑动浏览 → 点击进入笔记 → 读取详情内容 → 汇总分析。当用户需要调研某个话题在小红书上的表现、影响力、讨论度时使用本技 |

---

*总计：329 个技能*