import cv2
import shutil
import sys
import threading
import random
from PIL import Image
import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QRadioButton, QLineEdit,
    QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from util.paddleOCR_json_duixiang import OCRProcessor
ocr_processor = OCRProcessor()
import os
import pickle
current_scroll_position = 0
import time

alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()
from ultralytics import YOLO
def shibie(model,image_path,zhixindu):
    results = model(image_path)
    #results[0].show()
    result_cls = {}
    for r in results:
        # 假设results中只有一个元素，代表一张图片的检测结果
        # 提取类别、置信度和边界框坐标
        classes = r.boxes.cls.cpu().numpy()  # 类别索引
        confidences = r.boxes.conf.cpu().numpy()  # 置信度
        coordinates = r.boxes.xyxy.cpu().numpy()  # 边界框坐标 (x_min, y_min, x_max, y_max)

        # 遍历每个检测到的目标
        for cls, conf, coord in zip(classes, confidences, coordinates):
            # 计算中心点坐标
            x_center = (coord[0] + coord[2]) / 2
            y_center = (coord[1] + coord[3]) / 2
            # 打印结果
            if(conf > zhixindu):
                result_cls[cls] = (x_center,y_center)
            #print(f"Class: {cls}, Confidence: {conf}, Center Coordinates: ({x_center}, {y_center})")

        return result_cls

def get_top_line_and_del(file):
    # 获取锁
    with file_lock:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            #print("----------------")
            #print(lines)
            if not lines:
                #print("lines为空")
                return None
            temp_str = lines[0].strip()  # 直接转换为字符串并去除换行符

        # 重新打开文件以写入，这里可以优化为在读取后不移除文件指针直接截断文件
        with open(file, 'w', encoding='utf-8') as f:
            # 写入除了第一行之外的所有行
            f.writelines(str(line).strip() + '\n' for i, line in enumerate(lines) if i != 0)
            # 或者使用更简洁的方式，但注意这种方式会保留原始行的换行符（如果需要去除，可以使用strip()）
            # f.writelines(lines[1:])  # 这将保留第二行及之后的换行符，如果需要去除每行的换行符，需要先strip()

    return temp_str
def get_device(serial):
    #d = ""
    #print("之前的d", d)
    #print(f"正在连接设备: {serial}")
    d = u2.connect(serial)
    d.watcher.remove()
    return d
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    #print("00000000000000000000000000---------")
    #print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def photo(s):
    Ui_file_Name =  str(int(time.time()))+"_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    return path
def get_files_in_directory(directory_path):
    files = []
    try:
        # 创建一个 Path 对象
        path = Path(directory_path)

        # 检查路径是否存在且是一个目录
        if not path.exists() or not path.is_dir():
            print(f"The directory {directory_path} does not exist or is not a directory.")
            return files

            # 遍历目录中的所有文件并添加到列表中
        for file_path in path.iterdir():
            if file_path.is_file():
                files.append(file_path)
    except PermissionError:
        print(f"Permission denied to access {directory_path}.")

    return files  # 将 Path 对象转换为字符串列表


from pathlib import Path


def create_directory_if_not_exists(directory_path):
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

    # 示例用法


import os


def create_file_if_not_exists(file_path):
    if not os.path.isfile(file_path):
        # 如果文件不存在，则创建它（这里只是创建一个空文件）
        with open(file_path, 'w') as file:
            file.write('')  # 或者你可以写入一些初始内容
        print(f"File '{file_path}' created.")
    else:
        print(f"File '{file_path}' already exists.")

    # 示例用法


def compare_with_file(target_string, file_path):
    # 打开文件并读取所有行
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return False

        # 遍历每一行，并进行比较
    for line in lines:
        # 去除每行末尾的换行符
        line = line.strip()
        # 分割每行，获取+前面的内容
        parts = line.split('+')
        if len(parts) > 0:
            # 获取+前面的部分
            prefix = parts[0]
            # 比较字符串
            if prefix == target_string:
                return True

                # 如果遍历完所有行都没有找到匹配项，则返回False
    return False

def find_string_in_file(file_path, search_string,phone_num):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                temps = line.split("+")
                if(len(temps)>1):
                    #if ((search_string == temps[0]) and (temps[1][0:2] == str(phone_num)[0:2] )):
                    if (search_string == temps[0]):
                        return line.strip()  # 使用strip()去掉行尾的换行符
        return None  # 如果没有找到，则返回None
    except FileNotFoundError:
        #print(f"The file {file_path} was not found.")
        return None

    # 示例用法



def is_close_to_any(num, B, tolerance=50):
    for b in B:
        if 0 < num - b <= tolerance:
            return True
    return False


def shell_neibu(cmd):
    os.system(cmd)

def get_random_pkl_file_in_directory(directory):
    # 获取目录下所有 .pkl 文件的列表
    pkl_files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
    print("pkl_files=",pkl_files)

    # 如果没有 .pkl 文件，则直接返回 False
    if not pkl_files:
        return False
    with video_lock:
        # 循环直到找到一个满足条件的文件或者所有文件都不满足条件
        while pkl_files:
            # 随机选择一个 .pkl 文件
            chosen_file = random.choice(pkl_files)
            file_path = os.path.join(directory, chosen_file)
            # 从列表中移除已选择的文件，以便在下次循环时不再选择它
            pkl_files.remove(chosen_file)
            # 尝试读取文件内容
            try:
                with open(file_path, 'rb') as file:
                    data = pickle.load(file)
                # 检查数据是否满足条件
                if 'TONGJI' in data and 'BIG_COUNT' in data and isinstance(int(data['TONGJI']), (int, float)) and isinstance(
                        int(data['BIG_COUNT']), (int, float)):
                    print("tongji=",int(data['TONGJI']))
                    print("BIG_COUNT=", int(data['BIG_COUNT']))
                    if int(data['TONGJI']) < int(data['BIG_COUNT']):
                        return chosen_file
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        # 如果没有文件满足条件，则返回 False
        return False
def load_pkl(pklfile):
    with video_lock:
        if(os.path.exists(pklfile)):
            with open(pklfile, 'rb') as pkl_file:
                my_object111 = pickle.load(pkl_file)
                return my_object111
        else:
            return None
def get_connected_devices111():
    """获取已连接的安卓设备列表"""
    try:
        # 运行 adb devices 命令
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 检查命令是否成功执行
        if result.returncode != 0:
            print(f"Error running adb devices: {result.stderr}")
            return []

        # 解析输出
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        devices = [line.split('\t')[0] for line in lines if line.strip() and line.split('\t')[1] == 'device']
        return devices
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
def find_devices_with_name_containing(substring):
    """查找设备名称包含指定子字符串的设备"""
    connected_devices = get_connected_devices111()
    print(connected_devices)

    # 获取设备名称（假设设备名称在 `adb devices -l` 的输出中）
    for device in connected_devices:
        try:
            # 使用 adb -l 获取详细设备信息
                if substring in device:
                    return device
        except Exception as e:
            print(f"An error occurred for device {device}: {e}")
    return None
