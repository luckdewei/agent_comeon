from langsmith import traceable


@traceable(run_type="tool")
def get_product_price(product: str) -> float:
    """
    产品目录工具
    在产品目录中查找某件产品的价格
    """
    print(f"    >> get_product_price(product='{product}')")
    prices = {"笔记本电脑": 1299.99, "耳机": 149.95, "键盘": 89.50}
    return prices.get(product, 0)


original_function = getattr(get_product_price, "__wrapped__")

print(f"get_product_price: {get_product_price}")
print(f"original_function: {original_function}")
