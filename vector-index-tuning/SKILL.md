---
name: vector-index-tuning
description: 优化向量索引性能，包括延迟、召回率和内存。适用于调优 HNSW 参数、选择量化策略或扩展向量搜索基础设施。
---

# 向量索引调优

优化向量索引以获得生产性能的指南。

## 何时使用此技能

- 调优 HNSW 参数
- 实现量化
- 优化内存使用
- 降低搜索延迟
- 平衡召回率与速度
- 扩展到数十亿向量

## 核心概念

### 1. 索引类型选择

```
数据大小           推荐索引
────────────────────────────────────────
< 10K 向量  →    Flat（精确搜索）
10K - 1M       →    HNSW
1M - 100M      →    HNSW + 量化
> 100M         →    IVF + PQ 或 DiskANN
```

### 2. HNSW 参数

| 参数          | 默认值 | 效果                                               |
| ------------------ | ------- | ---------------------------------------------------- |
| **M**              | 16      | 每个节点的连接数，↑ = 更好的召回率，更多内存 |
| **efConstruction** | 100     | 构建质量，↑ = 更好的索引，更慢的构建        |
| **efSearch**       | 50      | 搜索质量，↑ = 更好的召回率，更慢的搜索     |

### 3. 量化类型

```
全精度 (FP32): 4 字节 × 维度
半精度 (FP16): 2 字节 × 维度
INT8 标量:           1 字节 × 维度
乘积量化:  ~32-64 字节总计
二进制:                维度/8 字节
```

## 模板

### 模板 1：HNSW 参数调优

```python
import numpy as np
from typing import List, Tuple
import time

def benchmark_hnsw_parameters(
    vectors: np.ndarray,
    queries: np.ndarray,
    ground_truth: np.ndarray,
    m_values: List[int] = [8, 16, 32, 64],
    ef_construction_values: List[int] = [64, 128, 256],
    ef_search_values: List[int] = [32, 64, 128, 256]
) -> List[dict]:
    """对不同的 HNSW 配置进行基准测试。"""
    import hnswlib

    results = []
    dim = vectors.shape[1]
    n = vectors.shape[0]

    for m in m_values:
        for ef_construction in ef_construction_values:
            # 构建索引
            index = hnswlib.Index(space='cosine', dim=dim)
            index.init_index(max_elements=n, M=m, ef_construction=ef_construction)

            build_start = time.time()
            index.add_items(vectors)
            build_time = time.time() - build_start

            # 获取内存使用
            memory_bytes = index.element_count * (
                dim * 4 +  # 向量存储
                m * 2 * 4  # 图边（近似）
            )

            for ef_search in ef_search_values:
                index.set_ef(ef_search)

                # 测量搜索
                search_start = time.time()
                labels, distances = index.knn_query(queries, k=10)
                search_time = time.time() - search_start

                # 计算召回率
                recall = calculate_recall(labels, ground_truth, k=10)

                results.append({
                    "M": m,
                    "ef_construction": ef_construction,
                    "ef_search": ef_search,
                    "build_time_s": build_time,
                    "search_time_ms": search_time * 1000 / len(queries),
                    "recall@10": recall,
                    "memory_mb": memory_bytes / 1024 / 1024
                })

    return results


def calculate_recall(predictions: np.ndarray, ground_truth: np.ndarray, k: int) -> float:
    """计算 recall@k。"""
    correct = 0
    for pred, truth in zip(predictions, ground_truth):
        correct += len(set(pred[:k]) & set(truth[:k]))
    return correct / (len(predictions) * k)


def recommend_hnsw_params(
    num_vectors: int,
    target_recall: float = 0.95,
    max_latency_ms: float = 10,
    available_memory_gb: float = 8
) -> dict:
    """根据需求推荐 HNSW 参数。"""

    # 基础推荐
    if num_vectors < 100_000:
        m = 16
        ef_construction = 100
    elif num_vectors < 1_000_000:
        m = 32
        ef_construction = 200
    else:
        m = 48
        ef_construction = 256

    # 根据召回率目标调整 ef_search
    if target_recall >= 0.99:
        ef_search = 256
    elif target_recall >= 0.95:
        ef_search = 128
    else:
        ef_search = 64

    return {
        "M": m,
        "ef_construction": ef_construction,
        "ef_search": ef_search,
        "notes": f"预估 {num_vectors:,} 个向量，{target_recall:.0%} 召回率"
    }
```

### 模板 2：量化策略

