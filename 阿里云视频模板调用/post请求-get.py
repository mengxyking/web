import requests

# 替换为你的DashScope API密钥和任务ID
YOUR_API_KEY = 'sk-eff868b0d58743c790e3ad7e7f55f0d2'
YOUR_TASK_ID = 'c76a3c20-22c0-466c-9a2b-8d2f644a65b7'

# API请求的URL
url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{YOUR_TASK_ID}'

# 设置请求头部
headers = {
    'Authorization': f'Bearer {YOUR_API_KEY}'
}

# 发送GET请求
response = requests.get(url, headers=headers)

# 处理响应
if response.status_code == 200:
    # 请求成功，打印响应内容（假设服务器返回JSON格式的数据）
    response_data = response.json()
    print('请求成功，响应内容：', response_data)
else:
    # 请求失败，打印错误信息
    print(f'请求失败，状态码：{response.status_code}，响应内容：{response.text}')