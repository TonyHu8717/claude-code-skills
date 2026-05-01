---
name: similarity-search-patterns
description: 使用向量数据库实现高效的相似性搜索。在构建语义搜索、实现最近邻查询或优化检索性能时使用。
---

# 相似性搜索模式

在生产系统中实现高效相似性搜索的模式。

## 何时使用此技能

- 构建语义搜索系统
- 实现 RAG 检索
- 创建推荐引擎
- 优化搜索延迟
- 扩展到数百万向量
- 组合语义和关键词搜索

## 核心概念

### 1. 距离度量

| 度量             | 公式               | 最适用于              |
| ---------------- | ------------------ | --------------------- |
| **余弦**         | 1 - (A·B)/(‖A‖‖B‖) | 归一化嵌入            |
| **欧几里得 (L2)** | √Σ(a-b)²           | 原始嵌入              |
| **点积**         | A·B                | 大小很重要            |
| **曼哈顿 (L1)**  | Σ|a-b|             | 稀疏向量              |

### 2. 索引类型

```
┌─────────────────────────────────────────────────┐
│                 索引类型                          │
├─────────────┬───────────────┬───────────────────┤
│    Flat     │     HNSW      │    IVF+PQ         │
│ (精确)      │ (基于图)      │ (量化)            │
├─────────────┼───────────────┼───────────────────┤
│ O(n) 搜索   │ O(log n)      │ O(√n)             │
│ 100% 召回率 │ ~95-99%       │ ~90-95%           │
│ 小数据      │ 中大型        │ 超大型            │
└─────────────┴───────────────┴───────────────────┘
```

## 模板

### 模板 1：Pinecone 实现

```python
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
import hashlib

class PineconeVectorStore:
    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        metric: str = "cosine"
    ):
        self.pc = Pinecone(api_key=api_key)

        # Create index if not exists
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = self.pc.Index(index_name)

    def upsert(
        self,
        vectors: List[Dict],
        namespace: str = ""
    ) -> int:
        """
        Upsert vectors.
        vectors: [{"id": str, "values": List[float], "metadata": dict}]
        """
        # Batch upsert
        batch_size = 100
        total = 0

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
            total += len(batch)

        return total

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        namespace: str = "",
        filter: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """Search for similar vectors."""
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata
        )

        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]

    def search_with_rerank(
        self,
        query: str,
        query_vector: List[float],
        top_k: int = 10,
        rerank_top_n: int = 50,
        namespace: str = ""
    ) -> List[Dict]:
        """Search and rerank results."""
        # Over-fetch for reranking
        initial_results = self.search(
            query_vector,
            top_k=rerank_top_n,
            namespace=namespace
        )

        # Rerank with cross-encoder or LLM
        reranked = self._rerank(query, initial_results)

        return reranked[:top_k]

    def _rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using cross-encoder."""
        from sentence_transformers import CrossEncoder

        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        pairs = [(query, r["metadata"]["text"]) for r in results]
        scores = model.predict(pairs)

        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        return sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    def delete(self, ids: List[str], namespace: str = ""):
        """Delete vectors by ID."""
        self.index.delete(ids=ids, namespace=namespace)

    def delete_by_filter(self, filter: Dict, namespace: str = ""):
        """Delete vectors matching filter."""
        self.index.delete(filter=filter, namespace=namespace)
```

### 模板 2：Qdrant 实现

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional

class QdrantVectorStore:
    def __init__(
        self,
        url: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        vector_size: int = 1536
    ):
        self.client = QdrantClient(url=url, port=port)
        self.collection_name = collection_name

        # Create collection if not exists
        collections = self.client.get_collections().collections
        if collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                ),
                # Optional: enable quantization for memory efficiency
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=0.99,
                        always_ram=True
                    )
                )
            )

    def upsert(self, points: List[Dict]) -> int:
        """
        Upsert points.
        points: [{"id": str/int, "vector": List[float], "payload": dict}]
        """
        qdrant_points = [
            models.PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p.get("payload", {})
            )
            for p in points
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=qdrant_points
        )
        return len(points)

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter: Optional[models.Filter] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """Search for similar vectors."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter,
            score_threshold=score_threshold
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload
            }
            for r in results
        ]

    def search_with_filter(
        self,
        query_vector: List[float],
        must_conditions: List[Dict] = None,
        should_conditions: List[Dict] = None,
        must_not_conditions: List[Dict] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search with complex filters."""
        conditions = []

        if must_conditions:
            conditions.extend([
                models.FieldCondition(
                    key=c["key"],
                    match=models.MatchValue(value=c["value"])
                )
                for c in must_conditions
            ])

        filter = models.Filter(must=conditions) if conditions else None

        return self.search(query_vector, limit=limit, filter=filter)

    def search_with_sparse(
        self,
        dense_vector: List[float],
        sparse_vector: Dict[int, float],
        limit: int = 10,
        dense_weight: float = 0.7
    ) -> List[Dict]:
        """Hybrid search with dense and sparse vectors."""
        # Requires collection with named vectors
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=models.NamedVector(
                name="dense",
                vector=dense_vector
            ),
            limit=limit
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]
```

### 模板 3：pgvector 与 PostgreSQL

```python
import asyncpg
from typing import List, Dict, Optional
import numpy as np

