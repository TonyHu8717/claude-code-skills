---
name: python-performance-optimization
description: 使用 cProfile、内存分析器和性能最佳实践来分析和优化 Python 代码。在调试缓慢的 Python 代码、优化瓶颈或提高应用程序性能时使用。
---

# Python 性能优化

分析、分析和优化 Python 代码以获得更好性能的综合指南，包括 CPU 分析、内存优化和实现最佳实践。

## 何时使用此技能

- 识别 Python 应用程序中的性能瓶颈
- 减少应用程序延迟和响应时间
- 优化 CPU 密集型操作
- 减少内存消耗和内存泄漏
- 提高数据库查询性能
- 优化 I/O 操作
- 加速数据处理管道
- 实现高性能算法
- 分析生产应用程序

## 核心概念

### 1. 分析类型

- **CPU 分析**：识别耗时函数
- **内存分析**：跟踪内存分配和泄漏
- **行分析**：逐行粒度分析
- **调用图**：可视化函数调用关系

### 2. 性能指标

- **执行时间**：操作耗时
- **内存使用**：峰值和平均内存消耗
- **CPU 利用率**：处理器使用模式
- **I/O 等待**：I/O 操作花费的时间

### 3. 优化策略

- **算法**：更好的算法和数据结构
- **实现**：更高效的代码模式
- **并行化**：多线程/多处理
- **缓存**：避免冗余计算
- **原生扩展**：C/Rust 用于关键路径

## 快速开始

### 基本计时

```python
import time

def measure_time():
    """Simple timing measurement."""
    start = time.time()

    # Your code here
    result = sum(range(1000000))

    elapsed = time.time() - start
    print(f"Execution time: {elapsed:.4f} seconds")
    return result

# Better: use timeit for accurate measurements
import timeit

execution_time = timeit.timeit(
    "sum(range(1000000))",
    number=100
)
print(f"Average time: {execution_time/100:.6f} seconds")
```

## 分析工具

### 模式 1：cProfile - CPU 分析

```python
import cProfile
import pstats
from pstats import SortKey

def slow_function():
    """Function to profile."""
    total = 0
    for i in range(1000000):
        total += i
    return total

def another_function():
    """Another function."""
    return [i**2 for i in range(100000)]

def main():
    """Main function to profile."""
    result1 = slow_function()
    result2 = another_function()
    return result1, result2

# Profile the code
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)  # Top 10 functions

    # Save to file for later analysis
    stats.dump_stats("profile_output.prof")
```

**命令行分析：**

```bash
# Profile a script
python -m cProfile -o output.prof script.py

# View results
python -m pstats output.prof
# In pstats:
# sort cumtime
# stats 10
```

### 模式 2：line_profiler - 逐行分析

```python
# Install: pip install line-profiler

# Add @profile decorator (line_profiler provides this)
@profile
def process_data(data):
    """Process data with line profiling."""
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result

# Run with:
# kernprof -l -v script.py
```

**手动行分析：**

```python
from line_profiler import LineProfiler

def process_data(data):
    """Function to profile."""
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result

if __name__ == "__main__":
    lp = LineProfiler()
    lp.add_function(process_data)

    data = list(range(100000))

    lp_wrapper = lp(process_data)
    lp_wrapper(data)

    lp.print_stats()
```

### 模式 3：memory_profiler - 内存使用

```python
# Install: pip install memory-profiler

from memory_profiler import profile

@profile
def memory_intensive():
    """Function that uses lots of memory."""
    # Create large list
    big_list = [i for i in range(1000000)]

    # Create large dict
    big_dict = {i: i**2 for i in range(100000)}

    # Process data
    result = sum(big_list)

    return result

if __name__ == "__main__":
    memory_intensive()

# Run with:
# python -m memory_profiler script.py
```

### 模式 4：py-spy - 生产环境分析

```bash
# Install: pip install py-spy

# Profile a running Python process
py-spy top --pid 12345

# Generate flamegraph
py-spy record -o profile.svg --pid 12345

# Profile a script
py-spy record -o profile.svg -- python script.py

# Dump current call stack
py-spy dump --pid 12345
```

## 优化模式

### 模式 5：列表推导式 vs 循环

```python
import timeit

# Slow: Traditional loop
def slow_squares(n):
    """Create list of squares using loop."""
    result = []
    for i in range(n):
        result.append(i**2)
    return result

# Fast: List comprehension
def fast_squares(n):
    """Create list of squares using comprehension."""
    return [i**2 for i in range(n)]

# Benchmark
n = 100000

slow_time = timeit.timeit(lambda: slow_squares(n), number=100)
fast_time = timeit.timeit(lambda: fast_squares(n), number=100)

print(f"Loop: {slow_time:.4f}s")
print(f"Comprehension: {fast_time:.4f}s")
print(f"Speedup: {slow_time/fast_time:.2f}x")

# Even faster for simple operations: map
def faster_squares(n):
    """Use map for even better performance."""
    return list(map(lambda x: x**2, range(n)))
```

