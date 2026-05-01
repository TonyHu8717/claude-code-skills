---
name: stride-analysis-patterns
description: 应用 STRIDE 方法论系统性地识别威胁。适用于分析系统安全、进行威胁建模会议或创建安全文档。
---

# STRIDE 分析模式

使用 STRIDE 方法论进行系统性威胁识别。

## 何时使用此技能

- 开始新的威胁建模会议
- 分析现有系统架构
- 审查安全设计决策
- 创建威胁文档
- 培训团队进行威胁识别
- 合规和审计准备

## 核心概念

### 1. STRIDE 类别

```
S - Spoofing（欺骗）       → 认证威胁
T - Tampering（篡改）      → 完整性威胁
R - Repudiation（抵赖）    → 不可否认性威胁
I - Information             → 机密性威胁
    Disclosure（信息泄露）
D - Denial of               → 可用性威胁
    Service（拒绝服务）
E - Elevation of            → 授权威胁
    Privilege（权限提升）
```

### 2. 威胁分析矩阵

| 类别                | 问题                                    | 控制族       |
| ------------------- | --------------------------------------- | ------------ |
| **欺骗**            | 攻击者能否冒充他人？                    | 认证         |
| **篡改**            | 攻击者能否修改传输/静态数据？           | 完整性       |
| **抵赖**            | 攻击者能否否认操作？                    | 日志/审计    |
| **信息泄露**        | 攻击者能否访问未授权数据？              | 加密         |
| **拒绝服务**        | 攻击者能否破坏可用性？                  | 速率限制     |
| **权限提升**        | 攻击者能否获取更高权限？                | 授权         |

## 模板

### 模板 1：STRIDE 威胁模型文档

```markdown
# 威胁模型：[系统名称]

## 1. 系统概述

### 1.1 描述

[系统及其用途的简要描述]

### 1.2 数据流图
```

[用户] --> [Web 应用] --> [API 网关] --> [后端服务]
|
v
[数据库]

```

### 1.3 信任边界
- **外部边界**：互联网到 DMZ
- **内部边界**：DMZ 到内部网络
- **数据边界**：应用到数据库

## 2. 资产

| 资产 | 敏感度 | 描述 |
|------|--------|------|
| 用户凭据 | 高 | 认证令牌、密码 |
| 个人数据 | 高 | PII、财务信息 |
| 会话数据 | 中 | 活跃用户会话 |
| 应用日志 | 中 | 系统活动记录 |
| 配置 | 高 | 系统设置、密钥 |

## 3. STRIDE 分析

### 3.1 欺骗威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| S1 | 会话劫持 | 用户会话 | 高 | 中 |
| S2 | 令牌伪造 | JWT 令牌 | 高 | 低 |
| S3 | 凭据填充 | 登录端点 | 高 | 高 |

**缓解措施：**
- [ ] 实施 MFA
- [ ] 使用安全会话管理
- [ ] 实施账户锁定策略

### 3.2 篡改威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| T1 | SQL 注入 | 数据库查询 | 严重 | 中 |
| T2 | 参数操纵 | API 请求 | 高 | 高 |
| T3 | 文件上传滥用 | 文件存储 | 高 | 中 |

**缓解措施：**
- [ ] 所有端点的输入验证
- [ ] 参数化查询
- [ ] 文件类型验证

### 3.3 抵赖威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| R1 | 交易否认 | 财务操作 | 高 | 中 |
| R2 | 访问日志篡改 | 审计日志 | 中 | 低 |
| R3 | 操作归因 | 用户操作 | 中 | 中 |

**缓解措施：**
- [ ] 全面的审计日志
- [ ] 日志完整性保护
- [ ] 关键操作的数字签名

### 3.4 信息泄露威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| I1 | 数据泄露 | 用户 PII | 严重 | 中 |
| I2 | 错误消息泄露 | 系统信息 | 低 | 高 |
| I3 | 不安全传输 | 网络流量 | 高 | 中 |

**缓解措施：**
- [ ] 静态和传输加密
- [ ] 清理错误消息
- [ ] 实施 TLS 1.3

### 3.5 拒绝服务威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| D1 | 资源耗尽 | API 服务器 | 高 | 高 |
| D2 | 数据库过载 | 数据库 | 严重 | 中 |
| D3 | 带宽饱和 | 网络 | 高 | 中 |

**缓解措施：**
- [ ] 速率限制
- [ ] 自动扩缩容
- [ ] DDoS 防护

### 3.6 权限提升威胁

| ID | 威胁 | 目标 | 影响 | 可能性 |
|----|------|------|------|--------|
| E1 | IDOR 漏洞 | 用户资源 | 高 | 高 |
| E2 | 角色操纵 | 管理员访问 | 严重 | 低 |
| E3 | JWT 声明篡改 | 授权 | 高 | 中 |

**缓解措施：**
- [ ] 正确的授权检查
- [ ] 最小权限原则
- [ ] 服务端角色验证

## 4. 风险评估

### 4.1 风险矩阵

```

              影响
         低   中   高   严重
    低   1    2    3    4

