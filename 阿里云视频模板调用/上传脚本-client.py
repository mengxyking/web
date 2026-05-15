import requests
import os
image_path = r'C:\Users\Administrator\Desktop\rumeng.jpg'
upload_url = 'http://39.106.24.175:5557/upload'

with open(image_path, 'rb') as image_file:
    files = {'file': (os.path.basename(image_path), image_file)}  # 注意：这里不需要指定MIME类型，requests会自动处理
    response = requests.post(upload_url, files=files)

print(response.status_code, response.text)