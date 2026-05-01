---
name: architecture-decision-records
description: 按照技术决策文档的最佳实践编写和维护架构决策记录（ADR）。在记录重要技术决策、审查过去的架构选择或建立决策流程时使用。
---

# 架构决策记录

创建、维护和管理架构决策记录（ADR）的综合模式，用于捕获重要技术决策背后的上下文和理由。

## 使用场景

- 做出重要的架构决策
- 记录技术选择
- 记录设计权衡
- 新团队成员入职
- 审查历史决策
- 建立决策流程

## 核心概念

### 1. 什么是 ADR？

架构决策记录捕获：

- **上下文**：为什么我们需要做决策
- **决策**：我们决定了什么
- **后果**：结果会怎样

### 2. 何时编写 ADR

| 编写 ADR | 跳过 ADR |
| ---------- | ---------- |
| 新框架采用 | 次要版本升级 |
| 数据库技术选择 | Bug 修复 |
| API 设计模式 | 实现细节 |
| 安全架构 | 日常维护 |
| 集成模式 | 配置变更 |

### 3. ADR 生命周期

```
已提议 → 已接受 → 已弃用 → 已取代
            ↓
         已拒绝
```

## 模板

### 模板 1：标准 ADR（MADR 格式）

```markdown
# ADR-0001: Use PostgreSQL as Primary Database

## 状态

已接受

## 上下文

我们需要为新的电商平台选择主数据库。系统将处理：

- 约 10,000 并发用户
- 带有分层类别的复杂产品目录
- 订单和支付的事务处理
- 产品的全文搜索
- 商店定位器的地理空间查询

团队有 MySQL、PostgreSQL 和 MongoDB 的经验。金融交易需要 ACID 合规。

## 决策驱动因素

- **必须有 ACID 合规**用于支付处理
- **必须支持复杂查询**用于报告
- **应支持全文搜索**以减少基础设施复杂性
- **应有良好的 JSON 支持**用于灵活的产品属性
- **团队熟悉度**减少入职时间

## 考虑的选项

### 选项 1：PostgreSQL

- **优点**：ACID 合规、优秀的 JSON 支持（JSONB）、内置全文搜索、PostGIS 地理空间、团队有经验
- **缺点**：复制设置比 MySQL 稍复杂

### 选项 2：MySQL

- **优点**：团队非常熟悉、简单复制、大型社区
- **缺点**：JSON 支持较弱、无内置全文搜索（需要 Elasticsearch）、无扩展无地理空间

### 选项 3：MongoDB

- **优点**：灵活模式、原生 JSON、水平扩展
- **缺点**：多文档事务无 ACID（决策时）、团队经验有限、需要模式设计纪律

## 决策

我们将使用 **PostgreSQL 15** 作为主数据库。

## 理由

PostgreSQL 提供了最佳平衡：

1. **ACID 合规**对电商交易至关重要
2. **内置能力**（全文搜索、JSONB、PostGIS）减少基础设施复杂性
3. **团队对 SQL 数据库的熟悉**减少学习曲线
4. **成熟的生态系统**拥有优秀的工具和社区支持

复制的轻微复杂性被减少额外服务（无需单独的 Elasticsearch）所抵消。

## 后果

### 积极

- 单一数据库处理事务、搜索和地理空间查询
- 降低运维复杂性（更少的服务需要管理）
- 金融数据的强一致性保证
- 团队可以利用现有的 SQL 专业知识

### 消极

- 需要学习 PostgreSQL 特定功能（JSONB、全文搜索语法）
- 垂直扩展限制可能需要更早使用读副本
- 部分团队成员需要 PostgreSQL 特定培训

### 风险

- 全文搜索可能不如专用搜索引擎扩展性好
- 缓解：设计为可能添加 Elasticsearch

## 实现说明

- 使用 JSONB 存储灵活的产品属性
- 使用 PgBouncer 实现连接池
- 设置流式复制用于读副本
- 使用 pg_trgm 扩展进行模糊搜索

## 相关决策

- ADR-0002：缓存策略（Redis）- 补充数据库选择
- ADR-0005：搜索架构 - 如需要 Elasticsearch 可能取代

## 参考

- [PostgreSQL JSON 文档](https://www.postgresql.org/docs/current/datatype-json.html)
- [PostgreSQL 全文搜索](https://www.postgresql.org/docs/current/textsearch.html)
- 内部：`/docs/benchmarks/database-comparison.md` 中的性能基准
```