可 中   2    4    6    8
能 高   3    6    9    12
性 严重  4    8    12   16

```

### 4.2 优先级排序风险

| 排名 | 威胁 | 风险分数 | 优先级 |
|------|------|---------|--------|
| 1 | SQL 注入 (T1) | 12 | 严重 |
| 2 | IDOR (E1) | 9 | 高 |
| 3 | 凭据填充 (S3) | 9 | 高 |
| 4 | 数据泄露 (I1) | 8 | 高 |

## 5. 建议

### 立即行动
1. 实施输入验证框架
2. 为认证端点添加速率限制
3. 启用全面的审计日志

### 短期（30 天）
1. 部署带有 OWASP 规则集的 WAF
2. 为敏感操作实施 MFA
3. 加密所有静态 PII

### 长期（90 天）
1. 安全意识培训
2. 渗透测试
3. 漏洞赏金计划
```

### 模板 2：STRIDE 分析代码

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import json

class StrideCategory(Enum):
    SPOOFING = "S"
    TAMPERING = "T"
    REPUDIATION = "R"
    INFORMATION_DISCLOSURE = "I"
    DENIAL_OF_SERVICE = "D"
    ELEVATION_OF_PRIVILEGE = "E"


class Impact(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Likelihood(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Threat:
    id: str
    category: StrideCategory
    title: str
    description: str
    target: str
    impact: Impact
    likelihood: Likelihood
    mitigations: List[str] = field(default_factory=list)
    status: str = "open"

    @property
    def risk_score(self) -> int:
        return self.impact.value * self.likelihood.value

    @property
    def risk_level(self) -> str:
        score = self.risk_score
        if score >= 12:
            return "Critical"
        elif score >= 6:
            return "High"
        elif score >= 3:
            return "Medium"
        return "Low"


@dataclass
class Asset:
    name: str
    sensitivity: str
    description: str
    data_classification: str


@dataclass
class TrustBoundary:
    name: str
    description: str
    from_zone: str
    to_zone: str


@dataclass
class ThreatModel:
    name: str
    version: str
    description: str
    assets: List[Asset] = field(default_factory=list)
    boundaries: List[TrustBoundary] = field(default_factory=list)
    threats: List[Threat] = field(default_factory=list)

    def add_threat(self, threat: Threat) -> None:
        self.threats.append(threat)

    def get_threats_by_category(self, category: StrideCategory) -> List[Threat]:
        return [t for t in self.threats if t.category == category]

    def get_critical_threats(self) -> List[Threat]:
        return [t for t in self.threats if t.risk_level in ("Critical", "High")]

    def generate_report(self) -> Dict:
        """生成威胁模型报告。"""
        return {
            "summary": {
                "name": self.name,
                "version": self.version,
                "total_threats": len(self.threats),
                "critical_threats": len([t for t in self.threats if t.risk_level == "Critical"]),
                "high_threats": len([t for t in self.threats if t.risk_level == "High"]),
            },
            "by_category": {
                cat.name: len(self.get_threats_by_category(cat))
                for cat in StrideCategory
            },
            "top_risks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "risk_score": t.risk_score,
                    "risk_level": t.risk_level
                }
                for t in sorted(self.threats, key=lambda x: x.risk_score, reverse=True)[:10]
            ]
        }


