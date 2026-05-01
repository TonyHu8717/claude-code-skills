---
name: terraform-module-library
description: 为 AWS、Azure、GCP 和 OCI 基础设施构建可复用的 Terraform 模块，遵循基础设施即代码最佳实践。适用于创建基础设施模块、标准化云资源配置或实现可复用的 IaC 组件时使用。
---

# Terraform 模块库

适用于 AWS、Azure、GCP 和 OCI 基础设施的生产级 Terraform 模块模式。

## 用途

为跨多个云提供商的常见云基础设施模式创建可复用、经过充分测试的 Terraform 模块。

## 何时使用

- 构建可复用的基础设施组件
- 标准化云资源配置
- 实现基础设施即代码最佳实践
- 创建多云兼容模块
- 建立组织级 Terraform 标准

## 模块结构

```
terraform-modules/
├── aws/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── s3/
├── azure/
│   ├── vnet/
│   ├── aks/
│   └── storage/
├── gcp/
│   ├── vpc/
│   ├── gke/
│   └── cloud-sql/
└── oci/
    ├── vcn/
    ├── oke/
    └── object-storage/
```

## 标准模块模式

```
module-name/
├── main.tf          # 主要资源
├── variables.tf     # 输入变量
├── outputs.tf       # 输出值
├── versions.tf      # 提供者版本
├── README.md        # 文档
├── examples/        # 使用示例
│   └── complete/
│       ├── main.tf
│       └── variables.tf
└── tests/           # Terratest 测试文件
    └── module_test.go
```

## AWS VPC 模块示例

**main.tf:**

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.name
    },
    var.tags
  )
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.name}-private-${count.index + 1}"
      Tier = "private"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  count  = var.create_internet_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.name}-igw"
    },
    var.tags
  )
}
```

**variables.tf:**

```hcl
variable "name" {
  description = "Name of the VPC"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", var.cidr_block))
    error_message = "CIDR block must be valid IPv4 CIDR notation."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = []
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

**outputs.tf:**

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr_block" {
  description = "CIDR block of VPC"
  value       = aws_vpc.main.cidr_block
}
```

## 最佳实践

1. **使用语义化版本** 管理模块
2. **为所有变量编写文档** 并附描述
3. **提供使用示例** 放在 examples/ 目录中
4. **使用验证块** 进行输入校验
5. **输出重要属性** 以便模块组合使用
6. **固定提供者版本** 在 versions.tf 中
7. **使用 locals** 处理计算值
8. **实现条件资源** 使用 count/for_each
9. **测试模块** 使用 Terratest
10. **统一标记所有资源**

**参考：** 参见 `references/aws-modules.md` 和 `references/oci-modules.md`

## 模块组合

```hcl
module "vpc" {
  source = "../../modules/aws/vpc"

  name               = "production"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  private_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

module "rds" {
  source = "../../modules/aws/rds"

  identifier     = "production-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.large"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  tags = {
    Environment = "production"
  }
}
```


## 测试

```go
// tests/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

## 相关技能

- `multi-cloud-architecture` - 用于架构决策
- `cost-optimization` - 用于成本优化设计