### 模板 2：轻量级 ADR

```markdown
# ADR-0012: Adopt TypeScript for Frontend Development

**状态**：已接受
**日期**：2024-01-15
**决策者**：@alice、@bob、@charlie

## 上下文

我们的 React 代码库已增长到 50+ 个组件，与 prop 类型不匹配和未定义错误相关的错误报告不断增加。PropTypes 仅提供运行时检查。

## 决策

所有新前端代码采用 TypeScript。现有代码增量迁移。

## 后果

**好**：编译时捕获类型错误、更好的 IDE 支持、自文档化代码。

**坏**：团队学习曲线、初始减速、构建复杂性增加。

**缓解**：TypeScript 培训课程，允许通过 `allowJs: true` 渐进采用。
```

### 模板 3：Y 陈述格式

```markdown
# ADR-0015: API Gateway Selection

在**构建微服务架构**的背景下，
面对**需要集中式 API 管理、认证和速率限制**的问题，
我们决定使用 **Kong Gateway**
而非 **AWS API Gateway 和自定义 Nginx 方案**，
以实现**供应商独立性、插件可扩展性和团队对 Lua 的熟悉**，
接受**我们需要自己管理 Kong 基础设施**。
```

### 模板 4：弃用 ADR

```markdown
# ADR-0020: Deprecate MongoDB in Favor of PostgreSQL

## 状态

已接受（取代 ADR-0003）

## 上下文

ADR-0003（2021）因模式灵活性需求选择了 MongoDB 用于用户配置文件存储。此后：

- MongoDB 的多文档事务对我们用例仍有问题
- 我们的模式已稳定，很少变更
- 我们现在从其他服务获得了 PostgreSQL 专业知识
- 维护两个数据库增加了运维负担

## 决策

弃用 MongoDB 并将用户配置文件迁移到 PostgreSQL。

## 迁移计划

1. **阶段 1**（第 1-2 周）：创建 PostgreSQL 模式，启用双写
2. **阶段 2**（第 3-4 周）：回填历史数据，验证一致性
3. **阶段 3**（第 5 周）：切换读到 PostgreSQL，监控
4. **阶段 4**（第 6 周）：移除 MongoDB 写入，退役

## 后果

### 积极

- 单一数据库技术降低运维复杂性
- 用户数据的 ACID 事务
- 团队可以专注 PostgreSQL 专业知识

### 消极

- 迁移工作量（约 4 周）
- 迁移期间数据问题风险
- 失去一些模式灵活性

## 经验教训

从 ADR-0003 经验记录：

- 模式灵活性好处被高估
- 多数据库的运维成本被低估
- 技术决策中考虑长期维护
```

### 模板 5：征求意见稿（RFC）风格

```markdown
# RFC-0025: Adopt Event Sourcing for Order Management

## 摘要

提议在订单管理领域采用事件溯源模式，以提高可审计性、支持时态查询和业务分析。

## 动机

当前挑战：

1. 审计要求需要完整的订单历史
2. "时间 X 时订单状态是什么？"查询不可能
3. 分析团队需要事件流用于实时仪表板
4. 客户支持的订单状态重建是手动的

## 详细设计

### 事件存储
```

OrderCreated { orderId, customerId, items[], timestamp }
OrderItemAdded { orderId, item, timestamp }
OrderItemRemoved { orderId, itemId, timestamp }
PaymentReceived { orderId, amount, paymentId, timestamp }
OrderShipped { orderId, trackingNumber, timestamp }

