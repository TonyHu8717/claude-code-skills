---
name: langchain-architecture
description: 使用 LangChain 1.x 和 LangGraph 设计 LLM 应用，支持代理、记忆和工具集成。在构建 LangChain 应用、实现 AI 代理或创建复杂 LLM 工作流时使用。
---

# LangChain & LangGraph 架构

掌握现代 LangChain 1.x 和 LangGraph，用于构建具有代理、状态管理、记忆和工具集成的复杂 LLM 应用。

## 何时使用此技能

- 构建具有工具访问能力的自主 AI 代理
- 实现复杂的多步骤 LLM 工作流
- 管理对话记忆和状态
- 将 LLM 与外部数据源和 API 集成
- 创建模块化、可复用的 LLM 应用组件
- 实现文档处理管道
- 构建生产级 LLM 应用

## 包结构（LangChain 1.x）

```
langchain (1.2.x)         # 高级编排
langchain-core (1.2.x)    # 核心抽象（消息、提示、工具）
langchain-community       # 第三方集成
langgraph                 # 代理编排和状态管理
langchain-openai          # OpenAI 集成
langchain-anthropic       # Anthropic/Claude 集成
langchain-voyageai        # Voyage AI 嵌入
langchain-pinecone        # Pinecone 向量存储
```

## 核心概念

### 1. LangGraph 代理

LangGraph 是 2026 年构建代理的标准。它提供：

**关键特性：**

- **StateGraph**：带类型化状态的显式状态管理
- **持久执行**：代理在故障中持久化
- **人机协同**：在任意点检查和修改状态
- **记忆**：跨会话的短期和长期记忆
- **检查点**：保存和恢复代理状态

**代理模式：**

- **ReAct**：使用 `create_react_agent` 的推理 + 行动
- **计划与执行**：分离的规划和执行节点
- **多代理**：在专业代理之间路由的监督者
- **工具调用**：使用 Pydantic 模式的结构化工具调用

### 2. 状态管理

LangGraph 使用 TypedDict 进行显式状态管理：

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState

# 简单的基于消息的状态
class AgentState(MessagesState):
    """扩展 MessagesState 添加自定义字段。"""
    context: Annotated[list, "retrieved documents"]

# 复杂代理的自定义状态
class CustomState(TypedDict):
    messages: Annotated[list, "conversation history"]
    context: Annotated[dict, "retrieved context"]
    current_step: str
    results: list
```

### 3. 记忆系统

现代记忆实现：

- **ConversationBufferMemory**：存储所有消息（短对话）
- **ConversationSummaryMemory**：总结旧消息（长对话）
- **ConversationTokenBufferMemory**：基于 token 的窗口
- **VectorStoreRetrieverMemory**：语义相似性检索
- **LangGraph Checkpointer**：跨会话的持久状态

### 4. 文档处理

加载、转换和存储文档：

**组件：**

- **文档加载器**：从各种来源加载
- **文本分割器**：智能分块文档
- **向量存储**：存储和检索嵌入
- **检索器**：获取相关文档

### 5. 回调和追踪

LangSmith 是可观测性标准：

- 请求/响应日志
- token 使用跟踪
- 延迟监控
- 错误跟踪
- 追踪可视化

## 快速开始

### 使用 LangGraph 的现代 ReAct 代理

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import ast
import operator

# 初始化 LLM（推荐 Claude Sonnet 4.6）
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

# 使用 Pydantic 模式定义工具
@tool
def search_database(query: str) -> str:
    """搜索内部数据库获取信息。"""
    # 你的数据库搜索逻辑
    return f"Results for: {query}"

@tool
def calculate(expression: str) -> str:
    """安全评估数学表达式。

    支持：+、-、*、/、**、%、括号
    示例：'(2 + 3) * 4' 返回 '20'
    """
    # 使用 ast 进行安全数学评估
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            return allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return allowed_operators[type(node.op)](operand)
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        return str(_eval(tree.body))
    except Exception as e:
        return f"Error: {e}"

tools = [search_database, calculate]

# 创建用于记忆持久化的检查点
checkpointer = MemorySaver()

# 创建 ReAct 代理
agent = create_react_agent(
    llm,
    tools,
    checkpointer=checkpointer
)

# 使用线程 ID 运行代理以实现记忆
config = {"configurable": {"thread_id": "user-123"}}
result = await agent.ainvoke(
    {"messages": [("user", "Search for Python tutorials and calculate 25 * 4")]},
    config=config
)
```

## 架构模式

### 模式 1：使用 LangGraph 的 RAG

