import base64
import hashlib
import json
import platform
import shutil
import sys
import threading
import random
import uuid
from datetime import datetime

import requests
import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
import os
import pickle
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding
#抖音养号+微信加好友脚本
shuju_config_file_name = "shuju_config_jiaoyou.pkl"
video_lock = threading.Lock()
_pause_event = threading.Event()   # set = 暂停中
_stop_event  = threading.Event()   # set = 已停止
AES_KEY = b'OnlineStats_2026'  # 必须和服务端一致，16字节
def check_pause_stop():
    """在自然间隙检查暂停/停止，返回 True 表示需要停止。"""
    while _pause_event.is_set():
        if _stop_event.is_set():
            return True
        time.sleep(0.3)
    return _stop_event.is_set()

def get_device(serial):
    #d = ""
    #print("之前的d", d)
    #print(f"正在连接设备: {serial}")
    d = u2.connect(serial)
    d.watcher.remove()
    return d
from pathlib import Path


def create_directory_if_not_exists(directory_path):
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

def shell_neibu(cmd):
    os.system(cmd)

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
def random_boolean_with_probability(probability):
    """
    根据给定的概率返回 True 或 False。

    :param probability: 成功的概率（0 到 1 之间的浮点数）
    :return: 如果随机数小于或等于概率则返回 True，否则返回 False
    """
    if not (1 <= probability <= 100):
        raise ValueError("概率必须在 0 到 1 之间")

    return random.random()*100 <= probability


def get_random_line_from_file(file_path):
    """
    从指定的文本文件中随机选择并返回一行。
    自动尝试多种编码（utf-8-sig / gbk / gb18030 / utf-8），失败时返回空字符串。
    """
    for enc in ("utf-8-sig", "gbk", "gb18030", "utf-8", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc) as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if lines:
                return random.choice(lines)
            print(f"文件 {file_path} 内容为空。")
            return ""
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return ""
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
            return ""
    return ""

start_time = datetime.now()
def operate_device(serial):
    count_zong = 0
    while(True):
        if _stop_event.is_set():
            print(f"[{serial}] 收到停止信号，退出")
            return
        try:
            result = main(serial)
            if result == "stop":
                return
            if (result == "88"):
                print("运行结束")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束")
                    updata_pkl(filepath, "进行的任务", "空闲")
                    print("shifouguanbidouyin=",1)
                if(True == True):
                    print("开始执行关闭退出抖音")
                    #cmd = f"adb -s {serial} shell input keyevent 3"   am force-stop
                    cmd = f"adb -s {serial} shell am force-stop com.ss.android.ugc.aweme"

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
                return
            count_zong += 1
        except BaseException as ee:
            import traceback
            print("崩溃了", ee)
            traceback.print_exc()
            operate_device(serial)

def check_time_difference(interval_seconds):
    print("interval_seconds=",interval_seconds)
    if(interval_seconds == 0):
        print("interval_seconds = 0")
        return False
    # 获取当前时间
    end_time = datetime.now()
    # 计算时间差（以秒为单位）
    time_difference = (end_time - start_time).total_seconds()
    print("time_difference=",time_difference)
    # 如果时间差大于100秒，则返回True，否则返回False
    print(time_difference , interval_seconds)
    print(float(time_difference) > float(interval_seconds))
    return float(time_difference) > float(interval_seconds)
#搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注

def is_hit(probability):
    """
    根据概率随机判断是否命中
    :param probability: 命中概率（数字，如 50 代表 50%）
    :return: True=命中, False=未命中
    """
    # 概率小于等于 0，直接不命中
    if probability <= 0:
        return False
    # 概率大于等于 100，直接命中
    if probability >= 100:
        return True

    # 生成 1~100 的随机数，随机数 ≤ 概率 就代表命中
    random_num = random.randint(1, 100)
    return random_num <= probability

