---
name: gdpr-data-handling
description: 实现符合 GDPR 的数据处理，包括同意管理、数据主体权利和隐私设计。在构建处理欧盟个人数据的系统、实现隐私控制或进行 GDPR 合规审查时使用。
---

# GDPR 数据处理

符合 GDPR 的数据处理、同意管理和隐私控制的实用实现指南。

## 何时使用此技能

- 构建处理欧盟个人数据的系统
- 实现同意管理
- 处理数据主体请求（DSR）
- 进行 GDPR 合规审查
- 设计隐私优先的架构
- 创建数据处理协议

## 核心概念

### 1. 个人数据类别

| 类别               | 示例                    | 保护级别   |
| ---------------------- | --------------------------- | ------------------ |
| **基本**              | 姓名、电子邮件、电话          | 标准           |
| **敏感（第 9 条）** | 健康、宗教、种族 | 明确同意   |
| **刑事（第 10 条）** | 定罪、违法行为       | 官方机构 |
| **儿童**         | 16 岁以下数据               | 父母同意   |

### 2. 处理的法律依据

```
第 6 条 - 合法依据：
├── 同意：自由给予、具体、知情
├── 合同：履行合同所必需
├── 法律义务：法律要求
├── 利益攸关：保护某人生命
├── 公共利益：官方职能
└── 正当利益：与权利平衡
```

### 3. 数据主体权利

```
访问权（第 15 条）      ─┐
更正权（第 16 条） │
删除权（第 17 条）       │ 必须在 1 个月内
限制权（第 18 条）      │ 响应
可携权（第 20 条）   │
反对权（第 21 条）       ─┘
```

## 实现模式

### 模式 1：同意管理

```javascript
// 同意数据模型
const consentSchema = {
  userId: String,
  consents: [
    {
      purpose: String, // 'marketing', 'analytics' 等
      granted: Boolean,
      timestamp: Date,
      source: String, // 'web_form', 'api' 等
      version: String, // 隐私政策版本
      ipAddress: String, // 用于证明
      userAgent: String, // 用于证明
    },
  ],
  auditLog: [
    {
      action: String, // 'granted', 'withdrawn', 'updated'
      purpose: String,
      timestamp: Date,
      source: String,
    },
  ],
};

// 同意服务
class ConsentManager {
  async recordConsent(userId, purpose, granted, metadata) {
    const consent = {
      purpose,
      granted,
      timestamp: new Date(),
      source: metadata.source,
      version: await this.getCurrentPolicyVersion(),
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
    };

    // 存储同意
    await this.db.consents.updateOne(
      { userId },
      {
        $push: {
          consents: consent,
          auditLog: {
            action: granted ? "granted" : "withdrawn",
            purpose,
            timestamp: consent.timestamp,
            source: metadata.source,
          },
        },
      },
      { upsert: true },
    );

    // 发出事件供下游系统使用
    await this.eventBus.emit("consent.changed", {
      userId,
      purpose,
      granted,
      timestamp: consent.timestamp,
    });
  }

  async hasConsent(userId, purpose) {
    const record = await this.db.consents.findOne({ userId });
    if (!record) return false;

    const latestConsent = record.consents
      .filter((c) => c.purpose === purpose)
      .sort((a, b) => b.timestamp - a.timestamp)[0];

    return latestConsent?.granted === true;
  }

  async getConsentHistory(userId) {
    const record = await this.db.consents.findOne({ userId });
    return record?.auditLog || [];
  }
}
```

```html
<!-- 符合 GDPR 的同意 UI -->
<div class="consent-banner" role="dialog" aria-labelledby="consent-title">
  <h2 id="consent-title">Cookie 偏好设置</h2>

  <p>
    我们使用 cookie 来改善您的体验。请在下方选择您的偏好。
  </p>

  <form id="consent-form">
    <!-- 必要 - 始终开启，无需同意 -->
    <div class="consent-category">
      <input type="checkbox" id="necessary" checked disabled />
      <label for="necessary">
        <strong>必要</strong>
        <span>网站运行所必需。无法禁用。</span>
      </label>
    </div>

    <!-- 分析 - 需要同意 -->
    <div class="consent-category">
      <input type="checkbox" id="analytics" name="analytics" />
      <label for="analytics">
        <strong>分析</strong>
        <span>帮助我们了解您如何使用我们的网站。</span>
      </label>
    </div>

    <!-- 营销 - 需要同意 -->
    <div class="consent-category">
      <input type="checkbox" id="marketing" name="marketing" />
      <label for="marketing">
        <strong>营销</strong>
        <span>基于您兴趣的个性化广告。</span>
      </label>
    </div>

    <div class="consent-actions">
      <button type="button" id="accept-all">全部接受</button>
      <button type="button" id="reject-all">全部拒绝</button>
      <button type="submit">保存偏好</button>
    </div>

    <p class="consent-links">
      <a href="/privacy-policy">隐私政策</a> |
      <a href="/cookie-policy">Cookie 政策</a>
    </p>
  </form>
</div>
```