def operate_device(serial, dir_path, task,big,small,jiarenshuliang,shifouquxiaojiaoyi):
    code,txt = yewu(serial, dir_path, task,big,small,jiarenshuliang,shifouquxiaojiaoyi)
    if(code == 0 ):
        filepath = './shuju/' + serial + ".pkl"
        print("filepath-->", filepath)
        if (os.path.isfile(filepath)):
            updata_pkl(filepath, "执行状态", str(txt))
            updata_pkl(filepath, "进行的任务", "空闲")
            return
    else:
        filepath = './shuju/' + serial + ".pkl"
        print("filepath-->", filepath)
        updata_pkl(filepath, "执行状态", "执行完毕")
        updata_pkl(filepath, "进行的任务", "空闲")
def image_quzao(path):
    image_path = path  # 替换为你的图片路径
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 检查图片是否成功加载
    if image is None:
        print("Error: Could not load image.")
        exit()
    a_path = photo("serial")
    cv2.imwrite(a_path, image)
    return a_path
def yewu(serial, dir_path, task,big,small,jiarenshuliang,shifouquxiaojiaoyi):
    device_name = find_devices_with_name_containing(serial)
    print("device_name=",device_name)
    d = get_device(device_name)

    model = YOLO(r"best.pt")

    path = photo(serial)
    print("path=", path)
    screenshot_image = d.screenshot()
    screenshot_image.save(path)
    result = shibie(model, path, 0.1)
    print("识别结果=", result)
    if (4444.0 in result.keys()):
        print("坐标是----》", result[4.0][0], result[4.0][1])
        d.click(result[4.0][0], result[4.0][1])
    else:
        d.click(d.info["displayWidth"] - 35, 35)
        # d.click(d.info["displayWidth"] - 35, 35)
        # d.click(d.info["displayWidth"] - 35, 35)
    time.sleep(4)

    path = photo(serial)
    print("path=", path)
    screenshot_image = d.screenshot()
    screenshot_image.save(path)
    result = shibie(model, path, 0.1)
    print("识别结果=", result)
    if (5.0 in result.keys()):
        print("坐标是----》", result[5.0][0], result[5.0][1])
        d.click(result[5.0][0], result[5.0][1])
        d.click(result[5.0][0], result[5.0][1])
        d.click(result[5.0][0], result[5.0][1])
    elif (3.0 in result.keys()):
        print("坐标是----》", result[3.0][0], result[3.0][1])
        d.click(result[3.0][0] - 115, result[3.0][1])
        d.click(result[3.0][0] - 115, result[3.0][1])
        d.click(result[3.0][0] - 115, result[3.0][1])
    elif (1.0 in result.keys()):
        print("坐标是----》", result[1.0][0], result[1.0][1])
        d.click(result[1.0][0], (d.info["displayHeight"] - 80) / 2)
        d.click(result[1.0][0], (d.info["displayHeight"] - 80) / 2)
        d.click(result[1.0][0], (d.info["displayHeight"] - 80) / 2)
    else:
        print("交易图标定位失败")
        return 0,"交易图标定位失败"
    time.sleep(2)

    path = photo(serial)
    print("path=", path)
    screenshot_image = d.screenshot()
    screenshot_image.save(path)
    result = shibie(model, path, 0.1)
    print("识别结果=", result)
    if (6.0 in result.keys()):
        print("坐标是----》", result[6.0][0], result[6.0][1])
        d.click(result[6.0][0], result[6.0][1])
    else:
        print("交易tab定位失败")
        return 0,"交易tab定位失败"

    count_shouzuanshi = 0
    while (count_shouzuanshi < 4):
        time.sleep(2)
        # 进来之后先收钻石
        path = photo(serial)
        print("path=", path)
        screenshot_image = d.screenshot()
        screenshot_image.save(path)
        result = shibie(model, path, 0.1)
        print("识别结果=", result)
        if (8.0 in result.keys()):
            print("坐标是----》", result[8.0][0], result[8.0][1])
            d.click(result[8.0][0], result[8.0][1])
            time.sleep(1.5)
        else:
            print("当前没有收取钻石")
            break
        count_shouzuanshi += 1

    if(shifouquxiaojiaoyi == True):
        while (True):
            time.sleep(1.5)
            # 进来之后先取消交易
            path = photo(serial)
            print("path=", path)
            screenshot_image = d.screenshot()
            screenshot_image.save(path)
            result = shibie(model, path, 0.1)
            print("识别结果=", result)
            if (9.0 in result.keys()):
                print("坐标是----》", result[9.0][0], result[9.0][1])
                d.click(result[9.0][0], result[9.0][1])
                time.sleep(1.5)
                d.click(716, 496)
                time.sleep(1.5)
            else:
                print("当前没有需要取消的交易")
                break

    count = 0
    target_x = 0
    target_y = 0
    while (count < 28):
        time.sleep(1.5)
        if (target_x == 0):
            path = photo(serial)
            print("path=", path)
            screenshot_image = d.screenshot()
            screenshot_image.save(path)
            result = shibie(model, path, 0.1)
            print("识别结果=", result)
            if (7.0 in result.keys()):
                print("坐标是----》", result[7.0][0], result[7.0][1])
                # d.click(result[7.0][0] + 50, result[7.0][1] + 90)
                target_x = result[7.0][0] + 25
                target_y = result[7.0][1] + 58
            elif (11.0 in result.keys()):
                print("坐标是----》", result[11.0][0], result[11.0][1])
                # d.click(result[11.0][0] - 385, result[11.0][1])
                target_x = result[11.0][0] - 256
                target_y = result[11.0][1]
            else:
                print("加号定位失败")
                return 0,"加号定位失败"
        print("target_x,count%4*90=", target_x, count % 4 * 90)
        print("target_y , count//4*100", target_y, count // 4 * 100)
        target_x_temp = target_x
        target_y_temp = target_y
        target_x = target_x + count % 4 * 60
        target_y = target_y + count // 4 * 68
        print(f"count={count},targetx={target_x},tagety={target_y}")

        # path = photo(serial)
        # print("path=", path)
        # screenshot_image = d.screenshot()
        # screenshot_image.save(path)
        #
        # # 打开截图文件
        # with Image.open(path) as img:
        #     # 指定要截取的区域的坐标和大小
        #     left = target_x-26  # 左边界坐标
        #     top = target_y  # 上边界坐标
        #     right = target_x+36  # 右边界坐标
        #     bottom = target_y+35  # 下边界坐标
        #
        #     # 计算宽度和高度
        #     width = right - left
        #     height = bottom - top
        #     # 截取指定区域
        #     cropped_img = img.crop((left, top, right, bottom))
        #     # 保存截取的区域到文件
        #     cropped_img_path = photo(serial)
        #     cropped_img.save(cropped_img_path)
        #
        #
        # alldata = ocr_processor.getAllData_test(cropped_img_path)
        # #shuliang = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata, target_x-26, target_x+36, target_y, target_y+35)
        # print("alldata=", alldata)
        # #print("shuliang=", shuliang)

        d.click(target_x, target_y)
        target_x = target_x_temp
        target_y = target_y_temp

        time.sleep(1.5)
        # 先判断有没有打开弹窗
        path = photo(serial)
        print("path=", path)
        screenshot_image = d.screenshot()
        screenshot_image.save(path)
        result = shibie(model, path, 0.1)
        print("识别结果=", result)
        if (14.0 in result.keys()):
            print("坐标是----》", result[14.0][0], result[14.0][1])

        else:
            print("点击没有弹窗啊")
            time.sleep(1)
            d.click(1254, 28)
            time.sleep(2)
            return 1,"点击没有弹窗啊"
        time.sleep(2.5)
        d.click(896, 201)
        time.sleep(1)
        d.click(921, 446)
        time.sleep(0.5)
        d.click(883, 237)
        time.sleep(1.5)

        # 开始识别图片内容
        result_j = judge_celue(serial, d)
        print("result_j------------->", result_j)

        if (result_j == 1):
            path = photo(serial)
            print("path=", path)
            screenshot_image = d.screenshot()
            screenshot_image.save(path)
            result = shibie(model, path, 0.1)
            print("识别结果=", result)
            if (14.0 in result.keys()):
                print("坐标是----》", result[14.0][0], result[14.0][1])
                d.click(result[14.0][0], result[14.0][1])
                time.sleep(2)
                d.click(729, 518)
                time.sleep(2)
            else:
                d.click(100, 100)
                time.sleep(2)
        else:
            count += 1
            d.click(100, 100)
            time.sleep(2)
    time.sleep(1)
    d.click(1254,28)
    time.sleep(2)
    return 1

        #return 1,"执行完毕"

        # path = photo(serial)
        # print("path=", path)
        # screenshot_image = d.screenshot()
        # screenshot_image.save(path)
        # result = shibie(model, path, 0.1)
        # print("识别结果=", result)
        # if (12.0 in result.keys()):
        #     print("坐标是----》", result[12.0][0], result[12.0][1])
        #     d.click(result[12.0][0], result[12.0][1])
        # elif (14.0 in result.keys()):
        #     d.click(100, 100)
        # else:
        #     print("关闭定位失败")
        #     #return
        # time.sleep(3)
def jietu(path,serial,x1,x2,y1,y2):
    # 打开截图文件
    with Image.open(path) as img:
        # 指定要截取的区域的坐标和大小
        left = x1  # 左边界坐标
        top = y1  # 上边界坐标
        right = x2  # 右边界坐标
        bottom = y2  # 下边界坐标

        # 计算宽度和高度
        width = right - left
        height = bottom - top
        # 截取指定区域
        cropped_img = img.crop((left, top, right, bottom))
        # 保存截取的区域到文件
        cropped_img_path = photo(serial)
        cropped_img.save(cropped_img_path)
        return cropped_img_path
def getzhengshu(a,b):
    # 计算浮点结果
    result = a * b

    # 将浮点结果转换为整型（实际上是向下取整）
    int_result = int(result)

    # 检查转换后的整型结果是否等于浮点结果四舍五入到最接近的整数
    if int_result == round(result):
        # 如果相等，则加一
        final_result = int_result + 1
    else:
        # 如果不相等，则保持原浮点结果（这里我们实际上没有用到原浮点结果，
        # 但为了说明，可以保留或转换回浮点表示，这里直接保持整型表示）
        final_result = int_result  # 注意这里已经是整型了，其实不需要再赋值，只是为了代码清晰

    # 输出结果
    return final_result
def judge_celue(serial,d):
    points = {"0":[716,489],"1":[716,446],"2":[780,446],"3":[844,446],"4":[716,403],"5":[780,403],"6":[844,403],"7":[716,367],"8":[780,367],"9":[844,367]}
    try:
        path = photo(serial)
        print("path=", path)
        screenshot_image = d.screenshot()
        screenshot_image.save(path)

        path = image_quzao(path)

        alldata = ocr_processor.getAllData_test(path)
        # danjia = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata, 486, 563, 396, 432)

        jiatupath = jietu(path, serial, 490, 563, 396, 432)
        danjia = ocr_processor.getAllData_test(jiatupath)
        if (len(danjia) == 1):
            print("alldata111=", alldata)
            print("danjia=", danjia[0]["text"])
            danjia = float(danjia[0]["text"])
        else:
            return 0

        zongjia = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata, 857, 970, 216, 252)
        print("alldata111=", alldata)
        print("zongjia=", zongjia)

        shuliang = None
        jiatupath = jietu(path, serial, 857, 934, 187, 216)
        shuliangs = ocr_processor.getAllData_test(jiatupath)
        if (len(shuliangs) == 1):
            print("shuliangs=", alldata)
            print("shuliangs=", shuliangs[0]["text"])
            if (shuliangs[0]["text"] == "二"):
                shuliang = 11
            else:
                shuliang = float(shuliangs[0]["text"])
    except:
        print("当前反升崩溃")
        return 0
    # else:
    #     return 0
    # shuliang = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata, 857, 960, 187, 216)
    # print("alldata111=", alldata)
    # print("shuliang=", shuliang)

    if ("999" in zongjia):
        try:
            print("当前数量是 1 ，或者2 或者没有识别出来")

            if isinstance(danjia, float):
                danjia = int(danjia)+1
            else:
                danjia = int(danjia)
            if (danjia >= 10):
                # 先点击min
                time.sleep(0.5)
                d.click(921, 403)
                time.sleep(0.5)
                d.click(921, 482)
                time.sleep(1)
                zongjia_list = list(str(danjia))
                for temp in zongjia_list:
                    if (temp in points.keys()):
                        d.click(int(points[temp][0]), int(points[temp][1]))
                        time.sleep(0.5)
                return 1
            else:
                return 0
        except:
            print("当前崩溃了啊，返回0")
            return 0
    else:
        #求平均价
        try:
            if(shuliang == None):
                path = photo(serial)
                print("path=", path)
                screenshot_image = d.screenshot()
                screenshot_image.save(path)
                path = image_quzao(path)
                alldata = ocr_processor.getAllData_test(path)
                pingjunjia = ocr_processor.getPoint_BY_PaddleOCRJsons_area_No_by_txt(alldata, 819, 960, 252, 288)
                print("danjia=", pingjunjia)
                if ("2.5" in pingjunjia):
                    # 当前数量是2
                    print("当前数量是2")
                    shuliang = 2
                elif ("10" in pingjunjia):
                    # 当前数量是1
                    print("当前数量是1")
                    shuliang = 1
                elif ("3.33" in pingjunjia):
                    # 当前数量是1
                    print("当前数量是3")
                    shuliang = 3
                elif ("5" in pingjunjia):
                    # 当前数量是1
                    print("当前数量是4")
                    shuliang = 4
                elif ("2" in pingjunjia):
                    # 当前数量是1
                    print("当前数量是1")
                    shuliang = 5
                else:
                    print("当前数量未知")
                    shuliang = 1

            zhenshizongjia = int(shuliang) * danjia

            if isinstance(danjia, float):
                zhenshizongjia = int(zhenshizongjia)+1
            else:
                zhenshizongjia = int(zhenshizongjia)

            time.sleep(1)
            d.click(896, 237)
            time.sleep(1)
            if (zhenshizongjia >= 10):
                # 先点击min
                d.click(921, 403)
                time.sleep(0.5)
                # for i in range(0, zhenshizongjia - int(zongjia)):
                #     d.click(921, 324)
                #     time.sleep(0.2)
                time.sleep(0.5)
                d.click(921, 482)
                time.sleep(1)
                zongjia_list = list(str(zhenshizongjia))
                for temp in zongjia_list:
                    if(temp in points.keys()):
                        d.click(int(points[temp][0]),int(points[temp][1]))
                        time.sleep(0.5)
                return 1
            else:
                return 0
        except:
            print("当前崩溃了啊，返回0")
            return 0





