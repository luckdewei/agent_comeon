import asyncio
import time


# async def task(name: str, seconds: float):
#     print(f"[{name}] 开始，等待 {seconds}s")
#     await asyncio.sleep(seconds)
#     print(f"[{name}] 完成")
#     return name


# async def sequential():
#     """顺序执行：总时间 = 所有任务之和"""
#     t0 = time.perf_counter()
#     await task("A", 1.0)
#     await task("B", 1.5)
#     await task("C", 0.5)
#     print(f"顺序耗时: {time.perf_counter() - t0:.2f}s")  # ~3.0s


# async def concurrent():
#     """并发执行：总时间 ≈ 最慢的那个"""
#     t0 = time.perf_counter()
#     await asyncio.gather(
#         task("A", 1.0),
#         task("B", 1.5),
#         task("C", 0.5),
#     )
#     print(f"并发耗时: {time.perf_counter() - t0:.2f}s")  # ~1.5s


# asyncio.run(sequential())
# asyncio.run(concurrent())


async def countdown(name: str, seconds: int):
    # TODO: 实现倒计时逻辑
    for i in range(seconds, 0, -1):
        print(f"[{name}] {i}秒")
        await asyncio.sleep(1)
    print(f"[{name}] 完成！")


async def main():
    # TODO: 并发运行三个倒计时
    await asyncio.gather(
        countdown("A", 5),
        countdown("B", 3),
        countdown("C", 4),
    )


asyncio.run(main())