class PgVectorStore:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def init(self):
        """Initialize connection pool and extension."""
        self.pool = await asyncpg.create_pool(self.connection_string)

        async with self.pool.acquire() as conn:
            # Enable extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    metadata JSONB,
                    embedding vector(1536)
                )
            """)

            # Create index (HNSW for better performance)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_embedding_idx
                ON documents
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)

    async def upsert(self, documents: List[Dict]):
        """Upsert documents with embeddings."""
        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO documents (id, content, metadata, embedding)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
                """,
                [
                    (
                        doc["id"],
                        doc["content"],
                        doc.get("metadata", {}),
                        np.array(doc["embedding"]).tolist()
                    )
                    for doc in documents
                ]
            )

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents."""
        query = """
            SELECT id, content, metadata,
                   1 - (embedding <=> $1::vector) as similarity
            FROM documents
        """

        params = [query_embedding]

        if filter_metadata:
            conditions = []
            for key, value in filter_metadata.items():
                params.append(value)
                conditions.append(f"metadata->>'{key}' = ${len(params)}")
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY embedding <=> $1::vector LIMIT ${len(params) + 1}"
        params.append(limit)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [
            {
                "id": row["id"],
                "content": row["content"],
                "metadata": row["metadata"],
                "score": row["similarity"]
            }
            for row in rows
        ]

    async def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        limit: int = 10,
        vector_weight: float = 0.5
    ) -> List[Dict]:
        """Hybrid search combining vector and full-text."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                WITH vector_results AS (
                    SELECT id, content, metadata,
                           1 - (embedding <=> $1::vector) as vector_score
                    FROM documents
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3 * 2
                ),
                text_results AS (
                    SELECT id, content, metadata,
                           ts_rank(to_tsvector('english', content),
                                   plainto_tsquery('english', $2)) as text_score
                    FROM documents
                    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $2)
                    LIMIT $3 * 2
                )
                SELECT
                    COALESCE(v.id, t.id) as id,
                    COALESCE(v.content, t.content) as content,
                    COALESCE(v.metadata, t.metadata) as metadata,
                    COALESCE(v.vector_score, 0) * $4 +
                    COALESCE(t.text_score, 0) * (1 - $4) as combined_score
                FROM vector_results v
                FULL OUTER JOIN text_results t ON v.id = t.id
                ORDER BY combined_score DESC
                LIMIT $3
                """,
                query_embedding, query_text, limit, vector_weight
            )

        return [dict(row) for row in rows]
```

### 模板 4：Weaviate 实现

```python
import weaviate
from weaviate.util import generate_uuid5
from typing import List, Dict, Optional

class WeaviateVectorStore:
    def __init__(
        self,
        url: str = "http://localhost:8080",
        class_name: str = "Document"
    ):
        self.client = weaviate.Client(url=url)
        self.class_name = class_name
        self._ensure_schema()

    def _ensure_schema(self):
        """Create schema if not exists."""
        schema = {
            "class": self.class_name,
            "vectorizer": "none",  # We provide vectors
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["string"]},
                {"name": "chunk_id", "dataType": ["int"]}
            ]
        }

        if not self.client.schema.exists(self.class_name):
            self.client.schema.create_class(schema)

    def upsert(self, documents: List[Dict]):
        """Batch upsert documents."""
        with self.client.batch as batch:
            batch.batch_size = 100

            for doc in documents:
                batch.add_data_object(
                    data_object={
                        "content": doc["content"],
                        "source": doc.get("source", ""),
                        "chunk_id": doc.get("chunk_id", 0)
                    },
                    class_name=self.class_name,
                    uuid=generate_uuid5(doc["id"]),
                    vector=doc["embedding"]
                )

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        where_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Vector search."""
        query = (
            self.client.query
            .get(self.class_name, ["content", "source", "chunk_id"])
            .with_near_vector({"vector": query_vector})
            .with_limit(limit)
            .with_additional(["distance", "id"])
        )

        if where_filter:
            query = query.with_where(where_filter)

        results = query.do()

        return [
            {
                "id": item["_additional"]["id"],
                "content": item["content"],
                "source": item["source"],
                "score": 1 - item["_additional"]["distance"]
            }
            for item in results["data"]["Get"][self.class_name]
        ]

    def hybrid_search(
        self,
        query: str,
        query_vector: List[float],
        limit: int = 10,
        alpha: float = 0.5  # 0 = keyword, 1 = vector
    ) -> List[Dict]:
        """Hybrid search combining BM25 and vector."""
        results = (
            self.client.query
            .get(self.class_name, ["content", "source"])
            .with_hybrid(query=query, vector=query_vector, alpha=alpha)
            .with_limit(limit)
            .with_additional(["score"])
            .do()
        )

        return [
            {
                "content": item["content"],
                "source": item["source"],
                "score": item["_additional"]["score"]
            }
            for item in results["data"]["Get"][self.class_name]
        ]
```

## 最佳实践

### 应该做的

- **使用适当的索引** - 大多数情况下使用 HNSW
- **调优参数** - ef_search、nprobe 用于召回率/速度
- **实现混合搜索** - 与关键词搜索组合
- **监控召回率** - 衡量搜索质量
- **尽可能预过滤** - 减少搜索空间

### 不应该做的

- **不要跳过评估** - 优化前先衡量
- **不要过度索引** - 从 flat 开始，逐步扩展
- **不要忽视延迟** - P99 对用户体验很重要
- **不要忘记成本** - 向量存储会累积
