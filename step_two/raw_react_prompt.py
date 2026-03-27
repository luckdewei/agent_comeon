"""纯 prompt 实现 React"""

# CHANGE 1: 添加 re + inspect — 我们将从原始文本而不是结构化 JSON 中解析工具调用

# reAct 范式 底层原理
from pyexpat import model
import re
import inspect
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
    # 需要转换下数据类型
    price = float(price)
    discount_percentages = {"青铜": 5, "白银": 12, "黄金": 23}
    discount = discount_percentages.get(discount_tier, 0)
    return round(price * (1 - discount / 100), 2)


tools = {
    "get_product_price": get_product_price,
    "apply_discount": apply_discount,
}
# 变更 3：删除 JSON 模式。工具现在以纯文本形式直接显示在提示符中。
# 我们使用 inspect 命令从函数本身获取描述。


def get_tool_descriptions(tools_dict):
    descriptions = []
    for tool_name, tool_function in tools_dict.items():
        # __wrapped__ bypasses decorator wrappers (e.g., @traceable adds *, config=None)
        original_function = getattr(tool_function, "__wrapped__", tool_function)
        signature = inspect.signature(original_function)
        docstring = inspect.getdoc(tool_function) or ""
        descriptions.append(f"{tool_name}{signature} - {docstring}")
    return "\n".join(descriptions)


tool_descriptions = get_tool_descriptions(tools)
tool_names = ", ".join(tools.keys())

react_prompt = f"""
严格规则 — 你必须严格遵守以下规则：
1. 绝对不要猜测或假设任何产品价格。你必须先调用 get_product_price 来获取真实价格。
2. 只有在从 get_product_price 获取到价格之后，才能调用 apply_discount。传递的参数必须是 get_product_price 返回的确切价格——不要传递自己编造的数字。
3. 绝对不要自己用数学计算折扣。始终使用 apply_discount 工具。
4. 如果用户没有指定折扣档位，请询问他们使用哪个档位——不要自行假设。

请尽力回答以下问题。你可以使用以下工具：

{tool_descriptions}

请使用以下格式：

Question: 你需要回答的输入问题

Thought: 你应该始终思考要做什么

Action: 要执行的动作，应为 [{tool_names}] 之一

Action Input: 动作的输入，以逗号分隔的值

Observation: 动作的结果

...（这个 Thought/Action/Action Input/Observation 可以重复多次）

Thought: 我现在知道最终答案了

Final Answer: 对原始输入问题的最终答案

开始！

Question: {{question}}
Thought:"""


@traceable(name="Ollama Chat", run_type="llm")
def ollama_chat_traced(model, messages, options):
    return ollama.chat(model=model, messages=messages, options=options)


@traceable(name="LangChain Agent Loop")
def run_agent(question: str):
    print(f"Question: {question}")
    print("=" * 60)

    prompt = react_prompt.format(question=question)

    scratchpad = ""

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")
        full_prompt = prompt + scratchpad

        response = ollama_chat_traced(
            model=MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            options={"stop": ["\nObservation"], "temperature": 0},
        )

        output = response.message.content

        print(f"LLM 输出:\n{output}")

        print(f"  [Parsing] Looking for Final Answer in LLM output...")

        final_answer_match = re.search(r"Final Answer:\s*(.+)", output)

        if final_answer_match:
            final_answer = final_answer_match.group(1).strip()
            print("\n" + "=" * 60)
            print(f"最终答案: {final_answer}")
            return final_answer

        print(f"  [Parsing] Looking for Action and Action Input in LLM output...")

        action_match = re.search(r"Action:\s*(.+)", output)
        action_input_match = re.search(r"Action Input:\s*(.+)", output)

        if not action_match or not action_input_match:
            print(
                "  [Parsing] ERROR: Could not parse Action/Action Input from LLM output"
            )
            break

        tool_name = action_match.group(1).strip()
        tool_input_raw = action_input_match.group(1).strip()

        print(f" [工具选择] {tool_name} 参数: {tool_input_raw}")

        raw_args = [x.strip() for x in tool_input_raw.split(",")]
        args = [x.split("=", 1)[-1].strip().strip("'\"") for x in raw_args]

        print(f"  [工具执行...] {tool_name}({args})...")
        if tool_name not in tools:
            observation = f"Error: Tool '{tool_name}' not found. Available tools: {list(tools.keys())}"
        else:
            observation = str(tools[tool_name](*args))

        print(f"  [工具输出结果] {observation}")

        scratchpad += f"{output}\nObservation: {observation}\nThought:"

    print("ERROR: Max iterations reached without a final answer")
    return None


if __name__ == "__main__":
    print("Hello LangChain Agent (.bind_tools)!")
    print()
    result = run_agent("黄金等级购买笔记本电脑的价格是多少？")
