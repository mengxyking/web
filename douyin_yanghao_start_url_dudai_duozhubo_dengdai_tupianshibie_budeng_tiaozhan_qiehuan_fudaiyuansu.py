import base64
import cv2
import hashlib
import re
import shutil
import sys
import threading
import random
import traceback
import uuid
from datetime import datetime

import numpy as np
import requests
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
#from RapidOCR_json.api.python.demo3 import OCRProcessor
from paddleOCR_json_duixiang_0308 import OCRProcessor
ocr1 = OCRProcessor(id=1)
ocr2 = OCRProcessor(id=2)
# ocr3 = OCRProcessor(id=3)
# ocr4 = OCRProcessor(id=4)
# ocr5 = OCRProcessor(id=5)
# 2. 创建全局锁（保证轮询时的线程安全）
ocr_lock = threading.Lock()
#print(ocr)
current_scroll_position = 0
import time

# 抖音养号+微信加好友脚本
black_zhubo = []
alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()

from typing import Tuple, Optional

# 1. 全局文件读取锁（保护多线程并发读取文件，避免系统句柄竞争）
file_read_lock = threading.Lock()

def get_available_ocr():
    """获取空闲的OCR对象，没有则等待（轮询ocr1→ocr2）"""
    while True:
        with ocr_lock:
            # 先查ocr1，空闲则返回
            if not ocr1.busy:
                return ocr1
            # 再查ocr2，空闲则返回
            if not ocr2.busy:
                return ocr2
            # if not ocr3.busy:
            #     return ocr3
            # if not ocr4.busy:
            #     return ocr4
            # if not ocr5.busy:
            #     return ocr5
        # 都忙则等待50ms再查，避免CPU空转
        time.sleep(0.05)

def find_id_from_area_2(d, x1_1,x2_2, y1_1 ,y2_2):
    xml = d.dump_hierarchy()
    tree = etree.fromstring(xml.encode('utf-8'))

    # 目标坐标范围：判断控件是否包含该坐标
    #target_point = (x1, y1)  # 你需要检查的点

    # 存储符合条件的控件信息 (面积, 控件, 中心坐标)
    candidates = []
    zuobiaodian = []
    elements = tree.xpath('//node')
    for elem in elements:
        bounds_str = elem.get('bounds', '')
        resource_id = elem.get('resource-id', '')
        text = elem.get('text', '')
        contentdesc = elem.get('content-desc', '')
        if not bounds_str:
            continue

        # 解析bounds坐标 [x1,y1][x2,y2]
        coords = re.findall(r'\[(\d+),(\d+)]\[(\d+),(\d+)]', bounds_str)
        if not coords:
            continue

        x1, y1, x2, y2 = map(int, coords[0])
        #print(x1, y1, x2, y2)

        if(x1_1 < x1 and x2 < x2_2 and y1_1 < y1 and y2 < y2_2 and y2 - y1 == x2 - x1 and x1 != 0 and y1 != 0 and resource_id == "" and text == "" and contentdesc == ""):
            # print("------------------------------------------------------")
            # print(x1, y1, x2, y2)
            # print(resource_id,text,contentdesc)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # print(center_x,center_y)

            zuobiaodian.append((center_x,center_y))
    zuobiaodian = list(set(zuobiaodian))
    # print("zuobiaodian=",zuobiaodian)
    zuobiaodian1 = zuobiaodian
    for elem in elements:

        bounds_str = elem.get('bounds', '')

        if not bounds_str:
            continue

        # 解析bounds坐标 [x1,y1][x2,y2]
        coords = re.findall(r'\[(\d+),(\d+)]\[(\d+),(\d+)]', bounds_str)
        if not coords:
            continue

        x1, y1, x2, y2 = map(int, coords[0])
        #print("x1, y1, x2, y2",x1, y1, x2, y2)
        for iii in zuobiaodian:
           if(x1 != 0 and y1 != 0 and x1 < iii[0] < x2 and y1 < iii[1] < y2):
                print("x1, y1, x2, y2",x1, y1, x2, y2)
                resource_id = elem.get('resource-id', '')
                text = elem.get('text', '')
                contentdesc = elem.get('content-desc', '')
                # print(resource_id, text, contentdesc)
                if( text != "" or contentdesc != ""):
                    print(f"应该去掉,{iii}，text={text}，contentdesc={contentdesc}")
                    if(iii in zuobiaodian1):
                        zuobiaodian1.remove(iii)
    print("-----------")
    print(zuobiaodian1)
    return zuobiaodian1
import json
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding

AES_KEY = b'OnlineStats_2026'
def encrypt_payload(data: dict) -> str:
    iv = os.urandom(16)
    plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
    padder = crypto_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def heartbeat(product_key, computer_code, phone_codes):
    try:
        payload = encrypt_payload({
            "product_key": product_key,
            "computer_code": computer_code,
            "phone_codes": phone_codes,  # 列表，支持批量
        })
        resp = requests.post(
            "http://123.57.93.159:5003/api/v1/heartbeat",
            json={"payload": payload},
            timeout=10
        )
        return resp.json()
    except BaseException as e:
        print(e)




def init_serial_logger(serial):
    """初始化serial对应的日志文件，确保文件存在"""
    # 日志文件路径：当前目录下 serial.log.txt
    log_dir = "./serial_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"{serial}.log.txt")
    # 新建文件（若不存在）
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"===== {serial} 日志开始 =====")
    return log_file

def write_serial_log(serial, *args):
    """
    写入日志到serial对应的txt文件，同时打印到控制台
    :param serial: 第一个参数，用于标识日志文件
    :param args: 后面任意多个参数，会自动拼接成日志内容
    """
    try:
        log_file = init_serial_logger(serial)
        # 拼接所有后续参数为内容
        content = " ".join(str(arg) for arg in args)
        # 日志时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_content = f"[{timestamp}] {content}\n"
        # 打印到控制台
        print(log_content.strip())
        # 写入文件（追加模式，加锁保证线程安全）
        with file_lock:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_content)
    except Exception as e:
        print(f"日志写入失败：{e}")

# def safe_load_image(image_path: str) -> Optional[np.ndarray]:
#     """
#     线程安全的图片加载函数（适配不同大图、兼容中文路径）
#     :param image_path: 任意图片路径（支持中文）
#     :return: 图片数组（BGR格式），失败返回None
#     """
#     # 加锁读取文件（即使不同文件，也避免同时打开过多句柄）
#     with file_read_lock:
#         try:
#             # 解决cv2.imread无法读取中文路径的问题
#             img_data = np.fromfile(image_path, dtype=np.uint8)
#             if img_data.size == 0:
#                 raise ValueError("文件为空或无法读取")
#
#             # 解码图片（IMREAD_COLOR：读取彩色图，忽略透明通道）
#             img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
#             if img is None:
#                 raise ValueError("图片解码失败（格式错误/损坏）")
#             return img
#         except Exception as e:
#             print(f"❌ 加载图片失败 {image_path}：{str(e)}")
#             return None
#
#
# def find_target_by_template(
#         big_image_path: str,  # 待搜索的大图路径（每个线程可能不同）
#         template_image_path: str,  # 目标模板小图路径
#         threshold: float = 0.7  # 匹配阈值（0-1，越高越精准）
# ) -> tuple | None:
#     """
#     适配「多线程读取不同大图」的模板匹配函数（线程安全）
#     解决"无法读取大图"的核心问题
#     """
#     # 1. 线程安全加载图片（替代原cv2.imread）
#     time.sleep(0.2)
#     big_img = safe_load_image(big_image_path)
#     template_img = safe_load_image(template_image_path)
#
#     # 校验图片加载结果
#     if big_img is None:
#         raise ValueError(f"无法读取大图：{big_image_path}，请检查路径/文件完整性")
#     if template_img is None:
#         raise ValueError(f"无法读取模板图：{template_image_path}，请检查路径/文件完整性")
#
#     # 2. 获取模板图宽高
#     template_h, template_w = template_img.shape[:2]
#
#     # 3. 执行模板匹配（纯内存操作，线程安全）y
#     result = cv2.matchTemplate(big_img, template_img, cv2.TM_CCOEFF_NORMED)
#     locations = np.where(result >= threshold)
#     for iii in locations:
#         print(f"------->{iii}")
#
#     # 4. 返回第一个匹配点的中心点坐标
#     if len(locations[0]) > 0:
#         top_left_y, top_left_x = locations[0][0], locations[1][0]
#         center_x = top_left_x + template_w // 2
#         center_y = top_left_y + template_h // 2
#         return (center_x, center_y)
#     else:
#         return None

def safe_load_image(image_path: str) -> Optional[np.ndarray]:
    """
    线程安全的图片加载函数（适配不同大图、兼容中文路径）
    :param image_path: 任意图片路径（支持中文）
    :return: 图片数组（BGR格式），失败返回None
    """
    # 加锁读取文件（即使不同文件，也避免同时打开过多句柄）
    with file_read_lock:
        try:
            # 解决cv2.imread无法读取中文路径的问题
            img_data = np.fromfile(image_path, dtype=np.uint8)
            if img_data.size == 0:
                raise ValueError("文件为空或无法读取")

            # 解码图片（IMREAD_COLOR：读取彩色图，忽略透明通道）
            img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("图片解码失败（格式错误/损坏）")
            return img
        except Exception as e:
            print(f"❌ 加载图片失败 {image_path}：{str(e)}")
            return None


