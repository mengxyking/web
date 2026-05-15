import base64
import hashlib
import platform
import shutil
import sys
import threading
import random
import traceback
import uuid
from datetime import datetime

import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QRadioButton, QLineEdit,
    QFileDialog, QTextEdit, QTabWidget, QFrame, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
import os
import pickle


current_scroll_position = 0
import time

#抖音养号+微信加好友脚本

alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()
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
    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    #d.watcher.remove()
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
    Ui_file_Name =  str(int(time.time()))+"_"+str(s)+"_ui.png"
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

def random_click_view(d,view):
    bottom = view.info["bounds"]["top"]
    left = view.info["bounds"]["left"]

    random_x = int(left)+random.randint(0,5)
    random_y = int(bottom) + random.randint(0, 5)

    d.click(random_x,random_y)
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

def random_boolean_with_probability(probability):
    """
    根据给定的概率返回 True 或 False。

    :param probability: 成功的概率（0 到 1 之间的浮点数）
    :return: 如果随机数小于或等于概率则返回 True，否则返回 False
    """
    if not (1 <= probability <= 100):
        raise ValueError("概率必须在 0 到 1 之间")

    return random.random()*100 <= probability


import random

# 全局字典：记录每个文件上一次选中的行（标准化路径做key）
last_selected_line = {}


def get_order_line_from_file(file_path):
    """
    从指定文本文件中获取一行，避免连续两次获取到同一条内容，兼容含特殊字符的路径

    :param file_path: 文本文件的路径（可含中文、空格、特殊符号）
    :return: 选中的一行文本，文件为空/不存在返回None
    """
    try:
        # 彻底标准化路径：解决所有格式/特殊字符问题
        # 1. abspath：转绝对路径 2. normpath：规范化格式 3. normcase：统一大小写
        normalized_path = os.path.normcase(os.path.abspath(os.path.normpath(file_path)))

        # 读取文件（保留原逻辑，兼容特殊字符路径的文件读取）
        with open(file_path, 'r', encoding='utf-8') as file:
            # 过滤空行，保留有效内容
            lines = [line.strip() for line in file.readlines() if line.strip()]

        # 空文件处理
        if not lines:
            return None

        # 只有一行时直接返回
        if len(lines) == 1:
            return lines[0]

        # 用标准化路径取上一次记录，避免特殊字符/格式导致的key冲突
        last_line = last_selected_line.get(normalized_path)
        # 筛选非上一次的行
        candidate_lines = [line for line in lines if line != last_line]
        selected_line = random.choice(candidate_lines)

        # 更新记录（标准化路径做key）
        last_selected_line[normalized_path] = selected_line

        return selected_line

    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        # 清理不存在文件的记录，释放内存
        normalized_path = os.path.normcase(os.path.abspath(os.path.normpath(file_path)))
        if normalized_path in last_selected_line:
            del last_selected_line[normalized_path]
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


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

start_time = datetime.now()
# def operate_device(serials,file_path):
#     print("1")
#     ds = []
#     serialssss = {}
#
#     for serial in serials:
#         d = get_device(serial)
#         ds.append(d)
#         serialssss[d] = serial
#
#     for i in range(10000):
#         try:
#             d = random.choice(ds)
#             print(d.info)
#             result = main_control(d, file_path,serialssss[d])
#             if (result == "1"):
#                 douyinshipinguankanshichang_xiao = int(
#                     get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao"))
#                 douyinshipinguankanshichang_da = int(
#                     get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da"))
#                 time_t = random.randint(douyinshipinguankanshichang_xiao, douyinshipinguankanshichang_da)
#                 print(f"等待{time_t}秒")
#                 time.sleep(time_t)
#         except BaseException as e:
#             print("bengkuile",e)
#             operate_device(serials, file_path)
#start_time = datetime.datetime.now()

# 定义一个全局/闭包变量来记录当前的索引位置
current_index = 0


