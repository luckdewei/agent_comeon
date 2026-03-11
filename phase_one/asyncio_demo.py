import asyncio
import time


def fetch_data(url):
    time.sleep(2)
    return f"data from {url}"


def main1():
    start = time.time()
    r1 = fetch_data("http://api-a.com")  # 等 2s
    r2 = fetch_data("http://api-b.com")  # 再等 2s
    r3 = fetch_data("http://api-c.com")  # 再等 2s
    print(f"耗时 {time.time() - start:.1f}s")  # 6.0s


# main1()


async def fetch_data_async(url):
    await asyncio.sleep(2)  # 挂起当前协程，事件循环去跑别的任务
    return f"data from {url}"


async def main():
    start = asyncio.get_event_loop().time()
    r1, r2, r3 = await asyncio.gather(
        fetch_data_async("http://api-a.com"),
        fetch_data_async("http://api-b.com"),
        fetch_data_async("http://api-c.com"),
    )
    print(f"耗时 {asyncio.get_event_loop().time() - start:.1f}s")  # ~2.0s


asyncio.run(main())
