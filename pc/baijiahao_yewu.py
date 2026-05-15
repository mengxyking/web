import base64
import chardet
import random
import requests
import subprocess
import sys
import json
import os
import threading
from util.paddleOCR_json_duixiang import OCRProcessor
import time

import pyautogui
from PIL import ImageGrab
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                         QHBoxLayout, QLabel, QLineEdit, QPushButton,
                         QGroupBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator


clicked_user = []
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    print("00000000000000000000000000---------")
    print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def photo():
    Ui_file_Name = str(int(time.time())) + "_ui.png"
    path = getPhotoPath() + "/" + Ui_file_Name
    #screenshot = pyautogui.screenshot()
    screenshot = ImageGrab.grab()
    screenshot.save(path)

    return path

def photo_region(left, top, width, height):
    Ui_file_Name = str(int(time.time())) + "_ui.png"
    path = getPhotoPath() + "/" + Ui_file_Name
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(path)
    return path


def kill_app_by_name(process_name):
    """
    通过进程名杀死应用程序
    :param process_name: 进程名（如 "notepad.exe"、"chrome.exe"）
    """
    try:
        # 使用taskkill命令杀死进程，/F表示强制终止，/IM指定进程名
        result = subprocess.run(
            f'taskkill /F /IM {process_name}',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"成功杀死进程: {process_name}")
        else:
            print(f"杀死进程失败: {process_name}，错误信息: {result.stderr}")
    except Exception as e:
        print(f"操作出错: {str(e)}")

def start_program_by_exe(exe_path):
    """
    根据EXE文件路径启动程序

    :param exe_path: EXE文件的完整路径
    :return: 启动成功返回进程对象，失败返回None
    """
    # 验证路径是否有效
    if not exe_path:
        print("错误：未提供EXE文件路径")
        return None

    # 检查文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误：文件不存在 - {exe_path}")
        return None

    # 检查是否是EXE文件
    if not os.path.isfile(exe_path) or not exe_path.lower().endswith('.exe'):
        print(f"错误：不是有效的EXE文件 - {exe_path}")
        return None

    try:
        # 启动程序，stdout和stderr重定向到DEVNULL以避免控制台输出
        # creationflags=subprocess.CREATE_NEW_CONSOLE 用于在新窗口中启动程序
        process = subprocess.Popen(
            exe_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform.startswith('win') else 0
        )

        print(f"成功启动程序：{os.path.basename(exe_path)} (PID: {process.pid})")
        return process

    except Exception as e:
        print(f"启动程序失败：{str(e)}")
        return None

def control(ocr_processor,exe_path):
    #fabu(ocr_processor)
    #yanzheng(ocr_processor)
    kill_app_by_name("创作罐头.exe")
    time.sleep(2)
    start_program_by_exe(exe_path)
    time.sleep(8)
    temp_file = photo()
    alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_file,temp_file))
    print(alldata)
    fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "创作罐头")
    if (fabuzuopin_point != None):
        print("shouye")
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3, duration=random.uniform(0.2, 0.9))
        pyautogui.doubleClick()
        pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
        print("确定")
        time.sleep(3)


    while (True):

        alldata = ocr_processor.getAllData(photo())
        fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "关闭全部")
        if (fabuzuopin_point != None):
            pyautogui.moveTo(x=fabuzuopin_point[0], y=fabuzuopin_point[1],duration=random.uniform(0.2, 0.9))
            pyautogui.click()
            pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
            print("关闭全部")
            time.sleep(3)

            alldata = ocr_processor.getAllData(photo())
            fabuzuopin_point = ocr_processor.getPoint_by_data_true(alldata, "确定")
            if (fabuzuopin_point != None):
                pyautogui.moveTo(x=fabuzuopin_point[0], y=fabuzuopin_point[1],duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("确定")
                time.sleep(3)

        print("")
        result_switch = switch_user(ocr_processor)
        print("result_switch=", result_switch)

        if (result_switch == "99"):
            kill_app_by_name("创作罐头.exe")
            time.sleep(2)
            start_program_by_exe(exe_path)
            time.sleep(8)
            temp_file = photo()
            alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_file, temp_file))
            print(alldata)
            fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "创作罐头")
            if (fabuzuopin_point != None):
                print("shouye")
                pyautogui.moveTo(x=fabuzuopin_point[0] + random.randint(0, 6) - 3,
                                 y=fabuzuopin_point[1] + random.randint(0, 6) - 3, duration=random.uniform(0.2, 0.9))
                pyautogui.doubleClick()
                pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
                print("确定")
                time.sleep(3)
        if (result_switch != True):
            continue
        time.sleep(6)

        # 疯狂点击下一步 或者完成
        result_xiayibu = xiayibu(ocr_processor)
        if (result_xiayibu != True):
            continue
        time.sleep(6)

        result_inTer_fabu = inTer_fabu(ocr_processor)
        if (result_inTer_fabu != True):
            continue
        time.sleep(6)

        result_shengchengwenan = shengchengwenan(ocr_processor)
        if (result_shengchengwenan != True):
            continue
        time.sleep(6)
        print("开始发布-------")
        fabu(ocr_processor)

