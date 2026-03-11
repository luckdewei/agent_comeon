# Pydantic

Python 数据验证完整教程

从入门到实战 · 适用于 Pydantic v2

## 一、什么是 Pydantic

Pydantic 是 Python 生态中最流行的数据验证库，它使用 Python 类型注解来定义数据结构，自动完成类型转换、数据校验和序列化。Pydantic v2 在 v1 基础上进行了重写，性能提升超过 50 倍。

Pydantic 核心理念：**用 Python 类型注解描述数据模型，库负责验证和转换。**

### 1.1 主要特性

- 基于 Python 标准类型注解，学习成本低
- 自动类型转换（如字符串转整数）
- 内置丰富的验证器
- 完整的 JSON Schema 支持
- 与 FastAPI、SQLModel 等框架深度集成
- v2 版本核心用 Rust 编写，性能极强

### 1.2 安装

```bash
# 安装 Pydantic v2
pip install pydantic

# 验证安装
python -c "import pydantic; print(pydantic.VERSION)"

# 如需 email 验证支持
pip install pydantic[email]
```

## 二、BaseModel 基础用法

所有 Pydantic 模型都继承自 BaseModel。定义模型时，使用类型注解声明字段，Pydantic 会自动处理验证逻辑。

### 2.1 定义第一个模型

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None  # 可选字段，默认 None
    is_active: bool = True      # 有默认值的字段

# 创建实例
user = User(id=1, name='张三', email='zhang@example.com', age=25)
print(user)
# id=1 name='张三' email='zhang@example.com' age=25 is_active=True
```

### 2.2 自动类型转换

Pydantic 会尝试将输入值转换为目标类型，而不是直接报错：

```python
user = User(id='42', name='李四', email='li@example.com')  # id 传入字符串
print(user.id)       # 42 (自动转换为 int)
print(type(user.id)) # <class 'int'>
```

> **💡 提示** 如需严格模式（禁止自动转换），可在 model_config 中设置 strict=True。

### 2.3 验证失败

```python
from pydantic import ValidationError

try:
    user = User(id='not_a_number', name='王五', email='wang@example.com')
except ValidationError as e:
    print(e)
    # 1 validation error for User
    # id
    #   Input should be a valid integer [type=int_parsing, ...]
```

### 2.4 模型方法

```python
user = User(id=1, name='张三', email='zhang@example.com')

# 转为字典
print(user.model_dump())
# {'id': 1, 'name': '张三', 'email': 'zhang@example.com', 'age': None, 'is_active': True}

# 转为 JSON 字符串
print(user.model_dump_json())

# 从字典创建
data = {'id': 2, 'name': '李四', 'email': 'li@example.com'}
user2 = User.model_validate(data)

# 从 JSON 字符串创建
user3 = User.model_validate_json('{"id": 3, "name": "王五", "email": "w@example.com"}')
```

## 三、字段（Field）详解

Field() 函数用于为字段提供额外的元数据和验证约束：

### 3.1 Field 常用参数

```python
from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description='商品名称')
    price: float = Field(gt=0, description='价格，必须大于0')
    stock: int = Field(ge=0, le=9999, default=0)  # 0 ~ 9999
    tags: list[str] = Field(default_factory=list)  # 动态默认值
    sku: Optional[str] = Field(default=None, pattern=r'^[A-Z]{3}\d{6}$')
