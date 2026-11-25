#!/usr/bin/env python
import subprocess
import time

# Kill existing python processes
subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
time.sleep(2)

# Start the server
proc = subprocess.Popen(
    [".\\venv\\Scripts\\python.exe", "-m", "uvicorn", "mains:app", "--port", "8091", "--host", "127.0.0.1"],
    cwd="E:\\Desktop_Backup\\ABUS_WEB\\John-Report\\fastAPI\\demo1",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for startup
time.sleep(3)

# Test the API
import urllib.request
import json

try:
    url = "http://127.0.0.1:8091/file/pandian-all"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("✓ API测试成功!")
        print(f"  状态: {data.get('status')}")
        print(f"  数据条目数: {len(data.get('data', {}))}")
except Exception as e:
    print(f"✗ API测试失败: {e}")

# Kill server after test
proc.terminate()
proc.wait()
print("服务已停止")