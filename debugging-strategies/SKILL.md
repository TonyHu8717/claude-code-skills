---
name: debugging-strategies
description: 掌握系统化调试技术、性能分析工具和根本原因分析，以高效追踪任何代码库或技术栈中的 bug。在调查 bug、性能问题或意外行为时使用。
---

# 调试策略

将调试从令人沮丧的猜测转变为系统化的问题解决，使用经过验证的策略、强大的工具和有条理的方法。

## 使用场景

- 追踪难以捉摸的 bug
- 调查性能问题
- 理解不熟悉的代码库
- 调试生产问题
- 分析崩溃转储和堆栈跟踪
- 分析应用性能
- 调查内存泄漏
- 调试分布式系统

## 核心原则

### 1. 科学方法

**1. 观察**：实际行为是什么？
**2. 假设**：什么可能导致它？
**3. 实验**：测试您的假设
**4. 分析**：是否证明/推翻了您的理论？
**5. 重复**：直到找到根本原因

### 2. 调试心态

**不要假设：**

- "不可能是 X" — 是的，可以
- "我没有改 Y" — 还是要检查
- "在我的机器上可以" — 找出原因

**要做：**

- 一致地复现
- 隔离问题
- 保持详细笔记
- 质疑一切
- 卡住时休息一下

### 3. 小黄鸭调试法

向小黄鸭、同事或自己大声解释您的代码和问题。通常能揭示问题所在。

## 系统化调试流程

### 阶段 1：复现

```markdown
## 复现清单

1. **能否复现？**
   - 总是？有时？随机？
   - 需要特定条件？
   - 其他人能复现吗？

2. **创建最小复现**
   - 简化到最小示例
   - 移除无关代码
   - 隔离问题

3. **记录步骤**
   - 写下确切步骤
   - 注意环境详情
   - 捕获错误消息
```

### 阶段 2：收集信息

```markdown
## 信息收集

1. **错误消息**
   - 完整堆栈跟踪
   - 错误代码
   - 控制台/日志输出

2. **环境**
   - 操作系统版本
   - 语言/运行时版本
   - 依赖版本
   - 环境变量

3. **最近更改**
   - Git 历史
   - 部署时间线
   - 配置更改

4. **范围**
   - 影响所有用户还是特定用户？
   - 所有浏览器还是特定浏览器？
   - 仅生产还是开发也有？
```

### 阶段 3：形成假设

```markdown
## 假设形成

基于收集的信息，问：

1. **什么改变了？**
   - 最近的代码更改
   - 依赖更新
   - 基础设施更改

2. **什么不同？**
   - 工作 vs 损坏的环境
   - 工作 vs 损坏的用户
   - 之前 vs 之后

3. **哪里可能失败？**
   - 输入验证
   - 业务逻辑
   - 数据层
   - 外部服务
```

### 阶段 4：测试和验证

```markdown
## 测试策略

1. **二分搜索**
   - 注释掉一半代码
   - 缩小有问题的部分
   - 重复直到找到

2. **添加日志**
   - 战略性 console.log/print
   - 跟踪变量值
   - 追踪执行流程

3. **隔离组件**
   - 单独测试每个部分
   - 模拟依赖
   - 移除复杂性

4. **比较工作 vs 损坏**
   - 对比配置
   - 对比环境
   - 对比数据
```

## 调试工具

### JavaScript/TypeScript 调试

```typescript
// Chrome DevTools 调试器
function processOrder(order: Order) {
  debugger; // 执行在此暂停

  const total = calculateTotal(order);
  console.log("Total:", total);

  // 条件断点
  if (order.items.length > 10) {
    debugger; // 仅在条件为真时中断
  }

  return total;
}

// 控制台调试技术
console.log("Value:", value); // 基本
console.table(arrayOfObjects); // 表格格式
console.time("operation");
/* code */ console.timeEnd("operation"); // 计时
console.trace(); // 堆栈跟踪
console.assert(value > 0, "Value must be positive"); // 断言

// 性能分析
performance.mark("start-operation");
// ... 操作代码
performance.mark("end-operation");
performance.measure("operation", "start-operation", "end-operation");
console.log(performance.getEntriesByType("measure"));
```