def swipe_tuozhuai(A_x, A_y, B_x, B_y):
    import pyautogui
    import time
    # A点和B点的坐标（这里假设的坐标，你需要根据你的屏幕和需要来设置）
    # 可选：移动到A点（如果你知道鼠标当前不在A点）
    pyautogui.mouseDown(button='left', x=A_x, y=A_y)
    # 移动鼠标到B点（同时鼠标左键是按下的）
    pyautogui.moveTo(B_x, B_y, duration=1.25)  # duration参数表示移动所需的时间（秒）

    # 释放鼠标左键
    pyautogui.mouseUp(button='left', x=B_x, y=B_y)

    # 等待一段时间以便你可以看到鼠标移动和拖拽的效果（可选）
    time.sleep(1)
def extract_number_from_response(json_text):
    """
    从API返回的JSON文本中提取data字段里的数字（如260#_ → 260）
    :param json_text: API返回的原始JSON字符串（如'{"success":true,"msg":"执行成功","data":"260#_"}'）
    :return: 提取到的数字（字符串格式，如需整数可转int），失败返回None
    """
    try:
        # 1. 解析JSON字符串为Python字典
        response_dict = json.loads(json_text)

        # 2. 获取data字段的值（先判断是否存在，避免KeyError）
        data_value = response_dict.get("data")
        if not data_value:
            print("❌ 未找到data字段或data值为空")
            return None

        # 3. 提取数字部分（按"#"分割，取分割后的第一部分）
        # 示例："260#_" → 分割后为["260", "_"]，取第一个元素
        number_str = data_value.split("#")[0]

        # 4. 可选：验证是否为数字（确保提取结果正确）
        if number_str.isdigit():
            return number_str  # 返回字符串格式，如需整数可改为 return int(number_str)
        else:
            print(f"❌ 提取到的内容不是数字：{number_str}")
            return None

    except json.JSONDecodeError:
        print("❌ JSON格式解析失败，检查返回文本是否为合法JSON")
        return None
    except Exception as e:
        print(f"❌ 提取数字出错：{str(e)}")
        return None

