---
name: hybrid-search-implementation
description: 结合向量和关键词搜索以提高检索效果。在实现 RAG 系统、构建搜索引擎，或当单一方法无法提供足够召回率时使用。
---

# 混合搜索实现

结合向量相似性和基于关键词搜索的模式。

## 何时使用此技能

- 构建具有更高召回率的 RAG 系统
- 结合语义理解和精确匹配
- 处理包含特定术语的查询（名称、代码）
- 改善领域特定词汇的搜索
- 当纯向量搜索遗漏关键词匹配时

## 核心概念

### 1. 混合搜索架构

```
查询 → ┬─► 向量搜索 ──► 候选结果 ─┐
       │                            │
       └─► 关键词搜索 ─► 候选结果 ─┴─► 融合 ─► 结果
```

### 2. 融合方法

| 方法              | 描述                         | 最佳适用场景    |
| ----------------- | ---------------------------- | --------------- |
| **RRF**           | 倒数排名融合                 | 通用            |
| **线性**          | 分数加权求和                 | 可调平衡        |
| **交叉编码器**    | 使用神经模型重排             | 最高质量        |
| **级联**          | 先过滤再重排                 | 效率优先        |

## 模板

### 模板 1：倒数排名融合

```python
from typing import List, Dict, Tuple
from collections import defaultdict

def reciprocal_rank_fusion(
    result_lists: List[List[Tuple[str, float]]],
    k: int = 60,
    weights: List[float] = None
) -> List[Tuple[str, float]]:
    """
    使用 RRF 合并多个排名列表。

    参数：
        result_lists: 每种搜索方法的 (doc_id, score) 元组列表
        k: RRF 常数（越大 = 低排名权重越高）
        weights: 每个结果列表的可选权重

    返回：
        融合排名的 (doc_id, score) 元组
    """
    if weights is None:
        weights = [1.0] * len(result_lists)

    scores = defaultdict(float)

    for result_list, weight in zip(result_lists, weights):
        for rank, (doc_id, _) in enumerate(result_list):
            # RRF 公式：1 / (k + rank)
            scores[doc_id] += weight * (1.0 / (k + rank + 1))

    # 按融合分数排序
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def linear_combination(
    vector_results: List[Tuple[str, float]],
    keyword_results: List[Tuple[str, float]],
    alpha: float = 0.5
) -> List[Tuple[str, float]]:
    """
    使用线性插值合并结果。

    参数：
        vector_results: 来自向量搜索的 (doc_id, similarity_score)
        keyword_results: 来自关键词搜索的 (doc_id, bm25_score)
        alpha: 向量搜索权重（1-alpha 为关键词权重）
    """
    # 将分数归一化到 [0, 1]
    def normalize(results):
        if not results:
            return {}
        scores = [s for _, s in results]
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s != min_s else 1
        return {doc_id: (score - min_s) / range_s for doc_id, score in results}

    vector_scores = normalize(vector_results)
    keyword_scores = normalize(keyword_results)

    # 合并
    all_docs = set(vector_scores.keys()) | set(keyword_scores.keys())
    combined = {}

    for doc_id in all_docs:
        v_score = vector_scores.get(doc_id, 0)
        k_score = keyword_scores.get(doc_id, 0)
        combined[doc_id] = alpha * v_score + (1 - alpha) * k_score

    return sorted(combined.items(), key=lambda x: x[1], reverse=True)
```

### 模板 2：PostgreSQL 混合搜索

