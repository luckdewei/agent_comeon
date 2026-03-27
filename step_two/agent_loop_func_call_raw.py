"""手动实现工具调用和agent循环调用"""

# reAct 范式 底层原理

from dotenv import load_dotenv

load_dotenv()

import ollama
from langsmith import traceable

MAX_ITERATIONS = 10
MODEL = "qwen3:1.7b"


@traceable(run_type="tool")
def get_product_price(product: str) -> float:
    """
    产品目录工具
    在产品目录中查找某件产品的价格
    """
    print(f"    >> get_product_price(product='{product}')")
    prices = {"笔记本电脑": 1299.99, "耳机": 149.95, "键盘": 89.50}
    return prices.get(product, 0)


@traceable(run_type="tool")
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


tools_for_llm = [
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "产品目录工具, 可以在产品目录中查找某件产品的价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "产品名称, 例如 '笔记本电脑', '耳机', '键盘'",
                    }
                },
                "required": ["product"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_discount",
            "description": "折扣计算工具, 根据传入的折扣等级进行折扣计算输出最终价格. 支持的折扣等级: 青铜,白银,黄金",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "产品原始价格"},
                    "discount_tier": {
                        "type": "string",
                        "description": "折扣等级: 青铜,白银,黄金",
                    },
                },
                "required": ["product"],
            },
        },
    },
]


@traceable(name="Ollama Chat", run_type="llm")
def ollama_chat_traced(messages):
    return ollama.chat(model=MODEL, tools=tools_for_llm, messages=messages)


@traceable(name="LangChain Agent Loop")
def run_agent(question: str):

    tools_dict = {
        "get_product_price": get_product_price,
        "apply_discount": apply_discount,
    }

    print(f"Question: {question}")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
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
            ),
        },
        {"role": "user", "content": question},
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")

        response = ollama_chat_traced(messages=messages)
        ai_message = response.message

        tool_calls = ai_message.tool_calls

        if not tool_calls:
            print(f"\n最终回答：{ai_message.content}")
            return ai_message.content

        tool_call = tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments

        print(f" [工具选择] {tool_name} 参数: {tool_args}")

        tool_to_use = tools_dict.get(tool_name)

        if tool_to_use is None:
            raise ValueError(f"工具 '{tool_name}' 不存在")

        observation = tool_to_use(**tool_args)

        print(f"  [工具输出结果] {observation}")

        messages.append(ai_message)
        messages.append({"role": "tool", "content": str(observation)})

    print("ERROR: Max iterations reached without a final answer")
    return None


if __name__ == "__main__":
    print("Hello LangChain Agent (.bind_tools)!")
    print()
    result = run_agent("黄金等级购买笔记本电脑的价格是多少？")
