---
name: sciomc
description: 编排并行科学家代理进行综合分析，支持 AUTO 模式
argument-hint: <研究目标>
level: 4
---

# 研究技能

编排并行科学家代理进行综合研究工作流，支持可选的 AUTO 模式实现完全自主执行。

## 概述

研究是一个多阶段工作流，将复杂的研究目标分解为并行调查：

1. **分解** — 将研究目标拆分为独立的阶段/假设
2. **执行** — 在每个阶段上运行并行科学家代理
3. **验证** — 交叉验证发现，检查一致性
4. **综合** — 将结果聚合为综合报告

## 使用示例

```
/oh-my-claudecode:sciomc <目标>                     # 标准研究，带用户检查点
/oh-my-claudecode:sciomc AUTO: <目标>               # 完全自主运行直到完成
/oh-my-claudecode:sciomc status                     # 检查当前研究会话状态
/oh-my-claudecode:sciomc resume                     # 恢复中断的研究会话
/oh-my-claudecode:sciomc list                       # 列出所有研究会话
/oh-my-claudecode:sciomc report <session-id>        # 为会话生成报告
```

### 快速示例

```
/oh-my-claudecode:sciomc 不同排序算法的性能特征是什么？
/oh-my-claudecode:sciomc AUTO: 分析此代码库中的认证模式
/oh-my-claudecode:sciomc API 层的错误处理是如何工作的？
```

## 研究协议

### 阶段分解模式

收到研究目标后，分解为 3-7 个独立阶段：

```markdown
## 研究分解

**目标：** <原始研究目标>

### 阶段 1：<阶段名称>
- **焦点：** 此阶段调查的内容
- **假设：** 预期发现（如适用）
- **范围：** 要检查的文件/区域
- **层级：** LOW | MEDIUM | HIGH

### 阶段 2：<阶段名称>
...
```

### 并行科学家调用

通过 Task 工具并行启动独立阶段：

```
// 阶段 1 - 简单数据收集
Task(subagent_type="oh-my-claudecode:scientist", model="haiku", prompt="[RESEARCH_STAGE:1] 调查...")

// 阶段 2 - 标准分析
Task(subagent_type="oh-my-claudecode:scientist", model="sonnet", prompt="[RESEARCH_STAGE:2] 分析...")

// 阶段 3 - 复杂推理
Task(subagent_type="oh-my-claudecode:scientist", model="opus", prompt="[RESEARCH_STAGE:3] 深度分析...")
```

### 智能模型路由

**关键：始终显式传递 `model` 参数！**

| 任务复杂度 | 代理 | 模型 | 用途 |
|------------|------|------|------|
| 数据收集 | `scientist` (model=haiku) | haiku | 文件枚举、模式计数、简单查找 |
| 标准分析 | `scientist` | sonnet | 代码分析、模式检测、文档审查 |
| 复杂推理 | `scientist` | opus | 架构分析、跨领域关注点、假设验证 |

### 路由决策指南

| 研究任务 | 层级 | 示例提示 |
|----------|------|----------|
| "计算 X 出现次数" | LOW | "计算所有 useState 钩子的使用次数" |
| "查找所有匹配 Y 的文件" | LOW | "列出项目中所有测试文件" |
| "分析模式 Z" | MEDIUM | "分析 API 路由中的错误处理模式" |
| "记录 W 如何工作" | MEDIUM | "记录认证流程" |
| "解释为什么 X 发生" | HIGH | "解释为什么缓存层中出现竞态条件" |
| "比较方法 A vs B" | HIGH | "比较 Redux vs Context 在此处的状态管理" |

### 验证循环

并行执行完成后，验证发现：

```
// 交叉验证阶段
Task(subagent_type="oh-my-claudecode:scientist", model="sonnet", prompt="
[RESEARCH_VERIFICATION]
交叉验证这些发现的一致性：

阶段 1 发现：<摘要>
阶段 2 发现：<摘要>
阶段 3 发现：<摘要>

检查：
1. 阶段间的矛盾
2. 缺失的连接
3. 覆盖范围的空白
4. 证据质量

输出：[VERIFIED] 或 [CONFLICTS:<列表>]
")
```

## AUTO 模式

AUTO 模式自主运行完整的研究工作流，带循环控制。

### 循环控制协议

```
[RESEARCH + AUTO - ITERATION {{ITERATION}}/{{MAX}}]

您之前的尝试未输出完成承诺。请继续工作。

当前状态：{{STATE}}
已完成阶段：{{COMPLETED_STAGES}}
待处理阶段：{{PENDING_STAGES}}
```

### 承诺标签

| 标签 | 含义 | 使用时机 |
|------|------|----------|
| `[PROMISE:RESEARCH_COMPLETE]` | 研究成功完成 | 所有阶段完成、已验证、报告已生成 |
| `[PROMISE:RESEARCH_BLOCKED]` | 无法继续 | 缺少数据、访问问题、循环依赖 |