```python
import asyncpg
from typing import List, Dict, Optional
import numpy as np

class PostgresHybridSearch:
    """使用 pgvector 和全文搜索的混合搜索。"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def setup_schema(self):
        """创建表和索引。"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;

                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB DEFAULT '{}',
                    ts_content tsvector GENERATED ALWAYS AS (
                        to_tsvector('english', content)
                    ) STORED
                );

                -- 向量索引（HNSW）
                CREATE INDEX IF NOT EXISTS documents_embedding_idx
                ON documents USING hnsw (embedding vector_cosine_ops);

                -- 全文索引（GIN）
                CREATE INDEX IF NOT EXISTS documents_fts_idx
                ON documents USING gin (ts_content);
            """)

    async def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        limit: int = 10,
        vector_weight: float = 0.5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        执行结合向量和全文的混合搜索。

        使用 RRF 融合合并结果。
        """
        async with self.pool.acquire() as conn:
            # 构建过滤子句
            where_clause = "1=1"
            params = [query_embedding, query, limit * 3]

            if filter_metadata:
                for key, value in filter_metadata.items():
                    params.append(value)
                    where_clause += f" AND metadata->>'{key}' = ${len(params)}"

            results = await conn.fetch(f"""
                WITH vector_search AS (
                    SELECT
                        id,
                        content,
                        metadata,
                        ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) as vector_rank,
                        1 - (embedding <=> $1::vector) as vector_score
                    FROM documents
                    WHERE {where_clause}
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3
                ),
                keyword_search AS (
                    SELECT
                        id,
                        content,
                        metadata,
                        ROW_NUMBER() OVER (ORDER BY ts_rank(ts_content, websearch_to_tsquery('english', $2)) DESC) as keyword_rank,
                        ts_rank(ts_content, websearch_to_tsquery('english', $2)) as keyword_score
                    FROM documents
                    WHERE ts_content @@ websearch_to_tsquery('english', $2)
                      AND {where_clause}
                    ORDER BY ts_rank(ts_content, websearch_to_tsquery('english', $2)) DESC
                    LIMIT $3
                )
                SELECT
                    COALESCE(v.id, k.id) as id,
                    COALESCE(v.content, k.content) as content,
                    COALESCE(v.metadata, k.metadata) as metadata,
                    v.vector_score,
                    k.keyword_score,
                    -- RRF 融合
                    COALESCE(1.0 / (60 + v.vector_rank), 0) * $4::float +
                    COALESCE(1.0 / (60 + k.keyword_rank), 0) * (1 - $4::float) as rrf_score
                FROM vector_search v
                FULL OUTER JOIN keyword_search k ON v.id = k.id
                ORDER BY rrf_score DESC
                LIMIT $3 / 3
            """, *params, vector_weight)

            return [dict(row) for row in results]

    async def search_with_rerank(
        self,
        query: str,
        query_embedding: List[float],
        limit: int = 10,
        rerank_candidates: int = 50
    ) -> List[Dict]:
        """带交叉编码器重排的混合搜索。"""
        from sentence_transformers import CrossEncoder

        # 获取候选
        candidates = await self.hybrid_search(
            query, query_embedding, limit=rerank_candidates
        )

        if not candidates:
            return []

        # 使用交叉编码器重排
        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        pairs = [(query, c["content"]) for c in candidates]
        scores = model.predict(pairs)

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        # 按重排分数排序并返回顶部结果
        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:limit]
```

### 模板 3：Elasticsearch 混合搜索

```python
from elasticsearch import Elasticsearch
from typing import List, Dict, Optional

class ElasticsearchHybridSearch:
    """使用 Elasticsearch 和稠密向量的混合搜索。"""

    def __init__(
        self,
        es_client: Elasticsearch,
        index_name: str = "documents"
    ):
        self.es = es_client
        self.index_name = index_name

    def create_index(self, vector_dims: int = 1536):
        """创建包含稠密向量和文本字段的索引。"""
        mapping = {
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "analyzer": "english"
                    },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": vector_dims,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "metadata": {
                        "type": "object",
                        "enabled": True
                    }
                }
            }
        }
        self.es.indices.create(index=self.index_name, body=mapping, ignore=400)

    def hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        limit: int = 10,
        boost_vector: float = 1.0,
        boost_text: float = 1.0,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        使用 Elasticsearch 内置功能的混合搜索。
        """
        # 构建混合查询
        search_body = {
            "size": limit,
            "query": {
                "bool": {
                    "should": [
                        # 向量搜索（kNN）
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": f"cosineSimilarity(params.query_vector, 'embedding') * {boost_vector} + 1.0",
                                    "params": {"query_vector": query_embedding}
                                }
                            }
                        },
                        # 文本搜索（BM25）
                        {
                            "match": {
                                "content": {
                                    "query": query,
                                    "boost": boost_text
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        }

        # 如果提供了过滤器则添加
        if filter:
            search_body["query"]["bool"]["filter"] = filter

        response = self.es.search(index=self.index_name, body=search_body)

        return [
            {
                "id": hit["_id"],
                "content": hit["_source"]["content"],
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

    def hybrid_search_rrf(
        self,
        query: str,
        query_embedding: List[float],
        limit: int = 10,
        window_size: int = 100
    ) -> List[Dict]:
        """
        使用 Elasticsearch 8.x RRF 的混合搜索。
        """
        search_body = {
            "size": limit,
            "sub_searches": [
                {
                    "query": {
                        "match": {
                            "content": query
                        }
                    }
                },
                {
                    "query": {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_embedding,
                            "k": window_size,
                            "num_candidates": window_size * 2
                        }
                    }
                }
            ],
            "rank": {
                "rrf": {
                    "window_size": window_size,
                    "rank_constant": 60
                }
            }
        }

        response = self.es.search(index=self.index_name, body=search_body)

        return [
            {
                "id": hit["_id"],
                "content": hit["_source"]["content"],
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
```

