---
name: cost-optimization
description: 通过资源合理化、标签策略、预留实例和支出分析优化 AWS、Azure、GCP 和 OCI 的云成本。在降低云费用、分析基础设施成本或实施成本治理策略时使用。
---

# 云成本优化

优化 AWS、Azure、GCP 和 OCI 云成本的策略和模式。

## 目的

实施系统化的成本优化策略，在保持性能和可靠性的同时降低云支出。

## 使用场景

- 降低云支出
- 合理化资源
- 实施成本治理
- 优化多云成本
- 满足预算约束

## 成本优化框架

### 1. 可见性

- 实施成本分配标签
- 使用云成本管理工具
- 设置预算警报
- 创建成本仪表板

### 2. 合理化

- 分析资源利用率
- 缩减过度配置的资源
- 使用自动扩展
- 移除闲置资源

### 3. 定价模型

- 使用预留容量
- 利用竞价/可抢占实例
- 实施节省计划
- 使用承诺使用折扣

### 4. 架构优化

- 使用托管服务
- 实施缓存
- 优化数据传输
- 使用生命周期策略

## AWS 成本优化

### 预留实例

```
节省：与按需相比 30-72%
期限：1 年或 3 年
付款方式：全部/部分/无预付
灵活性：标准或可转换
```

### 节省计划

```
计算节省计划：节省 66%
EC2 实例节省计划：节省 72%
适用于：EC2、Fargate、Lambda
跨实例系列、区域、操作系统灵活使用
```

### 竞价实例

```
节省：与按需相比高达 90%
最适合：批处理作业、CI/CD、无状态工作负载
风险：2 分钟中断通知
策略：与按需混合使用以提高弹性
```

### S3 成本优化

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

## Azure 成本优化

### 预留 VM 实例

- 1 年或 3 年期限
- 节省高达 72%
- 灵活大小
- 可交换

### Azure 混合权益

- 使用现有 Windows Server 许可证
- 与 RI 结合可节省高达 80%
- 适用于 Windows 和 SQL Server

### Azure Advisor 建议

- 合理化 VM
- 删除未使用的资源
- 使用预留容量
- 优化存储

## GCP 成本优化

### 承诺使用折扣

- 1 年或 3 年承诺
- 节省高达 57%
- 适用于 vCPU 和内存
- 基于资源或基于支出

### 持续使用折扣

- 自动折扣
- 运行实例最高可节省 30%
- 无需承诺
- 适用于 Compute Engine、GKE

### 可抢占 VM

- 节省高达 80%
- 最长 24 小时运行时间
- 最适合批处理工作负载

## OCI 成本优化

### 灵活形状

- 独立扩展 OCPU 和内存
- 将实例大小与工作负载需求匹配
- 减少固定 VM 形状的浪费容量

### 承诺和预算

- 对可预测支出使用年度承诺
- 设置分区级预算并附带警报
- 使用 OCI 成本分析跟踪月度预测

### 可抢占容量

- 对批处理和临时工作负载使用可抢占实例
- 保持中断容忍的自动扩展组
- 与标准容量混合用于关键服务

## 标签策略

### AWS 标签

```hcl
locals {
  common_tags = {
    Environment = "production"
    Project     = "my-project"
    CostCenter  = "engineering"
    Owner       = "team@example.com"
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  tags = merge(
    local.common_tags,
    {
      Name = "web-server"
    }
  )
}
```

**参考：** 见 `references/tagging-standards.md`

## 成本监控

### 预算警报

```hcl
# AWS Budget
resource "aws_budgets_budget" "monthly" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "1000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["team@example.com"]
  }
}
```

### 成本异常检测

- AWS 成本异常检测
- Azure 成本管理警报
- GCP 预算警报
- OCI 预算和成本分析

## 架构模式

### 模式 1：无服务器优先

- 对事件驱动使用 Lambda/Functions
- 仅按执行时间付费
- 包含自动扩展
- 无闲置成本

### 模式 2：合理大小的数据库

```
开发环境：t3.small RDS
预发布环境：t3.large RDS
生产环境：r6g.2xlarge RDS 带只读副本
```

### 模式 3：多层存储

```
热数据：S3 Standard
温数据：S3 Standard-IA（30 天）
冷数据：S3 Glacier（90 天）
归档：S3 Deep Archive（365 天）
```

### 模式 4：自动扩展

```hcl
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}
```

## 成本优化清单

- [ ] 实施成本分配标签
- [ ] 删除未使用的资源（EBS、EIP、快照）
- [ ] 基于利用率合理化实例
- [ ] 对稳定工作负载使用预留容量
- [ ] 实施自动扩展
- [ ] 优化存储类别
- [ ] 使用生命周期策略
- [ ] 启用成本异常检测
- [ ] 设置预算警报
- [ ] 每周审查成本
- [ ] 使用竞价/可抢占实例
- [ ] 优化数据传输成本
- [ ] 实施缓存层
- [ ] 使用托管服务
- [ ] 持续监控和优化

## 工具

- **AWS：** Cost Explorer、Cost Anomaly Detection、Compute Optimizer
- **Azure：** Cost Management、Advisor
- **GCP：** Cost Management、Recommender
- **OCI：** Cost Analysis、Budgets、Cloud Advisor
- **多云：** CloudHealth、Cloudability、Kubecost


## 相关技能

- `terraform-module-library` - 用于资源配置
- `multi-cloud-architecture` - 用于云选择