class StrideAnalyzer:
    """自动化 STRIDE 分析助手。"""

    STRIDE_QUESTIONS = {
        StrideCategory.SPOOFING: [
            "攻击者能否冒充合法用户？",
            "认证令牌是否正确验证？",
            "会话标识符是否可预测或被盗？",
            "是否提供多因素认证？",
        ],
        StrideCategory.TAMPERING: [
            "数据在传输过程中能否被修改？",
            "数据在静态存储中能否被修改？",
            "输入验证控制是否充分？",
            "攻击者能否操纵应用逻辑？",
        ],
        StrideCategory.REPUDIATION: [
            "所有安全相关操作是否被记录？",
            "日志是否可被篡改？",
            "操作是否有充分的归因？",
            "时间戳是否可靠且同步？",
        ],
        StrideCategory.INFORMATION_DISCLOSURE: [
            "敏感数据是否加密存储？",
            "敏感数据是否加密传输？",
            "错误消息是否泄露敏感信息？",
            "访问控制是否正确执行？",
        ],
        StrideCategory.DENIAL_OF_SERVICE: [
            "是否实施了速率限制？",
            "资源是否可被恶意输入耗尽？",
            "是否有放大攻击防护？",
            "是否存在单点故障？",
        ],
        StrideCategory.ELEVATION_OF_PRIVILEGE: [
            "授权检查是否一致执行？",
            "用户能否访问其他用户的资源？",
            "是否可通过参数操纵进行权限提升？",
            "是否遵循最小权限原则？",
        ],
    }

    def generate_questionnaire(self, component: str) -> List[Dict]:
        """为组件生成 STRIDE 问卷。"""
        questionnaire = []
        for category, questions in self.STRIDE_QUESTIONS.items():
            for q in questions:
                questionnaire.append({
                    "component": component,
                    "category": category.name,
                    "question": q,
                    "answer": None,
                    "notes": ""
                })
        return questionnaire

    def suggest_mitigations(self, category: StrideCategory) -> List[str]:
        """为 STRIDE 类别建议常见缓解措施。"""
        mitigations = {
            StrideCategory.SPOOFING: [
                "实施多因素认证",
                "使用安全会话管理",
                "实施账户锁定策略",
                "使用加密安全令牌",
                "在每次请求时验证认证",
            ],
            StrideCategory.TAMPERING: [
                "实施输入验证",
                "使用参数化查询",
                "应用完整性检查（HMAC、签名）",
                "实施内容安全策略",
                "使用不可变基础设施",
            ],
            StrideCategory.REPUDIATION: [
                "启用全面的审计日志",
                "保护日志完整性",
                "实施数字签名",
                "使用集中式、防篡改日志",
                "维护准确的时间戳",
            ],
            StrideCategory.INFORMATION_DISCLOSURE: [
                "加密静态和传输数据",
                "实施正确的访问控制",
                "清理错误消息",
                "使用安全默认值",
                "实施数据分类",
            ],
            StrideCategory.DENIAL_OF_SERVICE: [
                "实施速率限制",
                "使用自动扩缩容",
                "部署 DDoS 防护",
                "实施断路器",
                "设置资源配额",
            ],
            StrideCategory.ELEVATION_OF_PRIVILEGE: [
                "实施正确的授权",
                "遵循最小权限原则",
                "在服务端验证权限",
                "使用基于角色的访问控制",
                "实施安全边界",
            ],
        }
        return mitigations.get(category, [])
```

### 模板 3：数据流图分析

```python
from dataclasses import dataclass
from typing import List, Set, Tuple
from enum import Enum

class ElementType(Enum):
    EXTERNAL_ENTITY = "external"
    PROCESS = "process"
    DATA_STORE = "datastore"
    DATA_FLOW = "dataflow"


@dataclass
class DFDElement:
    id: str
    name: str
    type: ElementType
    trust_level: int  # 0 = 不受信任，越高越受信任
    description: str = ""


@dataclass
class DataFlow:
    id: str
    name: str
    source: str
    destination: str
    data_type: str
    protocol: str
    encrypted: bool = False