### 模板 4：自定义混合 RAG 管道

```python
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass

@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    source: str  # "vector"、"keyword"、"hybrid"
    metadata: Dict = None


class HybridRAGPipeline:
    """用于 RAG 的完整混合搜索管道。"""

    def __init__(
        self,
        vector_store,
        keyword_store,
        embedder,
        reranker=None,
        fusion_method: str = "rrf",
        vector_weight: float = 0.5
    ):
        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.embedder = embedder
        self.reranker = reranker
        self.fusion_method = fusion_method
        self.vector_weight = vector_weight

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict] = None,
        use_rerank: bool = True
    ) -> List[SearchResult]:
        """执行混合搜索管道。"""

        # 步骤 1：获取查询嵌入
        query_embedding = self.embedder.embed(query)

        # 步骤 2：执行并行搜索
        vector_results, keyword_results = await asyncio.gather(
            self._vector_search(query_embedding, top_k * 3, filter),
            self._keyword_search(query, top_k * 3, filter)
        )

        # 步骤 3：融合结果
        if self.fusion_method == "rrf":
            fused = self._rrf_fusion(vector_results, keyword_results)
        else:
            fused = self._linear_fusion(vector_results, keyword_results)

        # 步骤 4：如果启用则重排
        if use_rerank and self.reranker:
            fused = await self._rerank(query, fused[:top_k * 2])

        return fused[:top_k]

    async def _vector_search(
        self,
        embedding: List[float],
        limit: int,
        filter: Dict
    ) -> List[SearchResult]:
        results = await self.vector_store.search(embedding, limit, filter)
        return [
            SearchResult(
                id=r["id"],
                content=r["content"],
                score=r["score"],
                source="vector",
                metadata=r.get("metadata")
            )
            for r in results
        ]

    async def _keyword_search(
        self,
        query: str,
        limit: int,
        filter: Dict
    ) -> List[SearchResult]:
        results = await self.keyword_store.search(query, limit, filter)
        return [
            SearchResult(
                id=r["id"],
                content=r["content"],
                score=r["score"],
                source="keyword",
                metadata=r.get("metadata")
            )
            for r in results
        ]

    def _rrf_fusion(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult]
    ) -> List[SearchResult]:
        """使用 RRF 融合。"""
        k = 60
        scores = {}
        content_map = {}

        for rank, result in enumerate(vector_results):
            scores[result.id] = scores.get(result.id, 0) + 1 / (k + rank + 1)
            content_map[result.id] = result

        for rank, result in enumerate(keyword_results):
            scores[result.id] = scores.get(result.id, 0) + 1 / (k + rank + 1)
            if result.id not in content_map:
                content_map[result.id] = result

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        return [
            SearchResult(
                id=doc_id,
                content=content_map[doc_id].content,
                score=scores[doc_id],
                source="hybrid",
                metadata=content_map[doc_id].metadata
            )
            for doc_id in sorted_ids
        ]

    async def _rerank(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """使用交叉编码器重排。"""
        if not results:
            return results

        pairs = [(query, r.content) for r in results]
        scores = self.reranker.predict(pairs)

        for result, score in zip(results, scores):
            result.score = float(score)

        return sorted(results, key=lambda x: x.score, reverse=True)
```

## 最佳实践

### 应该做的

- **凭经验调优权重** - 在你的数据上测试
- **使用 RRF 以获得简洁性** - 无需调优即可良好工作
- **添加重排** - 显著提升质量
- **记录两个分数** - 有助于调试
- **A/B 测试** - 衡量真实用户影响

### 不应该做的

- **不要假设一刀切** - 不同查询需要不同权重
- **不要跳过关键词搜索** - 更好地处理精确匹配
- **不要过度获取** - 平衡召回率与延迟
- **不要忽略边界情况** - 空结果、单词查询