```

### 3.2 Field 参数速查

| 参数            | 说明                    | 示例                        |
| --------------- | ----------------------- | --------------------------- |
| default         | 默认值                  | Field(default=0)            |
| default_factory | 动态默认值（函数）      | Field(default_factory=list) |
| gt / ge         | 大于 / 大于等于（数字） | Field(gt=0)                 |
| lt / le         | 小于 / 小于等于（数字） | Field(le=100)               |
| min_length      | 最小长度（字符串/列表） | Field(min_length=1)         |
| max_length      | 最大长度                | Field(max_length=50)        |
| pattern         | 正则表达式              | Field(pattern=r'^\d+$')     |
| description     | 字段描述（用于文档）    | Field(description='用户ID') |
| alias           | 序列化/反序列化别名     | Field(alias='user_id')      |
| exclude         | 序列化时排除该字段      | Field(exclude=True)         |

### 3.3 别名（Alias）

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    item_id: int = Field(alias='itemId')     # 输入时使用 itemId
    item_name: str = Field(alias='itemName') # 输入时使用 itemName

# 使用别名创建
item = Item.model_validate({'itemId': 1, 'itemName': '手机'})
print(item.item_id)  # 1

# 序列化时使用别名输出
print(item.model_dump(by_alias=True))
# {'itemId': 1, 'itemName': '手机'}
```

## 四、验证器（Validator）

Pydantic 提供了强大的自定义验证器机制，可以对字段值进行任意逻辑验证。

### 4.1 field_validator

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    email: str
    password: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('姓名不能为空')
        return v

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v.lower()  # 统一转小写

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        return v
```

### 4.2 model_validator（跨字段验证）

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: str
    end_date: str

    @model_validator(mode='after')
    def check_date_order(self) -> 'DateRange':
        if self.start_date >= self.end_date:
            raise ValueError('开始日期必须早于结束日期')
        return self
```

> **⚠️ 注意** mode='before' 在类型转换前运行（接收原始输入），mode='after' 在转换后运行（接收已验证的值）。

## 五、嵌套模型与复杂类型

### 5.1 嵌套模型

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    city: str
    province: str
    zip_code: str

class Order(BaseModel):
    order_id: int
    shipping_address: Address  # 嵌套模型
    items: List[str]

order = Order(
    order_id=1001,
    shipping_address={'city': '上海', 'province': '上海', 'zip_code': '200000'},
    items=['手机', '耳机']
)
print(order.shipping_address.city)  # 上海
```

### 5.2 常用类型注解

| 类型                     | 说明                              | 示例                                  |
| ------------------------ | --------------------------------- | ------------------------------------- |
| str / int / float / bool | 基本类型                          | name: str                             |
| Optional[T]              | 可选类型，等价于 T \| None        | age: Optional[int] = None             |
| List[T]                  | 列表                              | tags: List[str]                       |
| Dict[K, V]               | 字典                              | meta: Dict[str, Any]                  |
| Tuple[T, ...]            | 元组                              | coords: Tuple[float, float]           |
| Set[T]                   | 集合（自动去重）                  | ids: Set[int]                         |
| Union[A, B]              | 联合类型                          | value: Union[int, str]                |
| Literal['a', 'b']        | 枚举字面量                        | status: Literal['active', 'inactive'] |
| datetime / date          | 日期时间（自动解析）              | created_at: datetime                  |
| HttpUrl                  | URL 验证                          | website: HttpUrl                      |
| EmailStr                 | 邮箱验证（需安装email-validator） | email: EmailStr                       |

### 5.3 使用 Annotated 组合约束

```python
from typing import Annotated
from pydantic import BaseModel, Field

# 使用 Annotated 复用约束定义
PositiveInt = Annotated[int, Field(gt=0)]
ShortStr = Annotated[str, Field(max_length=50)]

class Product(BaseModel):
    name: ShortStr
    quantity: PositiveInt
    price: PositiveInt
```

## 六、模型配置（model_config）

### 6.1 ConfigDict 常用配置项

```python
from pydantic import BaseModel
from pydantic import ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        strict=False,                # 是否开启严格模式
        str_strip_whitespace=True,   # 自动去除字符串首尾空白
        str_to_lower=False,          # 字符串统一转小写
        use_enum_values=True,        # 枚举字段存储 value 而非枚举对象
        populate_by_name=True,       # 允许用字段名或别名创建
        frozen=False,                # True 时实例不可变（类似 dataclass frozen）
        extra='ignore',              # 忽略额外字段（也可设为 'forbid' 或 'allow'）
        validate_default=True,       # 对默认值也进行验证
    )
    name: str
    age: int