```python
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated

class RAGState(TypedDict):
    question: str
    context: Annotated[list[Document], "retrieved documents"]
    answer: str

# 初始化组件
llm = ChatAnthropic(model="claude-sonnet-4-6")
embeddings = VoyageAIEmbeddings(model="voyage-3-large")
vectorstore = PineconeVectorStore(index_name="docs", embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 定义节点
async def retrieve(state: RAGState) -> RAGState:
    """检索相关文档。"""
    docs = await retriever.ainvoke(state["question"])
    return {"context": docs}

async def generate(state: RAGState) -> RAGState:
    """从上下文生成答案。"""
    prompt = ChatPromptTemplate.from_template(
        """基于以下上下文回答。如果无法回答，请说明。

        上下文：{context}

        问题：{question}

        答案："""
    )
    context_text = "\n\n".join(doc.page_content for doc in state["context"])
    response = await llm.ainvoke(
        prompt.format(context=context_text, question=state["question"])
    )
    return {"answer": response.content}

# 构建图
builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

rag_chain = builder.compile()

# 使用链
result = await rag_chain.ainvoke({"question": "主要话题是什么？"})
```

### 模式 2：带结构化工具的自定义代理

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """数据库搜索输入。"""
    query: str = Field(description="搜索查询")
    filters: dict = Field(default={}, description="可选过滤器")

class EmailInput(BaseModel):
    """发送邮件输入。"""
    recipient: str = Field(description="邮件收件人")
    subject: str = Field(description="邮件主题")
    content: str = Field(description="邮件正文")

async def search_database(query: str, filters: dict = {}) -> str:
    """搜索内部数据库获取信息。"""
    # 你的数据库搜索逻辑
    return f"Results for '{query}' with filters {filters}"

async def send_email(recipient: str, subject: str, content: str) -> str:
    """向指定收件人发送邮件。"""
    # 邮件发送逻辑
    return f"Email sent to {recipient}"

tools = [
    StructuredTool.from_function(
        coroutine=search_database,
        name="search_database",
        description="搜索内部数据库",
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        coroutine=send_email,
        name="send_email",
        description="发送邮件",
        args_schema=EmailInput
    )
]

agent = create_react_agent(llm, tools)
```

### 模式 3：使用 StateGraph 的多步骤工作流

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class WorkflowState(TypedDict):
    text: str
    entities: list
    analysis: str
    summary: str
    current_step: str

async def extract_entities(state: WorkflowState) -> WorkflowState:
    """从文本中提取关键实体。"""
    prompt = f"从以下文本提取关键实体：{state['text']}\n\n以 JSON 列表返回。"
    response = await llm.ainvoke(prompt)
    return {"entities": response.content, "current_step": "analyze"}

async def analyze_entities(state: WorkflowState) -> WorkflowState:
    """分析提取的实体。"""
    prompt = f"分析这些实体：{state['entities']}\n\n提供洞察。"
    response = await llm.ainvoke(prompt)
    return {"analysis": response.content, "current_step": "summarize"}

async def generate_summary(state: WorkflowState) -> WorkflowState:
    """生成最终摘要。"""
    prompt = f"""总结：
    实体：{state['entities']}
    分析：{state['analysis']}

    提供简洁的摘要。"""
    response = await llm.ainvoke(prompt)
    return {"summary": response.content, "current_step": "complete"}

def route_step(state: WorkflowState) -> Literal["analyze", "summarize", "end"]:
    """根据当前状态路由到下一步。"""
    step = state.get("current_step", "extract")
    if step == "analyze":
        return "analyze"
    elif step == "summarize":
        return "summarize"
    return "end"

# 构建工作流
builder = StateGraph(WorkflowState)
builder.add_node("extract", extract_entities)
builder.add_node("analyze", analyze_entities)
builder.add_node("summarize", generate_summary)

builder.add_edge(START, "extract")
builder.add_conditional_edges("extract", route_step, {
    "analyze": "analyze",
    "summarize": "summarize",
    "end": END
})
builder.add_conditional_edges("analyze", route_step, {
    "summarize": "summarize",
    "end": END
})
builder.add_edge("summarize", END)

workflow = builder.compile()
```

### 模式 4：多代理编排

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from typing import Literal

class MultiAgentState(TypedDict):
    messages: list
    next_agent: str

# 创建专业代理
researcher = create_react_agent(llm, research_tools)
writer = create_react_agent(llm, writing_tools)
reviewer = create_react_agent(llm, review_tools)

async def supervisor(state: MultiAgentState) -> MultiAgentState:
    """根据任务路由到适当的代理。"""
    prompt = f"""根据对话，哪个代理应该处理此任务？

    选项：
    - researcher：用于查找信息
    - writer：用于创建内容
    - reviewer：用于审查和编辑
    - FINISH：任务已完成

    消息：{state['messages']}

    只回复代理名称。"""

    response = await llm.ainvoke(prompt)
    return {"next_agent": response.content.strip().lower()}

def route_to_agent(state: MultiAgentState) -> Literal["researcher", "writer", "reviewer", "end"]:
    """根据监督者决策路由。"""
    next_agent = state.get("next_agent", "").lower()
    if next_agent == "finish":
        return "end"
    return next_agent if next_agent in ["researcher", "writer", "reviewer"] else "end"

