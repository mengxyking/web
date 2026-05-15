import requests

# 替换为你的DashScope API密钥
DASHSCOPE_API_KEY = 'sk-eff868b0d58743c790e3ad7e7f55f0d2'

# API请求的URL
url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/aa-detect'

# 要发送的表单数据
data = {
    'model': 'animate-anyone-detect-gen2',
    'parameters': {}  # 如果parameters需要非空数据，请在这里添加
}

# 本地图片文件的路径
image_path = r"C:\Users\Administrator\Desktop\rumeng.jpg"

# 设置请求头部和文件
headers = {
    'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
    # 注意：当使用files参数时，Content-Type会自动设置为multipart/form-data
    # 因此，你不需要在这里手动设置Content-Type
}
files = {
    'input': (image_path, open(image_path, 'rb'), 'image/jpeg')  # 假设图片是JPEG格式
}

# 发送POST请求
response = requests.post(url, headers=headers, data=data, files=files)

# 处理响应
if response.status_code == 200:
    # 请求成功，打印响应内容（假设服务器返回JSON格式的数据）
    response_data = response.json()
    print('请求成功，响应内容：', response_data)
else:
    # 请求失败，打印错误信息
    print(f'请求失败，状态码：{response.status_code}，响应内容：{response.text}')