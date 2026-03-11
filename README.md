# agent_comeon

前端 -> AI Agent


## 第一阶段：思维重塑与 Python 突击

1. 关键技能点
+ Python 进阶：重点掌握 asyncio (异步并发)、Pydantic (数据校验，Agent 的基石)、装饰器、生成器。
+ LLM 原理直觉：理解 Token 限制、Temperature 对输出的影响、Prompt 的基本结构（System/User/Assistant）。
+ 基础交互：不依赖框架，直接用 openai 或 anthropic 原生 SDK 写一个带“重试机制”和“JSON 格式强校验”的脚本。
2. 推荐资料
+ 文档：Python Asyncio 官方文档, Pydantic V2 文档 (重点看 TypeAdapter 和 model_validate)。
+ 课程：DeepLearning.AI 的短课 "Chat with Your Data" 和 "Functions, Tools and Agents with LangChain" (虽然讲 LangChain，但概念通用)。
+ 实战作业：
  + 写一个 Python 脚本，调用 LLM 提取非结构化文本中的特定字段，强制输出为标准 JSON。如果 LLM 输出错误，代码自动捕获并重试（最多 3 次），若仍失败则抛出特定异常。


## 第二阶段：掌控核心编排框架 LangGraph
目标：这是高级开发者的护城河。学会用“状态机”思维构建复杂、可中断、可记忆的 Agent。
1. 为什么是 LangGraph？
2025-2026 年，简单的线性 Chain 已被淘汰。企业需要的是能处理多轮对话、人工介入、循环反思的复杂流程。LangGraph 基于图（Graph）和状态（State），完美解决这些问题。

2. 关键技能点
+ State Management：定义全局状态对象（TypedDict/Pydantic），理解状态如何在节点间传递。
+ Nodes & Edges：编写功能节点，设计条件边（Conditional Edges）实现逻辑分支。
+ Human-in-the-loop：实现“断点”，让 Agent 在执行关键操作前暂停，等待人类确认后再继续。
+ Memory & Persistence：使用 Checkpointer 实现长短期记忆，支持对话回溯。

3. 推荐资料
+ 官方文档：LangGraph Documentation (必读，尤其是 "Tutorials" 和 "How-to" 部分)。
+ 视频：LangChain 官方 YouTube 频道的 "LangGraph Zero to Hero" 系列。
+ 实战作业：
  + 构建一个“旅行规划 Agent”：
    1. 用户输入需求。
    2. Agent 调用搜索工具查机票/酒店。
    3. 关键点：在预订前，Agent 必须暂停，生成一个总结让用户确认（Human-in-the-loop）。
    4. 用户确认后，调用模拟预订 API。
    5. 如果预订失败，Agent 自动反思并重新搜索（循环边）。

## 第三阶段：RAG 进阶与上下文工程

## 第四阶段：评估、观测与部署

## 第五阶段：综合实战与作品集