def click_point(serial,model,d):
    path = photo(serial)
    print("path=", path)
    screenshot_image = d.screenshot()
    screenshot_image.save(path)
    result = shibie(model, path, 0.1)
    print("识别结果=", result)
    if (6.0 in result.keys()):
        print("坐标是----》", result[6.0][0], result[6.0][1])
        d.click(result[6.0][0], result[6.0][1])

        return 1
    else:
        print("交易tab定位失败")
        return


def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)



def backToHome(d):
    dd =  0
    d.app_start(package_name="com.alipay.mobile.socialwidget")
    time.sleep(3)
    while(dd < 10):
        elements = d(resourceId='com.alipay.mobile.socialwidget:id/social_tab_text')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 PKL 文件查看器")
        self.setGeometry(100, 100, 650, 300)
        #layout = QVBoxLayout()
        self.titleLabel = QLabel("*"*55+"手机列表"+"*"*55)
        self.titleLabel.setStyleSheet("""  
            QLabel {  
                font-size: 14px; /* 字体大小 */  
                font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                padding: 10px; /* 内边距 */  
                font-weight: bold; /* 字体加粗 */
                background-color: #f0f0f0; /* 背景色 */  
                color: #333; /* 文本颜色 */  
               
            }  
        """)
        self.titleLabel_renwu = QLabel("*"*55+"运行进度"+"*"*55)
        self.titleLabel_renwu.setStyleSheet("""  
                    QLabel {  
                        font-size: 14px; /* 字体大小 */  
                        font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                        padding: 10px; /* 内边距 */  
                        background-color: #f0f0f0; /* 背景色 */  
                        font-weight: bold; /* 字体加粗 */
                        color: #333; /* 文本颜色 */  

                    }  
                """)
        self.caozuo_tiel = QLabel("*"*55+"操       作"+"*"*55)
        self.caozuo_tiel.setStyleSheet("""  
                            QLabel {  
                                font-size: 14px; /* 字体大小 */  
                                font-weight: bold; /* 字体加粗 */
                                font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                                padding: 10px; /* 内边距 */  
                                background-color: #f0f0f0; /* 背景色 */  
                                color: #333; /* 文本颜色 */  

                            }  
                        """)
        self.caozuo_config = QLabel("*" * 55 + "脚本配置" + "*" * 55)
        self.caozuo_config.setStyleSheet("""  
                                    QLabel {  
                                        font-size: 14px; /* 字体大小 */  
                                        font-weight: bold; /* 字体加粗 */
                                        font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                                        padding: 10px; /* 内边距 */  
                                        background-color: #f0f0f0; /* 背景色 */  
                                        color: #333; /* 文本颜色 */  

                                    }  
                                """)

        # Table widget to display pkl file information
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)  # Increase column count for checkboxes
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"统计"])
        self.table_widget.setColumnWidth(0,30)
        self.table_widget.setShowGrid(True)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        #self.table_widget.itemClicked.connect(self.on_item_clicked)
        #self.table_widget.setItem(2, 1, QTableWidgetItem(2))

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area.setFixedHeight(300)  # Set fixed height for the scroll area
        self.scroll_area.setFixedWidth(650)
        #self.scroll_area.verticalScrollBar().setValue(3)
        #self.scroll_area




        #以下是内容相关的列表
        # self.text_edit = QTextEdit(self)
        # self.text_edit.setReadOnly(True)  # Make the text edit read-only
        # self.scroll_area_log = QScrollArea(self)
        # self.scroll_area_log.setWidget(self.text_edit)
        # self.scroll_area_log.setWidgetResizable(True)  # Allow the widget to resize
        # self.scroll_area_log.setFixedHeight(200)  # Set a fixed height for the scroll area
        # self.scroll_area_log.setFixedWidth(650)

        # self.scroll_area.verticalScrollBar().setValue(3)
        # self.scroll_area

        self.horizontal_layout = QHBoxLayout()
        #self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button0 = QLabel("           ")
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("韩游上架任务")
        self.radio_button1.setChecked(True)
        self.radio_button2 = QCheckBox("是否取消交易")
        # self.radio_button3 = QCheckBox("统计")
        # self.radio_button3.setChecked(True)
        # self.radio_button4 = QCheckBox("删除直通")
        # self.radio_button4.setChecked(True)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addWidget(self.radio_button2)
        # self.horizontal_layout.addWidget(self.radio_button3)
        # self.horizontal_layout.addWidget(self.radio_button4)
        self.horizontal_layout.addWidget(self.radio_button5)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
          # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('                          每隔多久启动一个手机：')
        self.line_edit_from = QLineEdit("100")
        self.line_edit_from.setFixedWidth(40)

        self.label_to = QLabel('至')
        self.line_edit_to = QLineEdit("50")
        self.line_edit_to.setFixedWidth(100)
        self.label_seconds = QLabel('秒', self)

        self.label_from111 = QLabel('                          单次播放')
        self.jiarenshurukuang = QLineEdit("100")
        self.jiarenshurukuang.setFixedWidth(40)
        self.label_from222 = QLabel('次                      ')
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        #self.h_layout.addWidget(self.label_to)
        #self.h_layout.addWidget(self.line_edit_to)
        self.h_layout.addWidget(self.label_seconds)

        # self.h_layout.addWidget(self.label_from111)
        # self.h_layout.addWidget(self.jiarenshurukuang)
        # self.h_layout.addWidget(self.label_from222)

        self.h_layout.setSpacing(5)
        # 设置布局与窗口边框之间的边距（例如，设置为 0 像素）
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.h_layout_kongge = QHBoxLayout()
        self.label_file_kongge = QLabel("                          ")
        self.h_layout_kongge.addWidget(self.label_file_kongge)

        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择配置文件夹:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl","file_path")
        if(file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入文件夹路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件",self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

        self.clear_task_config_button = QPushButton('一键清除任务列表', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)


        #下面是观看任务列表
        self.task_widget = QTableWidget(self)
        self.task_widget.setColumnCount(4)  # Increase column count for checkboxes
        self.task_widget.setHorizontalHeaderLabels(['编号', '任务', '任务数量', '统计'])
        self.task_widget.setColumnWidth(0, 80)
        self.task_widget.setColumnWidth(1, 300)
        self.task_widget.setColumnWidth(2, 130)
        self.task_widget.setColumnWidth(3, 130)
        self.task_widget.setShowGrid(True)

        self.scroll_area_task = QScrollArea(self)
        self.scroll_area_task.setWidget(self.task_widget)
        self.scroll_area_task.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area_task.setFixedHeight(200)  # Set fixed height for the scroll area
        self.scroll_area_task.setFixedWidth(650)


        #self.task_widget.setItem(1, 1, QTableWidgetItem("111111111111111111111111"))


        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)  # 设置布局间距为0
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.caozuo_config)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge)
        #layout.addLayout(self.h_layout_dir)
        #layout.addWidget(self.titleLabel_renwu)
        #layout.addWidget(self.scroll_area_task)
        #layout.addWidget(self.scroll_area_log)

        # Variable to store the selected IDs
        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(30000)
        self.refresh_pkl_files_test()
        self.timer.timeout.connect(self.refresh_pkl_files_test)
        self.timer.start(10000)

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.add_text)
        self.timer1.start(1300)

        # Initial load
        self.refresh_pkl_files()
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("执行")
        self.execute_button.resize(100,30)

        self.button_gang.addWidget(self.execute_button)

        #self.button_gang.addWidget(self.clear_task_config_button)
        self.execute_button_delete = QPushButton("删除")
        self.execute_button_delete.resize(100, 30)
        #self.button_gang.addWidget(self.execute_button_delete)

        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_reset)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.file_button.clicked.connect(self.showDialog)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.execute_button_delete.clicked.connect(self.execute_delete_button_clicked)
        layout.addLayout(self.button_gang)
        #layout.addWidget(self.execute_button_reset)

    def on_item_changed(self,item: QTableWidgetItem):
        if self.table_widget.currentColumn() == 2:
            # 获取新的数据并打印（或保存到其他地方）
            new_data = item.text()
            #print(item.column())

            item.row()
            #print(self.table_widget.item(item.row(),1).text())
            phone_name = self.table_widget.item(item.row(),1).text()
            #print(f"New data in row {item.column()}, column 2: {new_data}")
            # 你可以在这里添加保存数据的逻辑，比如保存到数据库或文件中
            updata_pkl_config("config.pkl",phone_name,new_data)
            #print(pkl_list("config.pkl"))
    def on_item_clicked(self):

        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}
        self.selected_ids = current_device_ids
        print(self.selected_ids)
        self.refresh_pkl_files()
        # 获取新的数据并打印（或保存到其他地方）
        # new_data = item.text()
        # #print(item.column())
        #
        # item.row()
        # #print(self.table_widget.item(item.row(),1).text())
        # phone_name = self.table_widget.item(item.row(),1).text()
        # #print(f"New data in row {item.column()}, column 2: {new_data}")
        # # 你可以在这里添加保存数据的逻辑，比如保存到数据库或文件中
        # updata_pkl_config("config.pkl",phone_name,new_data)
        #print(pkl_list("config.pkl"))
        print("全选")

    def shell_neibu(self,cmd):
        os.system(cmd)

    def on_file_button_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            # If a folder is selected, update the QLabel
            self.file_textbox.setText(folder_path)
            updata_pkl_config_mianban("file_path",folder_path)
        else:
            self.file_textbox.setText('No folder selected')

    def showDialog(self):
        # 设置文件过滤器
        print("1")
        filters = "Excel Files (*.txt);;All Files (*)"

        # 创建文件对话框
        dialog = QFileDialog(self, "Open Excel File", "", filters)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setDefaultSuffix("txt")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        # 显示对话框并获取用户选择
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                selected_file = selected_files[0]  # 获取第一个选中的文件（假设只选择一个文件）
                self.file_textbox.setText(selected_file)
                updata_pkl_config_mianban("file_path", selected_file)
                #self.excel_file = selected_file
                self.import_config()
                self.refresh_pkl_files_test()
    def import_config(self):
        print("")
        path_dir = "task_config"
        create_directory_if_not_exists(path_dir)

        # path = path_dir+"/"+"config.pkl"
        # self.judge_pkl_creat(path)
        # 指定文件的路径
        with video_lock:
            file_path = self.file_textbox.text()
            # 使用 with 语句打开文件，这样可以确保文件在读取完毕后自动关闭
            with open(file_path, 'r', encoding='utf-8') as file:
                # 逐行读取文件内容并打印
                for line in file:
                    print(line, end='')  # 使用 end='' 是为了避免打印每行末尾的额外换行符
                    if((str(line).count("_")>0) and (str(line).count("/")>0)):
                        file_name = str(line).split("/")[-2]
                        new_data = {"url":str(line).split("_")[0],"BIG_COUNT":int(str(line).split("_")[1]),"TONGJI":0}
                        print("newdata=",new_data)
                        file_name = path_dir + "/" +file_name +".pkl"
                        print("file_name=", file_name)
                        self.judge_pkl_creat(file_name,new_data)
        # 注意：使用 with 语句后，不需要手动关闭文件，它会在块结束时自动关闭

    def get_random_pkl_file_in_directory(self,directory):
        # 获取目录下所有 .pkl 文件的列表
        pkl_files = [f for f in os.listdir(directory) if f.endswith('.pkl')]

        # 如果没有 .pkl 文件，则直接返回 False
        if not pkl_files:
            return False

        # 循环直到找到一个满足条件的文件或者所有文件都不满足条件
        while pkl_files:
            # 随机选择一个 .pkl 文件
            chosen_file = random.choice(pkl_files)
            file_path = os.path.join(directory, chosen_file)

            # 从列表中移除已选择的文件，以便在下次循环时不再选择它
            pkl_files.remove(chosen_file)

            # 尝试读取文件内容
            try:
                with open(file_path, 'rb') as file:
                    data = pickle.load(file)

                # 检查数据是否满足条件
                if 'TONGJI' in data and 'BIG_COUNT' in data and isinstance(data['TONGJI'], (int, float)) and isinstance(
                        data['BIG_COUNT'], (int, float)):
                    if data['TONGJI'] <= data['BIG_COUNT']:
                        return chosen_file
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        # 如果没有文件满足条件，则返回 False
        return False
    def judge_pkl_creat(self,pkl_file,new_data):
        # 指定文件的路径
        file_path = pkl_file
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 如果文件不存在，则创建一个新的字典
            new_data = new_data
            # 使用 with 语句打开（或创建）文件，并写入数据
            with open(file_path, 'wb') as file:
                pickle.dump(new_data, file)

            print(f"文件 {file_path} 已创建并写入新数据。")
        else:
            print(f"文件 {file_path} 已存在。")

        # 注意：'wb' 模式用于以二进制写入方式打开文件，这是 pickle 所需的。
    def updata_pkl_config_video(self,pklfile, key, value):
        # dic = {}
        if not os.path.exists(pklfile):
            # 如果文件不存在，创建一个新的字典（或其他对象）
            data = {key: value}  # 这里可以替换为你想要保存的任何Python对象
            # 使用pickle将对象序列化并保存到文件中
            with open(pklfile, 'wb') as file:
                pickle.dump(data, file)
        else:
            with open(pklfile, 'rb') as pkl_file:
                dic = pickle.load(pkl_file)
                # print("li----------------",dic)
            dic[key] = value
            # print("----------------------------------",dic)
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)





    def execute_button_clicked(self):
        #print("---------------")
        if(self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "游戏上架任务")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()

        # if (self.radio_button2.isChecked() == True):
        #     tasks.append("delete")
        # if (self.radio_button3.isChecked() == True):
        #     tasks.append("tongji")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")


        thread = threading.Thread(target=self.thread_UI, args=())
        thread.start()

    def thread_UI(self):
        tasks = []
        print("tasks------------", tasks)
        # self.scroll_area.ensureWidgetVisible(100)
        if (self.radio_button1.isChecked() == True):
            tasks.append("add")
        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,self.file_textbox.text(),tasks,self.line_edit_from.text(),self.line_edit_to.text(),self.jiarenshurukuang.text(),self.radio_button2.isChecked()))
            #threads.append(thread)
            thread.start()
            time.sleep(int(self.line_edit_from.text()))

        self.selected_ids = []
    def add_text(self):
        print("")
        # Get the current text from the QTextEdit
        # list =  pkl_list("log.pkl")
        # current_text = self.text_edit.toPlainText()
        # for bbb in list:
        #     if(str(bbb) in str(current_text)):
        #         pass
        #     else:
        #         # Append new text (for example, a new line with some content)
        #         new_text = str(bbb)+"--->"+str(list[bbb])  # You can change this to whatever text you want to add
        #         # Set the new text (old text + new text)
        #         self.text_edit.setPlainText(current_text +"\n" +new_text)
        #         # Optionally, move the cursor to the end of the text
        #         cursor = self.text_edit.textCursor()
        #         # cursor.movePosition(cursor.End)
        #         self.text_edit.setTextCursor(cursor)
        #         # Scroll to the bottom (optional, depending on your needs)
        #         scrollbar = self.text_edit.verticalScrollBar()
        #         scrollbar.setValue(scrollbar.maximum())
        # if(os.path.isdir("./task_config")):
        #     shutil.rmtree("./task_config")
        #     self.refresh_pkl_files_test()
    def clear_task(self):
        print("")
        # Get the current text from the QTextEdit
        # list =  pkl_list("log.pkl")
        # current_text = self.text_edit.toPlainText()
        # for bbb in list:
        #     if(str(bbb) in str(current_text)):
        #         pass
        #     else:
        #         # Append new text (for example, a new line with some content)
        #         new_text = str(bbb)+"--->"+str(list[bbb])  # You can change this to whatever text you want to add
        #         # Set the new text (old text + new text)
        #         self.text_edit.setPlainText(current_text +"\n" +new_text)
        #         # Optionally, move the cursor to the end of the text
        #         cursor = self.text_edit.textCursor()
        #         # cursor.movePosition(cursor.End)
        #         self.text_edit.setTextCursor(cursor)
        #         # Scroll to the bottom (optional, depending on your needs)
        #         scrollbar = self.text_edit.verticalScrollBar()
        #         scrollbar.setValue(scrollbar.maximum())
        if(os.path.isdir("./task_config")):
            shutil.rmtree("./task_config")
            self.refresh_pkl_files_test()

    def execute_delete_button_clicked(self):
        print("---------------")
        if(self.selected_ids == []):
            toast("请选择删除的机型")
            return
        for temp in self.selected_ids:
            #print(temp)
            if(os.path.isfile("./shuju/" + temp + ".pkl")):
                os.remove("./shuju/" + temp + ".pkl")
        self.refresh_pkl_files()
        self.selected_ids = []

    def execute_reset_button_clicked(self):
        #print("execute_reset_button_clicked")
        directory = './shuju'
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                filepath = os.path.join(directory, filename)
                updata_pkl(filepath, "执行状态", "运行结束")
                updata_pkl(filepath, "进行的任务", "空闲")
        self.refresh_pkl_files()

    def refresh_pkl_files_video(self):
        # 保存当前滚动位置
        current_pos = self.task_widget.verticalScrollBar().value()
        print("current_pos=",current_pos)

        #print("current_scroll_position",current_scroll_position)
        # 清除旧数据
        #self.task_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './task_config'
        row_index = 0
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                print("filename---",filename)
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'rb') as file:
                        data = pickle.load(file)
                        print("data=",data)
                        print("row_index=",row_index)

                        # 假设数据是一个字典
                        if isinstance(data, dict):

                            print("进来了")
                            print("-----",data.get('url', 'N/A'))

                            bianhao = QTableWidgetItem(filename)
                            bianhao.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            self.task_widget.setItem(row_index, 0, bianhao)
                            renwu = QTableWidgetItem(data.get('url', 'N/A'))
                            renwu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.task_widget.setItem(row_index, 1, renwu)

                            bigCount = QTableWidgetItem(data.get('BIG_COUNT', 'N/A'))
                            bigCount.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.task_widget.setItem(row_index, 2, bigCount)

                            tongji = QTableWidgetItem(data.get('TONGJI', 'N/A'))
                            tongji.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.task_widget.setItem(row_index, 3, tongji)
                            row_index += 1
                except Exception as e:
                    print(f"读取文件 {filepath} 时出错: {e}")
         # 恢复滚动位置
        self.task_widget.verticalScrollBar().setSliderPosition(current_pos)
    def refresh_pkl_files_test(self):
        with video_lock:
            # 保存当前滚动位置
            current_pos = self.task_widget.verticalScrollBar().value()

            #print("current_scroll_position",current_scroll_position)
            # 清除旧数据
            self.task_widget.setRowCount(0)
            # 遍历目录中的所有文件
            directory = './task_config'
            create_directory_if_not_exists(directory)
            row_index = 0

            #print("sorted_data=",sorted_data)

            for file_name in os.listdir(directory):
                task_name = file_name
                #print("device_id---->",device_id)
                file_name = directory+"/"+str(file_name)
                #print("file_name---",file_name)
                if(os.path.isfile(file_name)):
                    try:
                        with open(file_name, 'rb') as file:
                            data = pickle.load(file)
                            #print("data-----------,",data)

                            # 假设数据是一个字典
                            if isinstance(data, dict):
                                # 插入新行
                                self.task_widget.insertRow(row_index)
                                # print("data====",data)
                                # print("url=",data.get('url', 'N/A'))

                                self.task_widget.setItem(row_index, 0, QTableWidgetItem(str(task_name).split(".")[0]))
                                # 设置文件名（去除后缀）
                                self.task_widget.setItem(row_index, 1, QTableWidgetItem(data.get('url', 'N/A')))
                                # 设置其他数据
                                # phone_name = get_value_by_key_pkl("config.pkl",data.get('name', 'N/A'))
                                # if(phone_name != None):
                                #     item_i = QTableWidgetItem(phone_name)
                                # else:
                                #     item_i = QTableWidgetItem(data.get('nick_name', 'N/A'))
                                # #item_i.setForeground(QBrush(QColor(255,0,0)))

                                self.task_widget.setItem(row_index, 2, QTableWidgetItem(str(data.get('BIG_COUNT', 'N/A'))))
                                # if(data.get('连接状态', 'N/A') == "中断连接"):
                                #     item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                #     item_lianjie.setForeground(QBrush(QColor(255,0,0)))
                                # else:
                                #     item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                #     item_lianjie.setForeground(QBrush(QColor(0, 0, 0)))
                                # item_lianjie.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.task_widget.setItem(row_index, 3, QTableWidgetItem(str(data.get('TONGJI', 'N/A'))))

                                # #item_i = QTableWidgetItem(data.get('执行状态', 'N/A'))
                                # # item_i.setForeground(QBrush(QColor(255,0,0)))
                                # item_zhuangtai = QTableWidgetItem(data.get('执行状态', 'N/A'))
                                # item_zhuangtai.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                #self.task_widget.setItem(row_index, 4, QTableWidgetItem(data.get('TONGJI', 'N/A')))

                                # item_zhuangage = QTableWidgetItem(data.get('age', 'N/A'))
                                # item_zhuangage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                # self.task_widget.setItem(row_index, 5, item_zhuangage)
                                #
                                # item_add = QTableWidgetItem(data.get('add', 'N/A'))
                                # item_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                # self.task_widget.setItem(row_index, 6, item_add)

                                # item_renwu = QTableWidgetItem(data.get('进行的任务', 'N/A'))
                                # item_renwu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                # self.task_widget.setItem(row_index, 5, item_renwu)
                                #
                                # button111 = QTableWidgetItem(data.get('tongji', 'N/A'))
                                # # button111.clicked.connect(lambda: print("Button clicked!"))
                                # self.task_widget.setItem(row_index, 6,button111)

                                row_index += 1
                    except Exception as e:
                        print(f"读取文件 {file_name} 时出错: {e}")
             # 恢复滚动位置
            self.task_widget.verticalScrollBar().setSliderPosition(current_pos)
    def refresh_pkl_files(self):
        # 保存当前滚动位置
        current_pos = self.table_widget.verticalScrollBar().value()

        #print("current_scroll_position",current_scroll_position)
        # 清除旧数据
        self.table_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './shuju'
        row_index = 0

        sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))
        #print("sorted_data=",sorted_data)

        for device_id,v in sorted_data.items():
            #print("device_id---->",device_id)
            file_name = directory+"/"+str(device_id)+".pkl"
            #print("file_name---",file_name)
            if(os.path.isfile(file_name)):
                try:
                    with open(file_name, 'rb') as file:
                        data = pickle.load(file)

                        #print("data-----------,",data)

                        # 假设数据是一个字典
                        if isinstance(data, dict):
                            # 插入新行
                            self.table_widget.insertRow(row_index)
                            # 添加复选框
                            checkbox = QCheckBox(self)
                            #print("self.selected_ids=",self.selected_ids)
                            #print("os.path.splitext(file_name)[0]",os.path.splitext(file_name)[0].split("/")[2])
                            if os.path.splitext(file_name)[0].split("/")[2] in self.selected_ids:
                                checkbox.setChecked(True)
                            if(data.get('执行状态', 'N/A') == "运行中"):
                                checkbox.setEnabled(False)
                            else:
                                checkbox.setEnabled(True)
                            # if (data.get('连接状态', 'N/A') == "中断连接"):
                            #     checkbox.setEnabled(True)
                            # else:
                            #     checkbox.setEnabled(True)
                            checkbox.stateChanged.connect(lambda state, row=row_index: self.update_selected_ids(state, row))
                            self.table_widget.setCellWidget(row_index, 0, checkbox)
                            # 设置文件名（去除后缀）
                            self.table_widget.setItem(row_index, 1, QTableWidgetItem(device_id))
                            # 设置其他数据
                            phone_name = get_value_by_key_pkl("config.pkl",data.get('name', 'N/A'))
                            if(phone_name != None):
                                item_i = QTableWidgetItem(phone_name)
                            else:
                                item_i = QTableWidgetItem(data.get('nick_name', 'N/A'))
                            #item_i.setForeground(QBrush(QColor(255,0,0)))

                            self.table_widget.setItem(row_index, 2, item_i)
                            if(data.get('连接状态', 'N/A') == "中断连接"):
                                item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                item_lianjie.setForeground(QBrush(QColor(255,0,0)))
                            else:
                                item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                item_lianjie.setForeground(QBrush(QColor(0, 0, 0)))
                            item_lianjie.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 3, item_lianjie)

                            #item_i = QTableWidgetItem(data.get('执行状态', 'N/A'))
                            # item_i.setForeground(QBrush(QColor(255,0,0)))
                            item_zhuangtai = QTableWidgetItem(data.get('执行状态', 'N/A'))
                            item_zhuangtai.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 4, item_zhuangtai)

                            # item_zhuangage = QTableWidgetItem(data.get('age', 'N/A'))
                            # item_zhuangage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            # self.table_widget.setItem(row_index, 5, item_zhuangage)
                            #
                            # item_add = QTableWidgetItem(data.get('add', 'N/A'))
                            # item_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            # self.table_widget.setItem(row_index, 6, item_add)

                            item_renwu = QTableWidgetItem(data.get('进行的任务', 'N/A'))
                            item_renwu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 5, item_renwu)

                            button111 = QTableWidgetItem(data.get('tongji', 'N/A'))
                            # button111.clicked.connect(lambda: print("Button clicked!"))
                            self.table_widget.setItem(row_index, 6,button111)

                            row_index += 1
                except Exception as e:
                    print(f"读取文件 {file_name} 时出错: {e}")
         # 恢复滚动位置
        self.table_widget.verticalScrollBar().setSliderPosition(current_pos)

    def update_selected_ids(self, state, row):
        # 更新选中的编号
        item_id = self.table_widget.item(row, 1).text()  # 获取编号
        #print("item_id=",item_id)
        if item_id not in self.selected_ids:
            self.selected_ids.append(item_id)  # 添加到选中的编号
        else:
            if item_id in self.selected_ids:
                self.selected_ids.remove(item_id)  # 从选中的编号中移除
        # 打印当前选中的编号
        #print("当前选中的编号:", self.selected_ids)
