---
name: embedding-strategies
description: 为语义搜索和 RAG 应用选择和优化嵌入模型。在选择嵌入模型、实现分块策略或为特定领域优化嵌入质量时使用。
---

# 嵌入策略

为向量搜索应用选择和优化嵌入模型的指南。

## 何时使用此技能

- 为 RAG 选择嵌入模型
- 优化分块策略
- 为领域微调嵌入
- 比较嵌入模型性能
- 降低嵌入维度
- 处理多语言内容

## 核心概念

### 1. 嵌入模型比较（2026）

| 模型                      | 维度 | 最大令牌数 | 最适合                            |
| -------------------------- | ---------- | ---------- | ----------------------------------- |
| **voyage-3-large**         | 1024       | 32000      | Claude 应用（Anthropic 推荐）|
| **voyage-3**               | 1024       | 32000      | Claude 应用，性价比高         |
| **voyage-code-3**          | 1024       | 32000      | 代码搜索                         |
| **voyage-finance-2**       | 1024       | 32000      | 金融文档                 |
| **voyage-law-2**           | 1024       | 32000      | 法律文档                     |
| **text-embedding-3-large** | 3072       | 8191       | OpenAI 应用，高精度          |
| **text-embedding-3-small** | 1536       | 8191       | OpenAI 应用，性价比高         |
| **bge-large-en-v1.5**      | 1024       | 512        | 开源，本地部署       |
| **all-MiniLM-L6-v2**       | 384        | 256        | 快速，轻量                   |
| **multilingual-e5-large**  | 1024       | 512        | 多语言                      |

### 2. 嵌入管道

```
文档 → 分块 → 预处理 → 嵌入模型 → 向量
              ↓
      [重叠, 大小]  [清理, 标准化]  [API/本地]
```

## 模板

### 模板 1：Voyage AI 嵌入（Claude 推荐）

```python
from langchain_voyageai import VoyageAIEmbeddings
from typing import List
import os

# 初始化 Voyage AI 嵌入（Anthropic 为 Claude 推荐）
embeddings = VoyageAIEmbeddings(
    model="voyage-3-large",
    voyage_api_key=os.environ.get("VOYAGE_API_KEY")
)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """从 Voyage AI 获取嵌入。"""
    return embeddings.embed_documents(texts)

def get_query_embedding(query: str) -> List[float]:
    """获取单个查询嵌入。"""
    return embeddings.embed_query(query)

# 领域专用模型
code_embeddings = VoyageAIEmbeddings(model="voyage-code-3")
finance_embeddings = VoyageAIEmbeddings(model="voyage-finance-2")
legal_embeddings = VoyageAIEmbeddings(model="voyage-law-2")
```

### 模板 2：OpenAI 嵌入

```python
from openai import OpenAI
from typing import List
import numpy as np

client = OpenAI()

def get_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    dimensions: int = None
) -> List[List[float]]:
    """从 OpenAI 获取嵌入，支持可选的维度降低。"""
    # 处理大列表的批处理
    batch_size = 100
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        kwargs = {"input": batch, "model": model}
        if dimensions:
            # Matryoshka 维度降低
            kwargs["dimensions"] = dimensions

        response = client.embeddings.create(**kwargs)
        embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(embeddings)

    return all_embeddings


def get_embedding(text: str, **kwargs) -> List[float]:
    """获取单个嵌入。"""
    return get_embeddings([text], **kwargs)[0]


# 使用 Matryoshka 嵌入降低维度
def get_reduced_embedding(text: str, dimensions: int = 512) -> List[float]:
    """获取降低维度的嵌入（Matryoshka）。"""
    return get_embedding(
        text,
        model="text-embedding-3-small",
        dimensions=dimensions
    )
```

### 模板 3：使用 Sentence Transformers 的本地嵌入

```python
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np

class LocalEmbedder:
    """使用 sentence-transformers 的本地嵌入。"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        device: str = "cuda"
    ):
        self.model = SentenceTransformer(model_name, device=device)
        self.model_name = model_name

    def embed(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """嵌入文本，支持可选标准化。"""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """嵌入查询，为检索模型添加适当的前缀。"""
        # BGE 和类似模型受益于查询前缀
        if "bge" in self.model_name.lower():
            query = f"Represent this sentence for searching relevant passages: {query}"
        return self.embed([query])[0]

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """嵌入文档用于索引。"""
        return self.embed(documents)


# 带指令的 E5 模型
class E5Embedder:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large"):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, query: str) -> np.ndarray:
        """E5 查询需要 'query:' 前缀。"""
        return self.model.encode(f"query: {query}")

    def embed_document(self, document: str) -> np.ndarray:
        """E5 文档需要 'passage:' 前缀。"""
        return self.model.encode(f"passage: {document}")
```

### 模板 4：分块策略

