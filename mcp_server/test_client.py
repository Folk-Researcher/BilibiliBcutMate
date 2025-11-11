import requests
import time

# 定义服务器地址
SERVER_URL = "http://127.0.0.1:5001/api"

# 定义要添加的字幕列表
captions_to_add = [
    {"text": "你好，这是第一段字幕！", "start_time_ms": 1000, "duration_ms": 4000},
    {"text": "欢迎来到 Bilibili Bcut Mate 项目！", "start_time_ms": 6000, "duration_ms": 5000},
    {"text": "这是使用 MCP 服务器添加的字幕。", "start_time_ms": 12000, "duration_ms": 4000},
    {"text": "感谢使用我们的服务！", "start_time_ms": 17000, "duration_ms": 3000}
]

# 循环添加每段字幕
for caption in captions_to_add:
    # 准备请求数据
    data = {
        "method": "add_caption",
        "params": caption
    }

    # 发送请求
    response = requests.post(SERVER_URL, json=data)

    # 打印响应
    print(f"添加字幕: '{caption['text']}' - Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("-" * 50)

    # 短暂延迟，避免请求过快
    time.sleep(0.5)