class DFDAnalyzer:
    """分析数据流图以识别 STRIDE 威胁。"""

    def __init__(self):
        self.elements: Dict[str, DFDElement] = {}
        self.flows: List[DataFlow] = []

    def add_element(self, element: DFDElement) -> None:
        self.elements[element.id] = element

    def add_flow(self, flow: DataFlow) -> None:
        self.flows.append(flow)

    def find_trust_boundary_crossings(self) -> List[Tuple[DataFlow, int]]:
        """查找跨越信任边界的数据流。"""
        crossings = []
        for flow in self.flows:
            source = self.elements.get(flow.source)
            dest = self.elements.get(flow.destination)
            if source and dest and source.trust_level != dest.trust_level:
                trust_diff = abs(source.trust_level - dest.trust_level)
                crossings.append((flow, trust_diff))
        return sorted(crossings, key=lambda x: x[1], reverse=True)

    def identify_threats_per_element(self) -> Dict[str, List[StrideCategory]]:
        """将适用的 STRIDE 类别映射到元素类型。"""
        threat_mapping = {
            ElementType.EXTERNAL_ENTITY: [
                StrideCategory.SPOOFING,
                StrideCategory.REPUDIATION,
            ],
            ElementType.PROCESS: [
                StrideCategory.SPOOFING,
                StrideCategory.TAMPERING,
                StrideCategory.REPUDIATION,
                StrideCategory.INFORMATION_DISCLOSURE,
                StrideCategory.DENIAL_OF_SERVICE,
                StrideCategory.ELEVATION_OF_PRIVILEGE,
            ],
            ElementType.DATA_STORE: [
                StrideCategory.TAMPERING,
                StrideCategory.REPUDIATION,
                StrideCategory.INFORMATION_DISCLOSURE,
                StrideCategory.DENIAL_OF_SERVICE,
            ],
            ElementType.DATA_FLOW: [
                StrideCategory.TAMPERING,
                StrideCategory.INFORMATION_DISCLOSURE,
                StrideCategory.DENIAL_OF_SERVICE,
            ],
        }

        result = {}
        for elem_id, elem in self.elements.items():
            result[elem_id] = threat_mapping.get(elem.type, [])
        return result

    def analyze_unencrypted_flows(self) -> List[DataFlow]:
        """查找跨越信任边界的未加密数据流。"""
        risky_flows = []
        for flow in self.flows:
            if not flow.encrypted:
                source = self.elements.get(flow.source)
                dest = self.elements.get(flow.destination)
                if source and dest and source.trust_level != dest.trust_level:
                    risky_flows.append(flow)
        return risky_flows

    def generate_threat_enumeration(self) -> List[Dict]:
        """生成全面的威胁枚举。"""
        threats = []
        element_threats = self.identify_threats_per_element()

        for elem_id, categories in element_threats.items():
            elem = self.elements[elem_id]
            for category in categories:
                threats.append({
                    "element_id": elem_id,
                    "element_name": elem.name,
                    "element_type": elem.type.value,
                    "stride_category": category.name,
                    "description": f"{category.name} threat against {elem.name}",
                    "trust_level": elem.trust_level
                })

        return threats
```

### 模板 4：每交互 STRIDE 分析

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Interaction:
    """表示两个组件之间的交互。"""
    id: str
    source: str
    target: str
    action: str
    data: str
    protocol: str


class StridePerInteraction:
    """对系统中的每个交互应用 STRIDE 分析。"""

    INTERACTION_THREATS = {
        # 源类型 -> 目标类型 -> 适用威胁
        ("external", "process"): {
            "S": "外部实体向进程伪造身份",
            "T": "篡改发送到进程的数据",
            "R": "外部实体否认发送数据",
            "I": "传输过程中的数据暴露",
            "D": "用请求淹没进程",
            "E": "利用进程获取权限",
        },
        ("process", "datastore"): {
            "T": "进程篡改存储数据",
            "R": "进程否认数据修改",
            "I": "进程未授权访问数据",
            "D": "进程耗尽存储资源",
        },
        ("process", "process"): {
            "S": "进程冒充另一个进程",
            "T": "篡改进程间数据",
            "I": "进程间数据泄露",
            "D": "一个进程压倒另一个进程",
            "E": "进程获取提升的访问权限",
        },
    }

    def analyze_interaction(
        self,
        interaction: Interaction,
        source_type: str,
        target_type: str
    ) -> List[Dict]:
        """分析单个交互的 STRIDE 威胁。"""
        threats = []
        key = (source_type, target_type)

        applicable_threats = self.INTERACTION_THREATS.get(key, {})

        for stride_code, description in applicable_threats.items():
            threats.append({
                "interaction_id": interaction.id,
                "source": interaction.source,
                "target": interaction.target,
                "stride_category": stride_code,
                "threat_description": description,
                "context": f"{interaction.action} - {interaction.data}",
            })

        return threats

    def generate_threat_matrix(
        self,
        interactions: List[Interaction],
        element_types: Dict[str, str]
    ) -> List[Dict]:
        """为所有交互生成完整的威胁矩阵。"""
        all_threats = []

        for interaction in interactions:
            source_type = element_types.get(interaction.source, "unknown")
            target_type = element_types.get(interaction.target, "unknown")

            threats = self.analyze_interaction(
                interaction, source_type, target_type
            )
            all_threats.extend(threats)

        return all_threats
```

## 最佳实践

### 应该做的

- **涉及利益相关者** — 安全、开发和运维视角
- **系统化** — 覆盖所有 STRIDE 类别
- **现实地排优先级** — 聚焦高影响威胁
- **定期更新** — 威胁模型是活文档
- **使用可视化辅助** — 数据流图有助于沟通

### 不应该做的

- **不要跳过类别** — 每个类别揭示不同威胁
- **不要假设安全** — 质疑每个组件
- **不要孤立工作** — 协作建模更好
- **不要忽视低概率** — 高影响威胁很重要
- **不要止步于识别** — 跟进缓解措施