```python
from typing import List, Tuple
import re

def chunk_by_tokens(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    tokenizer=None
) -> List[str]:
    """按令牌数分块文本。"""
    import tiktoken
    tokenizer = tokenizer or tiktoken.get_encoding("cl100k_base")

    tokens = tokenizer.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end - chunk_overlap

    return chunks


def chunk_by_sentences(
    text: str,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 100
) -> List[str]:
    """按句子分块文本，遵守大小限制。"""
    import nltk
    sentences = nltk.sent_tokenize(text)

    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        if current_size + sentence_size > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(sentence)
        current_size += sentence_size

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_by_semantic_sections(
    text: str,
    headers_pattern: str = r'^#{1,3}\s+.+$'
) -> List[Tuple[str, str]]:
    """按标题分块 markdown，保留层次结构。"""
    lines = text.split('\n')
    chunks = []
    current_header = ""
    current_content = []

    for line in lines:
        if re.match(headers_pattern, line, re.MULTILINE):
            if current_content:
                chunks.append((current_header, '\n'.join(current_content)))
            current_header = line
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        chunks.append((current_header, '\n'.join(current_content)))

    return chunks


def recursive_character_splitter(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: List[str] = None
) -> List[str]:
    """LangChain 风格的递归分割器。"""
    separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(text: str, separators: List[str]) -> List[str]:
        if not text:
            return []

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            # 字符级分割
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]

        splits = text.split(separator)
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split) + len(separator)

            if current_length + split_length > chunk_size and current_chunk:
                chunk_text = separator.join(current_chunk)

                # 如果仍然太大则递归分割
                if len(chunk_text) > chunk_size and remaining_separators:
                    chunks.extend(split_text(chunk_text, remaining_separators))
                else:
                    chunks.append(chunk_text)

                # 带重叠开始新块
                overlap_splits = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= chunk_overlap:
                        overlap_splits.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                current_chunk = overlap_splits
                current_length = overlap_length

            current_chunk.append(split)
            current_length += split_length

        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return chunks

    return split_text(text, separators)
```

### 模板 5：领域专用嵌入管道

```python
import re
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class EmbeddedDocument:
    id: str
    document_id: str
    chunk_index: int
    text: str
    embedding: List[float]
    metadata: dict

class DomainEmbeddingPipeline:
    """领域专用嵌入管道。"""

    def __init__(
        self,
        embedding_model: str = "voyage-3-large",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        preprocessing_fn=None
    ):
        self.embeddings = VoyageAIEmbeddings(model=embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.preprocess = preprocessing_fn or self._default_preprocess

    def _default_preprocess(self, text: str) -> str:
        """默认预处理。"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（根据您的领域自定义）
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    async def process_documents(
        self,
        documents: List[dict],
        id_field: str = "id",
        content_field: str = "content",
        metadata_fields: Optional[List[str]] = None
    ) -> List[EmbeddedDocument]:
        """处理文档用于向量存储。"""
        processed = []

        for doc in documents:
            content = doc[content_field]
            doc_id = doc[id_field]

            # 预处理
            cleaned = self.preprocess(content)

            # 分块
            chunks = chunk_by_tokens(
                cleaned,
                self.chunk_size,
                self.chunk_overlap
            )

            # 创建嵌入
            embeddings = await self.embeddings.aembed_documents(chunks)

            # 创建记录
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                metadata = {"document_id": doc_id, "chunk_index": i}

                # 添加指定的元数据字段
                if metadata_fields:
                    for field in metadata_fields:
                        if field in doc:
                            metadata[field] = doc[field]

                processed.append(EmbeddedDocument(
                    id=f"{doc_id}_chunk_{i}",
                    document_id=doc_id,
                    chunk_index=i,
                    text=chunk,
                    embedding=embedding,
                    metadata=metadata
                ))

        return processed


# 代码专用管道
class CodeEmbeddingPipeline:
    """代码嵌入专用管道。"""

    def __init__(self):
        # 使用 Voyage 的代码专用模型
        self.embeddings = VoyageAIEmbeddings(model="voyage-code-3")

    def chunk_code(self, code: str, language: str) -> List[dict]:
        """使用 tree-sitter 按函数/类分块代码。"""
        try:
            import tree_sitter_languages
            parser = tree_sitter_languages.get_parser(language)
            tree = parser.parse(bytes(code, "utf8"))

            chunks = []
            # 提取函数和类定义
            self._extract_nodes(tree.root_node, code, chunks)
            return chunks
        except ImportError:
            # 回退到简单分块
            return [{"text": code, "type": "module"}]

    def _extract_nodes(self, node, source_code: str, chunks: list):
        """递归提取函数/类定义。"""
        if node.type in ['function_definition', 'class_definition', 'method_definition']:
            text = source_code[node.start_byte:node.end_byte]
            chunks.append({
                "text": text,
                "type": node.type,
                "name": self._get_name(node),
                "start_line": node.start_point[0],
                "end_line": node.end_point[0]
            })
        for child in node.children:
            self._extract_nodes(child, source_code, chunks)

    def _get_name(self, node) -> str:
        """从函数/类节点提取名称。"""
        for child in node.children:
            if child.type == 'identifier' or child.type == 'name':
                return child.text.decode('utf8')
        return "unknown"

    async def embed_with_context(
        self,
        chunk: str,
        context: str = ""
    ) -> List[float]:
        """带上下文嵌入代码。"""
        if context:
            combined = f"Context: {context}\n\nCode:\n{chunk}"
        else:
            combined = chunk
        return await self.embeddings.aembed_query(combined)
```

