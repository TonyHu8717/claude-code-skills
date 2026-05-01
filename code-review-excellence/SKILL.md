---
name: code-review-excellence
description: 掌握有效的代码审查实践，提供建设性反馈、尽早发现 bug 并促进知识共享，同时保持团队士气。在审查拉取请求、建立审查标准或指导开发者时使用。
---

# 代码审查卓越

通过建设性反馈、系统分析和协作改进，将代码审查从把关转变为知识共享。

## 使用场景

- 审查拉取请求和代码变更
- 为团队建立代码审查标准
- 通过审查指导初级开发者
- 进行架构审查
- 创建审查清单和指南
- 改善团队协作
- 减少代码审查周期时间
- 维护代码质量标准

## 核心原则

### 1. 审查心态

**代码审查的目标：**

- 发现 bug 和边界情况
- 确保代码可维护性
- 在团队间分享知识
- 执行编码标准
- 改进设计和架构
- 建立团队文化

**不是目标：**

- 炫耀知识
- 吹毛求疵格式化（使用 linter）
- 不必要地阻碍进展
- 按你的偏好重写

### 2. 有效的反馈

**好的反馈是：**

- 具体且可操作
- 教育性的，而非评判性的
- 关注代码，而非个人
- 平衡的（也要表扬好的工作）
- 有优先级的（关键的 vs 锦上添花的）

```markdown
❌ 不好："这是错的。"
✅ 好："当多个用户同时访问时，这可能导致竞态条件。
考虑在这里使用互斥锁。"

❌ 不好："为什么不用 X 模式？"
✅ 好："你考虑过仓储模式吗？它会使测试更容易。
这里有一个示例：[链接]"

❌ 不好："重命名这个变量。"
✅ 好："[nit] 考虑用 `userCount` 代替 `uc` 以提高清晰度。
如果你想保留它，不会阻碍合并。"
```

### 3. 审查范围

**要审查什么：**

- 逻辑正确性和边界情况
- 安全漏洞
- 性能影响
- 测试覆盖率和质量
- 错误处理
- 文档和注释
- API 设计和命名
- 架构适配

**不要手动审查什么：**

- 代码格式化（使用 Prettier、Black 等）
- 导入组织
- Lint 违规
- 简单的拼写错误

## 审查流程

### 阶段 1：上下文收集（2-3 分钟）

```markdown
在深入代码之前，了解：

1. 阅读 PR 描述和关联的 issue
2. 检查 PR 大小（>400 行？要求拆分）
3. 审查 CI/CD 状态（测试通过？）
4. 理解业务需求
5. 注意任何相关的架构决策
```

### 阶段 2：高层审查（5-10 分钟）

```markdown
1. **架构和设计**
   - 解决方案是否适合问题？
   - 是否有更简单的方法？
   - 是否与现有模式一致？
   - 能否扩展？

2. **文件组织**
   - 新文件是否在正确的位置？
   - 代码是否按逻辑分组？
   - 是否有重复文件？

3. **测试策略**
   - 是否有测试？
   - 测试是否覆盖边界情况？
   - 测试是否可读？
```

### 阶段 3：逐行审查（10-20 分钟）

```markdown
对于每个文件：

1. **逻辑和正确性**
   - 边界情况处理了吗？
   - 有一错误吗？
   - 空值/未定义检查？
   - 竞态条件？

2. **安全**
   - 输入验证？
   - SQL 注入风险？
   - XSS 漏洞？
   - 敏感数据暴露？

3. **性能**
   - N+1 查询？
   - 不必要的循环？
   - 内存泄漏？
   - 阻塞操作？

4. **可维护性**
   - 变量名清晰？
   - 函数只做一件事？
   - 复杂代码有注释？
   - 魔法数字被提取？
```

### 阶段 4：总结和决策（2-3 分钟）

```markdown
1. 总结关键问题
2. 强调你喜欢的部分
3. 做出明确决策：
   - ✅ 批准
   - 💬 评论（小建议）
   - 🔄 请求更改（必须处理）
4. 如果复杂，提供结对帮助
```

## 审查技巧

### 技巧 1：清单方法

