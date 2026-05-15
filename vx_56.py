#import cv2
import shutil
import sys
import threading
import random
from datetime import datetime

import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QRadioButton, QLineEdit,
    QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
import os
import pickle

from uiautomator2 import Direction

current_scroll_position = 0
import time

#抖音养号+微信加好友脚本

alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()
clicked_touxiang = []
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

# 创建一个全局的线程锁
file_lock11 = threading.Lock()
def read_file_line_by_line(file_path):
    with file_lock11:  # 获取锁，确保只有一个线程能进入这个块
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    #print(f"Thread {thread_id} read line {line_number}: {line.strip()}")
                    return
        except Exception as e:
            print(f" encountered an error: {e}")
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
def operate_device(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian):
    # 手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数

    count_zong = 0
    while(True):
        try:
            result = main(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                          swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian)
            if (result == 88):
                print("运行结束")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束-添加频繁了")
                    updata_pkl(filepath, "进行的任务", "空闲")

                    cmd = f"adb -s {serial} shell input keyevent 3"
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                return
            if (result == 99):
                print("运行结束")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                if (os.path.isfile(filepath)):
                    updata_pkl(filepath, "执行状态", "运行结束")
                    updata_pkl(filepath, "进行的任务", "空闲")

                    cmd = f"adb -s {serial} shell input keyevent 3"
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
            print("崩溃了",ee)
            operate_device(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                           swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian)


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
def back_to_home(d):
    count = 0
    while(count < 10):
        if (d(text='微信').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            # d.press("back")
            # time.sleep(3)
            # d.press("back")
            time.sleep(3)

            return 1
        else:
            print("当前bu在首页了。。。。。。。。")
        count += 1
        d.press("back")
    return 88
def back_to_video(d):
    count = 0
    while (count < 10):
        if (d(resourceId='com.smile.gifmaker:id/slide_play_avatar_click_area').exists(timeout=3)):
            print("当前在视频里了了。。。。。。。。")

            return 1
        else:
            print("当前不在视频里了了。。。。。。。。")
        count += 1
        d.press("back")
    return 0

def back_to_comment(d):
    count = 0
    while (count < 10):
        #time.sleep(1)
        if ((d(resourceId='com.smile.gifmaker:id/tabs_panel_close').exists(timeout=3)) or (d(description='回复评论').exists(timeout=0.1))):
            print("当前在评论里了了。。。。。。。。")
            time.sleep(1)
            return 1
        else:
            print("当前不在评论里了了。。。。。。。。")
        count += 1
        d.press("back")
    return 0
def random_click_view(d,view):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left)+random.randint(2,15)
    random_y = int(bottom) + random.randint(2, 15)

    d.click(random_x,random_y)

#搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def main(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,count_zong,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian):
    # 手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数

    if(len(task) == 0):
        return
    d = get_device(serial)
    d.watcher.when("以后再说").click()
    d.watcher.when("我知道了").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    shifou_pengyouquan = shifousixinpinglunyonghu
    shipinhao = shifouzuixin
    shifou_gongzhonghao = jinyiri
    shifou_xinwen = jinqiri
    print("---------------->",shifou_pengyouquan,shipinhao,shifou_gongzhonghao,shifou_xinwen)

    if(shifouqunfashoucang == True or shifouqufnawenzi == True):
        d.app_start(package_name="com.tencent.mm")
        result_back = back_to_home(d)
        print("result_back--->", result_back)
        if (result_back != 1):
            return 0

        if (result_back == 88):
            return 0

        if (d(text='我').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(text='我').info)
            random_click_view(d, d(text='我').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有通讯录按钮")
            return 0

        if (d(resourceId='com.tencent.mm:id/kbb').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(resourceId='com.tencent.mm:id/kbb').info)
            nick_name = d(resourceId='com.tencent.mm:id/kbb').get_text()
            print("nick_name = ",nick_name)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有通讯录按钮")
            return 0
        if (d(text='通讯录').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(text='通讯录').info)
            random_click_view(d, d(text='通讯录').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有通讯录按钮")
            return 0

        result_qunfa = qunfa(d, serial,nick_name,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian)
        if(result_qunfa == 99):
            return 99
        if(result_qunfa == 0 or result_qunfa == None):
            return

    if("sixin" in task):
        sixin_comment = run_time #添加好友申请语
        search_key_count_video_small = int(change_small) #添加好友间隔小
        search_key_count_video_big = int(chang_big)#添加好友间隔大
        fans_count_small = int(swipe_small)#添加好友数量限制 配置

        print("开始了。。。")
        if (count_zong == 0):
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.tencent.mm")
            result_back = back_to_home(d)
            print("result_back--->", result_back)
            if (result_back != 1):
                return 0

            if (result_back == 88):
                return 88

        else:
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.tencent.mm")
            backToHome(d)
            result_back = back_to_home(d)
            if (result_back != 1):
                return 0

            if (result_back == 88):
                return 88

        big_wai_count = 0
        while(True):
            result_back = back_to_home(d)
            print("result_back--->", result_back)
            if (result_back != 1):
                return 0

            if (result_back == 88):
                return 88

            result_xiaoyewu = xiaoyewu(d,serial,search_path,sixin_comment)
            if(result_xiaoyewu == 88):
                print("当前频繁了")
                return result_xiaoyewu
            if(result_xiaoyewu == 1):
                update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                time.sleep(random.randint(search_key_count_video_small,search_key_count_video_big))
            tongji = get_value_by_key_pkl("./shuju/" + str(serial) + ".pkl", "tongji")
            if (int(tongji) >= fans_count_small):
                return 99
    if ("yanghao" in task):
        pengyouquan(d,shifou_pengyouquan,shipinhao,serial)
        if(shifou_gongzhonghao):
            yanghao_gongzhonghao(d, comment_path, serial)
        if(shifou_xinwen):
            yanghao_xinwen(d,serial)
        return 99

def pengyouquan(d,shifou_pengyouquan,shifou_shipinhao,serial):
    task_yanghao = []
    if(shifou_pengyouquan):
        task_yanghao.append("朋友圈")
    if (shifou_shipinhao):
        task_yanghao.append("视频号")
    for task_temp in task_yanghao:
        print("养号")
        d.app_start(package_name="com.tencent.mm")
        result_back = back_to_home(d)
        print("result_back--->", result_back)
        if (result_back != 1):
            return 0

        if (result_back == 88):
            return 88

        if (d(text='发现').exists(timeout=3)):
            d(text='发现').click()
            time.sleep(random.randint(3, 5))
        else:
            print("首页没有发现按钮")
            return 0

        if (d(text=task_temp).exists(timeout=3)):
            d(text=task_temp).click()
            time.sleep(random.randint(3, 5))
        else:
            print("首页没有朋友圈")
            return 0

        if(task_temp == "朋友圈"):
            filepath = './shuju/' + serial + ".pkl"
            print("filepath-->", filepath)
            if (os.path.isfile(filepath)):
                updata_pkl(filepath, "进行的任务", "vx养号-朋友圈")
            pengyouquan_huadong_cishu_xiao = read_config("pengyouquan_huadong_cishu_xiao")
            if(pengyouquan_huadong_cishu_xiao == None):
                pengyouquan_huadong_cishu_xiao = 40

            pengyouquan_huadong_cishu_da = read_config("pengyouquan_huadong_cishu_da")
            if (pengyouquan_huadong_cishu_da == None):
                pengyouquan_huadong_cishu_da = 100

            pengyouquan_dianzan_gailv = read_config("pengyouquan_dianzan_gailv")
            if (pengyouquan_dianzan_gailv == None):
                pengyouquan_dianzan_gailv = 2
            random_swipe = random.randint(int(pengyouquan_huadong_cishu_xiao), int(pengyouquan_huadong_cishu_da))
            bb = 0
            while (bb < random_swipe):
                bb+=1
                if (random.randint(1, 11) > 10-int(pengyouquan_dianzan_gailv)):
                    if (d(resourceId='com.tencent.mm:id/r2').exists(timeout=3)):
                        dianzans = d(resourceId='com.tencent.mm:id/r2')
                        if (len(dianzans) > 1):
                            dianzans[1].click()
                            time.sleep(random.randint(1, 2))
                            if(d(text="赞").exists(timeout=3)):
                                d(text="赞").click()
                        time.sleep(random.randint(3, 5))
                    else:
                        print("首页没有朋友圈")
                        # return 0

                d.swipe_ext("up", scale=0.8)
                time.sleep(random.randint(2, 5))
        time.sleep(random.randint(2, 5))

        if (task_temp == "视频号"):
            filepath = './shuju/' + serial + ".pkl"
            print("filepath-->", filepath)
            if (os.path.isfile(filepath)):
                updata_pkl(filepath, "进行的任务", "vx养号-视频号")
            shipinhao_liulan_cishu_xiao = read_config("shipinhao_liulan_cishu_xiao")
            if (shipinhao_liulan_cishu_xiao == None):
                shipinhao_liulan_cishu_xiao = 50
            shipinhao_liulan_cishu_da = read_config("shipinhao_liulan_cishu_da")
            if (shipinhao_liulan_cishu_da == None):
                shipinhao_liulan_cishu_da = 100
            shipinhao_dianzai_gailv = read_config("shipinhao_dianzai_gailv")
            if (shipinhao_dianzai_gailv == None):
                shipinhao_dianzai_gailv = 2
            random_swipe = random.randint(int(shipinhao_liulan_cishu_xiao), int(shipinhao_liulan_cishu_da))
            bb = 0
            while (bb < random_swipe):
                bb += 1
                if (random.randint(1, 11) > 10-int(shipinhao_dianzai_gailv)):
                    if (d(resourceId='com.tencent.mm:id/ng5').exists(timeout=3)):
                        d(resourceId='com.tencent.mm:id/ng5').click()
                        time.sleep(random.randint(3, 5))
                    else:
                        print("首页没有朋友圈")
                        # return 0
                d.swipe_ext("up", scale=0.9)
                time.sleep(random.randint(10, 20))
        time.sleep(random.randint(2, 5))
def yanghao_gongzhonghao(d,comment_path,serial):
    print("养号")
    filepath = './shuju/' + serial + ".pkl"
    print("filepath-->", filepath)
    if (os.path.isfile(filepath)):
        updata_pkl(filepath, "进行的任务", "vx养号-公众号")
    d.app_start(package_name="ca.zgrs.clipper")
    time.sleep(1)
    gongzhonghao_zhanghao_liulan_xiao = read_config("gongzhonghao_zhanghao_liulan_xiao")
    if (gongzhonghao_zhanghao_liulan_xiao == None):
        gongzhonghao_zhanghao_liulan_xiao = 3
    gongzhonghao_zhanghao_liulan_da = read_config("gongzhonghao_zhanghao_liulan_da")
    if (gongzhonghao_zhanghao_liulan_da == None):
        gongzhonghao_zhanghao_liulan_da = 8
    gongzhonghao_count = random.randint(int(gongzhonghao_zhanghao_liulan_xiao),int(gongzhonghao_zhanghao_liulan_da))
    temp_count = 0
    while(temp_count < gongzhonghao_count):
        gongzhonghao = get_random_line_from_file(comment_path)
        temp_count += 1
        d.app_start(package_name="com.tencent.mm")
        result_back = back_to_home(d)

        if (d(text='微信').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(text='微信').info)

            random_click_view(d, d(text='微信').info)

            time.sleep(random.randint(3, 5))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(resourceId='com.tencent.mm:id/meb').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(resourceId='com.tencent.mm:id/meb').info)

            random_click_view(d, d(resourceId='com.tencent.mm:id/meb').info)

            time.sleep(random.randint(3, 5))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='公众号').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            # print(d(resourceId='com.tencent.mm:id/meb').info)

            random_click_view(d, d(text='公众号').info)

            time.sleep(random.randint(3, 5))
        else:
            print("首页没有加号按钮")
            return 0
        print("gongzhonghao---", gongzhonghao)

        shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + str(gongzhonghao))
        shell_neibu(f"adb -s {serial} shell input  keyevent 279")
        time.sleep(1)
        time.sleep(random.randint(5, 8))

        d.click(d.info["displayWidth"] - 120, 170)
        time.sleep(random.randint(5, 8))
        d.click(533, 618)
        time.sleep(random.randint(5, 8))

        d.click(533, 1299)
        d.click(533, 1399)

        time.sleep(random.randint(5, 8))

        d.swipe_ext("up", scale=0.9)
        time.sleep(random.randint(1, 5))
        d.swipe_ext("up", scale=0.9)
        time.sleep(random.randint(1, 5))
        d.swipe_ext("up", scale=0.9)
        time.sleep(random.randint(1, 5))
        d.swipe_ext("up", scale=0.9)
        time.sleep(random.randint(1, 5))
        d.swipe_ext("up", scale=0.9)