def send_request_with_image(img_bin):
    url = "http://localhost:8080/runtime/bea62ff1-fdd9-4b41-b01e-6fbd8be3750d/invoke"
    try:
        response = requests.post(
            url,
            data=img_bin,
            timeout=30
        )
        response_bytes = response.content
        print("response_bytes=",response_bytes)

        # （原编码转换逻辑不变，此处省略，最终得到result_text：API返回的JSON文本）
        try:
            utf8_text = response_bytes.decode("utf-8")
            gb2312_bytes = utf8_text.encode("gb2312", errors="replace")
            result_text = gb2312_bytes.decode("gb2312")
        except UnicodeDecodeError:
            detected_encoding = chardet.detect(response_bytes)["encoding"] or "gb2312"
            result_text = response_bytes.decode(detected_encoding, errors="replace")

        # ------------------- 新增：提取260 -------------------
        extracted_number = extract_number_from_response(result_text)
        if extracted_number:
            print(f"✅ 成功提取数字：{extracted_number}")
            # 此处可直接使用提取的数字（如260），或返回给调用者
            return extracted_number  # 改为返回提取的数字，而非原始文本
        else:
            print("❌ 数字提取失败")
            return None
        # -----------------------------------------------------

    except requests.exceptions.RequestException as e:
        print(f"请求出错：{str(e)}")
        return None
    else:
        print("没有浏览器")
        return None
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
def send_image_to_api( image_path):
    api_key = "2579722a0cb69d776909a678774c9227"
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
        return response.json()["data"]["px_distance"]
    except requests.exceptions.RequestException as e:
        print(f"API请求失败：{str(e)}")
        return None

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

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
def yanzheng(ocr_processor):
    print("kaishi................")
    point = ocr_processor.getPoint_BY_PaddleOCRJson_true(photo(), "百度安全验证")
    if (point != None):
        print(point)
        x_t = point[0]
        y_t = point[1]
        pyautogui.moveTo(x=point[0]+random.randint(0, 6) - 3, y=point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        print("有打开")
        time.sleep(1)
        print(point[0] - 100, point[1], point[0] - 100 + 500, point[1] + 600)
        result_p = photo_region(point[0]+10, point[1]+55, 170, 170)
        print(result_p)
        imageBack = photo_region(point[0] - 100, point[1] -15, 333, 410)
        print(imageBack)
        result = base64_api(uname='13424199671', pwd='Aa00000000', img=result_p, typeid=1029, img_back=imageBack)
        print(result)

        time.sleep(2)

        if (is_integer(result)):
            print("当前返回的是数字")
            result = int(result)
            if (result < 0):
                dure = (result + 360) / 360 * 243
            else:
                dure = result / 360 * 243
            print("dure=", dure)
            x = point[0] - 27
            y = point[1] + 267
            swipe_tuozhuai(x, y, x + dure, y)

        # with open(result_p, "rb") as f:
        #     img_bin = f.read()

        # 发送请求并获取结果
        #response_text = send_request_with_image(img_bin)
        # response_text = send_image_to_api(result_p)
        # if(response_text):
        #     res_t = int(response_text)
        #     print(res_t)
        #     if (res_t > 0):
        #         duresion = res_t + 6
        #     else:
        #         duresion = (360 - res_t) / 360 * 280
        #     print("duresion=",duresion)
        #
        #
        #     x = x_t - 27
        #     y = y_t + 266
        #     print(x, y, x + duresion, y)
        #     swipe_tuozhuai(x, y, x + duresion, y)
        # else:
        #     return False

def fabu(ocr_processor):

    for i in range(20):
        print("i=",i)

        temp_path = photo()
        Ui_file_Name = str(int(time.time())) + "_ui.png"
        path = getPhotoPath() + "/" + Ui_file_Name
        alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path, path))
        print("alldata111=", alldata)

        fabushipin_fafafa = ocr_processor.getPoint_by_data(alldata, "发布视")
        fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "位置没有")
        baiduanquanyanzheng = ocr_processor.getPoint_by_data(alldata, "百度安全验证")
        tuwen = ocr_processor.getPoint_by_data_true(alldata, "图文")
        fabudao_baijiahao = ocr_processor.getPoint_by_data(alldata, "发布到百家号")
        fuwuqi_kaixiaochai = ocr_processor.getPoint_by_data(alldata, "服务器开了小差")
        jixufabu = ocr_processor.getPoint_by_data(alldata, "继续发布")
        if (jixufabu != None):
            pyautogui.moveTo(x=jixufabu[0]+random.randint(0, 6) - 3, y=jixufabu[1]+random.randint(0, 6) - 3, duration=random.uniform(0.2, 0.9))
            pyautogui.click()
            pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
            print("jixufabu")
            time.sleep(4)
        if(fabudao_baijiahao != None):
            pyautogui.moveTo(x=fabudao_baijiahao[0]+random.randint(0, 6) - 3, y=fabudao_baijiahao[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
            pyautogui.click()
            pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
            print("发布视频")
            time.sleep(4)
        elif (fabuzuopin_point != None):
            while (True):
                alldata = ocr_processor.getAllData(photo())
                print("alldata=", alldata)
                fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "位置没有")
                print("fabuzuopin_point111=", fabuzuopin_point)
                if (fabuzuopin_point != None):
                    alldata = ocr_processor.getAllData(photo())
                    fabuzuopin_point = ocr_processor.getPoint_text_by_data(alldata, "本地素材")
                    if (fabuzuopin_point != None):

                        first_key = next(iter(fabuzuopin_point))  # 获取第一个键
                        first_value = fabuzuopin_point[first_key]
                        print("first_key=",first_key)
                        print("first_value=", first_value)
                        if (str(first_value).count("中")):
                            pyautogui.moveTo(x=first_value[0]+ 30, y=first_value[1]+random.randint(0, 6) - 3 , duration=random.uniform(0.2, 0.9))
                            pyautogui.click()
                            pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
                            print("本地素材")
                            time.sleep(4)

                        else:
                            pyautogui.moveTo(x=first_value[0]+70, y=first_value[1], duration=random.uniform(0.2, 0.9))
                            pyautogui.click()
                            pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
                            print("视觉中国")
                            time.sleep(4)
                        alldata = ocr_processor.getAllData(photo())
                        fabuzuopin_point = ocr_processor.getPoint_by_data_true(alldata, "视频")
                        sousuojieguo = ocr_processor.getPoint_by_data(alldata, "搜索结果")
                        if (sousuojieguo != None):
                            return False
                        elif (fabuzuopin_point != None):
                            pyautogui.moveTo(x=fabuzuopin_point[0] + 20, y=fabuzuopin_point[1] + 100,
                                             duration=random.uniform(0.2, 0.9))
                            pyautogui.click()
                            time.sleep(2)
                            pyautogui.click()
                            time.sleep(2)
                            pyautogui.click()
                            time.sleep(2)
                            pyautogui.click()
                            time.sleep(2)
                            # pyautogui.moveTo(1, 1)
                            print("视频")
                            time.sleep(4)
                            if (fabushipin_fafafa):
                                pyautogui.moveTo(x=fabushipin_fafafa[0], y=fabushipin_fafafa[1],
                                                 duration=random.uniform(0.2, 0.9))
                                pyautogui.click()
                            time.sleep(2)

                        else:
                            print("7777")
                            return False
                    else:
                        print("8888")
                        return False
                else:
                    break
        elif (baiduanquanyanzheng != None):
            yanzheng(ocr_processor)
        elif (tuwen != None):
            return True
        elif (fuwuqi_kaixiaochai != None):
            return False
        elif (fabushipin_fafafa != None):
            pyautogui.moveTo(x=fabushipin_fafafa[0]+random.randint(0, 6) - 3, y=fabushipin_fafafa[1]+random.randint(0, 6) - 3, duration=random.uniform(0.2, 0.9))
            pyautogui.click()
            pyautogui.moveTo(1, 1, duration=random.uniform(0.2, 0.9))
            print("发布视频")
            time.sleep(4)






def shengchengwenan(ocr_processor):

    alldata = ocr_processor.getAllData(photo())
    print(alldata)
    fabuzuopin_point111 = ocr_processor.getPoint_by_data(alldata, "我的积分")
    if (fabuzuopin_point111 != None):
        pyautogui.moveTo(x=fabuzuopin_point111[0]+random.randint(0, 6) - 3, y=fabuzuopin_point111[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        # pyautogui.moveTo(1, 1)
        print("我的积分")
        time.sleep(3)
    else:
        print("9999")
        return False

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "领取")
    ling_point = ocr_processor.getPoint_by_data(alldata, "规则")
    #qu_point = ocr_processor.getPoint_by_data_back(alldata, "领")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("领取")
        time.sleep(4)
    elif(ling_point != None):
        pyautogui.moveTo(x=ling_point[0]+random.randint(0, 6) - 3, y=ling_point[1]+50,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("规则")
        time.sleep(4)

    # else:
    #     return False
    if (fabuzuopin_point111 != None):
        pyautogui.moveTo(x=fabuzuopin_point111[0]-300, y=fabuzuopin_point111[1],duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        # pyautogui.moveTo(1, 1)
        print("取消弹窗")
        time.sleep(1)

    swipe_count = random.randint(0,20)

    alldata = ocr_processor.getAllData(photo())
    print(alldata)
    fabuzuopin_point_quanwang = ocr_processor.getPoint_by_data_true(alldata, "全网")
    if (fabuzuopin_point_quanwang != None):
        pyautogui.moveTo(x=fabuzuopin_point_quanwang[0]+random.randint(100,300), y=fabuzuopin_point_quanwang[1] + 400,duration=random.uniform(0.2, 0.9))
        print("swipe_count=",swipe_count)
        for i in range(swipe_count):
            print("i=",i)
            pyautogui.scroll(random.randint(-500,-100))
            time.sleep(0.1)
        print("guandong")
        time.sleep(3)
    else:
        print("10101010")
        return False

    alldata = ocr_processor.getAllData(photo())
    print("----",alldata)
    fabuzuopin_point = ocr_processor.getPoint_BY_PaddleOCRJsons_area_from_alldata(alldata, "生成文",fabuzuopin_point_quanwang[0],fabuzuopin_point_quanwang[0]+500,0,9999)
    fabuzuopin_point_wenwen = ocr_processor.getPoint_BY_PaddleOCRJsons_area_from_alldata(alldata, "生成",fabuzuopin_point_quanwang[0],fabuzuopin_point_quanwang[0]+500,0,9999)
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        time.sleep(2)
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布视频")
        time.sleep(6)
    elif(fabuzuopin_point_wenwen != None):
        pyautogui.moveTo(x=fabuzuopin_point_wenwen[0]+random.randint(0, 6) - 3, y=fabuzuopin_point_wenwen[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        time.sleep(2)
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布视频")
        time.sleep(6)
    else:
        print("1212121212")
        return False

    time.sleep(15)

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "窗口")
    if (fabuzuopin_point != None):
        print("13131313")
        return False

    temp_path = photo()
    Ui_file_Name = str(int(time.time())) + "_ui.png"
    path = getPhotoPath() + "/" + Ui_file_Name
    alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path, path))
    print("alldata111=", alldata)
    fabuzuopin_point = ocr_processor.getPoint_by_data_back(alldata, "成片")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0], y=fabuzuopin_point[1],duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("一键成片")
        time.sleep(6)
    else:
        print("141414")
        return False

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "积分不足")
    if (fabuzuopin_point != None):
        print("15151515")
        return False

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data_true(alldata, "知道了")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布视频")
        time.sleep(6)

    for i in range(15):
        alldata = ocr_processor.getAllData(photo())
        print(alldata)
        fabuzuopin_point111 = ocr_processor.getPoint_by_data(alldata, "补充中")
        if (fabuzuopin_point111 != None):
            print("you 补  充中")
            time.sleep(3)
        else:
            print("meiyiou 补   充中")
            return True

        time.sleep(3)

        if(i>=14):
            print("16161616")
            return False


def inTer_fabu(ocr_processor):
    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data(alldata, "发布作品")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布作品")
        time.sleep(3)
    else:
        print("1111")
        return False

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data_true(alldata, "视频")
    zhanghao_zhiliang_buzu = ocr_processor.getPoint_by_data(alldata, "账号内容质量不足")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布视频")
        time.sleep(6)
    elif(zhanghao_zhiliang_buzu != None):
        print("账号内容质量不足，退出")
        return False
    else:
        print("2222")
        return False

    alldata = ocr_processor.getAllData(photo())
    fabuzuopin_point = ocr_processor.getPoint_by_data_true(alldata, "在线创作")
    if (fabuzuopin_point != None):
        pyautogui.moveTo(x=fabuzuopin_point[0]+random.randint(0, 6) - 3, y=fabuzuopin_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
        pyautogui.click()
        pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
        print("发布视频")
        time.sleep(6)
    else:
        print("3333")
        return False

    return True
def xiayibu(ocr_processor):
    try:
        # alldata = self.ocr_processor.getAllData(self.photo())
        # xiayibu_point = self.ocr_processor.getPoint_by_data(alldata, "账号已被封停")
        # print(xiayibu_point)
        time.sleep(4)
        while (True):
            print("开始下一步")
            temp_path = photo()
            Ui_file_Name = str(int(time.time())) + "_ui.png"
            path = getPhotoPath() + "/" + Ui_file_Name
            alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path,path))
            print("alldata111=",alldata)
            xiayibu_point = ocr_processor.getPoint_by_data(alldata, "下一步")
            wancheng_point = ocr_processor.getPoint_by_data_true(alldata, "完成")
            lijitiyan_point = ocr_processor.getPoint_by_data(alldata, "立即体验")
            liji_point = ocr_processor.getPoint_by_data(alldata, "立即111")
            tiyan_point = ocr_processor.getPoint_by_data(alldata, "体验")
            https = ocr_processor.getPoint_by_data(alldata, "创作罐头")
            baijiahao = ocr_processor.getPoint_by_data(alldata, "baijiahao")
            baidu = ocr_processor.getPoint_by_data(alldata, "baidu")
            print("xiayibu_point=", xiayibu_point)
            if (xiayibu_point != None):
                pyautogui.moveTo(x=xiayibu_point[0]+random.randint(0, 6) - 3, y=xiayibu_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                time.sleep(2)
                pyautogui.click()
                time.sleep(2)
                pyautogui.click()
                time.sleep(1)
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (wancheng_point != None):
                pyautogui.moveTo(x=wancheng_point[0]+random.randint(0, 6) - 3, y=wancheng_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))

            elif (lijitiyan_point != None):
                pyautogui.moveTo(x=lijitiyan_point[0]+random.randint(0, 6) - 3, y=lijitiyan_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (liji_point != None):
                pyautogui.moveTo(x=liji_point[0]+random.randint(0, 6) - 3, y=liji_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (tiyan_point != None):
                pyautogui.moveTo(x=tiyan_point[0]+random.randint(0, 6) - 3, y=tiyan_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (https != None):
                print("开始点击刷新1")
                pyautogui.moveTo(x=https[0] + 248, y=https[1]+45,duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                break
            elif (baijiahao != None):
                print("开始点击刷新2")
                pyautogui.moveTo(x=baijiahao[0] - 130, y=baijiahao[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                break
            elif (baidu != None):
                print("开始点击刷新3")
                pyautogui.moveTo(x=baidu[0] - 130, y=baidu[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                break
            else:
                print("shibai")
                return False
            time.sleep(3)


        while (True):
            print("开始下一步")
            temp_path = photo()
            Ui_file_Name = str(int(time.time())) + "_ui.png"
            path = getPhotoPath() + "/" + Ui_file_Name
            alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path, path))
            print("alldata111=", alldata)
            xiayibu_point = ocr_processor.getPoint_by_data(alldata, "下一步")
            wancheng_point = ocr_processor.getPoint_by_data_true(alldata, "完成")
            lijitiyan_point = ocr_processor.getPoint_by_data(alldata, "立即体验")
            liji_point = ocr_processor.getPoint_by_data(alldata, "立即111")
            tiyan_point = ocr_processor.getPoint_by_data(alldata, "体验")
            https = ocr_processor.getPoint_by_data(alldata, "创作罐头")
            baijiahao = ocr_processor.getPoint_by_data(alldata, "baijiahao")
            baidu = ocr_processor.getPoint_by_data(alldata, "baidu")
            print("xiayibu_point=", xiayibu_point)
            if (xiayibu_point != None):
                pyautogui.moveTo(x=xiayibu_point[0]+random.randint(0, 6) - 3, y=xiayibu_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                time.sleep(2)
                pyautogui.click()
                time.sleep(2)
                pyautogui.click()
                time.sleep(0.1)
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (wancheng_point != None):
                pyautogui.moveTo(x=wancheng_point[0]+random.randint(0, 6) - 3, y=wancheng_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))

            elif (lijitiyan_point != None):
                pyautogui.moveTo(x=lijitiyan_point[0]+random.randint(0, 6) - 3, y=lijitiyan_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (liji_point != None):
                pyautogui.moveTo(x=liji_point[0]+random.randint(0, 6) - 3, y=liji_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (tiyan_point != None):
                pyautogui.moveTo(x=tiyan_point[0]+random.randint(0, 6) - 3, y=tiyan_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (https != None):
                print("开始点击刷新1")
                pyautogui.moveTo(x=https[0] + 248, y=https[1] + 45, duration=random.uniform(0.2, 0.9))

                time.sleep(1)
                pyautogui.click()
                time.sleep(3)
                break
            elif (baijiahao != None):
                print("开始点击刷新2")
                pyautogui.moveTo(x=baijiahao[0] - 130, y=baijiahao[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                break
            elif (baidu != None):
                print("开始点击刷新3")
                pyautogui.moveTo(x=baidu[0] - 130, y=baidu[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                break
            else:
                print("shibai")
                return False
            time.sleep(3)
        while (True):
            print("开始下一步")
            temp_path = photo()
            Ui_file_Name = str(int(time.time())) + "_ui.png"
            path = getPhotoPath() + "/" + Ui_file_Name
            alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path, path))
            print("alldata111=", alldata)
            xiayibu_point = ocr_processor.getPoint_by_data_true(alldata, "下一步")
            wancheng_point = ocr_processor.getPoint_by_data_true(alldata, "完成")
            lijitiyan_point = ocr_processor.getPoint_by_data_true(alldata, "立即体验")
            https = ocr_processor.getPoint_by_data(alldata, "创作罐头")
            baijiahao = ocr_processor.getPoint_by_data(alldata, "baijiahao")
            baidu = ocr_processor.getPoint_by_data(alldata, "baidu")
            print("xiayibu_point=", xiayibu_point)
            if (xiayibu_point != None):
                pyautogui.moveTo(x=xiayibu_point[0]+random.randint(0, 6) - 3, y=xiayibu_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1)
                print("有打开")
            elif (wancheng_point != None):
                pyautogui.moveTo(x=wancheng_point[0]+random.randint(0, 6) - 3, y=wancheng_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (lijitiyan_point != None):
                pyautogui.moveTo(x=lijitiyan_point[0]+random.randint(0, 6) - 3, y=lijitiyan_point[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                pyautogui.click()
                pyautogui.moveTo(1, 1,duration=random.uniform(0.2, 0.9))
                print("有打开")
            elif (https != None):
                print("开始点击刷新1")
                pyautogui.moveTo(x=https[0] + 248, y=https[1] + 45, duration=random.uniform(0.2, 0.9))

                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                return True
            elif (baijiahao != None):
                print("开始点击刷新2")
                pyautogui.moveTo(x=baijiahao[0] - 130, y=baijiahao[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                return True
            elif (baidu != None):
                print("开始点击刷新3")
                pyautogui.moveTo(x=baidu[0] - 130, y=baidu[1],duration=random.uniform(0.2, 0.9))
                time.sleep(1)
                pyautogui.click()
                time.sleep(5)
                return True
            else:
                print("shibai")
                return False
            time.sleep(3)
    except BaseException as e:
        print(e)
        print("5555")
        return False


def switch_user(ocr_processor):
    try:
        # points_user = []
        time.sleep(3)
        # point = self.ocr_processor.getPoint_BY_PaddleOCRJson(self.photo(), "发布")
        temp_path = photo()
        Ui_file_Name = str(int(time.time())) + "_ui.png"
        path = getPhotoPath() + "/" + Ui_file_Name
        alldata = ocr_processor.getAllData(ocr_processor.convert_to_black_white(temp_path, path))
        print("alldata111=", alldata)
        shoujihao_point = ocr_processor.getPoint_by_data(alldata, "手机号等")
        print("shoujihao_point=", shoujihao_point)
        points_user = ocr_processor.getPointsAndTexts_by_data_from_small_area(alldata, "未认证", 0,
                                                                                   shoujihao_point[0] + 100,
                                                                                   shoujihao_point[1], 99999)
        # print("points_user=", points_user)
        point_yinggai = None
        print("points_user=",points_user)

        for point_user in points_user:
            print(point_user)
            if (str(point_user).count("未认证") > 0):
                xunhao = str(point_user).split("未认证")[1][0:3]
                if (xunhao not in clicked_user):
                    # print(xunhao, "没有被点击", points_user[point_user])
                    point_yinggai = points_user[point_user]
                    clicked_user.append(xunhao)
                    print(point_yinggai)
                    pyautogui.moveTo(x=point_yinggai[0]+random.randint(0, 6) - 3, y=point_yinggai[1]+random.randint(0, 6) - 3,duration=random.uniform(0.2, 0.9))
                    time.sleep(1)
                    pyautogui.click()
                    pyautogui.click()
                    print("有打开")
                    time.sleep(2)
                    pyautogui.moveTo(x=1, y=1,duration=random.uniform(0.2, 0.9))
                    time.sleep(2)
                    return True
            if (str(point_user).count("结束") > 0):
                return "99"

        if (point_yinggai == None):
            print("开始滑动-----")
            pyautogui.moveTo(x=shoujihao_point[0]+random.randint(0, 6) - 3, y=shoujihao_point[1] + 50,duration=random.uniform(0.2, 0.9))
            time.sleep(1)
            pyautogui.scroll(-100)
            time.sleep(1)
            pyautogui.scroll(-200)
            time.sleep(1)
            pyautogui.scroll(-100)
    except BaseException as e:
        print(e)
        switch_user(ocr_processor)
# ocr_processor = OCRProcessor()
# fabu(ocr_processor)

#
# with open(r"C:\Users\Administrator\Desktop\11111111.png", "rb") as f:
#     img_bin = f.read()
#
# # 发送请求并获取结果
# response_text = send_request_with_image(img_bin)