---
name: parallel-feature-development
description: 通过文件所有权策略、冲突避免规则和多代理实现的集成模式来协调并行功能开发。在将大型功能分解为独立工作流、两个或更多代理需要同时实现同一系统的不同层、建立文件所有权以防止共享代码库中的合并冲突、设计接口契约以便并行实现者可以在 API 准备好之前针对其构建、或决定是使用垂直切片还是水平层来实现全栈功能时使用此技能。
version: 1.0.2
---

# 并行功能开发

将功能分解为并行工作流、建立文件所有权边界、避免冲突以及集成多个实现者代理结果的策略。

## 何时使用此技能

- 分解功能以进行并行实现
- 在代理之间建立文件所有权边界
- 设计并行工作流之间的接口契约
- 选择集成策略（垂直切片 vs 水平层）
- 管理并行开发的分支和合并工作流

## 文件所有权策略

### 按目录

分配每个实现者对特定目录的所有权：

```
implementer-1: src/components/auth/
implementer-2: src/api/auth/
implementer-3: tests/auth/
```

**最适合**：具有清晰目录边界的组织良好的代码库。

### 按模块

分配逻辑模块的所有权（可能跨越目录）：

```
implementer-1: Authentication module (login, register, logout)
implementer-2: Authorization module (roles, permissions, guards)
```

**最适合**：面向功能的架构、领域驱动设计。

### 按层

分配架构层的所有权：

```
implementer-1: UI layer (components, styles, layouts)
implementer-2: Business logic layer (services, validators)
implementer-3: Data layer (models, repositories, migrations)
```

**最适合**：传统的 MVC/分层架构。

## 冲突避免规则

### 基本规则

**每个文件一个所有者。** 不应将任何文件分配给多个实现者。

### 当文件必须共享时

如果文件确实需要多个实现者的更改：

1. **指定单一所有者** — 一个实现者拥有该文件
2. **其他实现者请求更改** — 向所有者发送具体的更改请求
3. **所有者顺序应用更改** — 防止合并冲突
4. **替代方案：提取接口** — 创建单独的接口文件，非所有者可以导入而无需修改

### 接口契约

当实现者需要在边界处协调时：

```typescript
// src/types/auth-contract.ts (owned by team-lead, read-only for implementers)
export interface AuthResponse {
  token: string;
  user: UserProfile;
  expiresAt: number;
}

export interface AuthService {
  login(email: string, password: string): Promise<AuthResponse>;
  register(data: RegisterData): Promise<AuthResponse>;
}
```

两个实现者都从契约文件导入，但都不修改它。

## 集成模式

### 垂直切片

每个实现者构建一个完整的功能切片（UI + API + 测试）：

```
implementer-1: Login feature (login form + login API + login tests)
implementer-2: Register feature (register form + register API + register tests)
```

**优点**：每个切片可独立测试，需要最少的集成。
**缺点**：可能重复共享工具，对于紧耦合功能更困难。

### 水平层

每个实现者构建跨所有功能的一层：

```
implementer-1: All UI components (login form, register form, profile page)
implementer-2: All API endpoints (login, register, profile)
implementer-3: All tests (unit, integration, e2e)
```

**优点**：每层内模式一致，自然专业化。
**缺点**：更多集成点，第 3 层依赖第 1 和第 2 层。

### 混合

根据耦合度混合垂直和水平：

```
implementer-1: Login feature (vertical slice — UI + API + tests)
implementer-2: Shared auth infrastructure (horizontal — middleware, JWT utils, types)
```

**最适合**：大多数具有共享基础设施的真实世界功能。

## 分支管理

### 单分支策略

所有实现者在同一功能分支上工作：

- 设置简单，无合并开销
- 需要严格的文件所有权以避免冲突
- 最适合：小团队（2-3人），明确定义的边界

### 多分支策略

每个实现者在子分支上工作：

```
feature/auth
  ├── feature/auth-login      (implementer-1)
  ├── feature/auth-register    (implementer-2)
  └── feature/auth-tests       (implementer-3)
```

- 更多隔离，明确的合并点
- 更高开销，共享文件中仍可能出现合并冲突
- 最适合：较大团队（4+人），复杂功能

## 故障排除

**实现者互相阻塞等待共享代码。**
将共享部分提取到自己的接口契约文件中，由团队负责人拥有，实现者从中导入。两个实现者都不修改契约 — 他们只针对其实现。

**即使有明确的所有权规则也出现合并冲突。**
文件被分配给两个代理，或自动导入所有内容的配置/索引文件（如 `index.ts`、`__init__.py`）被双方修改。为所有 barrel/index 文件指定一个所有者，或让负责人最后合并它们。

**实现者提前完成但集成步骤被阻塞。**
使用暂存接口：完成的实现者编写下游依赖的桩或模拟，以便其他实现者可以继续工作。在集成时替换为真实实现。

**功能分解在中途被证明是错误的。**
停止新工作，让负责人重新分配文件，并通过广播传达更改。部分编写代码的沉没成本是可以接受的 — 继续错误的拆分更糟。

**一个实现者编写的测试针对另一个实现者编写的代码失败。**
接口契约发生了漂移：拥有 API 的实现者在未通知测试实现者的情况下更改了签名。强制执行规则：契约文件在修改前需要广播。

## 相关技能

- [team-composition-patterns](../team-composition-patterns/SKILL.md) — 在分解工作之前选择正确的团队规模和代理类型
- [team-communication-protocols](../team-communication-protocols/SKILL.md) — 协调实现者之间的集成交接和计划审批
