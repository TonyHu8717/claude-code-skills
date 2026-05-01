---
name: go-concurrency-patterns
description: 掌握 Go 并发编程，包括 goroutine、channel、同步原语和 context。在构建并发 Go 应用、实现工作池或调试竞态条件时使用。
---

# Go 并发模式

Go 并发的生产级模式，包括 goroutine、channel、同步原语和上下文管理。

## 何时使用此技能

- 构建并发 Go 应用
- 实现工作池和管道
- 管理 goroutine 生命周期
- 使用 channel 进行通信
- 调试竞态条件
- 实现优雅关闭

## 核心概念

### 1. Go 并发原语

| 原语              | 用途                           |
| ----------------- | ------------------------------ |
| `goroutine`       | 轻量级并发执行                 |
| `channel`         | goroutine 间通信               |
| `select`          | 多路复用 channel 操作          |
| `sync.Mutex`      | 互斥锁                         |
| `sync.WaitGroup`  | 等待 goroutine 完成            |
| `context.Context` | 取消和截止时间                 |

### 2. Go 并发格言

```
不要通过共享内存来通信；
通过通信来共享内存。
```

## 快速开始

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    results := make(chan string, 10)
    var wg sync.WaitGroup

    // 启动工作者
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go worker(ctx, i, results, &wg)
    }

    // 完成后关闭 results
    go func() {
        wg.Wait()
        close(results)
    }()

    // 收集结果
    for result := range results {
        fmt.Println(result)
    }
}

func worker(ctx context.Context, id int, results chan<- string, wg *sync.WaitGroup) {
    defer wg.Done()

    select {
    case <-ctx.Done():
        return
    case results <- fmt.Sprintf("Worker %d done", id):
    }
}
```

## 模式

### 模式 1：工作池

```go
package main

import (
    "context"
    "fmt"
    "sync"
)

type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID int
    Output string
    Err   error
}

func WorkerPool(ctx context.Context, numWorkers int, jobs <-chan Job) <-chan Result {
    results := make(chan Result, len(jobs))

    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for job := range jobs {
                select {
                case <-ctx.Done():
                    return
                default:
                    result := processJob(job)
                    results <- result
                }
            }
        }(i)
    }

    go func() {
        wg.Wait()
        close(results)
    }()

    return results
}

func processJob(job Job) Result {
    // 模拟工作
    return Result{
        JobID:  job.ID,
        Output: fmt.Sprintf("Processed: %s", job.Data),
    }
}

// 使用
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    jobs := make(chan Job, 100)

    // 发送任务
    go func() {
        for i := 0; i < 50; i++ {
            jobs <- Job{ID: i, Data: fmt.Sprintf("job-%d", i)}
        }
        close(jobs)
    }()

    // 使用 5 个工作者处理
    results := WorkerPool(ctx, 5, jobs)

    for result := range results {
        fmt.Printf("Result: %+v\n", result)
    }
}
```

### 模式 2：扇出/扇入管道

```go
package main

import (
    "context"
    "sync"
)

// 阶段 1：生成数字
func generate(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            select {
            case <-ctx.Done():
                return
            case out <- n:
            }
        }
    }()
    return out
}

// 阶段 2：平方数字（可以运行多个实例）
func square(ctx context.Context, in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            select {
            case <-ctx.Done():
                return
            case out <- n * n:
            }
        }
    }()
    return out
}

// 扇入：将多个 channel 合并为一个
func merge(ctx context.Context, cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    // 为每个输入 channel 启动输出 goroutine
    output := func(c <-chan int) {
        defer wg.Done()
        for n := range c {
            select {
            case <-ctx.Done():
                return
            case out <- n:
            }
        }
    }

    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }

    // 所有输入完成后关闭 out
    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // 生成输入
    in := generate(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    // 扇出到多个平方器
    c1 := square(ctx, in)
    c2 := square(ctx, in)
    c3 := square(ctx, in)

    // 扇入结果
    for result := range merge(ctx, c1, c2, c3) {
        fmt.Println(result)
    }
}
```

### 模式 3：使用信号量限制并发

```go
package main