### 模式 2：数据主体访问请求（DSAR）

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class DSARHandler:
    """处理数据主体访问请求。"""

    RESPONSE_DEADLINE_DAYS = 30
    EXTENSION_ALLOWED_DAYS = 60  # 对于复杂请求

    def __init__(self, data_sources: List['DataSource']):
        self.data_sources = data_sources

    async def submit_request(
        self,
        request_type: str,  # 'access', 'erasure', 'rectification', 'portability'
        user_id: str,
        verified: bool,
        details: Optional[Dict] = None
    ) -> str:
        """提交新的 DSAR。"""
        request = {
            'id': self.generate_request_id(),
            'type': request_type,
            'user_id': user_id,
            'status': 'pending_verification' if not verified else 'processing',
            'submitted_at': datetime.utcnow(),
            'deadline': datetime.utcnow() + timedelta(days=self.RESPONSE_DEADLINE_DAYS),
            'details': details or {},
            'audit_log': [{
                'action': 'submitted',
                'timestamp': datetime.utcnow(),
                'details': 'Request received'
            }]
        }

        await self.db.dsar_requests.insert_one(request)
        await self.notify_dpo(request)

        return request['id']

    async def process_access_request(self, request_id: str) -> Dict:
        """处理数据访问请求。"""
        request = await self.get_request(request_id)

        if request['type'] != 'access':
            raise ValueError("Not an access request")

        # 从所有来源收集数据
        user_data = {}
        for source in self.data_sources:
            try:
                data = await source.get_user_data(request['user_id'])
                user_data[source.name] = data
            except Exception as e:
                user_data[source.name] = {'error': str(e)}

        # 格式化响应
        response = {
            'request_id': request_id,
            'generated_at': datetime.utcnow().isoformat(),
            'data_categories': list(user_data.keys()),
            'data': user_data,
            'retention_info': await self.get_retention_info(),
            'processing_purposes': await self.get_processing_purposes(),
            'third_party_recipients': await self.get_recipients()
        }

        # 更新请求状态
        await self.update_request(request_id, 'completed', response)

        return response

    async def process_erasure_request(self, request_id: str) -> Dict:
        """处理删除权请求。"""
        request = await self.get_request(request_id)

        if request['type'] != 'erasure':
            raise ValueError("Not an erasure request")

        results = {}
        exceptions = []

        for source in self.data_sources:
            try:
                # 检查法律例外
                can_delete, reason = await source.can_delete(request['user_id'])

                if can_delete:
                    await source.delete_user_data(request['user_id'])
                    results[source.name] = 'deleted'
                else:
                    exceptions.append({
                        'source': source.name,
                        'reason': reason  # 例如 'legal retention requirement'
                    })
                    results[source.name] = f'retained: {reason}'
            except Exception as e:
                results[source.name] = f'error: {str(e)}'

        response = {
            'request_id': request_id,
            'completed_at': datetime.utcnow().isoformat(),
            'results': results,
            'exceptions': exceptions
        }

        await self.update_request(request_id, 'completed', response)

        return response

    async def process_portability_request(self, request_id: str) -> bytes:
        """生成可移植数据导出。"""
        request = await self.get_request(request_id)
        user_data = await self.process_access_request(request_id)

        # 转换为机器可读格式（JSON）
        portable_data = {
            'export_date': datetime.utcnow().isoformat(),
            'format_version': '1.0',
            'data': user_data['data']
        }

        return json.dumps(portable_data, indent=2, default=str).encode()
```

### 模式 3：数据保留

```python
from datetime import datetime, timedelta
from enum import Enum

