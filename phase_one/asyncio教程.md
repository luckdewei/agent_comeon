# Python Asyncio 完整教程

> 从事件循环原理到生产级并发实践，面向有同步编程基础的开发者

---

## 目录

1. [为什么需要异步？](#一为什么需要异步)
2. [核心概念](#二核心概念)
3. [async / await 基础](#三async--await-基础)
4. [Task 与并发](#四task-与并发)
5. [常用 API 速查](#五常用-api-速查)
6. [异步上下文管理器与迭代器](#六异步上下文管理器与迭代器)
7. [asyncio 与同步代码互操作](#七asyncio-与同步代码互操作)
8. [错误处理](#八错误处理)
9. [实战项目：异步批量爬虫](#九实战项目异步批量爬虫)
10. [常见坑与最佳实践](#十常见坑与最佳实践)

---

## 一、为什么需要异步？

### 1.1 同步 vs 异步的本质区别

同步程序在等待 I/O 时会**阻塞整个线程**，CPU 只能干等：

```python
import time

def fetch_data(url):
    time.sleep(2)          # 模拟网络请求，CPU 在这里什么都不做
    return f"data from {url}"

def main():
    start = time.time()
    r1 = fetch_data("http://api-a.com")   # 等 2s
    r2 = fetch_data("http://api-b.com")   # 再等 2s
    r3 = fetch_data("http://api-c.com")   # 再等 2s
    print(f"耗时 {time.time() - start:.1f}s")  # 6.0s

main()
```

异步程序在等待 I/O 时**把控制权交还给事件循环**，让其他任务趁机运行：

```python
import asyncio

async def fetch_data(url):
    await asyncio.sleep(2)   # 挂起当前协程，事件循环去跑别的任务
    return f"data from {url}"

async def main():
    start = asyncio.get_event_loop().time()
    r1, r2, r3 = await asyncio.gather(
        fetch_data("http://api-a.com"),
        fetch_data("http://api-b.com"),
        fetch_data("http://api-c.com"),
    )
    print(f"耗时 {asyncio.get_event_loop().time() - start:.1f}s")  # ~2.0s

asyncio.run(main())
```

**3 个请求并发运行，总耗时从 6s 降到 2s。**

### 1.2 什么时候用异步？

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 大量网络请求（爬虫、API 调用） | asyncio | I/O 密集，等待时间长 |
| 数据库查询 | asyncio + 异步驱动 | 同上 |
| 文件读写（大量小文件） | asyncio | 同上 |
| CPU 密集计算（图像处理、加密） | multiprocessing | 计算密集，异步无帮助 |
| 简单脚本，无并发需求 | 同步即可 | 过度设计 |

---

## 二、核心概念

### 2.1 事件循环（Event Loop）

事件循环是 asyncio 的心脏，负责：
- 调度和运行协程
- 处理 I/O 事件通知
- 管理回调和定时器

```
┌─────────────────────────────────┐
│           Event Loop            │
│                                 │
│  ┌────────┐    ┌─────────────┐  │
│  │ 就绪队列 │───▶│  执行协程    │  │
│  └────────┘    └──────┬──────┘  │
│       ▲               │ await   │
│       │        ┌──────▼──────┐  │
│       └────────│  I/O 事件    │  │
│                │  (epoll)    │  │
│                └─────────────┘  │
└─────────────────────────────────┘
```

### 2.2 协程（Coroutine）

用 `async def` 定义的函数，调用后**不会立即执行**，而是返回一个协程对象：

```python
async def greet(name):
    return f"Hello, {name}"

# 调用只是创建协程对象，不执行
coro = greet("world")
print(type(coro))   # <class 'coroutine'>

# 必须通过事件循环运行
result = asyncio.run(greet("world"))
print(result)       # Hello, world
```

### 2.3 await 关键字

`await` 只能在 `async def` 函数内使用，作用是：
1. 挂起当前协程
2. 把控制权交给事件循环
3. 等待目标完成后恢复执行

```python
async def main():
    print("开始")
    await asyncio.sleep(1)   # 挂起 1 秒，期间事件循环可运行其他协程
    print("1秒后恢复")
```

### 2.4 Task（任务）

Task 是协程的**包装器**，让协程能被事件循环并发调度：

```python
async def main():
    # 直接 await：顺序执行
    await coro_a()    # 等 a 完成
    await coro_b()    # 再等 b 完成

    # 创建 Task：并发执行
    task_a = asyncio.create_task(coro_a())   # 立即开始调度
    task_b = asyncio.create_task(coro_b())   # 立即开始调度
    await task_a      # 等待结果
    await task_b
```

---

## 三、async / await 基础

### 3.1 定义与运行协程

```python
import asyncio

async def say_hello(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    msg = f"Hello, {name}!"
    print(msg)
    return msg

# Python 3.7+ 推荐入口
asyncio.run(say_hello("asyncio", 1.0))
```

### 3.2 顺序 vs 并发对比

```python
import asyncio
import time

async def task(name: str, seconds: float):
    print(f"[{name}] 开始，等待 {seconds}s")
    await asyncio.sleep(seconds)
    print(f"[{name}] 完成")
    return name

async def sequential():
    """顺序执行：总时间 = 所有任务之和"""
    t0 = time.perf_counter()
    await task("A", 1.0)
    await task("B", 1.5)
    await task("C", 0.5)
    print(f"顺序耗时: {time.perf_counter() - t0:.2f}s")  # ~3.0s

async def concurrent():
    """并发执行：总时间 ≈ 最慢的那个"""
    t0 = time.perf_counter()
    await asyncio.gather(
        task("A", 1.0),
        task("B", 1.5),
        task("C", 0.5),
    )
    print(f"并发耗时: {time.perf_counter() - t0:.2f}s")  # ~1.5s

asyncio.run(sequential())
asyncio.run(concurrent())
```

### 🔨 练习 1：实现一个异步倒计时

**要求：** 同时运行 3 个倒计时（5秒、3秒、1秒），每秒打印一次，到 0 时打印 "X 完成"，三个倒计时并发运行。

```python
import asyncio

async def countdown(name: str, seconds: int):
    # TODO: 实现倒计时逻辑
    pass

async def main():
    # TODO: 并发运行三个倒计时
    pass

asyncio.run(main())
```

<details>
<summary>▶ 查看答案</summary>

```python
import asyncio

async def countdown(name: str, seconds: int):
    for i in range(seconds, 0, -1):
        print(f"[{name}] {i}...")
        await asyncio.sleep(1)
    print(f"[{name}] 完成！🎉")

async def main():
    await asyncio.gather(
        countdown("Timer-5", 5),
        countdown("Timer-3", 3),
        countdown("Timer-1", 1),
    )

asyncio.run(main())
```

**预期输出（时序交错）：**
```
[Timer-5] 5...
[Timer-3] 3...
[Timer-1] 1...
[Timer-1] 完成！🎉
[Timer-5] 4...
[Timer-3] 2...
[Timer-5] 3...
[Timer-3] 1...
[Timer-3] 完成！🎉
...
```
</details>

---

## 四、Task 与并发

### 4.1 asyncio.gather() — 并发执行，收集结果

```python
import asyncio

async def fetch(url: str, delay: float) -> dict:
    await asyncio.sleep(delay)
    return {"url": url, "status": 200}

async def main():
    # 所有任务并发，按传入顺序返回结果
    results = await asyncio.gather(
        fetch("http://api-a.com", 1.0),
        fetch("http://api-b.com", 0.5),
        fetch("http://api-c.com", 1.5),
    )
    for r in results:
        print(r)

    # return_exceptions=True：某个任务失败不影响其他任务
    results = await asyncio.gather(
        fetch("http://api-a.com", 1.0),
        fetch("http://bad-url.com", 0.1),
        return_exceptions=True
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"出错了: {r}")
        else:
            print(r)
```

### 4.2 asyncio.create_task() — 创建后台任务

```python
import asyncio

async def background_job(name: str):
    for i in range(3):
        print(f"[{name}] 执行第 {i+1} 步")
        await asyncio.sleep(1)

async def main():
    # create_task 后任务立刻开始（不需要 await 才启动）
    task = asyncio.create_task(background_job("后台任务"))

    # 主逻辑可以同时运行
    print("主逻辑开始运行...")
    await asyncio.sleep(1.5)
    print("主逻辑做了些事情")

    # 最后等待后台任务完成
    await task
    print("所有任务完成")

asyncio.run(main())
```

### 4.3 asyncio.wait() — 更细粒度的控制

```python
import asyncio

async def task(name: str, delay: float):
    await asyncio.sleep(delay)
    return name

async def main():
    tasks = {
        asyncio.create_task(task("fast", 0.5)),
        asyncio.create_task(task("medium", 1.5)),
        asyncio.create_task(task("slow", 3.0)),
    }

    # FIRST_COMPLETED：第一个完成就返回
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for t in done:
        print(f"最先完成: {t.result()}")

    # 取消剩余任务
    for t in pending:
        t.cancel()

asyncio.run(main())
```

### 4.4 asyncio.timeout() — 超时控制（Python 3.11+）

```python
import asyncio

async def slow_operation():
    await asyncio.sleep(10)
    return "完成"

async def main():
    try:
        async with asyncio.timeout(2.0):   # 最多等 2 秒
            result = await slow_operation()
    except TimeoutError:
        print("超时了！")

# Python 3.10 及以下使用 asyncio.wait_for
async def main_old():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
    except asyncio.TimeoutError:
        print("超时了！")

asyncio.run(main())
```

### 🔨 练习 2：带超时的并发请求

**要求：** 模拟 5 个 API 请求（延迟随机 0.5~3s），设置 2s 超时，统计成功和超时的数量。

```python
import asyncio
import random

async def api_call(api_id: int) -> str:
    delay = random.uniform(0.5, 3.0)
    # TODO: 模拟请求，delay 秒后返回结果

async def main():
    # TODO: 并发发起 5 个请求，超过 2s 的视为超时
    # 最后打印: 成功 X 个，超时 Y 个
    pass

asyncio.run(main())
```

<details>
<summary>▶ 查看答案</summary>

```python
import asyncio
import random

async def api_call(api_id: int) -> str:
    delay = random.uniform(0.5, 3.0)
    print(f"  API-{api_id} 开始，预计耗时 {delay:.1f}s")
    await asyncio.sleep(delay)
    return f"API-{api_id} 返回数据"

async def main():
    success = 0
    timeout_count = 0

    tasks = [api_call(i) for i in range(1, 6)]

    results = await asyncio.gather(
        *[asyncio.wait_for(t, timeout=2.0) for t in tasks],
        return_exceptions=True
    )

    for i, r in enumerate(results, 1):
        if isinstance(r, asyncio.TimeoutError):
            print(f"API-{i} ❌ 超时")
            timeout_count += 1
        else:
            print(f"API-{i} ✅ {r}")
            success += 1

    print(f"\n结果：成功 {success} 个，超时 {timeout_count} 个")

asyncio.run(main())
```
</details>

---

## 五、常用 API 速查

### 5.1 asyncio.Queue — 异步队列（生产者-消费者模式）

```python
import asyncio

async def producer(queue: asyncio.Queue, items: list):
    for item in items:
        await queue.put(item)
        print(f"生产: {item}")
        await asyncio.sleep(0.3)
    await queue.put(None)   # 哨兵值，通知消费者结束

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        print(f"[{name}] 消费: {item}")
        await asyncio.sleep(0.5)   # 模拟处理时间
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=3)   # 最多缓存 3 个
    items = ["task-1", "task-2", "task-3", "task-4", "task-5"]

    await asyncio.gather(
        producer(queue, items),
        consumer(queue, "消费者A"),
    )

asyncio.run(main())
```

### 5.2 asyncio.Lock / Semaphore — 并发控制

```python
import asyncio

# Lock：同一时间只允许一个协程访问
lock = asyncio.Lock()

async def safe_update(resource: list, value: int):
    async with lock:
        resource.append(value)     # 临界区，不会被打断
        await asyncio.sleep(0.01)  # 即使有 await 也安全

# Semaphore：限制最大并发数
sem = asyncio.Semaphore(3)   # 最多 3 个协程同时运行

async def limited_request(url: str):
    async with sem:              # 超过 3 个时自动排队等待
        await asyncio.sleep(1)   # 模拟请求
        return f"data from {url}"

async def main():
    # 发起 10 个请求，但最多 3 个同时进行
    urls = [f"http://api.com/{i}" for i in range(10)]
    results = await asyncio.gather(*[limited_request(u) for u in urls])
    print(f"完成 {len(results)} 个请求")

asyncio.run(main())
```

### 5.3 asyncio.Event — 事件通知

```python
import asyncio

async def waiter(event: asyncio.Event, name: str):
    print(f"[{name}] 等待事件...")
    await event.wait()
    print(f"[{name}] 事件触发，开始工作！")

async def trigger(event: asyncio.Event):
    await asyncio.sleep(2)
    print("触发事件！")
    event.set()

async def main():
    event = asyncio.Event()
    await asyncio.gather(
        waiter(event, "Worker-1"),
        waiter(event, "Worker-2"),
        waiter(event, "Worker-3"),
        trigger(event),
    )

asyncio.run(main())
```

---

## 六、异步上下文管理器与迭代器

### 6.1 async with — 异步上下文管理器

```python
import asyncio

class AsyncDB:
    async def __aenter__(self):
        print("连接数据库...")
        await asyncio.sleep(0.1)   # 模拟连接耗时
        print("连接成功")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("关闭数据库连接")
        await asyncio.sleep(0.05)
        return False   # 不抑制异常

    async def query(self, sql: str):
        await asyncio.sleep(0.1)
        return [{"id": 1, "name": "test"}]

async def main():
    async with AsyncDB() as db:
        result = await db.query("SELECT * FROM users")
        print(result)

asyncio.run(main())
```

### 6.2 async for — 异步迭代器

```python
import asyncio

class AsyncRange:
    """异步版 range，每次 yield 前等待一小段时间"""
    def __init__(self, start: int, stop: int):
        self.current = start
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)   # 模拟异步获取数据
        value = self.current
        self.current += 1
        return value

async def main():
    async for num in AsyncRange(0, 5):
        print(f"获取到: {num}")

asyncio.run(main())
```

### 6.3 异步生成器

```python
import asyncio

async def async_fibonacci(limit: int):
    """异步斐波那契生成器"""
    a, b = 0, 1
    while a < limit:
        await asyncio.sleep(0.05)   # 模拟计算延迟
        yield a
        a, b = b, a + b

async def main():
    async for num in async_fibonacci(100):
        print(num, end=" ")
    print()

asyncio.run(main())
```

---

## 七、asyncio 与同步代码互操作

### 7.1 在异步代码中运行同步阻塞函数

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def blocking_io(filename: str) -> str:
    """同步阻塞操作，不能直接 await"""
    time.sleep(1)   # 模拟阻塞读取
    return f"content of {filename}"

def cpu_bound(n: int) -> int:
    """CPU 密集操作"""
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_event_loop()

    # 方法1：run_in_executor 放到线程池（适合 I/O 阻塞）
    result = await loop.run_in_executor(None, blocking_io, "data.txt")
    print(result)

    # 方法2：自定义线程池
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, blocking_io, "big_file.txt")

    # 方法3：ProcessPoolExecutor（适合 CPU 密集）
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_bound, 10_000_000)
        print(f"计算结果: {result}")

asyncio.run(main())
```

### 7.2 在同步代码中调用异步函数

```python
import asyncio

async def async_task() -> str:
    await asyncio.sleep(1)
    return "异步结果"

# 方法1：asyncio.run()（最常用，创建新事件循环）
result = asyncio.run(async_task())

# 方法2：在已有事件循环中（如 Jupyter Notebook）
# import nest_asyncio
# nest_asyncio.apply()
# result = asyncio.run(async_task())

print(result)
```

---

## 八、错误处理

### 8.1 协程内的异常处理

```python
import asyncio

async def risky_task(name: str, should_fail: bool):
    await asyncio.sleep(0.5)
    if should_fail:
        raise ValueError(f"{name} 执行失败！")
    return f"{name} 成功"

async def main():
    # gather 中某个任务失败默认会取消其他任务
    try:
        results = await asyncio.gather(
            risky_task("A", False),
            risky_task("B", True),     # 这个会失败
            risky_task("C", False),
        )
    except ValueError as e:
        print(f"捕获到错误: {e}")

    # return_exceptions=True：所有任务独立运行，失败的返回异常对象
    results = await asyncio.gather(
        risky_task("A", False),
        risky_task("B", True),
        risky_task("C", False),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"❌ {r}")
        else:
            print(f"✅ {r}")

asyncio.run(main())
```

### 8.2 Task 异常与取消

```python
import asyncio

async def cancellable_task():
    try:
        print("任务开始...")
        await asyncio.sleep(10)
        print("任务完成")
    except asyncio.CancelledError:
        print("任务被取消，执行清理...")
        # 可以在这里做清理工作
        raise   # 必须重新抛出 CancelledError

async def main():
    task = asyncio.create_task(cancellable_task())
    await asyncio.sleep(1)

    task.cancel()   # 发送取消信号

    try:
        await task
    except asyncio.CancelledError:
        print("确认任务已取消")

asyncio.run(main())
```

---

## 九、实战项目：异步批量爬虫

综合运用前面所有知识，构建一个完整的异步爬虫系统。

### 9.1 项目结构

```
async_crawler/
├── crawler.py       # 核心爬虫逻辑
├── models.py        # 数据模型
└── main.py          # 入口
```

### 9.2 完整代码

**models.py**
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CrawlResult:
    url: str
    status: int
    content_length: int
    title: Optional[str] = None
    error: Optional[str] = None
    elapsed: float = 0.0

    @property
    def success(self) -> bool:
        return self.error is None
```

**crawler.py**
```python
import asyncio
import time
import re
from dataclasses import dataclass
from typing import Optional
import aiohttp   # pip install aiohttp
from models import CrawlResult

class AsyncCrawler:
    def __init__(
        self,
        concurrency: int = 5,       # 最大并发数
        timeout: float = 10.0,      # 单次请求超时
        retry: int = 2,             # 失败重试次数
    ):
        self.sem = asyncio.Semaphore(concurrency)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retry = retry
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={"User-Agent": "AsyncCrawler/1.0"}
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    def _extract_title(self, html: str) -> Optional[str]:
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None

    async def _fetch_one(self, url: str) -> CrawlResult:
        """单个 URL 抓取，含重试逻辑"""
        last_error = None
        for attempt in range(self.retry + 1):
            try:
                t0 = time.perf_counter()
                async with self.session.get(url) as resp:
                    html = await resp.text(errors="replace")
                    elapsed = time.perf_counter() - t0
                    return CrawlResult(
                        url=url,
                        status=resp.status,
                        content_length=len(html),
                        title=self._extract_title(html),
                        elapsed=elapsed,
                    )
            except asyncio.TimeoutError:
                last_error = "超时"
            except aiohttp.ClientError as e:
                last_error = str(e)

            if attempt < self.retry:
                wait = 2 ** attempt   # 指数退避：1s, 2s
                print(f"  [{url}] 第{attempt+1}次失败，{wait}s 后重试...")
                await asyncio.sleep(wait)

        return CrawlResult(url=url, status=0, content_length=0, error=last_error)

    async def fetch(self, url: str) -> CrawlResult:
        """带并发控制的抓取"""
        async with self.sem:
            return await self._fetch_one(url)

    async def crawl(self, urls: list[str]) -> list[CrawlResult]:
        """批量并发抓取"""
        tasks = [self.fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)
```

**main.py**
```python
import asyncio
import time
from crawler import AsyncCrawler

URLS = [
    "https://httpbin.org/get",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://example.com",
    "https://python.org",
    "https://github.com",
]

async def main():
    print(f"准备爬取 {len(URLS)} 个 URL，并发数：5\n")
    t0 = time.perf_counter()

    async with AsyncCrawler(concurrency=5, timeout=8.0, retry=1) as crawler:
        results = await crawler.crawl(URLS)

    elapsed = time.perf_counter() - t0

    # 打印结果
    print("\n" + "=" * 60)
    print(f"{'URL':<40} {'状态':>5} {'大小':>8} {'耗时':>6}")
    print("=" * 60)

    success_count = 0
    for r in results:
        if r.success:
            success_count += 1
            status_str = str(r.status)
            size_str = f"{r.content_length:,}B"
            time_str = f"{r.elapsed:.2f}s"
        else:
            status_str = "ERR"
            size_str = "-"
            time_str = "-"

        url_short = r.url[:38] + ".." if len(r.url) > 40 else r.url
        icon = "✅" if r.success else "❌"
        print(f"{icon} {url_short:<40} {status_str:>5} {size_str:>8} {time_str:>6}")
        if r.title:
            print(f"   标题: {r.title[:60]}")
        if r.error:
            print(f"   错误: {r.error}")

    print("=" * 60)
    print(f"\n完成！成功 {success_count}/{len(URLS)}，总耗时 {elapsed:.2f}s")
    print(f"（同步串行预计需要 {sum(r.elapsed for r in results if r.success):.1f}s）")

asyncio.run(main())
```

### 9.3 运行

```bash
pip install aiohttp
python main.py
```

### 🔨 练习 3：扩展爬虫功能

在上面爬虫的基础上，完成以下任意一项扩展：

**初级：** 添加进度条，实时显示当前已完成 / 总数

**中级：** 将结果保存到 JSON 文件，支持断点续爬（跳过已爬的 URL）

**高级：** 实现深度爬取，从初始 URL 中提取新链接，最多爬取 2 层，总 URL 数量上限 50 个

<details>
<summary>▶ 初级答案：进度条</summary>

```python
import asyncio
from crawler import AsyncCrawler

async def main_with_progress():
    urls = [...]   # 你的 URL 列表
    total = len(urls)
    done = 0

    async with AsyncCrawler(concurrency=5) as crawler:

        async def fetch_with_progress(url):
            nonlocal done
            result = await crawler.fetch(url)
            done += 1
            bar = "█" * (done * 20 // total) + "░" * (20 - done * 20 // total)
            print(f"\r[{bar}] {done}/{total} {url[:30]}...", end="", flush=True)
            return result

        tasks = [fetch_with_progress(url) for url in urls]
        results = await asyncio.gather(*tasks)

    print()   # 换行
    return results

asyncio.run(main_with_progress())
```
</details>

---

## 十、常见坑与最佳实践

### ⚠️ 坑 1：忘记 await

```python
# ❌ 错误：协程对象没有被 await，直接被忽略
async def main():
    result = fetch_data()    # 返回协程对象，不执行！
    print(result)            # <coroutine object fetch_data at 0x...>

# ✅ 正确
async def main():
    result = await fetch_data()
    print(result)
```

### ⚠️ 坑 2：在异步代码中用同步阻塞调用

```python
import time
import requests   # 同步库

# ❌ 错误：time.sleep 和 requests 会阻塞整个事件循环！
async def bad_fetch():
    time.sleep(1)                        # 阻塞！
    response = requests.get("http://...") # 阻塞！
    return response.text

# ✅ 正确：使用异步库
import asyncio
import aiohttp

async def good_fetch():
    await asyncio.sleep(1)               # 不阻塞
    async with aiohttp.ClientSession() as session:
        async with session.get("http://...") as resp:
            return await resp.text()
```

### ⚠️ 坑 3：并发数量失控

```python
# ❌ 错误：一次性发起 10000 个请求，可能耗尽连接/内存
async def bad_main():
    urls = ["http://api.com"] * 10000
    await asyncio.gather(*[fetch(u) for u in urls])

# ✅ 正确：用 Semaphore 限制并发
async def good_main():
    sem = asyncio.Semaphore(50)   # 最多 50 个并发
    async def limited_fetch(url):
        async with sem:
            return await fetch(url)

    urls = ["http://api.com"] * 10000
    await asyncio.gather(*[limited_fetch(u) for u in urls])
```

### ⚠️ 坑 4：create_task 后忘记 await

```python
# ❌ 危险：任务创建了但没人等它，异常会被静默丢弃
async def bad():
    task = asyncio.create_task(risky())
    # 程序结束，task 还没跑完就被销毁了

# ✅ 正确：始终保存并 await task
async def good():
    task = asyncio.create_task(risky())
    # ... 做其他事 ...
    await task   # 确保任务完成
```

### ✅ 最佳实践总结

| 场景 | 推荐做法 |
|------|---------|
| 并发执行多个独立任务 | `asyncio.gather()` |
| 需要第一个完成就继续 | `asyncio.wait(FIRST_COMPLETED)` |
| 限制最大并发数 | `asyncio.Semaphore` |
| 需要超时控制 | `asyncio.wait_for()` 或 `asyncio.timeout()` |
| 调用阻塞 I/O | `loop.run_in_executor(None, func)` |
| 调用 CPU 密集操作 | `loop.run_in_executor(ProcessPoolExecutor(), func)` |
| 生产者-消费者模式 | `asyncio.Queue` |
| 多协程同步信号 | `asyncio.Event` |
| 保护共享资源 | `asyncio.Lock` |

---

## 附录：常用异步库推荐

| 类别 | 库名 | 说明 |
|------|-----|------|
| HTTP 请求 | `aiohttp` | 最主流的异步 HTTP 客户端/服务端 |
| HTTP 请求 | `httpx` | 支持同步和异步，API 友好 |
| 数据库 | `asyncpg` | PostgreSQL 异步驱动，极快 |
| 数据库 | `aiomysql` | MySQL 异步驱动 |
| Redis | `redis.asyncio` | 官方 Redis 异步客户端 |
| 文件 I/O | `aiofiles` | 异步文件读写 |
| Web 框架 | `FastAPI` | 基于 asyncio 的高性能 API 框架 |
| Web 框架 | `Sanic` | 异步 Web 框架，性能极强 |
| 测试 | `pytest-asyncio` | 异步代码单元测试 |
| 调试 | `aiodebug` | asyncio 性能分析工具 |

---

*教程版本：Python 3.11+  |  最后更新：2026-03*
