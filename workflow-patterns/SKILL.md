---
name: workflow-patterns
description: 当按照 Conductor 的 TDD 工作流实现任务、处理阶段检查点、管理任务的 git 提交或理解验证协议时使用此技能。
version: 1.0.0
---

# 工作流模式

使用 Conductor 的 TDD 工作流实现任务、管理阶段检查点、处理 git 提交和执行验证协议的指南，确保实现过程中的质量。

## 何时使用此技能

- 从 track 的 plan.md 实现任务
- 遵循 TDD 红-绿-重构循环
- 完成阶段检查点
- 管理 git 提交和笔记
- 理解质量保证门
- 处理验证协议
- 在计划文件中记录进度

## TDD 任务生命周期

每个任务遵循以下 11 个步骤：

### 步骤 1：选择下一个任务

读取 plan.md 并识别下一个待处理的 `[ ]` 任务。在当前阶段内按顺序选择任务。不要跳到后面的阶段。

### 步骤 2：标记为进行中

更新 plan.md 将任务标记为 `[~]`：

```markdown
- [~] **Task 2.1**: Implement user validation
```

将此状态更改与实现分开提交。

### 步骤 3：红 - 编写失败的测试

在编写实现之前编写定义预期行为的测试：

- 需要时创建测试文件
- 编写覆盖正常路径的测试用例
- 编写覆盖边界情况的测试用例
- 编写覆盖错误条件的测试用例
- 运行测试——它们应该失败

示例：

```python
def test_validate_user_email_valid():
    user = User(email="test@example.com")
    assert user.validate_email() is True

def test_validate_user_email_invalid():
    user = User(email="invalid")
    assert user.validate_email() is False
```

### 步骤 4：绿 - 实现最小代码

编写使测试通过所需的最小代码：

- 专注于使测试变绿，而非完美
- 避免过早优化
- 保持实现简单
- 运行测试——它们应该通过

### 步骤 5：重构 - 改善清晰度

测试变绿后，改进代码：

- 提取常见模式
- 改进命名
- 消除重复
- 简化逻辑
- 每次更改后运行测试——它们应该保持绿色

### 步骤 6：验证覆盖率

检查测试覆盖率是否达到 80% 目标：

```bash
pytest --cov=module --cov-report=term-missing
```

如果覆盖率低于 80%：

- 识别未覆盖的行
- 为缺失路径添加测试
- 重新运行覆盖率检查

### 步骤 7：记录偏差

如果实现偏离计划或引入了新依赖：

- 用新依赖更新 tech-stack.md
- 在 plan.md 任务注释中标记偏差
- 如果需求变更则更新 spec.md

### 步骤 8：提交实现

为任务创建聚焦的提交：

```bash
git add -A
git commit -m "feat(user): implement email validation

- Add validate_email method to User class
- Handle empty and malformed emails
- Add comprehensive test coverage

Task: 2.1
Track: user-auth_20250115"
```

提交消息格式：

- 类型：feat、fix、refactor、test、docs、chore
- 范围：受影响的模块或组件
- 摘要：祈使句、现在时
- 正文：更改的要点
- 脚注：任务和 track 引用

### 步骤 9：附加 Git Notes

添加丰富的任务摘要作为 git note：

```bash
git notes add -m "Task 2.1: Implement user validation

Summary:
- Added email validation using regex pattern
- Handles edge cases: empty, no @, no domain
- Coverage: 94% on validation module

Files changed:
- src/models/user.py (modified)
- tests/test_user.py (modified)

Decisions:
- Used simple regex over email-validator library
- Reason: No external dependency for basic validation"
```

### 步骤 10：用 SHA 更新计划

更新 plan.md 用提交 SHA 标记任务完成：

```markdown
- [x] **Task 2.1**: Implement user validation `abc1234`
```

### 步骤 11：提交计划更新

提交计划状态更新：

```bash
git add conductor/tracks/*/plan.md
git commit -m "docs: update plan - task 2.1 complete

Track: user-auth_20250115"
```

## 阶段完成协议

当阶段中的所有任务完成时，执行验证协议：

### 识别更改的文件

列出自上次检查点以来修改的所有文件：

```bash
git diff --name-only <last-checkpoint-sha>..HEAD
```

### 确保测试覆盖率

对于每个修改的文件：

