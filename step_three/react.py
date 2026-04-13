from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai.chat_models import ChatOpenAI
from langchain_tavily import TavilySearch
import os

load_dotenv()


@tool
def triple(num: float) -> float:
    """
    :param num: a number to triple
    :return: the number tripled ->  multiplied by 3
    """
    return 3 * float(num)


tools = [TavilySearch(max_results=1), triple]

llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3.2",
    base_url=os.environ.get("BASE_URL"),
).bind_tools(tools=tools)