```

### 投影

- **CurrentOrderState**：查询的物化视图
- **OrderHistory**：审计的完整时间线
- **DailyOrderMetrics**：分析聚合

### 技术

- 事件存储：EventStoreDB（专用构建，处理投影）
- 考虑的替代方案：Kafka + 自定义投影服务

## 缺点

- 团队学习曲线
- 比 CRUD 复杂性增加
- 需要仔细设计事件（存储后不可变）
- 存储增长（事件永不删除）

## 替代方案

1. **审计表**：更简单但不支持时态查询
2. **从现有 DB 的 CDC**：复杂，不改变数据模型
3. **混合**：仅对订单状态变更事件溯源

## 未解决问题

- [ ] 事件模式版本控制策略
- [ ] 事件保留策略
- [ ] 性能快照频率

## 实现计划

1. 用单一订单类型原型（2 周）
2. 团队事件溯源培训（1 周）
3. 完整实现和迁移（4 周）
4. 监控和优化（持续）

## 参考

- [Martin Fowler 的事件溯源](https://martinfowler.com/eaaDev/EventSourcing.html)
- [EventStoreDB 文档](https://www.eventstore.com/docs)
```

## ADR 管理

### 目录结构

```
docs/
├── adr/
│   ├── README.md           # 索引和指南
│   ├── template.md         # 团队的 ADR 模板
│   ├── 0001-use-postgresql.md
│   ├── 0002-caching-strategy.md
│   ├── 0003-mongodb-user-profiles.md  # [已弃用]
│   └── 0020-deprecate-mongodb.md      # 取代 0003
```

### ADR 索引（README.md）

```markdown
# 架构决策记录

此目录包含 [项目名称] 的架构决策记录（ADR）。

## 索引

| ADR | 标题 | 状态 | 日期 |
| ----- | ---- | ---- | ---- |
| [0001](0001-use-postgresql.md) | Use PostgreSQL as Primary Database | 已接受 | 2024-01-10 |
| [0002](0002-caching-strategy.md) | Caching Strategy with Redis | 已接受 | 2024-01-12 |
| [0003](0003-mongodb-user-profiles.md) | MongoDB for User Profiles | 已弃用 | 2023-06-15 |
| [0020](0020-deprecate-mongodb.md) | Deprecate MongoDB | 已接受 | 2024-01-15 |

## 创建新 ADR

1. 复制 `template.md` 为 `NNNN-title-with-dashes.md`
2. 填写模板
3. 提交 PR 审查
4. 批准后更新此索引

## ADR 状态

- **已提议**：讨论中
- **已接受**：决策已定，实施中
- **已弃用**：不再相关
- **已取代**：被另一个 ADR 替代
- **已拒绝**：考虑但未采用
```

### 自动化（adr-tools）

```bash
# 安装 adr-tools
brew install adr-tools

# 初始化 ADR 目录
adr init docs/adr

# 创建新 ADR
adr new "Use PostgreSQL as Primary Database"

# 取代 ADR
adr new -s 3 "Deprecate MongoDB in Favor of PostgreSQL"

# 生成目录
adr generate toc > docs/adr/README.md

# 链接相关 ADR
adr link 2 "Complements" 1 "Is complemented by"
```

## 审查流程

```markdown
## ADR 审查清单

### 提交前

- [ ] 上下文清晰说明问题
- [ ] 考虑了所有可行选项
- [ ] 优缺点平衡且诚实
- [ ] 后果（积极和消极）已记录
- [ ] 相关 ADR 已链接

### 审查期间

- [ ] 至少 2 名高级工程师审查
- [ ] 已咨询受影响的团队
- [ ] 考虑了安全影响
- [ ] 记录了成本影响
- [ ] 评估了可逆性

### 接受后

- [ ] ADR 索引已更新
- [ ] 团队已通知
- [ ] 实现已创建
- [ ] 相关文档已更新
```

## 最佳实践

### 应该

- **尽早编写 ADR** — 在实现开始前
- **保持简短** — 最多 1-2 页
- **诚实面对权衡** — 包含真实的缺点
- **链接相关决策** — 构建决策图
- **更新状态** — 被取代时弃用

### 不应该

- **不要修改已接受的 ADR** — 编写新的来取代
- **不要跳过上下文** — 未来的读者需要背景
- **不要隐藏失败** — 被拒绝的决策也有价值
- **不要模糊** — 具体的决策，具体的后果
- **不要忘记实现** — 没有行动的 ADR 是浪费