# 构建多代理图
builder = StateGraph(MultiAgentState)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_node("reviewer", reviewer)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_to_agent, {
    "researcher": "researcher",
    "writer": "writer",
    "reviewer": "reviewer",
    "end": END
})

# 每个代理返回监督者
for agent in ["researcher", "writer", "reviewer"]:
    builder.add_edge(agent, "supervisor")

multi_agent = builder.compile()
```

## 记忆管理

### 使用 LangGraph 的基于 Token 的记忆

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# 内存检查点（开发环境）
checkpointer = MemorySaver()

# 创建带持久记忆的代理
agent = create_react_agent(llm, tools, checkpointer=checkpointer)

# 每个 thread_id 维护独立对话
config = {"configurable": {"thread_id": "session-abc123"}}

# 使用相同 thread_id 的消息在调用间持久化
result1 = await agent.ainvoke({"messages": [("user", "My name is Alice")]}, config)
result2 = await agent.ainvoke({"messages": [("user", "What's my name?")]}, config)
# 代理记住："Your name is Alice"
```

### 使用 PostgreSQL 的生产记忆

```python
from langgraph.checkpoint.postgres import PostgresSaver

# 生产检查点
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/langgraph"
)

agent = create_react_agent(llm, tools, checkpointer=checkpointer)
```

### 用于长期上下文的向量存储记忆

```python
from langchain_community.vectorstores import Chroma
from langchain_voyageai import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(model="voyage-3-large")
memory_store = Chroma(
    collection_name="conversation_memory",
    embedding_function=embeddings,
    persist_directory="./memory_db"
)

async def retrieve_relevant_memory(query: str, k: int = 5) -> list:
    """检索相关的过去对话。"""
    docs = await memory_store.asimilarity_search(query, k=k)
    return [doc.page_content for doc in docs]

async def store_memory(content: str, metadata: dict = {}):
    """将对话存储到长期记忆中。"""
    await memory_store.aadd_texts([content], metadatas=[metadata])
```

## 回调系统和 LangSmith

### LangSmith 追踪

```python
import os
from langchain_anthropic import ChatAnthropic

# 启用 LangSmith 追踪
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# 所有 LangChain/LangGraph 操作自动追踪
llm = ChatAnthropic(model="claude-sonnet-4-6")
```

### 自定义回调处理器

```python
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List

class CustomCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        print(f"LLM started with {len(prompts)} prompts")

    def on_llm_end(self, response, **kwargs) -> None:
        print(f"LLM completed: {len(response.generations)} generations")

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        print(f"LLM error: {error}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs
    ) -> None:
        print(f"Tool started: {serialized.get('name')}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"Tool completed: {output[:100]}...")

# 使用回调
result = await agent.ainvoke(
    {"messages": [("user", "query")]},
    config={"callbacks": [CustomCallbackHandler()]}
)
```

## 流式响应

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6", streaming=True)

# 流式 token
async for chunk in llm.astream("Tell me a story"):
    print(chunk.content, end="", flush=True)

# 流式代理事件
async for event in agent.astream_events(
    {"messages": [("user", "Search and summarize")]},
    version="v2"
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
    elif event["event"] == "on_tool_start":
        print(f"\n[Using tool: {event['name']}]")
```

## 测试策略

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_tool_selection():
    """测试代理选择正确的工具。"""
    with patch.object(llm, 'ainvoke') as mock_llm:
        mock_llm.return_value = AsyncMock(content="Using search_database")

        result = await agent.ainvoke({
            "messages": [("user", "search for documents")]
        })

        # 验证工具被调用
        assert "search_database" in str(result)

@pytest.mark.asyncio
async def test_memory_persistence():
    """测试记忆在调用间持久化。"""
    config = {"configurable": {"thread_id": "test-thread"}}

    # 第一条消息
    await agent.ainvoke(
        {"messages": [("user", "Remember: the code is 12345")]},
        config
    )

    # 第二条消息应记住
    result = await agent.ainvoke(
        {"messages": [("user", "What was the code?")]},
        config
    )

    assert "12345" in result["messages"][-1].content
```

## 性能优化

### 1. 使用 Redis 缓存

```python
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
import redis

redis_client = redis.Redis.from_url("redis://localhost:6379")
set_llm_cache(RedisCache(redis_client))
```

### 2. 异步批处理

```python
import asyncio
from langchain_core.documents import Document

async def process_documents(documents: list[Document]) -> list:
    """并行处理文档。"""
    tasks = [process_single(doc) for doc in documents]
    return await asyncio.gather(*tasks)

async def process_single(doc: Document) -> dict:
    """处理单个文档。"""
    chunks = text_splitter.split_documents([doc])
    embeddings = await embeddings_model.aembed_documents(
        [c.page_content for c in chunks]
    )
    return {"doc_id": doc.metadata.get("id"), "embeddings": embeddings}
```

### 3. 连接池

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# 复用 Pinecone 客户端
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("my-index")

# 使用现有索引创建向量存储
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
```