def get_format_time():
    import time
    from datetime import datetime
    # 获取当前时间的时间戳
    timestamp = time.time()
    # 将时间戳转换为datetime对象
    current_time = datetime.fromtimestamp(timestamp)
    # 格式化datetime对象为字符串
    formatted_date = current_time.strftime("%Y-%m-%d-%H:%M:%S")
    return formatted_date

def pkl_add_log(pkl,phone,values):
    # if(pkl == "log.pkl"):
    #     if (os.path.isfile(pkl)):
    #         print()
    #     else:
    #         data = dic
    #         # 将数据写入pkl文件
    #         with open(pkl, 'wb') as file:
    #             pickle.dump(data, file)
    # with open(pkl, 'rb') as pkl_file:
    #     dic = pickle.load(pkl_file)
    # dic.update({name: value})
    time = get_format_time()
    with open(pkl, 'wb') as pkl_file:
        pickle.dump({time:phone+"--->"+values}, pkl_file)

def pkl_add(pkl,dic):
    # if(pkl == "log.pkl"):
    #     if (os.path.isfile(pkl)):
    #         print()
    #     else:
    #         data = dic
    #         # 将数据写入pkl文件
    #         with open(pkl, 'wb') as file:
    #             pickle.dump(data, file)
    # with open(pkl, 'rb') as pkl_file:
    #     dic = pickle.load(pkl_file)
    # dic.update({name: value})
    with open(pkl, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
#import pickle
def toast(tishi):
    # import win32con
    # import ctypes
    # ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 3000)
    a = ""
# 反序列化对象

lock111 = threading.Lock()
def pkl_list(pklfile):
    # 使用with语句自动管理锁的获取和释放
    try:
        with lock111:
            if(not os.path.exists(pklfile)):
                data = {}
                with open(pklfile, 'wb') as file:
                    pickle.dump(data, file)
            if pklfile == "log.pkl":
                if os.path.isfile(pklfile):
                    print()  # 这里只是打印了一个空行，可能需要根据实际需求修改
                else:
                    data = {}
                    with open(pklfile, 'wb') as file:
                        pickle.dump(data, file)

                        # 读取文件
            with open(pklfile, 'rb') as pkl_file:
                my_object111 = pickle.load(pkl_file)
                return my_object111
    except BaseException:
        print("崩溃了")
        data = {}
        with open(pklfile, 'wb') as file:
            pickle.dump(data, file)

#import pickle

# 修改Python对象
#my_object['age'] = 31

# 重新序列化对象
lock222 = threading.Lock()
def get_value_by_key_pkl(pklfile, key):
    # 使用with语句自动管理锁的获取和释放
    with lock222:
        if not os.path.isfile(pklfile):
            return None

        dic = {}
        try:
            with open(pklfile, 'rb') as pkl_file:
                dic = pickle.load(pkl_file)
        except (EOFError, pickle.PickleError):
            # 处理文件为空或损坏的情况
            print(f"Warning: Unable to load pickle file {pklfile}")
            return None

            # 检查键是否在字典中
        if key in dic:
            return dic[key]
        else:
            return None

def updata_pkl_config(pklfile,key,value):
    #dic = {}
    if not os.path.exists(pklfile):
        # 如果文件不存在，创建一个新的字典（或其他对象）
        data = {key:value}  # 这里可以替换为你想要保存的任何Python对象
        # 使用pickle将对象序列化并保存到文件中
        with open(pklfile, 'wb') as file:
            pickle.dump(data, file)
    else:
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)
            #print("li----------------",dic)
        dic[key] = value
        #print("----------------------------------",dic)
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)