def find_target_by_template(
        big_image_path: str,  # 待搜索的大图路径（每个线程可能不同）
        template_image_path: str,  # 目标模板小图路径
        threshold: float = 0.85,  # 匹配阈值（0-1，越高越精准）
        save_marked_image: bool = True,  # 是否保存标记后的图片
        show_image: bool = False  # 是否显示标记后的图片
) -> tuple | None:
    """
    适配「多线程读取不同大图」的模板匹配函数（线程安全）
    功能：1. 在匹配位置绘制红色方块标记 2. 返回匹配值最高的目标位置
    """
    # 1. 线程安全加载图片（替代原cv2.imread）
    time.sleep(0.2)
    big_img = safe_load_image(big_image_path)
    template_img = safe_load_image(template_image_path)

    # 校验图片加载结果
    if big_img is None:
        raise ValueError(f"无法读取大图：{big_image_path}，请检查路径/文件完整性")
    if template_img is None:
        raise ValueError(f"无法读取模板图：{template_image_path}，请检查路径/文件完整性")

    # 2. 获取模板图宽高
    template_h, template_w = template_img.shape[:2]

    # 3. 执行模板匹配（纯内存操作，线程安全）
    result = cv2.matchTemplate(big_img, template_img, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    # 创建大图的副本用于绘制标记，避免修改原图
    marked_img = big_img.copy()

    # 4. 遍历所有匹配点，记录坐标和匹配值
    match_info = []
    if len(locations[0]) > 0:
        # 遍历所有匹配位置，记录坐标和对应的匹配值
        for y, x in zip(locations[0], locations[1]):
            match_value = result[y, x]  # 获取该位置的匹配值
            center_x = x + template_w // 2
            center_y = y + template_h // 2

            if(10 < center_x < 800 and 200 < center_y < 600):

                match_info.append({
                    "x": x,
                    "y": y,
                    "center_x": center_x,
                    "center_y": center_y,
                    "match_value": match_value
                })
            # 绘制所有匹配位置的红色方块
            cv2.rectangle(
                marked_img,
                (x, y),  # 左上角
                (x + template_w, y + template_h),  # 右下角
                (0, 0, 255),  # 红色
                2  # 线条宽度
            )
            print(f"匹配位置：中心坐标({center_x}, {center_y})，匹配值：{match_value:.4f}")

        # 5. 找到匹配值最高的那个目标
        best_match = max(match_info, key=lambda item: item["match_value"])
        # 为最佳匹配位置绘制更粗的绿色方块，突出显示
        cv2.rectangle(
            marked_img,
            (best_match["x"], best_match["y"]),
            (best_match["x"] + template_w, best_match["y"] + template_h),
            (0, 255, 0),  # 绿色
            4  # 更粗的线条，突出最佳匹配
        )
        print(f"\n🏆 最佳匹配位置：中心坐标({best_match['center_x']}, {best_match['center_y']})，匹配值：{best_match['match_value']:.4f}")

        # 6. 保存标记后的图片
        # if save_marked_image:
        #     try:
        #         # 构造保存路径（在原图路径后添加"_marked_模板文件名"）
        #         template_name = os.path.basename(template_image_path).rsplit('.', 1)[0]
        #         save_path = big_image_path.rsplit('.', 1)[0] + f"_marked_{template_name}.png"
        #         # 解决中文路径保存问题
        #         cv2.imencode('.png', marked_img)[1].tofile(save_path)
        #         print(f"✅ 标记后的图片已保存至：{save_path}")
        #     except Exception as e:
        #         print(f"❌ 保存标记图片失败：{str(e)}")
        #
        # # 7. 显示标记后的图片（可选）
        # if show_image:
        #     cv2.namedWindow("Matched Image", cv2.WINDOW_NORMAL)
        #     cv2.imshow("Matched Image", marked_img)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()

        # 返回最佳匹配坐标
        return (best_match["center_x"], best_match["center_y"])
    else:
        print(f"❌ 模板 {os.path.basename(template_image_path)} 未匹配到任何目标")
        return None


def find_target_in_template_folder(
        big_image_path: str,
        template_folder_path: str,
        threshold: float = 0.85,
        save_marked_image: bool = True,
        show_image: bool = False
) -> tuple | None:
    """
    遍历指定文件夹内所有图片模板，依次匹配大图，找到第一个匹配成功的模板并返回坐标
    :param big_image_path: 大图路径
    :param template_folder_path: 模板小图所在文件夹路径
    :param threshold: 匹配阈值
    :param save_marked_image: 是否保存标记图
    :param show_image: 是否显示标记图
    :return: 第一个匹配成功的坐标，全部失败返回None
    """
    # 1. 校验模板文件夹是否存在
    if not os.path.exists(template_folder_path):
        print(f"❌ 模板文件夹不存在：{template_folder_path}")
        return None

    # 2. 获取文件夹内所有图片文件（支持常见图片格式）
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    template_files = []
    for file in os.listdir(template_folder_path):
        # 过滤非图片文件，忽略大小写
        if file.lower().endswith(image_extensions):
            template_files.append(os.path.join(template_folder_path, file))

    if not template_files:
        print(f"❌ 模板文件夹 {template_folder_path} 内未找到任何图片文件")
        return None

    print(f"\n📁 找到 {len(template_files)} 个模板文件，开始依次匹配...")
    print("template_files=",template_files)
    # 3. 遍历所有模板文件，依次匹配
    for idx, template_path in enumerate(template_files, 1):
        print(f"\n========== 正在匹配第 {idx}/{len(template_files)} 个模板：{os.path.basename(template_path)} ==========")
        try:
            # 执行匹配
            match_result = find_target_by_template(
                big_image_path=big_image_path,
                template_image_path=template_path,
                threshold=threshold,
                save_marked_image=save_marked_image,
                show_image=show_image
            )
            # 如果匹配成功，立即返回坐标
            if match_result is not None:
                print(f"\n✅ 匹配成功！使用模板：{os.path.basename(template_path)}，坐标：{match_result}")
                return match_result
        except Exception as e:
            print(f"❌ 匹配模板 {os.path.basename(template_path)} 时出错：{str(e)}")
            continue

    # 4. 所有模板都匹配失败
    print(f"\n❌ 所有 {len(template_files)} 个模板均未匹配到目标")
    return None


# def safe_load_image(image_path: str, retry_times: int = 3, retry_delay: float = 0.1) -> Optional[np.ndarray]:
#     """
#     线程安全的图片加载函数（适配大图、兼容中文路径、重试机制解决PNG读取不完整）
#     :param image_path: 任意图片路径（支持中文）
#     :param retry_times: 读取失败重试次数
#     :param retry_delay: 重试间隔（秒）
#     :return: 图片数组（BGR格式），失败返回None
#     """
#     # 加锁读取文件（避免多线程同时读取文件句柄）
#     with file_read_lock:
#         for attempt in range(retry_times):
#             try:
#                 # 1. 读取文件字节（完整读取，避免部分读取）
#                 with open(image_path, 'rb') as f:
#                     img_data = f.read()  # 一次性读取全部字节，替代np.fromfile
#                 if not img_data:
#                     raise ValueError("File is empty or unreadable")
#
#                 # 2. 转换为numpy数组
#                 img_np = np.frombuffer(img_data, dtype=np.uint8)
#                 if img_np.size == 0:
#                     raise ValueError("Image data is empty after conversion")
#
#                 # 3. 解码图片（IMREAD_COLOR：读取彩色图，忽略透明通道）
#                 img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
#                 if img is None:
#                     raise ValueError("Image decoding failed (wrong format/corrupted)")
#
#                 return img
#             except Exception as e:
#                 # 最后一次重试失败才打印报错
#                 if attempt == retry_times - 1:
#                     print(f"❌ Failed to load image {image_path} (after {retry_times} retries): {str(e)}")
#                     return None
#                 # 非最后一次，重试前等待
#                 time.sleep(retry_delay)
#     return None
#
#
# def find_target_by_template(
#         big_image_path: str,  # 待搜索的大图路径（每个线程可能不同）
#         template_image_path: str,  # 目标模板小图路径
#         threshold: float = 0.7  # 匹配阈值（0-1，越高越精准）
# ) -> Tuple[int, int] | None:
#     """
#     适配「多线程读取不同大图」的模板匹配函数（线程安全）
#     解决"无法读取大图"和PNG缓冲区不完整问题
#     """
#     # 1. 线程安全加载图片（带重试机制，替代原cv2.imread）
#     big_img = safe_load_image(big_image_path)
#     template_img = safe_load_image(template_image_path)
#
#     # 校验图片加载结果
#     if big_img is None:
#         raise ValueError(f"Cannot read big image: {big_image_path}, check path/file integrity")
#     if template_img is None:
#         raise ValueError(f"Cannot read template image: {template_image_path}, check path/file integrity")
#
#     # 2. 获取模板图宽高
#     template_h, template_w = template_img.shape[:2]
#
#     # 3. 执行模板匹配（纯内存操作，线程安全）
#     result = cv2.matchTemplate(big_img, template_img, cv2.TM_CCOEFF_NORMED)
#     locations = np.where(result >= threshold)
#
#     print("locations=====list====",locations)
#
#     # 4. 返回第一个匹配点的中心点坐标
#     if len(locations[0]) > 0:
#         top_left_y, top_left_x = locations[0][0], locations[1][0]
#         center_x = top_left_x + template_w // 2
#         center_y = top_left_y + template_h // 2
#         return (center_x, center_y)
#     else:
#         return None


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
        random_int = random.randint(0,10000)
        timestamp = time.strftime("%Y%m%d%H%M%S")
        save_path = os.path.join(SAVE_DIR, f"{timestamp}_{str(random_int)}.png")
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


# def get_real_device_idevice_id():
#     """获取更真实的设备唯一标识，并返回缩短后的版本"""
#     try:
#         # 收集各种硬件和系统信息
#         info = [
#             platform.node(),  # 计算机名
#             platform.machine(),  # 机器类型
#             platform.processor(),  # 处理器信息
#             platform.system(),  # 操作系统名称
#             platform.release(),  # 操作系统版本
#             str(os.environ.get('COMPUTERNAME', '')),  # Windows计算机名
#             str(os.environ.get('USERNAME', '')),  # 用户名
#         ]
#
#         # 创建哈希作为设备ID
#         hash_obj = hashlib.sha256()
#         hash_obj.update(''.join(info).encode('utf-8'))
#         full_hash = hash_obj.hexdigest()
#
#         # 返回缩短后的唯一码（例如前8个字符）
#         return full_hash[:18]  # 取前8个字符作为缩短的唯一码
#     except Exception as e:
#         return f"ERR-{str(e)[:18]}"  # 错误情况下也返回缩短的字符串

def get_real_device_id():
    """获取更真实的设备唯一标识，增强唯一性，降低重合概率"""
    try:
        info = []

        # ==================== 原有基础信息（保留） ====================
        info.append(platform.node())               # 计算机名
        info.append(platform.machine())            # 机器架构
        info.append(platform.processor())          # 处理器
        info.append(platform.system())             # 系统
        info.append(platform.release())            # 系统版本
        info.append(os.environ.get('COMPUTERNAME', ''))
        info.append(os.environ.get('USERNAME', ''))

        # ==================== 新增高唯一性信息（核心增强） ====================
        # 1. 系统 UUID（最稳定唯一）
        try:
            info.append(str(uuid.getnode()))       # MAC 地址哈希值（最常用）
        except:
            info.append("no-mac")

        # 2. Windows 机器 GUID（系统级唯一，几乎不重复）
        try:
            if platform.system() == "Windows":
                info.append(os.environ.get('SYSTEMGUID', ''))
                info.append(os.environ.get('PROCESSOR_IDENTIFIER', ''))
                info.append(os.environ.get('NUMBER_OF_PROCESSORS', ''))
        except:
            pass

        # 3. 系统目录 + 启动信息（进一步区分）
        try:
            info.append(os.environ.get('SYSTEMROOT', ''))
            info.append(os.path.expanduser('~'))    # 用户目录
        except:
            pass

        # 4. 内存/CPU 硬件信息（区分不同配置机器）
        try:
            if platform.system() == "Windows":
                info.append(str(platform.win32_ver()))
        except:
            pass

        # 过滤空值，避免干扰
        info = [str(i).strip() for i in info if str(i).strip()]

        # 生成强唯一哈希
        hash_obj = hashlib.sha256()
        hash_obj.update(''.join(info).encode('utf-8', errors='ignore'))
        full_hash = hash_obj.hexdigest()

        # 返回长度 18 位（保持你原来的长度不变）
        return full_hash[:18]

    except Exception as e:
        return f"ERR-{str(e)[:18]}"



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
    #print(final_str)
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
                   shouyehuadongda,pinglunshijianjiange,init_time_2):
    result_j = judge()
    if (result_j == False):
        print("当前需要联系")
        return

    count_zong = 0
    while (True):
        try:
            print("while------------")
            result = duozhubo(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big,
                              swipe_small,
                              swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,
                              shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi,
                              jinrufangshi, shouyehuadongxiao, shouyehuadongda,pinglunshijianjiange,init_time_2)
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
                           shouyehuadongxiao, shouyehuadongda,pinglunshijianjiange,init_time_2)


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
             shouyehuadongda,pinglunshijianjiange,init_time_2):
    if (len(fudai) > 0):
        fudai_list = str(fudai).split("/")
        zhubo_len = len(fudai_list)
        i = 0
        while (True):
            result_main = 0

            print(serial,"--------","应该进入的直播间", fudai_list[i])
            write_serial_log(serial,str("应该进入的直播间"+ fudai_list[i]))
            try:
                result_main = main(serial, class_phone, search_path, comment_path, task, run_time, change_small,
                                   chang_big, swipe_small, swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,
                                   count_zong, shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao,
                                   fudai_list[i], fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
                                   shouyehuadongda,pinglunshijianjiange,init_time_2)
            except:
                error_info = traceback.format_exc()
                print(serial,"--------","完整错误信息:")
                print(error_info)
                write_serial_log(serial, str("完整错误信息"))
                write_serial_log(serial, str(error_info))

            if (result_main == "99"):
                return "99"

            if (result_main == "66"):  # 代表 进入下一个主播
                i += 1

            if(i >= zhubo_len):
                i = 0

            while (True):
                if (fudai_list[i] in black_zhubo):
                    i = i + 1
                else:
                    break
                if (i >= zhubo_len):
                    i = 0

            if (result_main == "55"):
                print("55 代表的意思是 中断了，意外出来了，还得重新试错")
                write_serial_log(serial, str("55 代表的意思是 中断了，意外出来了，还得重新试错"))
                print(traceback.print_exc())
                write_serial_log(serial,traceback.print_exc())
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
         shouyehuadongda,pinglunshijianjiange,init_time_2):
    #global ocr
    try:
        pinglunshijianjiange = int(pinglunshijianjiange)
        new_flag = "older"
        print(serial + "---------", "fudai,fudai_guanjianzi=", fudai, fudai_guanjianzi)
        write_serial_log(serial, "---------", "fudai,fudai_guanjianzi=", fudai, fudai_guanjianzi)

        if (len(task) == 0):
            print("0")
            write_serial_log(serial, "0")

            return
        print(serial + "---------", "1")

        d = get_device(serial)
        print("2")
        # d.watcher.when("以后再说").click()
        d.watcher.when("忽略").click()
        d.watcher.when("残忍放弃").click()
        d.watcher.start()
        pineisuijishijian_xiao = int(change_small)
        pineisuijishijian_da = int(chang_big)
        print(serial + "---------", "class_phone=", class_phone)
        write_serial_log(serial,  "class_phone=", class_phone)

        if (str(class_phone).count("-") < 1):
            print(serial + "---------", "当前手机没有分组")
            write_serial_log(serial, "---------", "当前手机没有分组")

            return "99"
        print("3")
        sleep_time_phone = 3
        if (str(class_phone).count("-") > 1):
            temp_time = str(class_phone).split("-")[2]
            if (temp_time.isdigit()):
                sleep_time_phone = int(temp_time)
                print(serial + "---------", "sleep_time_phone=", sleep_time_phone)
                write_serial_log(serial, "sleep_time_phone=", sleep_time_phone)

        print("4")

        if (str(class_phone).count("-") > 2):
            temp_cc = str(class_phone).split("-")[3]
            if (str(temp_cc).count("新") > 0):
                new_flag = "newer"
        print(serial + "---------", "new_flag=", new_flag)
        write_serial_log(serial, "new_flag=", new_flag)


        class_phone = str(class_phone).split("-")[0]
        print(serial + "---------", "class_phone---->", class_phone)
        write_serial_log(serial, "---------", "class_phone---->", class_phone)

        sleep_class(class_phone, init_time=init_time_2)
        print(serial + "---------", "当前会等=", sleep_time_phone)
        write_serial_log(serial, "当前会等=", sleep_time_phone)

        time.sleep(sleep_time_phone)
        updata_pkl("./shuju/" + serial + ".pkl", "执行状态", "运行中")
        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "进入直播间")
        if ("fudai" in task):
            time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme",stop=False)
            backToHome(d)
            time.sleep(3)
            count_temp = random.randint(int(shouyehuadongxiao), int(shouyehuadongda))
            for i in range(count_temp):
                beisaier(d)
                time.sleep(random.randint(1, 10))

            print(serial + "---------", "global_var----->", global_var)
            write_serial_log(serial, "global_var----->", global_var)

            if (jinrufangshi == "通过关注进入"):
                if (d(text="关注").exists(timeout=3)):
                    # d(text="关注").click()
                    random_click_view(d, d(text="关注").info)
                    time.sleep(3)
                else:
                    return "55"

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
                d.watcher.remove()
                print(serial + "---------", "通过搜索进入")
                write_serial_log(serial,  "---------", "通过搜索进入")

                if (d(text='首页').exists(timeout=3) or d(text='推荐').exists(timeout=3)):  # descriptionContains
                    if (d(description='搜索').exists(timeout=3)):  # descriptionContains
                        d(description='搜索').click()
                        print("当前有搜索按钮")
                        write_serial_log(serial,"当前有搜索按钮")

                        time.sleep(5)
                    else:
                        print("当前没有搜索按钮，只能点坐标啊")
                        write_serial_log(serial, "当前没有搜索按钮，只能点坐标啊")

                        d.click(d.info["displayWidth"] - 50, 180)
                        time.sleep(5)
                else:
                    print(serial + "---------", "当前bu在首页了。。。。。。。。")
                    write_serial_log(serial, "---------", "当前bu在首页了。。。。。。。。")

                    return "55"
                search_key = str(fudai)
                if ((len(search_key) >= 1) and (search_key != None)):
                    print(serial + "---------", "搜索词符合规范")
                    write_serial_log(serial,"---------", "搜索词符合规范")

                else:
                    print(serial + "---------", "搜索词为空")
                    write_serial_log(serial, "---------", "搜索词为空")

                    return "55"

                # shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + search_key)
                # shell_neibu(f"adb -s {serial} shell input  keyevent 279")

                if (d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').exists(timeout=3)):
                    d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').set_text(search_key)
                    time.sleep(5)
                else:
                    print(serial + "---------", "当前bu在首页了。。。。。。。。")
                    write_serial_log(serial,  "---------", "当前bu在首页了。。。。。。。。")

                    return "55"

                time.sleep(3)
                if(d(text="搜索").exists(timeout=3)):
                    #d(text="搜索").click()
                    print(f"{serial}----有搜索按钮")
                    write_serial_log(serial, str("---有搜索按钮"))

                    random_click_view(d,d(text="搜索").info)
                else:
                    d.click(d.info["displayWidth"] - 50, 180)
                time.sleep(8)

                if (new_flag == "newer"):
                    # if (d(text="直播").exists(timeout=3)):
                    #     random_click_view(d,d(text="直播").info)
                    # else:
                    #     print("没有直播tab")
                    #     write_serial_log(serial, "没有直播tab")
                    #
                    #     return "55"

                    print("ocr 进直播间")
                    write_serial_log(serial, str("ocr 进直播间"))

                    path_photo = take_screenshot(d)
                    ocr = get_available_ocr()
                    all_data = ocr.yewu(path_photo)
                    print(all_data)
                    write_serial_log(serial, str(all_data))

                    point = ocr.getPoint_by_data(all_data, "直播中")
                    write_serial_log(serial, str("直播中"))

                    print(point)
                    if (point != None):
                        d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))


                    elif(d(descriptionContains="直播，按钮").exists(timeout=3)):
                        print("点直播按钮")
                        write_serial_log(serial, str("点直播按钮"))

                        random_click_view(d,d(descriptionContains="直播，按钮").info)
                        time.sleep(3.5)
                    elif (d(descriptionContains="关注按钮").exists(timeout=3)):
                        print(serial + "---------", "关注按钮")
                        print(serial + "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                        write_serial_log(serial, str("关注按钮"))
                        write_serial_log(serial, "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])

                        d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50+450)
                        time.sleep(3.5)
                    else:

                        if (d(text="直播").exists(timeout=3)):
                            random_click_view(d,d(text="直播").info)
                            time.sleep(5)
                        else:
                            print("没有直播tab")
                            write_serial_log(serial, "没有直播tab")

                            return "55"

                        print("ocr 进直播间")
                        write_serial_log(serial, str("ocr 进直播间"))

                        path_photo = take_screenshot(d)
                        ocr = get_available_ocr()
                        all_data = ocr.yewu(path_photo)
                        print(all_data)
                        write_serial_log(serial, str(all_data))

                        point = ocr.getPoint_by_data(all_data, "直播中")
                        write_serial_log(serial, str("直播中"))

                        print(point)
                        if (point != None):
                            d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                            time.sleep(5)
                        else:
                            return "55"
                else:
                    if(d(textContains=fudai).exists(timeout=15)):
                        bb = d(textContains=fudai)
                        print(serial + "---------", "1")
                        if (len(bb) > 1):
                            print(serial + "---------", "2")
                            temp = bb[1].info
                            bottom = temp["bounds"]["bottom"]
                            left = temp["bounds"]["left"]
                            print(serial + "---------", "bottom", bottom, left)
                            write_serial_log(serial, "---------", "bottom", bottom, left)

                            d.click(150, int(bottom) - 80)
                            time.sleep(8)
                        elif (d(descriptionContains="关注按钮").exists(timeout=3)):
                            print(serial + "---------", "关注按钮")
                            print(serial + "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                            write_serial_log(serial, str("关注按钮"))
                            write_serial_log(serial, "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])

                            d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50)
                            time.sleep(3.5)
                    elif (d(textContains="粉丝：").exists(timeout=5)):
                        bottom = d(textContains="粉丝：").info["bounds"]["bottom"]
                        left = d(textContains="粉丝：").info["bounds"]["left"]
                        d.click(150, int(bottom) - 80)
                        time.sleep(8)
                    elif (d(descriptionContains="关注按钮").exists(timeout=3)):
                        print(serial + "---------", "关注按钮")
                        print(serial + "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])
                        write_serial_log(serial, str("关注按钮"))
                        write_serial_log(serial,  "---------", d(descriptionContains="关注按钮").info["bounds"]["bottom"])

                        d.click(154, d(descriptionContains="关注按钮").info["bounds"]["bottom"] - 50)
                        time.sleep(3.5)
                    else:
                        print(serial + "---------", "当前没有搜索框999。。。。。。。。")
                        return "55"

                if (d(textContains="说点什么").exists(timeout=15)):
                    print(serial + "---------", "当前成功进入直播间")
                    write_serial_log(serial, "---------", "当前成功进入直播间")

                else:
                    return "66"
            # sleep_class(class_phone,init_time=init_time_2)
            # time.sleep(5)
            fudai_flag = 0

            canyu_chenggong_dengdaishijian = get_value_by_key_pkl("shuju_config.pkl",
                                                                  "sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao")
            sousuocipinlvxiao_shouye_pinglunjiangeshijian_da = int(
                get_value_by_key_pkl("shuju_config.pkl", "sousuocipinlvxiao_shouye_pinglunjiangeshijian_da"))
            # print(sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao,sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
            start_time = time.time()
            # jiangehijian = random.randint(sousuocipinlvxiao_shouye_pinglunjiangeshijian_xiao,sousuocipinlvxiao_shouye_pinglunjiangeshijian_da)
            fudai_guanjianzi_dengdaishijian = int(
                get_value_by_key_pkl("shuju_config.pkl", "fudai_guanjianzi_dengdaishijian"))
            # fudai_resourceId = "com.ss.android.ugc.aweme:id/yxl"
            fudai_resourceId = None
            step = 0
            No_fudai_count = 0
            zhibojian_detail = 0
            while (True):
                if(zhibojian_detail != 0):
                    print("d.app_current()=", d.app_current())
                    write_serial_log(serial, d.app_current())

                    if (str(d.app_current()["activity"]).count(str(zhibojian_detail)) > 0):
                        print(f"{serial}------->当前在直播间")
                        write_serial_log(serial, str("当前在直播间"))

                    else:
                        print(f"{serial}------->当前bu在直播间")
                        write_serial_log(serial, str("当前bu在直播间"))

                        for iiiiii in range(5):
                            if (str(d.app_current()["activity"]).count("LivePlayActivity") > 0):
                                print(f"{serial}------->当前在直播间")
                                write_serial_log(serial, str("当前在直播间"))

                                break
                            else:
                                print(f"{serial}------->当前bu在直播间")
                                write_serial_log(serial, str("当前bu在直播间"))

                            time.sleep(5)
                        else:
                            print(f"{serial}------->五次了 一直bu在直播间，退出")
                            write_serial_log(serial, str("五次了 一直bu在直播间，退出"))

                            return "55"

                if (step != 0):
                    sleep_sleep(class_phone, init_time=init_time_2)

                flag = 0

                try:
                    if (new_flag == "newer"):
                        print(serial + "---------", "")
                        write_serial_log(serial, str("----------"))

                        if (fudai_resourceId == None):
                            if (d(description="关闭").exists(timeout=3)):  # com.ss.android.ugc.aweme:id/yxl
                                print(serial + "---------", "超级福袋")
                                print(serial + "---------", "，按钮")
                                write_serial_log(serial, str("---------超级福袋"))
                                write_serial_log(serial, str("按钮"))

                                if(zhibojian_detail == 0):
                                    zhibojian_detail = d.app_current()["activity"]

                                close_point_y = d(resourceId="com.ss.android.ugc.aweme:id/root").info["bounds"][
                                                    "bottom"] + 180
                                print(serial + "---------", "close_point_y=", close_point_y)
                                write_serial_log(serial, "close_point_y=", close_point_y)

                                fudai_resourceId = find_id_from_area(d, 100, close_point_y)

                            else:
                                print(serial + "---------", "没有关闭按钮啊")
                                write_serial_log(serial, "---------", "没有关闭按钮啊")

                                continue
                            continue

                        print(serial + "---------", "fudai_resourceId11=", fudai_resourceId)
                        if (d(resourceId=fudai_resourceId).exists(timeout=3)):  # com.ss.android.ugc.aweme:id/yxl
                            print(serial + "---------", "超级福袋")
                            print(serial + "---------", "，按钮")
                            write_serial_log(serial, str("超级福袋"))
                            write_serial_log(serial, str("按钮"))

                            current_time = time.time()
                            if (current_time - start_time > pinglunshijianjiange):
                                # 检查一下 是不是开始评论了
                                if os.path.exists("pinglun111.txt"):
                                    start_time = current_time
                                    zhibojianpinglun(d)
                                    backToLiveRoom(d)

                            if (step != 0):
                                sleep_class(class_phone, init_time=init_time_2)
                            print("fudai_flag===",fudai_flag)
                            write_serial_log(serial, "fudai_flag===",fudai_flag)

                            if (0 == 0):
                                time.sleep(random.randint(pineisuijishijian_xiao, pineisuijishijian_da))
                                print("")

                                updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "点击福袋")
                                # d(textContains='超级福袋').click()
                                print(serial + "---------", "开始点击超级福袋")
                                write_serial_log(serial, "---------", "开始点击超级福袋")

                                if (step != 0):
                                    sleep_class(class_phone, init_time=init_time_2)

                                if (1 == 2):
                                    print("kyi找到福袋id")
                                    random_click_view(d,d(resourceId="com.ss.android.ugc.aweme:id/zqc"))
                                else:

                                    # path_photo = take_screenshot(d)
                                    # #all_data = ocr.yewu(path_photo)
                                    # point = find_target_in_template_folder(path_photo, "fudai_path")

                                    if(step != 0):
                                        print(serial + "---------", "当前会等小时间=", sleep_time_phone)
                                        write_serial_log(serial,  "---------", "当前会等小时间=", sleep_time_phone)

                                        time.sleep(sleep_time_phone)
                                    else:
                                        print(serial + "---------", "第一次不用等小时间", sleep_time_phone)
                                    point = find_id_from_area_2(d,30,500,200,600)

                                    print("point=",point)
                                    write_serial_log(serial, "point=",point)

                                    if(len(point)>0):
                                        xx, yy = point[-1]
                                        print(f"{serial}---->当前有福袋，第一层")
                                        write_serial_log(serial, str("当前有福袋，第一层"))

                                        sleep_sleep(class_phone, init_time=init_time_2)
                                        d.click(int(xx),int(yy))

                                    else:
                                        # point = find_target_by_template(path_photo, "fudai1.png")
                                        # if (point != None):
                                        #     xx, yy = point
                                        #     print(f"{serial}---->当前有福袋，第二层")
                                        #     sleep_sleep(class_phone, init_time=init_time_2)
                                        #     d.click(int(xx), int(yy)+10)
                                        # else:
                                        print(f"{serial}---->当前彻底没有福袋")
                                        write_serial_log(serial, str("当前彻底没有福袋"))

                                time.sleep(3)

                                if (len(fudai_guanjianzi) > 0):
                                    print("开始验证福袋关键字")
                                    write_serial_log(serial, str("开始验证福袋关键字"))

                                    flag_guanjianzi = 0
                                    path_photo = take_screenshot(d)
                                    ocr = get_available_ocr()
                                    all_data = ocr.yewu(path_photo)
                                    if(all_data == "22"):
                                        print(f"ocr 失败了啊，需要重新加载一下，本来的ocr={ocr}")
                                        ocr = get_available_ocr()
                                        #ocr = OCRProcessor()
                                        print(f"重新获取ocr之后={ocr}")
                                    if (str(all_data).count("后开奖") > 0):

                                        xx,yy = ocr.getPoint_by_data(all_data,"后开奖")

                                        print("当前页面有后开奖")
                                        write_serial_log(serial, str("当前页面有后开奖"))

                                        guanjianzi_list = str(fudai_guanjianzi).split("/")
                                        print("guanjianzi_list=", guanjianzi_list)
                                        write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                        for guanjianzi in guanjianzi_list:
                                            print("guanjianzi=", guanjianzi)
                                            write_serial_log(serial, guanjianzi)

                                            aaa = ocr.getAreaDataFromAlldataByPoint(all_data,100,3000,yy,5000)
                                            print("范围内的文字有=",aaa)
                                            write_serial_log(serial,"范围内的文字有=",aaa)

                                            if (len(str(guanjianzi)) > 0):
                                                if (str(aaa).count(guanjianzi) > 0):
                                                    print(f"包含{guanjianzi}，可以强")
                                                    write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                    flag_guanjianzi = 1
                                                    break
                                        if (flag_guanjianzi == 0):
                                            print("当前不能抢")
                                            write_serial_log(serial,"当前不能抢")

                                            black_zhubo.append(fudai)
                                            if (zhubo_len == 1):
                                                print(serial + "---------", "返回")
                                                write_serial_log(serial,"---------", "返回")

                                                if (d(description='说点什么...').exists(timeout=1)):
                                                    print("")
                                                else:
                                                    d.press("back")
                                                time.sleep(15)
                                                print("fanhui")
                                                write_serial_log(serial,"fanhui")

                                                continue
                                            return "66"
                                    fudai_flag = 1
                                    if (flag_guanjianzi == 0):
                                        continue
                            else:
                                print(serial + "---------", "没有超级福袋")  # return
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)
                        else:
                            print(serial + "---------", "当前没有超级福袋")
                            write_serial_log(serial, "当前没有超级福袋")

                            if( d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=3)):
                                print("当前没有弹窗")
                                write_serial_log(serial, "当前没有弹窗")

                                continue


                            path_photo = take_screenshot(d)
                            ocr = get_available_ocr()
                            all_data = ocr.yewu(path_photo)
                            if (all_data == "22"):
                                print(f"ocr 失败了啊，需要重新加载一下，本来的ocr={ocr}")
                                #ocr = OCRProcessor()
                                print(f"重新获取ocr之后={ocr}")
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)

                            if (str(all_data).count("一键发表评论") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有一件发表评论")
                                write_serial_log(serial, "有一件发表评论")

                                if (len(fudai_guanjianzi) > 0):
                                    print("开始验证福袋关键字")
                                    write_serial_log(serial, "开始验证福袋关键字")

                                    flag_guanjianzi = 0
                                    # path_photo = take_screenshot(d)
                                    # all_data = ocr.yewu(path_photo)
                                    if (str(all_data).count("后开奖") > 0):
                                        print("当前页面有后开奖")
                                        write_serial_log(serial, "当前页面有后开奖")

                                        guanjianzi_list = str(fudai_guanjianzi).split("/")
                                        print("guanjianzi_list=", guanjianzi_list)
                                        write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                        for guanjianzi in guanjianzi_list:
                                            print("guanjianzi=", guanjianzi)
                                            write_serial_log(serial,"guanjianzi=", guanjianzi)

                                            if (len(str(guanjianzi)) > 0):
                                                if (str(all_data).count(guanjianzi) > 0):
                                                    print(f"包含{guanjianzi}，可以强")
                                                    write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                    flag_guanjianzi = 1
                                                    break
                                        if (flag_guanjianzi == 0):
                                            continue
                                    fudai_flag = 1
                                    if (flag_guanjianzi == 0):
                                        continue

                                # d(textContains='一键发表评论').click()
                                # random_click_view(d, d(textContains='一键发表评论').info)
                                point = ocr.getPoint_by_data(all_data, "一键发表评论")
                                if (point != None):
                                    sleep_sleep(class_phone, init_time=init_time_2)
                                    if( d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=2)):
                                        print("当前在直播间")
                                        write_serial_log(serial, "当前在直播间")

                                    else:
                                        d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    continue
                                flag = 1
                            elif (str(all_data).count("发表评论") > 0):
                                print(serial + "---------", "发表评论")
                                write_serial_log(serial, "---------", "发表评论")

                                # d(textContains='一键发表评论').click()
                                # random_click_view(d, d(textContains='一键发表评论').info)

                                if (len(fudai_guanjianzi) > 0):
                                    print("开始验证福袋关键字")
                                    write_serial_log(serial, "开始验证福袋关键字")

                                    flag_guanjianzi = 0
                                    # path_photo = take_screenshot(d)
                                    # all_data = ocr.yewu(path_photo)
                                    if (str(all_data).count("后开奖") > 0):
                                        print("当前页面有后开奖")
                                        write_serial_log(serial, "当前页面有后开奖")

                                        guanjianzi_list = str(fudai_guanjianzi).split("/")
                                        print("guanjianzi_list=", guanjianzi_list)
                                        write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                        for guanjianzi in guanjianzi_list:
                                            print("guanjianzi=", guanjianzi)
                                            write_serial_log(serial,"guanjianzi=", guanjianzi)

                                            if (len(str(guanjianzi)) > 0):
                                                if (str(all_data).count(guanjianzi) > 0):
                                                    print(f"包含{guanjianzi}，可以强")
                                                    write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                    flag_guanjianzi = 1
                                                    break
                                        if (flag_guanjianzi == 0):
                                            continue
                                    fudai_flag = 1
                                    if (flag_guanjianzi == 0):
                                        continue

                                point = ocr.getPoint_by_data_back(all_data, "发表评论")
                                if (point != None):
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    # continue
                                flag = 1
                            else:
                                print(serial + "---------", "没有一件发表评论")
                                write_serial_log(serial,  "---------", "没有一件发表评论")

                            if (str(all_data).count("红包") > 0 and str(all_data).count("抢") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有红包，点返回")
                                write_serial_log(serial,  "---------", "有红包，点返回")

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
                                write_serial_log(serial, "---------", "没有一件发表评论")

                            if (str(all_data).count("开心收下")):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有开心收下，点返回")
                                write_serial_log(serial, "---------", "有开心收下，点返回")

                                if (d(description='说点什么...').exists(timeout=1)):
                                    print("")
                                else:
                                    d.press("back")
                                flag = 1
                            else:
                                print(serial + "---------", "没有开心收下")
                                write_serial_log(serial, "---------", "没有开心收下")

                            if (str(all_data).count("开心收下")):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有开心收下，点返回")
                                write_serial_log(serial, "---------", "有开心收下，点返回")

                                if (d(description='说点什么...').exists(timeout=1)):
                                    print("")
                                else:
                                    d.press("back")
                                flag = 1
                            else:
                                print(serial + "---------", "没有开心收下")
                                write_serial_log(serial, "---------", "没有开心收下")

                            if (str(all_data).count("立即用券")):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有立即用券，点返回")
                                write_serial_log(serial, "有立即用券，点返回")

                                if (d(description='说点什么...').exists(timeout=1)):
                                    print("")
                                else:
                                    d.press("back")
                                flag = 1
                            else:
                                print(serial + "---------", "没有立即用券")
                                write_serial_log(serial, str("没有立即用券"))

                            if (str(all_data).count("立即用券") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "立即用券")
                                write_serial_log(serial, str("立即用券"))

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
                                write_serial_log(serial, str("没有一件发表评论"))

                            if (str(all_data).count("立即用券") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有一件发表评论")
                                write_serial_log(serial, str("有一件发表评论"))

                                # d(textContains='一键发表评论').click()
                                # random_click_view(d, d(textContains='一键发表评论').info)
                                point = ocr.getPoint_by_data(all_data, "立即用券")
                                if (point != None):
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    continue
                                flag = 1
                            else:
                                print(serial + "---------", "没有一件发表评论")
                                write_serial_log(serial, str("没有一件发表评论"))

                                # return
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)
                            if (str(all_data).count("参与抽奖") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "参与抽奖")
                                write_serial_log(serial, str("参与抽奖"))

                                # d(text='加入粉丝团').click()
                                point = ocr.getPoint_by_data(all_data, "参与抽奖")
                                if (point != None):
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    continue
                                flag = 1

                            else:
                                print(serial + "---------", "没有参与抽奖")
                                write_serial_log(serial, str("没有参与抽奖"))


                            if (str(all_data).count("加入购物粉丝团并关注主播") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有加入购物粉丝团并关注主播，但是也得识别关键字了")
                                write_serial_log(serial, str("55 有加入购物粉丝团并关注主播，但是也得识别关键字了"))

                                flag_guanjianzi = 0
                                if (str(all_data).count("后开奖") > 0):
                                    print("当前页面有后开奖")
                                    write_serial_log(serial, str("当前页面有后开奖"))

                                    guanjianzi_list = str(fudai_guanjianzi).split("/")
                                    print("guanjianzi_list=", guanjianzi_list)
                                    write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                    for guanjianzi in guanjianzi_list:
                                        print("guanjianzi=", guanjianzi)
                                        write_serial_log(serial, "guanjianzi=", guanjianzi)

                                        if (len(str(guanjianzi)) > 0):
                                            if (str(all_data).count(guanjianzi) > 0):
                                                print(f"包含{guanjianzi}，可以强")
                                                write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                flag_guanjianzi = 1
                                                break
                                    if (flag_guanjianzi == 0):
                                        print("当前不能抢")
                                        write_serial_log(serial, str("当前不能抢"))

                                        black_zhubo.append(fudai)
                                        if (zhubo_len == 1):
                                            print(serial + "---------", "返回")
                                            write_serial_log(serial,"---------", "返回")

                                            if (d(description='说点什么...').exists(timeout=1)):
                                                print("")
                                            else:
                                                d.press("back")
                                            time.sleep(15)
                                            print("fanhui")
                                            write_serial_log(serial,"fanhui")

                                            continue
                                        return "66"
                                fudai_flag = 1
                                if (flag_guanjianzi == 0):
                                    continue



                                # d(text='加入粉丝团').click()
                                print("fudai_path")
                                write_serial_log(serial, str("fudai_path"))

                                x000 = 0
                                y000 = 0

                                point = ocr.getPoint_by_data(all_data, "加入购物粉丝团并关注主播")
                                if (point != None):
                                    x000 = point[0]
                                    y000 = point[1]
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    #continue
                                    time.sleep(8)

                                flag = 1

                                if(d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(30, 40))
                                    time.sleep(8)
                                    print("333")

                                if (d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.press("back")
                                    time.sleep(8)
                                    print("444")
                                continue

                            else:
                                print(serial + "---------", "加入购物粉丝团并关注主播")
                                write_serial_log(serial, str("加入购物粉丝团并关注主播"))
                                # return


                            if (str(all_data).count("加入直播粉丝团并关注主播") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "加入直播粉丝团并关注主播，但是也得识别关键字了")
                                write_serial_log(serial, str("55 加入直播粉丝团并关注主播，但是也得识别关键字了"))

                                flag_guanjianzi = 0
                                if (str(all_data).count("后开奖") > 0):
                                    print("当前页面有后开奖")
                                    write_serial_log(serial, str("当前页面有后开奖"))

                                    guanjianzi_list = str(fudai_guanjianzi).split("/")
                                    print("guanjianzi_list=", guanjianzi_list)
                                    write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                    for guanjianzi in guanjianzi_list:
                                        print("guanjianzi=", guanjianzi)
                                        write_serial_log(serial, "guanjianzi=", guanjianzi)

                                        if (len(str(guanjianzi)) > 0):
                                            if (str(all_data).count(guanjianzi) > 0):
                                                print(f"包含{guanjianzi}，可以强")
                                                write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                flag_guanjianzi = 1
                                                break
                                    if (flag_guanjianzi == 0):
                                        print("当前不能抢")
                                        write_serial_log(serial, str("当前不能抢"))

                                        black_zhubo.append(fudai)
                                        if (zhubo_len == 1):
                                            print(serial + "---------", "返回")
                                            write_serial_log(serial,"---------", "返回")

                                            if (d(description='说点什么...').exists(timeout=1)):
                                                print("")
                                            else:
                                                d.press("back")
                                            time.sleep(15)
                                            print("fanhui")
                                            write_serial_log(serial,"fanhui")

                                            continue
                                        return "66"
                                fudai_flag = 1
                                if (flag_guanjianzi == 0):
                                    continue



                                # d(text='加入粉丝团').click()
                                print("fudai_path")
                                write_serial_log(serial, str("fudai_path"))

                                x000 = 0
                                y000 = 0

                                point = ocr.getPoint_by_data(all_data, "加入直播粉丝团并关注主播")
                                if (point != None):
                                    x000 = point[0]
                                    y000 = point[1]
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    #continue
                                    time.sleep(8)

                                flag = 1

                                if(d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(30, 40))
                                    time.sleep(8)
                                    print("333")

                                if (d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.press("back")
                                    time.sleep(8)
                                    print("444")
                                continue

                            else:
                                print(serial + "---------", "没有加入直播粉丝团并关注主播")
                                write_serial_log(serial, str("没有加入直播粉丝团并关注主播"))
                                # return


                            if (str(all_data).count("加入粉丝团") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有加入粉丝团，但是也得识别关键字了")
                                write_serial_log(serial, str("55 有加入粉丝团，但是也得识别关键字了"))

                                flag_guanjianzi = 0
                                if (str(all_data).count("后开奖") > 0):
                                    print("当前页面有后开奖")
                                    write_serial_log(serial, str("当前页面有后开奖"))

                                    guanjianzi_list = str(fudai_guanjianzi).split("/")
                                    print("guanjianzi_list=", guanjianzi_list)
                                    write_serial_log(serial, "guanjianzi_list=", guanjianzi_list)

                                    for guanjianzi in guanjianzi_list:
                                        print("guanjianzi=", guanjianzi)
                                        write_serial_log(serial, "guanjianzi=", guanjianzi)

                                        if (len(str(guanjianzi)) > 0):
                                            if (str(all_data).count(guanjianzi) > 0):
                                                print(f"包含{guanjianzi}，可以强")
                                                write_serial_log(serial,f"包含{guanjianzi}，可以强")

                                                flag_guanjianzi = 1
                                                break
                                    if (flag_guanjianzi == 0):
                                        print("当前不能抢")
                                        write_serial_log(serial, str("当前不能抢"))

                                        black_zhubo.append(fudai)
                                        if (zhubo_len == 1):
                                            print(serial + "---------", "返回")
                                            write_serial_log(serial,"---------", "返回")

                                            if (d(description='说点什么...').exists(timeout=1)):
                                                print("")
                                            else:
                                                d.press("back")
                                            time.sleep(15)
                                            print("fanhui")
                                            write_serial_log(serial,"fanhui")

                                            continue
                                        return "66"
                                fudai_flag = 1
                                if (flag_guanjianzi == 0):
                                    continue



                                # d(text='加入粉丝团').click()
                                print("fudai_path")
                                write_serial_log(serial, str("fudai_path"))

                                x000 = 0
                                y000 = 0

                                point = ocr.getPoint_by_data(all_data, "加入粉丝团")
                                if (point != None):
                                    x000 = point[0]
                                    y000 = point[1]
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    #continue
                                    time.sleep(8)

                                flag = 1

                                if(d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(30, 40))
                                    time.sleep(8)
                                    print("333")

                                if (d(resourceId="com.ss.android.ugc.aweme:id/root").exists(timeout=5)):
                                    print("当前应该没有弹窗")
                                    write_serial_log(serial, str("当前应该没有弹窗"))
                                else:
                                    print("当前应该有弹窗")
                                    write_serial_log(serial, str("当前应该有弹窗"))
                                    d.press("back")
                                    time.sleep(8)
                                    print("444")
                                continue

                            else:
                                print(serial + "---------", "没有加入粉丝团")
                                write_serial_log(serial, str("没有加入粉丝团"))
                                # return
                            if (str(all_data).count("去发表评论") > 0):  # 这种是需要 在输入框内 评论的
                                # d(text='添加评论...').click()
                                # d(text='去发表评论').click()
                                point = ocr.getPoint_by_data(all_data, "加入粉丝团")
                                if (point != None):
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                print(serial + "---------", "有去发表评论")
                                write_serial_log(serial, str("有去发表评论"))
                                flag = 1

                                if (d(text='发送').exists(timeout=1)):  # 这种是需要 在输入框内 评论的
                                    # d(text='添加评论...').click()
                                    # d(text='发送').click()
                                    random_click_view(d, d(text='发送').info)
                                    print(serial + "---------", "有发送按钮")
                                    write_serial_log(serial, str("有发送按钮"))
                                    continue
                            else:
                                print(serial + "---------", "没有去发表评论")
                                write_serial_log(serial, str("没有去发表评论"))
                                # return
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)

                            if (str(all_data).count("我的等级特权") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有我的等级特权")
                                write_serial_log(serial, str("有我的等级特权"))
                                if (d(description='说点什么...').exists(timeout=1)):
                                    print(serial + "---------", "")
                                    write_serial_log(serial, str("---------"))
                                else:
                                    d.press("back")
                                flag = 1
                                continue
                            else:
                                print(serial + "---------", "没有我的等级特权")
                                write_serial_log(serial, str("没有我的等级特权"))
                                # return

                            if (str(all_data).count("已参与") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "有已参与，等着就行了")
                                write_serial_log(serial, str("有已参与，等着就行了"))
                                flag = 1
                            else:
                                print(serial + "---------", "没有已参与")
                                write_serial_log(serial, str("没有已参与"))

                            if (str(all_data).count("做任务赚宝石") > 0 or str(all_data).count("宝石换钻") > 0):
                                # d(text='添加评论...').click()
                                print(serial + "---------", "做任务赚宝石 或者 宝石换钻")
                                write_serial_log(serial, str("做任务赚宝石 或者 宝石换钻"))
                                d.press("back")
                                time.sleep(2)
                                flag = 1
                            else:
                                print(serial + "---------", "没有已参与")
                                write_serial_log(serial, str("没有已参与"))

                            if (str(all_data).count("我知道了") > 0):
                                # d(text='添加评论...').click()
                                updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "没有抢到福袋")
                                # time.sleep(random.randint(2,15))
                                # time.sleep(sleep_time_phone)
                                # time.sleep(sleep_time_phone)
                                print("有我知道啦")
                                write_serial_log(serial, str("有我知道啦"))
                                if (str(all_data).count("我知道了") > 0):
                                    # d(text='我知道了').click()
                                    point = ocr.getPoint_by_data(all_data, "我知道了")
                                    if (point != None):
                                        d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                        continue

                                #     print("有我知道啦")
                                #     flag = 1
                                #     fudai_flag = 0
                                #     time.sleep(5)
                                #     # lingling = d(text='00')
                                #     # if (len(lingling) > 1):
                                #     #     print("当前需要返回")
                                #     #     d.press("back")
                                #     # continue
                                #     path_photo = take_screenshot(d)
                                #     all_data = ocr.yewu(path_photo)
                                #     if (str(all_data).count("后开奖") > 0):
                                #         # d(text='添加评论...').click()
                                #         print("参与成功弹窗没有 自动隐藏")
                                #         points = ocr.getPoints_by_data(all_data, "后开奖")
                                #         if (len(points) > 0):
                                #             d.press("back")
                                #             time.sleep(3)
                                #             continue
                                #         flag = 1
                                #     else:
                                #         print("没有已参与")

                                # time.sleep(sleep_time_phone)
                                #
                                # time.sleep(15)
                            elif (str(all_data).count("我知道") > 0):
                                time.sleep(15)
                                #     # d(text='添加评论...').click()
                                updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "没有抢到福袋")
                                # time.sleep(random.randint(2,15))
                                # time.sleep(sleep_time_phone)
                                # time.sleep(sleep_time_phone)
                                print("有我知道啦")
                                write_serial_log(serial, str("有我知道啦"))
                                if (str(all_data).count("我知道") > 0):
                                    # d(text='我知道了').click()
                                    point = ocr.getPoint_by_data(all_data, "我知道")
                                    if (point != None):
                                        d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                        continue

                            else:
                                print(serial + "---------", "没有我知道啦")
                                write_serial_log(serial, str("没有我知道啦"))
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)

                            if (str(all_data).count("立即领取奖品") > 0):
                                # d(text='添加评论...').click()
                                updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抢到福袋")
                                point = ocr.getPoint_by_data(all_data, "立即领取奖品")
                                if (point != None):
                                    time.sleep(100 * 60 * 60)
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))

                                print(serial + "---------", "立即领取奖品")
                                write_serial_log(serial, str("立即领取奖品"))
                                flag = 1
                                fudai_flag = 0
                                time.sleep(5)
                                path_photo = take_screenshot(d)
                                ocr = get_available_ocr()
                                all_data = ocr.yewu(path_photo)
                                if (all_data == "22"):
                                    print(f"ocr 失败了啊，需要重新加载一下，本来的ocr={ocr}")
                                    #ocr = OCRProcessor()
                                    print(f"重新获取ocr之后={ocr}")
                                if (str(all_data).count("00") > 1):
                                    # d(text='添加评论...').click()
                                    print(serial + "---------", "参与成功弹窗没有 自动隐藏")
                                    write_serial_log(serial, str("参与成功弹窗没有 自动隐藏"))
                                    points = ocr.getPoints_by_data(all_data, "00")
                                    if (len(points) > 1):
                                        if (d(description='说点什么...').exists(timeout=1)):
                                            print(serial + "---------", "")
                                            write_serial_log(serial,"--1234")
                                        else:
                                            d.press("back")
                                        time.sleep(3)
                                        continue
                                    flag = 1
                                else:
                                    print(serial + "---------", "没有已参与")
                                    write_serial_log(serial, str("没有已参与"))

                            else:
                                print(serial + "---------", "没有立即领取奖品")
                                write_serial_log(serial, str("没有立即领取奖品"))
                            # return
                            if (str(all_data).count("等待开奖") > 0):
                                # d(text='添加评论...').click()
                                step = step + 1
                                # d(text='参与成功 等待开奖').click()
                                print(serial + "---------", "有参与成功，等着就行了")
                                write_serial_log(serial, str("有参与成功，等着就行了"))


                                daojishi_time = get_lottery_remaining_time(all_data)
                                print(f"{serial}------>倒计时daojishi_time=",daojishi_time)
                                write_serial_log(serial, f"{serial}------>倒计时daojishi_time=",daojishi_time)
                                if(str(daojishi_time).isdigit()):

                                    if(daojishi_time > 0):
                                        time.sleep(daojishi_time+random.randint(20,50))
                                    elif(daojishi_time == 0):
                                        time.sleep(16)
                                    else:
                                        print(f"{serial}------>当前获取的倒计时不对啊", daojishi_time)
                                        write_serial_log(serial, f"{serial}------>当前获取的倒计时不对啊", daojishi_time)
                                        continue

                                    print(f"{serial}---倒计时结束，开始回到福袋")
                                    write_serial_log(serial, f"{serial}---倒计时结束，开始回到福袋")

                                    path_photo = take_screenshot(d)
                                    ocr = get_available_ocr()
                                    all_data = ocr.yewu(path_photo)

                                    if (str(all_data).count("立即领取奖品") > 0):
                                        # d(text='添加评论...').click()
                                        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抢到福袋")
                                        point = ocr.getPoint_by_data(all_data, "立即领取奖品")
                                        if (point != None):
                                            time.sleep(100 * 60 * 60)
                                            d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))

                                    for ppp in range(3):
                                        if (d(description='说点什么...').exists(timeout=3)):
                                            print(f"{serial}---->huidao，福袋页面了")
                                            write_serial_log(serial,f"{serial}---->huidao，福袋页面了")
                                        else:
                                            print(f"{serial}---倒计时结束，返回")
                                            write_serial_log(serial,f"{serial}---倒计时结束，返回")
                                            d.press("back")
                                continue

                            else:
                                print(serial + "---------", "没有有参与成功，等着就行了")
                                write_serial_log(serial, "没有有参与成功，等着就行了")

                            if (str(all_data).count("请勿离开直播间") > 0):
                                # d(text='添加评论...').click()
                                step = step + 1
                                # d(text='参与成功 等待开奖').click()
                                print(serial + "---------", "请勿离开直播间，等着就行了")
                                write_serial_log(serial, str("请勿离开直播间，等着就行了"))


                                daojishi_time = get_lottery_remaining_time(all_data)
                                print(f"{serial}------>倒计时daojishi_time=",daojishi_time)
                                write_serial_log(serial, f"{serial}------>倒计时daojishi_time=",daojishi_time)
                                if(str(daojishi_time).isdigit()):

                                    if(daojishi_time > 0):
                                        time.sleep(daojishi_time+random.randint(20,50))
                                    elif(daojishi_time == 0):
                                        time.sleep(16)
                                    else:
                                        print(f"{serial}------>当前获取的倒计时不对啊", daojishi_time)
                                        write_serial_log(serial, f"{serial}------>当前获取的倒计时不对啊", daojishi_time)
                                        continue

                                    print(f"{serial}---倒计时结束，开始回到福袋")
                                    write_serial_log(serial, f"{serial}---倒计时结束，开始回到福袋")

                                    path_photo = take_screenshot(d)
                                    ocr = get_available_ocr()
                                    all_data = ocr.yewu(path_photo)

                                    if (str(all_data).count("立即领取奖品") > 0):
                                        # d(text='添加评论...').click()
                                        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抢到福袋")
                                        point = ocr.getPoint_by_data(all_data, "立即领取奖品")
                                        if (point != None):
                                            time.sleep(100 * 60 * 60)
                                            d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))

                                    for ppp in range(3):
                                        if (d(description='说点什么...').exists(timeout=3)):
                                            print(f"{serial}---->huidao，福袋页面了")
                                            write_serial_log(serial,f"{serial}---->huidao，福袋页面了")
                                        else:
                                            print(f"{serial}---倒计时结束，返回")
                                            write_serial_log(serial,f"{serial}---倒计时结束，返回")
                                            d.press("back")
                                continue

                            else:
                                print(serial + "---------", "没有有参与成功，等着就行了")
                                write_serial_log(serial, "没有有参与成功，等着就行了")

                            if (str(all_data).count("活动已结束") > 0):
                                # d(text='添加评论...').click()
                                # d(text='参与成功 等待开奖').click()
                                print(serial + "---------", "活动已结束")
                                write_serial_log(serial, "活动已结束")
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
                                write_serial_log(serial, "没有有参与成功，等着就行了")

                            if (str(all_data).count("开心收下") > 0):
                                # d(text='添加评论...').click()
                                # d(text='参与成功 等待开奖').click()
                                print(serial + "---------", "有开心收下")
                                write_serial_log(serial, "有开心收下")
                                if (d(description='说点什么...').exists(timeout=1)):
                                    print(serial + "---------", "")
                                    write_serial_log(serial, str("   "))
                                else:
                                    d.press("back")
                                time.sleep(5)
                                # time.sleep(fudai_guanjianzi_dengdaishijian)
                                flag = 1
                                continue
                            else:
                                print(serial + "---------", "没有有参与成功，等着就行了")
                                write_serial_log(serial, str("没有有参与成功，等着就行了"))
                                # return
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)
                            if (str(all_data).count("开始观看直播任务") > 0):
                                # d(text='添加评论...').click()
                                point = ocr.getPoint_by_data(all_data, "开始观看直播任务")
                                if (point != None):
                                    d.click(point[0] + random.randint(-3, 3), point[1] + random.randint(-3, 3))
                                    continue
                                print(serial + "---------", "开始观看直播任务")
                                write_serial_log(serial, str("开始观看直播任务"))
                                flag = 1
                            else:
                                print(serial + "---------", "没有开始观看直播任务")
                                write_serial_log(serial, str("没有开始观看直播任务"))
                                # return
                            if (str(all_data).count("还需看播") > 0):
                                # d(text='添加评论...').click()
                                # d(text='参与成功 等待开奖').click()
                                print(serial + "---------", "还需看播，等着就行了")
                                write_serial_log(serial, str("还需看播，等着就行了"))
                                flag = 1

                            else:
                                print(serial + "---------", "没有还需看播")
                                write_serial_log(serial, str("没有还需看播"))

                            if (str(all_data).count("直播已结束") > 0):  # 判断主播退出直播间
                                # d(text='添加评论...').click()
                                # d(text='参与成功 等待开奖').click()
                                return "66"
                            else:
                                print(serial + "---------", "没有直播已结束")
                                write_serial_log(serial, str("没有直播已结束"))

                            if (str(all_data).count("开始检测") > 0):  # 判断有没有用户校验
                                # d(text='添加评论...').click()
                                # d(text='参与成功 等待开奖').click()
                                return "99"
                            else:
                                print(serial + "---------", "没有开始检测")
                                write_serial_log(serial, str("没有开始检测"))
                            if (step != 0):
                                sleep_sleep(class_phone, init_time=init_time_2)

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
                            write_serial_log(serial, str("超级福袋"))
                            current_time = time.time()
                            print(serial + "---------", "1")
                            # if(current_time - start_time > jiangehijian):
                            #     #检查一下 是不是开始评论了
                            #     start_time = current_time
                            #     zhibojianpinglun(d)
                            #     backToLiveRoom(d)

                            if (fudai_flag == 0):
                                print(serial + "---------", "2")
                                if (step != 0):
                                    sleep_class(class_phone, init_time=init_time_2)
                                print(serial + "---------", "2")
                                time.sleep(random.randint(pineisuijishijian_xiao, pineisuijishijian_da))
                                print(serial + "---------", "3")
                            if (d(textContains='超级福袋').exists(timeout=0.1)):
                                print(serial + "---------", "4")
                                time.sleep(sleep_time_phone)
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
                            write_serial_log(serial, str("没有超级福袋"))
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)

                        if (d(textContains='一键发表评论').exists(timeout=1)):
                            # d(text='添加评论...').click()
                            print(serial + "---------", "有一件发表评论")
                            write_serial_log(serial, str("有一件发表评论"))
                            # d(textContains='一键发表评论').click()
                            random_click_view(d, d(textContains='一键发表评论').info)
                            flag = 1
                        else:
                            print(serial + "---------", "没有一件发表评论")
                            write_serial_log(serial, str("没有一件发表评论"))
                            # return
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)
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
                            time.sleep(sleep_time_phone)

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
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)

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
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)

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
                            # time.sleep(int(canyu_chenggong_dengdaishijian))
                            step = step + 1
                            # if (d(description='说点什么...').exists(timeout=1)):
                            #     print(serial + "---------", "")
                            # else:
                            #     print(serial + "---------", "20")
                            #     d.press("back")
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
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)
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
                        if (step != 0):
                            sleep_sleep(class_phone, init_time=init_time_2)

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
            print(serial + "---------", "filepath-->", filepath)
            if (os.path.isfile(filepath)):
                updata_pkl(filepath, "执行状态", "准备退出直播间")
            if (step != 0):
                sleep_class(class_phone, init_time=init_time_2)
            time.sleep(sleep_time_phone)
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
            print(serial + "---------", "filepath-->", filepath)
            if (os.path.isfile(filepath)):
                updata_pkl(filepath, "执行状态", "已退出直播间")
            return "99"

        print(serial + "---------", "运行结束")
        filepath = './shuju/' + serial + ".pkl"
        print(serial + "---------", "filepath-->", filepath)
        if (os.path.isfile(filepath)):
            updata_pkl(filepath, "执行状态", "运行结束")
            updata_pkl(filepath, "进行的任务", "空闲")
        return '99'
    except BaseException as e:
        print("bengkuile ", e)
        error_info = traceback.format_exc()
        print(error_info)
        return "55"


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
init_time = 1740237875

