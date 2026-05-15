import requests
import json

# 替换为你的DashScope API密钥
YOUR_API_KEY = 'sk-eff868b0d58743c790e3ad7e7f55f0d2'

# API请求的URL
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/aa-template-generation/'

# 要发送的JSON数据
data = {
    "model": "animate-anyone-template-gen2",
    "input": {
        "video_url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241210/cwjmsz/1.mp4"
    },
    "parameters": {}
}

# 设置请求头部
headers = {
    'X-DashScope-Async': 'enable',
    'Authorization': f'Bearer {YOUR_API_KEY}',
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