def updata_pkl(pklfile,key,value):
    #dic = {}
    if(os.path.isfile(pklfile)):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)
        dic[key] = value
        #print("----------------------------------",dic)
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)
import subprocess
import time
def get_connected_devices():
    # Run the adb devices command
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)
    #print("连接的设备有。。。",devices)
    connected_devices = []
    for device in devices:
        if device.strip():
            device_info = device.split('\t')
            connected_devices.append((device_info[0], device_info[1]))  # (device_id, status)

    return connected_devices

def updata_pkl_config_mianban(key,value):
    pklfile = "shuju_config.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"file_path": "请输入文件夹路径"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    dic[key]=value
    with open(pklfile, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
def monitor_devices():
    known_devices = set()
    create_directory_if_not_exists("shuju")
    delete_directory_contents("shuju")
    if(os.path.exists("config.pkl")):
        print()

    while True:
        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}

        # Check for new connections
        new_devices = current_device_ids - known_devices
        for device_id in new_devices:
            #print(f"Device connected: {device_id}")
            if(str(device_id).count(":")):
                device_id = str(device_id).split('.')[-1].split(':')[0]
            dic = {"name": device_id, "连接状态": "已连接", "执行状态": "空闲中", "age": "1811", "add": "bj1",
                   "xingbie": "nan", "进行的任务": "空闲", "nick_name": "昵称点击可编辑", "tongji": "0"}
            pkl_add("./shuju/" + device_id + ".pkl", dic)
            if (device_id not in dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))):
                updata_pkl_config("config.pkl", device_id, "昵称点击可编辑")

        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
            if (str(device_id).count(":")):
                device_id = str(device_id).split('.')[-1].split(':')[0]
            #print(f"Device disconnected: {device_id}")
            updata_pkl("./shuju/"+device_id+".pkl","连接状态","中断连接")
        # Update the known devices set
        known_devices = current_device_ids

        time.sleep(15)  # Check every 5 seconds

def delete_directory_contents(directory):
    shutil.rmtree(directory)
    os.makedirs(directory)  # 重新创建空文件夹
# def create_directory_if_not_exists(directory):
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#         print(f"Directory '{directory}' created.")
#     else:
#         print(f"Directory '{directory}' already exists.")


import os
import pickle


def update_pkl_add_one(pklfile, key):
    if os.path.isfile(pklfile):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)

            # 检查键是否存在，并更新其值
        if key in dic:
            dic[key] = str(int(dic[key])+1)
            #print("----------------------------------", dic)
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)
        else:
            print(f"Key '{key}' not found in the pickle file.")
    else:
        print(f"The file '{pklfile}' does not exist.")

    # 示例用法


# pklfile = 'example.pkl'  # 替换为您的 .pkl 文件路径
# key_to_update = 'some_key'  # 替换为您要更新的键
# update_pkl(pklfile, key_to_update)

if __name__ == "__main__":
    thread = threading.Thread(target=monitor_devices)
    thread.start()
    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())

    #sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))

    #print(sorted_data)



    # d = u2.connect("Q5S0219527003267")
    # tongji(d,"Q5S0219527003267",r"C:\Users\Administrator\Desktop\config")