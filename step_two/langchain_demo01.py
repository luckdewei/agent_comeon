from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

prompt = PromptTemplate(
    template="What is a good name for a company that makes {product}?",
    input_variables=["product"],
)

llm = ChatOpenAI(
    api_key=os.environ.get("MODELSCOPE_TOKEN"),
    base_url="https://api-inference.modelscope.cn/v1",
    model="moonshotai/Kimi-K2.5",
    temperature=0,
)

chain = prompt | llm

response = chain.invoke(input={"product": "colorful socks"})

print(response)
