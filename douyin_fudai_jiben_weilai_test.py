import base64
import hashlib
import re
import shutil
import sys
import threading
import random
import traceback
import uuid
from datetime import datetime
from lxml import etree

import psutil
import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QRadioButton, QLineEdit,
    QFileDialog, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
import os
import pickle
from RapidOCR_json.api.python.demo1 import OCRProcessor

ocr = OCRProcessor()
print(ocr)
current_scroll_position = 0
import time

# 抖音养号+微信加好友脚本
black_zhubo = []
alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()


def get_top_line_and_del(file):
    # 获取锁
    with file_lock:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # print("----------------")
            # print(lines)
            if not lines:
                # print("lines为空")
                return None
            temp_str = lines[0].strip()  # 直接转换为字符串并去除换行符

        # 重新打开文件以写入，这里可以优化为在读取后不移除文件指针直接截断文件
        with open(file, 'w', encoding='utf-8') as f:
            # 写入除了第一行之外的所有行
            f.writelines(str(line).strip() + '\n' for i, line in enumerate(lines) if i != 0)
            # 或者使用更简洁的方式，但注意这种方式会保留原始行的换行符（如果需要去除，可以使用strip()）
            # f.writelines(lines[1:])  # 这将保留第二行及之后的换行符，如果需要去除每行的换行符，需要先strip()
    return temp_str


import psutil
import os


def create_folder_on_current_disk():
    # 获取当前代码文件所在的路径
    current_script_path = os.path.abspath(__file__)
    # 提取当前代码所在的磁盘（如 'C:\\' 或 'D:\\'）
    current_disk = os.path.splitdrive(current_script_path)[0] + os.sep
    # 拼接新建文件夹的路径（以磁盘根目录为例）
    folder_path = os.path.join(current_disk, "dy_temp")
    # 新建文件夹
    try:
        os.makedirs(folder_path)
        print(f"已在 {current_disk} 上成功创建文件夹：{folder_path}")
    except FileExistsError:
        print(f"文件夹 {folder_path} 已存在")
    except Exception as e:
        print(f"创建文件夹失败：{e}")
    return folder_path


def take_screenshot(d):
    try:
        SAVE_DIR = create_folder_on_current_disk()
        # 生成带时间戳的文件名，避免重复
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
        # 截图并保存
        d.screenshot(save_path)
        print(f"截图已保存至：{save_path}")
        return save_path
    except BaseException as e:
        print("截图时，发生崩溃", str(e))
        return None


# 执行函数
# create_folder_on_last_disk()
def get_device(serial):
    # d = ""
    # print("之前的d", d)
    # print(f"正在连接设备: {serial}")
    d = u2.connect(serial)
    d.watcher.remove()
    return d


def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    # print("00000000000000000000000000---------")
    # print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path


def photo(s):
    Ui_file_Name = str(int(time.time())) + "_" + str(s) + "_ui.png"
    path = getPhotoPath() + "/" + Ui_file_Name
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


def find_string_in_file(file_path, search_string, phone_num):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                temps = line.split("+")
                if (len(temps) > 1):
                    # if ((search_string == temps[0]) and (temps[1][0:2] == str(phone_num)[0:2] )):
                    if (search_string == temps[0]):
                        return line.strip()  # 使用strip()去掉行尾的换行符
        return None  # 如果没有找到，则返回None
    except FileNotFoundError:
        # print(f"The file {file_path} was not found.")
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
    # print("pkl_files=",pkl_files)

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
                if 'TONGJI' in data and 'BIG_COUNT' in data and isinstance(int(data['TONGJI']),
                                                                           (int, float)) and isinstance(
                        int(data['BIG_COUNT']), (int, float)):
                    # print("tongji=",int(data['TONGJI']))
                    # print("BIG_COUNT=", int(data['BIG_COUNT']))
                    if int(data['TONGJI']) < int(data['BIG_COUNT']):
                        return chosen_file
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        # 如果没有文件满足条件，则返回 False
        return False


def load_pkl(pklfile):
    with video_lock:
        if (os.path.exists(pklfile)):
            with open(pklfile, 'rb') as pkl_file:
                my_object111 = pickle.load(pkl_file)
                return my_object111
        else:
            return None


def random_boolean_with_probability(probability):
    """
    根据给定的概率返回 True 或 False。

    :param probability: 成功的概率（0 到 1 之间的浮点数）
    :return: 如果随机数小于或等于概率则返回 True，否则返回 False
    """
    if not (1 <= probability <= 100):
        raise ValueError("概率必须在 0 到 1 之间")

    return random.random() * 100 <= probability


import random