def sleep_sleep(class_phone,init_time=init_time):
    if (os.path.isfile("pause.txt")):
        time.sleep(1)
        while (True):
            if (os.path.isfile("pause.txt")):
                time.sleep(1)
            else:
                sleep_class(class_phone,init_time=init_time)
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



jiange_shijian = 10

def calculate_time_difference(init_time=init_time):
    global global_time, global_zong,jiange_shijian
    #print("global_time,global_zong=", global_time, global_zong)
    # 获取当前时间戳（精确到秒）
    current_timestamp = int(time.time())
    #print("jiange_shijian=",jiange_shijian)

    # 计算时间差（秒）
    time_difference = current_timestamp - init_time
    #print(time_difference)

    # 除以140取整和取余
    # quotient = time_difference // 140
    quotient1 = time_difference // int(global_time) % int(global_zong)
    remainder = time_difference % int(global_time)
    if (int(global_time) - remainder < jiange_shijian):
        #print("小于六十秒了，不行")
        return 9999

    return quotient1 + 1

#
# def sleep_class(class_phone):
#     while (True):
#         #print(class_phone, global_var)
#         if (int(class_phone) == int(calculate_time_difference())):
#             print("退出")
#             return
#         #print("等待")
#         time.sleep(1)


def sleep_class(class_phone,init_time=init_time):
    print("init_time=",init_time)
    while (True):
        #print(class_phone, global_var)
        if (int(class_phone) == int(calculate_time_difference(init_time))):
            print(f"当前第{class_phone}批，开始执行去了")
            print("退出")
            return
        #else:
            #print(f"当前第{class_phone}批，还得等")

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
        elements111 = d(text='推荐')
        # print(len(elements))
        if (len(elements) > 0):
            return "1"
        if (len(elements111) > 0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)


