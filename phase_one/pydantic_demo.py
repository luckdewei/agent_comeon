from pydantic import BaseModel, Field, ValidationError
from typing import Optional


class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None  # 可选字段，默认 None
    is_active: bool = True  # 有默认值的字段


# 创建实例
user = User(id=1, name="张三", email="zhang@example.com", age=25)
print(user)
# id=1 name='张三' email='zhang@example.com' age=25 is_active=True


try:
    user = User(id="not_a_number", name="王五", email="wang@example.com")
except ValidationError as e:
    print(e)


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="商品名称")
    price: float = Field(gt=0, description="价格，必须大于0")
    stock: int = Field(ge=0, le=9999, default=0)  # 0 ~ 9999
    tags: list[str] = Field(default_factory=list)  # 动态默认值
    sku: Optional[str] = Field(default=None, pattern=r"^[A-Z]{3}\d{6}$")