def get_random_line_from_file(file_path):
    """
    从指定的文本文件中随机选择并返回一行。

    :param file_path: 文本文件的路径
    :return: 随机选择的一行文本
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 读取所有行并存储在一个列表中
            lines = file.readlines()

        # 如果文件不为空，随机选择一行
        if lines:
            random_line = random.choice(lines)
            return random_line.strip()  # 去除行尾的换行符
        else:
            return None  # 或者抛出一个异常，表示文件为空
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


import platform


def get_real_device_id():
    """获取更真实的设备唯一标识，并返回缩短后的版本"""
    try:
        # 收集各种硬件和系统信息
        info = [
            platform.node(),  # 计算机名
            platform.machine(),  # 机器类型
            platform.processor(),  # 处理器信息
            platform.system(),  # 操作系统名称
            platform.release(),  # 操作系统版本
            str(os.environ.get('COMPUTERNAME', '')),  # Windows计算机名
            str(os.environ.get('USERNAME', '')),  # 用户名
            str(uuid.getnode()),  # MAC地址
        ]

        # 创建哈希作为设备ID
        hash_obj = hashlib.sha256()
        hash_obj.update(''.join(info).encode('utf-8'))
        full_hash = hash_obj.hexdigest()

        # 返回缩短后的唯一码（例如前8个字符）
        return full_hash[:18]  # 取前8个字符作为缩短的唯一码
    except Exception as e:
        return f"ERR-{str(e)[:18]}"  # 错误情况下也返回缩短的字符串


def encrypt_and_modify(shebeima):
    """对输入的字符串进行Base64编码，并在特定位置插入字符"""
    input_text = shebeima

    if not input_text:
        return

    # 进行Base64编码
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')

    # 在特定位置插入字符
    modified_str = list(encoded_str)

    # 确保字符串足够长，以避免索引错误
    if len(modified_str) >= 1:
        modified_str[0] += 'a'
    if len(modified_str) >= 3:
        modified_str[2] += 'b'
    if len(modified_str) >= 5:
        modified_str[4] += 'f'
    if len(modified_str) >= 2:
        modified_str[-2] += 'g'

    # 将列表转换回字符串
    final_str = ''.join(modified_str)
    return final_str


def judge():
    shebeima = get_real_device_id()
    final_str = encrypt_and_modify(shebeima)
    if (os.path.isfile(final_str)):
        return True
    else:
        return False


start_time = datetime.now()


def operate_device(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                   swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, shipinhuadongcishu, gouwu,
                   shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, shouyehuadongxiao,
                   shouyehuadongda):
    result_j = judge()
    if (result_j == False):
        print("当前需要联系")
        #return

    count_zong = 0
    while (True):
        try:
            print("while------------")
            result = duozhubo(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big,
                              swipe_small,
                              swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,
                              shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi,
                              jinrufangshi, shouyehuadongxiao, shouyehuadongda)
            if (result == "88"):
                print("运行结束")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束")
                    updata_pkl(filepath, "进行的任务", "空闲")
                    print("shifouguanbidouyin=", shifouguanbidouyin)
                if (shifouguanbidouyin == True):
                    print("开始执行关闭退出抖音")
                    cmd = f"adb -s {serial} shell input keyevent 4"
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)

                return
            if (result == "99"):
                print("运行结束")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束")
                    updata_pkl(filepath, "进行的任务", "空闲")
                if (shifouguanbidouyin == True):
                    print("开始执行关闭退出抖音")
                    cmd = f"adb -s {serial} shell input keyevent 4"
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                return
            count_zong += 1
        except BaseException as ee:
            print("崩溃了", ee)
            error_info = traceback.format_exc()
            print(serial, "--------", "完整错误信息:")
            print(error_info)
            operate_device(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big,
                           swipe_small,
                           swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, shipinhuadongcishu, gouwu,
                           shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi,
                           shouyehuadongxiao, shouyehuadongda)


def random_click_view(d, view):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left) + random.randint(2, 15)
    random_y = int(bottom) + random.randint(2, 15)
    print("开始点击")
    print(random_x, random_y)

    d.click(random_x, random_y)


def check_time_difference(interval_seconds):
    if (interval_seconds == 0):
        return False
    # 获取当前时间
    end_time = datetime.now()
    # 计算时间差（以秒为单位）
    time_difference = (end_time - start_time).total_seconds()
    print("time_difference=", time_difference)
    # 如果时间差大于100秒，则返回True，否则返回False
    return time_difference > interval_seconds


# 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def duozhubo(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
             swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu,
             shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, shouyehuadongxiao,
             shouyehuadongda):
    if (len(fudai) > 0):
        fudai_list = str(fudai).split("/")
        zhubo_len = len(fudai_list)
        i = 0
        while (True):
            result_main = 0

            print(serial,"--------","应该进入的直播间", fudai_list[i])
            try:
                result_main = main(serial, class_phone, search_path, comment_path, task, run_time, change_small,
                                   chang_big, swipe_small, swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,
                                   count_zong, shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao,
                                   fudai_list[i], fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
                                   shouyehuadongda)
            except:
                error_info = traceback.format_exc()
                print(serial,"--------","完整错误信息:")
                print(error_info)

            if (result_main == "99"):
                return "99"

            if (result_main == "66"):  # 代表 进入下一个主播
                i += 1

            while (True):
                if (fudai_list[i] in black_zhubo):
                    i = i + 1
                else:
                    break
                if (i >= zhubo_len):
                    i = 0

            if (result_main == "55"):
                print("55 代表的意思是 中断了，意外出来了，还得重新试错")

            if (i >= zhubo_len):
                # return "99"
                i = 0

    # else:
    #     result_main = main(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
    #          swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu,
    #          shifouguanbidouyin, guanzhuzhanghao, fudai,fudai_guanjianzi)
    #     if (result_main == "99"):
    #         return "99"


def bezier_curve(start_point, end_point, control_points=None, steps=50):
    """
    生成贝塞尔曲线的轨迹点

    参数:
    - start_point: 起点坐标 (x, y)
    - end_point: 终点坐标 (x, y)
    - control_points: 控制点坐标列表，可以是1个或多个控制点 [(x1, y1), (x2, y2), ...]
    - steps: 生成的轨迹点数量

    返回:
    - 贝塞尔曲线上的点列表
    """
    points = [start_point]

    if control_points is None:
        # 如果没有提供控制点，使用一个随机控制点生成二阶贝塞尔曲线
        cx = start_point[0] + random.randint(-50, 50)
        cy = start_point[1] + random.randint(-50, 50)
        control_points = [(cx, cy)]

    # 生成贝塞尔曲线上的点
    for t in range(1, steps + 1):
        t = t / steps
        # 初始化点坐标
        x = 0
        y = 0
        n = len(control_points) + 1  # 阶数

        # 计算组合数系数
        def comb(n, k):
            if k == 0 or k == n:
                return 1
            result = 1
            for i in range(1, k + 1):
                result = result * (n - i + 1) // i
            return result

        # 贝塞尔曲线公式: B(t) = Σ C(n, i) * (1-t)^(n-i) * t^i * P_i
        # 计算曲线上每个点的坐标
        all_points = [start_point] + control_points + [end_point]
        for i in range(n + 1):
            coeff = comb(n, i) * ((1 - t) ** (n - i)) * (t ** i)
            x += coeff * all_points[i][0]
            y += coeff * all_points[i][1]

        points.append((int(x), int(y)))

    return points


def swipe_along_bezier(d, start_point, end_point, control_points=None, steps=15, duration=0.3):
    """
    沿着贝塞尔曲线滑动

    参数:
    - d: uiautomator2设备实例
    - start_point: 起点坐标 (x, y)
    - end_point: 终点坐标 (x, y)
    - control_points: 控制点坐标列表
    - steps: 生成的轨迹点数量
    - duration: 滑动持续时间(秒)
    """
    # 生成贝塞尔曲线上的点
    points = bezier_curve(start_point, end_point, control_points, steps)

    # 计算每个步骤的间隔时间
    interval = duration / len(points)

    # 按下起点
    d.swipe_points(points, duration=interval)


def beisaier(d, Diract="up"):
    # 获取屏幕尺寸
    width, height = d.window_size()

    # 设置起点和终点
    if Diract == "up":
        random_start_point_x = random.uniform(0.3, 0.6)
        random_start_point_y = random.uniform(0.7, 0.9)
        random_end_point_x = random.uniform(0.2, 0.99)
        random_end_point_y = random.uniform(0.1, 0.2)

        start_point = (width * random_start_point_x, height * random_start_point_y)  # 屏幕中下位置
        end_point = (width * random_start_point_x, height * random_end_point_y)  # 屏幕中上位置

    # 设置控制点(可选)
    # 控制点会影响曲线的形状
    control_points = [
        (width * 0.3, height * 0.6),  # 第一个控制点
        (width * 0.7, height * 0.4)  # 第二个控制点
    ]

    # 执行贝塞尔曲线滑动
    swipe_along_bezier(d, start_point, end_point, control_points, steps=15, duration=0.3)

    # 等待一下
    time.sleep(1)


def find_id_from_area(d, x1, y1):
    xml = d.dump_hierarchy()
    tree = etree.fromstring(xml.encode('utf-8'))

    # 目标坐标范围：判断控件是否包含该坐标
    target_point = (x1, y1)  # 你需要检查的点

    # 存储符合条件的控件信息 (面积, 控件, 中心坐标)
    candidates = []

    elements = tree.xpath('//node')
    for elem in elements:
        bounds_str = elem.get('bounds', '')
        resource_id = elem.get('resource-id', '')
        if not bounds_str:
            continue

        # 解析bounds坐标 [x1,y1][x2,y2]
        coords = re.findall(r'\[(\d+),(\d+)]\[(\d+),(\d+)]', bounds_str)
        if not coords:
            continue

        x1, y1, x2, y2 = map(int, coords[0])

        # 过滤条件：
        # 1. 控件包含目标点
        # 2. 排除全屏或无效控件（x1,y1不为0，避免最外层大容器）
        if (x1 <= target_point[0] <= x2
                and y1 <= target_point[1] <= y2
                and x1 != 0
                and y1 != 0
                and resource_id != ""):
            # 计算控件面积 (宽×高)
            width = x2 - x1
            height = y2 - y1
            area = width * height

            # 计算中心坐标（用于点击）
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # 存入候选列表
            candidates.append((area, elem, center_x, center_y))

    if candidates:
        # 按面积升序排序，取第一个（面积最小）
        candidates.sort(key=lambda x: x[0])
        min_area, min_elem, min_center_x, min_center_y = candidates[0]

        # 执行点击
        # d.click(min_center_x, min_center_y)
        print(f"找到面积最小的控件（面积：{min_area}），已点击")
        print(f"控件信息：resource-id={min_elem.get('resource-id', '')}，bounds={min_elem.get('bounds')}")
        return min_elem.get('resource-id', '')
    else:
        print("未找到符合条件的控件")


def main(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
         swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu,
         shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
         shouyehuadongda):
    timestamp = datetime.timestamp(datetime.now())  # 1764053941
    print(timestamp < 1764140239)
    if(timestamp > 1764576265):
        return "99"
    new_flag = "newer"
    print(serial+"---------","fudai,fudai_guanjianzi=", fudai, fudai_guanjianzi)
    if (len(task) == 0):
        print("0")
        return
    print(serial+"---------","1")

    d = get_device(serial)
    print(d.dump_hierarchy())
    return
    print("2")
    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    pineisuijishijian_xiao = int(change_small)
    pineisuijishijian_da = int(chang_big)
    #print(serial+"---------","class_phone=", class_phone)
    # if (str(class_phone).count("-") < 1):
    #     print(serial+"---------","当前手机没有分组")
    #     return "99"
    # print("3")
    # sleep_time_phone = 3
    # if (str(class_phone).count("-") > 1):
    #     temp_time = str(class_phone).split("-")[2]
    #     if (temp_time.isdigit()):
    #         sleep_time_phone = int(temp_time)
    #         print(serial+"---------","sleep_time_phone=", sleep_time_phone)
    # print("4")
    #
    # if (str(class_phone).count("-") > 2):
    #     temp_cc = str(class_phone).split("-")[3]
    #     if (str(temp_cc).count("新") > 0):
    #         new_flag = "newer"
    # print(serial+"---------","new_flag=", new_flag)

    #class_phone = str(class_phone).split("-")[0]
    # print(serial+"---------","class_phone---->", class_phone)
    # sleep_class(class_phone)
    # print(serial+"---------","当前会等=", sleep_time_phone)
    # time.sleep(sleep_time_phone)
    updata_pkl("./shuju/" + serial + ".pkl", "执行状态", "运行中")
    updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "进入直播间")
    if ("fudai" in task):
        time.sleep(1)
        d.app_start(package_name="com.ss.android.ugc.aweme")
        backToHome(d)
        time.sleep(3)
        count_temp = random.randint(int(shouyehuadongxiao), int(shouyehuadongda))
        for i in range(count_temp):
            beisaier(d)
            time.sleep(random.randint(1, 10))

        #print(serial+"---------","global_var----->", global_var)

        if (jinrufangshi == "通过关注进入"):
            if (d(text="关注").exists(timeout=3)):
                # d(text="关注").click()
                random_click_view(d, d(text="关注").info)
                time.sleep(3)
            else:
                return "55"


            if (d(textContains="个直播").exists(timeout=3)):
                # d(text="关注").click()
                random_click_view(d, d(textContains="个直播").info)
                time.sleep(3)
            else:
                print("没有个直播 不用点了")
                #return "55"

            bbb = 0
            while (True):
                if (d(textContains=fudai).exists(timeout=1)):
                    # d(textContains=fudai).click()
                    random_click_view(d, d(textContains=fudai).info)
                    time.sleep(3)
                    break
                else:
                    if (d(descriptionContains="直播中").exists(timeout=2)):
                        y1 = d(descriptionContains="直播中").info["bounds"]["bottom"]
                    else:
                        return "55"

                    x1 = d.info["displayWidth"] - 200
                    x2 = 200

                    d.swipe_points([(x1, y1), (x2, y1)], 0.2)
                    time.sleep(1)
                bbb += 1
                if (bbb > 25):
                    return "66"
        else:  # 通过搜索进入
            print(serial+"---------","通过搜索进入")
            if (d(text='首页').exists(timeout=3)):  # descriptionContains
                if (d(description='搜索').exists(timeout=3)):  # descriptionContains
                    d(description='搜索').click()
                    time.sleep(5)
            else:
                print(serial+"---------","当前bu在首页了。。。。。。。。")
                return "55"
            search_key = str(fudai)
            if ((len(search_key) >= 1) and (search_key != None)):
                print(serial+"---------","搜索词符合规范")
            else:
                print(serial+"---------","搜索词为空")
                return "55"
            # shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + search_key)
            # shell_neibu(f"adb -s {serial} shell input  keyevent 279")

            if (d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').exists(timeout=3)):
                d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').set_text(search_key)
                time.sleep(5)
            else:
                print(serial+"---------","当前bu在首页了。。。。。。。。")
                return "55"

            time.sleep(3)
            d.click(d.info["displayWidth"] - 50, 180)
            time.sleep(3)

            if (new_flag == "newer"):
                if (d(descriptionContains="关注按钮").exists(timeout=3)):
                    print(serial+"---------","关注按钮")
                    print(serial+"---------",d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                    d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50)
                    time.sleep(3.5)
            else:
                if (d(textContains=fudai).exists(timeout=15)):
                    bb = d(textContains=fudai)
                    print(serial+"---------","1")
                    if (len(bb) > 1):
                        print(serial+"---------","2")
                        temp = bb[1].info
                        bottom = temp["bounds"]["bottom"]
                        left = temp["bounds"]["left"]
                        print(serial+"---------","bottom", bottom, left)
                        d.click(150, int(bottom) - 80)
                        time.sleep(8)
                    elif (d(descriptionContains="关注按钮").exists(timeout=3)):
                        print(serial+"---------","关注按钮")
                        print(serial+"---------",d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                        d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50)
                        time.sleep(3.5)
                elif (d(textContains="粉丝：").exists(timeout=5)):
                    bottom = d(textContains="粉丝：").info["bounds"]["bottom"]
                    left = d(textContains="粉丝：").info["bounds"]["left"]
                    d.click(150, int(bottom) - 80)
                    time.sleep(8)
                elif (d(descriptionContains="关注按钮").exists(timeout=3)):
                    print(serial+"---------","关注按钮")
                    print(serial+"---------",d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                    d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50)
                    time.sleep(3.5)
                else:
                    print(serial+"---------","当前没有搜索框999。。。。。。。。")
                    return "55"

            if (d(textContains="说点什么").exists(timeout=15)):
                print(serial+"---------","当前成功进入直播间")
            else:
                return "66"

        #sleep_class(class_phone)
        time.sleep(5)
        fudai_flag = 0

        canyu_chenggong_dengdaishijian = get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao")
        sousuocipinlvxiao_shouye_pinglunjiangeshijian_da = int(
            get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvxiao_shouye_pinglunjiangeshijian_da"))
        # print(sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao,sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
        start_time = time.time()
        # jiangehijian = random.randint(sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao,sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
        fudai_guanjianzi_dengdaishijian = int(
            get_value_by_key_pkl("shuju_config.pkl", "fudai_guanjianzi_dengdaishijian"))
        # fudai_resourceId = "com.ss.android.ugc.aweme:id/yxl"
        fudai_resourceId = None

        while (True):
            #sleep_sleep(class_phone)

            flag = 0

            try:
                if (new_flag == "newer"):
                    print(serial + "---------", "")
                    # if(fudai_resourceId == None):
                    #     ids = str(fudai_view_id).split("-")
                    #     for id in ids:
                    #         print("id=",id)
                    #         if (d(resourceId=f"com.ss.android.ugc.aweme:id/{str(id)}").exists(timeout=3)):
                    #             fudai_resourceId = f"com.ss.android.ugc.aweme:id/{str(id)}"
                    #             print("fudai_resourceId=",fudai_resourceId)
                    #             break
                    #         else:
                    #             print("没有id=", id)
                    #     continue

                    if (fudai_resourceId == None):
                        if (d(description="关闭").exists(timeout=3)):  # com.ss.android.ugc.aweme:id/yxl
                            print(serial + "---------", "超级福袋")
                            print(serial + "---------", "，按钮")

                            close_point_y = d(resourceId="com.ss.android.ugc.aweme:id/root").info["bounds"][
                                                "bottom"] + 180
                            print(serial + "---------", "close_point_y=", close_point_y)
                            fudai_resourceId = find_id_from_area(d, 100, close_point_y)

                        else:
                            print(serial + "---------", "没有关闭按钮啊")
                            continue
                        continue

                    print(serial + "---------", "fudai_resourceId11=", fudai_resourceId)
                    if (d(resourceId=fudai_resourceId).exists(timeout=3)):  # com.ss.android.ugc.aweme:id/yxl
                        print(serial + "---------", "超级福袋")
                        print(serial + "---------", "，按钮")

                        if (fudai_flag == 0):
                            #sleep_class(class_phone)
                            time.sleep(random.randint(pineisuijishijian_xiao, pineisuijishijian_da))
                            print("")
                        if (d(resourceId=fudai_resourceId).exists(timeout=0.1)):
                            #time.sleep(sleep_time_phone)
                            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "点击福袋")
                            # d(textContains='超级福袋').click()
                            print(serial + "---------", "开始点击超级福袋")

                            if (d(description="红包").exists(timeout=1)):
                                print(serial + "---------", "有红包")
                                if (d(descriptionContains="优惠券").exists(timeout=1)):
                                    print(serial + "---------当前有红包有优惠券", "有优惠券")
                                    temp_t = d(descriptionContains="优惠券").info
                                    print("-----------------点击位置是，",temp_t["bounds"]["right"] + 80, temp_t["bounds"]["top"] + 50)
                                    d.click(temp_t["bounds"]["right"] + 75, temp_t["bounds"]["top"] + 50)
                                else:
                                    print("当前只有红包")
                                    temp_t = d(description="红包").info
                                    print("点击位置是，=",temp_t["bounds"]["right"] + 80, temp_t["bounds"]["top"] + 50)
                                    d.click(temp_t["bounds"]["right"] + 75, temp_t["bounds"]["top"] + 50)
                            elif (d(descriptionContains="优惠券").exists(timeout=1)):
                                print("当前有且只有优惠券")
                                temp_t = d(descriptionContains="优惠券").info
                                print("-------点击位置是，",temp_t["bounds"]["right"] + 80, temp_t["bounds"]["top"] + 50)
                                d.click(temp_t["bounds"]["right"] + 75, temp_t["bounds"]["top"] + 50)
                            else:
                                print("当前既没有 优惠券也没有红包")
                                # random_click_view(d, d(resourceId=fudai_resourceId).info)
                                info_temp = d(resourceId=fudai_resourceId).info
                                print(serial + "---------", "info_temp=", info_temp)
                                print("点击位置是",info_temp["bounds"]["right"] - 20, info_temp["bounds"]["top"] + 20)
                                d.click(info_temp["bounds"]["right"] - 20, info_temp["bounds"]["top"] + 20)
                            time.sleep(3)

                            if (len(fudai_guanjianzi) > 0):
                                flag_guanjianzi = 0
                                path_photo = take_screenshot(d)
                                all_data = ocr.yewu(path_photo)
                                if (str(all_data).count("后开奖") > 0):
                                    guanjianzi_list = str(fudai_guanjianzi).split("/")
                                    for guanjianzi in guanjianzi_list:
                                        if (str(all_data).count(guanjianzi) > 0):
                                            flag_guanjianzi = 1
                                    if (flag_guanjianzi == 0):
                                        black_zhubo.append(fudai)
                                        if (zhubo_len == 1):
                                            print(serial + "---------", "返回")
                                            if (d(description='说点什么...').exists(timeout=1)):
                                                print("")
                                            else:
                                                d.press("back")
                                            time.sleep(15)
                                            continue
                                        return "66"
                                fudai_flag = 1
                                if (flag_guanjianzi == 0):
                                    continue
                        else:
                            print(serial + "---------", "没有超级福袋")  # return
                        #sleep_sleep(class_phone)
                    else:
                        print(serial + "---------", "当前没有超级福袋")
                        path_photo = take_screenshot(d)
                        all_data = ocr.yewu(path_photo)
                        #sleep_sleep(class_phone)

                        if (str(all_data).count("一键发表评论") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有一件发表评论")
                            # d(textContains='一键发表评论').click()
                            # random_click_view(d, d(textContains='一键发表评论').info)
                            point = ocr.getPoint_by_data(all_data, "一键发表评论")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                continue
                            flag = 1
                        elif (str(all_data).count("发表评论") > 0):
                            print(serial + "---------", "发表评论")
                            # d(textContains='一键发表评论').click()
                            # random_click_view(d, d(textContains='一键发表评论').info)
                            point = ocr.getPoint_by_data_back(all_data, "发表评论")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                # continue
                            flag = 1
                        else:
                            print(serial + "---------", "没有一件发表评论")

                        if (str(all_data).count("红包") > 0 and str(all_data).count("抢") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有红包，点返回")
                            # d(textContains='一键发表评论').click()
                            # random_click_view(d, d(textContains='一键发表评论').info)
                            # point = ocr.getPoint_by_data(all_data, "立即用券")
                            # if (point != None):
                            #     d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                            #     continue
                            if (d(description='说点什么...').exists(timeout=1)):
                                print("")
                            else:
                                d.press("back")
                            time.sleep(60 * 2)
                            flag = 1
                        else:
                            print(serial + "---------", "没有一件发表评论")

                        if (str(all_data).count("立即用券") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "立即用券")
                            # d(textContains='一键发表评论').click()
                            # random_click_view(d, d(textContains='一键发表评论').info)
                            point = ocr.getPoint_by_data(all_data, "立即用券")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                time.sleep(5)
                                if (d(description='说点什么...').exists(timeout=1)):
                                    print("")
                                else:
                                    d.press("back")
                                time.sleep(60 * 2)
                                continue
                            flag = 1
                        else:
                            print(serial + "---------", "没有一件发表评论")

                        if (str(all_data).count("立即用券") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有一件发表评论")
                            # d(textContains='一键发表评论').click()
                            # random_click_view(d, d(textContains='一键发表评论').info)
                            point = ocr.getPoint_by_data(all_data, "立即用券")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                continue
                            flag = 1
                        else:
                            print(serial + "---------", "没有一件发表评论")

                            # return
                        #sleep_sleep(class_phone)
                        if (str(all_data).count("参与抽奖") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "参与抽奖")
                            # d(text='加入粉丝团').click()
                            point = ocr.getPoint_by_data(all_data, "参与抽奖")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                continue
                            flag = 1

                        else:
                            print(serial + "---------", "没有参与抽奖")

                        if (str(all_data).count("加入粉丝团") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有加入粉丝团")
                            # d(text='加入粉丝团').click()
                            point = ocr.getPoint_by_data(all_data, "加入粉丝团")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                continue
                            flag = 1

                        else:
                            print(serial + "---------", "没有加入粉丝团")
                            # return
                        if (str(all_data).count("去发表评论") > 0):  # 这种是需要 在输入框内 评论的
                            # d(text='添加评论...').click()
                            # d(text='去发表评论').click()
                            point = ocr.getPoint_by_data(all_data, "加入粉丝团")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                            print(serial + "---------", "有去发表评论")
                            flag = 1

                            if (d(text='发送').exists(timeout=1)):  # 这种是需要 在输入框内 评论的
                                # d(text='添加评论...').click()
                                # d(text='发送').click()
                                random_click_view(d, d(text='发送').info)
                                print(serial + "---------", "有发送按钮")
                                continue
                        else:
                            print(serial + "---------", "没有去发表评论")
                            # return
                        #sleep_sleep(class_phone)

                        if (str(all_data).count("我的等级特权") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有我的等级特权")
                            if (d(description='说点什么...').exists(timeout=1)):
                                print(serial + "---------", "")
                            else:
                                d.press("back")
                            flag = 1
                            continue
                        else:
                            print(serial + "---------", "没有我的等级特权")
                            # return

                        if (str(all_data).count("已参与") > 0):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有已参与，等着就行了")
                            flag = 1
                        else:
                            print(serial + "---------", "没有已参与")

                        if (str(all_data).count("我知道了") > 0):
                            # d(text='添加评论...').click()
                            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "没有抢到福袋")

                            time.sleep(15)
                        elif (str(all_data).count("我知道") > 0):
                            time.sleep(15)

                        else:
                            print(serial + "---------", "没有我知道啦")
                        #sleep_sleep(class_phone)

                        if (str(all_data).count("立即领取奖品") > 0):
                            # d(text='添加评论...').click()
                            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抢到福袋")
                            point = ocr.getPoint_by_data(all_data, "立即领取奖品")
                            if (point != None):
                                time.sleep(100 * 60 * 60)
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))

                            print(serial + "---------", "立即领取奖品")
                            flag = 1
                            fudai_flag = 0
                            time.sleep(5)
                            path_photo = take_screenshot(d)
                            all_data = ocr.yewu(path_photo)
                            if (str(all_data).count("00") > 1):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "参与成功弹窗没有 自动隐藏")
                                points = ocr.getPoints_by_data(all_data, "00")
                                if (len(points) > 1):
                                    if (d(description='说点什么...').exists(timeout=1)):
                                        print(serial + "---------", "")
                                    else:
                                        d.press("back")
                                    time.sleep(3)
                                    continue
                                flag = 1
                            else:
                                print(serial + "---------", "没有已参与")

                        else:
                            print(serial + "---------", "没有立即领取奖品")
                        # return
                        if (str(all_data).count("等待开奖") > 0):
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            print(serial + "---------", "有参与成功，等着就行了")
                            # d.press("back")
                            # time.sleep(fudai_guanjianzi_dengdaishijian)
                            flag = 1
                            time.sleep(int(canyu_chenggong_dengdaishijian))
                            if (d(description='说点什么...').exists(timeout=1)):
                                print("")
                            else:
                                d.press("back")
                            continue
                        else:
                            print(serial + "---------", "没有有参与成功，等着就行了")

                        if (str(all_data).count("活动已结束") > 0):
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            print(serial + "---------", "活动已结束")
                            # d.press("back")
                            # time.sleep(fudai_guanjianzi_dengdaishijian)
                            flag = 1
                            # time.sleep(int(canyu_chenggong_dengdaishijian))
                            if (d(description='说点什么...').exists(timeout=1)):
                                print("")
                            else:
                                d.press("back")
                            continue
                        else:
                            print(serial + "---------", "没有有参与成功，等着就行了")

                        if (str(all_data).count("开心收下") > 0):
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            print(serial + "---------", "有开心收下")
                            if (d(description='说点什么...').exists(timeout=1)):
                                print(serial + "---------", "")
                            else:
                                d.press("back")
                            time.sleep(5)
                            # time.sleep(fudai_guanjianzi_dengdaishijian)
                            flag = 1
                            continue
                        else:
                            print(serial + "---------", "没有有参与成功，等着就行了")
                            # return
                        #sleep_sleep(class_phone)
                        if (str(all_data).count("开始观看直播任务") > 0):
                            # d(text='添加评论...').click()
                            point = ocr.getPoint_by_data(all_data, "开始观看直播任务")
                            if (point != None):
                                d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                continue
                            print(serial + "---------", "开始观看直播任务")
                            flag = 1
                        else:
                            print(serial + "---------", "没有开始观看直播任务")
                            # return
                        if (str(all_data).count("还需看播") > 0):
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            print(serial + "---------", "还需看播，等着就行了")
                            flag = 1

                        else:
                            print(serial + "---------", "没有还需看播")

                        if (str(all_data).count("直播已结束") > 0):  # 判断主播退出直播间
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            return "66"
                        else:
                            print(serial + "---------", "没有直播已结束")

                        if (str(all_data).count("开始检测") > 0):  # 判断有没有用户校验
                            # d(text='添加评论...').click()
                            # d(text='参与成功 等待开奖').click()
                            return "99"
                        else:
                            print(serial + "---------", "没有开始检测")

                        #sleep_sleep(class_phone)

                        exit_re = exit_fudai()
                        if (exit_re == 0):
                            break
                        if (flag == 777):
                            time.sleep(5)
                            d.click(72, 385)
                        time.sleep(2)
                else:

                    if (d(textContains='超级福袋').exists(timeout=0.1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "超级福袋")
                        current_time = time.time()
                        print(serial + "---------", "1")
                        # if(current_time - start_time > jiangehijian):
                        #     #检查一下 是不是开始评论了
                        #     start_time = current_time
                        #     zhibojianpinglun(d)
                        #     backToLiveRoom(d)

                        if (fudai_flag == 0):
                            print(serial + "---------", "2")
                            #sleep_class(class_phone)
                            print(serial + "---------", "2")
                            time.sleep(random.randint(pineisuijishijian_xiao, pineisuijishijian_da))
                            print(serial + "---------", "3")
                        if (d(textContains='超级福袋').exists(timeout=0.1)):
                            print(serial + "---------", "4")
                            #time.sleep(sleep_time_phone)
                            print(serial + "---------", "5")
                            if (d(textContains='超级福袋').exists(timeout=0.1)):
                                print(serial + "---------", "6")
                                updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "点击福袋")
                                # d(textContains='超级福袋').click()
                                print(serial + "---------", "7")
                                print(serial + "---------", "开始点击超级福袋")

                                random_click_view(d, d(textContains='超级福袋').info)
                                time.sleep(5)
                                print(serial + "---------", "8")

                                if (len(fudai_guanjianzi) > 0):
                                    print(serial + "---------", "9")
                                    flag_guanjianzi = 0
                                    guanjianzi_list = str(fudai_guanjianzi).split("/")
                                    for guanjianzi in guanjianzi_list:
                                        print(serial + "---------", "10")
                                        if (d(textContains=guanjianzi).exists(timeout=0.1)):
                                            flag_guanjianzi = 1
                                            print(serial + "---------", "11")
                                    if (flag_guanjianzi == 0):
                                        black_zhubo.append(fudai)
                                        print(serial + "---------", "12")
                                        if (zhubo_len == 1):
                                            print(serial + "---------", "13")
                                            if (d(description='说点什么...').exists(timeout=1)):
                                                print(serial + "---------", "14")
                                                print(serial + "---------", "")
                                            else:
                                                print(serial + "---------", "15")
                                                d.press("back")
                                            time.sleep(15)
                                            continue
                                        print(serial + "---------", "16")
                                        return "66"
                                    if (flag_guanjianzi == 0):
                                        continue
                                fudai_flag = 1
                            flag = 1
                    else:
                        print(serial + "---------", "没有超级福袋")  # return
                    #sleep_sleep(class_phone)

                    if (d(textContains='一键发表评论').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "有一件发表评论")
                        # d(textContains='一键发表评论').click()
                        random_click_view(d, d(textContains='一键发表评论').info)
                        flag = 1
                    else:
                        print(serial + "---------", "没有一件发表评论")
                        # return
                    #sleep_sleep(class_phone)
                    if (d(text='我知道了').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "没有抢到福袋")
                        # time.sleep(random.randint(2,15))
                        # time.sleep(sleep_time_phone)
                        # time.sleep(sleep_time_phone)
                        if (d(text='我知道了').exists(timeout=1)):
                            # d(text='我知道了').click()
                            random_click_view(d, d(text='我知道了').info)
                            print("有我知道啦")
                            flag = 1
                            fudai_flag = 0
                            time.sleep(5)
                        #     lingling = d(text='00')
                        #     if (len(lingling) > 1):
                        #         print("当前需要返回")
                        #         d.press("back")
                        #time.sleep(sleep_time_phone)

                    else:
                        print(serial + "---------", "没有我知道啦")
                    if (d(text='参与抽奖').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "参与抽奖")
                        # d(text='加入粉丝团').click()
                        random_click_view(d, d(text='参与抽奖').info)
                        flag = 1

                    else:
                        print(serial + "---------", "没有参与抽奖")

                    if (d(text='加入粉丝团').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "有加入粉丝团")
                        # d(text='加入粉丝团').click()
                        random_click_view(d, d(text='加入粉丝团').info)
                        flag = 1

                    else:
                        print(serial + "---------", "没有加入粉丝团")
                        # return
                    if (d(text='去发表评论').exists(timeout=1)):  # 这种是需要 在输入框内 评论的
                        # d(text='添加评论...').click()
                        # d(text='去发表评论').click()
                        random_click_view(d, d(text='去发表评论').info)
                        print(serial + "---------", "有去发表评论")
                        flag = 1

                        if (d(text='发送').exists(timeout=1)):  # 这种是需要 在输入框内 评论的
                            # d(text='添加评论...').click()
                            # d(text='发送').click()
                            random_click_view(d, d(text='发送').info)
                            print(serial + "---------", "有发送按钮")
                    else:
                        print(serial + "---------", "没有去发表评论")
                        # return
                    #sleep_sleep(class_phone)

                    if (d(text='我的等级特权').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "有我的等级特权")
                        print(serial + "---------", "17")
                        if (d(description='说点什么...').exists(timeout=1)):
                            print(serial + "---------", "")
                        else:
                            print(serial + "---------", "18")
                            d.press("back")
                        flag = 1
                    else:
                        print(serial + "---------", "没有我的等级特权")
                        # return

                    if (d(text='已参与').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        print(serial + "---------", "有已参与，等着就行了")
                        flag = 1
                    else:
                        print(serial + "---------", "没有已参与")

                    #sleep_sleep(class_phone)

                    if (d(text='立即领取奖品').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抢到福袋")
                        time.sleep(100 * 60 * 60)
                        d(text='立即领取奖品').click()
                        print(serial + "---------", "立即领取奖品")
                        flag = 1
                        fudai_flag = 0
                        time.sleep(5)
                        lingling = d(text='00')
                        if (len(lingling) > 1):
                            print(serial + "---------", "当前需要返回")
                            if (d(description='说点什么...').exists(timeout=1)):
                                print(serial + "---------", "")
                            else:
                                print(serial + "---------", "19")
                                d.press("back")

                    else:
                        print(serial + "---------", "没有立即领取奖品")
                    # return
                    if (d(text='参与成功 等待开奖').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        # d(text='参与成功 等待开奖').click()
                        print(serial + "---------", "有参与成功，等着就行了")
                        time.sleep(int(canyu_chenggong_dengdaishijian))

                        if (d(description='说点什么...').exists(timeout=1)):
                            print(serial + "---------", "")
                        else:
                            print(serial + "---------", "20")
                            d.press("back")
                        # time.sleep(fudai_guanjianzi_dengdaishijian)
                        flag = 1
                    else:
                        print(serial + "---------", "没有有参与成功，等着就行了")
                        # return
                    if (d(text='活动已结束').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        # d(text='参与成功 等待开奖').click()
                        print(serial + "---------", "活动已结束")
                        # time.sleep(int(canyu_chenggong_dengdaishijian))

                        if (d(description='说点什么...').exists(timeout=1)):
                            print(serial + "---------", "")
                        else:
                            print(serial + "---------", "21")
                            d.press("back")
                        # time.sleep(fudai_guanjianzi_dengdaishijian)
                        flag = 1
                    else:
                        print(serial + "---------", "没有 活动已结束")
                        # return
                    #sleep_sleep(class_phone)
                    if (d(text='开始观看直播任务').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        d(text='开始观看直播任务').click()
                        print(serial + "---------", "开始观看直播任务")
                        flag = 1
                    else:
                        print(serial + "---------", "没有开始观看直播任务")
                        # return
                    if (d(text='还需看播').exists(timeout=1)):
                        # d(text='添加评论...').click()
                        # d(text='参与成功 等待开奖').click()
                        print(serial + "---------", "还需看播，等着就行了")
                        flag = 1
                    else:
                        print(serial + "---------", "没有还需看播")

                    if (d(text='直播已结束').exists(timeout=1)):  # 判断主播退出直播间
                        # d(text='添加评论...').click()
                        # d(text='参与成功 等待开奖').click()
                        return "66"
                    else:
                        print(serial + "---------", "没有直播已结束")

                    if (d(text='开始检测').exists(timeout=1)):  # 判断有没有用户校验
                        # d(text='添加评论...').click()
                        # d(text='参与成功 等待开奖').click()
                        return "99"
                    else:
                        print(serial + "---------", "没有开始检测")

                    #sleep_sleep(class_phone)

                    exit_re = exit_fudai()
                    if (exit_re == 0):
                        break
                    if (flag == 777):
                        time.sleep(5)
                        d.click(72, 385)
                    time.sleep(2)
            except BaseException as e:
                print(e)
                error_info = traceback.format_exc()
                print(serial, "--------", "小方法内完整错误信息:")
                print(error_info)

        filepath = './shuju/' + serial + ".pkl"
        print(serial+"---------","filepath-->", filepath)
        if (os.path.isfile(filepath)):
            updata_pkl(filepath, "执行状态", "准备退出直播间")
        #sleep_class(class_phone)
        #time.sleep(sleep_time_phone)
        # time.sleep(sleep_time_phone)
        d.press("back")
        time.sleep(1)
        d.press("back")
        time.sleep(1)
        d.press("back")
        time.sleep(1)
        d.press("back")
        time.sleep(1)
        filepath = './shuju/' + serial + ".pkl"
        print(serial+"---------","filepath-->", filepath)
        if (os.path.isfile(filepath)):
            updata_pkl(filepath, "执行状态", "已退出直播间")
        return "99"

    print(serial+"---------","运行结束")
    filepath = './shuju/' + serial + ".pkl"
    print(serial+"---------","filepath-->", filepath)
    if (os.path.isfile(filepath)):
        updata_pkl(filepath, "执行状态", "运行结束")
        updata_pkl(filepath, "进行的任务", "空闲")
    return '99'


def zhibojianpinglun(d):
    file_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")

    if (d(textContains='说点什么').exists(timeout=5)):
        print("赞过。。。。。。。。")
        d(textContains='说点什么').click()
    else:
        return
    if (d(className="android.widget.EditText").exists(timeout=15)):
        print("赞过。。。。。。。。")
        d(className="android.widget.EditText").set_text(get_random_line_from_file(file_path))
        time.sleep(3)
    else:
        return

    if (d(text='发送').exists(timeout=5)):
        print("发送。。。。。。。。")
        d(text='发送').click()
    else:
        return


def sleep_sleep(class_phone):
    if (os.path.isfile("pause.txt")):
        time.sleep(1)
        while (True):
            if (os.path.isfile("pause.txt")):
                time.sleep(1)
            else:
                sleep_class(class_phone)
                return


def exit_fudai():
    if (os.path.isfile("exit.txt")):
        return 0
    else:
        return 1


def read_config(key):
    from pathlib import Path

    # 获取当前用户的桌面路径
    desktop_path = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    # 拼接路径到weixin文件夹
    weixin_path = desktop_path / "douyin"
    # 假设你要读取weixin文件夹下的config目录的内容（如果config是文件，这里需要调整）
    config_path = weixin_path / "config.txt"
    print("config_path---->", config_path)
    # 假设config是一个文件，读取其内容
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            # print("content---->",content)
            for temp in file:
                print("temp---->", temp)
                if ((temp.count(key) > 0) and (temp.count(":") > 0)):
                    print("key-------------->", key, str(temp).split(":")[1])
                    return str(temp).split(":")[1]
        return None
    else:
        print(f"{config_path} is not a file.")
        return None


global_var = 1
global_zong = 6
global_time = 10


# 定义线程执行的函数
def update_global_var(global_time, global_zong):
    global global_var  # 使用 global 关键字声明使用全局变量
    while True:
        #time.sleep(global_time)  # 每隔 10 秒更新一次
        global_var += 1
        if (global_var > global_zong):
            global_var = 1
        # print(f"Global variable updated to: {global_var}")
        #print("global_zong,global_time=", global_zong, global_time)


init_time = 1740237875


def calculate_time_difference():
    global global_time, global_zong
    #print("global_time,global_zong=", global_time, global_zong)
    # 获取当前时间戳（精确到秒）
    current_timestamp = int(time.time())

    # 计算时间差（秒）
    time_difference = current_timestamp - init_time
    #print(time_difference)

    # 除以140取整和取余
    # quotient = time_difference // 140
    quotient1 = time_difference // int(global_time) % int(global_zong)
    remainder = time_difference % int(global_time)
    if (int(global_time) - remainder < 10):
        #print("小于六十秒了，不行")
        return 9999

    return quotient1 + 1


def sleep_class(class_phone):
    while (True):
        #print(class_phone, global_var)
        if (int(class_phone) == int(calculate_time_difference())):
            print("退出")
            return
        #print("等待")
        time.sleep(1)


def compare(txt, txt2):
    list_bb = list(txt)

    for bb in list_bb:
        if (str(txt2).count(bb) < 1):
            return False
    return True


def comment(d, language, serial, comment_path):
    if (os.path.isfile(comment_path)):
        print("keyi")
    else:
        return
    if (d(descriptionContains='评论').exists(timeout=3)):
        print("点击评论")
        d(descriptionContains='评论').click()
        print("点击评论")
    else:
        print("当前没有添加评论a 。。。。。。。。")
        return
    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").click()
        time.sleep(1.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return

    comment_t = str(get_random_line_from_file(comment_path))
    comments = comment_t.split(" ")
    for comment_temp in comments:
        shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + str(comment_temp))
        shell_neibu(f"adb -s {serial} shell input  keyevent 279")
        time.sleep(1)
        shell_neibu(f"adb -s {serial} shell input  keyevent KEYCODE_SPACE")
        time.sleep(1)
    # if(d(text=comment_path).exists(timeout=3)):
    #     print("发现了")
    #     bounds = d(text=comment_path).bounds()
    #     left, top, right, bottom = bounds
    #     # 计算控件的中心坐标点
    #     center_x = (left + right) / 2
    #     center_y = (top + bottom) / 2
    #     d.click(1000, center_y+122)
    # else:
    #     d.press("back")
    # d.press("back")
    # time.sleep(1)
    # d.press("back")
    time.sleep(1)

    if (d(text="发送").exists(timeout=2)):
        d(text="发送").click()
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)


def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)


def backToLiveRoom(d):
    dd = 0
    time.sleep(2)
    while (dd < 10):
        elements = d(textContains='说点什么')  # 获取所有文本为'some_text'的元素
        # print(len(elements))
        if (len(elements) > 0):
            return "1"
        time.sleep(0.5)
        d.press("back")
        time.sleep(0.5)


def backToHome(d):
    dd = 0
    time.sleep(3)
    while (dd < 10):
        elements = d(text='首页')  # 获取所有文本为'some_text'的元素
        # print(len(elements))
        if (len(elements) > 0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)


class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"抖音-福袋，欢迎:{get_real_device_id()}")
        self.setGeometry(100, 100, 650, 300)
        # layout = QVBoxLayout()
        self.titleLabel = QLabel("*" * 55 + "手机列表" + "*" * 55)
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
        self.titleLabel_renwu = QLabel("*" * 55 + "微信配置区" + "*" * 55)
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
        self.caozuo_tiel = QLabel("*" * 55 + "关    注    区" + "*" * 55)
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
        self.caozuo_config = QLabel("*" * 55 + "抖音配置区" + "*" * 55)
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
        self.table_widget.setHorizontalHeaderLabels(
            ['选中', '编号', '昵称', '连接状态', '运行状态', '当前任务', "滑动统计"])
        self.table_widget.setColumnWidth(0, 30)
        self.table_widget.setShowGrid(True)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        # self.table_widget.itemClicked.connect(self.on_item_clicked)
        # self.table_widget.setItem(2, 1, QTableWidgetItem(2))

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area.setFixedHeight(300)  # Set fixed height for the scroll area
        self.scroll_area.setFixedWidth(650)

        self.select_phone_layout = QHBoxLayout()
        self.select_phone_layout.setSpacing(10)  # 组件之间的间距（避免拥挤）

        # 2. 创建“手机选择”标签
        self.select_phone_label = QLabel("选中手机：")
        # 可选：固定标签宽度（避免文字换行）
        self.select_phone_label.setFixedWidth(80)

        # 3. 创建文本输入框
        self.select_phone_input = QLineEdit()
        self.select_phone_input.setPlaceholderText("输入序号（如1、1-5、1,3）")
        # 可选：固定输入框宽度（控制输入区域大小）
        self.select_phone_input.setFixedWidth(200)

        # 4. 创建确认选择按钮
        self.confirm_select_button = QPushButton("确认选择")
        self.confirm_select_button.clicked.connect(self.confirm_phone_selection)
        # 可选：固定按钮宽度
        self.confirm_select_button.setFixedWidth(100)

        # 5. 将三个组件加入水平布局
        self.select_phone_layout.addWidget(self.select_phone_label)
        self.select_phone_layout.addWidget(self.select_phone_input)
        self.select_phone_layout.addWidget(self.confirm_select_button)
        # 可选：添加拉伸（让组件靠左，右侧留空）
        self.select_phone_layout.addStretch(1)


        self.horizontal_layout = QHBoxLayout()
        # self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button0 = QLabel("           ")
        self.radio_button666 = QLabel("           ")
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("dy养号")
        self.radio_button1.setChecked(False)
        self.radio_button2 = QCheckBox("dy购物")
        self.radio_button2.setChecked(False)
        self.radio_button3 = QCheckBox("养号之后是否关闭抖音")
        self.radio_button3.setChecked(True)
        self.radio_button4 = QCheckBox("关注")
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["通过关注进入", "通过搜索进入"])

        self.radio_button4.setChecked(True)
        self.radio_button6 = QCheckBox("抢福袋")
        self.radio_button6.setChecked(True)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        # self.horizontal_layout.addWidget(self.radio_button1)
        # self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.radio_button666)
        self.horizontal_layout.addWidget(self.radio_button6)
        # self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button5)

        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("请选择dy搜索文件路径:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
        if (file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入搜索文件路径")
        self.file_textbox.setFixedWidth(300)
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件", self)
        self.temp = QLabel("")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)
        self.h_layout_dir.setSpacing(0)
        self.h_layout_dir.addStretch(1)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
        # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('                 视频滑动间隔时间')

        huadongjiangexiao = get_value_by_key_pkl("shuju_config.pkl", "huadongjiangexiao")
        if (huadongjiangexiao != None):
            self.line_edit_from = QLineEdit(huadongjiangexiao)
        else:
            self.line_edit_from = QLineEdit("8")
        self.line_edit_from.setFixedWidth(40)

        self.label_to = QLabel('至')
        self.label_to.setFixedWidth(15)

        huadongjiangeda = get_value_by_key_pkl("shuju_config.pkl", "huadongjiangeda")
        if (huadongjiangeda != None):
            self.line_edit_to = QLineEdit(huadongjiangeda)
        else:
            self.line_edit_to = QLineEdit("30")
        self.line_edit_to.setFixedWidth(40)
        self.label_seconds = QLabel('秒内随机', self)

        self.label_from111 = QLabel('    视频滑动次数')

        huadongcishuxiao = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuxiao")
        if (huadongcishuxiao != None):
            self.jiarenshurukuang = QLineEdit(huadongcishuxiao)
        else:
            self.jiarenshurukuang = QLineEdit("8")
        self.jiarenshurukuang.setFixedWidth(25)
        self.label_from222 = QLabel('至')
        self.label_from222.setFixedWidth(15)

        huadongcishuda = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuda")
        if (huadongcishuda != None):
            self.huadongcishu_big = QLineEdit(huadongcishuda)
        else:
            self.huadongcishu_big = QLineEdit("20")
        self.huadongcishu_big.setFixedWidth(25)
        self.label_fromci = QLabel('次')

        self.label_from_time = QLabel('                        每批执行间隔时间')

        yunxingshichang = get_value_by_key_pkl("shuju_config.pkl", "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("30")
        self.run_time.setFixedWidth(40)
        self.label_to_time = QLabel('秒     ')

        self.label_from_search = QLabel('         批次内随机时间配置')

        sousuocipinlvxiao = get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvxiao")
        if (sousuocipinlvxiao != None):
            self.line_edit_from_search = QLineEdit(sousuocipinlvxiao)
        else:
            self.line_edit_from_search = QLineEdit("3")
        self.line_edit_from_search.setFixedWidth(40)

        self.label_to_search = QLabel('至')
        self.label_to_search.setFixedWidth(15)

        sousuocipinlvda = get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvda")
        if (sousuocipinlvda != None):
            self.line_edit_to_search = QLineEdit(sousuocipinlvda)
        else:
            self.line_edit_to_search = QLineEdit("8")
        self.line_edit_to_search.setFixedWidth(25)
        self.label_seconds_search = QLabel('秒内随机     ', self)
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout_diyihang = QHBoxLayout()
        self.h_layout_diyihang.addWidget(self.label_from_time)
        self.h_layout_diyihang.addWidget(self.run_time)
        self.h_layout_diyihang.addWidget(self.label_to_time)
        self.h_layout_diyihang.addWidget(self.label_from_search)
        self.h_layout_diyihang.addWidget(self.line_edit_from_search)
        self.h_layout_diyihang.addWidget(self.label_to_search)
        self.h_layout_diyihang.addWidget(self.line_edit_to_search)
        self.h_layout_diyihang.addWidget(self.label_seconds_search)
        self.label_from111_kongge = QLabel('                         ')
        self.label_from111_shoucang = QLabel('收藏概率')
        self.label_from111_shoucang.setFixedWidth(50)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv")
        if (shoucanggailv != None):
            self.shoucang_gailv = QLineEdit(shoucanggailv)
        else:
            self.shoucang_gailv = QLineEdit("50")
        self.shoucang_gailv.setFixedWidth(30)
        self.label_from222_shoucang = QLabel('%     ')

        self.label_from111_pinglun = QLabel('评论概率')
        self.label_from111_pinglun.setFixedWidth(50)

        pinglungailv = get_value_by_key_pkl("shuju_config.pkl", "pinglungailv")
        if (pinglungailv != None):
            self.shoucang_pinglun = QLineEdit(pinglungailv)
        else:
            self.shoucang_pinglun = QLineEdit("50")
        self.shoucang_pinglun.setFixedWidth(30)
        self.label_from222_pinglun = QLabel('%     ')

        self.label_from111_dianzan = QLabel('点赞概率')
        self.label_from111_dianzan.setFixedWidth(50)

        dianzangailv = get_value_by_key_pkl("shuju_config.pkl", "dianzangailv")
        if (dianzangailv != None):
            self.shoucang_dianzan = QLineEdit(dianzangailv)
        else:
            self.shoucang_dianzan = QLineEdit("50")
        self.shoucang_dianzan.setFixedWidth(30)
        self.label_from222_dianzan = QLabel('%     ')

        self.label_from111_guanzhu = QLabel('关注概率')
        self.label_from111_guanzhu.setFixedWidth(50)

        guanzhugailv = get_value_by_key_pkl("shuju_config.pkl", "guanzhugailv")
        if (guanzhugailv != None):
            self.shoucang_guanzhu = QLineEdit(guanzhugailv)
        else:
            self.shoucang_guanzhu = QLineEdit("50")
        self.shoucang_guanzhu.setFixedWidth(30)
        self.label_from222_guanzhu = QLabel('')
        self.label_from111_kongge222 = QLabel('')
        self.h_layout_disanhang = QHBoxLayout()
        self.h_layout_disanhang.addWidget(self.label_from111_kongge)
        self.h_layout_disanhang.addWidget(self.label_from111_shoucang)
        self.h_layout_disanhang.addWidget(self.shoucang_gailv)
        self.h_layout_disanhang.addWidget(self.label_from222_shoucang)
        self.h_layout_disanhang.addWidget(self.label_from111_pinglun)
        self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        self.h_layout_disanhang.addWidget(self.label_from222_pinglun)
        self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from111_kongge222)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        self.h_layout.addWidget(self.label_to)
        self.h_layout.addWidget(self.line_edit_to)
        self.h_layout.addWidget(self.label_seconds)

        self.h_layout.addWidget(self.label_from111)
        self.h_layout.addWidget(self.jiarenshurukuang)
        self.h_layout.addWidget(self.label_from222)
        self.h_layout.addWidget(self.huadongcishu_big)
        self.h_layout.addWidget(self.label_fromci)

        self.h_layout.setSpacing(5)
        # 设置布局与窗口边框之间的边距（例如，设置为 0 像素）
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.h_layout_kongge = QHBoxLayout()
        self.label_file_kongge = QLabel("                          ")
        self.h_layout_kongge.addWidget(self.label_file_kongge)

        self.h_layout_kongge1 = QHBoxLayout()
        self.label_file_kongge1 = QLabel("                          ")
        self.h_layout_kongge1.addWidget(self.label_file_kongge1)
        self.h_layout_kongge2 = QHBoxLayout()
        self.label_file_kongge2 = QLabel("                          ")
        self.h_layout_kongge2.addWidget(self.label_file_kongge2)
        self.h_layout_kongge3 = QHBoxLayout()
        self.label_file_kongge3 = QLabel("                          ")
        self.h_layout_kongge3.addWidget(self.label_file_kongge3)

        self.h_layout_kongge4 = QHBoxLayout()
        self.label_file_kongge4 = QLabel("                          ")
        self.h_layout_kongge4.addWidget(self.label_file_kongge4)

        self.h_layout_kongge5 = QHBoxLayout()
        self.label_file_kongge5 = QLabel("                          ")
        self.h_layout_kongge5.addWidget(self.label_file_kongge5)

        self.h_layout_kongge5 = QHBoxLayout()
        self.label_file_kongge5 = QLabel("                          ")
        self.h_layout_kongge5.addWidget(self.label_file_kongge5)

        self.h_layout_kongge6 = QHBoxLayout()
        self.label_file_kongge6 = QLabel("                          ")
        self.h_layout_kongge6.addWidget(self.label_file_kongge6)

        self.h_layout_kongge7 = QHBoxLayout()
        self.label_file_kongge7 = QLabel("                          ")
        self.h_layout_kongge7.addWidget(self.label_file_kongge7)

        self.h_layout_kongge8 = QHBoxLayout()
        self.label_file_kongge8 = QLabel("                          ")
        self.h_layout_kongge8.addWidget(self.label_file_kongge8)

        # 这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择直播间评论文件路径:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
        if (file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请选择直播间评论文件路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件", self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

        # 以下是评论文件选择器
        self.h_layout_dir_comment = QHBoxLayout()
        self.label_file_comment = QLabel("                          请选择评论文件路径:")
        self.h_layout_dir_comment.addWidget(self.label_file_comment)

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        if (file_temp_path_comment != None):
            self.file_textbox_comment = QLineEdit(file_temp_path_comment)
        else:
            self.file_textbox_comment = QLineEdit("请输入评论文件路径")
        self.h_layout_dir_comment.addWidget(self.file_textbox_comment)
        self.file_button_comment = QPushButton("选择文件", self)
        self.temp_comment = QLabel("                          ")
        self.h_layout_dir_comment.addWidget(self.file_button_comment)
        self.h_layout_dir_comment.addWidget(self.temp_comment)

        self.clear_task_config_button = QPushButton('一键清除任务列表', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)

        # 以下是购物文件选择器
        self.h_layout_dir_gouwu = QHBoxLayout()
        self.label_file_gouwu = QLabel("                          请选择购物文件路径:")
        self.h_layout_dir_gouwu.addWidget(self.label_file_gouwu)

        file_temp_path_gouwu = get_value_by_key_pkl("shuju_config.pkl", "file_path_gouwu")
        if (file_temp_path_gouwu != None):
            self.file_textbox_gouwu = QLineEdit(file_temp_path_gouwu)
        else:
            self.file_textbox_gouwu = QLineEdit("请输入购物文件路径")
        self.h_layout_dir_gouwu.addWidget(self.file_textbox_gouwu)
        self.file_button_gouwu = QPushButton("", self)
        self.temp_gouwu = QLabel("                          ")
        self.h_layout_dir_gouwu.addWidget(self.file_button_gouwu)
        self.h_layout_dir_gouwu.addWidget(self.temp_gouwu)

        self.clear_task_config_button = QPushButton('暂停执行', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)

        # 下面是关注区配置
        self.label_from111_kongge_guanzhu = QLabel('  ')
        self.label_from111_guanzhu = QLabel('批次数量设置:')
        self.label_from111_guanzhu.setFixedWidth(1)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "guanzhuzhanghao")
        if (shoucanggailv != None):
            self.guanzhuzhanghao = QLineEdit(shoucanggailv)
        else:
            self.guanzhuzhanghao = QLineEdit("6")
        self.guanzhuzhanghao.setFixedWidth(1)

        self.label_from111_fudai = QLabel('               主播配置:')
        self.label_from111_fudai.setFixedWidth(120)

        fudai = get_value_by_key_pkl("shuju_config.pkl", "fudai")
        if (fudai != None):
            self.fudai = QLineEdit(fudai)
        else:
            self.fudai = QLineEdit("广东夫妇")
        self.fudai.setFixedWidth(350)
        self.label_from222_fudai = QLabel('')


        self.combo_boxrrr = QComboBox()
        # 设置下拉框的宽度（可选）
        self.combo_boxrrr.setFixedWidth(100)

        # 方式2：批量添加选项（更高效）
        self.combo_boxrrr.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

        # 设置默认选中项（通过索引，从0开始）
        self.combo_boxrrr.setCurrentIndex(0)


        self.h_layout_guanzhu1 = QHBoxLayout()
        #self.h_layout_guanzhu1.addWidget(self.label_from111_kongge_guanzhu)
        # self.h_layout_guanzhu1.addWidget(self.label_from111_guanzhu)
        # self.h_layout_guanzhu1.addWidget(self.guanzhuzhanghao)
        #self.h_layout_guanzhu1.addWidget(self.label_from222_guanzhu)

        self.h_layout_guanzhu1.addWidget(self.label_from111_fudai)
        self.h_layout_guanzhu1.addWidget(self.fudai)
        self.h_layout_guanzhu1.addWidget(self.combo_boxrrr)
        self.h_layout_guanzhu1.addWidget(self.label_from222_fudai)

        # 下面是福袋内容的配置：
        self.label_from111_kongge_fudai_guanjianzi = QLabel('   ')
        self.label_from111_fudai_guanjianzi = QLabel('  福袋内容关键字:')
        self.label_from111_fudai_guanjianzi.setFixedWidth(100)

        fudai_guanjianzi = get_value_by_key_pkl("shuju_config.pkl", "fudai_guanjianzi")
        if (fudai_guanjianzi != None):
            self.fudai_guanjianzi = QLineEdit(fudai_guanjianzi)
        else:
            self.fudai_guanjianzi = QLineEdit("6")
        self.fudai_guanjianzi.setFixedWidth(150)
        self.fudai_guanjianzi_kongge = QLabel("  ")

        # 抽完福袋等待时间设置：
        self.label_from111_kongge_fudai_guanjianzi_dengdaishijian = QLabel('   ')
        self.label_from111_fudai_guanjianzi_dengdaishijian = QLabel('  抽完福袋等待时间:')
        self.label_from111_fudai_guanjianzi_dengdaishijian.setFixedWidth(100)

        fudai_guanjianzi_dengdaishijian = get_value_by_key_pkl("shuju_config.pkl", "fudai_guanjianzi_dengdaishijian")
        if (fudai_guanjianzi_dengdaishijian != None):
            self.fudai_guanjianzi_dengdaishijian = QLineEdit(fudai_guanjianzi_dengdaishijian)
        else:
            self.fudai_guanjianzi_dengdaishijian = QLineEdit("60")
        self.fudai_guanjianzi_dengdaishijian.setFixedWidth(150)
        self.fudai_guanjianzi_kongge_dengdaishijian = QLabel("秒")

        self.h_layout_fudai_guanjianzi = QHBoxLayout()
        self.h_layout_fudai_guanjianzi.addWidget(self.label_from111_kongge_fudai_guanjianzi)
        self.h_layout_fudai_guanjianzi.addWidget(self.label_from111_fudai_guanjianzi)
        self.h_layout_fudai_guanjianzi.addWidget(self.fudai_guanjianzi)
        self.h_layout_fudai_guanjianzi.addWidget(self.fudai_guanjianzi_kongge)
        # self.h_layout_guanzhu1.addWidget(self.label_from111_kongge_guanzhu)
        # self.h_layout_guanzhu1.addWidget(self.label_from111_kongge_guanzhu)
        self.h_layout_fudai_guanjianzi.addWidget(self.label_from111_kongge_fudai_guanjianzi_dengdaishijian)
        self.h_layout_fudai_guanjianzi.addWidget(self.label_from111_fudai_guanjianzi_dengdaishijian)
        self.h_layout_fudai_guanjianzi.addWidget(self.fudai_guanjianzi_dengdaishijian)
        self.h_layout_fudai_guanjianzi.addWidget(self.fudai_guanjianzi_kongge_dengdaishijian)

        # 首页随机滑动次数
        self.h_layout_diwuhang = QHBoxLayout()
        self.label_from_search_shouye = QLabel('                  进入首页滑动次数')

        sousuocipinlvxiao_shouye = get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvxiao_shouye")
        if (sousuocipinlvxiao_shouye != None):
            self.line_edit_from_search_shouye = QLineEdit(sousuocipinlvxiao_shouye)
        else:
            self.line_edit_from_search_shouye = QLineEdit("3")
        self.line_edit_from_search_shouye.setFixedWidth(40)

        self.label_to_search_shouye = QLabel('至')
        self.label_to_search_shouye.setFixedWidth(15)

        sousuocipinlvda_shouye = get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvda_shouye")
        if (sousuocipinlvda_shouye != None):
            self.line_edit_to_search_shouye = QLineEdit(sousuocipinlvda_shouye)
        else:
            self.line_edit_to_search_shouye = QLineEdit("8")
        self.line_edit_to_search_shouye.setFixedWidth(25)
        self.label_seconds_search_shouye = QLabel('内随机     ', self)

        self.label_from_search_shouye_pinglunjiangeshijian = QLabel('参与成功等待时间')

        sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao = get_value_by_key_pkl("shuju_config.pkl",
                                                                                  "sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao")
        if (sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao != None):
            self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao = QLineEdit(
                sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao)
        else:
            self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao = QLineEdit("yxl")
        self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao.setFixedWidth(130)

        self.label_to_search_shouye_pinglunjiangeshijian = QLabel('秒')
        self.label_to_search_shouye_pinglunjiangeshijian.setFixedWidth(15)

        sousuocipinlvxiao_shouye_pinglunjiangeshijian_da = get_value_by_key_pkl("shuju_config.pkl",
                                                                                "sousuocipinlvxiao_shouye_pinglunjiangeshijian_da")
        if (sousuocipinlvxiao_shouye_pinglunjiangeshijian_da != None):
            self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_da = QLineEdit(
                sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
        else:
            self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_da = QLineEdit("8")
        self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_da.setFixedWidth(25)
        self.label_seconds_search_shouye_pinglunjiangeshijian_da = QLabel('秒随机     ', self)

        self.h_layout_diwuhang.addWidget(self.label_from_search_shouye)
        self.h_layout_diwuhang.addWidget(self.line_edit_from_search_shouye)
        self.h_layout_diwuhang.addWidget(self.label_to_search_shouye)
        self.h_layout_diwuhang.addWidget(self.line_edit_to_search_shouye)
        self.h_layout_diwuhang.addWidget(self.label_seconds_search_shouye)

        self.h_layout_diwuhang.addWidget(self.label_from_search_shouye_pinglunjiangeshijian)
        self.h_layout_diwuhang.addWidget(self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao)
        self.h_layout_diwuhang.addWidget(self.label_to_search_shouye_pinglunjiangeshijian)
        # self.h_layout_diwuhang.addWidget(self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
        # self.h_layout_diwuhang.addWidget(self.label_seconds_search_shouye_pinglunjiangeshijian_da)
        self.h_layout_diwuhang.addStretch(1)

        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        central_widget.setFixedWidth(650)
        layout.setSpacing(0)  # 设置布局间距为0
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addLayout(self.select_phone_layout)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)

        layout.addWidget(self.caozuo_config)

        layout.addLayout(self.h_layout_dir)
        # layout.addLayout(self.h_layout_kongge)
        # layout.addLayout(self.h_layout_dir)
        # layout.addLayout(self.h_layout_kongge1)
        # layout.addLayout(self.h_layout_dir_comment)
        # layout.addLayout(self.h_layout_kongge2)
        # layout.addLayout(self.h_layout_dir_gouwu)
        # layout.addLayout(self.h_layout_kongge8)
        #layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge3)

        # layout.addLayout(self.h_layout)

        # layout.addLayout(self.h_layout_disanhang)
        # layout.addLayout(self.h_layout_kongge5)
        # layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.h_layout_guanzhu1)
        layout.addLayout(self.h_layout_kongge6)
        layout.addLayout(self.h_layout_fudai_guanjianzi)
        layout.addLayout(self.h_layout_kongge5)
        layout.addLayout(self.h_layout_diwuhang)
        layout.addLayout(self.h_layout_kongge4)

        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(30000)
        # self.refresh_pkl_files_test()
        # self.timer.timeout.connect(self.refresh_pkl_files_test)
        # self.timer.start(10000)

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.add_text)
        self.timer1.start(1300)

        # Initial load
        self.refresh_pkl_files()
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("执行")
        self.execute_button.resize(100, 30)

        self.button_gang.addWidget(self.execute_button)

        self.button_gang.addWidget(self.clear_task_config_button)
        self.execute_button_delete = QPushButton("退出直播间")
        self.execute_button_delete.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_delete)

        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_reset)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.file_button.clicked.connect(self.showDialog)
        self.file_button_comment.clicked.connect(self.showDialog_comment)
        self.file_button_gouwu.clicked.connect(self.showDialog_gouwu)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.execute_button_delete.clicked.connect(self.execute_delete_button_clicked)
        layout.addLayout(self.button_gang)
        # layout.addWidget(self.execute_button_reset)
    def confirm_phone_selection(self):
        input_text = self.select_phone_input.text().strip()
        if not input_text:
            return

        # 清空之前的选择
        self.selected_ids = []

        # 解析输入的序号
        selected_numbers = set()
        try:
            # 分割输入为各个部分
            parts = [p.strip() for p in input_text.replace(',', ' ').split()]

            for part in parts:
                if '-' in part:
                    # 处理范围格式 1-5
                    start, end = map(int, part.split('-'))
                    # 确保范围正确（小到大）
                    if start > end:
                        start, end = end, start
                    # 添加范围内所有数字
                    selected_numbers.update(range(start, end + 1))
                else:
                    # 处理单个数字
                    selected_numbers.add(int(part))
        except:
            # 输入格式错误时不做任何选择
            selected_numbers = set()
            print("输入格式错误")

        # 遍历表格中的所有行（行号从0开始，序号从1开始）
        for row in range(self.table_widget.rowCount()):
            # 当前行的序号（行号+1）
            current_number = row + 1  # 关键修改：用行号作为序号

            # 获取当前行的复选框
            checkbox = self.table_widget.cellWidget(row, 0)
            if not isinstance(checkbox, QCheckBox):
                continue

            # 获取当前行的手机ID（用于添加到selected_ids）
            item_id_text = self.table_widget.item(row, 1).text()

            # 检查是否需要选中
            is_selected = current_number in selected_numbers
            print("is_selected=",is_selected)

            # 更新复选框状态
            if(is_selected == True):
                checkbox.setChecked(is_selected)

            # 更新选中ID列表
            # if is_selected:
            #     self.selected_ids.append(item_id_text)

        print(f"最终选中的手机序号: {selected_numbers}")
        print(f"最终选中的手机ID: {self.selected_ids}")
        #self.selected_ids = []
        self.refresh_pkl_files()


    def on_item_changed(self, item: QTableWidgetItem):
        if self.table_widget.currentColumn() == 2:
            # 获取新的数据并打印（或保存到其他地方）
            new_data = item.text()
            # print(item.column())

            item.row()
            # print(self.table_widget.item(item.row(),1).text())
            phone_name = self.table_widget.item(item.row(), 1).text()
            # print(f"New data in row {item.column()}, column 2: {new_data}")
            # 你可以在这里添加保存数据的逻辑，比如保存到数据库或文件中
            updata_pkl_config("config.pkl", phone_name, new_data)
            # print(pkl_list("config.pkl"))

    def on_item_clicked(self):

        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}
        self.selected_ids = current_device_ids
        self.refresh_pkl_files()
        print(self.selected_ids)
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
        # print(pkl_list("config.pkl"))
        print("全选")

    def shell_neibu(self, cmd):
        os.system(cmd)

    def on_file_button_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            # If a folder is selected, update the QLabel
            self.file_textbox.setText(folder_path)
            updata_pkl_config_mianban("file_path", folder_path)
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
                # self.excel_file = selected_file
                # self.import_config()
                # self.refresh_pkl_files_test()

    def showDialog_comment(self):
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
                self.file_textbox_comment.setText(selected_file)
                updata_pkl_config_mianban("file_path_comment", selected_file)
                # self.excel_file = selected_file
                # self.import_config()
                # self.refresh_pkl_files_test()

    def showDialog_gouwu(self):
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
                self.file_textbox_gouwu.setText(selected_file)
                updata_pkl_config_mianban("file_path_gouwu", selected_file)
                # self.excel_file = selected_file
                # self.import_config()
                # self.refresh_pkl_files_test()

    def showDialog_comment_douyin_phone_file(self):
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
                self.file_textbox_douyin.setText(selected_file)
                updata_pkl_config_mianban("file_path_douyin", selected_file)
                # self.excel_file = selected_file
                # self.import_config()
                # self.refresh_pkl_files_test()

    def showDialog_comment_nick(self):
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
                self.file_textbox_comment_douyin.setText(selected_file)
                updata_pkl_config_mianban("file_path_comment_douyin", selected_file)
                # self.excel_file = selected_file
                # self.import_config()
                # self.refresh_pkl_files_test()

    def import_config(self):
        #print("")
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
                    #print(line, end='')  # 使用 end='' 是为了避免打印每行末尾的额外换行符
                    if ((str(line).count("_") > 0) and (str(line).count("/") > 0)):
                        file_name = str(line).split("/")[-2]
                        new_data = {"url": str(line).split("_")[0], "BIG_COUNT": int(str(line).split("_")[1]),
                                    "TONGJI": 0}
                        #print("newdata=", new_data)
                        file_name = path_dir + "/" + file_name + ".pkl"
                        #print("file_name=", file_name)
                        self.judge_pkl_creat(file_name, new_data)
        # 注意：使用 with 语句后，不需要手动关闭文件，它会在块结束时自动关闭

    def get_random_pkl_file_in_directory(self, directory):
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

    def judge_pkl_creat(self, pkl_file, new_data):
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

    def updata_pkl_config_video(self, pklfile, key, value):
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
        current_zhubo = self.combo_boxrrr.currentText()
        fudai_peizhi = str(self.fudai.text())
        print(fudai_peizhi)
        if(len(fudai_peizhi)>1):
            fudai_list = fudai_peizhi.split("/")
            print(current_zhubo)
            print(int(current_zhubo))
            print(fudai_list)
            if(int(current_zhubo) >= len(fudai_list)):
                current_zhubo = len(fudai_list)
        print("current_zhubo=",current_zhubo)

        curr_zhubo_nicheng = fudai_list[int(current_zhubo)-1]
        print("curr_zhubo_nicheng=",curr_zhubo_nicheng)


        result_j = judge()
        if (result_j == False):
            print("当前需要联系")
            self.titleLabel.setText("*" * 55 + "当前需要联系作者" + "*" * 55)
            self.titleLabel.setStyleSheet("color: red;")
            #return
        # print("---------------")

        updata_pkl_config_mianban("jiaobenyunxingshichang", self.run_time.text())
        updata_pkl_config_mianban("sousuocipinlvxiao", self.line_edit_from_search.text())
        updata_pkl_config_mianban("sousuocipinlvda", self.line_edit_to_search.text())
        updata_pkl_config_mianban("huadongjiangexiao", self.line_edit_from.text())
        updata_pkl_config_mianban("huadongjiangeda", self.line_edit_to.text())
        updata_pkl_config_mianban("huadongcishuxiao", self.jiarenshurukuang.text())
        updata_pkl_config_mianban("huadongcishuda", self.huadongcishu_big.text())
        updata_pkl_config_mianban("shoucanggailv", self.shoucang_gailv.text())
        updata_pkl_config_mianban("guanzhugailv", self.shoucang_guanzhu.text())
        updata_pkl_config_mianban("dianzangailv", self.shoucang_dianzan.text())
        updata_pkl_config_mianban("pinglungailv", self.shoucang_pinglun.text())
        updata_pkl_config_mianban("guanzhuzhanghao", self.guanzhuzhanghao.text())
        updata_pkl_config_mianban("fudai", self.fudai.text())
        updata_pkl_config_mianban("fudai_guanjianzi", self.fudai_guanjianzi.text())
        updata_pkl_config_mianban("fudai_guanjianzi_dengdaishijian", self.fudai_guanjianzi_dengdaishijian.text())
        updata_pkl_config_mianban("sousuocipinlvxiao_shouye", self.line_edit_from_search_shouye.text())
        updata_pkl_config_mianban("sousuocipinlvda_shouye", self.line_edit_to_search_shouye.text())

        updata_pkl_config_mianban("sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao",
                                  self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao.text())
        updata_pkl_config_mianban("sousuocipinlvxiao_shouye_pinglunjiangeshijian_da",
                                  self.sousuocipinlvxiao_shouye_pinglunjiangeshijian_da.text())

        if (self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            # print(temp)
            updata_pkl("./shuju/" + temp + ".pkl", "执行状态", "运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "福袋")
        # self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        # self.scroll_area.ensureWidgetVisible(100)
        # if(self.radio_button1.isChecked() == True):
        #     tasks.append("yanghao")
        # if (self.radio_button2.isChecked() == True):
        #     tasks.append("gouwu")
        # if(self.radio_button4.isChecked() == True):
        #     tasks.append("guanzhu")
        if (self.radio_button6.isChecked() == True):
            tasks.append("fudai")
        #     print("开启福袋。。。")
        # if (self.radio_button3.isChecked() == True):
        #     tasks.append("pinglun")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")
        global global_zong, global_time
        global_zong = int(self.guanzhuzhanghao.text())
        global_time = int(self.run_time.text())
        thread = threading.Thread(target=self.thread_temp, args=(tasks,curr_zhubo_nicheng))
        # thread111 = threading.Thread(target=update_global_var, args=(global_time,global_zong))
        thread.start()
        # thread111.start()

    def thread_temp(self, tasks,curr_zhubo_nicheng):
        print("self.selected_ids--->",self.selected_ids)
        for serial in self.selected_ids:
            #print("---------------->", get_value_by_key_pkl("config.pkl", serial))
            class_phone = get_value_by_key_pkl("config.pkl", serial)
            thread = threading.Thread(target=operate_device, args=(
            serial, class_phone, self.file_textbox.text(), self.file_textbox_comment.text(), tasks,
            self.run_time.text(), self.line_edit_from_search.text(), self.line_edit_to_search.text(),
            self.line_edit_from.text(), self.line_edit_to.text(), self.jiarenshurukuang.text(),
            self.shoucang_gailv.text(), self.shoucang_pinglun.text(), self.shoucang_dianzan.text(),
            self.shoucang_guanzhu.text(), self.huadongcishu_big.text(), self.file_textbox_gouwu.text(),
            self.radio_button3.isChecked(), self.guanzhuzhanghao.text(), curr_zhubo_nicheng,
            self.fudai_guanjianzi.text(), self.combo_box.currentText(), self.line_edit_from_search_shouye.text(),
            self.line_edit_to_search_shouye.text()))
            # 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
            # threads.append(thread)
            thread.start()
            time.sleep(random.randint(3, 20))

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
        # if(os.path.isdir("./task_config")):
        #     shutil.rmtree("./task_config")
        #     self.refresh_pkl_files_test()
        if (self.clear_task_config_button.text() == "暂停执行"):

            if not os.path.exists("pause.txt"):
                # 如果文件不存在，则创建文件
                with open("pause.txt", 'w') as file:
                    pass  # 这里不需要写入任何内容，只需要创建文件即可

            self.clear_task_config_button.setText("开始执行")
        else:
            if os.path.exists("pause.txt"):
                os.remove("pause.txt")
            self.clear_task_config_button.setText("暂停执行")

    def execute_delete_button_clicked(self):
        # print("---------------")
        # if(self.selected_ids == []):
        #     toast("请选择删除的机型")
        #     return
        # for temp in self.selected_ids:
        #     #print(temp)
        #     if(os.path.isfile("./shuju/" + temp + ".pkl")):
        #         os.remove("./shuju/" + temp + ".pkl")
        # self.refresh_pkl_files()
        # self.selected_ids = []

        if (self.execute_button_delete.text() == "退出直播间"):
            if not os.path.exists("exit.txt"):
                # 如果文件不存在，则创建文件
                with open("exit.txt", 'w') as file:
                    pass  # 这里不需要写入任何内容，只需要创建文件即可
            self.execute_button_delete.setText("停止退出")
        else:
            if os.path.exists("exit.txt"):
                os.remove("exit.txt")
            self.execute_button_delete.setText("退出直播间")

    def execute_reset_button_clicked(self):
        # print("execute_reset_button_clicked")
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
        print("current_pos=", current_pos)

        # print("current_scroll_position",current_scroll_position)
        # 清除旧数据
        # self.task_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './task_config'
        row_index = 0
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                #print("filename---", filename)
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'rb') as file:
                        data = pickle.load(file)
                        #print("data=", data)
                        #print("row_index=", row_index)

                        # 假设数据是一个字典
                        if isinstance(data, dict):
                            #print("进来了")
                            #print("-----", data.get('url', 'N/A'))

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

            # print("current_scroll_position",current_scroll_position)
            # 清除旧数据
            self.task_widget.setRowCount(0)
            # 遍历目录中的所有文件
            directory = './task_config'
            create_directory_if_not_exists(directory)
            row_index = 0

            # print("sorted_data=",sorted_data)

            for file_name in os.listdir(directory):
                task_name = file_name
                # print("device_id---->",device_id)
                file_name = directory + "/" + str(file_name)
                # print("file_name---",file_name)
                if (os.path.isfile(file_name)):
                    try:
                        with open(file_name, 'rb') as file:
                            data = pickle.load(file)
                            # print("data-----------,",data)

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

                                self.task_widget.setItem(row_index, 2,
                                                         QTableWidgetItem(str(data.get('BIG_COUNT', 'N/A'))))
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
                                # self.task_widget.setItem(row_index, 4, QTableWidgetItem(data.get('TONGJI', 'N/A')))

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

        # print("current_scroll_position",current_scroll_position)
        # 清除旧数据
        self.table_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './shuju'
        row_index = 0

        sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))
        # print("sorted_data=",sorted_data)

        for device_id, v in sorted_data.items():
            # print("device_id---->",device_id)
            file_name = directory + "/" + str(device_id) + ".pkl"
            # print("file_name---",file_name)
            if (os.path.isfile(file_name)):
                try:
                    with open(file_name, 'rb') as file:
                        data = pickle.load(file)

                        # print("data-----------,",data)

                        # 假设数据是一个字典
                        if isinstance(data, dict):
                            # 插入新行
                            self.table_widget.insertRow(row_index)
                            # 添加复选框
                            checkbox = QCheckBox(self)
                            # print("self.selected_ids=",self.selected_ids)
                            # print("os.path.splitext(file_name)[0]",os.path.splitext(file_name)[0].split("/")[2])
                            if os.path.splitext(file_name)[0].split("/")[2] in self.selected_ids:
                                checkbox.setChecked(True)
                            if (data.get('执行状态', 'N/A') == "运行中"):
                                checkbox.setEnabled(False)
                            else:
                                checkbox.setEnabled(True)
                            # if (data.get('连接状态', 'N/A') == "中断连接"):
                            #     checkbox.setEnabled(True)
                            # else:
                            #     checkbox.setEnabled(True)
                            checkbox.stateChanged.connect(
                                lambda state, row=row_index: self.update_selected_ids(state, row))
                            self.table_widget.setCellWidget(row_index, 0, checkbox)
                            # 设置文件名（去除后缀）
                            self.table_widget.setItem(row_index, 1, QTableWidgetItem(device_id))
                            # 设置其他数据
                            #print(data.get('name', 'N/A'))
                            phone_name = get_value_by_key_pkl("config.pkl", data.get('name', 'N/A'))
                            # print("phone_name---------->",phone_name)
                            if (phone_name != None):
                                item_i = QTableWidgetItem(phone_name)
                            else:
                                item_i = QTableWidgetItem(data.get('nick_name', 'N/A'))
                            # item_i.setForeground(QBrush(QColor(255,0,0)))

                            self.table_widget.setItem(row_index, 2, item_i)
                            if (data.get('连接状态', 'N/A') == "中断连接"):
                                item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                item_lianjie.setForeground(QBrush(QColor(255, 0, 0)))
                            else:
                                item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
                                item_lianjie.setForeground(QBrush(QColor(0, 0, 0)))
                            item_lianjie.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 3, item_lianjie)

                            # item_i = QTableWidgetItem(data.get('执行状态', 'N/A'))
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
                            self.table_widget.setItem(row_index, 6, button111)

                            row_index += 1
                except Exception as e:
                    print(f"读取文件 {file_name} 时出错: {e}")
        # 恢复滚动位置
        self.table_widget.verticalScrollBar().setSliderPosition(current_pos)

    def update_selected_ids(self, state, row):
        # 更新选中的编号
        item_id = self.table_widget.item(row, 1).text()  # 获取编号
        # print("item_id=",item_id)
        if item_id not in self.selected_ids:
            self.selected_ids.append(item_id)  # 添加到选中的编号
        else:
            if item_id in self.selected_ids:
                self.selected_ids.remove(item_id)  # 从选中的编号中移除
        # 打印当前选中的编号
        # print("当前选中的编号:", self.selected_ids)


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


def pkl_add_log(pkl, phone, values):
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
        pickle.dump({time: phone + "--->" + values}, pkl_file)


def pkl_add(pkl, dic):
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


# import pickle
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
            if (not os.path.exists(pklfile)):
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
        data = {}
        with open(pklfile, 'wb') as file:
            pickle.dump(data, file)


# import pickle

# 修改Python对象
# my_object['age'] = 31

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


def updata_pkl_config(pklfile, key, value):
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


def updata_pkl(pklfile, key, value):
    # dic = {}
    if (os.path.isfile(pklfile)):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)
        dic[key] = value
        # print("----------------------------------",dic)
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)


import subprocess
import time


def get_connected_devices():
    # Run the adb devices command
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)
    # print("连接的设备有。。。",devices)
    connected_devices = []
    for device in devices:
        if device.strip():
            device_info = device.split('\t')
            connected_devices.append((device_info[0], device_info[1]))  # (device_id, status)

    return connected_devices


def updata_pkl_config_mianban(key, value):
    pklfile = "shuju_config.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"file_path": "请输入文件夹路径"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    dic[key] = value
    with open(pklfile, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)


def monitor_devices():
    known_devices = set()
    create_directory_if_not_exists("shuju")
    delete_directory_contents("shuju")
    # if(os.path.exists("config.pkl")):
    #     print()

    while True:
        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}

        # Check for new connections
        new_devices = current_device_ids - known_devices
        for device_id in new_devices:
            # print(f"Device connected: {device_id}")
            dic = {"name": device_id, "连接状态": "已连接", "执行状态": "空闲中", "age": "1811", "add": "bj1",
                   "xingbie": "nan", "进行的任务": "空闲", "nick_name": "昵称点击可编辑", "tongji": "0"}
            pkl_add("./shuju/" + device_id + ".pkl", dic)
            if (device_id not in dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))):
                updata_pkl_config("config.pkl", device_id, "昵称点击可编辑")
        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
            # print(f"Device disconnected: {device_id}")
            updata_pkl("./shuju/" + device_id + ".pkl", "连接状态", "中断连接")
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
            dic[key] = str(int(dic[key]) + 1)
            # print("----------------------------------", dic)
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)
        else:
            print(f"Key '{key}' not found in the pickle file.")
    else:
        print(f"The file '{pklfile}' does not exist.")

    # 示例用法


def clear_folder(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹不存在：{folder_path}")
        return

    # 遍历文件夹内所有内容
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            # 如果是文件，直接删除
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"已删除文件：{item_path}")
            # 如果是文件夹，递归删除（包括子文件和子文件夹）
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"已删除文件夹及内容：{item_path}")
        except Exception as e:
            print(f"删除 {item_path} 失败：{e}")


# pklfile = 'example.pkl'  # 替换为您的 .pkl 文件路径
# key_to_update = 'some_key'  # 替换为您要更新的键
# update_pkl(pklfile, key_to_update)
# 定义全局变量
ocr = OCRProcessor()

if __name__ == "__main__":
    thread111 = threading.Thread(target=clear_folder, args=(create_folder_on_current_disk(),))
    thread111.start()
    if os.path.exists("pause.txt"):
        os.remove("pause.txt")
    if os.path.exists("exit.txt"):
        os.remove("exit.txt")
    thread = threading.Thread(target=monitor_devices)
    thread.start()

    # 创建并启动线程
    # update_thread = threading.Thread(target=update_global_var)
    # update_thread.daemon = True  # 设置为守护线程，确保主程序结束时线程也结束
    # update_thread.start()

    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())

    # sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))

    # print(sorted_data)

    # d = u2.connect("Q5S0219527003267")
    # tongji(d,"Q5S0219527003267",r"C:\Users\Administrator\Desktop\config")