def main(serial):
    # 从配置文件读取页面显示的七个输入框的值
    run_time           = int(get_value_by_key_pkl(shuju_config_file_name, "jiaobenyunxingshichang") or "0")
    swipe_small        = float(get_value_by_key_pkl(shuju_config_file_name, "huadongjiangexiao") or "8")
    swipe_big          = float(get_value_by_key_pkl(shuju_config_file_name, "huadongjiangeda") or "30")
    swipe_count        = int(get_value_by_key_pkl(shuju_config_file_name, "huadongcishuxiao") or "8") #jiaobenyunxingshichang
    shipinhuadongcishu = int(get_value_by_key_pkl(shuju_config_file_name, "huadongcishuda") or "20")
    zonggailv          = int(get_value_by_key_pkl(shuju_config_file_name, "zonggailv") or "50")
    comment_path       = get_value_by_key_pkl(shuju_config_file_name, "file_path_comment1") or ""
    memo_raw           = get_value_by_key_pkl(shuju_config_file_name, "memo_text") or ""
    memo_lines         = [l.strip() for l in memo_raw.splitlines() if l.strip()]

    jiaobenyunxingshichang = get_value_by_key_pkl(shuju_config_file_name, "jiaobenyunxingshichang") or "2"

    d = get_device(serial)
    #d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    if(str(jiaobenyunxingshichang).isdigit()):
        jiaobenyunxingshichang = jiaobenyunxingshichang
    else:
        jiaobenyunxingshichang = 2
    while(True):
        if check_pause_stop():
            return "stop"

        print(d.app_current())

        ids = {}
        allData = d.dump_hierarchy()
        if(str(allData).count("com.yanzhiyu.dahai") > 0): #com.yanzhiyu.dahai:id/et_content_container
            print("当前是附近陌约")
            ids["txt_top_center"] = "com.yanzhiyu.dahai:id/ll_top"
            ids["et_content_container"] = "com.yanzhiyu.dahai:id/et_content_container" #com.yanzhiyu.dahai:id/et_content_container
            ids["et_content_container_2"] = "com.yanzhiyu.dahai:id/et_content_container"  #id="com.yanzhiyu.dahai:id/tv_next"
            ids["tv_next"] = "com.yanzhiyu.dahai:id/tv_next" #com.huanyou.fjxasn:id/tv_content
            ids["tv_content"] = "com.yanzhiyu.dahai:id/tv_content"
        elif(str(allData).count("com.huanyou.fjxasn") > 0):
            print("当前是寻爱")

            ids["txt_top_center"] = "com.huanyou.fjxasn:id/ll_top"
            ids["et_content_container"] = "com.huanyou.fjxasn:id/tv_hint"  # com.yanzhiyu.dahai:id/et_content_container
            ids["et_content_container_2"] = "com.huanyou.fjxasn:id/et_content_container"  # id="com.yanzhiyu.dahai:id/tv_next"
            ids["tv_next"] = "com.huanyou.fjxasn:id/tv_next"
            ids["tv_content"] = "com.huanyou.fjxasn:id/tv_content"

        elif (str(allData).count("com.pangdaishu.huanyou") > 0):
            print("当前是欢友")
            ids["txt_top_center"] = "com.pangdaishu.huanyou:id/ll_top"
            ids["et_content_container"] = "com.pangdaishu.huanyou:id/tv_hint"  # com.yanzhiyu.dahai:id/et_content_container
            ids["et_content_container_2"] = "com.pangdaishu.huanyou:id/et_content_container"  # id="com.yanzhiyu.dahai:id/tv_next"
            ids["tv_next"] = "com.pangdaishu.huanyou:id/tv_next"
            ids["tv_content"] = "com.pangdaishu.huanyou:id/tv_content"
        elif (str(allData).count("com.huanyou.haituan") > 0):
            print("当前是附近寻欢")
            ids["txt_top_center"] = "com.huanyou.haituan:id/ll_top"
            ids["et_content_container"] = "com.huanyou.haituan:id/et_content_container"  # com.yanzhiyu.dahai:id/et_content_container
            ids["et_content_container_2"] = "com.huanyou.haituan:id/et_content_container"  # id="com.yanzhiyu.dahai:id/tv_next"
            ids["tv_next"] = "com.huanyou.haituan:id/tv_next"
            ids["tv_content"] = "com.huanyou.haituan:id/tv_content"
        else:
            print("当前不在三个APP里面")
            continue


        if (not d(resourceId=ids["txt_top_center"]).exists(timeout=3)):
            print("当前不在会话页面，请移步到会话页面")
            continue

        bbb = d(resourceId=ids["tv_content"])
        print(f"当前有{len(bbb)}条对话")

        if(len(bbb) >= 3):
            print("当前发过消息，跳过")
        else:

            print("当前在会话页面")
            print(f"每个会话发{jiaobenyunxingshichang}条消息")
            memo_index = 0
            for i in range(int(jiaobenyunxingshichang)):
                print(f"-------------{i+1}-----------------")
                if (d(resourceId=ids["et_content_container"]).exists(timeout=3)):  # com.huanyou.fjxasn:id/et_content_container
                    print("当前有会话框111")
                    random_click_view(d, d(resourceId=ids["et_content_container"]))
                    time.sleep(0.5)
                    send_text = memo_lines[memo_index % len(memo_lines)] if memo_lines else "111"
                    memo_index += 1
                    print("发送内容:", send_text)
                    d.clear_text()
                    d.send_keys(send_text)
                    time.sleep(0.5)

                    if (d(resourceId=ids["et_content_container_2"]).exists(timeout=3)):
                        print("当前输入了，找发送按钮")
                        el = d(resourceId=ids["et_content_container_2"])
                        el_y = el.info["bounds"]["top"] + 50
                        screen_w, _ = d.window_size()
                        print(screen_w - 100, el_y)
                        d.click(screen_w - 100, el_y)
                        time.sleep(0.5)
                    else:
                        continue
                time.sleep(0.5)
        if (d(resourceId=ids["tv_next"]).exists(timeout=3)):
            print("you 下一个，点击下一个")
            random_click_view(d,d(resourceId=ids["tv_next"]))
        else:
            print("mei you 下一个，直接退出")
            return
