---
name: spark-optimization
description: 使用分区、缓存、shuffle 优化和内存调优优化 Apache Spark 作业。在提升 Spark 性能、调试慢作业或扩展数据处理管道时使用。
---

# Apache Spark 优化

优化 Apache Spark 作业的生产模式，包括分区策略、内存管理、shuffle 优化和性能调优。

## 何时使用此技能

- 优化慢速 Spark 作业
- 调优内存和执行器配置
- 实现高效的分区策略
- 调试 Spark 性能问题
- 为大型数据集扩展 Spark 管道
- 减少 shuffle 和数据倾斜

## 核心概念

### 1. Spark 执行模型

```
驱动程序
    ↓
作业（由 action 触发）
    ↓
阶段（由 shuffle 分隔）
    ↓
任务（每个分区一个）
```

### 2. 关键性能因素

| 因素            | 影响                  | 解决方案                    |
| ---------------- | --------------------- | --------------------------- |
| **Shuffle**      | 网络 I/O、磁盘 I/O   | 最小化宽转换               |
| **数据倾斜**     | 任务持续时间不均匀   | 加盐、广播连接             |
| **序列化**       | CPU 开销              | 使用 Kryo、列式格式        |
| **内存**         | GC 压力、溢出         | 调优执行器内存             |
| **分区**         | 并行度                | 合理设置分区大小           |

## 快速开始

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Create optimized Spark session
spark = (SparkSession.builder
    .appName("OptimizedJob")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate())

# Read with optimized settings
df = (spark.read
    .format("parquet")
    .option("mergeSchema", "false")
    .load("s3://bucket/data/"))

# Efficient transformations
result = (df
    .filter(F.col("date") >= "2024-01-01")
    .select("id", "amount", "category")
    .groupBy("category")
    .agg(F.sum("amount").alias("total")))

result.write.mode("overwrite").parquet("s3://bucket/output/")
```

## 模式

### 模式 1：最优分区

```python
# Calculate optimal partition count
def calculate_partitions(data_size_gb: float, partition_size_mb: int = 128) -> int:
    """
    Optimal partition size: 128MB - 256MB
    Too few: Under-utilization, memory pressure
    Too many: Task scheduling overhead
    """
    return max(int(data_size_gb * 1024 / partition_size_mb), 1)

# Repartition for even distribution
df_repartitioned = df.repartition(200, "partition_key")

# Coalesce to reduce partitions (no shuffle)
df_coalesced = df.coalesce(100)

# Partition pruning with predicate pushdown
df = (spark.read.parquet("s3://bucket/data/")
    .filter(F.col("date") == "2024-01-01"))  # Spark pushes this down

# Write with partitioning for future queries
(df.write
    .partitionBy("year", "month", "day")
    .mode("overwrite")
    .parquet("s3://bucket/partitioned_output/"))
```

### 模式 2：连接优化

```python
from pyspark.sql import functions as F
from pyspark.sql.types import *

# 1. Broadcast Join - Small table joins
# Best when: One side < 10MB (configurable)
small_df = spark.read.parquet("s3://bucket/small_table/")  # < 10MB
large_df = spark.read.parquet("s3://bucket/large_table/")  # TBs

# Explicit broadcast hint
result = large_df.join(
    F.broadcast(small_df),
    on="key",
    how="left"
)

# 2. Sort-Merge Join - Default for large tables
# Requires shuffle, but handles any size
result = large_df1.join(large_df2, on="key", how="inner")

# 3. Bucket Join - Pre-sorted, no shuffle at join time
# Write bucketed tables
(df.write
    .bucketBy(200, "customer_id")
    .sortBy("customer_id")
    .mode("overwrite")
    .saveAsTable("bucketed_orders"))

# Join bucketed tables (no shuffle!)
orders = spark.table("bucketed_orders")
customers = spark.table("bucketed_customers")  # Same bucket count
result = orders.join(customers, on="customer_id")

