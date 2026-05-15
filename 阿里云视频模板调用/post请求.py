import requests
import json

# 替换为你的DashScope API密钥
DASHSCOPE_API_KEY = 'sk-793238876737471892408fb2d305e09b'

# API请求的URL
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/'

# 要发送的JSON数据
data = {
    "model": "animate-anyone-gen2",
    "input": {
        "image_url": "http://39.106.24.175:5557/downloads/111.jpg",
        "template_id": "AACT.8090e67b.7GAnLsE3Ee-X8Na1j4PL-A.tz-WS-oE"
    },
    "parameters": {
        "use_ref_img_bg": True,
        "video_ratio": "9:16"
    }
}

# 设置请求头部
headers = {
    'X-DashScope-Async': 'enable',
    'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
    'Content-Type': 'application/json'
}

# 发送POST请求
response = requests.post(url, headers=headers, data=json.dumps(data))

# 处理响应
if response.status_code == 200:
    # 请求成功，打印响应内容（假设服务器返回JSON格式的数据）
    response_data = response.json()
    print('请求成功，响应内容：', response_data)
else:
    # 请求失败，打印错误信息
    print(f'请求失败，状态码：{response.status_code}，响应内容：{response.text}')