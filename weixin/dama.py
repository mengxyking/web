import base64
import time

import requests

# www.jfbym.com  注册后登录去用户中心

def dama_f(path):
    with open(path, 'rb') as f:
        b = base64.b64encode(f.read()).decode()  ## 图片二进制流base64字符串
        url = "http://api.jfbym.com/api/YmServer/customApi"
        data = {
            ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
            "token": "u67GvS5JMav2p1HcBZLuG_m80bH6ngjddS-JbZDTttY",
            "type": "88888",
            "image": b,
        }
        _headers = {
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url, headers=_headers, json=data,timeout=60).json()
        print(response)
        print(response["code"])
        if(response is not None and int(response["code"]) == 10000):
            return response


if __name__ == '__main__':
    bbb = time.time()
    print(dama_f(r"C:\dy_temp\screenshot_20251117_001053.png"))
    print('haoshi = ',time.time() - bbb)