```python
import numpy as np
from typing import Optional

class VectorQuantizer:
    """向量压缩的量化策略。"""

    @staticmethod
    def scalar_quantize_int8(
        vectors: np.ndarray,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> Tuple[np.ndarray, dict]:
        """标量量化到 INT8。"""
        if min_val is None:
            min_val = vectors.min()
        if max_val is None:
            max_val = vectors.max()

        # 缩放到 0-255 范围
        scale = 255.0 / (max_val - min_val)
        quantized = np.clip(
            np.round((vectors - min_val) * scale),
            0, 255
        ).astype(np.uint8)

        params = {"min_val": min_val, "max_val": max_val, "scale": scale}
        return quantized, params

    @staticmethod
    def dequantize_int8(
        quantized: np.ndarray,
        params: dict
    ) -> np.ndarray:
        """反量化 INT8 向量。"""
        return quantized.astype(np.float32) / params["scale"] + params["min_val"]

    @staticmethod
    def product_quantize(
        vectors: np.ndarray,
        n_subvectors: int = 8,
        n_centroids: int = 256
    ) -> Tuple[np.ndarray, dict]:
        """乘积量化用于激进压缩。"""
        from sklearn.cluster import KMeans

        n, dim = vectors.shape
        assert dim % n_subvectors == 0
        subvector_dim = dim // n_subvectors

        codebooks = []
        codes = np.zeros((n, n_subvectors), dtype=np.uint8)

        for i in range(n_subvectors):
            start = i * subvector_dim
            end = (i + 1) * subvector_dim
            subvectors = vectors[:, start:end]

            kmeans = KMeans(n_clusters=n_centroids, random_state=42)
            codes[:, i] = kmeans.fit_predict(subvectors)
            codebooks.append(kmeans.cluster_centers_)

        params = {
            "codebooks": codebooks,
            "n_subvectors": n_subvectors,
            "subvector_dim": subvector_dim
        }
        return codes, params

    @staticmethod
    def binary_quantize(vectors: np.ndarray) -> np.ndarray:
        """二进制量化（每个维度的符号）。"""
        # 转换为二进制：正数 = 1，负数 = 0
        binary = (vectors > 0).astype(np.uint8)

        # 将位打包为字节
        n, dim = vectors.shape
        packed_dim = (dim + 7) // 8

        packed = np.zeros((n, packed_dim), dtype=np.uint8)
        for i in range(dim):
            byte_idx = i // 8
            bit_idx = i % 8
            packed[:, byte_idx] |= (binary[:, i] << bit_idx)

        return packed


def estimate_memory_usage(
    num_vectors: int,
    dimensions: int,
    quantization: str = "fp32",
    index_type: str = "hnsw",
    hnsw_m: int = 16
) -> dict:
    """估算不同配置的内存使用。"""

    # 向量存储
    bytes_per_dimension = {
        "fp32": 4,
        "fp16": 2,
        "int8": 1,
        "pq": 0.05,  # 近似
        "binary": 0.125
    }

    vector_bytes = num_vectors * dimensions * bytes_per_dimension[quantization]

    # 索引开销
    if index_type == "hnsw":
        # 每个节点有 ~M*2 条边，每条边 4 字节（int32）
        index_bytes = num_vectors * hnsw_m * 2 * 4
    elif index_type == "ivf":
        # 倒排列表 + 聚类中心
        index_bytes = num_vectors * 8 + 65536 * dimensions * 4
    else:
        index_bytes = 0

    total_bytes = vector_bytes + index_bytes

    return {
        "vector_storage_mb": vector_bytes / 1024 / 1024,
        "index_overhead_mb": index_bytes / 1024 / 1024,
        "total_mb": total_bytes / 1024 / 1024,
        "total_gb": total_bytes / 1024 / 1024 / 1024
    }
```

### 模板 3：Qdrant 索引配置

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