# 4. Skew Join Handling
# Enable AQE skew join optimization
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Manual salting for severe skew
def salt_join(df_skewed, df_other, key_col, num_salts=10):
    """Add salt to distribute skewed keys"""
    # Add salt to skewed side
    df_salted = df_skewed.withColumn(
        "salt",
        (F.rand() * num_salts).cast("int")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    # Explode other side with all salts
    df_exploded = df_other.crossJoin(
        spark.range(num_salts).withColumnRenamed("id", "salt")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    # Join on salted key
    return df_salted.join(df_exploded, on="salted_key", how="inner")
```

### 模式 3：缓存和持久化

```python
from pyspark import StorageLevel

# Cache when reusing DataFrame multiple times
df = spark.read.parquet("s3://bucket/data/")
df_filtered = df.filter(F.col("status") == "active")

# Cache in memory (MEMORY_AND_DISK is default)
df_filtered.cache()

# Or with specific storage level
df_filtered.persist(StorageLevel.MEMORY_AND_DISK_SER)

# Force materialization
df_filtered.count()

# Use in multiple actions
agg1 = df_filtered.groupBy("category").count()
agg2 = df_filtered.groupBy("region").sum("amount")

# Unpersist when done
df_filtered.unpersist()

# Storage levels explained:
# MEMORY_ONLY - Fast, but may not fit
# MEMORY_AND_DISK - Spills to disk if needed (recommended)
# MEMORY_ONLY_SER - Serialized, less memory, more CPU
# DISK_ONLY - When memory is tight
# OFF_HEAP - Tungsten off-heap memory

# Checkpoint for complex lineage
spark.sparkContext.setCheckpointDir("s3://bucket/checkpoints/")
df_complex = (df
    .join(other_df, "key")
    .groupBy("category")
    .agg(F.sum("amount")))
df_complex.checkpoint()  # Breaks lineage, materializes
```

### 模式 4：内存调优

```python
# Executor memory configuration
# spark-submit --executor-memory 8g --executor-cores 4

# Memory breakdown (8GB executor):
# - spark.memory.fraction = 0.6 (60% = 4.8GB for execution + storage)
#   - spark.memory.storageFraction = 0.5 (50% of 4.8GB = 2.4GB for cache)
#   - Remaining 2.4GB for execution (shuffles, joins, sorts)
# - 40% = 3.2GB for user data structures and internal metadata

spark = (SparkSession.builder
    .config("spark.executor.memory", "8g")
    .config("spark.executor.memoryOverhead", "2g")  # For non-JVM memory
    .config("spark.memory.fraction", "0.6")
    .config("spark.memory.storageFraction", "0.5")
    .config("spark.sql.shuffle.partitions", "200")
    # For memory-intensive operations
    .config("spark.sql.autoBroadcastJoinThreshold", "50MB")
    # Prevent OOM on large shuffles
    .config("spark.sql.files.maxPartitionBytes", "128MB")
    .getOrCreate())

# Monitor memory usage
def print_memory_usage(spark):
    """Print current memory usage"""
    sc = spark.sparkContext
    for executor in sc._jsc.sc().getExecutorMemoryStatus().keySet().toArray():
        mem_status = sc._jsc.sc().getExecutorMemoryStatus().get(executor)
        total = mem_status._1() / (1024**3)
        free = mem_status._2() / (1024**3)
        print(f"{executor}: {total:.2f}GB total, {free:.2f}GB free")
```

### 模式 5：Shuffle 优化

```python
# Reduce shuffle data size
spark.conf.set("spark.sql.shuffle.partitions", "auto")  # With AQE
spark.conf.set("spark.shuffle.compress", "true")
spark.conf.set("spark.shuffle.spill.compress", "true")

# Pre-aggregate before shuffle
df_optimized = (df
    # Local aggregation first (combiner)
    .groupBy("key", "partition_col")
    .agg(F.sum("value").alias("partial_sum"))
    # Then global aggregation
    .groupBy("key")
    .agg(F.sum("partial_sum").alias("total")))

# Avoid shuffle with map-side operations
# BAD: Shuffle for each distinct
distinct_count = df.select("category").distinct().count()

# GOOD: Approximate distinct (no shuffle)
approx_count = df.select(F.approx_count_distinct("category")).collect()[0][0]

# Use coalesce instead of repartition when reducing partitions
df_reduced = df.coalesce(10)  # No shuffle

# Optimize shuffle with compression
spark.conf.set("spark.io.compression.codec", "lz4")  # Fast compression
```

### 模式 6：数据格式优化

```python
# Parquet optimizations
(df.write
    .option("compression", "snappy")  # Fast compression
    .option("parquet.block.size", 128 * 1024 * 1024)  # 128MB row groups
    .parquet("s3://bucket/output/"))

# Column pruning - only read needed columns
df = (spark.read.parquet("s3://bucket/data/")
    .select("id", "amount", "date"))  # Spark only reads these columns

# Predicate pushdown - filter at storage level
df = (spark.read.parquet("s3://bucket/partitioned/year=2024/")
    .filter(F.col("status") == "active"))  # Pushed to Parquet reader

# Delta Lake optimizations
(df.write
    .format("delta")
    .option("optimizeWrite", "true")  # Bin-packing
    .option("autoCompact", "true")  # Compact small files
    .mode("overwrite")
    .save("s3://bucket/delta_table/"))

# Z-ordering for multi-dimensional queries
spark.sql("""
    OPTIMIZE delta.`s3://bucket/delta_table/`
    ZORDER BY (customer_id, date)
""")
```

### 模式 7：监控和调试

```python
# Enable detailed metrics
spark.conf.set("spark.sql.codegen.wholeStage", "true")
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

# Explain query plan
df.explain(mode="extended")
# Modes: simple, extended, codegen, cost, formatted

# Get physical plan statistics
df.explain(mode="cost")

# Monitor task metrics
def analyze_stage_metrics(spark):
    """Analyze recent stage metrics"""
    status_tracker = spark.sparkContext.statusTracker()

    for stage_id in status_tracker.getActiveStageIds():
        stage_info = status_tracker.getStageInfo(stage_id)
        print(f"Stage {stage_id}:")
        print(f"  Tasks: {stage_info.numTasks}")
        print(f"  Completed: {stage_info.numCompletedTasks}")
        print(f"  Failed: {stage_info.numFailedTasks}")

# Identify data skew
def check_partition_skew(df):
    """Check for partition skew"""
    partition_counts = (df
        .withColumn("partition_id", F.spark_partition_id())
        .groupBy("partition_id")
        .count()
        .orderBy(F.desc("count")))

    partition_counts.show(20)

    stats = partition_counts.select(
        F.min("count").alias("min"),
        F.max("count").alias("max"),
        F.avg("count").alias("avg"),
        F.stddev("count").alias("stddev")
    ).collect()[0]

    skew_ratio = stats["max"] / stats["avg"]
    print(f"Skew ratio: {skew_ratio:.2f}x (>2x indicates skew)")
```

## 配置速查表

```python
# Production configuration template
spark_configs = {
    # Adaptive Query Execution (AQE)
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",

    # Memory
    "spark.executor.memory": "8g",
    "spark.executor.memoryOverhead": "2g",
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.5",

    # Parallelism
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "200",

    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.sql.execution.arrow.pyspark.enabled": "true",

    # Compression
    "spark.io.compression.codec": "lz4",
    "spark.shuffle.compress": "true",

    # Broadcast
    "spark.sql.autoBroadcastJoinThreshold": "50MB",

    # File handling
    "spark.sql.files.maxPartitionBytes": "128MB",
    "spark.sql.files.openCostInBytes": "4MB",
}
```

## 最佳实践

### 应该做的

- **启用 AQE** - 自适应查询执行处理许多问题
- **使用 Parquet/Delta** - 带压缩的列式格式
- **广播小表** - 避免小连接的 shuffle
- **监控 Spark UI** - 检查倾斜、溢出、GC
- **合理设置分区大小** - 每个分区 128MB - 256MB

### 不应该做的

- **不要 collect 大数据** - 保持数据分布式
- **不要不必要地使用 UDF** - 使用内置函数
- **不要过度缓存** - 内存有限
- **不要忽视数据倾斜** - 它主导作业时间
- **不要使用 `.count()` 检查存在性** - 使用 `.take(1)` 或 `.isEmpty()`
