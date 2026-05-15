import base64
import json
import requests
import time


# 一、图片文字类型(默认 3 数英混合)：
# 1 : 纯数字
# 1001：纯数字2
# 2 : 纯英文
# 1002：纯英文2
# 3 : 数英混合
# 1003：数英混合2
#  4 : 闪动GIF
# 7 : 无感学习(独家)
# 11 : 计算题
# 1005:  快速计算题
# 16 : 汉字
# 32 : 通用文字识别(证件、单据)
# 66:  问答题
# 49 :recaptcha图片识别
# 二、图片旋转角度类型：
# 29 :  旋转类型
# 1029 :  背景匹配旋转类型 注意：中间小图传到image中，背景图传到imageback 中 imageback模仿image 添加
# 2029 :  背景匹配双旋转类型 注意：中间小图传到image中，背景图传到imageback 中  imageback模仿image 添加
#
# 三、图片坐标点选类型：
# 19 :  1个坐标
# 20 :  3个坐标
# 21 :  3 ~ 5个坐标
# 22 :  5 ~ 8个坐标
# 27 :  1 ~ 4个坐标
# 48 : 轨迹类型
#
# 四、缺口识别
# 18 : 缺口识别（需要2张图 一张目标图一张缺口图）
# 33 : 单缺口识别（返回X轴坐标 只需要1张图）
# 34 : 缺口识别2（返回X轴坐标 只需要1张图）
# 五、拼图识别
# 53：拼图识别
def base64_api(uname, pwd, img, typeid,img_back):
    with open(img, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        b64 = base64_data.decode()
    with open(img_back, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        img_back = base64_data.decode()
    data = {"username": uname, "password": pwd, "typeid": typeid, "image": b64,"imageBack":img_back}
    result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        #！！！！！！！注意：返回 人工不足等 错误情况 请加逻辑处理防止脚本卡死 继续重新 识别
        return result["message"]
    return ""
def swipe_tuozhuai(A_x, A_y, B_x, B_y):
    import pyautogui
    import time
    # A点和B点的坐标（这里假设的坐标，你需要根据你的屏幕和需要来设置）
    # 可选：移动到A点（如果你知道鼠标当前不在A点）
    pyautogui.mouseDown(button='left', x=A_x, y=A_y)
    # 移动鼠标到B点（同时鼠标左键是按下的）
    pyautogui.moveTo(B_x, B_y, duration=1.25)  # duration参数表示移动所需的时间（秒）

    # 释放鼠标左键
    #pyautogui.mouseUp(button='left', x=B_x, y=B_y)

    # 等待一段时间以便你可以看到鼠标移动和拖拽的效果（可选）
    time.sleep(3)
def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    img_path = r"C:\Users\Administrator\Desktop\2222.png"
    imageBack = r"C:\Users\Administrator\Desktop\6666.png"
    result = base64_api(uname='13424199671', pwd='Aa00000000', img=img_path, typeid=1029,img_back = imageBack)
    print(result)

    time.sleep(5)

    if(is_integer(result)):
        print("当前返回的是数字")
        result = int(result)
        if(result < 0 ):
            dure = (result + 360) / 360 * 245
        else:
            dure = result  / 360 * 245
        print("dure=",dure)
        swipe_tuozhuai(673,523,673 + dure,523)