class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("dy业务0421-福袋，欢迎："+get_real_device_id())
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
        self.combo_box.addItems([ "通过搜索进入","通过关注进入"])

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
        self.label_from111_shoucang = QLabel('评论时间间隔：')
        self.label_from111_shoucang.setFixedWidth(80)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv111")
        if (shoucanggailv != None):
            self.shoucang_gailv = QLineEdit(shoucanggailv)
        else:
            self.shoucang_gailv = QLineEdit("50")
        self.shoucang_gailv.setFixedWidth(80)
        self.label_from222_shoucang = QLabel('秒')

        self.combo_box1 = QComboBox()

        # 2. 向下拉框添加选项
        # 方式1：逐个添加选项
        self.combo_box1.addItem("不评论")
        self.combo_box1.addItem("评论")

        self.combo_box1.currentTextChanged.connect(self.on_text_changed)


        self.label_from111_pinglun = QLabel('批内剩余时间判断：')
        self.label_from111_pinglun.setFixedWidth(100)

        pinglungailv = get_value_by_key_pkl("shuju_config.pkl", "pinglungailv111")
        if (pinglungailv != None):
            self.shoucang_pinglun = QLineEdit(pinglungailv)
        else:
            self.shoucang_pinglun = QLineEdit("100")
        self.shoucang_pinglun.setFixedWidth(80)
        self.label_from222_pinglun = QLabel('秒')

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
        self.label_from222_guanzhu = QLabel('%     ')
        self.label_from111_kongge222 = QLabel('           ')
        self.h_layout_disanhang = QHBoxLayout()
        self.h_layout_disanhang.addWidget(self.label_from111_kongge)

        self.h_layout_disanhang.addWidget(self.label_from111_pinglun) #self.combo_box1
        self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        self.h_layout_disanhang.addWidget(self.label_from222_pinglun)
        self.h_layout_disanhang.addWidget(self.label_from111_shoucang)
        self.h_layout_disanhang.addWidget(self.shoucang_gailv)
        self.h_layout_disanhang.addWidget(self.label_from222_shoucang)
        self.h_layout_disanhang.addWidget(self.combo_box1)
        # self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        # self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        # self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        self.h_layout_disanhang.addWidget(self.label_from111_kongge222)

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

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment111")
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
        self.label_from111_kongge_guanzhu = QLabel('')
        self.label_from111_guanzhu = QLabel('批次数量设置:')
        self.label_from111_guanzhu.setFixedWidth(50)

        shoucanggailv888 = get_value_by_key_pkl("shuju_config.pkl", "guanzhuzhanghao")
        if (shoucanggailv888 != None):
            self.guanzhuzhanghao = QLineEdit(shoucanggailv888)
        else:
            self.guanzhuzhanghao = QLineEdit("6")
        self.guanzhuzhanghao.setFixedWidth(150)
        self.label_from222_guanzhu = QLabel('')

        self.label_from111_fudai = QLabel('主播配置:')
        self.label_from111_fudai.setFixedWidth(50)

        fudai = get_value_by_key_pkl("shuju_config.pkl", "fudai")
        if (fudai != None):
            self.fudai = QLineEdit(fudai)
        else:
            self.fudai = QLineEdit("广东夫妇")
        self.fudai.setFixedWidth(150)
        self.label_from222_fudai = QLabel('')

        self.h_layout_guanzhu1 = QHBoxLayout()
        self.h_layout_guanzhu1.addWidget(self.label_from111_kongge_guanzhu)
        self.h_layout_guanzhu1.addWidget(self.label_from111_guanzhu)
        self.h_layout_guanzhu1.addWidget(self.guanzhuzhanghao)
        self.h_layout_guanzhu1.addWidget(self.label_from222_guanzhu)

        self.h_layout_guanzhu1.addWidget(self.label_from111_fudai)
        self.h_layout_guanzhu1.addWidget(self.fudai)
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
        layout.addLayout(self.h_layout_kongge)
        # layout.addLayout(self.h_layout_dir)
        # layout.addLayout(self.h_layout_kongge1)
        # layout.addLayout(self.h_layout_dir_comment)
        # layout.addLayout(self.h_layout_kongge2)
        # layout.addLayout(self.h_layout_dir_gouwu)
        # layout.addLayout(self.h_layout_kongge8)
        layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge3)

        # layout.addLayout(self.h_layout)


        #
        # layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.h_layout_guanzhu1)
        layout.addLayout(self.h_layout_kongge6)
        layout.addLayout(self.h_layout_fudai_guanjianzi)
        layout.addLayout(self.h_layout_kongge5)
        layout.addLayout(self.h_layout_diwuhang)
        layout.addLayout(self.h_layout_kongge4)
        layout.addLayout(self.h_layout_disanhang)
        layout.addLayout(self.h_layout_kongge8)

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
        self.execute_button_reset_sys = QPushButton("一键脚本重启")
        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_reset_sys)
        self.button_gang.addWidget(self.execute_button_reset)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.execute_button_reset_sys.clicked.connect(self.execute_button_reset_sys_click)
        self.file_button.clicked.connect(self.showDialog)
        self.file_button_comment.clicked.connect(self.showDialog_comment)
        self.file_button_gouwu.clicked.connect(self.showDialog_gouwu)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.execute_button_delete.clicked.connect(self.execute_delete_button_clicked)
        layout.addLayout(self.button_gang)
        # layout.addWidget(self.execute_button_reset)

    # 处理文本变化事件
    def on_text_changed(self, selected_text):
        """
        选中文本变化时触发
        :param selected_text: 选中的选项文本（自动传入）
        """
        #self.event_label.setText(f"【文本变化事件】选中了：{selected_text}")
        file_path = "pinglun111.txt"
        print(f"当前：{selected_text}")
        if(selected_text == "评论"):
            # 方式A：使用x模式（Python 3.3+支持）
            if not os.path.exists(file_path):
                # 如果文件不存在，则创建文件
                with open(file_path, 'w') as file:
                    pass  # 这里不需要写入任何内容，只需要创建文件即可
        else:
            try:
                # 核心：删除指定路径的文件
                os.remove(file_path)
                print(f"文件 {file_path} 删除成功！")
            except FileNotFoundError:
                print(f"错误：文件 {file_path} 不存在，无需删除")
            except PermissionError:
                print(f"错误：没有权限删除文件 {file_path}")
            except Exception as e:
                print(f"删除失败：{e}")

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
                updata_pkl_config_mianban("file_path_comment111", selected_file)
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
    def execute_button_reset_sys_click(self):
            print("一键重启")

        #def restart_application():
            """
            一键重启当前 PyInstaller 打包的 EXE 程序
            :return: None
            """
            try:
                # 1. 获取当前程序的完整路径（兼容 PyInstaller 打包后的 EXE 路径）
                if getattr(sys, 'frozen', False):
                    # 打包后的 EXE 环境
                    current_exe_path = sys.executable  # 获取 EXE 完整路径
                else:
                    # 开发环境（方便测试）
                    current_exe_path = sys.argv[0]

                print(f"📌 准备重启应用：{current_exe_path}")

                # 2. 启动新的进程（detach 模式：脱离当前进程，避免被当前进程退出影响）
                # 创建新进程，不等待其执行完成
                subprocess.Popen(
                    [current_exe_path],  # 要启动的程序路径
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,  # Windows 下新建控制台（可选）
                    close_fds=True  # 关闭文件描述符，避免句柄泄漏
                )

                # 3. 短暂延迟（确保新进程启动成功），然后退出当前进程
                time.sleep(0.5)
                sys.exit(0)  # 退出当前进程

            except Exception as e:
                print(f"❌ 重启应用失败：{str(e)}")
                # 失败时不退出，让用户手动处理
                return


    def execute_button_clicked(self):
        global jiange_shijian
        jiange_shijian = int(self.shoucang_pinglun.text())
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
        updata_pkl_config_mianban("shoucanggailv111", self.shoucang_gailv.text())
        updata_pkl_config_mianban("guanzhugailv", self.shoucang_guanzhu.text())
        updata_pkl_config_mianban("dianzangailv", self.shoucang_dianzan.text())
        updata_pkl_config_mianban("pinglungailv111", self.shoucang_pinglun.text())
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
        thread = threading.Thread(target=self.thread_temp, args=(tasks,))
        # thread111 = threading.Thread(target=update_global_var, args=(global_time,global_zong))
        thread.start()
        # thread111.start()

    def thread_temp(self, tasks):
        print("self.selected_ids--->",self.selected_ids)
        init_time_2 = time.time()

        thread1 = threading.Thread(target=self.upload, args=(get_real_device_id(), self.selected_ids,))
        thread1.start()

        for serial in self.selected_ids:
            init_serial_logger(serial)
            #print("---------------->", get_value_by_key_pkl("config.pkl", serial))
            class_phone = get_value_by_key_pkl("config.pkl", serial)
            thread = threading.Thread(target=operate_device, args=(
            serial, class_phone, self.file_textbox.text(), self.file_textbox_comment.text(), tasks,
            self.run_time.text(), self.line_edit_from_search.text(), self.line_edit_to_search.text(),
            self.line_edit_from.text(), self.line_edit_to.text(), self.jiarenshurukuang.text(),
            self.shoucang_gailv.text(), self.shoucang_pinglun.text(), self.shoucang_dianzan.text(),
            self.shoucang_guanzhu.text(), self.huadongcishu_big.text(), self.file_textbox_gouwu.text(),
            self.radio_button3.isChecked(), self.guanzhuzhanghao.text(), self.fudai.text(),
            self.fudai_guanjianzi.text(), self.combo_box.currentText(), self.line_edit_from_search_shouye.text(),
            self.line_edit_to_search_shouye.text(),int(self.shoucang_gailv.text()),init_time_2))
            # 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
            # threads.append(thread)
            thread.start()
            #time.sleep(random.randint(3, 20))
            time.sleep(0.2)

        self.selected_ids = []
    def upload(self,computer,phones):
        product_key = "pk_cd37c0a9cd36bbe56db8b1c85fea4974"
        print("phones=",phones)
        phones = list(phones)
        heartbeat(product_key,computer,phones)

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
def calculate_centroid(box):
    """
    计算文本框的重心坐标（x均值，y均值）
    box格式：[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    """
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    centroid_x = sum(x_coords) / len(x_coords)
    centroid_y = sum(y_coords) / len(y_coords)
    return centroid_x, centroid_y