### AUTO 模式规则

1. **最大迭代次数：** 10（可配置）
2. **继续直到：** 发出承诺标签或达到最大迭代次数
3. **状态跟踪：** 每个阶段完成后持久化
4. **取消：** `/oh-my-claudecode:cancel` 或 "stop"、"cancel"

### AUTO 模式示例

```
/oh-my-claudecode:sciomc AUTO: 认证系统的综合安全分析

[分解]
- 阶段 1 (LOW): 枚举认证相关文件
- 阶段 2 (MEDIUM): 分析令牌处理
- 阶段 3 (MEDIUM): 审查会话管理
- 阶段 4 (HIGH): 识别漏洞模式
- 阶段 5 (MEDIUM): 记录安全控制

[执行 - 并行]
并行启动阶段 1-3...
依赖完成后启动阶段 4-5...

[验证]
交叉验证发现...

[综合]
生成报告...

[PROMISE:RESEARCH_COMPLETE]
```

## 并行执行模式

### 独立数据集分析（并行）

当阶段分析不同数据源时：

```
// 全部同时启动
Task(subagent_type="oh-my-claudecode:scientist", model="haiku", prompt="[STAGE:1] 分析 src/api/...")
Task(subagent_type="oh-my-claudecode:scientist", model="haiku", prompt="[STAGE:2] 分析 src/utils/...")
Task(subagent_type="oh-my-claudecode:scientist", model="haiku", prompt="[STAGE:3] 分析 src/components/...")
```

### 假设测试组（并行）

当测试多个假设时：

```
// 同时测试假设
Task(subagent_type="oh-my-claudecode:scientist", model="sonnet", prompt="[HYPOTHESIS:A] 测试缓存是否改善...")
Task(subagent_type="oh-my-claudecode:scientist", model="sonnet", prompt="[HYPOTHESIS:B] 测试批处理是否减少...")
Task(subagent_type="oh-my-claudecode:scientist", model="sonnet", prompt="[HYPOTHESIS:C] 测试延迟加载是否有帮助...")
```

### 交叉验证（顺序）

当验证依赖于所有发现时：

```
// 等待所有并行阶段
[阶段完成]

// 然后顺序验证
Task(subagent_type="oh-my-claudecode:scientist", model="opus", prompt="
[CROSS_VALIDATION]
验证所有发现的一致性：
- 发现 1: ...
- 发现 2: ...
- 发现 3: ...
")
```

### 并发限制

**最多 20 个并发科学家代理**以防止资源耗尽。

如果超过 20 个阶段，分批处理：
```
批次 1: 阶段 1-5（并行）
[等待完成]
批次 2: 阶段 6-7（并行）
```

## 会话管理

### 目录结构

```
.omc/research/{session-id}/
  state.json              # 会话状态和进度
  stages/
    stage-1.md            # 阶段 1 发现
    stage-2.md            # 阶段 2 发现
    ...
  findings/
    raw/                  # 科学家的原始发现
    verified/             # 验证后的发现
  figures/
    figure-1.png          # 生成的可视化
    ...
  report.md               # 最终综合报告
```

### 状态文件格式

```json
{
  "id": "research-20240115-abc123",
  "goal": "原始研究目标",
  "status": "in_progress | complete | blocked | cancelled",
  "mode": "standard | auto",
  "iteration": 3,
  "maxIterations": 10,
  "stages": [
    {
      "id": 1,
      "name": "阶段名称",
      "tier": "LOW | MEDIUM | HIGH",
      "status": "pending | running | complete | failed",
      "startedAt": "ISO 时间戳",
      "completedAt": "ISO 时间戳",
      "findingsFile": "stages/stage-1.md"
    }
  ],
  "verification": {
    "status": "pending | passed | failed",
    "conflicts": [],
    "completedAt": "ISO 时间戳"
  },
  "createdAt": "ISO 时间戳",
  "updatedAt": "ISO 时间戳"
}
```

### 会话命令

| 命令 | 操作 |
|------|------|
| `/oh-my-claudecode:sciomc status` | 显示当前会话进度 |
| `/oh-my-claudecode:sciomc resume` | 恢复最近中断的会话 |
| `/oh-my-claudecode:sciomc resume <session-id>` | 恢复特定会话 |
| `/oh-my-claudecode:sciomc list` | 列出所有会话及状态 |
| `/oh-my-claudecode:sciomc report <session-id>` | 生成/重新生成报告 |
| `/oh-my-claudecode:sciomc cancel` | 取消当前会话（保留状态） |

## 标签提取

科学家使用结构化标签记录发现。使用以下模式提取：

### 发现标签