1. 识别对应的测试文件
2. 验证新/更改的代码存在测试
3. 运行修改模块的覆盖率
4. 如果覆盖率 < 80% 则添加测试

### 运行完整测试套件

执行完整的测试套件：

```bash
pytest -v --tb=short
```

所有测试必须通过才能继续。

### 生成手动验证步骤

创建手动验证清单：

```markdown
## Phase 1 Verification Checklist

- [ ] User can register with valid email
- [ ] Invalid email shows appropriate error
- [ ] Database stores user correctly
- [ ] API returns expected response codes
```

### 等待用户批准

向用户展示验证清单：

```
Phase 1 complete. Please verify:
1. [ ] Test suite passes (automated)
2. [ ] Coverage meets target (automated)
3. [ ] Manual verification items (requires human)

Respond with 'approved' to continue, or note issues.
```

没有明确批准不要继续。

### 创建检查点提交

批准后，创建检查点提交：

```bash
git add -A
git commit -m "checkpoint: phase 1 complete - user-auth_20250115

Verified:
- All tests passing
- Coverage: 87%
- Manual verification approved

Phase 1 tasks:
- [x] Task 1.1: Setup database schema
- [x] Task 1.2: Implement user model
- [x] Task 1.3: Add validation logic"
```

### 记录检查点 SHA

更新 plan.md 检查点表：

```markdown
## Checkpoints

| Phase   | Checkpoint SHA | Date       | Status   |
| ------- | -------------- | ---------- | -------- |
| Phase 1 | def5678        | 2025-01-15 | verified |
| Phase 2 |                |            | pending  |
```

## 质量保证门

在标记任何任务完成之前，验证这些门：

### 测试通过

- 所有现有测试通过
- 新测试通过
- 无测试回归

### 覆盖率 >= 80%

- 新代码有 80%+ 覆盖率
- 整体项目覆盖率维持
- 关键路径完全覆盖

### 风格合规

- 代码遵循风格指南
- Lint 通过
- 格式正确

### 文档

- 公共 API 已文档化
- 复杂逻辑已解释
- 需要时更新 README

### 类型安全

- 存在类型提示（如适用）
- 类型检查器通过
- 无无理由的 type: ignore

### 无 Lint 错误

- 零 linter 错误
- 警告已处理或合理化
- 静态分析干净

### 移动兼容性

如适用：

- 响应式设计已验证
- 触控交互正常
- 性能可接受

### 安全审计

- 代码中无密钥
- 存在输入验证
- 认证/授权正确
- 依赖无漏洞

## Git 集成

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：

- `feat`：新功能
- `fix`：Bug 修复
- `refactor`：无功能/修复的代码更改
- `test`：添加测试
- `docs`：文档
- `chore`：维护

### Git Notes 用于丰富摘要

向提交附加详细笔记：

```bash
git notes add -m "<detailed summary>"
```

查看笔记：

```bash
git log --show-notes
```

好处：

- 保留上下文而不使提交消息混乱
- 启用跨提交的语义查询
- 支持基于 track 的操作

### 在 plan.md 中记录 SHA

完成任务时始终记录提交 SHA：

```markdown
- [x] **Task 1.1**: Setup schema `abc1234`
- [x] **Task 1.2**: Add model `def5678`
```

这使得：

- 从计划到代码的可追溯性
- 语义回滚操作
- 进度审计

## 验证检查点

### 为什么检查点重要

检查点为语义回滚创建恢复点：

- 回滚到任何阶段结束
- 维护逻辑代码状态
- 启用安全实验

### 何时创建检查点

在以下情况后创建检查点：

- 所有阶段任务完成
- 所有阶段验证通过
- 收到用户批准

### 检查点提交内容

检查点提交中包含：

- 所有未提交的更改
- 更新的 plan.md
- 更新的 metadata.json
- 任何文档更新

### 如何使用检查点

用于回滚：

```bash
# 回滚到阶段 1 结束
git revert --no-commit <phase-2-commits>...
git commit -m "revert: rollback to phase 1 checkpoint"
```

用于审查：

```bash
# 查看阶段 2 的更改
git diff <phase-1-sha>..<phase-2-sha>
```

## 处理偏差

在实现过程中，可能会出现偏离计划的情况。系统地处理它们：

### 偏差类型

**范围增加**
发现原始规范中没有的需求。

- 在 spec.md 中记录为新需求
- 在 plan.md 中添加任务
- 在任务注释中标记增加

