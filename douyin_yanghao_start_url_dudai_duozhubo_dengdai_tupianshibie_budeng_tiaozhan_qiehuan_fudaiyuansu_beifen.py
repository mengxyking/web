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
import os
import time
import pickle
from datetime import datetime

import numpy as np
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
from paddleOCR_json_duixiang_0308 import OCRProcessor

# 全局变量（用于日志绑定设备serial）
global_var = {}
ocr1 = OCRProcessor(id=1)
ocr2 = OCRProcessor(id=2)
# ocr3 = OCRProcessor(id=3)
# ocr4 = OCRProcessor(id=4)
# ocr5 = OCRProcessor(id=5)

# 2. 创建全局锁（保证轮询时的线程安全）
ocr_lock = threading.Lock()
current_scroll_position = 0

# 抖音养号+微信加好友脚本
black_zhubo = []
alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()

# 1. 全局文件读取锁（保护多线程并发读取文件，避免系统句柄竞争）
file_read_lock = threading.Lock()

# 新增：日志打印函数（自动绑定设备serial，保证线程日志隔离）
def log_print(*args, serial="unknown", **kwargs):
    """
    带设备标识的日志打印函数
    :param args: 打印内容
    :param serial: 设备序列号（核心，区分不同设备日志）
    :param kwargs: 其他print参数（如end、sep）
    """
    # 拼接设备标识前缀
    prefix = f"[{serial}] "
    # 组合最终打印内容
    print_content = (prefix + " ".join(map(str, args)))
    # 执行打印（保留原print的所有特性）
    print(print_content, **kwargs)

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

def find_id_from_area_2(d, x1_1,x2_2, y1_1 ,y2_2, serial="unknown"):
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
        #log_print(x1, y1, x2, y2, serial=serial)

        if(x1_1 < x1 and x2 < x2_2 and y1_1 < y1 and y2 < y2_2 and y2 - y1 == x2 - x1 and x1 != 0 and y1 != 0 and resource_id == "" and text == "" and contentdesc == ""):
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # log_print(center_x,center_y, serial=serial)

            zuobiaodian.append((center_x,center_y))
    zuobiaodian = list(set(zuobiaodian))
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
        for iii in zuobiaodian:
           if(x1 != 0 and y1 != 0 and x1 < iii[0] < x2 and y1 < iii[1] < y2):
                log_print("x1, y1, x2, y2",x1, y1, x2, y2, serial=serial)
                resource_id = elem.get('resource-id', '')
                text = elem.get('text', '')
                contentdesc = elem.get('content-desc', '')
                # log_print(resource_id, text, contentdesc, serial=serial)
                if( text != "" or contentdesc != ""):
                    log_print("应该去掉",iii, serial=serial)
                    if(iii in zuobiaodian1):
                        zuobiaodian1.remove(iii)
    log_print("-----------", serial=serial)
    log_print(zuobiaodian1, serial=serial)
    return zuobiaodian1