def read_config(key):
    from pathlib import Path


    # 获取当前用户的桌面路径
    desktop_path = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    # 拼接路径到weixin文件夹
    weixin_path = desktop_path / "weixin"
    # 假设你要读取weixin文件夹下的config目录的内容（如果config是文件，这里需要调整）
    config_path = weixin_path / "config.txt"
    print("config_path---->",config_path)
    # 假设config是一个文件，读取其内容
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            #print("content---->",content)
            for temp in file:
                print("temp---->",temp)
                if ((temp.count(key) > 0) and (temp.count(":") > 0)):
                    print("key-------------->", key, str(temp).split(":")[1])
                    return str(temp).split(":")[1]
        return None
    else:
        print(f"{config_path} is not a file.")
        return None
def yanghao_xinwen(d,serial):
    # 下面是腾讯新闻
    filepath = './shuju/' + serial + ".pkl"
    print("filepath-->", filepath)
    if (os.path.isfile(filepath)):
        updata_pkl(filepath, "进行的任务", "vx养号-腾讯新闻")
    d.app_start(package_name="com.tencent.mm")
    result_back = back_to_home(d)
    if (d(text='微信').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text='微信').info)

        random_click_view(d, d(text='微信').info)

        time.sleep(random.randint(3, 5))
    else:
        print("首页没有加号按钮")
        return 0

    if (d(resourceId='com.tencent.mm:id/meb').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/meb').info)

        random_click_view(d, d(resourceId='com.tencent.mm:id/meb').info)

        time.sleep(random.randint(3, 5))
    else:
        print("首页没有加号按钮")
        return 0

    if (d(resourceId='com.tencent.mm:id/d98').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()

        d(resourceId='com.tencent.mm:id/d98').set_text("腾讯新闻")

        time.sleep(random.randint(3, 5))
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text='功能').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()

        d.click(300, d(text='功能').info["bounds"]["bottom"] + 10)

        time.sleep(random.randint(3, 5))
    else:
        print("首页没有加号按钮")
        return 0

    xinwen_guankangeshu_xiao = read_config("xinwen_guankangeshu_xiao")
    if (xinwen_guankangeshu_xiao == None):
        xinwen_guankangeshu_xiao = 2
    xinwen_guankangeshu_da = read_config("xinwen_guankangeshu_da")
    if (xinwen_guankangeshu_da == None):
        xinwen_guankangeshu_da = 5
    xinwei_zong_count = random.randint(int(xinwen_guankangeshu_xiao), int(xinwen_guankangeshu_da))
    temp_xinwen = 0
    length_xinwen = d(resourceId='com.tencent.mm:id/obc')
    if (len(length_xinwen) < 1):
        return 0
    # if(xinwei_zong_count>=length_xinwen):
    xinwei_zong_count = min(xinwei_zong_count, len(length_xinwen))
    while (temp_xinwen < xinwei_zong_count):

        if (d(resourceId='com.tencent.mm:id/obc')[temp_xinwen].exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            # print(d(resourceId='com.tencent.mm:id/obc').info)

            random_click_view(d, d(resourceId='com.tencent.mm:id/obc')[temp_xinwen].info)

            time.sleep(random.randint(3, 5))
            d.swipe_ext("up", scale=0.9)
            time.sleep(random.randint(1, 5))
            d.swipe_ext("up", scale=0.9)
            time.sleep(random.randint(1, 5))
            d.swipe_ext("up", scale=0.9)
            time.sleep(random.randint(1, 5))
            d.swipe_ext("up", scale=0.9)
            time.sleep(random.randint(1, 5))
            d.swipe_ext("up", scale=0.9)

            d.press("back")
            time.sleep(random.randint(1, 5))
        else:
            print("首页没有加号按钮")
            return 0
        temp_xinwen += 1






added_friend = []





def qunfa(d,serial,nick_name,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian):
    global added_friend
    while(True):
        friends = d(resourceId='com.tencent.mm:id/kbq')
        print("meng=", friends)
        print(len(friends))

        count = 0
        for fridend in friends:
            print(fridend.info["text"])
            if(count < len(friends)-2): # 最后一个不让点击，点击会出问题
                if(fridend.info["text"] not in added_friend):
                    added_friend.append(fridend.info["text"])
                    random_click_view(d, fridend.info)
                    time.sleep(3)

                    result_sixin= sixin_fri(d,nick_name,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian)
                    if(result_sixin == 1):
                        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                    back_to_home(d)
                    time.sleep(3)
            count += 1

        time.sleep(3)

        if(d(textContains = "个朋友").exists(timeout=1)):
            print("已经到底了")
            return 99

        d.swipe_ext(Direction.FORWARD)
        time.sleep(3)

def sixin_fri(d,nick_name,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian):
    biaoqing = ["[得意]","[微笑]","[色]","[呲牙]","[调皮]","[偷笑]","[愉快]","[憨笑]","[亲亲]","[笑脸]","[奸笑]","[捂脸]","[嘿哈]","[破涕为笑]","[机智]","[皱眉]","[耶]","[吃瓜]","[加油]","[Emm]","[666]","[让我看看]","[哇]","[好的]","[社会社会]","[旺柴]","[握手]","[抱拳]","[拳头]","[OK]","[合十]","[啤酒]","[咖啡]","[蛋糕]","[玫瑰]","[太阳]","[庆祝]","[礼物]","[红包]","[發]","[福]","[烟花]","[爆竹]"]
    if (d(text='发消息').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text='发消息').info)
        random_click_view(d, d(text='发消息').info)
        time.sleep(random.randint(3, 10))
    else:
        print("没有发消息按钮")
        return 0

    if(shifouqufnawenzi):
        if (d(resourceId='com.tencent.mm:id/bkk').exists(timeout=3)):
            biaoqing_int = random.randint(0, len(biaoqing))
            biaoqing_count = random.randint(1, 4)
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(resourceId='com.tencent.mm:id/bkk').info)
            random_click_view(d, d(resourceId='com.tencent.mm:id/bkk').info)
            time.sleep(3)
            d(resourceId='com.tencent.mm:id/bkk').set_text("")
            time.sleep(1)
            d(resourceId='com.tencent.mm:id/bkk').set_text(qunfaneirong + biaoqing[biaoqing_int] * biaoqing_count)

            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='发送').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(text='发送').info)
            random_click_view(d, d(text='发送').info)
            time.sleep(3)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

    if(shifouqunfashoucang):
        sixin_shoucang(d, nick_name)

    if(str(qunfajiangeshijian).isdigit()):
        sleep_time_temp = random.randint(int(qunfajiangeshijian)-10,int(qunfajiangeshijian))
        if(int(sleep_time_temp) > 0):
            time.sleep(int(sleep_time_temp))
    else:
        time.sleep(10)
    return 1



