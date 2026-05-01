---
name: prompt-engineering-patterns
description: 掌握高级提示工程技术，以最大化 LLM 在生产环境中的性能、可靠性和可控性。在优化提示、改进 LLM 输出或设计生产提示模板时使用。
---

# 提示工程模式

掌握高级提示工程技术，以最大化 LLM 的性能、可靠性和可控性。

## 何时使用此技能

- 为生产 LLM 应用设计复杂提示
- 优化提示性能和一致性
- 实现结构化推理模式（思维链、思维树）
- 构建带动态示例选择的少样本学习系统
- 创建带变量插值的可复用提示模板
- 调试和改进产生不一致输出的提示
- 为专业 AI 助手实现系统提示
- 使用结构化输出（JSON 模式）进行可靠解析

## 核心能力

### 1. 少样本学习

- 示例选择策略（语义相似性、多样性采样）
- 平衡示例数量与上下文窗口约束
- 用输入-输出对构建有效的演示
- 从知识库动态检索示例
- 通过策略性示例选择处理边界情况

### 2. 思维链提示

- 逐步推理引导
- 使用「让我们逐步思考」的零样本 CoT
- 带推理轨迹的少样本 CoT
- 自一致性技术（采样多条推理路径）
- 验证和确认步骤

### 3. 结构化输出

- 用于可靠解析的 JSON 模式
- Pydantic 模式强制
- 类型安全的响应处理
- 格式错误输出的错误处理

### 4. 提示优化

- 迭代改进工作流
- A/B 测试提示变体
- 测量提示性能指标（准确性、一致性、延迟）
- 在保持质量的同时减少 token 使用
- 处理边界情况和失败模式

### 5. 模板系统

- 变量插值和格式化
- 条件提示部分
- 多轮对话模板
- 基于角色的提示组合
- 模块化提示组件

### 6. 系统提示设计

- 设置模型行为和约束
- 定义输出格式和结构
- 建立角色和专业领域
- 安全指南和内容策略
- 上下文设置和背景信息

## 快速开始

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Define structured output schema
class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query")
    explanation: str = Field(description="Brief explanation of what the query does")
    tables_used: list[str] = Field(description="List of tables referenced")

# Initialize model with structured output
llm = ChatAnthropic(model="claude-sonnet-4-6")
structured_llm = llm.with_structured_output(SQLQuery)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert SQL developer. Generate efficient, secure SQL queries.
    Always use parameterized queries to prevent SQL injection.
    Explain your reasoning briefly."""),
    ("user", "Convert this to SQL: {query}")
])

# Create chain
chain = prompt | structured_llm

# Use
result = await chain.ainvoke({
    "query": "Find all users who registered in the last 30 days"
})
print(result.query)
print(result.explanation)
```

## 关键模式

### 模式 1：使用 Pydantic 的结构化输出

```python
from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import Literal
import json

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
    key_phrases: list[str]
    reasoning: str

async def analyze_sentiment(text: str) -> SentimentAnalysis:
    """Analyze sentiment with structured output."""
    client = Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Analyze the sentiment of this text.

Text: {text}

Respond with JSON matching this schema:
{{
    "sentiment": "positive" | "negative" | "neutral",
    "confidence": 0.0-1.0,
    "key_phrases": ["phrase1", "phrase2"],
    "reasoning": "brief explanation"
}}"""
        }]
    )

    return SentimentAnalysis(**json.loads(message.content[0].text))
```

### 模式 2：带自验证的思维链

```python
from langchain_core.prompts import ChatPromptTemplate

cot_prompt = ChatPromptTemplate.from_template("""
Solve this problem step by step.

Problem: {problem}

Instructions:
1. Break down the problem into clear steps
2. Work through each step showing your reasoning
3. State your final answer
4. Verify your answer by checking it against the original problem

Format your response as:
## Steps
[Your step-by-step reasoning]

## Answer
[Your final answer]

## Verification
[Check that your answer is correct]
""")
```

### 模式 3：带动态示例选择的少样本

```python
from langchain_voyageai import VoyageAIEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma

# Create example selector with semantic similarity
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=[
        {"input": "How do I reset my password?", "output": "Go to Settings > Security > Reset Password"},
        {"input": "Where can I see my order history?", "output": "Navigate to Account > Orders"},
        {"input": "How do I contact support?", "output": "Click Help > Contact Us or email support@example.com"},
    ],
    embeddings=VoyageAIEmbeddings(model="voyage-3-large"),
    vectorstore_cls=Chroma,
    k=2  # Select 2 most similar examples
)

async def get_few_shot_prompt(query: str) -> str:
    """Build prompt with dynamically selected examples."""
    examples = await example_selector.aselect_examples({"input": query})

    examples_text = "\n".join(
        f"User: {ex['input']}\nAssistant: {ex['output']}"
        for ex in examples
    )

    return f"""You are a helpful customer support assistant.

Here are some example interactions:
{examples_text}

Now respond to this query:
User: {query}
Assistant:"""
```

### 模式 4：渐进式披露

从简单提示开始，仅在需要时添加复杂性：

```python
PROMPT_LEVELS = {
    # Level 1: Direct instruction
    "simple": "Summarize this article: {text}",

    # Level 2: Add constraints
    "constrained": """Summarize this article in 3 bullet points, focusing on:
- Key findings
- Main conclusions
- Practical implications

Article: {text}""",

    # Level 3: Add reasoning
    "reasoning": """Read this article carefully.
1. First, identify the main topic and thesis
2. Then, extract the key supporting points
3. Finally, summarize in 3 bullet points

Article: {text}

Summary:""",

    # Level 4: Add examples
    "few_shot": """Read articles and provide concise summaries.

Example:
Article: "New research shows that regular exercise can reduce anxiety by up to 40%..."
Summary:
• Regular exercise reduces anxiety by up to 40%
• 30 minutes of moderate activity 3x/week is sufficient
• Benefits appear within 2 weeks of starting

Now summarize this article:
Article: {text}

Summary:"""
}
```

### 模式 5：错误恢复和回退

```python
from pydantic import BaseModel, ValidationError
import json

class ResponseWithConfidence(BaseModel):
    answer: str
    confidence: float
    sources: list[str]
    alternative_interpretations: list[str] = []

ERROR_RECOVERY_PROMPT = """
Answer the question based on the context provided.

Context: {context}
Question: {question}

Instructions:
1. If you can answer confidently (>0.8), provide a direct answer
2. If you're somewhat confident (0.5-0.8), provide your best answer with caveats
3. If you're uncertain (<0.5), explain what information is missing
4. Always provide alternative interpretations if the question is ambiguous

Respond in JSON:
{{
    "answer": "your answer or 'I cannot determine this from the context'",
    "confidence": 0.0-1.0,
    "sources": ["relevant context excerpts"],
    "alternative_interpretations": ["if question is ambiguous"]
}}
"""

async def answer_with_fallback(
    context: str,
    question: str,
    llm
) -> ResponseWithConfidence:
    """Answer with error recovery and fallback."""
    prompt = ERROR_RECOVERY_PROMPT.format(context=context, question=question)

    try:
        response = await llm.ainvoke(prompt)
        return ResponseWithConfidence(**json.loads(response.content))
    except (json.JSONDecodeError, ValidationError) as e:
        # Fallback: try to extract answer without structure
        simple_prompt = f"Based on: {context}\n\nAnswer: {question}"
        simple_response = await llm.ainvoke(simple_prompt)
        return ResponseWithConfidence(
            answer=simple_response.content,
            confidence=0.5,
            sources=["fallback extraction"],
            alternative_interpretations=[]
        )
