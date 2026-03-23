from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from llm_config import llm
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient()


@tool
def search(query: str) -> str:
    """
    网络搜索工具
    Args:
        query: 搜索关键词

    Returns: 搜索结果
    """
    print(f"搜索关键词：{query}")
    return tavily_client.search(query=query)


tools = [search]

agent = create_agent(model=llm, tools=tools)


result = agent.invoke(
    {
        "messages": HumanMessage(
            content="我想要在BOOS直聘在找出三个AI agent的职位，帮我列举出来包含详细信息"
        ),
    }
)

print(result)