def random_click_view(d, view):
    """
    根据控件 bounds，在控件中心附近安全范围内随机点击
    :param d: 设备操作对象（如 adbutils、uiautomator2）
    :param view: 控件信息字典，包含 bounds: {top, left, right, bottom}
    """
    # 取出控件四个边界
    view = view.info
    top = int(view["bounds"]["top"])
    left = int(view["bounds"]["left"])
    right = int(view["bounds"]["right"])
    bottom = int(view["bounds"]["bottom"])

    # 计算控件中心点坐标
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    # 计算控件宽高，用于限制随机偏移范围（不超出控件）
    width = right - left
    height = bottom - top

    # 安全偏移：最大偏移量 = 宽/高的 40%，保证不会点出控件
    max_offset_x = int(width * 0.4)
    max_offset_y = int(height * 0.4)

    # 中心附近随机偏移（至少偏移2像素，避免死点）
    random_x = center_x + random.randint(-max_offset_x, max_offset_x)
    random_y = center_y + random.randint(-max_offset_y, max_offset_y)

    print(f"✅ 开始点击，坐标：({random_x}, {random_y})")
    d.click(random_x, random_y)


def comment(d,serial,comment_path):
    if(os.path.isfile(comment_path)):
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
    if (d(className='android.widget.EditText').exists(timeout=3)):
        print("点击评论")
        random_click_view(d, d(className='android.widget.EditText'))
        time.sleep(1.5)
    elif(d(text="作者仅允许自己评论").exists(timeout=3)):
        return "66"
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return "66"
    comment_t = get_random_line_from_file(comment_path)
    if not comment_t:
        print("评论内容为空，跳过评论")
        return "66"
    if (d(className='android.widget.EditText').exists(timeout=3)):
        print("点击评论")
        for tt in comment_t:
            d.send_keys(tt)
            time.sleep(0.1)
        time.sleep(1.5)
    elif(d(text="作者仅允许自己评论").exists(timeout=3)):
        return "66"
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return "66"

    time.sleep(1)

    if (d(text="发送").exists(timeout=2)):
        d(text="发送").click()
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)

    return "1"