def safe_load_image(image_path: str, serial="unknown") -> Optional[np.ndarray]:
    """
    线程安全的图片加载函数（适配不同大图、兼容中文路径）
    :param image_path: 任意图片路径（支持中文）
    :param serial: 设备序列号
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
            log_print(f"❌ 加载图片失败 {image_path}：{str(e)}", serial=serial)
            return None


def find_target_by_template(
        big_image_path: str,  # 待搜索的大图路径（每个线程可能不同）
        template_image_path: str,  # 目标模板小图路径
        threshold: float = 0.85,  # 匹配阈值（0-1，越高越精准）
        save_marked_image: bool = True,  # 是否保存标记后的图片
        show_image: bool = False,  # 是否显示标记后的图片
        serial="unknown"  # 新增：设备序列号
) -> tuple | None:
    """
    适配「多线程读取不同大图」的模板匹配函数（线程安全）
    功能：1. 在匹配位置绘制红色方块标记 2. 返回匹配值最高的目标位置
    """
    # 1. 线程安全加载图片（替代原cv2.imread）
    time.sleep(0.2)
    big_img = safe_load_image(big_image_path, serial=serial)
    template_img = safe_load_image(template_image_path, serial=serial)

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
            log_print(f"匹配位置：中心坐标({center_x}, {center_y})，匹配值：{match_value:.4f}", serial=serial)

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
        log_print(f"\n🏆 最佳匹配位置：中心坐标({best_match['center_x']}, {best_match['center_y']})，匹配值：{best_match['match_value']:.4f}", serial=serial)

        return (best_match["center_x"], best_match["center_y"])
    else:
        log_print(f"❌ 模板 {os.path.basename(template_image_path)} 未匹配到任何目标", serial=serial)
        return None


def find_target_in_template_folder(
        big_image_path: str,
        template_folder_path: str,
        threshold: float = 0.85,
        save_marked_image: bool = True,
        show_image: bool = False,
        serial="unknown"  # 新增：设备序列号
) -> tuple | None:
    """
    遍历指定文件夹内所有图片模板，依次匹配大图，找到第一个匹配成功的模板并返回坐标
    :param big_image_path: 大图路径
    :param template_folder_path: 模板小图所在文件夹路径
    :param threshold: 匹配阈值
    :param save_marked_image: 是否保存标记图
    :param show_image: 是否显示标记图
    :param serial: 设备序列号
    :return: 第一个匹配成功的坐标，全部失败返回None
    """
    # 1. 校验模板文件夹是否存在
    if not os.path.exists(template_folder_path):
        log_print(f"❌ 模板文件夹不存在：{template_folder_path}", serial=serial)
        return None

    # 2. 获取文件夹内所有图片文件（支持常见图片格式）
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
    template_files = []
    for file in os.listdir(template_folder_path):
        # 过滤非图片文件，忽略大小写
        if file.lower().endswith(image_extensions):
            template_files.append(os.path.join(template_folder_path, file))

    if not template_files:
        log_print(f"❌ 模板文件夹 {template_folder_path} 内未找到任何图片文件", serial=serial)
        return None

    log_print(f"\n📁 找到 {len(template_files)} 个模板文件，开始依次匹配...", serial=serial)
    log_print("template_files=",template_files, serial=serial)
    # 3. 遍历所有模板文件，依次匹配
    for idx, template_path in enumerate(template_files, 1):
        log_print(f"\n========== 正在匹配第 {idx}/{len(template_files)} 个模板：{os.path.basename(template_path)} ==========", serial=serial)
        try:
            # 执行匹配
            match_result = find_target_by_template(
                big_image_path=big_image_path,
                template_image_path=template_path,
                threshold=threshold,
                save_marked_image=save_marked_image,
                show_image=show_image,
                serial=serial
            )
            # 如果匹配成功，立即返回坐标
            if match_result is not None:
                log_print(f"\n✅ 匹配成功！使用模板：{os.path.basename(template_path)}，坐标：{match_result}", serial=serial)
                return match_result
        except Exception as e:
            log_print(f"❌ 匹配模板 {os.path.basename(template_path)} 时出错：{str(e)}", serial=serial)
            continue

    # 4. 所有模板都匹配失败
    log_print(f"\n❌ 所有 {len(template_files)} 个模板均未匹配到目标", serial=serial)
    return None


def get_top_line_and_del(file, serial="unknown"):
    # 获取锁
    with file_lock:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # log_print("----------------", serial=serial)
            # log_print(lines, serial=serial)
            if not lines:
                # log_print("lines为空", serial=serial)
                return None
            temp_str = lines[0].strip()  # 直接转换为字符串并去除换行符

        # 重新打开文件以写入，这里可以优化为在读取后不移除文件指针直接截断文件
        with open(file, 'w', encoding='utf-8') as f:
            # 写入除了第一行之外的所有行
            f.writelines(str(line).strip() + '\n' for i, line in enumerate(lines) if i != 0)
            # 或者使用更简洁的方式，但注意这种方式会保留原始行的换行符（如果需要去除，可以使用strip()）
            # f.writelines(lines[1:])  # 这将保留第二行及之后的换行符，如果需要去除每行的换行符，需要先strip()
    return temp_str


def create_folder_on_current_disk(serial="unknown"):
    # 获取当前代码文件所在的路径
    current_script_path = os.path.abspath(__file__)
    # 提取当前代码所在的磁盘（如 'C:\\' 或 'D:\\'）
    current_disk = os.path.splitdrive(current_script_path)[0] + os.sep
    # 拼接新建文件夹的路径（以磁盘根目录为例）
    folder_path = os.path.join(current_disk, "dy_temp")
    # 新建文件夹
    try:
        os.makedirs(folder_path)
        log_print(f"已在 {current_disk} 上成功创建文件夹：{folder_path}", serial=serial)
    except FileExistsError:
        log_print(f"文件夹 {folder_path} 已存在", serial=serial)
    except Exception as e:
        log_print(f"创建文件夹失败：{e}", serial=serial)
    return folder_path


def take_screenshot(d, serial="unknown"):
    try:
        SAVE_DIR = create_folder_on_current_disk(serial=serial)
        # 生成带时间戳的文件名，避免重复
        timestamp = time.strftime("%Y%m%d%H%M%S")
        save_path = os.path.join(SAVE_DIR, f"{timestamp}.png")
        # 截图并保存
        d.screenshot(save_path)
        log_print(f"截图已保存至：{save_path}", serial=serial)
        return save_path
    except BaseException as e:
        log_print("截图时，发生崩溃", str(e), serial=serial)
        return None


def get_device(serial):
    d = u2.connect(serial)
    d.watcher.remove()
    return d


def getPhotoPath(serial="unknown"):
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
        log_print(f"创建图片目录：{pic_path}", serial=serial)
    return pic_path


def photo(s, serial="unknown"):
    Ui_file_Name = str(int(time.time())) + "_" + str(s) + "_ui.png"
    path = getPhotoPath(serial=serial) + "/" + Ui_file_Name
    return path


def get_files_in_directory(directory_path, serial="unknown"):
    files = []
    try:
        # 创建一个 Path 对象
        path = Path(directory_path)

        # 检查路径是否存在且是一个目录
        if not path.exists() or not path.is_dir():
            log_print(f"The directory {directory_path} does not exist or is not a directory.", serial=serial)
            return files

        # 遍历目录中的所有文件并添加到列表中
        for file_path in path.iterdir():
            if file_path.is_file():
                files.append(file_path)
    except PermissionError:
        log_print(f"Permission denied to access {directory_path}.", serial=serial)

    return files  # 将 Path 对象转换为字符串列表


from pathlib import Path


def create_directory_if_not_exists(directory_path, serial="unknown"):
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True)
        log_print(f"Directory '{directory_path}' created.", serial=serial)
    else:
        log_print(f"Directory '{directory_path}' already exists.", serial=serial)


def create_file_if_not_exists(file_path, serial="unknown"):
    if not os.path.isfile(file_path):
        # 如果文件不存在，则创建它（这里只是创建一个空文件）
        with open(file_path, 'w') as file:
            file.write('')  # 或者你可以写入一些初始内容
        log_print(f"File '{file_path}' created.", serial=serial)
    else:
        log_print(f"File '{file_path}' already exists.", serial=serial)

    # 示例用法


def shell_neibu(cmd, serial="unknown"):
    log_print(f"执行shell命令：{cmd}", serial=serial)
    os.system(cmd)


def load_pkl(pklfile, serial="unknown"):
    with video_lock:
        if (os.path.exists(pklfile)):
            with open(pklfile, 'rb') as pkl_file:
                my_object111 = pickle.load(pkl_file)
                log_print(f"成功加载pkl文件：{pklfile}", serial=serial)
                return my_object111
        else:
            log_print(f"pkl文件不存在：{pklfile}", serial=serial)
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


def get_random_line_from_file(file_path, serial="unknown"):
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
            log_print(f"文件 {file_path} 为空", serial=serial)
            return None  # 或者抛出一个异常，表示文件为空
    except FileNotFoundError:
        log_print(f"文件 {file_path} 未找到。", serial=serial)
        return None
    except Exception as e:
        log_print(f"读取文件时发生错误: {e}", serial=serial)
        return None


def get_real_device_id(serial="unknown"):
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
        device_id = full_hash[:18]
        log_print(f"生成设备唯一标识：{device_id}", serial=serial)
        return device_id

    except Exception as e:
        err_id = f"ERR-{str(e)[:18]}"
        log_print(f"生成设备标识失败：{e}，返回默认值：{err_id}", serial=serial)
        return err_id


def encrypt_and_modify(shebeima, serial="unknown"):
    """对输入的字符串进行Base64编码，并在特定位置插入字符"""
    input_text = shebeima

    if not input_text:
        log_print("设备码为空，跳过加密", serial=serial)
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
    #log_print(final_str, serial=serial)
    return final_str


def judge(serial="unknown"):
    shebeima = get_real_device_id(serial=serial)
    final_str = encrypt_and_modify(shebeima, serial=serial)
    if (os.path.isfile(final_str)):
        log_print("设备验证通过", serial=serial)
        return True
    else:
        log_print("设备验证失败，需要联系管理员", serial=serial)
        return False


start_time = datetime.now()

# 补充缺失的updata_pkl函数（原代码引用但未定义）
def updata_pkl(pkl_path, key, value, serial="unknown"):
    """更新pkl文件中的指定键值对"""
    try:
        data = {}
        if os.path.exists(pkl_path):
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
        data[key] = value
        with open(pkl_path, 'wb') as f:
            pickle.dump(data, f)
        log_print(f"更新pkl文件 {pkl_path}：{key} = {value}", serial=serial)
    except Exception as e:
        log_print(f"更新pkl文件失败：{e}", serial=serial)

# 补充缺失的sleep_class函数（原代码引用但未定义）
def sleep_class(class_phone, init_time=0, serial="unknown"):
    """按手机分类执行休眠"""
    sleep_time = init_time or random.randint(1, 5)
    log_print(f"手机分类 {class_phone} 休眠 {sleep_time} 秒", serial=serial)
    time.sleep(sleep_time)

# 补充缺失的backToHome函数（原代码引用但未定义）
def backToHome(d, serial="unknown"):
    """返回抖音首页"""
    try:
        d.press("home")
        time.sleep(1)
        d.app_start(package_name="com.ss.android.ugc.aweme", stop=False)
        log_print("返回抖音首页成功", serial=serial)
    except Exception as e:
        log_print(f"返回抖音首页失败：{e}", serial=serial)

def operate_device(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                   swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, shipinhuadongcishu, gouwu,
                   shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, shouyehuadongxiao,
                   shouyehuadongda,pinglunshijianjiange,init_time_2):
    result_j = judge(serial=serial)
    if (result_j == False):
        log_print("当前需要联系管理员", serial=serial)
        return

    count_zong = 0
    while (True):
        try:
            log_print("while------------", serial=serial)
            result = duozhubo(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big,
                              swipe_small,
                              swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,
                              shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi,
                              jinrufangshi, shouyehuadongxiao, shouyehuadongda,pinglunshijianjiange,init_time_2)
            if (result == "88"):
                log_print("运行结束", serial=serial)
                filepath = './shuju/' + serial + ".pkl"
                log_print("filepath-->", filepath, serial=serial)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束", serial=serial)
                    updata_pkl(filepath, "进行的任务", "空闲", serial=serial)
                    log_print("shifouguanbidouyin=", shifouguanbidouyin, serial=serial)
                if (shifouguanbidouyin == True):
                    log_print("开始执行关闭退出抖音", serial=serial)
                    cmd = f"adb -s {serial} shell input keyevent 4"
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)

                return
            if (result == "99"):
                log_print("运行结束", serial=serial)
                filepath = './shuju/' + serial + ".pkl"
                log_print("filepath-->", filepath, serial=serial)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束", serial=serial)
                    updata_pkl(filepath, "进行的任务", "空闲", serial=serial)
                if (shifouguanbidouyin == True):
                    log_print("开始执行关闭退出抖音", serial=serial)
                    cmd = f"adb -s {serial} shell input keyevent 4"
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)
                    time.sleep(0.5)
                    shell_neibu(cmd, serial=serial)
                return
            count_zong += 1
        except BaseException as ee:
            log_print("崩溃了", ee, serial=serial)
            error_info = traceback.format_exc()
            log_print(serial, "--------", "完整错误信息:", serial=serial)
            log_print(error_info, serial=serial)
            operate_device(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big,
                           swipe_small,
                           swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, shipinhuadongcishu, gouwu,
                           shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi,
                           shouyehuadongxiao, shouyehuadongda,pinglunshijianjiange,init_time_2)


def random_click_view(d, view, serial="unknown"):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left) + random.randint(2, 15)
    random_y = int(bottom) + random.randint(2, 15)
    log_print("开始点击", serial=serial)
    log_print(random_x, random_y, serial=serial)

    d.click(random_x, random_y)


def check_time_difference(interval_seconds, serial="unknown"):
    if (interval_seconds == 0):
        return False
    # 获取当前时间
    end_time = datetime.now()
    # 计算时间差（以秒为单位）
    time_difference = (end_time - start_time).total_seconds()
    log_print("time_difference=", time_difference, serial=serial)
    # 如果时间差大于100秒，则返回True，否则返回False
    return time_difference > interval_seconds


# 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def duozhubo(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
             swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu,
             shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
             shouyehuadongda,pinglunshijianjiange,init_time_2):
    if (len(fudai) > 0):
        fudai_list = str(fudai).split("/")
        zhubo_len = len(fudai_list)
        i = 0
        while (True):
            result_main = 0

            log_print(serial,"--------","应该进入的直播间", fudai_list[i], serial=serial)
            try:
                result_main = main(serial, class_phone, search_path, comment_path, task, run_time, change_small,
                                   chang_big, swipe_small, swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,
                                   count_zong, shipinhuadongcishu, gouwu, shifouguanbidouyin, guanzhuzhanghao,
                                   fudai_list[i], fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
                                   shouyehuadongda,pinglunshijianjiange,init_time_2)
            except:
                error_info = traceback.format_exc()
                log_print(serial,"--------","完整错误信息:", serial=serial)
                log_print(error_info, serial=serial)

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
                log_print("55 代表的意思是 中断了，意外出来了，还得重新试错", serial=serial)

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


def swipe_along_bezier(d, start_point, end_point, control_points=None, steps=15, duration=0.3, serial="unknown"):
    """
    沿着贝塞尔曲线滑动

    参数:
    - d: uiautomator2设备实例
    - start_point: 起点坐标 (x, y)
    - end_point: 终点坐标 (x, y)
    - control_points: 控制点坐标列表
    - steps: 生成的轨迹点数量
    - duration: 滑动持续时间(秒)
    - serial: 设备序列号
    """
    # 生成贝塞尔曲线上的点
    points = bezier_curve(start_point, end_point, control_points, steps)

    # 计算每个步骤的间隔时间
    interval = duration / len(points)

    # 按下起点
    d.swipe_points(points, duration=interval)
    log_print(f"执行贝塞尔曲线滑动：起点{start_point} 终点{end_point}", serial=serial)


def beisaier(d, Diract="up", serial="unknown"):
    # 获取屏幕尺寸
    width, height = d.window_size()
    log_print(f"屏幕尺寸：宽{width} 高{height}", serial=serial)

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
    swipe_along_bezier(d, start_point, end_point, control_points, steps=15, duration=0.3, serial=serial)

    # 等待一下
    time.sleep(1)


def find_id_from_area(d, x1, y1, serial="unknown"):
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
        log_print(f"找到面积最小的控件（面积：{min_area}），中心坐标({min_center_x},{min_center_y})", serial=serial)
        log_print(f"控件信息：resource-id={min_elem.get('resource-id', '')}，bounds={min_elem.get('bounds')}", serial=serial)
        return min_elem.get('resource-id', '')
    else:
        log_print("未找到符合条件的控件", serial=serial)


def main(serial, class_phone, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
         swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu,
         shifouguanbidouyin, guanzhuzhanghao, fudai, fudai_guanjianzi, jinrufangshi, zhubo_len, shouyehuadongxiao,
         shouyehuadongda,pinglunshijianjiange,init_time_2):
    #global ocr
    try:
        pinglunshijianjiange = int(pinglunshijianjiange)
        new_flag = "older"
        log_print(serial + "---------", "fudai,fudai_guanjianzi=", fudai, fudai_guanjianzi, serial=serial)
        if (len(task) == 0):
            log_print("0", serial=serial)
            return
        log_print(serial + "---------", "1", serial=serial)

        d = get_device(serial)
        log_print("2", serial=serial)
        # d.watcher.when("以后再说").click()
        d.watcher.when("忽略").click()
        d.watcher.when("残忍放弃").click()
        d.watcher.start()
        pineisuijishijian_xiao = int(change_small)
        pineisuijishijian_da = int(chang_big)
        log_print(serial + "---------", "class_phone=", class_phone, serial=serial)
        if (str(class_phone).count("-") < 1):
            log_print(serial + "---------", "当前手机没有分组", serial=serial)
            return "99"
        log_print("3", serial=serial)
        sleep_time_phone = 3
        if (str(class_phone).count("-") > 1):
            temp_time = str(class_phone).split("-")[2]
            if (temp_time.isdigit()):
                sleep_time_phone = int(temp_time)
                log_print(serial + "---------", "sleep_time_phone=", sleep_time_phone, serial=serial)
        log_print("4", serial=serial)

        if (str(class_phone).count("-") > 2):
            temp_cc = str(class_phone).split("-")[3]
            if (str(temp_cc).count("新") > 0):
                new_flag = "newer"
        log_print(serial + "---------", "new_flag=", new_flag, serial=serial)

        class_phone = str(class_phone).split("-")[0]
        log_print(serial + "---------", "class_phone---->", class_phone, serial=serial)
        sleep_class(class_phone, init_time=init_time_2, serial=serial)
        log_print(serial + "---------", "当前会等=", sleep_time_phone, serial=serial)
        time.sleep(sleep_time_phone)
        updata_pkl("./shuju/" + serial + ".pkl", "执行状态", "运行中", serial=serial)
        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "进入直播间", serial=serial)
        if ("fudai" in task):
            time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme",stop=False)
            backToHome(d, serial=serial)
            time.sleep(3)
            count_temp = random.randint(int(shouyehuadongxiao), int(shouyehuadongda))
            for i in range(count_temp):
                beisaier(d, serial=serial)
                time.sleep(random.randint(1, 10))

            log_print(serial + "---------", "global_var----->", global_var, serial=serial)

            if (jinrufangshi == "通过关注进入"):
                if (d(text="关注").exists(timeout=3)):
                    # d(text="关注").click()
                    random_click_view(d, d(text="关注").info, serial=serial)
                    time.sleep(3)
                else:
                    return "55"

                bbb = 0
                while (True):
                    if (d(textContains=fudai).exists(timeout=1)):
                        # d(textContains=fudai).click()
                        random_click_view(d, d(textContains=fudai).info, serial=serial)
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
    except Exception as e:
        log_print(f"main函数执行异常：{e}", serial=serial)
        traceback.print_exc()
        return "55"

# 主函数入口（测试用）
if __name__ == "__main__":
    # 示例：执行单个设备的任务
    test_serial = "your_device_serial"  # 替换为实际设备序列号
    operate_device(
        serial=test_serial,
        class_phone="test-1-3-新",
        search_path="./search",
        comment_path="./comment",
        task=["fudai"],
        run_time=60,
        change_small=5,
        chang_big=10,
        swipe_small=1,
        swipe_big=3,
        swipe_count=10,
        shoucang=True,
        pinglun=True,
        dianzan=True,
        guanzhu=True,
        shipinhuadongcishu=5,
        gouwu=False,
        shifouguanbidouyin=True,
        guanzhuzhanghao="test_account",
        fudai="test_zhubo1/test_zhubo2",
        fudai_guanjianzi="test_keyword",
        jinrufangshi="通过关注进入",
        shouyehuadongxiao=2,
        shouyehuadongda=5,
        pinglunshijianjiange=10,
        init_time_2=3
    )