```

### 模式 6：基于角色的系统提示

```python
SYSTEM_PROMPTS = {
    "analyst": """You are a senior data analyst with expertise in SQL, Python, and business intelligence.

Your responsibilities:
- Write efficient, well-documented queries
- Explain your analysis methodology
- Highlight key insights and recommendations
- Flag any data quality concerns

Communication style:
- Be precise and technical when discussing methodology
- Translate technical findings into business impact
- Use clear visualizations when helpful""",

    "assistant": """You are a helpful AI assistant focused on accuracy and clarity.

Core principles:
- Always cite sources when making factual claims
- Acknowledge uncertainty rather than guessing
- Ask clarifying questions when the request is ambiguous
- Provide step-by-step explanations for complex topics

Constraints:
- Do not provide medical, legal, or financial advice
- Redirect harmful requests appropriately
- Protect user privacy""",

    "code_reviewer": """You are a senior software engineer conducting code reviews.

Review criteria:
- Correctness: Does the code work as intended?
- Security: Are there any vulnerabilities?
- Performance: Are there efficiency concerns?
- Maintainability: Is the code readable and well-structured?
- Best practices: Does it follow language idioms?

Output format:
1. Summary assessment (approve/request changes)
2. Critical issues (must fix)
3. Suggestions (nice to have)
4. Positive feedback (what's done well)"""
}
```

## 集成模式

### 与 RAG 系统集成

```python
RAG_PROMPT = """You are a knowledgeable assistant that answers questions based on provided context.

Context (retrieved from knowledge base):
{context}

Instructions:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say "I don't have information about that in my knowledge base"
3. Cite specific passages using [1], [2] notation
4. If the question is ambiguous, ask for clarification

Question: {question}

Answer:"""
```

### 与验证和确认集成

```python
VALIDATED_PROMPT = """Complete the following task:

Task: {task}

After generating your response, verify it meets ALL these criteria:
✓ Directly addresses the original request
✓ Contains no factual errors
✓ Is appropriately detailed (not too brief, not too verbose)
✓ Uses proper formatting
✓ Is safe and appropriate

If verification fails on any criterion, revise before responding.

Response:"""
```

## 性能优化

### Token 效率

```python
# Before: Verbose prompt (150+ tokens)
verbose_prompt = """
I would like you to please take the following text and provide me with a comprehensive
summary of the main points. The summary should capture the key ideas and important details
while being concise and easy to understand.
"""

# After: Concise prompt (30 tokens)
concise_prompt = """Summarize the key points concisely:

{text}

Summary:"""
```

### 缓存常见前缀

```python
from anthropic import Anthropic

client = Anthropic()

# Use prompt caching for repeated system prompts
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": user_query}]
)
```

## 最佳实践

1. **具体明确**：模糊的提示产生不一致的结果
2. **展示而非讲述**：示例比描述更有效
3. **使用结构化输出**：用 Pydantic 强制模式以提高可靠性
4. **广泛测试**：在多样化的代表性输入上评估
5. **快速迭代**：小改动可能产生大影响
6. **监控性能**：在生产中跟踪指标
7. **版本控制**：将提示视为代码进行适当版本管理
8. **记录意图**：解释提示为何如此结构化

## 常见陷阱

- **过度工程化**：在尝试简单提示之前就使用复杂提示
- **示例污染**：使用与目标任务不匹配的示例
- **上下文溢出**：过多示例超过 token 限制
- **模糊指令**：为多种解释留下空间
- **忽略边界情况**：未在不寻常或边界输入上测试
- **无错误处理**：假设输出总是格式良好的
- **硬编码值**：未参数化提示以供复用

## 成功指标

跟踪这些提示的 KPI：

- **准确性**：输出的正确性
- **一致性**：类似输入间的可重现性
- **延迟**：响应时间（P50、P95、P99）
- **Token 使用**：每请求平均 token 数
- **成功率**：有效、可解析输出的百分比
- **用户满意度**：评分和反馈