import (
    "context"
    "fmt"
    "golang.org/x/sync/semaphore"
    "sync"
)

type RateLimitedWorker struct {
    sem *semaphore.Weighted
}

func NewRateLimitedWorker(maxConcurrent int64) *RateLimitedWorker {
    return &RateLimitedWorker{
        sem: semaphore.NewWeighted(maxConcurrent),
    }
}

func (w *RateLimitedWorker) Do(ctx context.Context, tasks []func() error) []error {
    var (
        wg     sync.WaitGroup
        mu     sync.Mutex
        errors []error
    )

    for _, task := range tasks {
        // 获取信号量（达到限制时阻塞）
        if err := w.sem.Acquire(ctx, 1); err != nil {
            return []error{err}
        }

        wg.Add(1)
        go func(t func() error) {
            defer wg.Done()
            defer w.sem.Release(1)

            if err := t(); err != nil {
                mu.Lock()
                errors = append(errors, err)
                mu.Unlock()
            }
        }(task)
    }

    wg.Wait()
    return errors
}

// 替代方案：基于 channel 的信号量
type Semaphore chan struct{}

func NewSemaphore(n int) Semaphore {
    return make(chan struct{}, n)
}

func (s Semaphore) Acquire() {
    s <- struct{}{}
}

func (s Semaphore) Release() {
    <-s
}
```

### 模式 4：优雅关闭

```go
package main

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "sync"
    "syscall"
    "time"
)

type Server struct {
    shutdown chan struct{}
    wg       sync.WaitGroup
}

func NewServer() *Server {
    return &Server{
        shutdown: make(chan struct{}),
    }
}

func (s *Server) Start(ctx context.Context) {
    // 启动工作者
    for i := 0; i < 5; i++ {
        s.wg.Add(1)
        go s.worker(ctx, i)
    }
}

func (s *Server) worker(ctx context.Context, id int) {
    defer s.wg.Done()
    defer fmt.Printf("Worker %d stopped\n", id)

    ticker := time.NewTicker(time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            // 清理
            fmt.Printf("Worker %d cleaning up...\n", id)
            time.Sleep(500 * time.Millisecond) // 模拟清理
            return
        case <-ticker.C:
            fmt.Printf("Worker %d working...\n", id)
        }
    }
}

func (s *Server) Shutdown(timeout time.Duration) {
    // 发送关闭信号
    close(s.shutdown)

    // 带超时等待
    done := make(chan struct{})
    go func() {
        s.wg.Wait()
        close(done)
    }()

    select {
    case <-done:
        fmt.Println("Clean shutdown completed")
    case <-time.After(timeout):
        fmt.Println("Shutdown timed out, forcing exit")
    }
}

func main() {
    // 设置信号处理
    ctx, cancel := context.WithCancel(context.Background())

    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

    server := NewServer()
    server.Start(ctx)

    // 等待信号
    sig := <-sigCh
    fmt.Printf("\nReceived signal: %v\n", sig)

    // 取消 context 以停止工作者
    cancel()

    // 等待优雅关闭
    server.Shutdown(5 * time.Second)
}
```

### 模式 5：带取消的错误组

```go
package main

import (
    "context"
    "fmt"
    "golang.org/x/sync/errgroup"
    "net/http"
)

func fetchAllURLs(ctx context.Context, urls []string) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)

    results := make([]string, len(urls))

    for i, url := range urls {
        i, url := i, url // 捕获循环变量

        g.Go(func() error {
            req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
            if err != nil {
                return fmt.Errorf("creating request for %s: %w", url, err)
            }

            resp, err := http.DefaultClient.Do(req)
            if err != nil {
                return fmt.Errorf("fetching %s: %w", url, err)
            }
            defer resp.Body.Close()

            results[i] = fmt.Sprintf("%s: %d", url, resp.StatusCode)
            return nil
        })
    }

    // 等待所有 goroutine 完成或其中一个失败
    if err := g.Wait(); err != nil {
        return nil, err // 第一个错误取消所有其他
    }

    return results, nil
}