def create_optimized_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    num_vectors: int,
    optimize_for: str = "balanced"  # "recall"、"speed"、"memory"
) -> None:
    """创建带优化设置的集合。"""

    # 基于优化目标的 HNSW 配置
    hnsw_configs = {
        "recall": models.HnswConfigDiff(m=32, ef_construct=256),
        "speed": models.HnswConfigDiff(m=16, ef_construct=64),
        "balanced": models.HnswConfigDiff(m=16, ef_construct=128),
        "memory": models.HnswConfigDiff(m=8, ef_construct=64)
    }

    # 量化配置
    quantization_configs = {
        "recall": None,  # 最大召回率不使用量化
        "speed": models.ScalarQuantization(
            scalar=models.ScalarQuantizationConfig(
                type=models.ScalarType.INT8,
                quantile=0.99,
                always_ram=True
            )
        ),
        "balanced": models.ScalarQuantization(
            scalar=models.ScalarQuantizationConfig(
                type=models.ScalarType.INT8,
                quantile=0.99,
                always_ram=False
            )
        ),
        "memory": models.ProductQuantization(
            product=models.ProductQuantizationConfig(
                compression=models.CompressionRatio.X16,
                always_ram=False
            )
        )
    }

    # 优化器配置
    optimizer_configs = {
        "recall": models.OptimizersConfigDiff(
            indexing_threshold=10000,
            memmap_threshold=50000
        ),
        "speed": models.OptimizersConfigDiff(
            indexing_threshold=5000,
            memmap_threshold=20000
        ),
        "balanced": models.OptimizersConfigDiff(
            indexing_threshold=20000,
            memmap_threshold=50000
        ),
        "memory": models.OptimizersConfigDiff(
            indexing_threshold=50000,
            memmap_threshold=10000  # 更早使用磁盘
        )
    }

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE
        ),
        hnsw_config=hnsw_configs[optimize_for],
        quantization_config=quantization_configs[optimize_for],
        optimizers_config=optimizer_configs[optimize_for]
    )


def tune_search_parameters(
    client: QdrantClient,
    collection_name: str,
    target_recall: float = 0.95
) -> dict:
    """为目标召回率调优搜索参数。"""

    # 搜索参数推荐
    if target_recall >= 0.99:
        search_params = models.SearchParams(
            hnsw_ef=256,
            exact=False,
            quantization=models.QuantizationSearchParams(
                ignore=True,  # 搜索时不使用量化
                rescore=True
            )
        )
    elif target_recall >= 0.95:
        search_params = models.SearchParams(
            hnsw_ef=128,
            exact=False,
            quantization=models.QuantizationSearchParams(
                ignore=False,
                rescore=True,
                oversampling=2.0
            )
        )
    else:
        search_params = models.SearchParams(
            hnsw_ef=64,
            exact=False,
            quantization=models.QuantizationSearchParams(
                ignore=False,
                rescore=False
            )
        )

    return search_params
```

### 模板 4：性能监控

```python
import time
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class SearchMetrics:
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    recall: float
    qps: float


class VectorSearchMonitor:
    """监控向量搜索性能。"""

    def __init__(self, ground_truth_fn=None):
        self.latencies = []
        self.recalls = []
        self.ground_truth_fn = ground_truth_fn

    def measure_search(
        self,
        search_fn,
        query_vectors: np.ndarray,
        k: int = 10,
        num_iterations: int = 100
    ) -> SearchMetrics:
        """对搜索性能进行基准测试。"""
        latencies = []

        for _ in range(num_iterations):
            for query in query_vectors:
                start = time.perf_counter()
                results = search_fn(query, k=k)
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)

        latencies = np.array(latencies)
        total_queries = num_iterations * len(query_vectors)
        total_time = sum(latencies) / 1000  # 秒

        return SearchMetrics(
            latency_p50_ms=np.percentile(latencies, 50),
            latency_p95_ms=np.percentile(latencies, 95),
            latency_p99_ms=np.percentile(latencies, 99),
            recall=self._calculate_recall(search_fn, query_vectors, k) if self.ground_truth_fn else 0,
            qps=total_queries / total_time
        )

    def _calculate_recall(self, search_fn, queries: np.ndarray, k: int) -> float:
        """根据真实值计算召回率。"""
        if not self.ground_truth_fn:
            return 0

        correct = 0
        total = 0

        for query in queries:
            predicted = set(search_fn(query, k=k))
            actual = set(self.ground_truth_fn(query, k=k))
            correct += len(predicted & actual)
            total += k

        return correct / total


def profile_index_build(
    build_fn,
    vectors: np.ndarray,
    batch_sizes: List[int] = [1000, 10000, 50000]
) -> dict:
    """分析索引构建性能。"""
    results = {}

    for batch_size in batch_sizes:
        times = []
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            start = time.perf_counter()
            build_fn(batch)
            times.append(time.perf_counter() - start)

        results[batch_size] = {
            "avg_batch_time_s": np.mean(times),
            "vectors_per_second": batch_size / np.mean(times)
        }

    return results
```

## 最佳实践

### 应该做的

- **使用真实查询进行基准测试** - 合成数据可能不代表生产环境
- **持续监控召回率** - 数据漂移可能导致退化
- **从默认值开始** - 仅在需要时调优
- **使用量化** - 显著节省内存
- **考虑分层存储** - 热/冷数据分离

### 不应该做的

- **不要过早过度优化** - 先分析
- **不要忽略构建时间** - 索引更新有成本
- **不要忘记重建索引** - 规划维护
- **不要跳过预热** - 冷索引很慢
