---
name: security-requirement-extraction
description: 从威胁模型和业务上下文中推导安全需求。在将威胁转化为可操作需求、创建安全用户故事或构建安全测试用例时使用。
---

# 安全需求提取

将威胁分析转化为可操作的安全需求。

## 何时使用此技能

- 将威胁模型转化为需求
- 编写安全用户故事
- 创建安全测试用例
- 构建安全验收标准
- 合规需求映射
- 安全架构文档

## 核心概念

### 1. 需求类别

```
业务需求 → 安全需求 → 技术控制
    ↓           ↓           ↓
"保护客户    "静态加密    "AES-256 加密
 数据"       PII 数据"    配合 KMS 密钥轮换"
```

### 2. 安全需求类型

| 类型           | 焦点                 | 示例                                |
| -------------- | -------------------- | ----------------------------------- |
| **功能性**     | 系统必须做什么       | "系统必须认证用户"                  |
| **非功能性**   | 系统必须如何执行     | "认证必须在 <2 秒内完成"            |
| **约束**       | 施加的限制           | "必须使用批准的加密库"              |

### 3. 需求属性

| 属性           | 描述                 |
| -------------- | -------------------- |
| **可追溯性**   | 链接到威胁/合规      |
| **可测试性**   | 可验证               |
| **优先级**     | 业务重要性           |
| **风险级别**   | 未满足时的影响       |

## 模板

### 模板 1：安全需求模型

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set
from datetime import datetime