**范围缩减**
实现过程中认为不必要的功能。

- 将任务标记为 `[-]`（跳过）并说明原因
- 更新 spec.md 范围部分
- 记录决策理由

**技术偏差**
与计划不同的实现方法。

- 在任务完成注释中标记偏差
- 如果依赖变更则更新 tech-stack.md
- 记录为什么原方法不合适

**需求变更**
工作过程中对需求的理解变化。

- 用更正的需求更新 spec.md
- 需要时调整 plan.md 任务
- 重新验证验收标准

### 偏差文档格式

完成有偏差的任务时：

```markdown
- [x] **Task 2.1**: Implement validation `abc1234`
  - DEVIATION: Used library instead of custom code
  - Reason: Better edge case handling
  - Impact: Added email-validator to dependencies
```

## 错误恢复

### 绿之后测试失败

如果达到绿之后测试失败：

1. 不要继续到重构
2. 识别哪个测试开始失败
3. 检查重构是否破坏了什么
4. 回到最后已知的绿状态
5. 重新尝试实现

### 检查点被拒绝

如果用户拒绝检查点：

1. 在 plan.md 中记录拒绝原因
2. 创建任务解决问题
3. 完成修复任务
4. 再次请求检查点批准

### 被依赖阻塞

如果任务无法继续：

1. 将任务标记为 `[!]` 并描述阻塞因素
2. 检查其他任务是否可以继续
3. 记录预期解决时间线
4. 考虑创建依赖解决 track

## 按任务类型的 TDD 变体

### 数据模型任务

```
红：编写模型创建和验证的测试
绿：实现带字段的模型类
重构：添加计算属性，改进类型
```

### API 端点任务

```
红：编写请求/响应契约的测试
绿：实现端点处理器
重构：提取验证，改进错误处理
```

### 集成任务

```
红：编写组件交互的测试
绿：将组件连接在一起
重构：改进错误传播，添加日志
```

### 重构任务

```
红：为当前行为添加表征测试
绿：应用重构（测试应保持绿色）
重构：清理引入的复杂性
```

## 使用现有测试

修改有现有测试的代码时：

### 扩展而非替换

- 保持现有测试通过
- 为新行为添加新测试
- 仅在需求变更时更新测试

### 测试迁移

当重构改变测试结构时：

1. 运行现有测试（应通过）
2. 为重构的代码添加新测试
3. 将测试用例迁移到新结构
4. 仅在新测试通过后删除旧测试

### 回归预防

任何更改后：

1. 运行完整测试套件
2. 检查意外失败
3. 调查任何新失败
4. 继续前修复回归

## 检查点验证详情

### 自动验证

请求批准前运行：

```bash
# 测试套件
pytest -v --tb=short

# 覆盖率
pytest --cov=src --cov-report=term-missing

# Lint
ruff check src/ tests/

# 类型检查（如适用）
mypy src/
```

### 手动验证指导

对于手动项目，提供具体说明：

```markdown
## Manual Verification Steps

### User Registration

1. Navigate to /register
2. Enter valid email: test@example.com
3. Enter password meeting requirements
4. Click Submit
5. Verify success message appears
6. Verify user appears in database

### Error Handling

1. Enter invalid email: "notanemail"
2. Verify error message shows
3. Verify form retains other entered data
```

## 性能考虑

### 测试套件性能

保持测试套件快速：

- 使用 fixture 避免冗余设置
- 模拟慢的外部调用
- 开发期间运行子集，检查点时运行完整套件

### 提交性能

保持提交原子性：

- 每个提交一个逻辑更改
- 完整的思想，而非进行中的工作
- 每次提交后测试应通过

## 最佳实践

1. **永远不要跳过红**：始终先编写失败的测试
2. **小提交**：每个提交一个逻辑更改
3. **即时更新**：任务完成后立即更新 plan.md
4. **等待批准**：永远不要跳过检查点验证
5. **丰富的 git notes**：包含有助于未来理解的上下文
6. **覆盖率纪律**：不接受低于目标的覆盖率
7. **质量门**：标记完成前检查所有门
8. **顺序阶段**：按顺序完成阶段
9. **记录偏差**：标记与原计划的任何偏差
10. **干净状态**：每次提交应使代码处于工作状态
11. **快速反馈**：开发期间频繁运行相关测试
12. **清晰阻塞**：及时处理阻塞，不要绕过它们
