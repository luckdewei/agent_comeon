from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from llm_config import llm
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


tools = [TavilySearch()]

agent = create_agent(model=llm, tools=tools)


result = agent.invoke(
    {
        "messages": HumanMessage(
            content="我想要在BOOS直聘在找出3个AI agent的职位，帮我列举出来包含详细信息"
        ),
    }
)

print(result)