### 模式 6：生成器表达式节省内存

```python
import sys

def list_approach():
    """Memory-intensive list."""
    data = [i**2 for i in range(1000000)]
    return sum(data)

def generator_approach():
    """Memory-efficient generator."""
    data = (i**2 for i in range(1000000))
    return sum(data)

# Memory comparison
list_data = [i for i in range(1000000)]
gen_data = (i for i in range(1000000))

print(f"List size: {sys.getsizeof(list_data)} bytes")
print(f"Generator size: {sys.getsizeof(gen_data)} bytes")

# Generators use constant memory regardless of size
```

### 模式 7：字符串拼接

```python
import timeit

def slow_concat(items):
    """Slow string concatenation."""
    result = ""
    for item in items:
        result += str(item)
    return result

def fast_concat(items):
    """Fast string concatenation with join."""
    return "".join(str(item) for item in items)

def faster_concat(items):
    """Even faster with list."""
    parts = [str(item) for item in items]
    return "".join(parts)

items = list(range(10000))

# Benchmark
slow = timeit.timeit(lambda: slow_concat(items), number=100)
fast = timeit.timeit(lambda: fast_concat(items), number=100)
faster = timeit.timeit(lambda: faster_concat(items), number=100)

print(f"Concatenation (+): {slow:.4f}s")
print(f"Join (generator): {fast:.4f}s")
print(f"Join (list): {faster:.4f}s")
```

### 模式 8：字典查找 vs 列表搜索

```python
import timeit

# Create test data
size = 10000
items = list(range(size))
lookup_dict = {i: i for i in range(size)}

def list_search(items, target):
    """O(n) search in list."""
    return target in items

def dict_search(lookup_dict, target):
    """O(1) search in dict."""
    return target in lookup_dict

target = size - 1  # Worst case for list

# Benchmark
list_time = timeit.timeit(
    lambda: list_search(items, target),
    number=1000
)
dict_time = timeit.timeit(
    lambda: dict_search(lookup_dict, target),
    number=1000
)

print(f"List search: {list_time:.6f}s")
print(f"Dict search: {dict_time:.6f}s")
print(f"Speedup: {list_time/dict_time:.0f}x")
```

### 模式 9：局部变量访问

```python
import timeit

# Global variable (slow)
GLOBAL_VALUE = 100

def use_global():
    """Access global variable."""
    total = 0
    for i in range(10000):
        total += GLOBAL_VALUE
    return total

def use_local():
    """Use local variable."""
    local_value = 100
    total = 0
    for i in range(10000):
        total += local_value
    return total

# Local is faster
global_time = timeit.timeit(use_global, number=1000)
local_time = timeit.timeit(use_local, number=1000)

print(f"Global access: {global_time:.4f}s")
print(f"Local access: {local_time:.4f}s")
print(f"Speedup: {global_time/local_time:.2f}x")
```

### 模式 10：函数调用开销

```python
import timeit

def calculate_inline():
    """Inline calculation."""
    total = 0
    for i in range(10000):
        total += i * 2 + 1
    return total

def helper_function(x):
    """Helper function."""
    return x * 2 + 1

def calculate_with_function():
    """Calculation with function calls."""
    total = 0
    for i in range(10000):
        total += helper_function(i)
    return total

# Inline is faster due to no call overhead
inline_time = timeit.timeit(calculate_inline, number=1000)
function_time = timeit.timeit(calculate_with_function, number=1000)

print(f"Inline: {inline_time:.4f}s")
print(f"Function calls: {function_time:.4f}s")
```

有关高级优化技术，包括 NumPy 向量化、缓存、内存管理、并行化、异步 I/O、数据库优化和基准测试工具，请参阅 [references/advanced-patterns.md](references/advanced-patterns.md)

## 最佳实践

1. **优化前先分析** - 测量以找到真正的瓶颈
2. **关注热路径** - 优化最频繁运行的代码
3. **使用适当的数据结构** - 字典用于查找，集合用于成员测试
4. **避免过早优化** - 清晰性优先，然后优化
5. **使用内置函数** - 它们是用 C 实现的
6. **缓存昂贵的计算** - 使用 lru_cache
7. **批量 I/O 操作** - 减少系统调用
8. **使用生成器** 处理大数据集
9. **考虑 NumPy** 进行数值运算
10. **分析生产代码** - 使用 py-spy 分析在线系统

## 常见陷阱

- 不分析就优化
- 不必要地使用全局变量
- 不使用适当的数据结构
- 创建不必要的数据副本
- 不为数据库使用连接池
- 忽视算法复杂度
- 过度优化不常见的代码路径
- 不考虑内存使用
