from concurrent.futures import ThreadPoolExecutor

import cv2
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
    QFileDialog, QTextEdit, QComboBox
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
import uiautomator2 as u2
import socket
from functools import wraps

def timeout(seconds):
    """超时装饰器，限制函数执行时间"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 保存原始超时设置
            original_timeout = socket.getdefaulttimeout()
            try:
                # 设置超时时间
                socket.setdefaulttimeout(seconds)
                # 执行被装饰的函数
                return func(*args, **kwargs)
            finally:
                # 恢复原始超时设置
                socket.setdefaulttimeout(original_timeout)
        return wrapper
    return decorator

@timeout(10)  # 设置30秒连接超时
def get_device(serial):
    """
    连接指定设备并返回设备对象
    :param serial: 设备序列号
    :return: uiautomator2设备对象
    :raises: ADBError 当连接失败或超时
    """
    try:
        # 尝试连接设备
        d = u2.connect(serial)
        # 验证连接是否有效（获取设备信息）
        print(d.info)
        # 移除所有监听器
        d.watcher.remove()
        return d
    except BaseException as e:
        # 捕获ADB错误和超时错误
        print(f"设备 {serial} 连接超时或失败: {str(e)}")
        get_device(serial)

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


def get_random_line_from_file(file_path):
    """
    从指定的文本文件中随机选择并返回一行。

    :param file_path: 文本文件的路径
    :return: 随机选择的一行文本
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']  # 尝试的编码列表

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                lines = file.readlines()
            if lines:
                return random.choice(lines).strip()
            else:
                return None
        except UnicodeDecodeError:
            continue  # 尝试下一个编码
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return None
        except Exception as e:
            print(f"读取文件时发生未知错误: {e}")
            return None

    print(f"无法使用任何编码读取文件 {file_path}")
    return None