```markdown
## 安全清单

- [ ] 用户输入已验证和清理
- [ ] SQL 查询使用参数化
- [ ] 认证/授权已检查
- [ ] 密钥未硬编码
- [ ] 错误消息不泄露信息

## 性能清单

- [ ] 没有 N+1 查询
- [ ] 数据库查询已索引
- [ ] 大列表已分页
- [ ] 昂贵操作已缓存
- [ ] 热路径中没有阻塞 I/O

## 测试清单

- [ ] 正常路径已测试
- [ ] 边界情况已覆盖
- [ ] 错误情况已测试
- [ ] 测试名称具有描述性
- [ ] 测试是确定性的
```

### 技巧 2：提问方法

不要陈述问题，而是通过提问来鼓励思考：

```markdown
❌ "如果列表为空，这会失败。"
✅ "如果 `items` 是空数组会发生什么？"

❌ "你需要在这里添加错误处理。"
✅ "如果 API 调用失败，这里应该怎么表现？"

❌ "这效率低下。"
✅ "我看到这会遍历所有用户。我们考虑过
10 万用户的性能影响吗？"
```

### 技巧 3：建议，不要命令

````markdown
## 使用协作语言

❌ "你必须把这个改成 async/await"
✅ "建议：async/await 可能会让这更可读：
`typescript
    async function fetchUser(id: string) {
        const user = await db.query('SELECT * FROM users WHERE id = ?', id);
        return user;
    }
    `
你怎么看？"

❌ "把这个提取成一个函数"
✅ "这个逻辑出现在 3 个地方。把它提取到
一个共享的工具函数中有意义吗？"
````

### 技巧 4：区分严重程度

```markdown
使用标签指示优先级：

🔴 [blocking] - 合并前必须修复
🟡 [important] - 应该修复，不同意则讨论
🟢 [nit] - 锦上添花，不阻碍
💡 [suggestion] - 考虑的替代方法
📚 [learning] - 教育性评论，无需行动
🎉 [praise] - 做得好，继续保持！

示例：
"🔴 [blocking] 这个 SQL 查询容易被注入。
请使用参数化查询。"

"🟢 [nit] 考虑将 `data` 重命名为 `userData` 以提高清晰度。"

"🎉 [praise] 优秀的测试覆盖率！这会捕捉边界情况。"
```

## 语言特定模式

### Python 代码审查

```python
# 检查 Python 特定问题

# ❌ 可变默认参数
def add_item(item, items=[]):  # Bug！跨调用共享
    items.append(item)
    return items

# ✅ 使用 None 作为默认值
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# ❌ 捕获范围太广
try:
    result = risky_operation()
except:  # 捕获一切，甚至 KeyboardInterrupt！
    pass

# ✅ 捕获特定异常
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise

# ❌ 使用可变类属性
class User:
    permissions = []  # 所有实例共享！

# ✅ 在 __init__ 中初始化
class User:
    def __init__(self):
        self.permissions = []
```

### TypeScript/JavaScript 代码审查

```typescript
// 检查 TypeScript 特定问题

// ❌ 使用 any 破坏类型安全
function processData(data: any) {  // 避免 any
    return data.value;
}

// ✅ 使用正确的类型
interface DataPayload {
    value: string;
}
function processData(data: DataPayload) {
    return data.value;
}

// ❌ 不处理异步错误
async function fetchUser(id: string) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();  // 如果网络失败怎么办？
}

// ✅ 正确处理错误
async function fetchUser(id: string): Promise<User> {
    try {
        const response = await fetch(`/api/users/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
}

// ❌ 修改 props
function UserProfile({ user }: Props) {
    user.lastViewed = new Date();  // 修改 prop！
    return <div>{user.name}</div>;
}

// ✅ 不要修改 props
function UserProfile({ user, onView }: Props) {
    useEffect(() => {
        onView(user.id);  // 通知父组件更新
    }, [user.id]);
    return <div>{user.name}</div>;
}
```

## 高级审查模式

### 模式 1：架构审查

```markdown
当审查重大变更时：

1. **先有设计文档**
   - 对于大型功能，在代码之前请求设计文档
   - 在实现之前与团队审查设计
   - 同意方法以避免返工

2. **分阶段审查**
   - 第一个 PR：核心抽象和接口
   - 第二个 PR：实现
   - 第三个 PR：集成和测试
   - 更容易审查，更快迭代

3. **考虑替代方案**
   - "我们考虑过使用 [模式/库] 吗？"
   - "与更简单的方法相比，权衡是什么？"
   - "随着需求变化，这将如何演进？"
