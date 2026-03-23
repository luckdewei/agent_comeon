from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

llm = ChatOpenAI(
    base_url="https://api-inference.modelscope.cn/v1",
    model="moonshotai/Kimi-K2.5",
    temperature=0,
)