### 模板 6：嵌入质量评估

```python
import numpy as np
from typing import List, Dict

def evaluate_retrieval_quality(
    queries: List[str],
    relevant_docs: List[List[str]],  # 每个查询的相关文档 ID 列表
    retrieved_docs: List[List[str]],  # 每个查询的检索文档 ID 列表
    k: int = 10
) -> Dict[str, float]:
    """评估检索的嵌入质量。"""

    def precision_at_k(relevant: set, retrieved: List[str], k: int) -> float:
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & relevant)
        return relevant_retrieved / k if k > 0 else 0

    def recall_at_k(relevant: set, retrieved: List[str], k: int) -> float:
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & relevant)
        return relevant_retrieved / len(relevant) if relevant else 0

    def mrr(relevant: set, retrieved: List[str]) -> float:
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                return 1 / (i + 1)
        return 0

    def ndcg_at_k(relevant: set, retrieved: List[str], k: int) -> float:
        dcg = sum(
            1 / np.log2(i + 2) if doc in relevant else 0
            for i, doc in enumerate(retrieved[:k])
        )
        ideal_dcg = sum(1 / np.log2(i + 2) for i in range(min(len(relevant), k)))
        return dcg / ideal_dcg if ideal_dcg > 0 else 0

    metrics = {
        f"precision@{k}": [],
        f"recall@{k}": [],
        "mrr": [],
        f"ndcg@{k}": []
    }

    for relevant, retrieved in zip(relevant_docs, retrieved_docs):
        relevant_set = set(relevant)
        metrics[f"precision@{k}"].append(precision_at_k(relevant_set, retrieved, k))
        metrics[f"recall@{k}"].append(recall_at_k(relevant_set, retrieved, k))
        metrics["mrr"].append(mrr(relevant_set, retrieved))
        metrics[f"ndcg@{k}"].append(ndcg_at_k(relevant_set, retrieved, k))

    return {name: np.mean(values) for name, values in metrics.items()}


def compute_embedding_similarity(
    embeddings1: np.ndarray,
    embeddings2: np.ndarray,
    metric: str = "cosine"
) -> np.ndarray:
    """计算嵌入集之间的相似度矩阵。"""
    if metric == "cosine":
        # 标准化并计算点积
        norm1 = embeddings1 / np.linalg.norm(embeddings1, axis=1, keepdims=True)
        norm2 = embeddings2 / np.linalg.norm(embeddings2, axis=1, keepdims=True)
        return norm1 @ norm2.T
    elif metric == "euclidean":
        from scipy.spatial.distance import cdist
        return -cdist(embeddings1, embeddings2, metric='euclidean')
    elif metric == "dot":
        return embeddings1 @ embeddings2.T
    else:
        raise ValueError(f"Unknown metric: {metric}")


def compare_embedding_models(
    texts: List[str],
    models: Dict[str, callable],
    queries: List[str],
    relevant_indices: List[List[int]],
    k: int = 5
) -> Dict[str, Dict[str, float]]:
    """比较多个嵌入模型的检索质量。"""
    results = {}

    for model_name, embed_fn in models.items():
        # 嵌入所有文本
        doc_embeddings = np.array(embed_fn(texts))

        retrieved_per_query = []
        for query in queries:
            query_embedding = np.array(embed_fn([query])[0])
            # 计算相似度
            similarities = compute_embedding_similarity(
                query_embedding.reshape(1, -1),
                doc_embeddings,
                metric="cosine"
            )[0]
            # 获取 top-k 索引
            top_k_indices = np.argsort(similarities)[::-1][:k]
            retrieved_per_query.append([str(i) for i in top_k_indices])

        # 将相关索引转换为字符串 ID
        relevant_docs = [[str(i) for i in indices] for indices in relevant_indices]

        results[model_name] = evaluate_retrieval_quality(
            queries, relevant_docs, retrieved_per_query, k
        )

    return results
```

## 最佳实践

### 应该做

- **匹配模型与用例**：代码 vs 文本 vs 多语言
- **精心分块**：保留语义边界
- **标准化嵌入**：用于余弦相似度搜索
- **批量请求**：比逐个更高效
- **缓存嵌入**：避免对静态内容重新计算
- **为 Claude 应用使用 Voyage AI**：Anthropic 推荐

### 不应该做

- **不要忽略令牌限制**：截断会丢失信息
- **不要混合嵌入模型**：向量空间不兼容
- **不要跳过预处理**：垃圾进，垃圾出
- **不要过度分块**：会丢失重要上下文
- **不要忘记元数据**：对过滤和调试至关重要
