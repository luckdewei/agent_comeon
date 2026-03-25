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
    """
    产品目录工具
    在产品目录中查找某件产品的价格
    """
    print(f"    >> get_product_price(product='{product}')")
    prices = {"笔记本电脑": 1299.99, "耳机": 149.95, "键盘": 89.50}
    return prices.get(product, 0)


@tool
def apply_discount(price: float, discount_tier: str) -> float:
    """
    折扣计算工具
    根据等级计算折扣，并返回最终价格。
    可用等级：青铜、白银、黄金。
    """
    print(f"    >> apply_discount(price={price}, discount_tier='{discount_tier}')")
    discount_percentages = {"青铜": 5, "白银": 12, "黄金": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)


@traceable(name="LangChain Agent Loop")
def run_agent(question: str):
    tools = [get_product_price, apply_discount]
    tools_dict = {t.name: t for t in tools}
    llm = init_chat_model(f"ollama:{MODEL}", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    print(f"Question: {question}")
    print("=" * 60)

    messages = [
        SystemMessage(
            content=(
                "你是一个购物助手。"
                "你可以使用产品目录工具和折扣计算工具。\n\n"
                "你必须严格遵守的规则：\n"
                "1. 绝对不要猜测或假设任何产品价格。"
                "你必须先调用 get_product_price 来获取产品的真实价格。\n"
                "2. 只有在从 get_product_price 接收到价格后，才能调用 apply_discount，并将接收到的价格传入"
                "返回apply_discount的输出 —— 不要虚构数字\n"
                "3. 绝对不要自己使用数学计算折扣。"
                "始终使用 apply_discount 工具。\n"
                "4. 如果用户未指定折扣等级，"
                "问他们要使用哪个等级 —— 不要假设某一个。"
                ""
            )
        ),
        HumanMessage(content=question),
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")

        ai_message = llm_with_tools.invoke(messages)

        tool_calls = ai_message.tool_calls

        if not tool_calls:
            print(f"\n最终回答：{ai_message.content}")
            return ai_message.content

        tool_call = tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")

        print(f" [工具选择] {tool_name} 参数: {tool_args}")

        tool_to_use = tools_dict.get(tool_name)

        if tool_to_use is None:
            raise ValueError(f"工具 '{tool_name}' 不存在")

        observation = tool_to_use.invoke(tool_args)

        print(f"  [工具输出结果] {observation}")

        messages.append(ai_message)
        messages.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call_id)
        )

    print("ERROR: Max iterations reached without a final answer")
    return None


if __name__ == "__main__":
    print("Hello LangChain Agent (.bind_tools)!")
    print()
    result = run_agent("黄金等级购买笔记本电脑的价格是多少？")
