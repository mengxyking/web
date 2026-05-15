import requests
import json
import base64


def image_to_base64(image_path):
    """将图片文件转换为Base64编码字符串"""
    try:
        with open(image_path, "rb") as image_file:
            # 读取图片内容并转换为Base64
            base64_str = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_str
    except FileNotFoundError:
        print(f"错误：找不到图片文件 {image_path}")
        return None
    except Exception as e:
        print(f"转换图片时发生错误：{str(e)}")
        return None


def send_image_to_api(api_key, image_path):
    """将图片的Base64编码发送到API"""
    # 转换图片为Base64
    base64_image = image_to_base64(image_path)
    if not base64_image:
        return None

    url = f"https://api.decodecaptcha.com/images?key={api_key}&image_id=3201101"

    # 构建请求 payload，将Base64字符串放入参数
    payload = json.dumps({
        "image": base64_image,  # 图片的Base64编码
        "title":"aaa"
    })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=payload,verify=False)
        response.raise_for_status()  # 检查请求是否成功
        print(response.json()["data"]["px_distance"])
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"API请求失败：{str(e)}")
        return None


if __name__ == "__main__":
    # 配置参数
    API_KEY = "2579722a0cb69d776909a678774c9227"  # 替换为你的实际API密钥
    IMAGE_PATH = r"C:\Users\Administrator\Desktop\565656.png"  # 替换为你的图片路径（支持jpg、png等格式）

    # 发送图片
    result = send_image_to_api(API_KEY, IMAGE_PATH)

    if result:
        print("API响应结果：")
        print(json.dumps(json.loads(result), indent=2))  # 格式化输出响应