```
[FINDING:<id>] <标题>
<证据和分析>
[/FINDING]

[EVIDENCE:<finding-id>]
- File: <路径>
- Lines: <范围>
- Content: <相关代码/文本>
[/EVIDENCE]

[CONFIDENCE:<级别>] # HIGH | MEDIUM | LOW
<置信度推理>
```

### 提取正则模式

```javascript
// 发现提取
const findingPattern = /\[FINDING:(\w+)\]\s*(.*?)\n([\s\S]*?)\[\/FINDING\]/g;

// 证据提取
const evidencePattern = /\[EVIDENCE:(\w+)\]([\s\S]*?)\[\/EVIDENCE\]/g;

// 置信度提取
const confidencePattern = /\[CONFIDENCE:(HIGH|MEDIUM|LOW)\]\s*(.*)/g;

// 阶段完成
const stageCompletePattern = /\[STAGE_COMPLETE:(\d+)\]/;

// 验证结果
const verificationPattern = /\[(VERIFIED|CONFLICTS):?(.*?)\]/;
```

### 证据窗口

提取证据时，包含上下文窗口：

```
[EVIDENCE:F1]
- File: /src/auth/login.ts
- Lines: 45-52 (context: 40-57)
- Content:
  ```typescript
  // 第 45-52 行，上下各 5 行上下文
  ```
[/EVIDENCE]
```

### 质量验证

发现必须满足质量阈值：

| 质量检查 | 要求 |
|----------|------|
| 存在证据 | 每个 [FINDING] 至少有 1 个 [EVIDENCE] |
| 声明置信度 | 每个发现有 [CONFIDENCE] |
| 引用来源 | 文件路径是绝对路径且有效 |
| 可重现 | 其他代理可以验证 |

## 报告生成

### 报告模板

```markdown
# 研究报告：{{GOAL}}

**会话 ID：** {{SESSION_ID}}
**日期：** {{DATE}}
**状态：** {{STATUS}}

## 执行摘要

{{关键发现的 2-3 段摘要}}

## 方法论

### 研究阶段

| 阶段 | 焦点 | 层级 | 状态 |
|------|------|------|------|
{{STAGES_TABLE}}

### 方法

{{分解原理和执行策略的描述}}

## 关键发现

### 发现 1：{{TITLE}}

**置信度：** {{HIGH|MEDIUM|LOW}}

{{包含证据的详细发现}}

#### 证据

{{嵌入的证据块}}

### 发现 2：{{TITLE}}
...

## 可视化

{{FIGURES}}

## 交叉验证结果

{{验证摘要，已解决的任何冲突}}

## 局限性

- {{局限性 1}}
- {{局限性 2}}
- {{未覆盖的领域及原因}}

## 建议

1. {{可操作的建议}}
2. {{可操作的建议}}

## 附录

### 原始数据

{{指向原始发现文件的链接}}

### 会话状态

{{指向 state.json 的链接}}
```

### 图表嵌入协议

科学家使用此标记生成可视化：

```
[FIGURE:path/to/figure.png]
Caption: 图表显示内容的描述
Alt: 无障碍描述
[/FIGURE]
```

报告生成器嵌入图表：

```markdown
## 可视化

![图表 1: 描述](figures/figure-1.png)
*说明：图表显示内容的描述*

![图表 2: 描述](figures/figure-2.png)
*说明：图表显示内容的描述*
```

### 图表类型

| 类型 | 用途 | 生成者 |
|------|------|--------|
| 架构图 | 系统结构 | scientist |
| 流程图 | 流程 | scientist |
| 依赖图 | 模块关系 | scientist |
| 时间线 | 事件序列 | scientist |
| 比较表 | A vs B 分析 | scientist |

## 配置

`.claude/settings.json` 中的可选设置：

```json
{
  "omc": {
    "research": {
      "maxIterations": 10,
      "maxConcurrentScientists": 5,
      "defaultTier": "MEDIUM",
      "autoVerify": true,
      "generateFigures": true,
      "evidenceContextLines": 5
    }
  }
}
```

## 取消

```
/oh-my-claudecode:cancel
```

或说："停止研究"、"取消研究"、"中止"

进度保存在 `.omc/research/{session-id}/` 中，可供恢复。

## 故障排除

**卡在验证循环中？**
- 检查阶段间的冲突发现
- 查看 state.json 了解具体冲突
- 可能需要用不同方法重新运行特定阶段

**科学家返回低质量发现？**
- 检查层级分配 — 复杂分析需要 HIGH 层级
- 确保提示包含清晰的范围和预期输出格式
- 审查研究目标是否过于宽泛

**AUTO 模式耗尽迭代次数？**
- 查看状态了解卡在哪里
- 检查目标是否可用数据实现
- 考虑拆分为更小的研究会话

**报告中缺少图表？**
- 验证 figures/ 目录存在
- 检查发现中的 [FIGURE:] 标签
- 确保路径相对于会话目录