start_time = datetime.now()
def operate_device(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,shipinhuadongcishu,gouwu,shifouguanbidouyin,douyinguanjianzi,douyinsuosuoguanjianzi,douyinshiyongguanjianzi,moshi,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai):
    count_zong = 0
    print("douyinsuosuoguanjianzi=",douyinsuosuoguanjianzi)
    print(moshi,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai)
    while(True):
        try:
            import datetime
            import time
            if(int(datetime.datetime.now().timestamp()) > 1842548805):
                return

            result = main(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                          swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,shipinhuadongcishu,gouwu,douyinguanjianzi,douyinsuosuoguanjianzi,douyinshiyongguanjianzi,moshi,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai)
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
                    cmd = f"adb -s {serial} shell input keyevent 3"
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    shell_neibu(cmd)
                    time.sleep(0.5)
                    # shell_neibu(cmd)
                    # time.sleep(0.5)
                    # shell_neibu(cmd)
                    # time.sleep(0.5)
                    # shell_neibu(cmd)

                return
            count_zong += 1
        except BaseException as ee:
            print("崩溃了",ee)
            operate_device(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                           swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,shipinhuadongcishu,gouwu,shifouguanbidouyin,douyinguanjianzi,douyinsuosuoguanjianzi,douyinshiyongguanjianzi,moshi,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai)


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
def main(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,count_zong,shipinhuadongcishu,gouwu,douyinguanjianzi,douyinsuosuoguanjianzi,douyinshiyongguanjianzi,moshi,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai):
    print("---->",serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,count_zong,shipinhuadongcishu,gouwu,douyinguanjianzi,douyinsuosuoguanjianzi,douyinshiyongguanjianzi)

    d = None
    try:
        d = get_device(serial)
    except BaseException as e:
        print("当前连接失败---------------------------------------------------------------=",e)
        main(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small, swipe_big,
             swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong, shipinhuadongcishu, gouwu, douyinguanjianzi,
             douyinsuosuoguanjianzi, douyinshiyongguanjianzi, moshi, zhibojianshoucang, zhibojianpinglun,
             zhibojiandengpai)
        return
    if (os.path.isfile("pause.txt")):
        os.remove("pause.txt")

    if (len(task) == 0):
        return
    print("douyinsuosuoguanjianzi111=", douyinsuosuoguanjianzi)
    print("gouwu=", gouwu)
    douyinguanjianzis = []
    if (douyinguanjianzi):
        douyinguanjianzis = str(douyinguanjianzi).split("_")
    douyinsousuoguanjianzis = []
    if (douyinsuosuoguanjianzi):
        douyinsousuoguanjianzis = str(douyinsuosuoguanjianzi).split("_")
    print("douyinsousuoguanjianzis=", douyinsousuoguanjianzis)

    shiyongguanjianziss = []
    if (douyinshiyongguanjianzi):
        shiyongguanjianziss = str(douyinshiyongguanjianzi).split("_")
    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    run_time = int(run_time)
    if ("shiyong" in task):
        run_time = int(run_time)
        change_small = int(change_small)
        chang_big = int(chang_big)
        swipe_small = int(swipe_small)
        swipe_big = int(swipe_big)
        swipe_count = int(swipe_count)
        shoucang = int(shoucang)
        pinglun = int(pinglun)
        dianzan = int(dianzan)
        guanzhu = int(guanzhu)
        shipinhuadongcishu = int(shipinhuadongcishu)

        if (check_time_difference(run_time * 60)):
            return "88"

        # ocr_processor = OCRProcessor()
        print("开始了。。。")
        ocr_processor = ""

        time.sleep(1)

        # 注册一个watcher，当弹窗上的“确定”按钮出现时，点击它

        # 开始后台监控

        if (1 == 0):
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme", stop=True)
        else:
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme")
            backToHome(d)
        #time.sleep(int(random.randint(5, 300)))

        time.sleep(2)
        kill_count = 0

        if (check_time_difference(run_time * 60)):
            return "88"
        # 当前判断在不在首页，如果有home 或者是首页，则认为当前在首页了
        if (d(text='推荐').exists(timeout=15)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return
        count_swipe = 0
        if (check_time_difference(run_time * 60)):
            return "88"
        swipe_count = random.uniform(swipe_count, shipinhuadongcishu)
        # while (count_swipe < swipe_count):
        #     wait_time = random.uniform(swipe_small, swipe_big)
        #     d.swipe_points([(500, 1500), (600, 200)], 0.2)
        #     time.sleep(wait_time)
        #     count_swipe += 1
        language = 0
        # 点击首页的搜索按钮
        if (check_time_difference(run_time * 60)):
            return "88"
        if (check_time_difference(run_time * 60)):
            return "88"
        # d.click(200, 800)
        time.sleep(3)

        while(True):
            print("")
            if (d(text='点击进入直播间').exists(timeout=3)):
                print("当前是直播间")
                flagzzz = False

                for guanjianzi in shiyongguanjianziss:
                    print("guanjianzi=", guanjianzi)
                    if (d(descriptionContains=guanjianzi).exists(timeout=1)):
                        flagzzz = True
                        break
                if(flagzzz == True):
                    print("dangqian直播间满足情况")
                    if (d(text="点击进入直播间").exists(timeout=1)):
                        return "88"
                else:
                    print("dangqian直播间不满足情况")

            time.sleep(random.randint(1,5))
            beisaier(d)
            time.sleep(random.randint(1, 5))

        print("当前遇到对的直播间了")

        while(True):
            if(d(text="推荐").exists(timeout=1)):
                print("当前在首页")
                return "88"
            # else:
            #     backToHome(d)
            if(os.path.exists("pause.txt")):
                break
            time.sleep(1)
        return "88"



    if ("yanghao_sousuo" in task):
        print("当前搜索养号")

        for sousuoguanjianzi in douyinsousuoguanjianzis:
            d.app_start(package_name="com.ss.android.ugc.aweme")
            backToHome(d)
            result_intott = search_into(d,sousuoguanjianzi)
            if(result_intott != 1):
                print("当前没有直播间")
                continue
            else:
                print("dangqian 有直播间")
                swipe_count0 = random.uniform(int(swipe_count), int(shipinhuadongcishu))
                swipe_count1 = random.uniform(int(swipe_count), int(shipinhuadongcishu))
                time.sleep(swipe_count1)
                live_douyin_detail(d,gouwu,11,11,11,11,swipe_count1,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai)





    if("yanghao_shanghua" in task):
        run_time = int(run_time)
        change_small = int(change_small)
        chang_big = int(chang_big)
        swipe_small = int(swipe_small)
        swipe_big = int(swipe_big)
        swipe_count = int(swipe_count)
        shoucang = int(shoucang)
        pinglun = int(pinglun)
        dianzan = int(dianzan)
        guanzhu = int(guanzhu)
        shipinhuadongcishu = int(shipinhuadongcishu)

        if (check_time_difference(run_time * 60)):
            return "88"

        # ocr_processor = OCRProcessor()
        print("开始了。。。")
        ocr_processor = ""

        time.sleep(1)

        # 注册一个watcher，当弹窗上的“确定”按钮出现时，点击它

        # 开始后台监控

        if (1 == 0):
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme", stop=True)
        else:
            # d.app_start(package_name="ca.zgrs.clipper")
            # time.sleep(1)
            d.app_start(package_name="com.ss.android.ugc.aweme")
            backToHome(d)
        #time.sleep(int(random.randint(5, 300)))

        time.sleep(1)
        kill_count = 0

        if (check_time_difference(run_time * 60)):
            return "88"
        # 当前判断在不在首页，如果有home 或者是首页，则认为当前在首页了
        if (d(text='推荐').exists(timeout=15)):
            print("当前在首页了。。。。。。。。")
        else:
            print("当前bu在首页了。。。。。。。。")
            return
        count_swipe = 0
        if (check_time_difference(run_time * 60)):
            return "88"
        swipe_count = random.uniform(swipe_count, shipinhuadongcishu)
        # while (count_swipe < swipe_count):
        #     wait_time = random.uniform(swipe_small, swipe_big)
        #     d.swipe_points([(500, 1500), (600, 200)], 0.2)
        #     time.sleep(wait_time)
        #     count_swipe += 1
        language = 0
        # 点击首页的搜索按钮
        if (check_time_difference(run_time * 60)):
            return "88"
        if (check_time_difference(run_time * 60)):
            return "88"
        # d.click(200, 800)
        time.sleep(3)
        if (1 == 1):
            if (d(descriptionContains='点赞').exists(timeout=3)):
                # d(text='添加评论...').click()
                print("当前在播放详情页里头")
                time.sleep(3)
                print("当前在播放详情页里头")
            elif(d(text='点击进入直播间').exists(timeout=3)):
                print("zhibojian ")
            else:
                print("当前没有添加评论a 。。。。。。。。")
                return

        # shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + "food good")
        # shell_neibu(f"adb -s {serial} shell input  keyevent 279")
        time.sleep(2)
        # d.click(1000, 1400)
        # time.sleep(2)
        if (check_time_difference(run_time * 60)):
            return "88"
        b_count = 0
        aa = swipe_count
        if (swipe_count == 0):
            aa = 10000
        swipe_count_temp = random.uniform(change_small, chang_big)
        print("swipe_count_temp--", swipe_count_temp)
        while (b_count < 1000000):
            backToHome(d)
            if(b_count != 0):
                time.sleep(1)
                beisaier(d)
                time.sleep(0.5)
            b_count += 1
            # update_pkl_add_one("/shuju/"+serial+".pkl","tongji")
            update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")

            print("当前在循环里头")
            if("zhibojian" in moshi):
                print("当前直播间养号")
                if (d(text='点击进入直播间').exists(timeout=0.5)):
                    print("当前是直播间")
                    flagzzz = False

                    for guanjianzi in douyinguanjianzis:
                        print("guanjianzi=", guanjianzi)
                        if (d(descriptionContains=guanjianzi).exists(timeout=0.8)):
                            flagzzz = True
                            break
                    if(flagzzz == True):
                        wait_time = random.uniform(swipe_small, swipe_big)
                        print("wait_time=====", wait_time)
                        time.sleep(wait_time)
                        print("dangqian直播间满足情况")
                        if (d(text="点击进入直播间").exists(timeout=0.2)):
                            d(text="点击进入直播间").click()
                            swipe_count1 = random.uniform(swipe_count, shipinhuadongcishu)
                            swipe_count2 = random.uniform(swipe_count, shipinhuadongcishu)
                            time.sleep(swipe_count2)
                            live_douyin_detail(d,gouwu,11,11,11,11,swipe_count1,zhibojianshoucang, zhibojianpinglun, zhibojiandengpai)
                            backToHome(d)
                    else:
                        print("dangqian直播间不满足情况")
                    backToHome(d)
                    time.sleep(0.5)
                    beisaier(d)
                    time.sleep(0.5)
                    continue
            if("duanshipin" in moshi):
                print("当前短视频养号")
                content_title = []
                if (d(resourceId='com.ss.android.ugc.aweme:id/title').exists(timeout=1)):
                    content_title.append(d(resourceId='com.ss.android.ugc.aweme:id/title').get_text())
                if (d(resourceId='com.ss.android.ugc.aweme:id/desc').exists(timeout=0.1)):
                    content_title.append(d(resourceId='com.ss.android.ugc.aweme:id/desc').get_text())
                print("content_title=",content_title)

                flagg = True
                for guanjianzi in douyinguanjianzis:
                    print("guanjianzi=",guanjianzi)
                    if(str(content_title).count(guanjianzi) > 0 ):
                        print('当前满足')
                        flagg = False
                        #continue
                    else:
                        print('当前bu满足')


                if(flagg == True):
                    #time.sleep(1)
                    # beisaier(d)
                    # time.sleep(0.5)
                    continue

                print(shoucang, dianzan, pinglun, guanzhu)
                wait_time = random.uniform(swipe_small, swipe_big)
                print("wait_time=====", wait_time)
                time.sleep(wait_time)

                if (d(descriptionContains='点赞').exists(timeout=3)):
                    if (d(descriptionContains='评论').exists(timeout=3)):
                        print("短视频")
                    if (random_boolean_with_probability(shoucang)):
                        print("当前可以收藏")
                        if (d(descriptionContains='收藏').exists(timeout=3)):
                            print("点击收藏")
                            d(descriptionContains='收藏').click()
                            print("点击收藏")
                        time.sleep(1.5)
                    if (random_boolean_with_probability(dianzan)):
                        print("当前可以dianzan")
                        if (d(descriptionContains='点赞').exists(timeout=3)):
                            print("点击点赞")
                            d(descriptionContains='点赞').click()
                            print("点击收藏")
                        time.sleep(1.5)
                    if (random_boolean_with_probability(pinglun)):
                        print("当前可以pinglun",comment_path)
                        result = comment(d, language, serial, comment_path)
                        if(result != "1"):
                            time.sleep(2)
                            backToHome(d)
                            d.swipe_points([(500, 1500), (600, 200)], 0.2)
                            time.sleep(2)
                            continue
                        backToHome(d)
                        time.sleep(1.5)
                    if (random_boolean_with_probability(guanzhu)):
                        print("当前可以guanzhu")
                        if (d(descriptionContains='关注').exists(timeout=3)):
                            print("点击关注")
                            d(descriptionContains='关注').click()
                            print("点击关注")
                            time.sleep(2)

                            if (d(descriptionContains='作品').exists(timeout=3)):
                                print("点击关注")
                                d.press("back")
                                time.sleep(2)
                        time.sleep(1.5)
            if (check_time_difference(run_time * 60)):
                return "88"
            d.swipe_points([(500, 1500), (600, 200)], 0.2)
            time.sleep(2)

            if (check_time_difference(run_time * 60)):
                return "88"
def live_douyin_detail(d,gouwu,guanzhugailv,fensituangailv,hudonggailv,fudaigailv,dengdaishijian,zhibojianshoucang,zhibojianpinglun,zhibojiandengpai):
    # 点击关注
    print(guanzhugailv,fensituangailv,hudonggailv,fudaigailv,dengdaishijian)
    guanzhugailv_int = random.randint(1, 100)
    print("guanzhugailv_int=",guanzhugailv_int)
    if(int(zhibojianshoucang)> int(guanzhugailv_int)):
        print("fudai_path")

        time.sleep(random.randint(1, 5))
        print("222")
        if (d(resourceId='com.ss.android.ugc.aweme:id/i6m').exists(timeout=3)):
            print(" 关注。。。。。。。。")
            print("333")
            d(resourceId='com.ss.android.ugc.aweme:id/i6m').click()
            time.sleep(random.randint(1, 15))
        elif(d(text='关注').exists(timeout=3)):
            print(" 关注。。。。。。。。")
            print("333")
            d(text='关注').click()
            time.sleep(random.randint(1, 15))
        else:
            print("dangqian 没有关注。。。。。。。。")
            # return
        print("fudai_path")
        backTody_live_detail(d)

    # 点击粉丝团
    if (int(zhibojiandengpai) > random.randint(1, 100)):
        time.sleep(random.randint(1, 5))
        if (d(descriptionContains='加入购物粉丝团').exists(timeout=3)):
            print(" 加入购物粉丝团。。。。。。。。")
            d(descriptionContains='加入购物粉丝团').click()
            time.sleep(random.randint(1, 5))
        elif (d(descriptionContains='加入粉丝团').exists(timeout=3)):
            print(" 加入粉丝团。。。。。。。。")
            d(descriptionContains='加入粉丝团').click()
            time.sleep(random.randint(1, 5))
        else:
            print("dangqian 没有关注。。。。。。。。")
            # return
        if (d(text='加入粉丝团').exists(timeout=3)):
            print(" 加入购物粉丝团。。。。。。。。")
            d(text='加入粉丝团').click()
            time.sleep(random.randint(1, 5))
        else:
            print("dangqian 没有关注。。。。。。。。")
            # return
            width, height = d.window_size()
            d.click(width/2,height-162)
            time.sleep(random.randint(1, 5))
        print("uuu")
        backTody_live_detail(d)
    # 下面开始互动
    # time.sleep(random.randint(1, 5))
    if (int(zhibojianpinglun) > random.randint(1, 100)):
        if (d(textContains='说点什么').exists(timeout=3)):
            print("直播间互动")
            d(textContains='说点什么').click()
            time.sleep(random.randint(3, 5))
            if (gouwu):
                content_pinglun = str(get_random_line_from_file(gouwu))
            else:
                content_pinglun = str("666")
            if (d(className='android.widget.EditText').exists(timeout=3)):
                print("直播间互动")
                d(className='android.widget.EditText').set_text(str(content_pinglun))
                time.sleep(random.randint(3, 5))
                if (d(text='发送').exists(timeout=3)):
                    print("直播间互动")
                    d(text='发送').click()
                    time.sleep(random.randint(3, 5))
                else:
                    print("dangqian 没有关注。。。。。。。。")
            else:
                print("dangqian 没有关注。。。。。。。。")
        else:
            print("dangqian 没有关注。。。。。。。。")
            # return
        print("yyyyyy")
        backTody_live_detail(d)
    if (int(fudaigailv) > random.randint(1, 11)):
        if (d(textContains='超级福袋').exists(timeout=0.1)):
            while (True):
                if (d(textContains='超级福袋').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("超级福袋")

                    if (d(textContains='超级福袋').exists(timeout=0.1)):
                        # time.sleep(sleep_time_phone)
                        if (d(textContains='超级福袋').exists(timeout=0.1)):
                            # d(textContains='超级福袋').click()
                            print("开始点击超级福袋")

                            random_click_view(d, d(textContains='超级福袋').info)
                            time.sleep(5)

                            fudai_flag = 1
                        flag = 1
                else:
                    print("没有超级福袋")  # return
                # sleep_sleep(class_phone)

                if (d(textContains='一键发表评论').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("有一件发表评论")
                    # d(textContains='一键发表评论').click()
                    random_click_view(d, d(textContains='一键发表评论').info)
                    flag = 1
                else:
                    print("没有一件发表评论")
                    # return
                # sleep_sleep(class_phone)
                if (d(text='参与抽奖').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("参与抽奖")
                    # d(text='加入粉丝团').click()
                    random_click_view(d, d(text='参与抽奖').info)
                    flag = 1

                else:
                    print("没有参与抽奖")

                if (d(text='加入粉丝团').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("有加入粉丝团")
                    # d(text='加入粉丝团').click()
                    random_click_view(d, d(text='加入粉丝团').info)
                    flag = 1

                else:
                    print("没有加入粉丝团")
                    # return
                if (d(text='去发表评论').exists(timeout=0.1)):  # 这种是需要 在输入框内 评论的
                    # d(text='添加评论...').click()
                    # d(text='去发表评论').click()
                    random_click_view(d, d(text='去发表评论').info)
                    print("有去发表评论")
                    flag = 1

                    if (d(text='发送').exists(timeout=0.1)):  # 这种是需要 在输入框内 评论的
                        # d(text='添加评论...').click()
                        # d(text='发送').click()
                        random_click_view(d, d(text='发送').info)
                        print("有发送按钮")
                else:
                    print("没有去发表评论")
                    # return
                # sleep_sleep(class_phone)

                if (d(text='我的等级特权').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("有我的等级特权")
                    d.press("back")
                    flag = 1
                else:
                    print("没有我的等级特权")
                    # return

                if (d(text='已参与').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    print("有已参与，等着就行了")
                    flag = 1
                else:
                    print("没有已参与")

                if (d(text='我知道了').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    # time.sleep(random.randint(2,15))
                    # time.sleep(sleep_time_phone)
                    # time.sleep(sleep_time_phone)
                    if (d(text='我知道了').exists(timeout=0.1)):
                        # d(text='我知道了').click()
                        random_click_view(d, d(text='我知道了').info)
                        print("有我知道啦")
                        flag = 1
                        fudai_flag = 0
                        time.sleep(5)
                        lingling = d(text='00')
                        if (len(lingling) > 1):
                            print("当前需要返回")
                            d.press("back")
                    # time.sleep(sleep_time_phone)

                else:
                    print("没有我知道啦")
                # sleep_sleep(class_phone)

                if (d(text='立即领取奖品').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    d(text='立即领取奖品').click()
                    print("立即领取奖品")
                    flag = 1
                    fudai_flag = 0
                    time.sleep(5)
                    lingling = d(text='00')
                    if (len(lingling) > 1):
                        print("当前需要返回")
                        d.press("back")

                else:
                    print("没有立即领取奖品")
                # return
                if (d(text='参与成功 等待开奖').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    # d(text='参与成功 等待开奖').click()
                    print("有参与成功，等着就行了")
                    flag = 1
                    break
                else:
                    print("没有有参与成功，等着就行了")
                    # return
                # sleep_sleep(class_phone)
                if (d(text='开始观看直播任务').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    d(text='开始观看直播任务').click()
                    print("开始观看直播任务")
                    flag = 1
                else:
                    print("没有开始观看直播任务")
                    # return
                if (d(text='还需看播').exists(timeout=0.1)):
                    # d(text='添加评论...').click()
                    # d(text='参与成功 等待开奖').click()
                    print("还需看播，等着就行了")
                    flag = 1
                else:
                    print("没有还需看播")

                if (d(text='直播已结束').exists(timeout=0.1)):  # 判断主播退出直播间
                    # d(text='添加评论...').click()
                    # d(text='参与成功 等待开奖').click()
                    return "66"
                else:
                    print("没有直播已结束")

                if (d(text='开始检测').exists(timeout=0.1)):  # 判断有没有用户校验
                    # d(text='添加评论...').click()
                    # d(text='参与成功 等待开奖').click()
                    return "99"
                else:
                    print("没有开始检测")
        backTody_live_detail(d)
    zong_count = dengdaishijian
    small_count = 0
    while (small_count < zong_count):
        small_count += 4
        time.sleep(1)
        backTody_live_detail(d)
def random_click_view(d,view):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left)+random.randint(2,15)
    random_y = int(bottom) + random.randint(2,15)
    print("开始点击")
    print(random_x,random_y)

    d.click(random_x,random_y)
def search_into(d,sousuoguanjianzi):
    if (d(text='推荐').exists(timeout=3)):
        d.click(d.info["displayWidth"] - 50, 180)
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    search_key = str(sousuoguanjianzi)
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
    counttt = 0
    while(counttt < 3):
        if (d(description=search_key+'直播中').exists(timeout=3)):
            print("找到直播了")
            d(description=search_key + '直播中').click()
            return 1
        elif(d(description='直播中，'+search_key+"，按钮").exists(timeout=3)):
            print("找到直播了")
            d(description='直播中，'+search_key+"，按钮").click()
            return 1


        time.sleep(1)
        beisaier(d)
        time.sleep(1)
        counttt += 1


def compare(txt,txt2):
    list_bb = list(txt)

    for bb in list_bb:
        if(str(txt2).count(bb)< 1):
            return False
    return True

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
    # if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
    #     print("善语结善缘，恶言伤人心")
    #     d(text="善语结善缘，恶言伤人心").click()
    #     time.sleep(1.5)
    # elif(d(text="作者仅允许自己评论").exists(timeout=3)):
    #     return "66"
    # else:
    #     print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
    #     return "66"

    if (d(textContains='评论').exists(timeout=1)):
        print("，按钮")
        pingluns = d(textContains='评论')
        pingluns[-1].click()
        time.sleep(2)
        # pingluns = d(textContains='评论')
        # pingluns[-1].set_text(random.choice(comments))   className="android.widget.EditText"
        time.sleep(1)
    else:
        print("当前没有善缘按钮")
        return "66"




    pinglunneirong = str(get_random_line_from_file(comment_path))
    print("pinglunneirong=",pinglunneirong)
    comment_t = str(pinglunneirong)
    # comments = comment_t.split(" ")
    # for comment_temp in comments:
    #     shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + str(comment_temp))
    #     shell_neibu(f"adb -s {serial} shell input  keyevent 279")
    #     time.sleep(1)
    #     shell_neibu(f"adb -s {serial} shell input  keyevent KEYCODE_SPACE")
    #     time.sleep(1)
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
    # if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
    #     print("善语结善缘，恶言伤人心")
    #     d(text="善语结善缘，恶言伤人心").set_text(str(comment_t))
    #     time.sleep(1.5)
    # else:
    #     print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
    #     return

    if (d(className="android.widget.EditText").exists(timeout=10)):
        print("，按钮")
        # pingluns[-1].set_text(random.choice(comments))   className="android.widget.EditText"
        d(className="android.widget.EditText").set_text(str(comment_t))
        time.sleep(1)

    else:
        print("当前buneng 输入内容啊")
        return


    time.sleep(1)

    if(d(text="发送").exists(timeout=2)):
        print("")
        d(text="发送").click()
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)

    return "1"

def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)



lock888 = threading.Lock()
def jundge(d,s):
    with lock888:
        path = photo(s)
        screenshot_image = d.screenshot()
        screenshot_image.save(path)
        image = cv2.imread(path)
        ee = d(textContains="看我的真实姓名")
        if(ee):
            # 选择像素点位置
            bounds = ee.info['bounds']
            print(bounds)
            # bounds是一个字符串，形如"[x1, y1][x2, y2]"
            # 其中(x1, y1)是左上角的坐标，(x2, y2)是右下角的坐标
            center_x = (bounds['left'] + bounds['right']) / 2.0
            center_y = (bounds['top'] + bounds['bottom']) / 2.0
            print(center_x, center_y)
            # 获取颜色值
            x_d, y_d = d.window_size()
            print(x_d, y_d)
            color = get_color_at_position(image, int(x_d - 183), int(center_y))
            # 打印颜色值
            print(f"The color at ({int(x_d - 183)}, {center_y}) is: R={color[0]}, G={color[1]}, B={color[2]}")
            print(color)
            print(len(color))
            print(color[1], color[2])
            if (len(color) == 3):
                if ((color[1] > 200) and (color[2] > 200)):
                    print("属于被删除了")
                    return False
                else:
                    print("没有被删除，可以统计")
                    return True
            return False
def backTody_live_detail(d):
    dd =  0
    time.sleep(3)
    while(dd < 4):
        print("888")
        dd += 1
        elements = d(descriptionContains='表情入口')  # 获取所有文本为'some_text'的元素
        elements1 = d(textContains='说点什么')
        elements2 = d(descriptionContains='礼物')
        #print(len(elements))
        if(len(elements)>0):
            print("888")
            return "1"
        if (len(elements1) > 0):
            print("999")
            return "1"
        if (len(elements2) > 0):
            print("1010101")
            return "1"
        time.sleep(1.5)
        print("222222")
        d.press("back")
        time.sleep(1.5)
def backToHome(d):
    dd =  0
    time.sleep(1)
    while(dd < 10):
        elements = d(text='推荐')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        #time.sleep(1.5)
        print("还得返回")
        d.press("back")
        time.sleep(0.5)
class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("dy业务")
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
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"滑动统计"])
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

        self.radio_button1 = QCheckBox("dy搜索养号")
        self.radio_button1.setChecked(False)
        self.radio_button2 = QCheckBox("自动上滑养号")
        self.radio_button2.setChecked(False)
        self.radio_button4 = QCheckBox("使用")
        self.radio_button4.setChecked(False)
        self.radio_button3 = QCheckBox("养号之后是否关闭抖音")
        self.radio_button3.setChecked(False)
        # self.radio_button4 = QCheckBox("删除直通")
        # self.radio_button4.setChecked(True)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.radio_button4)
        self.horizontal_layout.addWidget(self.radio_button3)

        self.horizontal_layout.addWidget(self.radio_button5)

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

        self.label_from111 = QLabel(' 进入直播间等待时间')

        huadongcishuxiao = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuxiao")
        if (huadongcishuxiao != None):
            self.jiarenshurukuang = QLineEdit(huadongcishuxiao)
        else:
            self.jiarenshurukuang = QLineEdit("8")
        self.jiarenshurukuang.setFixedWidth(40)
        self.label_from222 = QLabel('至')
        self.label_from222.setFixedWidth(15)

        huadongcishuda = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuda")
        if (huadongcishuda != None):
            self.huadongcishu_big = QLineEdit(huadongcishuda)
        else:
            self.huadongcishu_big = QLineEdit("20")
        self.huadongcishu_big.setFixedWidth(40)
        self.label_fromci = QLabel('秒')




        self.label_from_time = QLabel('                        脚本运行时长')

        yunxingshichang = get_value_by_key_pkl("shuju_config.pkl", "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("1111")
        self.run_time.setFixedWidth(50)
        self.label_to_time = QLabel('分钟(0为一直运行)     ')

        self.label_from_search = QLabel('         更换搜索词频率')

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
        self.label_seconds_search = QLabel('次内随机     ', self)
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
        self.label_from222_guanzhu = QLabel('%     ')
        self.label_from111_kongge222 = QLabel('                         ')
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
        self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        self.h_layout_disanhang.addWidget(self.label_from111_kongge222)

        #第八航
        self.label_from111_kongge_dibahang = QLabel('                         ')
        self.label_from111_shoucang_dibahang = QLabel('直播间关注概率')
        self.label_from111_shoucang_dibahang.setFixedWidth(90)

        shoucanggailv_dibahang = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv_dibahang")
        if (shoucanggailv_dibahang != None):
            self.shoucanggailv_dibahang = QLineEdit(shoucanggailv_dibahang)
        else:
            self.shoucanggailv_dibahang = QLineEdit("50")
        self.shoucanggailv_dibahang.setFixedWidth(30)
        self.label_from222_shoucang_dibahang = QLabel('%     ')

        self.label_from111_pinglun_dibahang = QLabel('直播间评论概率')
        self.label_from111_pinglun_dibahang.setFixedWidth(90)

        pinglungailv_dibahang = get_value_by_key_pkl("shuju_config.pkl", "pinglungailv_dibahang")
        if (pinglungailv_dibahang != None):
            self.pinglungailv_dibahang = QLineEdit(pinglungailv_dibahang)
        else:
            self.pinglungailv_dibahang = QLineEdit("50")
        self.pinglungailv_dibahang.setFixedWidth(30)
        self.label_from222_pinglun_dibahang = QLabel('%     ')

        self.label_from111_dianzan_dibahang = QLabel('直播间灯牌概率')
        self.label_from111_dianzan_dibahang.setFixedWidth(90)

        dianzangailv_dibahang = get_value_by_key_pkl("shuju_config.pkl", "dianzangailv_dibahang")
        if (dianzangailv_dibahang != None):
            self.dianzangailv_dibahang = QLineEdit(dianzangailv_dibahang)
        else:
            self.dianzangailv_dibahang = QLineEdit("50")
        self.dianzangailv_dibahang.setFixedWidth(30)
        self.label_from222_dianzan_dibahang = QLabel('%     ')

        self.label_from111_guanzhu_dibahang = QLabel('关注概率')
        self.label_from111_guanzhu_dibahang.setFixedWidth(50)

        guanzhugailv_dibahang = get_value_by_key_pkl("shuju_config.pkl", "guanzhugailv_dibahang")
        if (guanzhugailv_dibahang != None):
            self.guanzhugailv_dibahang = QLineEdit(guanzhugailv_dibahang)
        else:
            self.guanzhugailv_dibahang = QLineEdit("50")
        self.guanzhugailv_dibahang.setFixedWidth(30)
        self.label_from222_guanzhu_dibahang = QLabel('%     ')
        self.label_from111_kongge222_dibahang = QLabel('                         ')
        self.h_layout_dibahang = QHBoxLayout()
        self.h_layout_dibahang.addWidget(self.label_from111_kongge_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from111_shoucang_dibahang)
        self.h_layout_dibahang.addWidget(self.shoucanggailv_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from222_shoucang_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from111_pinglun_dibahang)
        self.h_layout_dibahang.addWidget(self.pinglungailv_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from222_pinglun_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from111_dianzan_dibahang)
        self.h_layout_dibahang.addWidget(self.dianzangailv_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from222_dianzan_dibahang)
        # self.h_layout_dibahang.addWidget(self.label_from111_guanzhu_dibahang)
        # self.h_layout_dibahang.addWidget(self.shoucang_guanzhu_dibahang)
        # self.h_layout_dibahang.addWidget(self.label_from222_guanzhu_dibahang)
        self.h_layout_dibahang.addWidget(self.label_from111_kongge222_dibahang)



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

        self.h_layout_diwuhang = QHBoxLayout()
        self.h_layout_diwuhang.setContentsMargins(70, 0, 0, 0)  # 设置布局边距
        self.h_layout_diwuhang.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben = QLabel('请输入上滑关键字:')
        self.douyin_guanjianzi_wenben.setFixedWidth(100)

        douyinguanjianzi = get_value_by_key_pkl("shuju_config.pkl", "douyinguanjianzi")
        if (douyinguanjianzi != None):
            self.douyinguanjianzi = QLineEdit(douyinguanjianzi)
        else:
            self.douyinguanjianzi = QLineEdit("多个关键字用'_'号隔开")
        self.douyinguanjianzi.setFixedWidth(310)


        self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_wenben)
        self.h_layout_diwuhang.addWidget(self.douyinguanjianzi)
        self.h_layout_diwuhang.addStretch(1)

        self.h_layout_diliuhang = QHBoxLayout()
        self.h_layout_diliuhang.setContentsMargins(70, 0, 0, 0)  # 设置布局边距
        self.h_layout_diliuhang.setSpacing(0)  # 设置控件间距

        self.douyin_sousuo_wenben = QLabel('请输入直播间搜索关键字:')
        self.douyin_sousuo_wenben.setFixedWidth(140)

        douyinsousuoguanjianzi = get_value_by_key_pkl("shuju_config.pkl", "douyinsousuoguanjianzi")
        if (douyinsousuoguanjianzi != None):
            self.douyinsousuoguanjianzi = QLineEdit(douyinsousuoguanjianzi)
        else:
            self.douyinsousuoguanjianzi = QLineEdit("多个关键字用'_'号隔开")
        self.douyinsousuoguanjianzi.setFixedWidth(280)

        self.h_layout_diliuhang.addWidget(self.douyin_sousuo_wenben)
        self.h_layout_diliuhang.addWidget(self.douyinsousuoguanjianzi)
        self.h_layout_diliuhang.addStretch(1)

        self.h_layout_diqihang = QHBoxLayout()
        self.h_layout_diqihang.setContentsMargins(70, 0, 0, 0)  # 设置布局边距
        self.h_layout_diqihang.setSpacing(0)  # 设置控件间距

        self.douyin_shiyong_wenben = QLabel('请输入使用关键字:')
        self.douyin_shiyong_wenben.setFixedWidth(110)

        douyinshiyongguanjianzi = get_value_by_key_pkl("shuju_config.pkl", "douyinshiyongguanjianzi")
        if (douyinshiyongguanjianzi != None):
            self.douyinshiyongguanjianzi = QLineEdit(douyinshiyongguanjianzi)
        else:
            self.douyinshiyongguanjianzi = QLineEdit("多个关键字用'_'号隔开")
        self.douyinshiyongguanjianzi.setFixedWidth(310)

        self.h_layout_diqihang.addWidget(self.douyin_shiyong_wenben)
        self.h_layout_diqihang.addWidget(self.douyinshiyongguanjianzi)
        self.h_layout_diqihang.addStretch(1)

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

        self.h_layout_kongge888 = QHBoxLayout()
        self.label_file_kongge888 = QLabel("                          ")
        self.h_layout_kongge888.addWidget(self.label_file_kongge888)

        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择搜索文件路径:")
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

        #模式选择
        self.h_layout_dir_comment_moshi = QHBoxLayout()
        self.label = QLabel("                                      模式选择:")
        self.h_layout_dir_comment_moshi.addWidget(self.label)
        # 创建下拉单选框
        self.combobox = QComboBox()

        # 向下拉框添加选项
        self.combobox.addItem("短视频-直播间")
        self.combobox.addItem("短视频")
        self.combobox.addItem("直播间")
        # 设置默认选中项（索引从0开始）
        self.combobox.setCurrentIndex(0)
        self.h_layout_dir_comment_moshi.addWidget(self.combobox)
        self.temp_comment111 = QLabel("                          ")
        self.h_layout_dir_comment_moshi.addWidget(self.temp_comment111)

        #以下是评论文件选择器
        self.h_layout_dir_comment = QHBoxLayout()
        self.label_file_comment = QLabel("                          请选择评论文件路径:")
        self.h_layout_dir_comment.addWidget(self.label_file_comment)

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        if (file_temp_path_comment != None):
            self.file_textbox_comment = QLineEdit(file_temp_path_comment)
        else:
            self.file_textbox_comment = QLineEdit("请输入短视频评论文件路径")
        self.h_layout_dir_comment.addWidget(self.file_textbox_comment)
        self.file_button_comment = QPushButton("选择文件", self)
        self.temp_comment = QLabel("                          ")
        self.h_layout_dir_comment.addWidget(self.file_button_comment)
        self.h_layout_dir_comment.addWidget(self.temp_comment)

        # 以下是购物文件选择器
        self.h_layout_dir_gouwu = QHBoxLayout()
        self.label_file_gouwu = QLabel("                          请选择直播互动文件路径:")
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

        self.clear_task_config_button = QPushButton('点击手动进入直播间', self)
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

        #layout.addLayout(self.h_layout_kongge)
        # layout.addLayout(self.h_layout_dir)
        # layout.addLayout(self.h_layout_kongge1)

        layout.addLayout(self.h_layout_dir_comment_moshi)
        layout.addLayout(self.h_layout_kongge888)
        layout.addLayout(self.h_layout_dir_comment)
        layout.addLayout(self.h_layout_kongge)
        layout.addLayout(self.h_layout_dir_gouwu)
        layout.addLayout(self.h_layout_kongge6)
        #layout.addLayout(self.h_layout_kongge8)
        layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge3)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge2)
        layout.addLayout(self.h_layout_diwuhang)
        layout.addLayout(self.h_layout_kongge4)
        layout.addLayout(self.h_layout_diliuhang)
        layout.addLayout(self.h_layout_kongge8)
        layout.addLayout(self.h_layout_diqihang)
        layout.addLayout(self.h_layout_kongge1)
        layout.addLayout(self.h_layout_disanhang)
        layout.addLayout(self.h_layout_kongge5)
        layout.addLayout(self.h_layout_dibahang)

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
    def clear_task(self):
        print("")
        if(self.clear_task_config_button.text() == "点击手动进入直播间"):

            if not os.path.exists("pause.txt"):
                # 如果文件不存在，则创建文件
                with open("pause.txt", 'w') as file:
                    pass  # 这里不需要写入任何内容，只需要创建文件即可

            self.clear_task_config_button.setText("取消手动进入直播间")
        else:
            if  os.path.exists("pause.txt"):
                os.remove("pause.txt")
            self.clear_task_config_button.setText("点击手动进入直播间")

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
        updata_pkl_config_mianban("douyinguanjianzi", self.douyinguanjianzi.text())
        updata_pkl_config_mianban("douyinsousuoguanjianzi", self.douyinsousuoguanjianzi.text())
        updata_pkl_config_mianban("douyinshiyongguanjianzi", self.douyinshiyongguanjianzi.text())

        updata_pkl_config_mianban("shoucanggailv_dibahang", self.shoucanggailv_dibahang.text())#直播间关注概率
        updata_pkl_config_mianban("pinglungailv_dibahang", self.pinglungailv_dibahang.text())#直播间评论概率
        updata_pkl_config_mianban("dianzangailv_dibahang", self.dianzangailv_dibahang.text())#直播间灯牌概率

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
            tasks.append("yanghao_sousuo")
        if (self.radio_button2.isChecked() == True):
            tasks.append("yanghao_shanghua")
        if (self.radio_button4.isChecked() == True):
            tasks.append("shiyong")

        moshi = []
        if (self.combobox.currentText() == "短视频"):
            moshi.append("duanshipin")
        elif (self.combobox.currentText() == "直播间"):
            moshi.append("zhibojian")
        else:
            moshi.append("zhibojian")
            moshi.append("duanshipin")

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
        # if (os.path.isfile(self.file_textbox_comment.text())):
        #     print("评论文件加载")
        # else:
        #     print("评论文件不在")
        #     return
        if(len(tasks) == 0):
            print("请选择任务")
            return
        print("self.douyinsousuoguanjianzi.text()=",self.douyinsousuoguanjianzi.text())
        threading.Thread(target=self.bbbb,args=(tasks,moshi,)).start()

    # def bbbb(self,tasks,moshi):
    #     for serial in self.selected_ids:
    #         print("开始启动-------------------------------->",serial)
    #         thread = threading.Thread(target=operate_device, args=(
    #         serial, self.file_textbox.text(), self.file_textbox_comment.text(), tasks, self.run_time.text(),
    #         self.line_edit_from_search.text(), self.line_edit_to_search.text(), self.line_edit_from.text(),
    #         self.line_edit_to.text(), self.jiarenshurukuang.text(), self.shoucang_gailv.text(),
    #         self.shoucang_pinglun.text(), self.shoucang_dianzan.text(), self.shoucang_guanzhu.text(),
    #         self.huadongcishu_big.text(), self.file_textbox_gouwu.text(), self.radio_button3.isChecked(),
    #         self.douyinguanjianzi.text(), self.douyinsousuoguanjianzi.text(), self.douyinshiyongguanjianzi.text(),
    #         moshi, self.shoucanggailv_dibahang.text(), self.pinglungailv_dibahang.text(),
    #         self.dianzangailv_dibahang.text()))
    #         # 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
    #         # threads.append(thread)
    #         thread.start()
    #         time.sleep(1)
    #
    #     self.selected_ids = []

    import threading
    from concurrent.futures import ThreadPoolExecutor

    def bbbb(self, tasks, moshi):
        # 关键修复：执行前先保存当前选择的ID，然后立即清空原始集合
        current_selected = self.selected_ids.copy()  # 保存当前选择的设备ID
        self.selected_ids.clear()  # 清空原始集合，避免后续累加

        selected_list = list(current_selected)  # 基于保存的ID创建列表
        print("本次执行的设备列表=", selected_list)

        group_size = 10
        device_groups = [selected_list[i:i + group_size] for i in range(0, len(selected_list), group_size)]
        group_index = 1

        # 限制最大并发线程数
        max_workers = 100
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for group in device_groups:
                print(f"开始启动第 {group_index} 组设备，共 {len(group)} 台")

                for i, serial in enumerate(group):
                    print(f"第 {group_index} 组第 {i + 1} 台设备提交任务-------------------------------->", serial)

                    executor.submit(
                        operate_device,
                        serial, self.file_textbox.text(), self.file_textbox_comment.text(), tasks, self.run_time.text(),
                        self.line_edit_from_search.text(), self.line_edit_to_search.text(), self.line_edit_from.text(),
                        self.line_edit_to.text(), self.jiarenshurukuang.text(), self.shoucang_gailv.text(),
                        self.shoucang_pinglun.text(), self.shoucang_dianzan.text(), self.shoucang_guanzhu.text(),
                        self.huadongcishu_big.text(), self.file_textbox_gouwu.text(), self.radio_button3.isChecked(),
                        self.douyinguanjianzi.text(), self.douyinsousuoguanjianzi.text(),
                        self.douyinshiyongguanjianzi.text(),
                        moshi, self.shoucanggailv_dibahang.text(), self.pinglungailv_dibahang.text(),
                        self.dianzangailv_dibahang.text()
                    )

                    # 组内间隔
                    if i < len(group) - 1:
                        time.sleep(3)

                # 组间间隔
                if group_index < len(device_groups):
                    print(f"第 {group_index} 组提交完成，等待30秒后启动下一组...")
                    time.sleep(30)

                group_index += 1

        print("本次执行结束，已清空选择的设备ID")

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