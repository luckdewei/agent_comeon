# diagnostic.py
import requests
import subprocess
import time

print("=" * 50)
print("Ollama 诊断工具")
print("=" * 50)

# 1. 检查 Ollama 进程
print("\n1. 检查 Ollama 进程...")
result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
if "ollama" in result.stdout:
    print("✅ Ollama 进程存在")
else:
    print("❌ Ollama 进程不存在，请运行: ollama serve")

# 2. 检查端口
print("\n2. 检查 11434 端口...")
result = subprocess.run(["lsof", "-i", ":11434"], capture_output=True, text=True)
if "ollama" in result.stdout:
    print("✅ 端口 11434 被 Ollama 占用")
else:
    print("❌ 端口 11434 未被占用")

# 3. 测试基础连接
print("\n3. 测试基础连接...")
try:
    r = requests.get("http://localhost:11434", timeout=5)
    print(f"✅ 基础连接成功: {r.status_code}")
    print(f"   响应: {r.text}")
except Exception as e:
    print(f"❌ 基础连接失败: {e}")

# 4. 测试 API 端点
print("\n4. 测试 API 端点...")
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    if r.status_code == 200:
        models = r.json().get("models", [])
        print(f"✅ API 端点正常，找到 {len(models)} 个模型")
        for m in models:
            print(f"   - {m['name']}")
    else:
        print(f"❌ API 返回 {r.status_code}")
except Exception as e:
    print(f"❌ API 测试失败: {e}")

# 5. 测试 OpenAI 兼容端点
print("\n5. 测试 OpenAI 兼容端点...")
try:
    r = requests.get("http://localhost:11434/v1/models", timeout=5)
    if r.status_code == 200:
        print("✅ OpenAI 兼容端点正常")
        models = r.json().get("data", [])
        for m in models:
            print(f"   - {m['id']}")
    else:
        print(f"❌ OpenAI 端点返回 {r.status_code}")
        print(f"   响应: {r.text}")
except Exception as e:
    print(f"❌ OpenAI 端点测试失败: {e}")

# 6. 测试模型加载
print("\n6. 测试模型加载...")
try:
    # 先检查模型是否存在
    r = requests.post(
        "http://localhost:11434/api/show", json={"name": "qwen3.5:4b"}, timeout=5
    )
    if r.status_code == 200:
        print("✅ 模型 qwen3.5:4b 存在")
    else:
        print(f"❌ 模型不存在或加载失败: {r.status_code}")

    # 尝试简单的生成
    print("\n   尝试简单生成...")
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen3.5:4b", "prompt": "你好", "stream": False},
        timeout=30,
    )
    if r.status_code == 200:
        print("✅ 生成成功!")
        print(f"   回复: {r.json().get('response', '')[:50]}...")
    else:
        print(f"❌ 生成失败: {r.status_code}")
        print(f"   响应: {r.text}")
except Exception as e:
    print(f"❌ 模型测试失败: {e}")

print("\n" + "=" * 50)
print("诊断完成")
print("=" * 50)