```

### 模式 2：测试质量审查

```typescript
// ❌ 差测试：测试实现细节
test('increments counter variable', () => {
    const component = render(<Counter />);
    const button = component.getByRole('button');
    fireEvent.click(button);
    expect(component.state.counter).toBe(1);  // 测试内部状态
});

// ✅ 好测试：测试行为
test('displays incremented count when clicked', () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });
    fireEvent.click(button);
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
});

// 测试的审查问题：
// - 测试描述的是行为，不是实现吗？
// - 测试名称清晰且有描述性吗？
// - 测试覆盖边界情况吗？
// - 测试是独立的（没有共享状态）吗？
// - 测试可以按任何顺序运行吗？
```

### 模式 3：安全审查

```markdown
## 安全审查清单

### 认证和授权

- [ ] 需要的地方是否有认证？
- [ ] 每个操作前是否有授权检查？
- [ ] JWT 验证是否正确（签名、过期）？
- [ ] API 密钥/密钥是否安全存储？

### 输入验证

- [ ] 所有用户输入已验证？
- [ ] 文件上传是否受限（大小、类型）？
- [ ] SQL 查询是否参数化？
- [ ] XSS 防护（转义输出）？

### 数据保护

- [ ] 密码是否哈希（bcrypt/argon2）？
- [ ] 敏感数据是否加密存储？
- [ ] 敏感数据是否强制 HTTPS？
- [ ] PII 是否按法规处理？

### 常见漏洞

- [ ] 没有 eval() 或类似动态执行？
- [ ] 没有硬编码密钥？
- [ ] 状态变更操作是否有 CSRF 保护？
- [ ] 公开端点是否有限速？
```

## 给予困难反馈

### 模式：三明治方法（改进版）

```markdown
传统：表扬 + 批评 + 表扬（感觉虚假）

更好：上下文 + 具体问题 + 有帮助的解决方案

示例：
"我注意到支付处理逻辑在控制器中是内联的。
这使得测试和重用更加困难。

[具体问题]
calculateTotal() 函数混合了税收计算、
折扣逻辑和数据库查询，使其难以
单元测试和理解。

[有帮助的解决方案]
我们能把这个提取到 PaymentService 类中吗？那样
会使它可测试和可重用。如果有帮助，我可以和你
结对做这个。"
```

### 处理分歧

```markdown
当作者不同意你的反馈时：

1. **寻求理解**
   "帮我理解你的方法。是什么让你
   选择这个模式？"

2. **承认有效观点**
   "关于 X 的观点很好。我没有考虑到那个。"

3. **提供数据**
   "我担心性能。我们能添加一个基准
   来验证这个方法吗？"

4. **必要时升级**
   "让我们找 [架构师/高级开发者] 来参与这个。"

5. **知道何时放手**
   如果它能工作且不是关键问题，就批准它。
   完美是进步的敌人。
```

## 最佳实践

1. **及时审查**：24 小时内，最好同一天
2. **限制 PR 大小**：有效审查最多 200-400 行
3. **分时间段审查**：最多 60 分钟，休息一下
4. **使用审查工具**：GitHub、GitLab 或专用工具
5. **自动化能自动化的**：Linter、格式化器、安全扫描
6. **建立关系**：表情符号、表扬和同理心很重要
7. **保持可用**：提供结对帮助处理复杂问题
8. **向他人学习**：审查他人的审查评论

## 常见陷阱

- **完美主义**：因为小的风格偏好而阻碍 PR
- **范围蔓延**："既然你在做了，你能也..."
- **不一致**：对不同人使用不同标准
- **延迟审查**：让 PR 搁置数天
- **消失**：请求更改后消失
- **橡皮图章**：没有实际审查就批准
- **自行车棚**：对琐碎细节进行大量辩论

## 模板

### PR 审查评论模板

```markdown
## 总结

[审查内容的简要概述]

## 优势

- [做得好的部分]
- [好的模式或方法]

## 必须更改

🔴 [阻碍问题 1]
🔴 [阻碍问题 2]

## 建议

💡 [改进 1]
💡 [改进 2]

## 问题

❓ [需要澄清 X]
❓ [替代方法考虑]

## 结论

✅ 处理必须更改后批准
```