def backToHome(d):
    dd =  0
    time.sleep(3)
    while(dd < 10):
        elements = d(text='首页')  # 获取所有文本为'some_text'的元素
        elements111 = d(text='推荐')
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        if (len(elements111) > 0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("dy业务")
        self.setWindowIcon(QIcon())
        self.setGeometry(100, 100, 650, 580)

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QWidget { font-family: "Microsoft YaHei", "Segoe UI", sans-serif; font-size: 13px; color: #333333; }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 3px 7px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus { border-color: #4096ff; }
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px 7px;
                background-color: white;
                color: #333333;
            }
            QTextEdit:focus { border-color: #4096ff; }
            QCheckBox { spacing: 6px; color: #333333; }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #1677ff;
                border-color: #1677ff;
            }
            QPushButton {
                background-color: #1677ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 16px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #4096ff; }
            QPushButton:pressed { background-color: #0958d9; }
            QTableWidget {
                border: 1px solid #e8e8e8;
                background-color: white;
                gridline-color: #f0f0f0;
                selection-background-color: #e6f4ff;
                selection-color: #333333;
                alternate-background-color: #fafbff;
            }
            QTableWidget::item { padding: 4px 6px; border: none; }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                border-right: 1px solid #e8e8e8;
                padding: 6px 8px;
                font-weight: bold;
                color: #555555;
                font-size: 12px;
            }
            QScrollBar:vertical { width: 8px; background: transparent; margin: 2px; }
            QScrollBar::handle:vertical { background: #c8c8c8; border-radius: 4px; min-height: 24px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollArea { border: 1px solid #e0e0e0; background-color: white; }
        """)

        self.titleLabel = QLabel("  手机列表")
        self.titleLabel.setFixedHeight(36)
        self.titleLabel.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #1677ff;
                background-color: #e8f3ff;
                border-left: 4px solid #1677ff;
                padding-left: 10px;
            }
        """)
        self.caozuo_tiel = QLabel("  操  作  区")
        self.caozuo_tiel.setFixedHeight(36)
        self.caozuo_tiel.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #389e0d;
                background-color: #f0fff0;
                border-left: 4px solid #52c41a;
                padding-left: 10px;
            }
        """)
        self.caozuo_config = QLabel("  脚本配置区")
        self.caozuo_config.setFixedHeight(36)
        self.caozuo_config.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #d4380d;
                background-color: #fff7f0;
                border-left: 4px solid #fa541c;
                padding-left: 10px;
            }
        """)

        # Table widget to display pkl file information
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(7)  # Increase column count for checkboxes
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"滑动统计"])
        self.table_widget.setColumnWidth(0,30)
        self.table_widget.setShowGrid(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        #self.table_widget.itemClicked.connect(self.on_item_clicked)
        #self.table_widget.setItem(2, 1, QTableWidgetItem(2))

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area.setFixedHeight(280)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setContentsMargins(15, 8, 15, 8)
        self.horizontal_layout.setSpacing(8)
        #self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.setFixedWidth(70)
        self.radio_button_select.setStyleSheet("""
            QPushButton { background-color: white; color: #1677ff; border: 1px solid #1677ff; border-radius: 4px; padding: 4px 10px; }
            QPushButton:hover { background-color: #e6f4ff; }
            QPushButton:pressed { background-color: #bae0ff; }
        """)
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("dy关注养号")
        self.radio_button1.setChecked(True)
        self.radio_button2 = QCheckBox("dy购物")
        self.radio_button2.setChecked(False)
        self.radio_button3 = QCheckBox("养号之后是否关闭抖音")
        self.radio_button3.setChecked(True)
        self.radio_button4 = QCheckBox("关注")
        self.radio_button4.setChecked(False)
        self.radio_button6 = QCheckBox("抢福袋")
        self.radio_button6.setChecked(False)
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addSpacing(20)
        #self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addSpacing(10)
        #self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addStretch()

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
          # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('视频滑动间隔时间')
        self.label_from.setFixedWidth(100)

        huadongjiangexiao = get_value_by_key_pkl(shuju_config_file_name, "huadongjiangexiao")
        if (huadongjiangexiao != None):
            self.line_edit_from = QLineEdit(huadongjiangexiao)
        else:
            self.line_edit_from = QLineEdit("8")
        self.line_edit_from.setFixedWidth(60)

        self.label_to = QLabel('至')
        self.label_to.setFixedWidth(15)

        huadongjiangeda = get_value_by_key_pkl(shuju_config_file_name, "huadongjiangeda")
        if (huadongjiangeda != None):
            self.line_edit_to = QLineEdit(huadongjiangeda)
        else:
            self.line_edit_to = QLineEdit("30")
        self.line_edit_to.setFixedWidth(60)
        self.label_seconds = QLabel('秒内随机', self)

        self.label_from111 = QLabel('视频滑动次数')

        huadongcishuxiao = get_value_by_key_pkl(shuju_config_file_name, "huadongcishuxiao")
        if (huadongcishuxiao != None):
            self.jiarenshurukuang = QLineEdit(huadongcishuxiao)
        else:
            self.jiarenshurukuang = QLineEdit("8")
        self.jiarenshurukuang.setFixedWidth(60)
        self.label_from222 = QLabel('至')
        self.label_from222.setFixedWidth(15)

        huadongcishuda = get_value_by_key_pkl(shuju_config_file_name, "huadongcishuda")
        if (huadongcishuda != None):
            self.huadongcishu_big = QLineEdit(huadongcishuda)
        else:
            self.huadongcishu_big = QLineEdit("20")
        self.huadongcishu_big.setFixedWidth(60)
        self.label_fromci = QLabel('次')




        self.label_from_time = QLabel('每个会话条数')
        self.label_from_time.setFixedWidth(100)

        yunxingshichang = get_value_by_key_pkl(shuju_config_file_name, "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("0")
        self.run_time.setFixedWidth(90)
        self.label_to_time = QLabel('分钟 (0为一直运行)')

        sousuocipinlvxiao = get_value_by_key_pkl(shuju_config_file_name, "sousuocipinlvxiao")
        self.line_edit_from_search = QLineEdit(sousuocipinlvxiao if sousuocipinlvxiao else "3")
        sousuocipinlvda = get_value_by_key_pkl(shuju_config_file_name, "sousuocipinlvda")
        self.line_edit_to_search = QLineEdit(sousuocipinlvda if sousuocipinlvda else "8")
        zonggailv_val = get_value_by_key_pkl(shuju_config_file_name, "zonggailv")
        self.zonggailv = QLineEdit(zonggailv_val if zonggailv_val else "50")
        self.zonggailv.setFixedWidth(90)

        self.h_layout_diyihang = QHBoxLayout()
        self.h_layout_diyihang.setContentsMargins(15, 6, 15, 6)
        self.h_layout_diyihang.addWidget(self.label_from_time)
        self.h_layout_diyihang.addWidget(self.run_time)
        #self.h_layout_diyihang.addWidget(self.label_to_time)
        self.h_layout_diyihang.addSpacing(80)
        # self.h_layout_diyihang.addWidget(QLabel('xxxxxx2  '))
        # self.h_layout_diyihang.addWidget(self.zonggailv)
        # self.h_layout_diyihang.addWidget(QLabel('%'))
        self.h_layout_diyihang.addStretch()
        shoucanggailv = get_value_by_key_pkl(shuju_config_file_name, "shoucanggailv")
        self.shoucang_gailv = QLineEdit(shoucanggailv if shoucanggailv else "50")
        pinglungailv = get_value_by_key_pkl(shuju_config_file_name, "pinglungailv")
        self.shoucang_pinglun = QLineEdit(pinglungailv if pinglungailv else "50")
        dianzangailv = get_value_by_key_pkl(shuju_config_file_name, "dianzangailv")
        self.shoucang_dianzan = QLineEdit(dianzangailv if dianzangailv else "50")
        guanzhugailv = get_value_by_key_pkl(shuju_config_file_name, "guanzhugailv")
        self.shoucang_guanzhu = QLineEdit(guanzhugailv if guanzhugailv else "50")


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

        self.h_layout.setSpacing(6)
        self.h_layout.setContentsMargins(15, 6, 15, 6)

        file_temp_path = get_value_by_key_pkl(shuju_config_file_name, "file_path")
        self.file_textbox = QLineEdit(file_temp_path if file_temp_path else "请输入搜索文件路径")
        self.file_button = QPushButton("选择文件", self)
        self.file_button.hide()

        #以下是评论文件选择器
        self.h_layout_dir_comment = QHBoxLayout()
        self.h_layout_dir_comment.setContentsMargins(15, 6, 15, 6)
        self.label_file_comment = QLabel("请选择评论文件路径:")
        self.label_file_comment.setFixedWidth(150)
        self.h_layout_dir_comment.addWidget(self.label_file_comment)

        file_temp_path_comment = get_value_by_key_pkl(shuju_config_file_name, "file_path_comment1")
        if (file_temp_path_comment != None):
            self.file_textbox_comment = QLineEdit(file_temp_path_comment)
        else:
            self.file_textbox_comment = QLineEdit("请输入评论文件路径")
        self.h_layout_dir_comment.addWidget(self.file_textbox_comment)
        self.file_button_comment = QPushButton("选择文件", self)
        self.file_button_comment.setStyleSheet("""
            QPushButton { background-color: white; color: #1677ff; border: 1px solid #1677ff; border-radius: 4px; padding: 4px 12px; }
            QPushButton:hover { background-color: #e6f4ff; }
            QPushButton:pressed { background-color: #bae0ff; }
        """)
        self.h_layout_dir_comment.addWidget(self.file_button_comment)

        # 隐藏评论文件路径行
        self.label_file_comment.hide()
        self.file_textbox_comment.hide()
        self.file_button_comment.hide()

        file_temp_path_gouwu = get_value_by_key_pkl(shuju_config_file_name, "file_path_gouwu")
        self.file_textbox_gouwu = QLineEdit(file_temp_path_gouwu if file_temp_path_gouwu else "")
        self.file_button_gouwu = QPushButton("选择文件", self)
        self.file_button_gouwu.hide()

        gz_val = get_value_by_key_pkl(shuju_config_file_name, "guanzhuzhanghao")
        self.guanzhuzhanghao = QLineEdit(gz_val if gz_val else "广东夫妇")
        fudai_val = get_value_by_key_pkl(shuju_config_file_name, "fudai")
        self.fudai = QLineEdit(fudai_val if fudai_val else "广东夫妇")

        # 备注多行输入框
        self.memo_title = QLabel("  语句输入区")
        self.memo_title.setFixedHeight(36)
        self.memo_title.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #531dab;
                background-color: #f9f0ff;
                border-left: 4px solid #722ed1;
                padding-left: 10px;
            }
        """)

        memo_val = get_value_by_key_pkl(shuju_config_file_name, "memo_text")
        self.memo_edit = QTextEdit()
        self.memo_edit.setAcceptRichText(False)
        self.memo_edit.setPlaceholderText("在此输入备注内容，回车可换行...")
        self.memo_edit.setMinimumHeight(130)
        if memo_val:
            self.memo_edit.setPlainText(memo_val)

        self.h_layout_memo = QVBoxLayout()
        self.h_layout_memo.setContentsMargins(15, 6, 15, 6)
        self.h_layout_memo.addWidget(self.memo_edit)


        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        central_widget.setFixedWidth(650)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.caozuo_config)
        layout.addLayout(self.h_layout_dir_comment)
        layout.addLayout(self.h_layout_diyihang)
        #layout.addLayout(self.h_layout)
        layout.addWidget(self.memo_title)
        layout.addLayout(self.h_layout_memo)

        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(30000)
        # self.refresh_pkl_files_test()
        # self.timer.timeout.connect(self.refresh_pkl_files_test)
        # self.timer.start(10000)

        # Initial load
        self.refresh_pkl_files()
        self.button_gang = QHBoxLayout()
        self.button_gang.setContentsMargins(15, 8, 15, 8)
        self.button_gang.setSpacing(10)
        self.execute_button = QPushButton("执行")
        self.execute_button.setFixedHeight(32)
        self.execute_button.setStyleSheet("""
            QPushButton { background-color: #52c41a; color: white; border: none; border-radius: 4px; padding: 5px 20px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #73d13d; }
            QPushButton:pressed { background-color: #389e0d; }
        """)
        self.button_gang.addWidget(self.execute_button)

        self.execute_button_delete = QPushButton("保存配置")
        self.execute_button_delete.setFixedHeight(32)
        self.execute_button_delete.setStyleSheet("""
            QPushButton { background-color: #1677ff; color: white; border: none; border-radius: 4px; padding: 5px 20px; font-size: 13px; }
            QPushButton:hover { background-color: #4096ff; }
            QPushButton:pressed { background-color: #0958d9; }
        """)


        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.setFixedHeight(32)
        self.execute_button_reset.setStyleSheet("""
            QPushButton { background-color: #8c8c8c; color: white; border: none; border-radius: 4px; padding: 5px 20px; font-size: 13px; }
            QPushButton:hover { background-color: #bfbfbf; }
            QPushButton:pressed { background-color: #595959; }
        """)


        self.pause_button = QPushButton("暂停")
        self.pause_button.setFixedHeight(32)
        self.pause_button.setStyleSheet("""
            QPushButton { background-color: #faad14; color: white; border: none; border-radius: 4px; padding: 5px 20px; font-size: 13px; }
            QPushButton:hover { background-color: #ffc53d; }
            QPushButton:pressed { background-color: #d48806; }
        """)
        self.button_gang.addWidget(self.pause_button)
        self.button_gang.addWidget(self.execute_button_delete)
        self.button_gang.addWidget(self.execute_button_reset)

        self.stop_button = QPushButton("停止")
        self.stop_button.setFixedHeight(32)
        self.stop_button.setStyleSheet("""
            QPushButton { background-color: #ff4d4f; color: white; border: none; border-radius: 4px; padding: 5px 20px; font-size: 13px; }
            QPushButton:hover { background-color: #ff7875; }
            QPushButton:pressed { background-color: #cf1322; }
        """)
        #self.button_gang.addWidget(self.stop_button)

        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.file_button.clicked.connect(self.showDialog)
        self.file_button_comment.clicked.connect(self.showDialog_comment)
        self.file_button_gouwu.clicked.connect(self.showDialog_gouwu)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.execute_button_delete.clicked.connect(self.save_config_clicked)
        self.pause_button.clicked.connect(self.pause_resume_clicked)
        self.stop_button.clicked.connect(self.stop_clicked)
        layout.addLayout(self.button_gang)
        #layout.addWidget(self.execute_button_reset)

    def pause_resume_clicked(self):
        if _pause_event.is_set():
            _pause_event.clear()
            print("开始")
            self.pause_button.setText("暂停")
        else:
            _pause_event.set()
            print("当前暂停中")
            self.pause_button.setText("继续")

    def stop_clicked(self):
        _stop_event.set()
        _pause_event.clear()
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)

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
        self.refresh_pkl_files()
        print(self.selected_ids)
        print("全选")

    def shell_neibu(self,cmd):
        os.system(cmd)

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
                #self.import_config()
                #self.refresh_pkl_files_test()
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
                updata_pkl_config_mianban("file_path_comment1", selected_file)
                #self.excel_file = selected_file
                #self.import_config()
                #self.refresh_pkl_files_test()
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


    def execute_button_clicked(self):
        _stop_event.clear()
        _pause_event.clear()
        self.pause_button.setText("暂停")
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        updata_pkl_config_mianban("jiaobenyunxingshichang", self.run_time.text())
        updata_pkl_config_mianban("huadongjiangexiao", self.line_edit_from.text())
        updata_pkl_config_mianban("huadongjiangeda", self.line_edit_to.text())
        updata_pkl_config_mianban("huadongcishuxiao", self.jiarenshurukuang.text())
        updata_pkl_config_mianban("huadongcishuda", self.huadongcishu_big.text())
        updata_pkl_config_mianban("zonggailv", self.zonggailv.text())

        if(self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "dy业务")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        #self.scroll_area.ensureWidgetVisible(100)
        if(self.radio_button1.isChecked() == True):
            tasks.append("yanghao")
        if (self.radio_button2.isChecked() == True):
            tasks.append("gouwu")
        if(self.radio_button4.isChecked() == True):
            tasks.append("guanzhu")
        if (self.radio_button6.isChecked() == True):
            #tasks.append("fudai")
            print("开启福袋。。。")
        # if (self.radio_button3.isChecked() == True):
        #     tasks.append("pinglun")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")
        print("tasks------------",tasks)
        # if(os.path.isfile(self.file_textbox.text())):
        #     print("搜索文件加载")
        # else:
        #     print("搜索文件buzai")
        #     return
        if (os.path.isfile(self.file_textbox_comment.text())):
            print("评论文件加载")
        else:
            print("评论文件不在")
        self.save_config_clicked()
        thread = threading.Thread(target=self.thread_temp,args=(tasks,))
        thread.start()
    def thread_temp(self,tasks):

        thread1 = threading.Thread(target=self.upload, args=(get_real_device_id(), self.selected_ids,))
        thread1.start()

        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,))
            #搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
            #threads.append(thread)
            thread.start()
            time.sleep(random.randint(1,3))

        self.selected_ids = []

    def encrypt_payload(self,data: dict) -> str:
        iv = os.urandom(16)
        plaintext = json.dumps(data, ensure_ascii=False).encode('utf-8')
        padder = crypto_padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext).decode('utf-8')

    def heartbeat(self,product_key, computer_code, phone_codes):
        payload = self.encrypt_payload({
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

    def upload(self,computer,phones):
        product_key = "pk_3fb38d164afca69bb15861d110e8c4a3"
        print("phones=",phones)
        phones = list(phones)
        self.heartbeat(product_key,computer,phones)

    def clear_task(self):
        if(os.path.isdir("./task_config")):
            shutil.rmtree("./task_config")

    def save_config_clicked(self):
        updata_pkl_config_mianban("jiaobenyunxingshichang", self.run_time.text())
        updata_pkl_config_mianban("huadongjiangexiao", self.line_edit_from.text())
        updata_pkl_config_mianban("huadongjiangeda", self.line_edit_to.text())
        updata_pkl_config_mianban("huadongcishuxiao", self.jiarenshurukuang.text())
        updata_pkl_config_mianban("huadongcishuda", self.huadongcishu_big.text())
        updata_pkl_config_mianban("zonggailv", self.zonggailv.text())
        updata_pkl_config_mianban("file_path_comment1", self.file_textbox_comment.text())
        updata_pkl_config_mianban("memo_text", self.memo_edit.toPlainText())
        toast("配置已保存")

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
    time = get_format_time()
    with open(pkl, 'wb') as pkl_file:
        pickle.dump({time:phone+"--->"+values}, pkl_file)

def pkl_add(pkl,dic):
    with open(pkl, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
#import pickle
def toast(tishi):
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
        data = {}
        with open(pklfile, 'wb') as file:
            pickle.dump(data, file)

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
    pklfile = shuju_config_file_name
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
            dic = {"name":device_id,"连接状态":"已连接","执行状态":"空闲中","age":"1811","add":"bj1","xingbie":"nan","进行的任务":"空闲","nick_name":"昵称点击可编辑","tongji":"0"}
            pkl_add("./shuju/"+device_id+".pkl",dic)
            if(device_id not in dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))):
                updata_pkl_config("config.pkl", device_id,"昵称点击可编辑")
        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
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

if __name__ == "__main__":
    thread = threading.Thread(target=monitor_devices)
    thread.start()
    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())