// 带并发限制
func fetchWithLimit(ctx context.Context, urls []string, limit int) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(limit) // 最大并发 goroutine 数

    results := make([]string, len(urls))
    var mu sync.Mutex

    for i, url := range urls {
        i, url := i, url

        g.Go(func() error {
            result, err := fetchURL(ctx, url)
            if err != nil {
                return err
            }

            mu.Lock()
            results[i] = result
            mu.Unlock()
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return results, nil
}
```

### 模式 6：使用 sync.Map 的并发 Map

```go
package main

import (
    "sync"
)

// 适用于频繁读取、不频繁写入
type Cache struct {
    m sync.Map
}

func (c *Cache) Get(key string) (interface{}, bool) {
    return c.m.Load(key)
}

func (c *Cache) Set(key string, value interface{}) {
    c.m.Store(key, value)
}

func (c *Cache) GetOrSet(key string, value interface{}) (interface{}, bool) {
    return c.m.LoadOrStore(key, value)
}

func (c *Cache) Delete(key string) {
    c.m.Delete(key)
}

// 对于写密集型工作负载，使用分片 map
type ShardedMap struct {
    shards    []*shard
    numShards int
}

type shard struct {
    sync.RWMutex
    data map[string]interface{}
}

func NewShardedMap(numShards int) *ShardedMap {
    m := &ShardedMap{
        shards:    make([]*shard, numShards),
        numShards: numShards,
    }
    for i := range m.shards {
        m.shards[i] = &shard{data: make(map[string]interface{})}
    }
    return m
}

func (m *ShardedMap) getShard(key string) *shard {
    // 简单哈希
    h := 0
    for _, c := range key {
        h = 31*h + int(c)
    }
    return m.shards[h%m.numShards]
}

func (m *ShardedMap) Get(key string) (interface{}, bool) {
    shard := m.getShard(key)
    shard.RLock()
    defer shard.RUnlock()
    v, ok := shard.data[key]
    return v, ok
}

func (m *ShardedMap) Set(key string, value interface{}) {
    shard := m.getShard(key)
    shard.Lock()
    defer shard.Unlock()
    shard.data[key] = value
}
```

### 模式 7：带超时和默认的 Select

```go
func selectPatterns() {
    ch := make(chan int)

    // 超时模式
    select {
    case v := <-ch:
        fmt.Println("Received:", v)
    case <-time.After(time.Second):
        fmt.Println("Timeout!")
    }

    // 非阻塞发送/接收
    select {
    case ch <- 42:
        fmt.Println("Sent")
    default:
        fmt.Println("Channel full, skipping")
    }

    // 优先级 select（先检查高优先级）
    highPriority := make(chan int)
    lowPriority := make(chan int)

    for {
        select {
        case msg := <-highPriority:
            fmt.Println("High priority:", msg)
        default:
            select {
            case msg := <-highPriority:
                fmt.Println("High priority:", msg)
            case msg := <-lowPriority:
                fmt.Println("Low priority:", msg)
            }
        }
    }
}
```

## 竞态检测

```bash
# 使用竞态检测器运行测试
go test -race ./...

# 使用竞态检测器构建
go build -race .

# 使用竞态检测器运行
go run -race main.go
```

## 最佳实践

### 应该做的

- **使用 context** - 用于取消和截止时间
- **关闭 channel** - 仅从发送方关闭
- **使用 errgroup** - 用于带错误的并发操作
- **缓冲 channel** - 当你知道数量时
- **优先使用 channel** - 尽可能代替互斥锁

### 不应该做的

- **不要泄漏 goroutine** - 始终有退出路径
- **不要从接收方关闭** - 会导致 panic
- **不要使用共享内存** - 除非必要
- **不要忽略 context 取消** - 检查 ctx.Done()
- **不要使用 time.Sleep 同步** - 使用正确的原语