def sixin_shoucang(d,nick_name):

    if (d(resourceId='com.tencent.mm:id/bkk').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/bkk').info)
        random_click_view(d,d(resourceId='com.tencent.mm:id/bkk').info)
        time.sleep(1)
        d(resourceId='com.tencent.mm:id/bkk').set_text("")
        time.sleep(2)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(resourceId='com.tencent.mm:id/bjz').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/bjz').info)
        random_click_view(d,d(resourceId='com.tencent.mm:id/bjz').info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text='我的收藏').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text='我的收藏').info)
        random_click_view(d,d(text='我的收藏').info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0


    if (d(text=nick_name).exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text=nick_name).info)
        random_click_view(d,d(text=nick_name).info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text="发送").exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text="发送").info)
        random_click_view(d,d(text="发送").info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0




def xiaoyewu(d,serial,search_path,sixin_comment):
    print("开始了1111111。。。")

    if (d(resourceId='com.tencent.mm:id/meb').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/meb').info)

        random_click_view(d, d(resourceId='com.tencent.mm:id/meb').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有加号按钮")
        return 0

    jiahaoyouqian_shijian_xiao = read_config("jiahaoyouqian_shijian_xiao")
    if (jiahaoyouqian_shijian_xiao == None):
        pengyouquan_huadong_cishu_xiao = 10
    jiahaoyouqian_shijian_da = read_config("jiahaoyouqian_shijian_da")
    if (jiahaoyouqian_shijian_da == None):
        jiahaoyouqian_shijian_da = 30

    search_key = get_top_line_and_del(search_path)
    if (search_key == None):
        return 88

    no_list = list(search_key)
    for n in no_list:
        cmd = f"adb -s {serial} shell input text " + str(n).strip()
        shell_neibu(cmd)
        time.sleep(0.3)
    time.sleep(random.randint(int(jiahaoyouqian_shijian_xiao), int(jiahaoyouqian_shijian_da)))

    if (d(textContains='查找手机').exists(timeout=3)):
        # d(textStartsWith='搜索').click()
        #d(textContains='查找手机').click()

        random_click_view(d,d(textContains='查找手机').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有搜索按钮")
        return 0
    time.sleep(random.randint(1, 10))

    #d.click(528,969)
    if (d(text='添加到通讯录').exists(timeout=3)):
        # d(textStartsWith='搜索').click()
        #d(text='添加到通讯录').click()

        random_click_view(d, d(text='添加到通讯录').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有搜索按钮")
        return 0
    time.sleep(random.randint(3, 10))

    if (d(text='该用户不存在').exists(timeout=1)):
        # d(text='该用户不存在').click()
        # time.sleep(3)3
        print("用户不存在")
        return 0
    elif (d(resourceId='com.tencent.mm:id/jlh').exists(timeout=1)):
        # d(text='该用户不存在').click()
        # time.sleep(3)3
        print("用户不存在")
        return 88
    elif (d(descriptionContains='头像').exists(timeout=1)):  # 出现这种情况证明已经加过好友啦
        # d(text='该用户不存在').click()
        # time.sleep(3)3
        print("已经加过好友啦")
        return 0
    # else:
    #     print("首页没有添加好友按钮")
    #     return 0
    time.sleep(3)
    if (d(resourceId='com.tencent.mm:id/m9y').exists(timeout=3)):  # 出现这种情况证明已经加过好友啦
        # d(text='该用户不存在').click()

        if (d(resourceId='com.tencent.mm:id/m9y').get_text() == sixin_comment):
            print("当前不用动")

        else:
            d(resourceId='com.tencent.mm:id/m9y').set_text("")
            d(resourceId='com.tencent.mm:id/m9y').set_text(sixin_comment)

        # random_click_view(d, d(resourceId='com.tencent.mm:id/m9y').info)
        time.sleep(random.randint(3, 10))
    else:
        print("meiyou 申请好友语view")
        #return 0

    if (d(resourceId='com.tencent.mm:id/m_1').exists(timeout=3)):  # 出现这种情况证明已经加过好友啦
        # d(text='该用户不存在').click()
        beizhu = str(search_key) + d(resourceId='com.tencent.mm:id/m_1').get_text()
        d(resourceId='com.tencent.mm:id/m_1').set_text(beizhu)
        time.sleep(random.randint(3, 10))
    else:
        print("meiyou 备注view")
        #return 0

    d.press("back")

    fasongqian_shijian_xiao = read_config("fasongqian_shijian_xiao")
    if (fasongqian_shijian_xiao == None):
        fasongqian_shijian_xiao = 10
    fasongqian_shijian_da = read_config("fasongqian_shijian_da")
    if (fasongqian_shijian_da == None):
        fasongqian_shijian_da = 30

    time.sleep(random.randint(int(fasongqian_shijian_xiao), int(fasongqian_shijian_da)))
    if (d(text='发送').exists(timeout=3)):
        d(text='发送').click()

        #random_click_view(d,d(text='发送').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有加号按钮")
        return 0
    #d.click(528, 2009)
    time.sleep(random.randint(3, 10))
    if (d(resourceId='com.tencent.mm:id/jlh').exists(timeout=5)):
        # d(text='该用户不存在').click()
        # time.sleep(3)3
        print("用户不存在")
        return 88
    #d.click(506, 668)
    return 1

def convert_to_number(input_str):
    # 去除字符串中的空格
    input_str = input_str.replace(" ", "")

    # 检查是否包含"万"
    if "万" in input_str:
        # 提取数字部分并转换为浮点数
        number_part = float(input_str.replace("万", ""))
        # 将数字部分乘以10000
        result = int(number_part * 10000)
    else:
        # 直接将字符串转换为整数（如果可能）或浮点数（如果不能直接转为整数）
        try:
            result = int(input_str)
        except ValueError:
            result = float(input_str)
            # 如果结果是浮点数且小数点后全为0，则转为整数
            if result.is_integer():
                result = int(result)

    return result


def conpare_dif(big,small):
    bigs = str(big).split("/")
    for big_t in bigs:
        if(str(small).count(big_t)>0):
            return 0
    return 1

def sixin(d,serial,sixin_comment,home_filter,c_t,age_small,age_big,fans_count_small,fans_count_big):
    biaoqing = ["[龇牙]","[哼]","[哦]","[呆住]","[贴贴]","[有八卦]","[尊嘟假嘟]","[你好呀]","[吹口哨]","[元旦快乐]","[新年快乐]","[出去丸]","[放假啦]","[进度50]","[我看行]","[稍等]","[让人头大]","[进度99]","[柴犬]","[羞涩]","[头盔]","[求求了]","[美滋滋]","[点点关注]","[星星眼]","[抱抱]","[放轻松]","[健身]","[礼花]","[稳]","[get]","[龇牙]","[皇冠]","[双鸡]","[发]","[灯笼]","[福字]","[鞭炮]","[元宝]","[钱]","[气球]","[赞]","[肌肉]","[早上好]","[优秀]","[网红]"]
    sixin_comment = sixin_comment + random.choice(biaoqing)
    result_con = conpare_dif(home_filter, c_t)
    print(f"home_filter={home_filter}, c_t={c_t},result_con={result_con}")
    if (result_con != 1):
        print("评论有关键字过滤")
        return 0
    if (d(resourceId='com.smile.gifmaker:id/label_name').exists(timeout=2)):
        lable_name = str(d(resourceId='com.smile.gifmaker:id/label_name').get_text())
        time.sleep(0.5)
        print(f"lable_name={lable_name}")
        if (lable_name.count("岁") > 0):
            age = int(lable_name.split("岁")[0])
            print(f"age_small={age_small}, age={age},age_big={age_big}")
            if ((age_small > age) or (age_big < age)):
                print("年龄不满足")
                return 0
    if (d(resourceId='com.smile.gifmaker:id/follower').exists(timeout=1)):  # 当前判断粉丝数量
        fans = d(resourceId='com.smile.gifmaker:id/follower').get_text()
        fans = int(convert_to_number(fans))
        print(f"fans={fans}, fans_count_small={fans_count_small},fans_count_big={fans_count_big}")
        if ((fans_count_small > fans) or (fans_count_big < fans)):
            print("粉丝数量不满足")
            return 0
    if (d(resourceId='com.smile.gifmaker:id/send_message_small_icon').exists(timeout=5)):
        d(resourceId='com.smile.gifmaker:id/send_message_small_icon').click()
        time.sleep(3)
    else:
        print("当前没有私信发送按钮")
        return 0

    # if (d(resourceId='com.smile.gifmaker:id/message_wrapper').exists(timeout=1)):
    #     return 0

    if (d(resourceId='com.smile.gifmaker:id/editor').exists(timeout=5)):
        d(resourceId='com.smile.gifmaker:id/editor').click()
        time.sleep(3)
    else:
        print("当前没有输入消息按钮")
        return 0

    comments = sixin_comment.split(" ")
    for comment_temp in comments:
        shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + str(comment_temp))
        shell_neibu(f"adb -s {serial} shell input  keyevent 279")
        time.sleep(1)
        shell_neibu(f"adb -s {serial} shell input  keyevent KEYCODE_SPACE")
        time.sleep(1)
    time.sleep(3)

    if (d(resourceId='com.smile.gifmaker:id/send_btn').exists(timeout=5)):
        d(resourceId='com.smile.gifmaker:id/send_btn').click()
        time.sleep(3)
    else:
        print("当前没有发送按钮")
        return 0

    return 1



def compare(txt,txt2):
    list_bb = list(txt)

    for bb in list_bb:
        if(str(txt2).count(bb)< 1):
            return False
    return True




def comment(d,language,serial,comment_path):
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

    if(d(text="发送").exists(timeout=2)):
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
class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("微信业务")
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
        self.titleLabel_renwu = QLabel("*"*55+"微信配置区"+"*"*55)
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
        self.caozuo_config = QLabel("*" * 55 + "脚本配置区" + "*" * 55)
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
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"加好友/群发统计"])
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

        self.horizontal_layout = QHBoxLayout()
        #self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button0 = QLabel("           ")
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("加好友")
        self.radio_button1.setChecked(True)
        self.radio_button8 = QCheckBox("群发文字")
        self.radio_button8.setChecked(True)
        self.radio_button9 = QCheckBox("群发收藏")
        self.radio_button9.setChecked(True)
        self.radio_button2 = QCheckBox("养号")
        self.radio_button2.setChecked(True)
        self.radio_button3 = QCheckBox("朋友圈")
        self.radio_button3.setChecked(True)
        self.radio_button4 = QCheckBox("视频号")
        self.radio_button4.setChecked(True)
        self.radio_button6 = QCheckBox("公众号")
        self.radio_button6.setChecked(True)
        self.radio_button7 = QCheckBox("新闻")
        self.radio_button7.setChecked(True)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addWidget(self.radio_button8)
        self.horizontal_layout.addWidget(self.radio_button9)
        self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button4)
        self.horizontal_layout.addWidget(self.radio_button6)
        self.horizontal_layout.addWidget(self.radio_button7)
        self.horizontal_layout.addWidget(self.radio_button5)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
          # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('                      添加好友数量:')

        huadongjiangexiao = get_value_by_key_pkl("shuju_config.pkl", "huadongjiangexiao")
        if (huadongjiangexiao != None):
            self.line_edit_from = QLineEdit(huadongjiangexiao)
        else:
            self.line_edit_from = QLineEdit("8")
        self.line_edit_from.setFixedWidth(100)

        self.label_to = QLabel('个')
        self.label_to.setFixedWidth(15)

        huadongjiangeda = get_value_by_key_pkl("shuju_config.pkl", "huadongjiangeda")
        if (huadongjiangeda != None):
            self.line_edit_to = QLineEdit(huadongjiangeda)
        else:
            self.line_edit_to = QLineEdit("30")
        self.line_edit_to.setFixedWidth(40)
        self.label_seconds = QLabel('                                                                                           ', self)

        self.label_from111 = QLabel('  年龄限制在')

        huadongcishuxiao = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuxiao")
        if (huadongcishuxiao != None):
            self.jiarenshurukuang = QLineEdit(huadongcishuxiao)
        else:
            self.jiarenshurukuang = QLineEdit("8")
        self.jiarenshurukuang.setFixedWidth(50)
        self.label_from222 = QLabel('至')
        self.label_from222.setFixedWidth(15)

        huadongcishuda = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuda")
        if (huadongcishuda != None):
            self.huadongcishu_big = QLineEdit(huadongcishuda)
        else:
            self.huadongcishu_big = QLineEdit("20")
        self.huadongcishu_big.setFixedWidth(40)
        self.label_fromci = QLabel('岁之间')




        self.label_from_time = QLabel('                      添加好友申请语:')

        yunxingshichang = get_value_by_key_pkl("shuju_config.pkl", "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("0")
        self.run_time.setFixedWidth(180)

        self.label_from_search = QLabel('        添加好友之间间隔')

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
        self.line_edit_to_search.setFixedWidth(40)
        self.label_seconds_search = QLabel('秒     ', self)
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout_diyihang = QHBoxLayout()
        self.h_layout_diyihang.addWidget(self.label_from_time)
        self.h_layout_diyihang.addWidget(self.run_time)
        self.h_layout_diyihang.addWidget(self.label_from_search)
        self.h_layout_diyihang.addWidget(self.line_edit_from_search)
        self.h_layout_diyihang.addWidget(self.label_to_search)
        self.h_layout_diyihang.addWidget(self.line_edit_to_search)
        self.h_layout_diyihang.addWidget(self.label_seconds_search)
        self.label_from111_kongge = QLabel('                  ')
        self.label_from111_shoucang = QLabel('群发私信内容：')
        self.label_from111_shoucang.setFixedWidth(80)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv")
        if (shoucanggailv != None):
            self.shoucang_gailv = QLineEdit(shoucanggailv)
        else:
            self.shoucang_gailv = QLineEdit("请输入群发内容")
        self.shoucang_gailv.setFixedWidth(250)
        self.label_from222_shoucang = QLabel('')

        self.label_from111_pinglun = QLabel('评论概率')
        self.label_from111_pinglun.setFixedWidth(50)

        pinglungailv = get_value_by_key_pkl("shuju_config.pkl", "pinglungailv")
        if (pinglungailv != None):
            self.shoucang_pinglun = QLineEdit(pinglungailv)
        else:
            self.shoucang_pinglun = QLineEdit("50")
        self.shoucang_pinglun.setFixedWidth(30)
        self.label_from222_pinglun = QLabel('        ')

        self.label_from111_dianzan = QLabel('群发间隔时间：')
        self.label_from111_dianzan.setFixedWidth(80)

        dianzangailv = get_value_by_key_pkl("shuju_config.pkl", "dianzangailv")
        if (dianzangailv != None):
            self.shoucang_dianzan = QLineEdit(dianzangailv)
        else:
            self.shoucang_dianzan = QLineEdit("50")
        self.shoucang_dianzan.setFixedWidth(50)
        self.label_from222_dianzan = QLabel('秒     ')

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
        self.h_layout_disanhang.addWidget(self.label_from111_shoucang)
        self.h_layout_disanhang.addWidget(self.shoucang_gailv)
        self.h_layout_disanhang.addWidget(self.label_from222_shoucang)
        #self.h_layout_disanhang.addWidget(self.label_from111_pinglun)
        #self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        self.h_layout_disanhang.addWidget(self.label_from222_pinglun)

        #self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        #self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
        #self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        #self.h_layout_disanhang.addWidget(self.label_from111_kongge222)


        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(5)
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        self.h_layout.addWidget(self.label_to)
        # self.h_layout.addWidget(self.line_edit_to)
        self.h_layout.addWidget(self.label_seconds)
        #
        # self.h_layout.addWidget(self.label_from111)
        # self.h_layout.addWidget(self.jiarenshurukuang)
        # self.h_layout.addWidget(self.label_from222)
        # self.h_layout.addWidget(self.huadongcishu_big)
        # self.h_layout.addWidget(self.label_fromci)

        #self.h_layout.setSpacing(5)
        # 设置布局与窗口边框之间的边距（例如，设置为 0 像素）
        #self.h_layout.setContentsMargins(0, 0, 0, 0)

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

        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择好友文件路径配置:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl","file_path")
        if(file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入搜索文件路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件",self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

        #以下是评论文件选择器
        self.h_layout_dir_comment = QHBoxLayout()
        self.label_file_comment = QLabel("                          请选择公众号文件路径:")
        self.h_layout_dir_comment.addWidget(self.label_file_comment)

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        if (file_temp_path_comment != None):
            self.file_textbox_comment = QLineEdit(file_temp_path_comment)
        else:
            self.file_textbox_comment = QLineEdit("请输入公众号文件路径")
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
        self.file_button_gouwu = QPushButton("选择文件", self)
        self.temp_gouwu = QLabel("                          ")
        self.h_layout_dir_gouwu.addWidget(self.file_button_gouwu)
        self.h_layout_dir_gouwu.addWidget(self.temp_gouwu)

        self.clear_task_config_button = QPushButton('一键清除任务列表', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)




        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        central_widget.setFixedWidth(650)
        layout.setSpacing(0)  # 设置布局间距为0
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.caozuo_config)

        layout.addLayout(self.h_layout_kongge)
        layout.addLayout(self.h_layout_dir)
        layout.addLayout(self.h_layout_kongge1)
        layout.addLayout(self.h_layout_dir_comment)
        layout.addLayout(self.h_layout_kongge2)
        # layout.addLayout(self.h_layout_dir_gouwu)
        layout.addLayout(self.h_layout_kongge8)
        layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge3)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge4)
        layout.addLayout(self.h_layout_disanhang)
        layout.addLayout(self.h_layout_kongge5)

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
        self.execute_button.resize(100,30)

        self.button_gang.addWidget(self.execute_button)

        self.button_gang.addWidget(self.clear_task_config_button)
        self.execute_button_delete = QPushButton("删除")
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





    def execute_button_clicked(self):
        #print("---------------")

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

        if(self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "vx添加好友")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        #self.scroll_area.ensureWidgetVisible(100)
        if(self.radio_button1.isChecked() == True):
            tasks.append("sixin")
        if (self.radio_button2.isChecked() == True):
            tasks.append("yanghao")
        if (self.radio_button8.isChecked() == True):
            tasks.append("qunfa_wenzi")
        if (self.radio_button9.isChecked() == True):
            tasks.append("qunfa_wenzi")
        # if (self.radio_button3.isChecked() == True):
        #     tasks.append("pinglun")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")
        print("tasks------------",tasks)
        if(os.path.isfile(self.file_textbox.text())):
            print("手机号配置文件加载")
        else:
            print("手机号配置文件buzai")
            return
        if (os.path.isfile(self.file_textbox_comment.text())):
            print("评论文件加载")
        else:
            print("公众号配置文件不在")
            return

        thread = threading.Thread(target=self.thread_temp,args=(tasks,))
        thread.start()


        self.selected_ids = []
    def thread_temp(self,tasks):
        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,self.file_textbox.text(),self.file_textbox_comment.text(),tasks,self.run_time.text(),self.line_edit_from_search.text(),self.line_edit_to_search.text(),self.line_edit_from.text(),self.line_edit_to.text(),self.jiarenshurukuang.text(),self.shoucang_gailv.text(),self.shoucang_pinglun.text(),self.shoucang_dianzan.text(),self.shoucang_guanzhu.text(),self.huadongcishu_big.text(),self.file_textbox_gouwu.text(),self.radio_button2.isChecked(),self.radio_button3.isChecked(),self.radio_button4.isChecked(),self.radio_button6.isChecked(),self.radio_button7.isChecked(),self.radio_button8.isChecked(),self.radio_button9.isChecked(),self.shoucang_gailv.text(),self.shoucang_dianzan.text()))
            #手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数、粉丝数量大、年龄限制小、收藏、评论、点赞、关注，年龄限制大，购物文件配置路径、是否私信视频作者，是否私信视频评论用户
            #threads.append(thread)
            thread.start()
            time.sleep(random.randint(2,5))

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