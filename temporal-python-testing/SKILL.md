---
name: temporal-python-testing
description: 使用 pytest、时间跳过和模拟策略测试 Temporal 工作流。涵盖单元测试、集成测试、重放测试和本地开发环境搭建。适用于实现 Temporal 工作流测试或调试测试失败时使用。
---

# Temporal Python 测试策略

使用 pytest 对 Temporal 工作流进行全面测试的方法，针对特定测试场景提供渐进式资源指引。

## 何时使用此技能

- **单元测试工作流** - 使用时间跳过的快速测试
- **集成测试** - 带模拟活动的工作流测试
- **重放测试** - 针对生产历史记录验证确定性
- **本地开发** - 搭建 Temporal 服务器和 pytest 环境
- **CI/CD 集成** - 自动化测试流水线
- **覆盖策略** - 实现 ≥80% 的测试覆盖率

## 测试理念

**推荐方法**（来源：docs.temporal.io/develop/python/testing-suite）：

- 以集成测试为主编写测试
- 使用 pytest 配合异步 fixtures
- 时间跳过可实现快速反馈（数月长的工作流 → 秒级完成）
- 模拟活动以隔离工作流逻辑
- 通过重放测试验证确定性

**三种测试类型**：

1. **单元测试**：使用时间跳过的工作流测试，使用 ActivityEnvironment 的活动测试
2. **集成测试**：带模拟活动的 Worker 测试
3. **端到端测试**：完整 Temporal 服务器配合真实活动（谨慎使用）

## 可用资源

本技能通过渐进式指引提供详细指导。根据测试需求加载特定资源：

### 单元测试资源

**文件**：`resources/unit-testing.md`
**何时加载**：单独测试单个工作流或活动时
**包含**：

- 使用时间跳过的 WorkflowEnvironment
- 用于活动测试的 ActivityEnvironment
- 长时间运行工作流的快速执行
- 手动时间推进模式
- pytest fixtures 和模式

### 集成测试资源

**文件**：`resources/integration-testing.md`
**何时加载**：测试带有模拟外部依赖的工作流时
**包含**：

- 活动模拟策略
- 错误注入模式
- 多活动工作流测试
- 信号和查询测试
- 覆盖策略

### 重放测试资源

**文件**：`resources/replay-testing.md`
**何时加载**：验证确定性或部署工作流变更时
**包含**：

- 确定性验证
- 生产历史记录重放
- CI/CD 集成模式
- 版本兼容性测试

### 本地开发资源

**文件**：`resources/local-setup.md`
**何时加载**：搭建开发环境时
**包含**：

- Docker Compose 配置
- pytest 设置与配置
- 覆盖率工具集成
- 开发工作流

## 快速入门指南

### 基本工作流测试

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

@pytest.fixture
async def workflow_env():
    env = await WorkflowEnvironment.start_time_skipping()
    yield env
    await env.shutdown()

@pytest.mark.asyncio
async def test_workflow(workflow_env):
    async with Worker(
        workflow_env.client,
        task_queue="test-queue",
        workflows=[YourWorkflow],
        activities=[your_activity],
    ):
        result = await workflow_env.client.execute_workflow(
            YourWorkflow.run,
            args,
            id="test-wf-id",
            task_queue="test-queue",
        )
        assert result == expected
```

### 基本活动测试

```python
from temporalio.testing import ActivityEnvironment

async def test_activity():
    env = ActivityEnvironment()
    result = await env.run(your_activity, "test-input")
    assert result == expected_output
```

## 覆盖目标

**推荐覆盖标准**（来源：docs.temporal.io 最佳实践）：

- **工作流**：≥80% 逻辑覆盖
- **活动**：≥80% 逻辑覆盖
- **集成测试**：关键路径配合模拟活动
- **重放测试**：部署前验证所有工作流版本

## 关键测试原则

1. **时间跳过** - 数月长的工作流秒级完成测试
2. **模拟活动** - 将工作流逻辑与外部依赖隔离
3. **重放测试** - 部署前验证确定性
4. **高覆盖率** - 生产工作流目标 ≥80%
5. **快速反馈** - 单元测试毫秒级运行

## 如何使用资源

**按需加载特定资源**：

- "展示单元测试模式" → 加载 `resources/unit-testing.md`
- "如何模拟活动？" → 加载 `resources/integration-testing.md`
- "搭建本地 Temporal 服务器" → 加载 `resources/local-setup.md`
- "验证确定性" → 加载 `resources/replay-testing.md`

## 补充参考

- Python SDK 测试：docs.temporal.io/develop/python/testing-suite
- 测试模式：github.com/temporalio/temporal/blob/main/docs/development/testing.md
- Python 示例：github.com/temporalio/samples-python