**VS Code 调试器配置：**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Program",
      "program": "${workspaceFolder}/src/index.ts",
      "preLaunchTask": "tsc: build - tsconfig.json",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"],
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Tests",
      "program": "${workspaceFolder}/node_modules/jest/bin/jest",
      "args": ["--runInBand", "--no-cache"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Python 调试

```python
# 内置调试器 (pdb)
import pdb

def calculate_total(items):
    total = 0
    pdb.set_trace()  # 调试器在此启动

    for item in items:
        total += item.price * item.quantity

    return total

# Breakpoint (Python 3.7+)
def process_order(order):
    breakpoint()  # 比 pdb.set_trace() 更方便
    # ... code

# 事后调试
try:
    risky_operation()
except Exception:
    import pdb
    pdb.post_mortem()  # 在异常点调试

# IPython 调试 (ipdb)
from ipdb import set_trace
set_trace()  # 比 pdb 更好的界面

# 用于调试的日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_user(user_id):
    logger.debug(f'Fetching user: {user_id}')
    user = db.query(User).get(user_id)
    logger.debug(f'Found user: {user}')
    return user

# 性能分析
import cProfile
import pstats

cProfile.run('slow_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)  # 前 10 个最慢的
```

### Go 调试

```go
// Delve 调试器
// 安装: go install github.com/go-delve/delve/cmd/dlv@latest
// 运行: dlv debug main.go

import (
    "fmt"
    "runtime"
    "runtime/debug"
)

// 打印堆栈跟踪
func debugStack() {
    debug.PrintStack()
}

// 带调试的 panic 恢复
func processRequest() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Panic:", r)
            debug.PrintStack()
        }
    }()

    // ... 可能 panic 的代码
}

// 内存分析
import _ "net/http/pprof"
// 访问 http://localhost:6060/debug/pprof/

// CPU 分析
import (
    "os"
    "runtime/pprof"
)

f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
// ... 要分析的代码
```

## 高级调试技术

### 技术 1：二分搜索调试

```bash
# Git bisect 查找回归
git bisect start
git bisect bad                    # 当前提交是坏的
git bisect good v1.0.0            # v1.0.0 是好的

# Git 检出中间提交
# 测试它，然后：
git bisect good   # 如果可以工作
git bisect bad    # 如果坏了

# 继续直到找到 bug
git bisect reset  # 完成时
```

### 技术 2：差异调试

比较工作 vs 损坏：

```markdown
## 什么不同？

| 方面 | 工作 | 损坏 |
|------|------|------|
| 环境 | 开发 | 生产 |
| Node 版本 | 18.16.0 | 18.15.0 |
| 数据 | 空数据库 | 100 万条记录 |
| 用户 | 管理员 | 普通用户 |
| 浏览器 | Chrome | Safari |
| 时间 | 白天 | 午夜后 |

假设：基于时间的问题？检查时区处理。
```

### 技术 3：追踪调试

```typescript
// 函数调用追踪
function trace(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor,
) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with args:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`${propertyKey} returned:`, result);
    return result;
  };

  return descriptor;
}

class OrderService {
  @trace
  calculateTotal(items: Item[]): number {
    return items.reduce((sum, item) => sum + item.price, 0);
  }
}
```

### 技术 4：内存泄漏检测

```typescript
// Chrome DevTools 内存分析器
// 1. 拍摄堆快照
// 2. 执行操作
// 3. 拍摄另一个快照
// 4. 比较快照

// Node.js 内存调试
if (process.memoryUsage().heapUsed > 500 * 1024 * 1024) {
  console.warn("High memory usage:", process.memoryUsage());

  // 生成堆转储
  require("v8").writeHeapSnapshot();
}

// 在测试中查找内存泄漏
let beforeMemory: number;

beforeEach(() => {
  beforeMemory = process.memoryUsage().heapUsed;
});

afterEach(() => {
  const afterMemory = process.memoryUsage().heapUsed;
  const diff = afterMemory - beforeMemory;

  if (diff > 10 * 1024 * 1024) {
    // 10MB 阈值
    console.warn(`Possible memory leak: ${diff / 1024 / 1024}MB`);
  }
});
```

## 按问题类型的调试模式

### 模式 1：间歇性 Bug

```markdown
## 不稳定 Bug 的策略

1. **添加大量日志**
   - 记录时间信息
   - 记录所有状态转换
   - 记录外部交互

2. **查找竞态条件**
   - 对共享状态的并发访问
   - 异步操作乱序完成
   - 缺少同步

3. **检查时序依赖**
   - setTimeout/setInterval
   - Promise 解析顺序
   - 动画帧时序

4. **压力测试**
   - 运行多次
   - 变化时序
   - 模拟负载
```

### 模式 2：性能问题

```markdown
## 性能调试

1. **先分析**
   - 不要盲目优化
   - 前后测量
   - 找到瓶颈

2. **常见罪魁祸首**
   - N+1 查询
   - 不必要的重新渲染
   - 大数据处理
   - 同步 I/O

3. **工具**
   - 浏览器 DevTools Performance 标签
   - Lighthouse
   - Python: cProfile, line_profiler
   - Node: clinic.js, 0x
```

### 模式 3：生产 Bug

```markdown
## 生产调试

1. **收集证据**
   - 错误跟踪 (Sentry, Bugsnag)
   - 应用日志
   - 用户报告
   - 指标/监控

2. **本地复现**
   - 使用生产数据（匿名化）
   - 匹配环境
   - 遵循确切步骤

3. **安全调查**
   - 不要更改生产环境
   - 使用功能标志
   - 添加监控/日志
   - 在预发布环境测试修复
```

## 最佳实践

1. **先复现**：无法修复无法复现的问题
2. **隔离问题**：移除复杂性直到最小情况
3. **阅读错误消息**：它们通常很有帮助
4. **检查最近更改**：大多数 bug 是最近的
5. **使用版本控制**：Git bisect、blame、history
6. **休息一下**：新鲜的眼睛看得更清楚
7. **记录发现**：帮助未来的自己
8. **修复根本原因**：不仅仅是症状

## 常见调试错误

- **做多个更改**：一次只改一件事
- **不阅读错误消息**：阅读完整堆栈跟踪
- **假设很复杂**：通常很简单
- **在生产中调试日志**：发布前移除
- **不使用调试器**：console.log 并非总是最好
- **放弃太早**：坚持会有回报
- **不测试修复**：验证它确实有效

## 快速调试清单

```markdown
## 卡住时检查：

- [ ] 拼写错误（变量名中的错字）
- [ ] 大小写敏感（fileName vs filename）
- [ ] 空值/未定义值
- [ ] 数组索引差一错误
- [ ] 异步时序（竞态条件）
- [ ] 作用域问题（闭包、提升）
- [ ] 类型不匹配
- [ ] 缺少依赖
- [ ] 环境变量
- [ ] 文件路径（绝对 vs 相对）
- [ ] 缓存问题（清除缓存）
- [ ] 陈旧数据（刷新数据库）
```
