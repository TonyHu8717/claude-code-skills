---
name: code-review
description: 执行全面的代码审查，涵盖安全性、性能和可维护性分析。当用户要求审查代码、检查 bug 或审计代码库时使用。
---

# 代码审查技能

您现在具备进行全面代码审查的专业知识。请遵循以下结构化方法：

## 审查清单

### 1. 安全性（关键）

检查：
- [ ] **注入漏洞**：SQL、命令、XSS、模板注入
- [ ] **认证问题**：硬编码凭据、弱认证
- [ ] **授权缺陷**：缺少访问控制、IDOR
- [ ] **数据暴露**：日志中的敏感数据、错误消息
- [ ] **加密**：弱算法、不当的密钥管理
- [ ] **依赖项**：已知漏洞（使用 `npm audit`、`pip-audit` 检查）

```bash
# 快速安全扫描
npm audit                    # Node.js
pip-audit                    # Python
cargo audit                  # Rust
grep -r "password\|secret\|api_key" --include="*.py" --include="*.js"
```

### 2. 正确性

检查：
- [ ] **逻辑错误**：差一错误、空值处理、边界条件
- [ ] **竞态条件**：无同步的并发访问
- [ ] **资源泄漏**：未关闭的文件、连接、内存
- [ ] **错误处理**：吞掉的异常、缺少错误路径
- [ ] **类型安全**：隐式转换、any 类型

### 3. 性能

检查：
- [ ] **N+1 查询**：循环中的数据库调用
- [ ] **内存问题**：大量分配、保留引用
- [ ] **阻塞操作**：异步代码中的同步 I/O
- [ ] **低效算法**：可以 O(n) 时使用 O(n^2)
- [ ] **缺少缓存**：重复的昂贵计算

### 4. 可维护性

检查：
- [ ] **命名**：清晰、一致、描述性
- [ ] **复杂度**：函数 > 50 行、嵌套 > 3 层
- [ ] **重复**：复制粘贴的代码块
- [ ] **死代码**：未使用的导入、不可达分支
- [ ] **注释**：过时、冗余或需要时缺失

### 5. 测试

检查：
- [ ] **覆盖率**：关键路径已测试
- [ ] **边界条件**：空值、空集、边界值
- [ ] **模拟**：外部依赖已隔离
- [ ] **断言**：有意义的、具体的检查

## 审查输出格式

```markdown
## 代码审查：[文件/组件名称]

### 摘要
[1-2 句概述]

### 严重问题
1. **[问题]**（第 X 行）：[描述]
   - 影响：[可能出什么问题]
   - 修复：[建议的解决方案]

### 改进建议
1. **[建议]**（第 X 行）：[描述]

### 亮点
- [做得好的地方]

### 结论
[ ] 准备合并
[ ] 需要小幅修改
[ ] 需要重大修订
```

## 常见问题模式

### Python
```python
# 不好：SQL 注入
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# 好：
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# 不好：命令注入
os.system(f"ls {user_input}")
# 好：
subprocess.run(["ls", user_input], check=True)

# 不好：可变默认参数
def append(item, lst=[]):  # Bug：共享可变默认值
# 好：
def append(item, lst=None):
    lst = lst or []
```

### JavaScript/TypeScript
```javascript
// 不好：原型污染
Object.assign(target, userInput)
// 好：
Object.assign(target, sanitize(userInput))

// 不好：使用 eval
eval(userCode)
// 好：永远不要对用户输入使用 eval

// 不好：回调地狱
getData(x => process(x, y => save(y, z => done(z))))
// 好：
const data = await getData();
const processed = await process(data);
await save(processed);
```

## 审查命令

```bash
# 显示最近的更改
git diff HEAD~5 --stat
git log --oneline -10

# 查找潜在问题
grep -rn "TODO\|FIXME\|HACK\|XXX" .
grep -rn "password\|secret\|token" . --include="*.py"

# 检查复杂度（Python）
pip install radon && radon cc . -a

# 检查依赖
npm outdated  # Node
pip list --outdated  # Python
```

## 审查工作流程

1. **理解上下文**：阅读 PR 描述、关联的 issue
2. **运行代码**：构建、测试、本地运行（如果可能）
3. **自顶向下阅读**：从主入口点开始
4. **检查测试**：变更是否经过测试？测试是否通过？
5. **安全扫描**：运行自动化工具
6. **手动审查**：使用上述清单
7. **撰写反馈**：具体、建议修复、友善
