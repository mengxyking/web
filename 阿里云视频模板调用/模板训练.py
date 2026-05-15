import requests
import json

# 替换为你的API密钥
api_key = 'sk-eff868b0d58743c790e3ad7e7f55f0d2'

# 请求的URL
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/aa-template-generation/'

# 请求头
headers = {
    'X-DashScope-Async': 'enable',
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# 请求体
data = {
    "model": "animate-anyone-template-gen2",
    "input": {
        "video_url": "http://39.106.24.175:5557/downloads/%E5%85%AB%E6%96%B9%E6%9D%A5%E8%B4%A2.mp4"
    },
    "parameters": {}
}

# 发送POST请求
response = requests.post(url, headers=headers, data=json.dumps(data))

# 输出响应状态码和响应内容
print('Status Code:', response.status_code)
print('Response:', response.json())