class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class SecurityDomain(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_PROTECTION = "data_protection"
    AUDIT_LOGGING = "audit_logging"
    INPUT_VALIDATION = "input_validation"
    ERROR_HANDLING = "error_handling"
    SESSION_MANAGEMENT = "session_management"
    CRYPTOGRAPHY = "cryptography"
    NETWORK_SECURITY = "network_security"
    AVAILABILITY = "availability"


class ComplianceFramework(Enum):
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"
    NIST_CSF = "nist_csf"
    ISO_27001 = "iso_27001"
    OWASP = "owasp"


@dataclass
class SecurityRequirement:
    id: str
    title: str
    description: str
    req_type: RequirementType
    domain: SecurityDomain
    priority: Priority
    rationale: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    test_cases: List[str] = field(default_factory=list)
    threat_refs: List[str] = field(default_factory=list)
    compliance_refs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: str = "draft"
    owner: str = ""
    created_date: datetime = field(default_factory=datetime.now)

    def to_user_story(self) -> str:
        """转换为用户故事格式。"""
        return f"""
**{self.id}: {self.title}**

作为一个注重安全的系统，
我需要 {self.description.lower()}，
以便 {self.rationale.lower()}。

**验收标准：**
{chr(10).join(f'- [ ] {ac}' for ac in self.acceptance_criteria)}

**优先级：** {self.priority.name}
**领域：** {self.domain.value}
**威胁引用：** {', '.join(self.threat_refs)}
"""

    def to_test_spec(self) -> str:
        """转换为测试规格。"""
        return f"""
## 测试规格：{self.id}

### 需求
{self.description}

### 测试用例
{chr(10).join(f'{i+1}. {tc}' for i, tc in enumerate(self.test_cases))}

### 验收标准验证
{chr(10).join(f'- {ac}' for ac in self.acceptance_criteria)}
"""


@dataclass
class RequirementSet:
    name: str
    version: str
    requirements: List[SecurityRequirement] = field(default_factory=list)

    def add(self, req: SecurityRequirement) -> None:
        self.requirements.append(req)

    def get_by_domain(self, domain: SecurityDomain) -> List[SecurityRequirement]:
        return [r for r in self.requirements if r.domain == domain]

    def get_by_priority(self, priority: Priority) -> List[SecurityRequirement]:
        return [r for r in self.requirements if r.priority == priority]

    def get_by_threat(self, threat_id: str) -> List[SecurityRequirement]:
        return [r for r in self.requirements if threat_id in r.threat_refs]

    def get_critical_requirements(self) -> List[SecurityRequirement]:
        return [r for r in self.requirements if r.priority == Priority.CRITICAL]

    def export_markdown(self) -> str:
        """导出所有需求为 markdown。"""
        lines = [f"# 安全需求：{self.name}\n"]
        lines.append(f"版本：{self.version}\n")

        for domain in SecurityDomain:
            domain_reqs = self.get_by_domain(domain)
            if domain_reqs:
                lines.append(f"\n## {domain.value.replace('_', ' ').title()}\n")
                for req in domain_reqs:
                    lines.append(req.to_user_story())

        return "\n".join(lines)

    def traceability_matrix(self) -> Dict[str, List[str]]:
        """生成威胁到需求的可追溯性矩阵。"""
        matrix = {}
        for req in self.requirements:
            for threat_id in req.threat_refs:
                if threat_id not in matrix:
                    matrix[threat_id] = []
                matrix[threat_id].append(req.id)
        return matrix
```

### 模板 2：威胁到需求提取器

```python
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class ThreatInput:
    id: str
    category: str  # STRIDE 类别
    title: str
    description: str
    target: str
    impact: str
    likelihood: str


class RequirementExtractor:
    """从威胁中提取安全需求。"""

    # STRIDE 类别到安全领域和需求模式的映射
    STRIDE_MAPPINGS = {
        "SPOOFING": {
            "domains": [SecurityDomain.AUTHENTICATION, SecurityDomain.SESSION_MANAGEMENT],
            "patterns": [
                ("为 {target} 实现强认证",
                 "确保 {target} 在授予访问权限前认证所有用户"),
                ("验证 {target} 的身份令牌",
                 "所有认证令牌必须经过密码学验证"),
                ("为 {target} 实现会话管理",
                 "会话必须安全管理并适当过期"),
            ]
        },
        "TAMPERING": {
            "domains": [SecurityDomain.INPUT_VALIDATION, SecurityDomain.DATA_PROTECTION],
            "patterns": [
                ("验证 {target} 的所有输入",
                 "所有输入必须根据预期格式进行验证"),
                ("为 {target} 实现完整性检查",
                 "数据完整性必须使用密码学签名验证"),
                ("保护 {target} 免受修改",
                 "实现控制以防止未授权的数据修改"),
            ]
        },
        "REPUDIATION": {
            "domains": [SecurityDomain.AUDIT_LOGGING],
            "patterns": [
                ("记录 {target} 的所有安全事件",
                 "安全相关事件必须记录以供审计"),
                ("为 {target} 实现不可否认性",
                 "关键操作必须有密码学来源证明"),
                ("保护 {target} 的审计日志",
                 "审计日志必须防篡改且受保护"),
            ]
        },
        "INFORMATION_DISCLOSURE": {
            "domains": [SecurityDomain.DATA_PROTECTION, SecurityDomain.CRYPTOGRAPHY],
            "patterns": [
                ("加密 {target} 中的敏感数据",
                 "敏感数据必须在静态和传输中加密"),
                ("为 {target} 实现访问控制",
                 "数据访问必须基于知情权进行限制"),
                ("防止 {target} 的信息泄露",
                 "错误消息和日志不得暴露敏感信息"),
            ]
        },
        "DENIAL_OF_SERVICE": {
            "domains": [SecurityDomain.AVAILABILITY, SecurityDomain.INPUT_VALIDATION],
            "patterns": [
                ("为 {target} 实现速率限制",
                 "请求必须进行速率限制以防止资源耗尽"),
                ("确保 {target} 的可用性",
                 "系统必须在高负载条件下保持可用"),
                ("为 {target} 实现资源配额",
                 "资源消耗必须有界且受监控"),
            ]
        },
        "ELEVATION_OF_PRIVILEGE": {
            "domains": [SecurityDomain.AUTHORIZATION],
            "patterns": [
                ("强制 {target} 的授权",
                 "所有操作必须基于用户权限进行授权"),
                ("为 {target} 实现最小权限",
                 "用户必须仅拥有最低必要权限"),
                ("验证 {target} 的权限",
                 "权限检查必须在服务器端执行"),
            ]
        },
    }

    def extract_requirements(
        self,
        threats: List[ThreatInput],
        project_name: str
    ) -> RequirementSet:
        """从威胁中提取安全需求。"""
        req_set = RequirementSet(
            name=f"{project_name} 安全需求",
            version="1.0"
        )

        req_counter = 1
        for threat in threats:
            reqs = self._threat_to_requirements(threat, req_counter)
            for req in reqs:
                req_set.add(req)
            req_counter += len(reqs)

        return req_set

    def _threat_to_requirements(
        self,
        threat: ThreatInput,
        start_id: int
    ) -> List[SecurityRequirement]:
        """将单个威胁转换为需求。"""
        requirements = []
        mapping = self.STRIDE_MAPPINGS.get(threat.category, {})
        domains = mapping.get("domains", [])
        patterns = mapping.get("patterns", [])

        priority = self._calculate_priority(threat.impact, threat.likelihood)

        for i, (title_pattern, desc_pattern) in enumerate(patterns):
            req = SecurityRequirement(
                id=f"SR-{start_id + i:03d}",
                title=title_pattern.format(target=threat.target),
                description=desc_pattern.format(target=threat.target),
                req_type=RequirementType.FUNCTIONAL,
                domain=domains[i % len(domains)] if domains else SecurityDomain.DATA_PROTECTION,
                priority=priority,
                rationale=f"缓解威胁：{threat.title}",
                threat_refs=[threat.id],
                acceptance_criteria=self._generate_acceptance_criteria(
                    threat.category, threat.target
                ),
                test_cases=self._generate_test_cases(
                    threat.category, threat.target
                )
            )
            requirements.append(req)

        return requirements

    def _calculate_priority(self, impact: str, likelihood: str) -> Priority:
        """从威胁属性计算需求优先级。"""
        score_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        impact_score = score_map.get(impact.upper(), 2)
        likelihood_score = score_map.get(likelihood.upper(), 2)

        combined = impact_score * likelihood_score

        if combined >= 12:
            return Priority.CRITICAL
        elif combined >= 6:
            return Priority.HIGH
        elif combined >= 3:
            return Priority.MEDIUM
        return Priority.LOW

    def _generate_acceptance_criteria(
        self,
        category: str,
        target: str
    ) -> List[str]:
        """为需求生成验收标准。"""
        criteria_templates = {
            "SPOOFING": [
                f"用户在访问 {target} 前必须认证",
                "认证失败已记录并监控",
                "敏感操作提供多因素认证",
            ],
            "TAMPERING": [
                f"{target} 的所有输入已验证",
                "数据完整性在处理前已验证",
                "修改尝试触发告警",
            ],
            "REPUDIATION": [
                f"{target} 的所有操作已记录用户身份",
                "普通用户无法修改日志",
                "日志保留满足合规要求",
            ],
            "INFORMATION_DISCLOSURE": [
                f"{target} 中的敏感数据已加密",
                "对敏感数据的访问已记录",
                "错误消息不泄露敏感信息",
            ],
            "DENIAL_OF_SERVICE": [
                f"对 {target} 强制执行速率限制",
                "系统在负载下优雅降级",
                "资源耗尽触发告警",
            ],
            "ELEVATION_OF_PRIVILEGE": [
                f"对 {target} 的所有操作检查授权",
                "用户无法访问超出权限的资源",
                "权限变更已记录并监控",
            ],
        }
        return criteria_templates.get(category, [])

    def _generate_test_cases(
        self,
        category: str,
        target: str
    ) -> List[str]:
        """为需求生成测试用例。"""
        test_templates = {
            "SPOOFING": [
                f"测试：对 {target} 的未认证访问被拒绝",
                "测试：无效凭据被拒绝",
                "测试：会话令牌无法伪造",
            ],
            "TAMPERING": [
                f"测试：对 {target} 的无效输入被拒绝",
                "测试：篡改数据被检测并拒绝",
                "测试：SQL 注入尝试被阻止",
            ],
            "REPUDIATION": [
                "测试：安全事件已记录",
                "测试：日志包含足够的取证细节",
                "测试：日志完整性受保护",
            ],
            "INFORMATION_DISCLOSURE": [
                f"测试：{target} 数据在传输中加密",
                f"测试：{target} 数据在静态中加密",
                "测试：错误消息已清理",
            ],
            "DENIAL_OF_SERVICE": [
                f"测试：{target} 的速率限制正常工作",
                "测试：系统优雅处理突发流量",
                "测试：资源限制已执行",
            ],
            "ELEVATION_OF_PRIVILEGE": [
                f"测试：对 {target} 的未授权访问被拒绝",
                "测试：权限提升尝试被阻止",
                "测试：不存在 IDOR 漏洞",
            ],
        }
        return test_templates.get(category, [])
```

### 模板 3：合规映射

```python
from typing import Dict, List, Set

class ComplianceMapper:
    """将安全需求映射到合规框架。"""

    FRAMEWORK_CONTROLS = {
        ComplianceFramework.PCI_DSS: {
            SecurityDomain.AUTHENTICATION: ["8.1", "8.2", "8.3"],
            SecurityDomain.AUTHORIZATION: ["7.1", "7.2"],
            SecurityDomain.DATA_PROTECTION: ["3.4", "3.5", "4.1"],
            SecurityDomain.AUDIT_LOGGING: ["10.1", "10.2", "10.3"],
            SecurityDomain.NETWORK_SECURITY: ["1.1", "1.2", "1.3"],
            SecurityDomain.CRYPTOGRAPHY: ["3.5", "3.6", "4.1"],
        },
        ComplianceFramework.HIPAA: {
            SecurityDomain.AUTHENTICATION: ["164.312(d)"],
            SecurityDomain.AUTHORIZATION: ["164.312(a)(1)"],
            SecurityDomain.DATA_PROTECTION: ["164.312(a)(2)(iv)", "164.312(e)(2)(ii)"],
            SecurityDomain.AUDIT_LOGGING: ["164.312(b)"],
        },
        ComplianceFramework.GDPR: {
            SecurityDomain.DATA_PROTECTION: ["Art. 32", "Art. 25"],
            SecurityDomain.AUDIT_LOGGING: ["Art. 30"],
            SecurityDomain.AUTHORIZATION: ["Art. 25"],
        },
        ComplianceFramework.OWASP: {
            SecurityDomain.AUTHENTICATION: ["V2.1", "V2.2", "V2.3"],
            SecurityDomain.SESSION_MANAGEMENT: ["V3.1", "V3.2", "V3.3"],
            SecurityDomain.INPUT_VALIDATION: ["V5.1", "V5.2", "V5.3"],
            SecurityDomain.CRYPTOGRAPHY: ["V6.1", "V6.2"],
            SecurityDomain.ERROR_HANDLING: ["V7.1", "V7.2"],
            SecurityDomain.DATA_PROTECTION: ["V8.1", "V8.2", "V8.3"],
            SecurityDomain.AUDIT_LOGGING: ["V7.1", "V7.2"],
        },
    }

    def map_requirement_to_compliance(
        self,
        requirement: SecurityRequirement,
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, List[str]]:
        """将需求映射到合规控制。"""
        mapping = {}
        for framework in frameworks:
            controls = self.FRAMEWORK_CONTROLS.get(framework, {})
            domain_controls = controls.get(requirement.domain, [])
            if domain_controls:
                mapping[framework.value] = domain_controls
        return mapping

    def get_requirements_for_control(
        self,
        requirement_set: RequirementSet,
        framework: ComplianceFramework,
        control_id: str
    ) -> List[SecurityRequirement]:
        """查找满足合规控制的需求。"""
        matching = []
        framework_controls = self.FRAMEWORK_CONTROLS.get(framework, {})

        for domain, controls in framework_controls.items():
            if control_id in controls:
                matching.extend(requirement_set.get_by_domain(domain))

        return matching

    def generate_compliance_matrix(
        self,
        requirement_set: RequirementSet,
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Dict[str, List[str]]]:
        """生成合规可追溯性矩阵。"""
        matrix = {}

        for framework in frameworks:
            matrix[framework.value] = {}
            framework_controls = self.FRAMEWORK_CONTROLS.get(framework, {})

            for domain, controls in framework_controls.items():
                for control in controls:
                    reqs = self.get_requirements_for_control(
                        requirement_set, framework, control
                    )
                    if reqs:
                        matrix[framework.value][control] = [r.id for r in reqs]

        return matrix

    def gap_analysis(
        self,
        requirement_set: RequirementSet,
        framework: ComplianceFramework
    ) -> Dict[str, List[str]]:
        """识别合规差距。"""
        gaps = {"missing_controls": [], "weak_coverage": []}
        framework_controls = self.FRAMEWORK_CONTROLS.get(framework, {})

        for domain, controls in framework_controls.items():
            domain_reqs = requirement_set.get_by_domain(domain)
            for control in controls:
                matching = self.get_requirements_for_control(
                    requirement_set, framework, control
                )
                if not matching:
                    gaps["missing_controls"].append(f"{framework.value}:{control}")
                elif len(matching) < 2:
                    gaps["weak_coverage"].append(f"{framework.value}:{control}")

        return gaps
```

### 模板 4：安全用户故事生成器

```python
class SecurityUserStoryGenerator:
    """生成安全聚焦的用户故事。"""

    STORY_TEMPLATES = {
        SecurityDomain.AUTHENTICATION: {
            "as_a": "注重安全的用户",
            "so_that": "我的身份受到保护，免受冒充",
        },
        SecurityDomain.AUTHORIZATION: {
            "as_a": "系统管理员",
            "so_that": "用户只能访问与其角色匹配的资源",
        },
        SecurityDomain.DATA_PROTECTION: {
            "as_a": "数据所有者",
            "so_that": "我的敏感信息保持机密",
        },
        SecurityDomain.AUDIT_LOGGING: {
            "as_a": "安全分析师",
            "so_that": "我可以调查安全事件",
        },
        SecurityDomain.INPUT_VALIDATION: {
            "as_a": "应用开发者",
            "so_that": "系统受到保护，免受恶意输入",
        },
    }

    def generate_story(self, requirement: SecurityRequirement) -> str:
        """从需求生成用户故事。"""
        template = self.STORY_TEMPLATES.get(
            requirement.domain,
            {"as_a": "用户", "so_that": "系统是安全的"}
        )

        story = f"""
## {requirement.id}: {requirement.title}

**用户故事：**
作为 {template['as_a']}，
我希望系统 {requirement.description.lower()}，
以便 {template['so_that']}。

**优先级：** {requirement.priority.name}
**类型：** {requirement.req_type.value}
**领域：** {requirement.domain.value}

**验收标准：**
{self._format_acceptance_criteria(requirement.acceptance_criteria)}

**完成定义：**
- [ ] 实现完成
- [ ] 安全测试通过
- [ ] 代码审查完成
- [ ] 安全审查批准
- [ ] 文档已更新

**安全测试用例：**
{self._format_test_cases(requirement.test_cases)}

**可追溯性：**
- 威胁：{', '.join(requirement.threat_refs) 或 'N/A'}
- 合规：{', '.join(requirement.compliance_refs) 或 'N/A'}
"""
        return story

    def _format_acceptance_criteria(self, criteria: List[str]) -> str:
        return "\n".join(f"- [ ] {c}" for c in criteria) if criteria else "- [ ] 待定"

    def _format_test_cases(self, tests: List[str]) -> str:
        return "\n".join(f"- {t}" for t in tests) if tests else "- 待定"

    def generate_epic(
        self,
        requirement_set: RequirementSet,
        domain: SecurityDomain
    ) -> str:
        """为安全领域生成史诗。"""
        reqs = requirement_set.get_by_domain(domain)

        epic = f"""
# 安全史诗：{domain.value.replace('_', ' ').title()}

## 概述
此史诗涵盖与 {domain.value.replace('_', ' ')} 相关的所有安全需求。

## 业务价值
- 防御 {domain.value.replace('_', ' ')} 相关威胁
- 满足合规要求
- 降低安全风险

## 此史诗中的故事
{chr(10).join(f'- [{r.id}] {r.title}' for r in reqs)}

## 验收标准
- 所有故事完成
- 安全测试通过
- 安全审查批准
- 合规要求满足

## 未实施的风险
- 易受 {domain.value.replace('_', ' ')} 攻击
- 合规违规
- 潜在数据泄露

## 依赖
{chr(10).join(f'- {d}' for r in reqs for d in r.dependencies) 或 '- 未识别'}
"""
        return epic
```

## 最佳实践

### 应该做的

- **追溯到威胁** — 每个需求都应映射到威胁
- **具体明确** — 模糊的需求无法测试
- **包含验收标准** — 定义"完成"
- **考虑合规** — 尽早映射到框架
- **定期审查** — 需求随威胁演进

### 不应该做的

- **不要泛泛而谈** — "要安全"不是需求
- **不要跳过原理解释** — 解释为什么重要
- **不要忽略优先级** — 并非所有需求都同等重要
- **不要忘记可测试性** — 如果无法测试，就无法验证
- **不要孤立工作** — 涉及利益相关者
