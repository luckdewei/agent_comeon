"""langchain 结构化输出"""

from typing import List

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from llm_config import llm
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


class Sourse(BaseModel):
    """agent 用来描述信息来源的结构"""

    url: str = Field(description="信息来源链接")


class AgentResponse(BaseModel):
    """agent 用来返回结果的结构"""

    answer: str = Field(description="agent的回答")
    source: List[Sourse] = Field(default_factory=list, description="信息来源列表")


tools = [TavilySearch()]

agent = create_agent(model=llm, tools=tools, response_format=AgentResponse)


result = agent.invoke(
    {
        "messages": HumanMessage(
            content="我想要在BOOS直聘在找出3个AI agent的职位，帮我列举出来包含详细信息"
        ),
    }
)

print(result)