def get_lottery_remaining_time(ocr_result):
    """
    核心逻辑：
    1. 定位包含"后开奖"的文本项，计算其重心坐标
    2. 查找该文本左侧、同一水平的纯数字项
    3. 按x坐标从右到左排序，确定分钟/秒数
    """
    # 步骤1：定位"后开奖"文本项并计算重心
    target_item = None
    target_centroid_x = 0
    target_centroid_y = 0
    for item in ocr_result:
        text = item.get('text', '').strip()
        if "后开奖" in text:
            print("text=",text)
            target_item = item
            # 计算重心坐标
            target_centroid_x, target_centroid_y = calculate_centroid(item['box'])
            # 提取"后开奖"前的数字（比如"46后开奖"中的46），后续用于验证
            pre_num = re.findall(r'(\d{1,2})后开奖', text)
            target_pre_num = pre_num[0] if pre_num else ""
            break

    if not target_item:
        return "未检测到「后开奖」文本"

    # 步骤2：筛选符合条件的数字项
    # 条件：纯数字 + y轴与目标差≤20（同一水平） + x轴＜目标x（左侧）
    valid_nums = []
    num_pattern = re.compile(r'^\d{1,2}$')  # 仅匹配1-2位纯数字

    for item in ocr_result:
        text = item.get('text', '').strip()
        # 跳过非纯数字
        if not num_pattern.match(text):
            continue

        # 计算当前项重心
        curr_x, curr_y = calculate_centroid(item['box'])

        # 核心筛选：同一水平（y差≤20）+ 左侧（x更小）
        if abs(curr_y - target_centroid_y) <= 20 and curr_x < target_centroid_x:
            valid_nums.append({
                'text': text,
                'centroid_x': curr_x,
                'centroid_y': curr_y
            })
    print("valid_nums=",valid_nums)
    # 步骤3：处理有效数字项
    if not valid_nums:
        # 兜底：如果没有左侧数字，检查"后开奖"文本内的数字（如"46后开奖"）
        if target_pre_num:
            return f"开奖倒计时：0分{target_pre_num}秒（总计{int(target_pre_num)}秒）"
        return "未找到开奖倒计时数字"

    # 按x坐标从大到小排序（越靠右越接近"后开奖"）
    valid_nums.sort(key=lambda x: x['centroid_x'], reverse=True)

    # 确定分钟/秒数：最右侧=秒数，次右侧=分钟数
    seconds = int(valid_nums[0]['text'])
    minutes = int(valid_nums[1]['text']) if len(valid_nums) >= 2 else 0

    # 验证：如果"后开奖"前有数字，优先匹配为秒数（解决"46后开奖"的问题）
    if target_pre_num and str(seconds) != target_pre_num:
        # 若最右侧数字不是文本内的数字，替换为文本内数字
        seconds = int(target_pre_num)
        # 分钟取次右侧数字（如果有）
        minutes = int(valid_nums[0]['text']) if len(valid_nums) >= 1 else 0

    # 计算总秒数并格式化
    total_seconds = minutes * 60 + seconds
    print(f"开奖倒计时：{minutes}分{seconds}秒（总计{total_seconds}秒）")
    if(total_seconds >= 15 * 60 and total_seconds < 0 ):
        return -1
    return total_seconds


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
#ocr = OCRProcessor()

if __name__ == "__main__":
    thread111 = threading.Thread(target=clear_folder, args=(create_folder_on_current_disk(),))
    thread111.start()
    if os.path.exists("pause.txt"):
        os.remove("pause.txt")
    if os.path.exists("exit.txt"):
        os.remove("exit.txt")
    if os.path.exists("pinglun111.txt"):
        os.remove("pinglun111.txt")
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