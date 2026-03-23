from llm_config import get_completion

prod_review = """
我女儿生日买了这个熊猫毛绒玩具，她非常喜欢，随身携带。\
玩具很柔软，表情超可爱，它的脸看起来很友好。\
不过对于我支付的价格来说它有点小，我认为相同价格可以买到更大的。\
比预期提前一天到了，所以在送给女儿之前我先玩了一会儿。
"""

prompt = f"""
您的任务是从电子商务网站上生成一个产品评论的简短摘要。
请对下面三个反引号之间的评论文本进行概括，最多30个词汇。

评论：```{prod_review}```
"""

response = get_completion(prompt, model="qwen2.5-coder:latest")
print(response)

# 批量
reviews = [
    "这款灯具外观漂亮，价格也不贵，收货很快...",
    "我需要一盏卧室台灯，这款有额外储物空间...",
    "我丈夫喜欢这款电动牙刷，感觉更换刷头方便...",
    "买给女儿当礼物，她喜欢这款化妆镜...",
]

for i, review in enumerate(reviews):
    prompt = f"""
    你的任务是从电子商务网站上生成一个产品评论的简短摘要，
    最多20个词。
    
    评论文本：```{review}```
    """
    response = get_completion(prompt, model="qwen2.5-coder:latest")
    print(f"评论 {i+1}：{response}\n")
