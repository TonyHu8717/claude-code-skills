---
name: hybrid-cloud-networking
description: 使用 VPN 和专用连接配置本地基础设施与云平台之间安全、高性能的连接。在构建混合云架构、将数据中心连接到云或实现安全的跨本地网络时使用。
---

# 混合云网络

使用 VPN、Direct Connect、ExpressRoute、Interconnect 和 FastConnect 配置本地与云环境之间安全、高性能的连接。

## 目的

在本地数据中心与云提供商（AWS、Azure、GCP、OCI）之间建立安全、可靠的网络连接。

## 何时使用

- 将本地连接到云
- 将数据中心扩展到云
- 实现混合双活设置
- 满足合规要求
- 逐步迁移到云

## 连接选项

### AWS 连接

#### 1. 站点到站点 VPN

- 基于互联网的 IPSec VPN
- 每隧道最高 1.25 Gbps
- 对中等带宽具有成本效益
- 延迟较高，依赖互联网

```hcl
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-vpn-gateway"
  }
}

resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "203.0.113.1"
  type       = "ipsec.1"
}

resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = false
}
```

#### 2. AWS Direct Connect

- 专用网络连接
- 1 Gbps 到 100 Gbps
- 延迟更低，带宽稳定
- 成本更高，需要设置时间

**参考：** 见 `references/direct-connect.md`

### Azure 连接

#### 1. 站点到站点 VPN

```hcl
resource "azurerm_virtual_network_gateway" "vpn" {
  name                = "vpn-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type     = "Vpn"
  vpn_type = "RouteBased"
  sku      = "VpnGw1"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
}
```

#### 2. Azure ExpressRoute

- 通过连接提供商的私有连接
- 最高 100 Gbps
- 低延迟，高可靠性
- 全球连接需高级版

### GCP 连接

#### 1. Cloud VPN

- IPSec VPN（经典版或高可用 VPN）
- 高可用 VPN：99.99% SLA
- 每隧道最高 3 Gbps

#### 2. Cloud Interconnect

- 专用（10 Gbps、100 Gbps）
- 合作伙伴（50 Mbps 到 50 Gbps）
- 比 VPN 延迟更低

### OCI 连接

#### 1. IPSec VPN Connect

- 带冗余隧道的 IPSec VPN
- 通过 DRG 的动态路由
- 适合分支机构和迁移阶段

#### 2. OCI FastConnect

- 通过 Oracle 或合作伙伴边缘的私有专用连接
- 适合可预测吞吐量和低延迟混合流量
- 通常与 DRG 配合用于中心辐射设计

## 混合网络模式

### 模式 1：中心辐射

```
本地数据中心
         ↓
    VPN/Direct Connect
         ↓
    Transit Gateway (AWS) / vWAN (Azure)
         ↓
    ├─ 生产 VPC/VNet
    ├─ 预发布 VPC/VNet
    └─ 开发 VPC/VNet
```

### 模式 2：多区域混合

```
本地
    ├─ Direct Connect → us-east-1
    └─ Direct Connect → us-west-2
            ↓
        跨区域对等连接
```

### 模式 3：多云混合

```
本地数据中心
    ├─ Direct Connect → AWS
    ├─ ExpressRoute → Azure
    ├─ Interconnect → GCP
    └─ FastConnect → OCI
```

## 路由配置

### BGP 配置

```
本地路由器：
- AS 编号：65000
- 通告：10.0.0.0/8

云路由器：
- AS 编号：64512 (AWS)、65515 (Azure)、GCP/OCI 由提供商分配
- 通告：云 VPC/VNet CIDR
```

### 路由传播

- 在路由表上启用路由传播
- 使用 BGP 实现动态路由
- 实现路由过滤
- 监控路由通告

## 安全最佳实践

1. **使用私有连接**（Direct Connect/ExpressRoute/Interconnect/FastConnect）
2. **为 VPN 隧道实现加密**
3. **使用 VPC 端点** 避免互联网路由
4. **配置网络 ACL** 和安全组
5. **启用 VPC 流日志** 进行监控
6. **实现 DDoS 防护**
7. **使用 PrivateLink/私有端点**
8. **使用 CloudWatch/Azure Monitor/Cloud Monitoring/OCI Monitoring 监控连接**
9. **实现冗余**（双隧道）
10. **定期安全审计**

## 高可用性

### 双 VPN 隧道

```hcl
resource "aws_vpn_connection" "primary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.primary.id
  type                = "ipsec.1"
}

resource "aws_vpn_connection" "secondary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.secondary.id
  type                = "ipsec.1"
}
```

### 双活配置

- 来自不同位置的多个连接
- BGP 实现自动故障转移
- 等价多路径（ECMP）路由
- 监控所有连接的健康状态

## 监控和故障排除

### 关键指标

- 隧道状态（up/down）
- 字节入/出
- 丢包率
- 延迟
- BGP 会话状态

### 故障排除

```bash
# AWS VPN
aws ec2 describe-vpn-connections
aws ec2 get-vpn-connection-telemetry

# Azure VPN
az network vpn-connection show
az network vpn-connection show-device-config-script

# OCI IPSec VPN
oci network ip-sec-connection list
oci network cpe list
```

## 成本优化

1. **根据流量合理选择连接**
2. **对低带宽工作负载使用 VPN**
3. **通过更少的连接整合流量**
4. **最小化数据传输成本**
5. **对高带宽使用专用私有链路**
6. **实现缓存以减少流量**


## 相关技能

- `multi-cloud-architecture` - 用于架构决策
- `terraform-module-library` - 用于 IaC 实现
