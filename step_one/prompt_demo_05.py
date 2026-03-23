from llm_config import get_completion

# get_completion("请用一句话介绍一下你自己。", model="qwen3.5:4b")


print(get_completion("请用一句话介绍一下你自己。", model="qwen2.5-coder:latest"))
