"""使用 langchain 基础组件 手动实现工具调用和agent循环调用"""

# reAct 范式 底层原理

from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langsmith import traceable

MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"


@tool
def get_product_price(product: str) -> float:
    """在产品目录中查找某件产品的价格"""
    print(f"    >> get_product_price(product='{product}')")
    prices = {"笔记本电脑": 1299.99, "耳机": 149.95, "键盘": 89.50}
    return prices.get(product, 0)


@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """对价格应用折扣等级，并返回最终价格。
    可用等级：青铜、白银、黄金。"""
    print(f"    >> apply_discount(price={price}, discount_tier='{discount_tier}')")
    discount_percentages = {"青铜": 5, "白银": 12, "黄金": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)


@traceable(name="LangChain Agent Loop")
def run_agent(question: str):
    pass


if __name__ == "__main__":
    print("Hello LangChain Agent (.bind_tools)!")
    print()
    result = run_agent("在打完黄金等级折扣后，笔记本电脑的价格是多少？")