```

### 6.2 extra 字段处理策略

| extra 值         | 行为                                        |
| ---------------- | ------------------------------------------- |
| 'ignore'（默认） | 忽略额外字段，不报错                        |
| 'forbid'         | 发现额外字段时抛出 ValidationError          |
| 'allow'          | 保留额外字段，可通过 model.model_extra 访问 |

## 七、序列化与反序列化

### 7.1 model_dump() 常用参数

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    password: str = Field(exclude=True)  # 默认排除
    email: Optional[str] = None

user = User(id=1, name='张三', password='secret', email=None)

# 基本导出
user.model_dump()  # {'id': 1, 'name': '张三', 'email': None}

# 排除 None 值
user.model_dump(exclude_none=True)  # {'id': 1, 'name': '张三'}

# 排除未设置的字段
user.model_dump(exclude_unset=True)

# 手动包含/排除
user.model_dump(include={'id', 'name'})
user.model_dump(exclude={'email'})
```

### 7.2 JSON 序列化

```python
import json
from datetime import datetime
from pydantic import BaseModel

class Event(BaseModel):
    name: str
    created_at: datetime

event = Event(name='会议', created_at=datetime.now())

# 序列化为 JSON 字符串（datetime 自动转为 ISO 格式）
json_str = event.model_dump_json()
print(json_str)  # {"name":"会议","created_at":"2024-01-15T10:30:00"}

# 从 JSON 字符串反序列化（datetime 字符串自动解析）
event2 = Event.model_validate_json(json_str)
print(type(event2.created_at))  # <class 'datetime.datetime'>
```

## 八、实战案例：FastAPI 接口数据验证

Pydantic 与 FastAPI 的集成是最常见的使用场景之一。以下是一个完整的用户注册/登录 API 示例：

### 8.1 定义请求/响应模型

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

# 注册请求体
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str

    @field_validator('username')
    @classmethod
    def username_lowercase(cls, v):
        return v.lower()

# 响应体（不暴露密码）
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
```

### 8.2 FastAPI 路由

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post('/register', response_model=UserResponse)
async def register(data: RegisterRequest):
    # FastAPI 自动验证请求体，验证失败返回 422
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail='两次密码不一致')

    # 模拟保存数据库
    return UserResponse(
        id=1,
        username=data.username,
        email=data.email,
        created_at=datetime.now()
    )
```

## 九、常见问题与最佳实践

### 9.1 常见问题

| ❓ **v1 和 v2 的主要区别？** | v2 使用 model_dump() 替代 dict()，model_validate() 替代 parse_obj()，@field_validator 替代 @validator。性能提升显著，但部分 API 不兼容。 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |

| ❓ **如何处理循环引用？** | 使用 model_rebuild() 方法，或使用 from **future** import annotations 进行延迟求值。 |
| ------------------------- | ----------------------------------------------------------------------------------- |

| ⚠️ **性能提示** | 频繁创建大量模型实例时，考虑使用 model_construct() 跳过验证（仅在数据来源可信时使用）。 |
| --------------- | --------------------------------------------------------------------------------------- |

### 9.2 最佳实践

- 将模型定义在独立文件（如 schemas.py）中，与业务逻辑分离
- 为字段添加 description，方便生成 API 文档
- 使用 exclude=True 保护敏感字段（如 password），避免序列化泄露
- 复用类型约束时，使用 Annotated 创建语义化类型
- 合理使用 model_config 统一控制模型行为，避免在各字段重复配置
- 生产环境中尽量在模型入口处验证数据，而不是在业务层做大量手动校验

### 9.3 推荐学习资源

| 资源                         | 说明                                     |
| ---------------------------- | ---------------------------------------- |
| https://docs.pydantic.dev    | 官方文档（最权威）                       |
| https://fastapi.tiangolo.com | FastAPI 官方文档（含大量 Pydantic 示例） |
| pydantic GitHub Issues       | 社区问题与最佳实践讨论                   |

---

_本教程基于 Pydantic v2 编写_
