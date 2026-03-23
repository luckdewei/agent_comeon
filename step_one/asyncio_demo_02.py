import asyncio


async def greet(name):
    return f"Hello, {name}"


# 调用只是创建协程对象，不执行
coro = greet("world")
print(type(coro))  # <class 'coroutine'>


# 必须通过事件循环运行
result = asyncio.run(greet("world"))
print(result)  # Hello, world