class RetentionBasis(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"

class DataRetentionPolicy:
    """定义和执行数据保留策略。"""

    POLICIES = {
        'user_account': {
            'retention_period_days': 365 * 3,  # 最后活动后 3 年
            'basis': RetentionBasis.CONTRACT,
            'trigger': 'last_activity_date',
            'archive_before_delete': True
        },
        'transaction_records': {
            'retention_period_days': 365 * 7,  # 税务要求 7 年
            'basis': RetentionBasis.LEGAL_OBLIGATION,
            'trigger': 'transaction_date',
            'archive_before_delete': True,
            'legal_reference': 'Tax regulations require 7 year retention'
        },
        'marketing_consent': {
            'retention_period_days': 365 * 2,  # 2 年
            'basis': RetentionBasis.CONSENT,
            'trigger': 'consent_date',
            'archive_before_delete': False
        },
        'support_tickets': {
            'retention_period_days': 365 * 2,
            'basis': RetentionBasis.LEGITIMATE_INTEREST,
            'trigger': 'ticket_closed_date',
            'archive_before_delete': True
        },
        'analytics_data': {
            'retention_period_days': 365,  # 1 年
            'basis': RetentionBasis.CONSENT,
            'trigger': 'collection_date',
            'archive_before_delete': False,
            'anonymize_instead': True
        }
    }

    async def apply_retention_policies(self):
        """运行保留策略执行。"""
        for data_type, policy in self.POLICIES.items():
            cutoff_date = datetime.utcnow() - timedelta(
                days=policy['retention_period_days']
            )

            if policy.get('anonymize_instead'):
                await self.anonymize_old_data(data_type, cutoff_date)
            else:
                if policy.get('archive_before_delete'):
                    await self.archive_data(data_type, cutoff_date)
                await self.delete_old_data(data_type, cutoff_date)

            await self.log_retention_action(data_type, cutoff_date)

    async def anonymize_old_data(self, data_type: str, before_date: datetime):
        """匿名化数据而非删除。"""
        # 示例：用哈希替换标识字段
        if data_type == 'analytics_data':
            await self.db.analytics.update_many(
                {'collection_date': {'$lt': before_date}},
                {'$set': {
                    'user_id': None,
                    'ip_address': None,
                    'device_id': None,
                    'anonymized': True,
                    'anonymized_date': datetime.utcnow()
                }}
            )
```

### 模式 4：隐私设计

```python
class PrivacyFirstDataModel:
    """隐私设计数据模型示例。"""

    # 将 PII 与行为数据分离
    user_profile_schema = {
        'user_id': str,  # UUID，非顺序
        'email_hash': str,  # 用于查找的哈希
        'created_at': datetime,
        # 最小数据收集
        'preferences': {
            'language': str,
            'timezone': str
        }
    }

    # 静态加密
    user_pii_schema = {
        'user_id': str,
        'email': str,  # 加密
        'name': str,   # 加密
        'phone': str,  # 加密（可选）
        'address': dict,  # 加密（可选）
        'encryption_key_id': str
    }

    # 假名化行为数据
    analytics_schema = {
        'session_id': str,  # 不与 user_id 关联
        'pseudonym_id': str,  # 轮换假名
        'events': list,
        'device_category': str,  # 泛化，非具体
        'country': str,  # 非城市级别
    }

class DataMinimization:
    """实现数据最小化原则。"""

    @staticmethod
    def collect_only_needed(form_data: dict, purpose: str) -> dict:
        """过滤表单数据，仅保留目的所需的字段。"""
        REQUIRED_FIELDS = {
            'account_creation': ['email', 'password'],
            'newsletter': ['email'],
            'purchase': ['email', 'name', 'address', 'payment'],
            'support': ['email', 'message']
        }

        allowed = REQUIRED_FIELDS.get(purpose, [])
        return {k: v for k, v in form_data.items() if k in allowed}

    @staticmethod
    def generalize_location(ip_address: str) -> str:
        """将 IP 泛化为国家级别。"""
        import geoip2.database
        reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        try:
            response = reader.country(ip_address)
            return response.country.iso_code
        except:
            return 'UNKNOWN'
```

### 模式 5：泄露通知

```python
from datetime import datetime
from enum import Enum

class BreachSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BreachNotificationHandler:
    """处理 GDPR 泄露通知要求。"""

    AUTHORITY_NOTIFICATION_HOURS = 72
    AFFECTED_NOTIFICATION_REQUIRED_SEVERITY = BreachSeverity.HIGH

    async def report_breach(
        self,
        description: str,
        data_types: List[str],
        affected_count: int,
        severity: BreachSeverity
    ) -> dict:
        """报告和处理数据泄露。"""
        breach = {
            'id': self.generate_breach_id(),
            'reported_at': datetime.utcnow(),
            'description': description,
            'data_types_affected': data_types,
            'affected_individuals_count': affected_count,
            'severity': severity.value,
            'status': 'investigating',
            'timeline': [{
                'event': 'breach_reported',
                'timestamp': datetime.utcnow(),
                'details': description
            }]
        }

        await self.db.breaches.insert_one(breach)

        # 立即通知
        await self.notify_dpo(breach)
        await self.notify_security_team(breach)

        # 必须在 72 小时内通知监管机构
        if self.requires_authority_notification(severity, data_types):
            breach['authority_notification_deadline'] = (
                datetime.utcnow() + timedelta(hours=self.AUTHORITY_NOTIFICATION_HOURS)
            )
            await self.schedule_authority_notification(breach)

        # 受影响个人通知
        if severity.value in [BreachSeverity.HIGH.value, BreachSeverity.CRITICAL.value]:
            await self.schedule_individual_notifications(breach)

        return breach

    def requires_authority_notification(
        self,
        severity: BreachSeverity,
        data_types: List[str]
    ) -> bool:
        """确定是否必须通知监管机构。"""
        # 对敏感数据始终通知
        sensitive_types = ['health', 'financial', 'credentials', 'biometric']
        if any(t in sensitive_types for t in data_types):
            return True

        # 中等及以上严重性通知
        return severity in [BreachSeverity.MEDIUM, BreachSeverity.HIGH, BreachSeverity.CRITICAL]

    async def generate_authority_report(self, breach_id: str) -> dict:
        """生成监管机构报告。"""
        breach = await self.get_breach(breach_id)

        return {
            'organization': {
                'name': self.config.org_name,
                'contact': self.config.dpo_contact,
                'registration': self.config.registration_number
            },
            'breach': {
                'nature': breach['description'],
                'categories_affected': breach['data_types_affected'],
                'approximate_number_affected': breach['affected_individuals_count'],
                'likely_consequences': self.assess_consequences(breach),
                'measures_taken': await self.get_remediation_measures(breach_id),
                'measures_proposed': await self.get_proposed_measures(breach_id)
            },
            'timeline': breach['timeline'],
            'submitted_at': datetime.utcnow().isoformat()
        }
```

## 合规检查清单

```markdown
## GDPR 实施检查清单

### 法律依据

- [ ] 每个处理活动都有记录的法律依据
- [ ] 同意机制符合 GDPR 要求
- [ ] 正当利益评估已完成

### 透明度

- [ ] 隐私政策清晰且可访问
- [ ] 处理目的明确说明
- [ ] 数据保留期限已记录

### 数据主体权利

- [ ] 访问请求流程已实现
- [ ] 删除请求流程已实现
- [ ] 可携性导出可用
- [ ] 更正流程可用
- [ ] 在 30 天截止日期内响应

### 安全

- [ ] 静态加密已实现
- [ ] 传输加密（TLS）
- [ ] 访问控制已到位
- [ ] 审计日志已启用

### 泄露响应

- [ ] 泄露检测机制
- [ ] 72 小时通知流程
- [ ] 泄露文档系统

### 文档

- [ ] 处理活动记录（第 30 条）
- [ ] 数据保护影响评估
- [ ] 与供应商的数据处理协议
```

## 最佳实践

### 应该做

- **最小化数据收集** - 仅收集所需数据
- **记录一切** - 处理活动、法律依据
- **加密 PII** - 静态和传输中
- **实现访问控制** - 基于需要知道的原则
- **定期审计** - 持续验证合规性

### 不应该做

- **不要预选同意框** - 必须是选择加入
- **不要捆绑同意** - 单独分隔各目的
- **不要无限期保留** - 定义并执行保留
- **不要忽视 DSAR** - 需要 30 天内响应
- **不要在没有保障的情况下传输** - 标准合同条款或充分性决定