def operate_device(serials, file_path):
    global current_index  # 声明使用全局变量
    print("1")
    ds = []
    serialssss = {}

    for serial in serials:
        d = get_device(serial)
        ds.append(d)
        serialssss[d] = serial

    # 如果设备列表为空，直接返回，避免索引错误
    if not ds:
        print("没有可用设备")
        return

    for i in range(10000):
        try:
            # 核心修改：按顺序选取，到末尾后重置索引
            d = ds[current_index]
            # 更新索引：如果到最后一个，重置为0，否则+1
            current_index = (current_index + 1) % len(ds)

            print(d.info)
            result = main_control(d, file_path, serialssss[d])
            if (result == "1"):
                douyinshipinguankanshichang_xiao = int(
                    get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao"))
                douyinshipinguankanshichang_da = int(
                    get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da"))
                time_t = random.randint(douyinshipinguankanshichang_xiao, douyinshipinguankanshichang_da)
                print(f"等待{time_t}秒")
                time.sleep(time_t)
        except BaseException as e:
            print("bengkuile", e)
            operate_device(serials, file_path)


def check_time_difference(interval_seconds):
    if(interval_seconds == 0):
        return False
    # 获取当前时间
    end_time = datetime.now()
    # 计算时间差（以秒为单位）
    time_difference = (end_time - start_time).total_seconds()
    print("time_difference=",time_difference)
    # 如果时间差大于100秒，则返回True，否则返回False
    return time_difference > interval_seconds
#搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def main_control(d,file_path,service):
    # task = get_value_by_key_pkl("shuju_config.pkl", "task")
    # print("task=",task)
    # d = get_device(serial)
    # task = "douyinyanghao"
    # if(str(task).count("douyinyanghao")):
    #     updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "抖音业务")
    #     print("")
    #     main_douyin(serial, d)
    #
    # return "88"
    result_main = main_douyin(d, file_path,service)
    updata_pkl("./shuju/" + service + ".pkl", "进行的任务", "互动结束")
    if(result_main == "1"):
        return "1"
    if(result_main != "1"):
        return "2"
def main_xiaohongshu(serial,d):
    print("")
def backTo_xhs_detail(d):
    dd =  0
    time.sleep(1)
    while(dd < 5):
        elements = d(textContains='说点什么')  # 获取所有文本为'some_text'的元素
        elements11 = d(textContains='发现')
        elements22 = d(textContains='分享')
        elements33 = d(textContains='评论')
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        if (len(elements11) > 0):
            return "1"
        if (len(elements22) > 0):
            return "1"
        if (len(elements33) > 0):
            return "1"
        #time.sleep(1.5)
        d.press("back")
        print("222")
        dd += 1
        time.sleep(1)

def comment(d,language,serial,comment_path):
    print("---------------------------------------------------------")
    print("comment_path=",comment_path)
    comment_path = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
    print("comment_path=", comment_path)
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
    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").click()
        time.sleep(1.5)
    elif(d(text="作者仅允许自己评论").exists(timeout=3)):
        return "66"
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return "66"

    comment_t = str(get_random_line_from_file(comment_path))
    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").set_text(str(comment_t))
        time.sleep(1.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return


    time.sleep(1)

    if(d(text="发送").exists(timeout=2)):
        d(text="发送").click()
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)

    return "1"

def tuwen_caozuo(d,xhszuohuagailv,xhsshanghuagailv,dianzan,shoucang,pinglun,fenxiang,comment_path,from_t="meng"):
    mengmeng = random_boolean_with_probability(int(xhszuohuagailv))
    print("random_boolean_with_probability(int(xhszuohuagailv)=", mengmeng)
    if (mengmeng):
        dianzan_t = 0
        shoucang_t = 0
        pinglun_t = 0
        zuohuacishu = random.randint(0, 3)
        couont = 0
        while (couont < zuohuacishu):
            couont += 1
            if (d(descriptionContains='图片').exists(timeout=3)):
                bottoms = d(descriptionContains='图片').info["bounds"]["bottom"]
                lefts = d(descriptionContains='图片').info["bounds"]["left"]
                rights = d(descriptionContains='图片').info["bounds"]["right"]
                tops = d(descriptionContains='图片').info["bounds"]["top"]
                time.sleep(0.5)
                d.swipe(900, tops + 10, 100, tops + 10, 0.5)
                time.sleep(0.5)
    # if (random_boolean_with_probability(int(xhsshanghuagailv))):
    #     zuohuacishu = random.randint(1, 4)
    #     couont = 0
    #     while (couont < zuohuacishu):
    #         couont += 1
    #         time.sleep(0.5)
    #         beisaier(d)
    #         time.sleep(0.5)

    if (d(descriptionContains='评论').exists(timeout=3)):
        print("有评论")
        pingluns = d(descriptionContains='评论')
        if(len(pingluns)>1):
            pinglun_t = str(d(descriptionContains='评论')[1].info["contentDescription"])[2:]
            if (str(pinglun_t).count("万")):
                pinglun_t = "10000"
            if (pinglun_t.isdigit()):
                pinglun_t = int(pinglun_t)
                print("pinglun_t=", pinglun_t)
        else:
            pinglun_t = str(d(descriptionContains='评论').info["contentDescription"])[2:]
            if (str(pinglun_t).count("万")):
                pinglun_t = "10000"
            if (pinglun_t.isdigit()):
                pinglun_t = int(pinglun_t)
                print("pinglun_t=", pinglun_t)

    if (d(descriptionContains='点赞').exists(timeout=3)):
        print("有点赞")
        dianzan_t = str(d(descriptionContains='点赞').info["contentDescription"])[2:]
        print("dianzan_t=", dianzan_t)
        if (str(dianzan_t).count("万")):
            dianzan_t = "10000"
        if (dianzan_t.isdigit()):
            dianzan_t = int(dianzan_t)
    if (d(descriptionContains='收藏').exists(timeout=3)):
        print("有评论")
        shoucang_t = str(d(descriptionContains='收藏').info["contentDescription"])[2:]
        print("shoucang_t=", shoucang_t)
        if (str(shoucang_t).count("万") > 0):
            shoucang_t = "10000"
        if (shoucang_t.isdigit()):
            shoucang_t = int(shoucang_t)
    if (d(descriptionContains='分享').exists(timeout=3)):
        print("有分享")
    time.sleep(0.5)
    dianzanyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi_xhs"))
    shoucangyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi_xhs"))
    pinglunyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi_xhs"))

    if(int(dianzan_t) > dianzanyuzhi):
        if (random_boolean_with_probability(dianzan)):
            print("当前可以dianzan")
            if (d(descriptionContains='点赞').exists(timeout=3)):
                print("点击点赞")
                d(descriptionContains='点赞').click()
            time.sleep(random.randint(1, 2))
    if (int(shoucang_t) > shoucangyuzhi):
        if (random_boolean_with_probability(shoucang)):
            print("当前可以收藏")
            if (d(descriptionContains='收藏').exists(timeout=3)):
                d(descriptionContains='收藏').click()
                print("点击收藏")
            time.sleep(random.randint(1, 2))
    if(int(pinglun_t)>pinglunyuzhi):
        if (random_boolean_with_probability(pinglun)):
            if (d(descriptionContains='评论').exists(timeout=3)):
                print("点击评论")
                ccc = d(descriptionContains='评论')

                d(descriptionContains='评论')[len(ccc) -1 ].click()
                print("点击评论")
                time.sleep(3)
            else:
                print("当前没有添加评论a 。。。。。。。。")

            s_count = random.randint(1,3)
            for ii in range(s_count):
                beisaier_random(d)
                time.sleep(1)
            text_t = "点赞"
            lens = d(textContains='回复')
            if(lens):
                temp_l = random.randint(0, len(lens) - 1)
                text_t = str(lens[temp_l].get_text()).split(" ")
                text_t = text_t[0]


            if (d(textContains='说点什么').exists(timeout=3)):
                print("点击评论")
                random_click_view(d,d(textContains='说点什么'))
                time.sleep(3)
            else:
                print("当前没有添加评论a 。。。。。。。。")



            biaoqing = ["[笑哭R]", "[失望R]", "[汗颜R]", "[哇R]", "[喝奶茶R]", "[自拍R]", "[暗中观察R]", "[蹲后续H]",
                        "[赞R]", "[笑哭R]", "[飞吻R]", "[偷笑R]", "[买爆R]", "[大笑R]", "[色色R]", "[生气R]", "[哭惹R]",
                        "[萌萌哒R]", "[斜眼R]", "[吧唧R]", "[派对R]", "[捂脸R]", "[抓狂R]", "[皱眉R]", "[鄙视R]",
                        "[可怜R]", "[惊恐R]", "[萌萌哒R]", "[派对R]", "[萌萌哒R]", "[斜眼R]", "[吧唧R]", "[派对R]",
                        "[抓狂R]", "[皱眉R]", "[鄙视R]", "[可怜R]", "[惊恐R]", "[抠鼻R]", "[再见R]", "[叹气R]",
                        "[睡觉R]", "[得意R]", "[吃瓜R]", "[笑哭了R]", "[doge]", "[扯脸H]", "[吐舌头H]", "[黄金薯R]",
                        "[黑薯问号R]", "[扶墙R]", "[棒R]", "[亲一个R]", "[完啦R]", "[心心眼R]", "[呃R]", "[坏笑R]",
                        "[尬住R]", "[泪崩R]", "[超喜欢R]", "[捂嘴笑R]", "[嘻嘻R]", "[天幕R]", "[卡式炉R]", "[折叠椅R]",
                        "[营地车R]", "[露营灯R]", "[露营R]", "[渔夫帽R]", "[风镜R]", "[头盔R]", "[手套R]", "[骑行服R]",
                        "[马甲R]", "[背包R]", "[登山鞋R]", "[公路车R]", "[折叠车R]", "[飞盘R]", "[冲浪板R]",
                        "[双翘滑板R]", "[陆冲板R]", "[长板R]", "[加油R]", "[okR]", "[合十R]", "[向右R]", "[点赞R]",
                        "[拔草R]", "[种草R]", "[握手R]", "[鼓掌R]", "[弱R]", "[耶R]", "[抱拳R]", "[勾引R]", "[拳头R]",
                        "[红书R]", "[仙女R]", "[集美R]", "[老虎R]", "[猪头R]", "[举手R]", "[拥抱R]", "[开箱R]",
                        "[探店R]", "[ootdR]", "[同款R]", "[打卡R]", "[飞机R]", "[拍立得R]", "[私信R]", "[生日蛋糕R]",
                        "[礼物R]", "[kissR]", "[购物车R]", "[优惠券R]", "[薯券R]", "[请文明R]", "[请友好R]", "[清单R]",
                        "[学生党R]", "[彩虹R]", "[流汗R]", "[钱袋R]", "[咖啡R]", "[啤酒R]", "[火R]", "[炸弹R]",
                        "[爆炸R]"]
            biaoqing_int = random.randint(0, len(biaoqing) - 3)

            if (str(text_t).count("-") > 0):
                text_t = ""
            if (str(text_t).count("展开") > 0):
                text_t = ""
            if (str(text_t).count("小时") > 0):
                text_t = ""
            if (str(text_t).count("@") > 0):
                text_t = ""
            if (str(text_t).count("天") > 0):
                text_t = ""
            if (str(text_t).count("前") > 0):
                text_t = ""

            text_t = text_t + str(random.randint(0,3)*biaoqing[biaoqing_int])
            comment_t = text_t
            if (d(className="android.widget.EditText").exists(timeout=12)):
                print("善语结善缘，恶言伤人心")
                d(className="android.widget.EditText").set_text(str(comment_t))
                time.sleep(random.randint(1,3))
            else:
                print("当前没有善语结善缘，恶言伤人心aqqqqqqbbbbb 。。。。。。。。")
                # return

            time.sleep(1)

            if (d(text="发送").exists(timeout=2)):
                d(text="发送").click()
            #else:
                #d.press("back")
        backTo_xhs_detail(d)
    if (from_t == "sousuo"):
        print("开始分享1")
        if (random_boolean_with_probability(fenxiang)):
            print("开始分享1命中分享")
            result_fenxiang = xhs_fenxiang( d)
            if(result_fenxiang != "1"):
                d.press("back")
def video_caozuo(d,dianzan,shoucang,pinglun,fenxiang,comment_path,from_t="meng"):
    if (d(descriptionContains='评论').exists(timeout=3)):
        print("有评论")
        pinglun_t = str(d(descriptionContains='评论').info["contentDescription"])[2:]
        if (str(pinglun_t).count("万")):
            pinglun_t = "10000"
        if (pinglun_t.isdigit()):
            pinglun_t = int(pinglun_t)
            print("pinglun_t=", pinglun_t)

    if (d(descriptionContains='点赞').exists(timeout=3)):
        print("有点赞")
        dianzan_t = str(d(descriptionContains='点赞').info["contentDescription"])[2:]
        print("dianzan_t=", dianzan_t)
        if (str(dianzan_t).count("万")):
            dianzan_t = "10000"
        if (dianzan_t.isdigit()):
            dianzan_t = int(dianzan_t)
    if (d(descriptionContains='收藏').exists(timeout=3)):
        print("有评论")
        shoucang_t = str(d(descriptionContains='收藏').info["contentDescription"])[2:]
        print("shoucang_t=", shoucang_t)
        if (str(shoucang_t).count("万") > 0):
            shoucang_t = "10000"
        if (shoucang_t.isdigit()):
            shoucang_t = int(shoucang_t)
    if (d(descriptionContains='分享').exists(timeout=3)):
        print("有分享")
    time.sleep(0.5)
    dianzanyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi_xhs"))
    shoucangyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi_xhs"))
    pinglunyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi_xhs"))

    if(int(dianzan_t) > dianzanyuzhi):
        if (random_boolean_with_probability(dianzan)):
            print("当前可以dianzan")
            if (d(descriptionContains='点赞').exists(timeout=3)):
                print("点击点赞")
                d(descriptionContains='点赞').click()
                print("点击收藏")
            time.sleep(random.randint(1, 3))
    if (int(shoucang_t) > shoucangyuzhi):
        if (random_boolean_with_probability(shoucang)):
            print("当前可以收藏")
            if (d(descriptionContains='收藏').exists(timeout=3)):
                print("点击点赞")
                d(descriptionContains='收藏').click()
                print("点击收藏")
            time.sleep(random.randint(1, 3))
    if (int(pinglun_t) > pinglunyuzhi):
        if (random_boolean_with_probability(pinglun)):
            # if (d(textContains='说点什么').exists(timeout=3)):
            #     print("点击评论")
            #     d(textContains='说点什么').click()
            #     print("点击评论")
            #     time.sleep(6)
            # else:
            #     print("当前没有添加评论a 。。。。。。。。")
            # comment_t = get_random_line_from_file(comment_path)
            # print("comment_t=", comment_t)
            # if (d(className="android.widget.EditText").exists(timeout=12)):
            #     print("善语结善缘，恶言伤人心")
            #     d(className="android.widget.EditText").set_text(str(comment_t))
            #     time.sleep(1.5)
            # else:
            #     print("当前没有善语结善缘，恶言伤人心aqqqqqq 。。。。。。。。")
            #     # return
            #
            # time.sleep(1)
            #
            # if (d(text="发送").exists(timeout=2)):
            #     d(text="发送").click()
            # else:
            #     d.press("back")

            if (d(descriptionContains='评论').exists(timeout=3)):
                print("点击评论")
                d(descriptionContains='评论').click()
                print("点击评论")
                time.sleep(6)
            else:
                print("当前没有添加评论a 。。。。。。。。")

            for i in range(random.randint(1,3)):
                beisaier_random(d)
                time.sleep(1)

            text_t = "点赞"
            lens = d(textContains='回复')
            if (lens):
                temp_l = random.randint(0, len(lens) - 1)
                text_t = str(lens[temp_l].get_text()).split(" ")
                text_t = text_t[0]

            if (d(className='android.widget.EditText').exists(timeout=3)):
                print("点击评论")
                random_click_view(d, d(className='android.widget.EditText'))
                time.sleep(3)
            else:
                print("当前没有添加评论a 。。。。。。。。")

            biaoqing = ["[笑哭R]", "[失望R]", "[汗颜R]", "[哇R]", "[喝奶茶R]", "[自拍R]", "[暗中观察R]", "[蹲后续H]",
                        "[赞R]", "[笑哭R]", "[飞吻R]", "[偷笑R]", "[买爆R]", "[大笑R]", "[色色R]", "[生气R]", "[哭惹R]",
                        "[萌萌哒R]", "[斜眼R]", "[吧唧R]", "[派对R]", "[捂脸R]", "[抓狂R]", "[皱眉R]", "[鄙视R]",
                        "[可怜R]", "[惊恐R]", "[萌萌哒R]", "[派对R]", "[萌萌哒R]", "[斜眼R]", "[吧唧R]", "[派对R]",
                        "[抓狂R]", "[皱眉R]", "[鄙视R]", "[可怜R]", "[惊恐R]", "[抠鼻R]", "[再见R]", "[叹气R]",
                        "[睡觉R]", "[得意R]", "[吃瓜R]", "[笑哭了R]", "[doge]", "[扯脸H]", "[吐舌头H]", "[黄金薯R]",
                        "[黑薯问号R]", "[扶墙R]", "[棒R]", "[亲一个R]", "[完啦R]", "[心心眼R]", "[呃R]", "[坏笑R]",
                        "[尬住R]", "[泪崩R]", "[超喜欢R]", "[捂嘴笑R]", "[嘻嘻R]", "[天幕R]", "[卡式炉R]", "[折叠椅R]",
                        "[营地车R]", "[露营灯R]", "[露营R]", "[渔夫帽R]", "[风镜R]", "[头盔R]", "[手套R]", "[骑行服R]",
                        "[马甲R]", "[背包R]", "[登山鞋R]", "[公路车R]", "[折叠车R]", "[飞盘R]", "[冲浪板R]",
                        "[双翘滑板R]", "[陆冲板R]", "[长板R]", "[加油R]", "[okR]", "[合十R]", "[向右R]", "[点赞R]",
                        "[拔草R]", "[种草R]", "[握手R]", "[鼓掌R]", "[弱R]", "[耶R]", "[抱拳R]", "[勾引R]", "[拳头R]",
                        "[红书R]", "[仙女R]", "[集美R]", "[老虎R]", "[猪头R]", "[举手R]", "[拥抱R]", "[开箱R]",
                        "[探店R]", "[ootdR]", "[同款R]", "[打卡R]", "[飞机R]", "[拍立得R]", "[私信R]", "[生日蛋糕R]",
                        "[礼物R]", "[kissR]", "[购物车R]", "[优惠券R]", "[薯券R]", "[请文明R]", "[请友好R]", "[清单R]",
                        "[学生党R]", "[彩虹R]", "[流汗R]", "[钱袋R]", "[咖啡R]", "[啤酒R]", "[火R]", "[炸弹R]",
                        "[爆炸R]"]
            biaoqing_int = random.randint(0, len(biaoqing) - 3)

            if (str(text_t).count("-") > 0):
                text_t = ""
            if (str(text_t).count("展开") > 0):
                text_t = ""
            if (str(text_t).count("小时") > 0):
                text_t = ""
            if (str(text_t).count("@") > 0):
                text_t = ""
            if (str(text_t).count("天") > 0):
                text_t = ""
            if (str(text_t).count("前") > 0):
                text_t = ""

            text_t = text_t + str(random.randint(0, 3) * biaoqing[biaoqing_int])
            comment_t = text_t
            if (d(className="android.widget.EditText").exists(timeout=12)):
                print("善语结善缘，恶言伤人心")
                d(className="android.widget.EditText").set_text(str(comment_t))
                time.sleep(random.randint(1, 3))
            else:
                print("当前没有善语结善缘，恶言伤人心aqqqqqqbbbbb 。。。。。。。。")
                # return

            time.sleep(1)

            if (d(text="发送").exists(timeout=2)):
                d(text="发送").click()

            backTo_xhs_detail(d)

    if (from_t == "sousuo"):
        print("开始分享1")
        if (random_boolean_with_probability(int(fenxiang))):
            print("命中开始分享1")
            result_fenxiang = xhs_fenxiang(d)
            if (result_fenxiang != "1"):
                d.press("back")
def xhs_shanghua_liulan(d,serial):

    search_path = ""
    change_small= ""
    chang_big= ""
    comment_path= get_value_by_key_pkl("shuju_config.pkl", "file_path_comment_xhs")
    swipe_count_xiao= int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao_xhs"))
    swipe_count_da = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da_xhs"))
    swipe_count = random.randint(swipe_count_xiao,swipe_count_da)
    print("swipe_count_xiao,swipe_count_da=",swipe_count_xiao,swipe_count_da)
    clicked_xhs = []
    swipe_count11 = 0
    print("随机出来的 swipe_count=",swipe_count)
    while (swipe_count11 < swipe_count):
        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        flagggg = True
        xhshuadongliulangailv = int(
            get_value_by_key_pkl("shuju_config.pkl", "xiaohongshumeicihuadongjinruxiangqingyegailv"))
        if (random_boolean_with_probability(int(xhshuadongliulangailv))):
            try:
                zansss = d(descriptionContains='赞')
                random_click = random.randint(0, len(zansss))
                miaoshu = zansss[random_click].info["contentDescription"]
                if (miaoshu not in clicked_xhs):
                    flagggg = False

                    clicked_xhs.append(miaoshu)
                    zansss[random_click].click()


                    time.sleep(2)

                    print(d.app_current())
                    if (str(d.app_current()).count("DetailFeedActivity") > 0):
                        douyinshipinguankanshichang_xiao_xhs = int(
                            get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao_xhs"))
                        douyinshipinguankanshichang_da_xhs = int(
                            get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da_xhs"))
                        time.sleep(random.randint(douyinshipinguankanshichang_xiao_xhs,douyinshipinguankanshichang_da_xhs))
                        print("当前是视频详情页")
                        dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv_xhs"))
                        shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv_xhs"))
                        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv_xhs"))
                        fenxiang = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv_xhs"))
                        try:
                            video_caozuo(d, dianzan, shoucang, pinglun, fenxiang, comment_path)
                        except BaseException as e:
                            print(e)
                        backToHome_xhs_no_faxian(d)
                        time.sleep(1)

                    if (str(d.app_current()).count("NoteDetailActivity")):
                        print("当前是图文详情页")
                        xhszuohuagailv = int(get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenzuohuagailv"))
                        xhsshanghuagailv = int(
                            get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenshanghuagailv"))
                        print("xhszuohuagailv=", xhszuohuagailv)

                        dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv_xhs"))
                        shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv_xhs"))
                        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv_xhs"))
                        fenxiang = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv_xhs"))
                        try:
                            tuwen_caozuo(d, xhszuohuagailv, xhsshanghuagailv, dianzan, shoucang, pinglun, fenxiang,
                                         comment_path)
                        except BaseException as e:
                            print(e)
                        backToHome_xhs_no_faxian(d)
                        time.sleep(1)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)

                print("bengkui le ")
                backToHome_xhs_no_faxian(d)
                time.sleep(1)

        if (flagggg == flagggg):
            swipe_count11 += 1
            time.sleep(random.randint(1, 2))
            beisaier_random(d)
            time.sleep(random.randint(1, 2))
    print("首页浏览结束")


def main_xhs(serial,d):
    task = get_value_by_key_pkl("shuju_config.pkl", "task_xhs")
    print("task-----------",task)
    tasks = str(task).split("_")
    print("task=", tasks)
    if (len(tasks) == 0):
        return
    task_suiji_t = ["task-tuijian-xhs","task-qingli-xhs","task-tongcheng-xhs","task-huifu-xhs","task-sousuo-xhs"]
    if (str(tasks).count("task-suiji-xhs") >0 ):
        tasks = random.sample(task_suiji_t, 3)
        print("无重复随机选择:", tasks)
    random.shuffle(tasks)
    print("顺序打乱之后的，组合=",tasks)

    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.when("仅使用期间允许").click()
    d.watcher.start()

    for task in tasks:
        print("task=",task)
        if ("task-tuijian-xhs" in task):
            backToHome(d)
            d.press("back")

            if(d(text="发现").exists(timeout=3)):
                random_click_view(d,d(text="发现"))
            time.sleep(2)
            print("task-tuijian")
            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "推荐任务中")
            try:
                xhs_shanghua_liulan(d, serial)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)

        if ("task-qingli-xhs" in task):
            backToHome(d)
            d.press("back")
            time.sleep(2)
            print("task-qingli")
            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "清理任务中")
            try:
                xhs_qingli(serial,d)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)
            backToHome(d)
        if ("task-tongcheng-xhs" in task):
            backToHome(d)
            d.press("back")
            time.sleep(2)
            print("task-tongcheng-xhs")
            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "同城任务中")
            try:

                xhs_tongcheng(serial,d)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)
            backToHome(d)
        if ("task-sousuo-xhs" in task):
            backToHome(d)
            d.press("back")
            time.sleep(2)
            print("task-sousuo")
            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "搜索任务中")
            try:
                douyin_xhs_sousuo(serial,d)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)
            backToHome(d)
        if ("task-huifu-xhs" in task):
            backToHome(d)
            d.press("back")
            time.sleep(2)
            print("task-huifu")
            updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "回复任务中")
            try:
                xhs_huifu(serial,d)
            except Exception as e:
                print(f"发生崩溃了: {e}")
                error_info = traceback.format_exc()
                print("完整错误信息:")
                print(error_info)
            backToHome(d)
        # if ("yanghao_xiaohongshu" in task):
        #     print()
    return "88"
def xhs_huifu(serial,d):
    biaoqing = ["[得意]","[微笑]","[色]","[呲牙]","[调皮]","[偷笑]","[愉快]","[憨笑]","[亲亲]","[笑脸]","[奸笑]","[捂脸]","[嘿哈]","[破涕为笑]","[机智]","[皱眉]","[耶]","[吃瓜]","[加油]","[666]","[让我看看]","[哇]","[好的]","[社会社会]","[旺柴]","[握手]","[抱拳]","[拳头]","[OK]","[合十]","[啤酒]","[咖啡]","[蛋糕]","[玫瑰]","[太阳]","[庆祝]","[礼物]","[红包]","[發]","[福]","[烟花]","[爆竹]"]
    biaoqing_int = random.randint(0, len(biaoqing))
    biaoqing_count = random.randint(1, 4)

    huifuxiaoxiyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "huifuxiaoxiyonghunicheng_xhs")

    huifuyonghus = str(huifuxiaoxiyonghunicheng).split("_")

    print("")
    if (d(text='消息').exists(timeout=3)):
        random_click_view(d,d(text='消息'))
        time.sleep(random.randint(1,3))
    else:
        print("当前没有消息啊。。。。。。。。")
        return

    xiaoxis = d(text='消息')
    if(len(xiaoxis)>1):
        print("当前消息页面")
    else:
        print("当前不在消息页面啊")
        return

    for i in range(5):
        print("i=",i)
        d.swipe(500, 500, 500, 1500, 0.1)
    huifued = []
    for i in range(10):
        for huifunicheng in huifuyonghus:
            if huifunicheng not in huifued:
                if (d(textContains=huifunicheng).exists(timeout=0.5)):
                    if(random_boolean_with_probability(35)):
                        print("mingzhong")
                        random_click_view(d, d(textContains=huifunicheng))
                        time.sleep(random.randint(1, 3))
                        huifued.append(huifunicheng)
                        print("当前找到了")
                        sendMessage_xhs(serial, d)
                        backToHome_xiaoxi_xhs(d)
                        time.sleep(random.randint(1,4))
                        #break
        if (d(text='暂时没有更多了').exists(timeout=2)):
            return

        beisaier_random(d)
        time.sleep(2)
