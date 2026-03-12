import openai
import os

print(f"正在加载模型配置...")
# 设置 API Key
client = openai.OpenAI(
    api_key=os.environ.get("MODELSCOPE_TOKEN"),
    base_url="https://api-inference.modelscope.cn/v1",
)  # 创建 OpenAI 客户端实例


# 课程封装的辅助函数（贯穿所有章节）
def get_completion(prompt: str, model: str = "deepseek-ai/DeepSeek-V3.2") -> str:
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 输出确定性最高
    )
    return response.choices[0].message.content


# 多轮对话版本（Chatbot 章节用到）
def get_completion_from_messages(
    messages: list, model: str = "deepseek-ai/DeepSeek-V3.2", temperature: float = 0
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