def sendMessage_xhs(serial,d):
    print("jinlaile")
    huifucishu_t = random.randint(0,3)
    for i in range(huifucishu_t):
        # biaoqing = ["[得意]", "[微笑]", "[色]", "[呲牙]", "[调皮]", "[偷笑]", "[愉快]", "[憨笑]", "[亲亲]", "[笑脸]",
        #             "[奸笑]", "[捂脸]", "[嘿哈]", "[破涕为笑]", "[机智]", "[皱眉]", "[耶]", "[吃瓜]", "[加油]", "[Emm]",
        #             "[666]", "[让我看看]", "[哇]", "[好的]", "[社会社会]", "[旺柴]", "[握手]", "[抱拳]", "[拳头]",
        #             "[OK]",
        #             "[合十]", "[啤酒]", "[咖啡]", "[蛋糕]", "[玫瑰]", "[太阳]", "[庆祝]", "[礼物]", "[红包]", "[發]",
        #             "[福]", "[烟花]", "[爆竹]"]
        biaoqing = ["[笑哭R]","[失望R]","[汗颜R]","[哇R]","[喝奶茶R]","[自拍R]","[暗中观察R]","[蹲后续H]","[赞R]","[笑哭R]","[飞吻R]","[偷笑R]","[买爆R]","[大笑R]","[色色R]","[生气R]","[哭惹R]","[萌萌哒R]","[斜眼R]","[吧唧R]","[派对R]","[捂脸R]","[抓狂R]","[皱眉R]","[鄙视R]","[可怜R]","[惊恐R]","[萌萌哒R]","[派对R]","[萌萌哒R]","[斜眼R]","[吧唧R]","[派对R]","[抓狂R]","[皱眉R]","[鄙视R]","[可怜R]","[惊恐R]","[抠鼻R]","[再见R]","[叹气R]","[睡觉R]","[得意R]","[吃瓜R]","[笑哭了R]","[doge]","[扯脸H]","[吐舌头H]","[黄金薯R]","[黑薯问号R]","[扶墙R]","[棒R]","[亲一个R]","[完啦R]","[心心眼R]","[呃R]","[坏笑R]","[尬住R]","[泪崩R]","[超喜欢R]","[捂嘴笑R]","[嘻嘻R]","[天幕R]","[卡式炉R]","[折叠椅R]","[营地车R]","[露营灯R]","[露营R]","[渔夫帽R]","[风镜R]","[头盔R]","[手套R]","[骑行服R]","[马甲R]","[背包R]","[登山鞋R]","[公路车R]","[折叠车R]","[飞盘R]","[冲浪板R]","[双翘滑板R]","[陆冲板R]","[长板R]","[加油R]","[okR]","[合十R]","[向右R]","[点赞R]","[拔草R]","[种草R]","[握手R]","[鼓掌R]","[弱R]","[耶R]","[抱拳R]","[勾引R]","[拳头R]","[红书R]","[仙女R]","[集美R]","[老虎R]","[猪头R]","[举手R]","[拥抱R]","[开箱R]","[探店R]","[ootdR]","[同款R]","[打卡R]","[飞机R]","[拍立得R]","[私信R]","[生日蛋糕R]","[礼物R]","[kissR]","[购物车R]","[优惠券R]","[薯券R]","[请文明R]","[请友好R]","[清单R]","[学生党R]","[彩虹R]","[流汗R]","[钱袋R]","[咖啡R]","[啤酒R]","[火R]","[炸弹R]","[爆炸R]"]

        biaoqing_int = random.randint(0, len(biaoqing)-3)
        file_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment_xhs")
        biaoqing_count = random.randint(1, 4)
        if (d(textContains='发消息').exists(timeout=6)):
            random_click_view(d, d(textContains='发消息'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return

        if (d(textContains='发消息').exists(timeout=3)):
            content_t = get_random_line_from_file(file_path_comment)
            d(textContains='发消息').set_text(content_t + biaoqing[biaoqing_int] * biaoqing_count)
            time.sleep(random.randint(1, 3))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return

        if (d(text='发送').exists(timeout=3)):
            random_click_view(d, d(text='发送'))
            time.sleep(random.randint(3, 10))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return

def xhs_tongcheng(serial,d):#tongchengguanjianzi_xhs
    tongchengguanjianzi_xhs = get_value_by_key_pkl("shuju_config.pkl", "tongchengguanjianzi_xhs")

    if (d(text=tongchengguanjianzi_xhs).exists(timeout=3)):
        random_click_view(d, d(text=tongchengguanjianzi_xhs))
        time.sleep(random.randint(3, 7))
    else:
        print("当前没有同城啊啊。。。。。。。。")
        return

    try:
        time.sleep(5)
        xhs_shanghua_liulan(d, serial)
    except Exception as e:
        print(f"发生崩溃了: {e}")
        error_info = traceback.format_exc()
        print("完整错误信息:")
        print(error_info)

def main_douyin(d, file_path,service):
    d = d
    updata_pkl("./shuju/" + service + ".pkl", "进行的任务", "开始互动")
    #先判断当前是否在直播间
    for i in range(3):
        #sleep_time = random.randint(douyinshipinguankanshichang_xiao,douyinshipinguankanshichang_da)
        if (d(text='说点什么...').exists(timeout=3)):
            # random_click_view(d,d(text='消息'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前不在直播间，退出。。。。。。。。")
            return "2"

    result_liveRoome = liveRoom(d,file_path)
    if(result_liveRoome != "1"):
        return "2"
    result_back = backToDyLiveRoom(d)
    if(result_back == "1"):
        return "1"
    else:
        return "2"

def liveRoom(d,file_path):
    content = get_order_line_from_file(file_path)
    if(not content):
        print("获取内容为空")
        return "2"

    for i in range(3):
        if (d(text='说点什么...').exists(timeout=3)):
            random_click_view(d, d(text='说点什么...'))
            time.sleep(random.randint(1, 3))
            break
        else:
            print("当前不在直播间，继续等待。。。。。。。。")
        time.sleep(2)
    else:
        return "2"


    if d(className="android.widget.EditText").exists(timeout=12):
        d(className="android.widget.EditText").set_text(content)
        time.sleep(random.randint(1,3))
    else:
        print("当前没有输入框啊，退出。。。。。。。。")
        return "2"

    if (d(text='发送').exists(timeout=3)):
        random_click_view(d,d(text='发送'))
        time.sleep(random.randint(1,3))
        return "1"
    else:
        print("当前没有发送按钮啊，退出。。。。。。。。")
        return "2"


    # if (1 == 1 ):
    #     d.app_start("com.ss.android.ugc.aweme")
    #     backToHome(d)
    #     d.press("back")
    #     time.sleep(2)
    #     updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "同城任务中")
    #     try:
    #         douyin_tongcheng(serial,d)
    #     except Exception as e:
    #         print(f"发生崩溃了: {e}")
    #         error_info = traceback.format_exc()
    #         print("完整错误信息:")
    #         print(error_info)
    #     backToHome(d)
    #
    # return "88"
def douyin_huifu(serial,d):
    biaoqing = ["[得意]","[微笑]","[色]","[呲牙]","[调皮]","[偷笑]","[愉快]","[憨笑]","[亲亲]","[笑脸]","[奸笑]","[捂脸]","[嘿哈]","[破涕为笑]","[机智]","[皱眉]","[耶]","[吃瓜]","[加油]","[666]","[让我看看]","[哇]","[好的]","[社会社会]","[旺柴]","[握手]","[抱拳]","[拳头]","[OK]","[合十]","[啤酒]","[咖啡]","[蛋糕]","[玫瑰]","[太阳]","[庆祝]","[礼物]","[红包]","[發]","[福]","[烟花]","[爆竹]"]
    biaoqing_int = random.randint(0, len(biaoqing))
    biaoqing_count = random.randint(1, 4)

    huifuxiaoxiyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "huifuxiaoxiyonghunicheng")

    huifuyonghus = str(huifuxiaoxiyonghunicheng).split("_")

    print("")
    if (d(text='消息').exists(timeout=3)):
        random_click_view(d,d(text='消息'))
        time.sleep(random.randint(1,3))
    else:
        print("当前没有消息啊。。。。。。。。")
        return

    xiaoxis = d(text='消息')
    if(len(xiaoxis)>1):
        print("当前消息页面")
    else:
        print("当前不在消息页面啊")
        return

    for i in range(10):
        print("i=",i)
        d.swipe(500, 500, 500, 1500, 0.1)
    huifued = []
    for i in range(10):
        for huifunicheng in huifuyonghus:
            if huifunicheng not in huifued:
                if (d(textContains=huifunicheng).exists(timeout=0.5)):
                    if(random_boolean_with_probability(35)):
                        print("mingzhong")
                        random_click_view(d, d(textContains=huifunicheng))
                        time.sleep(random.randint(1, 3))
                        huifued.append(huifunicheng)
                        sendMessage(serial, d)
                        backToHome_xiaoxi(d)
                        time.sleep(random.randint(1,4))
                        #break
        if (d(text='暂时没有更多了').exists(timeout=2)):
            return

        beisaier_random(d)
        time.sleep(2)



def sendMessage(serial,d):

    huifucishu_t = random.randint(0,3)
    for i in range(huifucishu_t):
        biaoqing = ["[得意]", "[微笑]", "[色]", "[呲牙]", "[调皮]", "[偷笑]", "[愉快]", "[憨笑]", "[亲亲]", "[笑脸]",
                    "[奸笑]", "[捂脸]", "[嘿哈]", "[破涕为笑]", "[机智]", "[皱眉]", "[耶]", "[吃瓜]", "[加油]", "[Emm]",
                    "[666]", "[让我看看]", "[哇]", "[好的]", "[社会社会]", "[旺柴]", "[握手]", "[抱拳]", "[拳头]",
                    "[OK]",
                    "[合十]", "[啤酒]", "[咖啡]", "[蛋糕]", "[玫瑰]", "[太阳]", "[庆祝]", "[礼物]", "[红包]", "[發]",
                    "[福]", "[烟花]", "[爆竹]"]
        biaoqing_int = random.randint(0, len(biaoqing)-1)
        file_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        biaoqing_count = random.randint(1, 4)
        if (d(text='发送消息').exists(timeout=3)):
            random_click_view(d, d(text='发送消息'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return

        if (d(text='发送消息').exists(timeout=3)):
            content_t = get_random_line_from_file(file_path_comment)
            d(text='发送消息').set_text(content_t + biaoqing[biaoqing_int] * biaoqing_count)
            time.sleep(random.randint(1, 3))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return

        if (d(descriptionContains='发送').exists(timeout=3)):
            random_click_view(d, d(descriptionContains='发送'))
            time.sleep(random.randint(3, 10))
        else:
            print("当前没有发送消息啊。。。。。。。。")
            return
def douyin_tongcheng(serial,d):
    print("当前同城任务")
    result_goto = goto_tongcheng(serial,d)
    if(result_goto == "1"):
        print("进入同城成功")
    else:
        print("进入同城失败")
        return

    detail(serial,d)
def douyin_sousuo(serial,d):
    print("当前sousuo任务")
    result_goto = goto_sousuo(serial,d)
    if(result_goto == "1"):
        print("进入sousuo成功")
    else:
        print("进入sousuo失败")
        return
    detail(serial,d,from_t="sousuo")

def douyin_xhs_sousuo(serial,d):
    print("当前小红书sousuo任务")
    result_goto = goto_xhs_sousuo(serial,d)
    if(result_goto == "1"):
        print("进入sousuo成功")
    else:
        print("进入sousuo失败")
        return
    detail_xhs(serial,d,from_t="sousuo")


def goto_xhs_sousuo(serial,d):
    file_path = get_value_by_key_pkl("shuju_config.pkl", "file_path_xhs")
    if (d(description="搜索").exists(timeout=3)):
        print("搜索")
        d(description="搜索").click()
        time.sleep(3.5)
    else:
        print("meiyou 搜索")
        return

    if (d(textContains="搜索").exists(timeout=3)):
        print("搜索")
        search_key = get_random_line_from_file(file_path)
        d(textContains="搜索").set_text(search_key)
        time.sleep(3.5)
    else:
        print("meiyou 搜索")
        return

    if (d(text="搜索").exists(timeout=3)):
        print("搜索")
        d(text="搜索").click()
        time.sleep(3.5)
    else:
        print("meiyou 搜索")
        return

    return "1"

def goto_sousuo(serial,d):
    file_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
    if (d(description='搜索').exists(timeout=3)):
        random_click_view(d,d(description='搜索'))
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    search_key = get_random_line_from_file(file_path)
    if ((len(search_key) > 1) and (search_key != None)):
        print("搜索词符合规范")
    else:
        print("搜索词为空")
        return
    # shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + search_key)
    # shell_neibu(f"adb -s {serial} shell input  keyevent 279")

    if (d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').exists(timeout=3)):
        d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').set_text(search_key)
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return

    # if (check_time_difference(run_time * 60)):
    #     return "88"
    time.sleep(3)
    if (d(text='搜索').exists(timeout=3)):
        d(text='搜索').click()
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    time.sleep(3)
    if (d(text='视频').exists(timeout=3)):
        d(text='视频').click()
        time.sleep(3)
    else:
        print("当前没有视频tab啊。。。。。。。。")
        return

    # if (check_time_difference(run_time * 60)):
    #     return "88"
    d.click(200, 800)
    time.sleep(3)
    if (1 == 1):
        if (d(descriptionContains='点赞').exists(timeout=3)):
            # d(text='添加评论...').click()
            print("当前在播放详情页里头")
            time.sleep(3)
            print("当前在播放详情页里头")
            return "1"
        else:
            print("当前没有添加评论a 。。。。。。。。")
            return
def detail_xhs(serial,d,from_t="meng"):
    quanbu_y = 0
    if (d(text='全部').exists(timeout=3)):
        quanbu_y = d(text='全部').info["bounds"]["bottom"]

    comment_path = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment_xhs")
    swipe_count_xiao= int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao_xhs"))
    swipe_count_da = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da_xhs"))

    swipe_count_temp = random.uniform(swipe_count_xiao, swipe_count_da)
    count_xhs_search = 0
    while (count_xhs_search < swipe_count_temp):
        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        count_xhs_search += 1
        xhshuadongliulangailv = int(get_value_by_key_pkl("shuju_config.pkl", "xiaohongshumeicihuadongjinruxiangqingyegailv"))
        if (random_boolean_with_probability(int(xhshuadongliulangailv))):
            fenzhongqian = d(textContains="分钟前")
            xiaoshiqian = d(textContains="小时前")
            zuotian = d(textContains="昨天")
            tianqian = d(textContains="天前")
            riqi = d(textContains="-0")
            riqi1 = d(textContains="-1")
            riqi2 = d(textContains="-2")

            zong = []

            for yiyiyi in fenzhongqian:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in xiaoshiqian:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in zuotian:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in tianqian:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in riqi:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in riqi1:
                print(yiyiyi.info)
                zong += yiyiyi
            for yiyiyi in riqi2:
                print(yiyiyi.info)
                zong += yiyiyi
            print("zong = ", zong)

            if (len(zong) == 0):
                print("当前搜索结果没有内容")
                return

            if (zong):
                click_p = random.randint(0, len(zong) - 1)

                mumu_y = zong[click_p].info["bounds"]["bottom"]
                if (mumu_y - quanbu_y > 50):
                    zong[click_p].click()
                    #time.sleep(random.randint(3, 7))
                    xiao_temp = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao_xhs"))
                    da_temp = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da_xhs"))
                    time.sleep(random.randint(xiao_temp,da_temp))

                    if (str(d.app_current()).count("DetailFeedActivity") > 0):
                        print("当前是视频详情页")
                        dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv_xhs"))
                        shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv_xhs"))
                        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv_xhs"))
                        fenxiang = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv_xhs"))
                        try:
                            video_caozuo(d, dianzan, shoucang, pinglun,fenxiang, comment_path,from_t="sousuo")
                        except BaseException as e:
                            print(e)
                        back_to_xhs_search_jieguo(d)
                        time.sleep(2)

                    if (str(d.app_current()).count("NoteDetailActivity")):
                        print("当前是图文详情页")

                        dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv_xhs"))
                        shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv_xhs"))
                        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv_xhs"))

                        xhszuohuagailv = int(get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenzuohuagailv"))
                        xhsshanghuagailv = int(get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenshanghuagailv"))
                        print("xhszuohuagailv=", xhszuohuagailv)

                        fenxiang = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv_xhs"))
                        try:
                            tuwen_caozuo(d, xhszuohuagailv, xhsshanghuagailv, dianzan, shoucang, pinglun, fenxiang,
                                         comment_path, from_t="sousuo")
                        except BaseException as e:
                            print(e)
                        back_to_xhs_search_jieguo(d)
                        time.sleep(2)
                    back_to_xhs_search_jieguo(d)

        if (d(text="无更多内容").exists(timeout=1)):
            return
        time.sleep(2)
        beisaier_random(d)
        time.sleep(2)

def back_to_xhs_search_jieguo(d):
    dd =  0
    time.sleep(3)
    while(dd < 4):
        elements = d(text='全部')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        print("333")
        dd += 1
        time.sleep(1.5)



def detail(serial,d,from_t="meng"):
    meicituijianhuadongcishu_xiao = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao"))
    meicituijianhuadongcishu_da = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da"))
    swipe_count_temp = random.uniform(meicituijianhuadongcishu_xiao, meicituijianhuadongcishu_da)
    print("swipe_count_temp--", swipe_count_temp)
    b_count = 0
    while (b_count < swipe_count_temp):

        backTo_dy_detail(d)
        beisaier_random(d)
        time.sleep(2)
        b_count += 1
        # update_pkl_add_one("/shuju/"+serial+".pkl","tongji")
        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        douyinshipinguankanshichang_xiao = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao"))
        douyinshipinguankanshichang_da = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da"))
        wait_time = random.uniform(douyinshipinguankanshichang_xiao, douyinshipinguankanshichang_da)
        print("wait_time=====", wait_time)
        time.sleep(wait_time)
        print("当前在循环里头")
        # dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv"))
        # shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv"))
        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv"))
        meihuadongcishu = int(get_value_by_key_pkl("shuju_config.pkl", "meihuadongcishu"))
        xiuxiduochangshijian = int(get_value_by_key_pkl("shuju_config.pkl", "xiuxiduochangshijian"))

        if(b_count % int(meihuadongcishu) == 0):
            print("开始休息")
            time.sleep(int(xiuxiduochangshijian) * 60)


        # fenxiang_gailv = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv"))
        #
        # dianzanyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi"))
        # shoucangyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi"))
        # pinglunyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi"))
        #
        # print(shoucang, dianzan, pinglun, fenxiang_gailv)
        # print("dianzanyuzhi=",dianzanyuzhi,shoucangyuzhi,pinglunyuzhi)
        pinglun_t = 0
        dianzan_t = 0
        shoucang_t = 0
        fenxiang_t = 0
        try:
            # if (d(descriptionContains='评论评论').exists(timeout=1)):
            #     pinglun_t = 0
            # elif (d(descriptionContains='评论').exists(timeout=3)):
            #     print("有评论")
            #     pinglun_t = str(d(descriptionContains='评论').info["contentDescription"])[2:-3]
            #     if (str(pinglun_t).count("万")):
            #         pinglun_t = "10000"
            #     if (pinglun_t.isdigit()):
            #         pinglun_t = int(pinglun_t)
            #         print("pinglun_t=", pinglun_t)
            # if (d(descriptionContains='未点赞，喜欢赞').exists(timeout=1)):
            #     dianzan_t = 0
            # if (d(descriptionContains='点赞').exists(timeout=3)):
            #     print("有点赞")
            #     dianzan_t = str(d(descriptionContains='点赞').info["contentDescription"])[6:-3]
            #     print("dianzan_t=", dianzan_t)
            #     if (str(dianzan_t).count("万")):
            #         dianzan_t = "10000"
            #     if (dianzan_t.isdigit()):
            #         dianzan_t = int(dianzan_t)
            # if (d(descriptionContains='收藏收藏').exists(timeout=1)):
            #     shoucang_t = 0
            # elif (d(descriptionContains='收藏').exists(timeout=3)):
            #     print("有评论")
            #     shoucang_t = str(d(descriptionContains='收藏').info["contentDescription"])[6:-3]
            #     print("shoucang_t=", shoucang_t)
            #     if (str(shoucang_t).count("万") > 0):
            #         shoucang_t = "10000"
            #     if (shoucang_t.isdigit()):
            #         shoucang_t = int(shoucang_t)
            # if (d(descriptionContains='分享').exists(timeout=3)):
            #     print("有分享")
            #     fenxiang_t = 0
            # time.sleep(0.5)

            if (d(text='点击进入直播间').exists(timeout=2)):
                #beisaier_random(d)
                time.sleep(2)

                continue
            # if (shoucang_t > shoucangyuzhi):
            #     if (random_boolean_with_probability(shoucang)):
            #         print("当前可以收藏")
            #         if (d(descriptionContains='收藏').exists(timeout=3)):
            #             print("点击收藏")
            #             d(descriptionContains='收藏').click()
            #             print("点击收藏")
            #         time.sleep(1.5)
            # if (dianzan_t > dianzanyuzhi):
            #     if (random_boolean_with_probability(dianzan)):
            #         print("当前可以dianzan")
            #         if (d(descriptionContains='点赞').exists(timeout=3)):
            #             print("点击点赞")
            #             d(descriptionContains='点赞').click()
            #             print("点击收藏")
            #         time.sleep(1.5)
            #if (dianzan_t > dianzanyuzhi):
            #if (pinglun_t > pinglunyuzhi):
            if (random_boolean_with_probability(int(pinglun))):
                print("当前可以pinglun")
                language = 0
                comment_path = 0
                result = comment(d, language, serial, comment_path)
                backTo_dy_detail(d)
                if (result != "1"):
                    #beisaier_random(d)
                    time.sleep(2)
                    continue
                time.sleep(1.5)

            if (d(textStartsWith="@").exists(timeout=6)):
                d(textStartsWith="@").click()
                time.sleep(1)
            else:
                # backTo_dy_detail(d)
                # beisaier_random(d)
                time.sleep(2)
                continue

            if (d(textContains="男").exists(timeout=3)):
                # d(textStartsWith="@").click()
                time.sleep(1)

                count_temp = random.randint(1, 5)
                for i in range(count_temp):
                    beisaier(d)
                    time.sleep(random.randint(1, 2))

                if (d(descriptionContains="点赞数").exists(timeout=6)):
                    d(descriptionContains="点赞数").click()
                    time.sleep(3)

                    for i in range(3):
                        beisaier(d)
                        time.sleep(random.randint(1, 2))

                    d.press("back")
                    time.sleep(random.randint(1, 2))

            # if (from_t == "sousuo"):
            #     if (random_boolean_with_probability(fenxiang_gailv)):
            #         douyin_fenxiang(serial, d)
            #         backTo_dy_detail(d)

        except Exception as e:
            print(f"发生崩溃了: {e}")
            error_info = traceback.format_exc()
            print("完整错误信息:")
            print(error_info)
            backTo_dy_detail(d)
            time.sleep(3)
        # if (check_time_difference(run_time * 60)):
        #     return "88"
        #time.sleep(2.5)
        #backTo_dy_detail(d)
        #time.sleep(2.5)
        #beisaier_random(d)
        #time.sleep(2)
        #b_count += 1
        # if (check_time_difference(run_time * 60)):
        #     return "88"
def douyin_fenxiang(serial,d):
    print("当前可以fenxiang_gailv")

    if (d(descriptionContains='分享').exists(timeout=3)):
        print("点击fenxiang")
        random_click_view(d, d(descriptionContains='分享'))
        time.sleep(random.randint(1,3))
    else:
        return

    result_f = findShareName(serial,d)
    if(result_f == "1"):
        if (d(text='发送').exists(timeout=3)):
            print("发送")
            random_click_view(d,d(text='发送'))
            time.sleep(random.randint(1, 3))
            return "1"
        else:
            return
def xhs_fenxiang(d):
    print("xhs_fenxiang")

    if (str(d.app_current()).count("DetailFeedActivity") > 0):
        print("当前是视频详情页面")
        if (d(descriptionContains='分享').exists(timeout=7)):
            print("点击fenxiang")
            random_click_view(d, d(descriptionContains='分享'))
            time.sleep(random.randint(1,3))
        else:
            print("ship详情页没有分享啊")
            return
    else:
        print("当前不是视频详情页面")
        if (d(resourceId='com.xingin.xhs:id/moreOperateIV').exists(timeout=3)):
            print("点击fenxiang")
            random_click_view(d, d(resourceId='com.xingin.xhs:id/moreOperateIV'))
            time.sleep(random.randint(1, 3))
        else:
            print("图文详情页没有分享啊")
            return

    result_f = findShareName_xhs(d)
    if(result_f == "1"):
        if (d(text='发送').exists(timeout=3)):
            print("发送")
            random_click_view(d,d(text='发送'))
            time.sleep(random.randint(1, 3))
            return "1"
        else:
            return

def findShareName_xhs(d):
    fenxiangyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "fenxiangyonghunicheng_xhs")
    fenxiangyonghunichengs = str(fenxiangyonghunicheng).split("_")
    fenxiangyonghunichengs = random.choice(fenxiangyonghunichengs)
    print("fenxiangyonghunichengs=",fenxiangyonghunichengs)

    fenxianggei_y = 0
    if (d(text='分享至').exists(timeout=3)):
        print("分享至")
        fenxianggei_y = d(text='分享至').info["bounds"]["top"] + 220
        time.sleep(random.randint(1, 3))
    else:
        print("没有分享至啊")
        return

    if(fenxianggei_y == 0 ):
        print("分享至是0 啊")
        return

    for i in range(5):
        if (d(textContains=fenxiangyonghunichengs).exists(timeout=3)):
            print("分享给")
            random_click_view(d,d(textContains=fenxiangyonghunichengs))
            time.sleep(random.randint(1, 3))
            print("找到人了")
            return "1"
        d.swipe(900, fenxianggei_y, 200, fenxianggei_y, 0.5)
        time.sleep(1.5)

def findShareName(serial,d):
    fenxiangyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "fenxiangyonghunicheng")
    fenxiangyonghunichengs = str(fenxiangyonghunicheng).split("_")
    fenxiangyonghunichengs = random.choice(fenxiangyonghunichengs)
    print("fenxiangyonghunichengs=",fenxiangyonghunichengs)

    fenxianggei_y = 0
    if (d(text='分享给').exists(timeout=3)):
        print("分享给")
        fenxianggei_y = d(text='分享给').info["bounds"]["top"] + 150
        time.sleep(random.randint(1, 3))
    else:
        return

    if(fenxianggei_y == 0 ):
        return

    for i in range(5):
        if (d(textContains=fenxiangyonghunichengs).exists(timeout=3)):
            print("分享给")
            random_click_view(d,d(textContains=fenxiangyonghunichengs))
            time.sleep(random.randint(1, 3))
            return "1"
        d.swipe(900, fenxianggei_y, 200, fenxianggei_y, 0.5)
        time.sleep(1.5)

def comment111(d,language,serial,comment_path):
    # if(os.path.isfile(comment_path)):
    #     print("keyi")
    # else:
    #     return
    if (d(descriptionContains='评论评论').exists(timeout=3)):
        print("当前不能评论")
        return
    if (d(descriptionContains='评论').exists(timeout=3)):
        print("点击评论")
        d(descriptionContains='评论').click()
        print("点击评论")
        time.sleep(5)
    else:
        print("当前没有添加评论a 。。。。。。。。")
        return

    for i in range(random.randint(1,4)):
        beisaier_random(d)
        time.sleep(1)

    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").click()
        time.sleep(1.5)
    elif(d(text="作者仅允许自己评论").exists(timeout=3)):
        return "66"
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return "66"

    comment_t = "赞"

    biaoqing = ["[得意]", "[微笑]", "[色]", "[呲牙]", "[调皮]", "[偷笑]", "[愉快]", "[憨笑]", "[亲亲]", "[笑脸]",
                "[奸笑]", "[捂脸]", "[嘿哈]", "[破涕为笑]", "[机智]", "[皱眉]", "[耶]", "[吃瓜]", "[加油]", "[Emm]",
                "[666]", "[让我看看]", "[哇]", "[好的]", "[社会社会]", "[旺柴]", "[握手]", "[抱拳]", "[拳头]", "[OK]",
                "[合十]", "[啤酒]", "[咖啡]", "[蛋糕]", "[玫瑰]", "[太阳]", "[庆祝]", "[礼物]", "[红包]", "[發]",
                "[福]", "[烟花]", "[爆竹]"]
    biaoqing_int = random.randint(0, len(biaoqing))
    biaoqing_count = random.randint(1, 4)

    if (d(resourceId="com.ss.android.ugc.aweme:id/content").exists(timeout=3)):
        print("有评论")
        contents = d(resourceId="com.ss.android.ugc.aweme:id/content")
        comment_t = contents[random.randint(0,len(contents)-1)].get_text()
        time.sleep(1.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        #return

    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").set_text(str(comment_t)+biaoqing[biaoqing_int] * biaoqing_count)
        time.sleep(1.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return


    time.sleep(1)

    if(d(text="发送").exists(timeout=2)):
        d(text="发送").click()
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)

    return "1"


def goto_tongcheng(serial,d):
    tuijian_y = 0
    if (d(text="推荐").exists(timeout=5)):
        print("当前在首页了。。。。。。。。")
        tuijian_y = d(text="推荐").info["bounds"]["top"] + 3
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    tongchengs = get_value_by_key_pkl("shuju_config.pkl", "tongchengguanjianzi")
    tongchengs = str(tongchengs).split("_")
    for i in range(5):
        for tongcheng in tongchengs:
            print("tongcheng=",tongcheng)
            if (len(tongcheng) > 0):
                print("ok")
            else:
                print("不 ok")
                continue
            if (d(text=tongcheng).exists(timeout=0.5)):
                print("当前找到同城乐。。。。。。。。")
                random_click_view(d, d(text=tongcheng))
                desc_t = "已选中，"+tongcheng

                if (d(descriptionContains=desc_t).exists(timeout=2)):
                    print("当前确实在同城了，需要划一下。。。。。。。。")
                    beisaier_random(d)
                    time.sleep(2)
                    beisaier_random(d)
                    time.sleep(2)
                    return "1"

                else:
                    print("当前没有  收藏的数据了")
                    #return

                # if (d(text="同城发现").exists(timeout=10)):
                #     print("当前确实在同城了，需要划一下。。。。。。。。")
                #     return "1"
                # else:
                #     print("当前没有  收藏的数据了")
                #     return
            else:
                print("当前没有同城")
        d.swipe(200, tuijian_y, 900, tuijian_y, 0.5)
        time.sleep(1)
def backToHome_xiaoxi_xhs(d):
    dd =  0
    time.sleep(2)
    while(dd < 10):
        elements = d(text='消息')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>1):
                return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
        dd += 1
def backToHome_xiaoxi(d):
    dd =  0
    time.sleep(2)
    while(dd < 10):
        elements = d(text='消息')  # 获取所有文本为'some_text'的元素
        elements11 = d(description='音视频通话')
        #print(len(elements))
        if(len(elements)>1):
            if (len(elements11) < 1):
                return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
        dd += 1
def backToDyLiveRoom(d):
    dd =  0
    time.sleep(1)
    while(dd < 3):
        elements = d(text='说点什么...')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
def backToHome(d):
    dd =  0
    time.sleep(2)
    while(dd < 10):
        elements = d(text='首页')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
def backTo_dy_detail(d):
    dd = 0
    time.sleep(3)
    while (dd < 3):
        if (d(textStartsWith="@").exists(timeout=3)):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
        dd += 1
def xhs_qingli(serial,d):
    qingli_task = ["quxiaoshoucang","quxiaodianzan"]
    #qingli_task = ["quxiaoshoucang"]
    cu_qingli_task = random.choice(qingli_task)

    if(str(cu_qingli_task).count("quxiaoshoucang")>0 ):
        print("jinshoucangle")
        if (d(text='首页').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return


        if (d(text='我').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d,d(text='我'))
            time.sleep(random.randint(1,3))
        else:
            print("当前bumeiyou111 我。。。。。。。。")

        if (d(text='收藏').exists(timeout=10)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d,d(text='收藏'))
            time.sleep(random.randint(1,3))
        else:
            print("没有收藏")
            return

        # beisaier(d)
        # time.sleep(random.randint(1, 3))

        shoucang_cansle_count = random.randint(2,6)

        for i in range(shoucang_cansle_count):
            zanguo_y = 0
            if (d(text='赞过').exists(timeout=5)):
                print("赞过。。。。。。。。")
                print(d(text='赞过').info)
                zanguo_y = d(text='赞过').info["bounds"]["bottom"]

            zans = d(descriptionContains='赞')
            lens = len(zans)
            print(lens)
            # d(descriptionContains='赞')[lens-1].click()
            for zan in zans:
                if (zan.info["bounds"]["bottom"] > zanguo_y):
                    print("有赞")
                    zan.click()
                    break

            if (d(descriptionContains='已收藏').exists(timeout=5)):
                #print("当前在首页了。。。。。。。。")

                quxiaoshoucang = random_boolean_with_probability(35)
                if(quxiaoshoucang):
                    print("取消收藏")
                    random_click_view(d, d(descriptionContains='已收藏'))
                    time.sleep(random.randint(1, 3))
                else:
                    print("当前不取消收藏")
            else:
                print("当前没有  收藏的数据了")
                #return

            backToShoucang(d)
            beisaier_random(d)
            time.sleep(random.randint(2,4))

    if (str(cu_qingli_task).count("quxiaodianzan") > 0):

        print("jinshoucangle")
        if (d(text='首页').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return

        if (d(text='我').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d, d(text='我'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前bumeiyou111 我。。。。。。。。")

        if (d(text='赞过').exists(timeout=10)):
            print("当前在赞过了。。。。。。。。")
            random_click_view(d, d(text='赞过'))
            time.sleep(random.randint(1, 3))
        else:
            print("没有赞过")
            return

        # beisaier(d)
        # time.sleep(random.randint(1, 3))

        shoucang_cansle_count = random.randint(2, 6)

        for i in range(shoucang_cansle_count):
            zanguo_y = 0
            if (d(text='赞过').exists(timeout=5)):
                print("赞过。。。。。。。。")
                print(d(text='赞过').info)
                zanguo_y = d(text='赞过').info["bounds"]["bottom"]

            zans = d(descriptionContains='赞')
            lens = len(zans)
            print(lens)
            # d(descriptionContains='赞')[lens-1].click()
            for zan in zans:
                if (zan.info["bounds"]["bottom"] > zanguo_y):
                    print("有赞")
                    zan.click()
                    break

            if (d(descriptionContains='已点赞').exists(timeout=5)):
                # print("当前在首页了。。。。。。。。")

                quxiaoshoucang = random_boolean_with_probability(35)
                if (quxiaoshoucang):
                    print("取消收藏")
                    random_click_view(d, d(descriptionContains='已点赞'))
                    time.sleep(random.randint(1, 3))
                else:
                    print("当前不取消收藏")
            else:
                print("当前没有  收藏的数据了")
                #return

            backToShoucang(d)
            beisaier_random(d)
            time.sleep(random.randint(2, 4))
def douyin_qingli(serial,d):
    qingli_task = ["quxiaoshoucang","quxiaodianzan"]
    cu_qingli_task = random.choice(qingli_task)

    if(str(cu_qingli_task).count("quxiaoshoucang")>0 ):

        if (d(text='首页').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return


        if (d(text='我').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d,d(text='我'))
            time.sleep(random.randint(1,3))
        else:
            print("当前bumeiyou 我。。。。。。。。")

        if (d(text='收藏').exists(timeout=10)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d,d(text='收藏'))
            time.sleep(random.randint(1,3))
        else:
            print("当前bumeiyou 我。。。。。。。。")
            return

        beisaier_random(d)
        time.sleep(random.randint(1, 3))

        if (d(descriptionContains='点赞数').exists(timeout=10)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d,d(descriptionContains='点赞数'))
            time.sleep(random.randint(1,3))
        else:
            print("当前没有  收藏的数据了")
            return

        shoucang_cansle_count = random.randint(10,20)

        for i in range(shoucang_cansle_count):
            if (d(descriptionContains='已选中，收藏').exists(timeout=5)):
                #print("当前在首页了。。。。。。。。")

                quxiaoshoucang = random_boolean_with_probability(35)
                if(quxiaoshoucang):
                    print("取消收藏")
                    random_click_view(d, d(descriptionContains='已选中，收藏'))
                    time.sleep(random.randint(1, 3))
                else:
                    print("当前不取消收藏")
            else:
                print("当前没有  收藏的数据了")
                return

            beisaier_random(d)
            time.sleep(random.randint(1,3))

    if (str(cu_qingli_task).count("quxiaodianzan") > 0):

        if (d(text='首页').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return

        if (d(text='我').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d, d(text='我'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前bumeiyou 我。。。。。。。。")

        if (d(text='喜欢').exists(timeout=10)):
            random_click_view(d, d(text='喜欢'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前bumeiyou 我。。。。。。。。")
            return

        beisaier_random(d)
        time.sleep(random.randint(1, 3))

        if (d(descriptionContains='点赞数').exists(timeout=10)):
            print("当前在首页了。。。。。。。。")
            random_click_view(d, d(descriptionContains='点赞数'))
            time.sleep(random.randint(1, 3))
        else:
            print("当前没有  收藏的数据了")
            return

        shoucang_cansle_count = random.randint(10, 20)

        for i in range(shoucang_cansle_count):
            if (d(descriptionContains='已点赞，喜欢').exists(timeout=5)):
                # print("当前在首页了。。。。。。。。")

                quxiaoshoucang = random_boolean_with_probability(35)
                if (quxiaoshoucang):
                    print("取消喜欢")
                    random_click_view(d, d(descriptionContains='已点赞，喜欢'))
                    time.sleep(random.randint(1, 3))
                else:
                    print("当前不取消喜欢")
            else:
                print("当前没有  喜欢的数据了")
                return

            beisaier_random(d)
            time.sleep(random.randint(1, 3))
def beisaier_small(d,Diract="up"):
    # 获取屏幕尺寸
    width, height = d.window_size()

    # 设置起点和终点
    if Diract == "up":
        random_start_point_x = random.uniform(0.3, 0.6)
        random_start_point_y = random.uniform(0.78, 0.82)
        random_end_point_x = random.uniform(0.2, 0.99)
        random_end_point_y = 0.01

        start_point = (width * random_start_point_x, height * random_start_point_y)  # 屏幕中下位置
        end_point = (width * random_start_point_x, height * random_end_point_y)  # 屏幕中上位置

    # 设置控制点(可选)
    # 控制点会影响曲线的形状
    control_points = [
        (width * 0.3, height * 0.6),  # 第一个控制点
        (width * 0.7, height * 0.4)  # 第二个控制点
    ]

    # 执行贝塞尔曲线滑动
    swipe_along_bezier(d, start_point, end_point, control_points, steps=15, duration=1.2)

    # 等待一下
    time.sleep(1)
def beisaier_random(d,Diract="up"):
    # 获取屏幕尺寸
    width, height = d.window_size()

    # 设置起点和终点
    if Diract == "up":
        random_start_point_x = random.uniform(0.3, 0.6)
        random_start_point_y = random.uniform(0.78, 0.82)
        random_end_point_x = random.uniform(0.2, 0.99)
        random_end_point_y = 0.01

        start_point = (width * random_start_point_x, height * random_start_point_y)  # 屏幕中下位置
        end_point = (width * random_start_point_x, height * random_end_point_y)  # 屏幕中上位置

    # 设置控制点(可选)
    # 控制点会影响曲线的形状
    control_points = [
        (width * 0.3, height * 0.6),  # 第一个控制点
        (width * 0.7, height * 0.4)  # 第二个控制点
    ]

    # 执行贝塞尔曲线滑动
    random_num = random.uniform(0.3, 0.5)
    swipe_along_bezier(d, start_point, end_point, control_points, steps=15, duration=random_num)

    # 等待一下
    time.sleep(1)
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
def beisaier(d,Diract="up"):
    # 获取屏幕尺寸
    width, height = d.window_size()

    # 设置起点和终点
    if Diract == "up":
        random_start_point_x = random.uniform(0.3, 0.6)
        random_start_point_y = random.uniform(0.78, 0.82)
        random_end_point_x = random.uniform(0.2, 0.99)
        random_end_point_y = 0.01

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

def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)

def backToHome_xhs(d):
    dd =  0
    time.sleep(3)
    while(dd < 10):
        elements = d(text='发现')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            d(text='发现').click()
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
def backToHome_xhs_no_faxian(d):
    dd =  0
    time.sleep(3)
    while(dd < 10):
        elements = d(text='发现')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
def backToHome(d):
    dd =  0
    time.sleep(3)
    while(dd < 10):
        elements = d(text='首页')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
def backToShoucang(d):
    dd =  0
    time.sleep(3)
    while(dd < 10):
        elements = d(text='收藏')  # 获取所有文本为'some_text'的元素
        elements11 = d(text='赞过')
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        if (len(elements11) > 0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
class PklViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files = []
        self.selected_ids = []
        self.init_ui()



    def init_ui(self):
        self.setWindowTitle("抖音直播间互动")
        self.setGeometry(100, 100, 550, 500)  # 适当增大窗口尺寸

        # ====== 顶部标题和手机列表区域 ======
        self.titleLabel = QLabel("*" * 55 + "手 机 列 表" + "*" * 55)
        self.titleLabel.setStyleSheet("""  
            QLabel {  
                font-size: 14px;  
                font-family: "Arial", sans-serif;  
                padding: 10px;  
                font-weight: bold;  
                background-color: #f0f0f0;  
                color: #333;  
            }  
        """)

        # 手机列表表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(
            ['选中', '编号', '昵称', '连接状态', '运行状态', '当前任务', "滑动统计"])
        self.table_widget.setColumnWidth(0, 30)
        self.table_widget.setShowGrid(True)
        self.table_widget.itemChanged.connect(self.on_item_changed)

        # 表格滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(200)  # 适当减小高度，给Tab区域留出空间

        # 操作区域标题和选择框
        self.caozuo_tiel = QLabel("*" * 55 + "功能配置" + "*" * 55)
        self.caozuo_tiel.setStyleSheet("""  
            QLabel {  
                font-size: 14px;  
                font-weight: bold;  
                font-family: "Arial", sans-serif;  
                padding: 10px;  
                background-color: #f0f0f0;  
                color: #333;  
            }  
        """)

        self.horizontal_layout = QHBoxLayout()
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)
        self.radio_button0 = QLabel("           ")
        self.radio_button1 = QCheckBox("dy直播间互动")
        self.radio_button1.setChecked(True)
        self.radio_button2 = QCheckBox("小红书养号")
        self.radio_button2.setChecked(False)
        self.radio_button3 = QCheckBox("养号之后是否关闭抖音")
        self.radio_button3.setChecked(True)
        self.radio_button5 = QLabel("           ")

        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        #self.horizontal_layout.addWidget(self.radio_button2)
        #self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button5)

        # ====== Tab布局区域 ======
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)  # 标签在顶部

        # 添加各个Tab页
        self.init_douyin_tab()  # 抖音配置Tab
        #self.init_xhs_tab()  # 小红书配置Tab
        self.init_advanced_tab()  # 高级设置Tab
        #self.init_other_tab()  # 其他设置Tab（示例）

        # ====== 底部按钮区域 ======
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("执行")
        self.execute_button.resize(100, 30)
        self.clear_task_config_button = QPushButton('保存配置', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)
        self.execute_button_delete = QPushButton("删除")
        self.execute_button_delete.resize(100, 30)
        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)

        self.button_gang.addWidget(self.execute_button)
        self.button_gang.addWidget(self.clear_task_config_button)
        self.button_gang.addWidget(self.execute_button_delete)
        self.button_gang.addWidget(self.execute_button_reset)

        # 绑定按钮事件
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.clear_task_config_button.clicked.connect(self.execute_save_button_clicked)
        self.execute_button_delete.clicked.connect(self.execute_delete_button_clicked)




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




        # ====== 主布局组装 ======
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self.titleLabel)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(self.select_phone_layout)
        main_layout.addWidget(self.caozuo_tiel)
        main_layout.addLayout(self.horizontal_layout)
        main_layout.addWidget(self.tab_widget)  # 添加Tab控件
        main_layout.addLayout(self.button_gang)

        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(30000)

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.add_text)
        self.timer1.start(1300)

        self.refresh_pkl_files()
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



    # ====== 初始化各个Tab页 ======
    def init_douyin_tab(self):
        """抖音配置Tab页"""
        douyin_tab = QWidget()
        douyin_tab.setStyleSheet("background-color: #f0f0f0;")
        douyin_tab.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;  /* 整体背景为浅灰色 */
            }
            QCheckBox {
                background-color: #f5f5f5;  /* 整体背景为浅灰色 */
                border-radius: 1px;
                padding: 1px;
            }
            QLineEdit {
                background-color: white;    /* 输入框保持白色 */
                border: 1px solid #cccccc;  /* 添加边框提升清晰度 */
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton {
                background-color: #e0e0e0;  /* 按钮背景色 */
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;  /* 按钮悬停效果 */
            }
        """)

        layout = QVBoxLayout(douyin_tab)
        self.horizontal_layout_dy_task = QHBoxLayout()
        self.radio_button_dy_task0 = QLabel("抖音养号任务选择:")
        self.radio_button_dy_task1 = QCheckBox("推荐")

        self.radio_button_dy_task1.setChecked(False)
        self.radio_button_dy_task2 = QCheckBox("同城")
        self.radio_button_dy_task2.setChecked(True)
        self.radio_button_dy_task3 = QCheckBox("搜索")
        self.radio_button_dy_task3.setChecked(False)
        self.radio_button_dy_task4 = QCheckBox("清理")
        self.radio_button_dy_task4.setChecked(False)
        self.radio_button_dy_task5 = QCheckBox("消息回复")
        self.radio_button_dy_task5.setChecked(False)
        self.radio_button_dy_task6 = QCheckBox("随机三条任务")
        self.radio_button_dy_task6.setChecked(False)

        #self.radio_button_dy_task1.setFixedWidth(50)
        self.radio_button_dy_task2.setFixedWidth(50)
        #self.radio_button_dy_task3.setFixedWidth(50)
        #self.radio_button_dy_task4.setFixedWidth(50)
        #self.radio_button_dy_task5.setFixedWidth(70)
        #self.radio_button_dy_task6.setFixedWidth(250)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task0)
        #self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task1)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task2)
        #self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task3)
        #self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task4)
        #self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task5)
        #self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task6)
        self.horizontal_layout_dy_task.addStretch(1)

        #任务市场
        self.renwushichang_layout = QHBoxLayout()
        self.renwushichang_layout = QHBoxLayout()
        self.renwushichang_layout.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.renwushichang_layout.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_renwushichang = QLabel('dy任务执行时长:')
        self.douyin_guanjianzi_wenben_renwushichang.setFixedWidth(90)

        douyinrenwuzhixingshichang = get_value_by_key_pkl("shuju_config.pkl", "douyinrenwuzhixingshichang")
        if (douyinrenwuzhixingshichang != None):
            self.douyinrenwuzhixingshichang = QLineEdit(douyinrenwuzhixingshichang)
        else:
            self.douyinrenwuzhixingshichang = QLineEdit("50")
        self.douyinrenwuzhixingshichang.setFixedWidth(40)

        self.baifenbi_2 = QLabel("分钟              ")

        self.renwushichang_layout.addWidget(self.douyin_guanjianzi_wenben_renwushichang)
        self.renwushichang_layout.addWidget(self.douyinrenwuzhixingshichang)
        self.renwushichang_layout.addWidget(self.baifenbi_2)





        # 搜索文件选择
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("请选择搜索文件路径:")

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
        if (file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入搜索文件路径")
        self.file_textbox.setFixedWidth(400)
        self.file_button = QPushButton("选择文件", self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.label_file)
        self.h_layout_dir.addWidget(self.file_textbox)
        self.h_layout_dir.addWidget(self.file_button)
        #self.h_layout_dir.addWidget(self.temp)

        # 评论文件选择
        self.h_layout_dir_comment = QHBoxLayout()
        self.label_file_comment = QLabel("请选择回复文件路径:")

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        #print("file_temp_path_comment=",file_temp_path_comment)
        if (file_temp_path_comment != None) :
            self.file_textbox_comment = QComboBox()
            #self.file_textbox_comment.addItem(file_temp_path_comment)

            for file_path in list(file_temp_path_comment):
                self.files.append(file_path)
                self.file_textbox_comment.addItem(file_path)
            #self.file_textbox_comment.addItem("2")
        else:
            #self.file_textbox_comment = QLineEdit("请输入回复文件路径")
            self.file_textbox_comment = QComboBox()
            self.file_textbox_comment.addItem("请输入回复文件路径")
        self.file_textbox_comment.setFixedWidth(400)
        self.file_button_comment = QPushButton("选择文件", self)
        self.temp_comment = QLabel("                          ")
        self.h_layout_dir_comment.addWidget(self.label_file_comment)
        self.h_layout_dir_comment.addWidget(self.file_textbox_comment)
        self.h_layout_dir_comment.addWidget(self.file_button_comment)
        #self.h_layout_dir_comment.addWidget(self.temp_comment)


        self.h_layout_diwuhang = QHBoxLayout()
        self.h_layout_diwuhang.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_diwuhang.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben = QLabel('直播间互动时间间隔:')
        self.douyin_guanjianzi_wenben.setFixedWidth(130)

        douyinshipinguankanshichang_xiao = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao")
        if (douyinshipinguankanshichang_xiao != None):
            self.douyinshipinguankanshichang_xiao = QLineEdit(douyinshipinguankanshichang_xiao)
        else:
            self.douyinshipinguankanshichang_xiao = QLineEdit("50")
        self.douyinshipinguankanshichang_xiao.setFixedWidth(60)
        self.baifenbi_1 = QLabel("至")

        douyinshipinguankanshichang_da = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da")
        if (douyinshipinguankanshichang_da != None):
            self.douyinshipinguankanshichang_da = QLineEdit(douyinshipinguankanshichang_da)
        else:
            self.douyinshipinguankanshichang_da = QLineEdit("50")
        self.douyinshipinguankanshichang_da.setFixedWidth(60)

        self.baifenbi_2 = QLabel("秒              ")

        self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_wenben)
        self.h_layout_diwuhang.addWidget(self.douyinshipinguankanshichang_xiao)
        self.h_layout_diwuhang.addWidget(self.baifenbi_1)

        self.h_layout_diwuhang.addWidget(self.douyinshipinguankanshichang_da)
        self.h_layout_diwuhang.addWidget(self.baifenbi_2)

        #抖音视频推荐单次滑动次数
        self.douyin_guanjianzi_wenben_huadongcishu = QLabel('每次推荐滑动次数:')
        self.douyin_guanjianzi_wenben_huadongcishu.setFixedWidth(105)

        meicituijianhuadongcishu_xiao = get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao")
        if (meicituijianhuadongcishu_xiao != None):
            self.meicituijianhuadongcishu_xiao = QLineEdit(meicituijianhuadongcishu_xiao)
        else:
            self.meicituijianhuadongcishu_xiao = QLineEdit("50")
        self.meicituijianhuadongcishu_xiao.setFixedWidth(40)
        self.baifenbi_6 = QLabel("至")

        meicituijianhuadongcishu_da = get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da")
        if (meicituijianhuadongcishu_da != None):
            self.meicituijianhuadongcishu_da = QLineEdit(meicituijianhuadongcishu_da)
        else:
            self.meicituijianhuadongcishu_da = QLineEdit("50")
        self.meicituijianhuadongcishu_da.setFixedWidth(40)

        self.baifenbi_7 = QLabel("次")

        # self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_wenben_huadongcishu)
        # self.h_layout_diwuhang.addWidget(self.meicituijianhuadongcishu_xiao)
        # self.h_layout_diwuhang.addWidget(self.baifenbi_6)

        # self.h_layout_diwuhang.addWidget(self.meicituijianhuadongcishu_da)
        # self.h_layout_diwuhang.addWidget(self.baifenbi_7)

        self.h_layout_diwuhang.addStretch(1)

        #同城相关配置
        self.h_layout_tongcheng = QHBoxLayout()
        self.h_layout_tongcheng.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_tongcheng.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_tongcheng = QLabel('同城城市名称配置:')
        self.douyin_guanjianzi_wenben_tongcheng.setFixedWidth(105)

        tongchengguanjianzi = get_value_by_key_pkl("shuju_config.pkl", "tongchengguanjianzi")
        if (tongchengguanjianzi != None):
            self.tongchengguanjianzi = QLineEdit(tongchengguanjianzi)
        else:
            self.tongchengguanjianzi = QLineEdit("多个城市用'_'隔开")
        self.tongchengguanjianzi.setFixedWidth(350)

        self.h_layout_tongcheng.addWidget(self.douyin_guanjianzi_wenben_tongcheng)
        self.h_layout_tongcheng.addWidget(self.tongchengguanjianzi)
        self.h_layout_tongcheng.addStretch(1)

        # 消息回复相关配置
        self.h_layout_xiaoxihuifu = QHBoxLayout()
        self.h_layout_xiaoxihuifu.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_xiaoxihuifu.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_huifu = QLabel('回复消息用户昵称配置:')
        self.douyin_guanjianzi_wenben_huifu.setFixedWidth(125)

        huifuxiaoxiyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "huifuxiaoxiyonghunicheng")
        if (huifuxiaoxiyonghunicheng != None):
            self.huifuxiaoxiyonghunicheng = QLineEdit(huifuxiaoxiyonghunicheng)
        else:
            self.huifuxiaoxiyonghunicheng = QLineEdit("多个名称用'_'隔开")
        self.huifuxiaoxiyonghunicheng.setFixedWidth(330)

        self.h_layout_xiaoxihuifu.addWidget(self.douyin_guanjianzi_wenben_huifu)
        self.h_layout_xiaoxihuifu.addWidget(self.huifuxiaoxiyonghunicheng)
        self.h_layout_xiaoxihuifu.addStretch(1)

        #分享用户配置
        self.h_layout_fenxianggei = QHBoxLayout()
        self.h_layout_fenxianggei.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_fenxianggei.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_fenxiang = QLabel('分享用户昵称配置:')
        self.douyin_guanjianzi_wenben_fenxiang.setFixedWidth(110)

        fenxiangyonghunicheng = get_value_by_key_pkl("shuju_config.pkl", "fenxiangyonghunicheng")
        if (fenxiangyonghunicheng != None):
            self.fenxiangyonghunicheng = QLineEdit(fenxiangyonghunicheng)
        else:
            self.fenxiangyonghunicheng = QLineEdit("多个名称用'_'隔开")
        self.fenxiangyonghunicheng.setFixedWidth(330)

        self.h_layout_fenxianggei.addWidget(self.douyin_guanjianzi_wenben_fenxiang)
        self.h_layout_fenxianggei.addWidget(self.fenxiangyonghunicheng)
        self.h_layout_fenxianggei.addStretch(1)

        # 低于多少个不点赞，低于多少个不收藏
        self.h_layout_shoucang_dianzan_yuzhi = QHBoxLayout()
        self.h_layout_shoucang_dianzan_yuzhi.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_shoucang_dianzan_yuzhi.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi = QLabel('点赞低于')
        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi.setFixedWidth(50)

        dianzanyuzhi = get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi")
        if (dianzanyuzhi != None):
            self.dianzanyuzhi = QLineEdit(dianzanyuzhi)
        else:
            self.dianzanyuzhi = QLineEdit("100")
        self.dianzanyuzhi.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan = QLabel('不点赞')
        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.dianzanyuzhi)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan)


        self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang = QLabel('收藏低于')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang.setFixedWidth(50)

        shoucangyuzhi = get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi")
        if (shoucangyuzhi != None):
            self.shoucangyuzhi = QLineEdit(shoucangyuzhi)
        else:
            self.shoucangyuzhi = QLineEdit("100")
        self.shoucangyuzhi.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan = QLabel('不收藏')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.shoucangyuzhi)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan)


        self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun = QLabel('评论低于')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun.setFixedWidth(50)

        pinglunyuzhi = get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi")
        if (pinglunyuzhi != None):
            self.pinglunyuzhi = QLineEdit(pinglunyuzhi)
        else:
            self.pinglunyuzhi = QLineEdit("100")
        self.pinglunyuzhi.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan = QLabel('不评论')
        self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.pinglunyuzhi)
        self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan)


        self.h_layout_shoucang_dianzan_yuzhi.addStretch(1)


        #点赞 收藏 评论 概率
        self.h_layout_gailv = QHBoxLayout()
        self.h_layout_gailv.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_gailv.setSpacing(0)  # 设置控件间距
        self.h_layout_gailv.setAlignment(Qt.AlignmentFlag.AlignLeft)


        self.douyin_dianzan_gailv = QLabel('点赞概率')
        self.douyin_dianzan_gailv.setFixedWidth(50)

        dianzan_gailv = get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv")
        if (dianzan_gailv != None):
            self.dianzan_gailv = QLineEdit(dianzan_gailv)
        else:
            self.dianzan_gailv = QLineEdit("50")
        self.dianzan_gailv.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao.setFixedWidth(50)
        # self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv)
        # self.h_layout_gailv.addWidget(self.dianzan_gailv)
        # self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao)

        self.douyin_shoucang_gailv = QLabel('收藏概率')
        self.douyin_shoucang_gailv.setFixedWidth(50)

        shoucang_gailv = get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv")
        if (shoucang_gailv != None):
            self.shoucang_gailv = QLineEdit(shoucang_gailv)
        else:
            self.shoucang_gailv = QLineEdit("50")
        self.shoucang_gailv.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao1 = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao1.setFixedWidth(50)
        # self.h_layout_gailv.addWidget(self.douyin_shoucang_gailv)
        # self.h_layout_gailv.addWidget(self.shoucang_gailv)
        # self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao1)

        self.douyin_pinglun_gailv = QLabel('评论概率')
        self.douyin_pinglun_gailv.setFixedWidth(50)

        pinglun_gailv = get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv")
        if (pinglun_gailv != None):
            self.pinglun_gailv = QLineEdit(pinglun_gailv)
        else:
            self.pinglun_gailv = QLineEdit("50")
        self.pinglun_gailv.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao2 = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao2.setFixedWidth(50)
        self.h_layout_gailv.addWidget(self.douyin_pinglun_gailv)
        self.h_layout_gailv.addWidget(self.pinglun_gailv)
        self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao2)

        self.douyin_meihuadong_gailv = QLabel('每滑动')
        self.douyin_meihuadong_gailv.setFixedWidth(50)

        fenxiang_gailv_meihuadong = get_value_by_key_pkl("shuju_config.pkl", "meihuadongcishu")
        if (fenxiang_gailv_meihuadong != None):
            self.fenxiang_gailv_meihuadong = QLineEdit(fenxiang_gailv_meihuadong)
        else:
            self.fenxiang_gailv_meihuadong = QLineEdit("50")
        self.fenxiang_gailv_meihuadong.setFixedWidth(50)

        self.douyin_cixiuxi = QLabel('次,休息')
        self.douyin_cixiuxi.setFixedWidth(40)

        xiuxiduochangshijian = get_value_by_key_pkl("shuju_config.pkl", "xiuxiduochangshijian")
        if (xiuxiduochangshijian != None):
            self.xiuxiduochangshijian = QLineEdit(xiuxiduochangshijian)
        else:
            self.xiuxiduochangshijian = QLineEdit("50")
        self.xiuxiduochangshijian.setFixedWidth(50)

        self.xiuxiduochanfenzhong = QLabel('分钟')
        self.xiuxiduochanfenzhong.setFixedWidth(50)

        self.h_layout_gailv.addWidget(self.douyin_meihuadong_gailv)
        self.h_layout_gailv.addWidget(self.fenxiang_gailv_meihuadong)
        self.h_layout_gailv.addWidget(self.douyin_cixiuxi)
        self.h_layout_gailv.addWidget(self.xiuxiduochangshijian)
        self.h_layout_gailv.addWidget(self.xiuxiduochanfenzhong)


        #layout.addLayout(self.horizontal_layout_dy_task)
        #layout.addLayout(self.renwushichang_layout)
        #layout.addLayout(self.h_layout_dir)
        layout.addLayout(self.h_layout_dir_comment)
        layout.addLayout(self.h_layout_diwuhang)
        #layout.addLayout(self.h_layout_tongcheng)
        #layout.addLayout(self.h_layout_xiaoxihuifu)
        #layout.addLayout(self.h_layout_fenxianggei)
        #layout.addLayout(self.h_layout_shoucang_dianzan_yuzhi)
        #layout.addLayout(self.h_layout_gailv)
        # layout.addLayout(self.h_layout)
        layout.addStretch()  # 底部留白

        # 绑定文件选择事件
        self.file_button.clicked.connect(self.showDialog)
        self.file_button_comment.clicked.connect(self.showDialog_comment)

        self.tab_widget.addTab(douyin_tab, "抖音配置")

    def init_xhs_tab(self):
        """小红书配置Tab页"""
        xhs_tab = QWidget()
        layout = QVBoxLayout(xhs_tab)

        xhs_tab.setStyleSheet("background-color: #f0f0f0;")
        xhs_tab.setStyleSheet("""
                    QWidget {
                background-color: #f5f5f5;  /* 整体背景为浅灰色 */
            }
            QCheckBox {
                background-color: #f5f5f5;  /* 整体背景为浅灰色 */
                border-radius: 1px;
                padding: 1px;
            }
            QLineEdit {
                background-color: white;    /* 输入框保持白色 */
                border: 1px solid #cccccc;  /* 添加边框提升清晰度 */
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton {
                background-color: #e0e0e0;  /* 按钮背景色 */
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;  /* 按钮悬停效果 */
            }
        """)



        self.horizontal_layout_dy_task = QHBoxLayout()
        self.radio_button_dy_task0_xhs = QLabel("小红书养号任务选择:")
        self.radio_button_dy_task1_xhs = QCheckBox("推荐")

        self.radio_button_dy_task1_xhs.setChecked(False)
        self.radio_button_dy_task2_xhs = QCheckBox("同城")
        self.radio_button_dy_task2_xhs.setChecked(False)
        self.radio_button_dy_task3_xhs = QCheckBox("搜索")
        self.radio_button_dy_task3_xhs.setChecked(False)
        self.radio_button_dy_task4_xhs = QCheckBox("清理")
        self.radio_button_dy_task4_xhs.setChecked(False)
        self.radio_button_dy_task5_xhs = QCheckBox("消息回复")
        self.radio_button_dy_task5_xhs.setChecked(False)
        self.radio_button_dy_task6_xhs = QCheckBox("随机三条任务")
        self.radio_button_dy_task6_xhs.setChecked(False)

        self.radio_button_dy_task1_xhs.setFixedWidth(50)
        self.radio_button_dy_task2_xhs.setFixedWidth(50)
        self.radio_button_dy_task3_xhs.setFixedWidth(50)
        self.radio_button_dy_task4_xhs.setFixedWidth(50)
        self.radio_button_dy_task5_xhs.setFixedWidth(70)
        self.radio_button_dy_task6_xhs.setFixedWidth(250)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task0_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task1_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task2_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task3_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task4_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task5_xhs)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task6_xhs)

        # 搜索文件选择
        self.h_layout_dir_xhs = QHBoxLayout()
        self.label_file_xhs = QLabel("请选择搜索文件路径:")

        file_temp_path_xhs = get_value_by_key_pkl("shuju_config.pkl", "file_path_xhs")
        if (file_temp_path_xhs != None):
            self.file_textbox_xhs = QLineEdit(file_temp_path_xhs)
        else:
            self.file_textbox_xhs = QLineEdit("请输入搜索文件路径")
        self.file_textbox_xhs.setFixedWidth(400)
        self.file_button_xhs = QPushButton("选择文件", self)
        self.temp_xhs = QLabel("                          ")
        self.h_layout_dir_xhs.addWidget(self.label_file_xhs)
        self.h_layout_dir_xhs.addWidget(self.file_textbox_xhs)
        self.h_layout_dir_xhs.addWidget(self.file_button_xhs)
        # self.h_layout_dir.addWidget(self.temp)

        # 评论文件选择
        self.h_layout_dir_comment_xhs = QHBoxLayout()
        self.label_file_comment_xhs = QLabel("请选择回复文件路径:")

        file_temp_path_comment_xhs = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment_xhs")
        if (file_temp_path_comment_xhs != None):
            self.file_textbox_comment_xhs = QLineEdit(file_temp_path_comment_xhs)
        else:
            self.file_textbox_comment_xhs = QLineEdit("请输入回复文件路径")
        self.file_textbox_comment_xhs.setFixedWidth(400)
        self.file_button_comment_xhs = QPushButton("选择文件", self)
        self.temp_comment_xhs = QLabel("                          ")
        self.h_layout_dir_comment_xhs.addWidget(self.label_file_comment_xhs)
        self.h_layout_dir_comment_xhs.addWidget(self.file_textbox_comment_xhs)
        self.h_layout_dir_comment_xhs.addWidget(self.file_button_comment_xhs)

        self.h_layout_diwuhang_xhs = QHBoxLayout()
        self.h_layout_diwuhang_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_diwuhang_xhs.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_xhs = QLabel('小红书视频观看时长:')
        self.douyin_guanjianzi_wenben_xhs.setFixedWidth(110)

        douyinshipinguankanshichang_xiao_xhs = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao_xhs")
        if (douyinshipinguankanshichang_xiao_xhs != None):
            self.douyinshipinguankanshichang_xiao_xhs = QLineEdit(douyinshipinguankanshichang_xiao_xhs)
        else:
            self.douyinshipinguankanshichang_xiao_xhs = QLineEdit("50")
        self.douyinshipinguankanshichang_xiao_xhs.setFixedWidth(40)
        self.baifenbi_1_xhs = QLabel("至")

        douyinshipinguankanshichang_da_xhs = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da_xhs")
        if (douyinshipinguankanshichang_da_xhs != None):
            self.douyinshipinguankanshichang_da_xhs = QLineEdit(douyinshipinguankanshichang_da_xhs)
        else:
            self.douyinshipinguankanshichang_da_xhs = QLineEdit("50")
        self.douyinshipinguankanshichang_da_xhs.setFixedWidth(40)

        self.baifenbi_2_xhs = QLabel("秒              ")

        self.h_layout_diwuhang_xhs.addWidget(self.douyin_guanjianzi_wenben_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.douyinshipinguankanshichang_xiao_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.baifenbi_1_xhs)

        self.h_layout_diwuhang_xhs.addWidget(self.douyinshipinguankanshichang_da_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.baifenbi_2_xhs)

        # 抖音视频推荐单次滑动次数
        self.douyin_guanjianzi_wenben_huadongcishu_xhs = QLabel('每次推荐滑动次数:')
        self.douyin_guanjianzi_wenben_huadongcishu_xhs.setFixedWidth(105)

        meicituijianhuadongcishu_xiao_xhs = get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao_xhs")
        if (meicituijianhuadongcishu_xiao_xhs != None):
            self.meicituijianhuadongcishu_xiao_xhs = QLineEdit(meicituijianhuadongcishu_xiao_xhs)
        else:
            self.meicituijianhuadongcishu_xiao_xhs = QLineEdit("50")
        self.meicituijianhuadongcishu_xiao_xhs.setFixedWidth(40)
        self.baifenbi_6_xhs = QLabel("至")

        meicituijianhuadongcishu_da_xhs = get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da_xhs")
        if (meicituijianhuadongcishu_da_xhs != None):
            self.meicituijianhuadongcishu_da_xhs = QLineEdit(meicituijianhuadongcishu_da_xhs)
        else:
            self.meicituijianhuadongcishu_da_xhs = QLineEdit("50")
        self.meicituijianhuadongcishu_da_xhs.setFixedWidth(40)

        self.baifenbi_7_xhs = QLabel("次")

        self.h_layout_diwuhang_xhs.addWidget(self.douyin_guanjianzi_wenben_huadongcishu_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.meicituijianhuadongcishu_xiao_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.baifenbi_6_xhs)

        self.h_layout_diwuhang_xhs.addWidget(self.meicituijianhuadongcishu_da_xhs)
        self.h_layout_diwuhang_xhs.addWidget(self.baifenbi_7_xhs)

        self.h_layout_diwuhang_xhs.addStretch(1)

        # 同城相关配置
        self.h_layout_tongcheng_xhs = QHBoxLayout()
        self.h_layout_tongcheng_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_tongcheng_xhs.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_tongcheng_xhs = QLabel('同城城市名称配置:')
        self.douyin_guanjianzi_wenben_tongcheng_xhs.setFixedWidth(105)

        tongchengguanjianzi_xhs = get_value_by_key_pkl("shuju_config.pkl", "tongchengguanjianzi_xhs")
        if (tongchengguanjianzi_xhs != None):
            self.tongchengguanjianzi_xhs = QLineEdit(tongchengguanjianzi_xhs)
        else:
            self.tongchengguanjianzi_xhs = QLineEdit("多个城市用'_'隔开")
        self.tongchengguanjianzi_xhs.setFixedWidth(350)

        self.h_layout_tongcheng_xhs.addWidget(self.douyin_guanjianzi_wenben_tongcheng_xhs)
        self.h_layout_tongcheng_xhs.addWidget(self.tongchengguanjianzi_xhs)
        self.h_layout_tongcheng_xhs.addStretch(1)

        # 消息回复相关配置
        self.h_layout_xiaoxihuifu_xhs = QHBoxLayout()
        self.h_layout_xiaoxihuifu_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_xiaoxihuifu_xhs.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_huifu_xhs = QLabel('回复消息用户昵称配置:')
        self.douyin_guanjianzi_wenben_huifu_xhs.setFixedWidth(125)

        huifuxiaoxiyonghunicheng_xhs = get_value_by_key_pkl("shuju_config.pkl", "huifuxiaoxiyonghunicheng_xhs")
        if (huifuxiaoxiyonghunicheng_xhs != None):
            self.huifuxiaoxiyonghunicheng_xhs = QLineEdit(huifuxiaoxiyonghunicheng_xhs)
        else:
            self.huifuxiaoxiyonghunicheng_xhs = QLineEdit("多个名称用'_'隔开")
        self.huifuxiaoxiyonghunicheng_xhs.setFixedWidth(330)

        self.h_layout_xiaoxihuifu_xhs.addWidget(self.douyin_guanjianzi_wenben_huifu_xhs)
        self.h_layout_xiaoxihuifu_xhs.addWidget(self.huifuxiaoxiyonghunicheng_xhs)
        self.h_layout_xiaoxihuifu_xhs.addStretch(1)

        # 分享用户配置
        self.h_layout_fenxianggei_xhs = QHBoxLayout()
        self.h_layout_fenxianggei_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_fenxianggei_xhs.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_fenxiang_xhs = QLabel('分享用户昵称配置:')
        self.douyin_guanjianzi_wenben_fenxiang_xhs.setFixedWidth(110)

        fenxiangyonghunicheng_xhs = get_value_by_key_pkl("shuju_config.pkl", "fenxiangyonghunicheng_xhs")
        if (fenxiangyonghunicheng_xhs != None):
            self.fenxiangyonghunicheng_xhs = QLineEdit(fenxiangyonghunicheng_xhs)
        else:
            self.fenxiangyonghunicheng_xhs = QLineEdit("多个名称用'_'隔开")
        self.fenxiangyonghunicheng_xhs.setFixedWidth(330)

        self.h_layout_fenxianggei_xhs.addWidget(self.douyin_guanjianzi_wenben_fenxiang_xhs)
        self.h_layout_fenxianggei_xhs.addWidget(self.fenxiangyonghunicheng_xhs)
        self.h_layout_fenxianggei_xhs.addStretch(1)

        # 低于多少个不点赞，低于多少个不收藏
        self.h_layout_shoucang_dianzan_yuzhi_xhs = QHBoxLayout()
        self.h_layout_shoucang_dianzan_yuzhi_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_shoucang_dianzan_yuzhi_xhs.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_xhs = QLabel('点赞低于')
        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_xhs.setFixedWidth(50)

        dianzanyuzhi_xhs = get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi_xhs")
        if (dianzanyuzhi_xhs != None):
            self.dianzanyuzhi_xhs = QLineEdit(dianzanyuzhi_xhs)
        else:
            self.dianzanyuzhi_xhs = QLineEdit("100")
        self.dianzanyuzhi_xhs.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan_xhs = QLabel('不点赞')
        self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan_xhs.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.dianzanyuzhi_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan_xhs)

        self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang_xhs = QLabel('收藏低于')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang_xhs.setFixedWidth(50)

        shoucangyuzhi_xhs = get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi_xhs")
        if (shoucangyuzhi_xhs != None):
            self.shoucangyuzhi_xhs = QLineEdit(shoucangyuzhi_xhs)
        else:
            self.shoucangyuzhi_xhs = QLineEdit("100")
        self.shoucangyuzhi_xhs.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan_xhs = QLabel('不收藏')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan_xhs.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.shoucangyuzhi_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan_xhs)

        self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun_xhs = QLabel('评论低于')
        self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun_xhs.setFixedWidth(50)

        pinglunyuzhi_xhs = get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi_xhs")
        if (pinglunyuzhi_xhs != None):
            self.pinglunyuzhi_xhs = QLineEdit(pinglunyuzhi_xhs)
        else:
            self.pinglunyuzhi_xhs = QLineEdit("100")
        self.pinglunyuzhi_xhs.setFixedWidth(50)

        self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan_xhs = QLabel('不评论')
        self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan_xhs.setFixedWidth(50)

        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_pinglun_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.pinglunyuzhi_xhs)
        self.h_layout_shoucang_dianzan_yuzhi_xhs.addWidget(self.douyin_guanjianzi_wenben_punglun_yuzhi_budianzan_xhs)

        self.h_layout_shoucang_dianzan_yuzhi_xhs.addStretch(1)

        # 点赞 收藏 评论 概率
        self.h_layout_gailv_xhs = QHBoxLayout()
        self.h_layout_gailv_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_gailv_xhs.setSpacing(0)  # 设置控件间距
        self.h_layout_gailv_xhs.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.douyin_dianzan_gailv_xhs = QLabel('点赞概率')
        self.douyin_dianzan_gailv_xhs.setFixedWidth(50)

        dianzan_gailv_xhs = get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv_xhs")
        if (dianzan_gailv_xhs != None):
            self.dianzan_gailv_xhs = QLineEdit(dianzan_gailv_xhs)
        else:
            self.dianzan_gailv_xhs = QLineEdit("50")
        self.dianzan_gailv_xhs.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao_xhs.setFixedWidth(50)
        self.h_layout_gailv_xhs.addWidget(self.douyin_dianzan_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.dianzan_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao_xhs)

        self.douyin_shoucang_gailv_xhs = QLabel('收藏概率')
        self.douyin_shoucang_gailv_xhs.setFixedWidth(50)

        shoucang_gailv_xhs = get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv_xhs")
        if (shoucang_gailv_xhs != None):
            self.shoucang_gailv_xhs = QLineEdit(shoucang_gailv_xhs)
        else:
            self.shoucang_gailv_xhs = QLineEdit("50")
        self.shoucang_gailv_xhs.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao1_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao1_xhs.setFixedWidth(50)
        self.h_layout_gailv_xhs.addWidget(self.douyin_shoucang_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.shoucang_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao1_xhs)

        self.douyin_pinglun_gailv_xhs = QLabel('评论概率')
        self.douyin_pinglun_gailv_xhs.setFixedWidth(50)

        pinglun_gailv_xhs = get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv_xhs")
        if (pinglun_gailv_xhs != None):
            self.pinglun_gailv_xhs = QLineEdit(pinglun_gailv_xhs)
        else:
            self.pinglun_gailv_xhs = QLineEdit("50")
        self.pinglun_gailv_xhs.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao2_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao2_xhs.setFixedWidth(50)
        self.h_layout_gailv_xhs.addWidget(self.douyin_pinglun_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.pinglun_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao2_xhs)

        self.douyin_fenxiang_gailv_xhs = QLabel('分享概率')
        self.douyin_fenxiang_gailv_xhs.setFixedWidth(50)

        fenxiang_gailv_xhs = get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv_xhs")
        if (fenxiang_gailv_xhs != None):
            self.fenxiang_gailv_xhs = QLineEdit(fenxiang_gailv_xhs)
        else:
            self.fenxiang_gailv_xhs = QLineEdit("50")
        self.fenxiang_gailv_xhs.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao3_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao3_xhs.setFixedWidth(50)
        self.h_layout_gailv_xhs.addWidget(self.douyin_fenxiang_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.fenxiang_gailv_xhs)
        self.h_layout_gailv_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao3_xhs)

        # xhs图文详情页面 左滑以及上划概率配置
        self.h_layout_gailv_detail_xhs = QHBoxLayout()
        self.h_layout_gailv_detail_xhs.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_gailv_detail_xhs.setSpacing(0)  # 设置控件间距
        self.h_layout_gailv_detail_xhs.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.douyin_dianzan_gailv_detail_xhs = QLabel('图文相册左滑概率')
        self.douyin_dianzan_gailv_detail_xhs.setFixedWidth(110)

        xiaohongshutuwenzuohuagailv = get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenzuohuagailv")
        if (xiaohongshutuwenzuohuagailv != None):
            self.xiaohongshutuwenzuohuagailv = QLineEdit(xiaohongshutuwenzuohuagailv)
        else:
            self.xiaohongshutuwenzuohuagailv = QLineEdit("50")
        self.xiaohongshutuwenzuohuagailv.setFixedWidth(30)

        self.douyin_dianzan_gailv_baifenhao_detail_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao_detail_xhs.setFixedWidth(25)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_dianzan_gailv_detail_xhs)
        self.h_layout_gailv_detail_xhs.addWidget(self.xiaohongshutuwenzuohuagailv)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao_detail_xhs)

        self.douyin_shoucang_gailv_detail_xhs = QLabel('图文详情页上划概率')
        self.douyin_shoucang_gailv_detail_xhs.setFixedWidth(110)

        xiaohongshutuwenshanghuagailv = get_value_by_key_pkl("shuju_config.pkl", "xiaohongshutuwenshanghuagailv")
        if (xiaohongshutuwenshanghuagailv != None):
            self.xiaohongshutuwenshanghuagailv = QLineEdit(xiaohongshutuwenshanghuagailv)
        else:
            self.xiaohongshutuwenshanghuagailv = QLineEdit("50")
        self.xiaohongshutuwenshanghuagailv.setFixedWidth(30)

        self.douyin_dianzan_gailv_baifenhao999_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao999_xhs.setFixedWidth(20)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_shoucang_gailv_detail_xhs)
        self.h_layout_gailv_detail_xhs.addWidget(self.xiaohongshutuwenshanghuagailv)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao999_xhs)

        self.douyin_shoucang_gailv_goto_xhs = QLabel('列表每次滑动进入详情页概率')
        self.douyin_shoucang_gailv_goto_xhs.setFixedWidth(130)

        xiaohongshumeicihuadongjinruxiangqingyegailv = get_value_by_key_pkl("shuju_config.pkl", "xiaohongshumeicihuadongjinruxiangqingyegailv")
        if (xiaohongshumeicihuadongjinruxiangqingyegailv != None):
            self.xiaohongshumeicihuadongjinruxiangqingyegailv = QLineEdit(xiaohongshumeicihuadongjinruxiangqingyegailv)
        else:
            self.xiaohongshumeicihuadongjinruxiangqingyegailv = QLineEdit("50")
        self.xiaohongshumeicihuadongjinruxiangqingyegailv.setFixedWidth(30)

        self.douyin_dianzan_gailv_baifenhao9999_xhs = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao9999_xhs.setFixedWidth(10)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_shoucang_gailv_goto_xhs)
        self.h_layout_gailv_detail_xhs.addWidget(self.xiaohongshumeicihuadongjinruxiangqingyegailv)
        self.h_layout_gailv_detail_xhs.addWidget(self.douyin_dianzan_gailv_baifenhao9999_xhs)


        layout.addLayout(self.horizontal_layout_dy_task)
        layout.addLayout(self.h_layout_dir_xhs)
        layout.addLayout(self.h_layout_dir_comment_xhs)
        layout.addLayout(self.h_layout_diwuhang_xhs)
        layout.addLayout(self.h_layout_tongcheng_xhs)
        layout.addLayout(self.h_layout_xiaoxihuifu_xhs)
        layout.addLayout(self.h_layout_fenxianggei_xhs)
        layout.addLayout(self.h_layout_shoucang_dianzan_yuzhi_xhs)
        layout.addLayout(self.h_layout_gailv_xhs)
        layout.addLayout(self.h_layout_gailv_detail_xhs)

        self.file_button_xhs.clicked.connect(self.showDialog_xhs)
        self.file_button_comment_xhs.clicked.connect(self.showDialog_comment_xhs)
        self.tab_widget.addTab(xhs_tab, "小红书配置")

    def init_advanced_tab(self):
        """高级设置Tab页"""
        advanced_tab = QWidget()
        layout = QVBoxLayout

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
                #self.import_config()
                #self.refresh_pkl_files_test()
    def showDialog_xhs(self):#showDialog_comment_xhs
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
                self.file_textbox_xhs.setText(selected_file)
                updata_pkl_config_mianban("file_path_xhs", selected_file)
                #self.excel_file = selected_file
                #self.import_config()
                #self.refresh_pkl_files_test()
    def showDialog_comment_xhs(self):#showDialog_comment_xhs
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
                self.file_textbox_comment_xhs.setText(selected_file)
                updata_pkl_config_mianban("file_path_comment_xhs", selected_file)
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
                #self.file_textbox_comment.setText(selected_file)

                self.file_textbox_comment.insertItem(0, selected_file)
                # 可选：设置首位为选中状态
                self.file_textbox_comment.setCurrentIndex(0)
                if(selected_file not in self.files):
                    self.files.append(selected_file)
                updata_pkl_config_mianban("file_path_comment", self.files)
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
                #self.excel_file = selected_file
                #self.import_config()
                #self.refresh_pkl_files_test()
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
                #self.excel_file = selected_file
                #self.import_config()
                #self.refresh_pkl_files_test()
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
                #self.excel_file = selected_file
                #self.import_config()
                #self.refresh_pkl_files_test()
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


    def save_config(self):
        try:
            task = ""
            if (self.radio_button_dy_task6.isChecked()):
                task = "task-suiji"
            else:
                if (self.radio_button_dy_task1.isChecked()):
                    task = task + "_" + "task-tuijian"
                if (self.radio_button_dy_task2.isChecked()):
                    task = task + "_" + "task-tongcheng"
                if (self.radio_button_dy_task3.isChecked()):
                    task = task + "_" + "task-sousuo"
                if (self.radio_button_dy_task4.isChecked()):
                    task = task + "_" + "task-qingli"
                if (self.radio_button_dy_task5.isChecked()):
                    task = task + "_" + "task-huifu"
            if(self.radio_button3.isChecked()):
                updata_pkl_config_mianban("shifouguanbidouyin", "1")
            else:
                updata_pkl_config_mianban("shifouguanbidouyin", "0")
            updata_pkl_config_mianban("task_douyin", task)

            task_xhs = ""
            # if (self.radio_button_dy_task6_xhs.isChecked()):
            #     print("----")
            #     task_xhs = "task-suiji-xhs"
            # else:
            #     print("0000")
            #     if (self.radio_button_dy_task1_xhs.isChecked()):
            #         task_xhs = task_xhs + "_" + "task-tuijian-xhs"
            #     if (self.radio_button_dy_task2_xhs.isChecked()):
            #         task_xhs = task_xhs + "_" + "task-tongcheng-xhs"
            #     if (self.radio_button_dy_task3_xhs.isChecked()):
            #         task_xhs = task_xhs + "_" + "task-sousuo-xhs"
            #     if (self.radio_button_dy_task4_xhs.isChecked()):
            #         task_xhs = task_xhs + "_" + "task-qingli-xhs"
            #     if (self.radio_button_dy_task5_xhs.isChecked()):
            #         task_xhs = task_xhs + "_" + "task-huifu-xhs"
            # print("task_xhs=",task_xhs)
            #
            #
            # updata_pkl_config_mianban("task_xhs", task_xhs)


            task = ""
            if (self.radio_button1.isChecked()):
                task = "douyinyanghao"
            if (self.radio_button2.isChecked()):
                task = "xiaohongshuyanghao"
            updata_pkl_config_mianban("task", task)
            updata_pkl_config_mianban("douyinrenwuzhixingshichang", self.douyinrenwuzhixingshichang.text())
            updata_pkl_config_mianban("douyinshipinguankanshichang_xiao", self.douyinshipinguankanshichang_xiao.text())
            updata_pkl_config_mianban("douyinshipinguankanshichang_da", self.douyinshipinguankanshichang_da.text())
            updata_pkl_config_mianban("meicituijianhuadongcishu_xiao", self.meicituijianhuadongcishu_xiao.text())
            updata_pkl_config_mianban("meicituijianhuadongcishu_da", self.meicituijianhuadongcishu_da.text())
            updata_pkl_config_mianban("tongchengguanjianzi", self.tongchengguanjianzi.text())
            updata_pkl_config_mianban("dianzanyuzhi", self.dianzanyuzhi.text())
            updata_pkl_config_mianban("shoucangyuzhi", self.shoucangyuzhi.text())
            updata_pkl_config_mianban("dianzan_gailv", self.dianzan_gailv.text())
            updata_pkl_config_mianban("shoucang_gailv", self.shoucang_gailv.text())
            updata_pkl_config_mianban("pinglun_gailv", self.pinglun_gailv.text())
            updata_pkl_config_mianban("pinglunyuzhi", self.pinglunyuzhi.text())
            updata_pkl_config_mianban("fenxiangyonghunicheng", self.fenxiangyonghunicheng.text())
            updata_pkl_config_mianban("huifuxiaoxiyonghunicheng", self.huifuxiaoxiyonghunicheng.text())
            updata_pkl_config_mianban("meihuadongcishu", self.fenxiang_gailv_meihuadong.text())
            updata_pkl_config_mianban("xiuxiduochangshijian", self.xiuxiduochangshijian.text())

            # updata_pkl_config_mianban("douyinshipinguankanshichang_xiao_xhs", self.douyinshipinguankanshichang_xiao_xhs.text())
            # updata_pkl_config_mianban("douyinshipinguankanshichang_da_xhs", self.douyinshipinguankanshichang_da_xhs.text())
            # updata_pkl_config_mianban("meicituijianhuadongcishu_xiao_xhs", self.meicituijianhuadongcishu_xiao_xhs.text())
            # updata_pkl_config_mianban("meicituijianhuadongcishu_da_xhs", self.meicituijianhuadongcishu_da_xhs.text())
            # updata_pkl_config_mianban("tongchengguanjianzi_xhs", self.tongchengguanjianzi_xhs.text())
            # updata_pkl_config_mianban("dianzanyuzhi_xhs", self.dianzanyuzhi_xhs.text())
            # updata_pkl_config_mianban("shoucangyuzhi_xhs", self.shoucangyuzhi_xhs.text())
            # updata_pkl_config_mianban("dianzan_gailv_xhs", self.dianzan_gailv_xhs.text())
            # updata_pkl_config_mianban("shoucang_gailv_xhs", self.shoucang_gailv_xhs.text())
            # updata_pkl_config_mianban("pinglun_gailv_xhs", self.pinglun_gailv_xhs.text())
            # updata_pkl_config_mianban("fenxiang_gailv_xhs", self.fenxiang_gailv_xhs.text())
            # updata_pkl_config_mianban("pinglunyuzhi_xhs", self.pinglunyuzhi_xhs.text())
            # updata_pkl_config_mianban("fenxiangyonghunicheng_xhs", self.fenxiangyonghunicheng_xhs.text())
            # updata_pkl_config_mianban("huifuxiaoxiyonghunicheng_xhs", self.huifuxiaoxiyonghunicheng_xhs.text())
            # updata_pkl_config_mianban("xiaohongshutuwenzuohuagailv", self.xiaohongshutuwenzuohuagailv.text())
            # updata_pkl_config_mianban("xiaohongshutuwenshanghuagailv", self.xiaohongshutuwenshanghuagailv.text())
            # updata_pkl_config_mianban("xiaohongshumeicihuadongjinruxiangqingyegailv", self.xiaohongshumeicihuadongjinruxiangqingyegailv.text())
        except BaseException as e:
            print(f"发生崩溃了: {e}")
            error_info = traceback.format_exc()
            print("完整错误信息:")
            print(error_info)



    def execute_button_clicked(self):
        #print("---------------")

        # result_j = judge()
        # if (result_j == False):
        #     print("当前需要联系")
        #     self.titleLabel.setText("*" * 55 + "当前需要联系作者" + "*" * 55)
        #     self.titleLabel.setStyleSheet("color: red;")
        #     return

        self.save_config()


        if(self.selected_ids == []):
            toast("请选择机型")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")

        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        print("tasks------------",tasks)
        # if(os.path.isfile(self.file_textbox.text())):
        #     print("搜索文件加载")
        # else:
        #     print("搜索文件buzai")
        #     return
        if (os.path.isfile(self.file_textbox_comment.currentText())):
            print("直播间话术文件加载完成")
        else:
            print("直播间话术文件不在，退出")
            return
        #for serial in self.selected_ids:
        thread = threading.Thread(target=operate_device, args=(self.selected_ids,self.file_textbox_comment.currentText(),))
        #搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
        #threads.append(thread)
        thread.start()

        self.selected_ids = []

    def add_text(self):
        print("")
    def clear_task(self):
        print("")
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

    def execute_save_button_clicked(self):
        print("baoc")
        self.save_config()

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
                    print(f"读取文件3 {filepath} 时出错: {e}")
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
                        print(f"读取文件1 {file_name} 时出错: {e}")
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
                    print(f"读取文件2 {file_name} 时出错: {e}")
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



    # 添加配置项到字典
    def add_config_item(layout, label_text, key, default_value="50", widget_type="QSpinBox", unit="%", width=40):
        label, widget, unit_label, config_key = create_config_item(
            label_text, key, default_value, widget_type, unit, width
        )
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addWidget(unit_label)

        return widget  # 返回控件以便设置额外属性
def judge():
    shebeima = get_real_device_id()
    final_str = encrypt_and_modify(shebeima)
    if (os.path.isfile(final_str)):
        return True
    else:
        return False
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

def create_config_item(label_text, key, default_value="50", widget_type="QLineEdit", unit="%", width=40):
    """
    动态生成配置项控件

    参数:
        label_text: 标签文本
        key: 配置文件中的键名
        default_value: 默认值
        widget_type: 控件类型 ("QLineEdit" 或 "QSpinBox")
        unit: 单位文本
        width: 输入框宽度
    """
    # 创建标签
    label = QLabel(label_text)
    label.setFixedWidth(120 if "dy" in label_text.lower() else 110)  # 根据标签内容调整宽度

    # 从配置文件获取值
    saved_value = get_value_by_key_pkl("shuju_config.pkl", key)
    value = saved_value if saved_value is not None else default_value

    # 创建输入控件
    if widget_type == "QSpinBox":
        input_widget = QSpinBox()
        input_widget.setRange(0, 100)  # 设置范围
        input_widget.setValue(int(value))
    else:  # 默认使用QLineEdit
        input_widget = QLineEdit(value)
        input_widget.setFixedWidth(width)

    # 创建单位标签
    unit_label = QLabel(unit)

    return label, input_widget, unit_label, key  # 返回控件和键名用于后续保存


def create_hline():
    line = QFrame()
    try:
        line.setFrameShape(QFrame.Shape.HLine)
    except AttributeError:
        line.setFrameShape(QFrame.HLine)

    try:
        line.setFrameShadow(QFrame.Shadow.Sunken)
    except AttributeError:
        line.setFrameShadow(QFrame.Sunken)

    line.setStyleSheet("color: #cccccc;")  # 分割线颜色
    return line


# 创建带标题和分隔线的行容器
def create_row_container(layout, title=None):
    container = QWidget()
    container.setStyleSheet("padding: 8px 0;")  # 上下内边距

    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)

    if title:
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; margin-bottom: 4px;")
        container_layout.addWidget(title_label)

    container_layout.addLayout(layout)

    # 添加底部分割线
    container_layout.addWidget(create_hline())

    return container


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


def pkl_add(pkl,dic):
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

    # 示例用法
if __name__ == "__main__":
    thread = threading.Thread(target=monitor_devices)
    thread.start()
    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())
