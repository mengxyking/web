# import cv2
import shutil
import sys
import threading
import random
import traceback
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

from uiautomator2 import Direction

current_scroll_position = 0
import time

# 抖音养号+微信加好友脚本

alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()
clicked_touxiang = []


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
    #else:
        #print(f"Directory '{directory_path}' already exists.")


    # 示例用法


import os


def create_file_if_not_exists(file_path):
    if not os.path.isfile(file_path):
        # 如果文件不存在，则创建它（这里只是创建一个空文件）
        with open(file_path, 'w') as file:
            file.write('')  # 或者你可以写入一些初始内容
        print(f"File '{file_path}' created.")
    # else:
    #     print(f"File '{file_path}' already exists.")

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
    print("pkl_files=", pkl_files)

    # 如果没有 .pkl 文件，则直接返回 False
    if not pkl_files:
        return False
    with video_lock:
        # 循环直到找到一个满足条件的文件或者所有文件都不满足条件
        while pkl_files:
            # 随机选择一个 .pkl 文件
            chosen_file = pkl_files[0]
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
                    print("tongji=", int(data['TONGJI']))
                    print("BIG_COUNT=", int(data['BIG_COUNT']))
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

# 创建一个全局的线程锁
file_lock11 = threading.Lock()


def read_file_line_by_line(file_path):
    with file_lock11:  # 获取锁，确保只有一个线程能进入这个块
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    # print(f"Thread {thread_id} read line {line_number}: {line.strip()}")
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


def operate_device(serial, task,comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu,tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage):
    # 手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数
    print("222")
    print("task===>",task)
    if (int(time.time()) > 1746109581 + 60 * 60 * 24 * 20):
        print("")
        #return


    count_zong = 0
    while (True):
        try:
            print("333")
            result = main(serial, task,comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu,tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage)
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
                    cmd = f"adb -s {serial} shell input  keyevent 26"
                    #shell_neibu(cmd)
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
                    cmd = f"adb -s {serial} shell input  keyevent 26"
                    #shell_neibu(cmd)
                return
            if(result == "999"):
                print("运行结束11")
                filepath = './shuju/' + serial + ".pkl"
                print("filepath-->", filepath)
                updata_pkl(filepath, "执行状态", "运行结束")
                updata_pkl(filepath, "进行的任务", "空闲")
                return
            count_zong += 1
        except BaseException as ee:
            print("崩溃了", ee)
            error_info = traceback.format_exc()
            print("完整错误信息:")
            print(error_info)
            operate_device(serial, task,comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu,tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage)


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


def back_to_home(d):
    count = 0
    while (count < 10):
        if (d(text='微信').exists(timeout=3)):
            if (d(text='发现').exists(timeout=1)):
                if (d(text='通讯录').exists(timeout=1)):
                    print("当前在首页了。。。。。。。。")
                    time.sleep(3)
                    return 1
        else:
            print("当前bu在首页了。。。。。。。。")
        count += 1
        d.press("back")
    return 88
def back_to_xiaoxi(d):
    count = 0
    while (count < 10):
        if (d(text='消息').exists(timeout=3)):
            if (d(text='首页').exists(timeout=1)):
                if (not d(description="表情").exists(timeout=1)):
                    print("当前在消息了。。。。。。。。")
                    time.sleep(3)
                    return 1
        else:
            print("当前bu在首页了。。。。。。。。")
        count += 1
        d.press("back")
    return 88

def back_to_moshengren(d):
    count = 0
    while (count < 10):
        if (d(text='一键已读').exists(timeout=3)):
            print("当前在一键已读。。。。。。。。")
            time.sleep(3)
            return 1
        else:
            print("当前bu在首页了。。。。。。。。")
        count += 1
        d.press("back")
    return 88
def back_to_douyin_jisu(d,banben):
    if(banben == "jisu"):
        d.app_start(package_name="com.ss.android.ugc.aweme.lite")
    else:
        d.app_start(package_name="com.ss.android.ugc.aweme")
    time.sleep(2)
    d.press("back")
    time.sleep(2)
    d.press("back")
    time.sleep(2)
    d.press("back")


    count = 0
    while (count < 10):
        if (d(text='消息').exists(timeout=3)):
            if (d(text='首页').exists(timeout=1)):
                print("当前在首页了。。。。。。。。")
                time.sleep(3)
                d(text='消息').click()
                time.sleep(2)
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
        # time.sleep(1)
        if ((d(resourceId='com.smile.gifmaker:id/tabs_panel_close').exists(timeout=3)) or (
        d(description='回复评论').exists(timeout=0.1))):
            print("当前在评论里了了。。。。。。。。")
            time.sleep(1)
            return 1
        else:
            print("当前不在评论里了了。。。。。。。。")
        count += 1
        d.press("back")
    return 0


def random_click_view(d, view):
    #view = view.info
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left) + random.randint(2, 8)
    random_y = int(bottom) + random.randint(2, 8)

    d.click(random_x, random_y)


# 搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def douyinsixin(d, serial, neirong, guanjianzi, douyinsixinshijianjiange, douyinsixingeshuxianzhi):
    folder_path = "user"
    create_directory_if_not_exists(folder_path)
    d.app_start(package_name="com.ss.android.ugc.aweme")
    backToHome(d)
    # time.sleep(int(random.randint(5, 300)))

    time.sleep(3)

    # 当前判断在不在首页，如果有home 或者是首页，则认为当前在首页了
    if (d(text='首页').exists(timeout=15)):
        print("当前在首页了。。。。。。。。")
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return

    if (d(description='搜索').exists(timeout=15)):
        print("当前在首页了。。。。。。。。")
        d(description='搜索').click()
        time.sleep(5)
    else:
        print("当前bu在首页了。。。。。。。。")
        return

    # if (d(text='首页').exists(timeout=3)):
    #     d.click(d.info["displayWidth"] - 50, 180)
    #     time.sleep(5)

    search_key = guanjianzi
    if ((len(search_key) > 1) and (search_key != None)):
        print("搜索词符合规范")
    else:
        print("搜索词为空")
        return

    if (d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').exists(timeout=3)):
        d(resourceId='com.ss.android.ugc.aweme:id/et_search_kw').set_text(search_key)
        time.sleep(3)
    else:
        print("当前bu在首页了。。。。。。。。")
        return

    time.sleep(3)
    if (d(text='搜索').exists(timeout=15)):
        print("当前在首页了。。。。。。。。")
        d(text='搜索').click()
        time.sleep(1)
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    time.sleep(8)

    bar_bottom = 0
    if (d(text="综合").exists(timeout=3)):
        print(d(text="综合").info["bounds"]["top"])
        bar_top = int(d(text="综合").info["bounds"]["top"] + 5)
        bar_bottom = int(d(text="综合").info["bounds"]["bottom"])

        count_small = 0
        while (count_small < 15):

            if (d(text="用户").exists(timeout=1)):
                d(text="用户").click()
                break
            time.sleep(1)
            d.swipe(400, bar_top, 200, bar_top, 0.5)
            time.sleep(1)
            if (count_small > 12):
                print("当前搜索页面没有用户tab")
                return 0

        time.sleep(3)
    else:
        print("当前bu在首页了。。。。。。。。")
        return

    if (d(textContains="，按钮").exists(timeout=3)):
        print("11")
    else:
        return
    phone_height = d.info["displayHeight"]
    sixin_count = 0
    while (sixin_count < int(douyinsixingeshuxianzhi)):
        users = d(textContains="，按钮")
        for user in users:
            # print(user.info)
            if ((str(user.info).count("粉丝") < 1) and (str(user.info).count("抖音号") < 1) and (
                    str(user.info).count("直播中") < 1)):
                clean_string_str = clean_string(str(user.info["text"]))
                file_path = folder_path + "/" + clean_string_str
                if (not os.path.isfile(file_path)):
                    if (int(user.info["bounds"]["bottom"]) - bar_bottom > 10):
                        create_file_if_not_exists(file_path)
                        user.click()
                        sixin_count += 1
                        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                        time.sleep(2)
                        dysixin(d, serial, neirong)
                        backToUser_list(d)
                        time.sleep(random.randint(int(douyinsixinshijianjiange), int(douyinsixinshijianjiange) + 8))
        time.sleep(1)
        d.swipe_ext(Direction.FORWARD)
        time.sleep(1)

        if (d(text="找不到想找的帐号？").exists(timeout=1)):

            time.sleep(1)
            d.swipe_ext(Direction.FORWARD)
            time.sleep(1)
            if (d(text="找不到想找的帐号？").exists(timeout=1)):
                bottom_view = d(text="找不到想找的帐号？").info["bounds"]["bottom"]
                if (phone_height - bottom_view < 300):
                    print("到头了")
                    return


def backToUser_list(d):
    dd = 0
    time.sleep(3)
    while (dd < 10):
        # print(len(elements))
        if ((d(text="用户").exists(timeout=2)) and (d(text="搜索").exists(timeout=2))):
            return "1"
        time.sleep(0.8)
        d.press("back")
        time.sleep(0.8)


def dysixin(d, serier, neirong):
    if (d(description="更多").exists(timeout=5)):
        print("当前在详情页")
        d(description="更多").click()
        time.sleep(4)
    else:
        return

    if (d(text="发私信").exists(timeout=5)):
        print("当前在详情页")
        d(text="发私信").click()
        time.sleep(4)
    else:
        return

    if (d(resourceId="com.ss.android.ugc.aweme:id/msg_et").exists(timeout=5)):
        print("发送消息")
        d(resourceId="com.ss.android.ugc.aweme:id/msg_et").click()
        time.sleep(4)
    else:
        return

    if (d(resourceId="com.ss.android.ugc.aweme:id/msg_et").exists(timeout=5)):
        print("发送消息")
        d(resourceId="com.ss.android.ugc.aweme:id/msg_et").set_text(neirong)
        time.sleep(4)
    else:
        return

    if (d(description="发送").exists(timeout=5)):
        print("发送消息")
        # d(description="发送").click()
        # random_click_view(d,d(description="发送").info)
        random_click_view(d, d(description='发送').info)
        time.sleep(4)
    else:
        return

    return 1


import re


def clean_string(input_string):
    # 使用正则表达式匹配汉字、字母和数字
    pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
    # 替换掉所有不匹配的字符
    cleaned_string = pattern.sub('', input_string)

    if (cleaned_string == None):
        return "默认"

    return cleaned_string


def sixin_like_douyin(d, serial, comment_content, comment_fanwei, comment_count, comment_time, comments,tongchengdianzanzongshu,tongchengdianzandage):
    updata_pkl("./shuju/" + serial + ".pkl", "执行状态", "运行中")
    updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "dy同城粉丝视频点赞")


    # print("-----",d.app_list())
    #
    # if("com.ss.android.ugc.aweme" in d.app_list()):
    #     d.app_start(package_name="com.ss.android.ugc.aweme")
    #     print("启动抖音")
    # elif("com.ss.android.ugc.aweme.lite" in d.app_list()):
    #     d.app_start(package_name="com.ss.android.ugc.aweme.lite")
    #     print("启动抖音极速版")
    # else:
    #     print("当前没有安装app")
    #     return "99"
    #
    # result_back = backToHome(d)
    # d.press("back")
    # if(result_back != "1"):
    #     print("aaa tuichu")
    #     return "99"
    # city = "666"
    #
    # result_tongcheng = gotoTongcheng(d,serial)
    # if(result_tongcheng != "1"):
    #     return "99"


    if (d(text='同城发现').exists(timeout=3)):
        print("同城发现")
    else:
        print("当前没有同城发现")
        return 0

    count_f = 0
    pinglun_couont = 0
    count_zong = 0
    count_all = int(tongchengdianzanzongshu)
    while (True):
        if (count_f != 0):
            result_back = backToTongcheng(d)
            time.sleep(random.randint(5,15))
            print("result_back=", result_back)
            if (result_back != 1):
                return

            d.swipe_ext(Direction.FORWARD)
            time.sleep(2)
        count_f += 1

        if (d(descriptionStartsWith='评论').exists(timeout=3)):
            print("，按钮")
            d(descriptionStartsWith='评论').click()
            time.sleep(random.randint(3,8))
        else:
            print("当前没有，按钮")
            continue

        # if (d(text='作者').exists(timeout=1)):
        #     print("有作者")
        #     # d(text='作者').click()
        #     continue

        if (d(textContains='条评论').exists(timeout=1)):
            print("d(textContains='条评论').get_text()=")
            print(d(textContains='条评论').get_text())
            pinglun_temp = d(textContains='条评论').get_text()

            pinglun_count = str(pinglun_temp)[:-3]
            print("pinglun_count=", pinglun_count)
            if (str(pinglun_count).count("万") or (str(pinglun_count).count("."))):
                print("评论个数满足")
            else:
                if (pinglun_count.isdigit()):
                    if (int(pinglun_count) > int(comment_fanwei)):
                        print("评论个数满足")
                    else:
                        print("评论个数bu满足")
                        continue
                else:
                    print("fanwei 配置的不对，重新配置")
                    continue
        else:
            print("当前条评论")
            continue

        if (d(textContains='条评论').exists(timeout=1)):
            print("条评论")
        else:
            print("当前没有条评论")
            continue
        print("返回同城")
        backToTongcheng(d)
        time.sleep(0.1)

        if (d(textStartsWith="@").exists(timeout=6)):
            d(textStartsWith="@").click()
            time.sleep(1)
        else:
            continue

        if (d(text="粉丝").exists(timeout=6)):
            d(text="粉丝").click()
            time.sleep(random.randint(3,8))
        else:
            continue

        if (d(text="关注").exists(timeout=6)):
            guanzhus = d(text="关注")
            if(len(guanzhus) > 4):
                print()
            else:
                continue
            time.sleep(random.randint(1,3))
        else:
            continue

        liked = like_dianzan(d,serial,tongchengdianzanzongshu,tongchengdianzandage)
        if(liked == 99 ):
            return "99"
        #pinglun_couont = pinglun_couont + int(pinglun_couont)
def gotoTongcheng(d,serial):
    city = "666"
    city_name = get_value_by_key_pkl("config.pkl", serial)
    if (str(city_name).count("-") > 0):
        city = str(city_name).split("-")[1]
    print("city=", city)
    tongchengs = []
    tuijian_y = 0
    if (d(text="推荐").exists(timeout=5)):
        print("当前在首页了。。。。。。。。")
        tuijian_y = d(text="推荐").info["bounds"]["top"] + 3
    else:
        print("当前bu在首页了。。。。。。。。")
        return
    tongchengs.append(city)
    tongchengs.append("同城")
    for i in range(5):
        for tongcheng in tongchengs:
            print("tongcheng=", tongcheng)
            if (len(tongcheng) > 0):
                print("ok")
            else:
                print("不 ok")
                continue
            if (d(text=tongcheng).exists(timeout=0.5)):

                if(tongcheng == "同城"):
                    print("当前是同城")
                    print("当前找到同城乐。。。。。。。。", tongcheng)
                    random_click_view(d, d(text=tongcheng).info)
                    desc_t = "已选中，" + tongcheng

                    if (d(descriptionContains=desc_t).exists(timeout=10)):
                        print("当前确实在同城了，需要划一下。。。。。。。。")
                        beisaier_random(d)
                        time.sleep(2)
                        beisaier_random(d)
                        time.sleep(2)
                    else:
                        print("当前没有  收藏的数据了")
                        # return
                    if (d(text=tongcheng).exists(timeout=0.5)):
                        random_click_view(d, d(text=tongcheng).info)
                    else:
                        return "2"

                    if (d(text="输入城市或区县名搜索").exists(timeout=5)):
                        d(text="输入城市或区县名搜索").set_text(city)
                        time.sleep(random.randint(3,5))
                    else:
                        return "2"

                    citys = d(text=city)
                    print("citys---->",citys)
                    for cityttt in citys:
                        print(cityttt.info)

                    if (d(text=city).exists(timeout=5)):
                        d.click(500,d(text=city).info["bounds"]["bottom"]+50)
                        time.sleep(random.randint(5,8))
                        beisaier_random(d)
                        time.sleep(2)
                        beisaier_random(d)
                        time.sleep(2)
                        return "1"
                    else:
                        return "2"

                else:
                    print("当前找到同城乐。。。。。。。。", tongcheng)
                    random_click_view(d, d(text=tongcheng).info)
                    desc_t = "已选中，" + tongcheng

                    if (d(descriptionContains=desc_t).exists(timeout=10)):
                        print("当前确实在同城了，需要划一下。。。。。。。。")
                        beisaier_random(d)
                        time.sleep(2)
                        beisaier_random(d)
                        time.sleep(2)
                        return "1"

                    else:
                        print("当前没有  收藏的数据了")
                        # return
            else:
                print("当前没有同城")
        d.swipe(200, tuijian_y, 900, tuijian_y, 0.5)
        time.sleep(2)
def beisaier_random(d,Diract="up"):
    # 获取屏幕尺寸
    width, height = d.window_size()

    # 设置起点和终点
    if Diract == "up":
        random_start_point_x = random.uniform(0.3, 0.6)
        random_start_point_y = random.uniform(0.65, 0.68)
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
    random_num = random.uniform(0.3, 1.2)
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

def like_dianzan(d,serial,tongchengdianzanzongshu,tongchengdianzandage):
    clicked_like_touxiang = []
    flag = True
    liked = 0
    lahei_flag = 0
    while (liked < int(tongchengdianzandage)):
        back_to_touxiang_list(d)
        # if(len(clicked_like_touxiang) != 0):
        #     d.swipe_ext("up", scale=0.2)
        #     time.sleep(1)
        if(d(text = "部分用户已开启隐私设置，暂不支持查看").exists(timeout=1)):
            return liked
        if (d(text="暂时没有更多了").exists(timeout=0.1)):
            return liked
        if (d(textContains="部分用户来自抖音火山版").exists(timeout=0.1)):
            return liked

        if (d( descriptionContains="用户头像").exists(timeout=3)):
            print("由用户头像啊")
            return
        elif (d(descriptionContains="头像").exists(timeout=1)):
            namesss = d(descriptionContains="头像")
            for name in namesss:
                name_touxiang = name.info["contentDescription"]
                print("name_touxiang=",name_touxiang)
                print("name_touxiang not in clicked_like_touxiang = ",name_touxiang not in clicked_like_touxiang)
                if(name_touxiang not in clicked_like_touxiang):
                    clicked_like_touxiang.append(name_touxiang)
                    name.click()
                    time.sleep(1)
                    break
            else:
                d.swipe_ext("up", scale=0.8)
                time.sleep(1)
                continue
        else:
            continue

        if (d(descriptionContains="点赞数").exists(timeout=6)):
            d(descriptionContains="点赞数").click()
            time.sleep(random.randint(5,10))
        else:
            continue
        dongzuo = "dianzan"
        if(lahei_flag == 0):
            print("当前没被拉黑")
            random_value = random.randint(1, 100)

            if(random_value<=50):
                dongzuo = "dianzan"
            elif(random_value <= 60):
                dongzuo = "shoucang"
            else:
                dongzuo = "fenxiang"

        else:
            print("当前被拉黑")
            random_value = random.randint(1, 100)

            if (random_value <= 25):
                dongzuo = "shoucang"
            else:
                dongzuo = "fenxiang"
        if(dongzuo == "dianzan"):
            if (d(descriptionContains="未点赞").exists(timeout=3)):
                d(descriptionContains="未点赞").click()

                liked += 1
                update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                time.sleep(random.randint(2, 5))
                # zongshu = get_value_by_key_pkl("./shuju/" + str(serial) + ".pkl","tongji")
                # print("zongshu",zongshu)
                # print("tongchengdianzanzongshu", tongchengdianzanzongshu)
                # if(int(zongshu) >= int(tongchengdianzanzongshu)):
                #     print("99 tuichu")
                #     #return 99

            if (d(descriptionContains="未点赞").exists(timeout=3)):
                print("当前被拉黑")
                lahei_flag = 1
            else:
                continue
        print("dongzuo=",dongzuo)
        if(dongzuo == "shoucang"):
            if (d(descriptionContains="未选中，收藏").exists(timeout=3)):
                d(descriptionContains="未选中，收藏").click()

                liked += 1
                update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                time.sleep(random.randint(2, 5))
                # zongshu = get_value_by_key_pkl("./shuju/" + str(serial) + ".pkl","tongji")
                # print("zongshu",zongshu)
                # print("tongchengdianzanzongshu", tongchengdianzanzongshu)
                # if(int(zongshu) >= int(tongchengdianzanzongshu)):
                #     print("99 tuichu")
                #     #return 99
            else:
                continue
        if (dongzuo == "fenxiang"):
            if (d(descriptionContains="分享").exists(timeout=3)):
                d(descriptionContains="分享").click()

                liked += 1
                update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                time.sleep(random.randint(2, 4))

                if (d(text="推荐").exists(timeout=3)):
                    d(text="推荐").click()
                    time.sleep(random.randint(2, 4))

            else:
                continue
def back_to_touxiang_list(d):
    dd = 0
    time.sleep(1)
    while (dd < 3):
        elements = d(descriptionContains="头像")  # 获取所有文本为'some_text'的元素
        print("----len----", len(elements))
        if (d(descriptionContains="头像").exists(timeout=6)):
            elements = d(descriptionContains="用户头像")
            if(elements):
                print()
            else:
                print("tuichu")
                return 1

            elements = d(text='同城发现')
            if (elements):
                return 1
        dd += 1
        #time.sleep(1)
        d.press("back")
        time.sleep(1)

    return 2




def main(serial, task,comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu,tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage):
    # 手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数
    print("444")
    print(comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu)
    comments = str(comment_content).split("-")
    if (len(task) == 0):
        # return
        print("")
    d = get_device(serial)
    d.watcher.when("以后再说").click()
    d.watcher.when("我知道了").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.when("不再提醒").click()
    d.watcher.start()
    print("1")
    if("tongcheng_fansi_like" in task):
        print("开始点赞")
        sixin_like_douyin(d, serial, comment_content, comment_fanwei, comment_count, comment_time, comments,tongchengdianzanzongshu,tongchengdianzandage)
    if(tongbu_flag == 1):
        updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "dy回复私信")
        if ("sixin_reply" in task):

            result = get_random_pkl_file_in_directory("task_config")
            # print("result=", result)
            if ((result == False) or (result == None)):
                updata_pkl("./shuju/" + str(serial) + ".pkl", "执行状态", "已结束")
                return

            file_path = "task_config/" + result
            # print("file_path=", file_path)
            result_load = load_pkl(file_path)
            if (result_load == None):
                return 99

            # print("result_load=", result_load)
            url = dict(result_load).get("url", "aaa")
            print("url11111=", url)
            banben = "jisu"
            result_sixin = sixin_reply(d, serial, douyinsixinhuashu,banben)
        if ("sixin_reply_zhengban" in task):

            result = get_random_pkl_file_in_directory("task_config")
            # print("result=", result)
            if ((result == False) or (result == None)):
                updata_pkl("./shuju/" + str(serial) + ".pkl", "执行状态", "已结束")
                return

            file_path = "task_config/" + result
            # print("file_path=", file_path)
            result_load = load_pkl(file_path)
            if (result_load == None):
                return 99

            # print("result_load=", result_load)
            url = dict(result_load).get("url", "aaa")
            print("url11111=", url)
            banben = "zhengban"

            result_sixin = sixin_reply(d, serial, douyinsixinhuashu,banben)

    return 99
def sixin_reply(d,serial,xiaoxi,banben):
    print("")

    temp_c = 0
    while(temp_c<=3):
        result_back = back_to_douyin_jisu(d,banben)
        if (result_back == 1):
            if(temp_c != 3):
                if(banben == "jisu"):
                    d.app_stop("com.ss.android.ugc.aweme.lite")
                else:
                    d.app_stop("com.ss.android.ugc.aweme")
                time.sleep(2)
        temp_c += 1
        print("temp_c=",temp_c)

    if (d(text='消息').exists(timeout=3)):
        print("，按钮")
        d(text='消息').click()
        time.sleep(1)
        d(text='消息').click()
        time.sleep(1)
        d(text='消息').click()
        time.sleep(1)
    else:
        print("当前没有消息按钮")
        return

    # moshengren = d(text="陌生人消息")
    # if (moshengren):
    #     moshengren.click()
    #     moshengrenM(d, serial, xiaoxi, "file_path")
    #     time.sleep(2)

    swipe_count = 0
    while(swipe_count < 6):
        moshengren = d(text="陌生人消息")
        if (moshengren):
            moshengren.click()
            moshengrenM(d, serial, xiaoxi, "file_path")
            time.sleep(2)

        result = get_random_pkl_file_in_directory("task_config")
        # print("result=", result)
        if ((result == False) or (result == None)):
            updata_pkl("./shuju/" + str(serial) + ".pkl", "执行状态", "已结束")
            return 99

        file_path = "task_config/" + result
        # print("file_path=", file_path)
        result_load = load_pkl(file_path)
        if (result_load == None):
            return 99

        # print("result_load=", result_load)
        url = dict(result_load).get("url", "aaa")
        print("url11111=", url)

        time.sleep(2)


        dots = d(resourceId='com.ss.android.ugc.aweme.lite:id/red_tips_dot_view')
        counts = d(resourceId="com.ss.android.ugc.aweme.lite:id/red_tips_count_view")
        m9is = d(resourceId="com.ss.android.ugc.aweme.lite:id/m9i")
        ujia8s = d(resourceId="com.ss.android.ugc.aweme:id/u+8")

        ujia8s_dy = d(resourceId="com.ss.android.ugc.aweme:id/v+o") #正版已验证
        ujia8s1_dy = d(resourceId="com.ss.android.ugc.aweme:id/red_tips_dot_view")#正版已验证


        print("dots=", dots)
        print("counts=", counts)


        if(dots):
            dots.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif(counts):
            counts.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif (m9is):
            m9is.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif (ujia8s):
            ujia8s.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif (ujia8s_dy):
            ujia8s_dy.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif (ujia8s1_dy):
            ujia8s1_dy.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaoxi, file_path)
            back_to_xiaoxi(d)
            time.sleep(2)
        elif(d(text="暂时没有更多了").exists(timeout=1)):
            return
        else:
            time.sleep(2)
            d.swipe_ext(Direction.FORWARD)
            swipe_count += 1



def moshengrenM(d,serial,xiaomi,file_path):
    count = 0
    while(count < 5):

        result = get_random_pkl_file_in_directory("task_config")
        # print("result=", result)
        if ((result == False) or (result == None)):
            updata_pkl("./shuju/" + str(serial) + ".pkl", "执行状态", "已结束")
            return 99

        file_path = "task_config/" + result
        # print("file_path=", file_path)
        result_load = load_pkl(file_path)
        if (result_load == None):
            return 99

        # print("result_load=", result_load)
        url = dict(result_load).get("url", "aaa")
        print("url11111=", url)


        time.sleep(2)
        dots = d(resourceId='com.ss.android.ugc.aweme.lite:id/m9i')
        counts = d(resourceId="com.ss.android.ugc.aweme:id/oek") #已验证

        if(dots):
            dots.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaomi, file_path)
            back_to_moshengren(d)
            time.sleep(2)
        elif (counts):
            counts.click()
            time.sleep(2)
            liaotian(d, str(url).strip() + xiaomi, file_path)
            back_to_moshengren(d)
            time.sleep(2)
        elif (d(text="暂时没有更多了").exists(timeout=1)):
            back_to_xiaoxi(d)
            return
        else:
            time.sleep(1)
            d.swipe_ext(Direction.FORWARD)
            time.sleep(2)
            count += 1

def liaotian(d,xiaoxi,file_path):
    time.sleep(2)
    print("")
    liaotian_queren = d(textContains="确认聊天")
    if(liaotian_queren):
        liaotian_queren.click()
        time.sleep(2)

    liaotian_meigui = d(resourceId="com.ss.android.ugc.aweme:id/c4u")
    liaotian_meigui_jisu = d(resourceId="com.ss.android.ugc.aweme.lite:id/bhw")
    if(liaotian_meigui):
        for temp in liaotian_meigui:
            left = temp.info["bounds"]["left"]
            if(left > 700):
                print("当前回复过")
                return
    elif(liaotian_meigui_jisu):
        for temp in liaotian_meigui_jisu:
            left = temp.info["bounds"]["left"]
            if(left > 700):
                print("当前回复过")
                return
    liaotian_queren = d(textContains="发送消息")

    if (liaotian_queren):
        liaotian_queren.click()
        time.sleep(2)
        d(textContains="发送消息").set_text(xiaoxi)
        time.sleep(2)
    else:
        return

    liaotian_queren = d(descriptionContains="发送")

    if (liaotian_queren):
        update_pkl_add_one(file_path, "TONGJI")
        liaotian_queren.click()
        time.sleep(2)
        time.sleep(2)
        return 1
    else:
        return

def sixin_douyin(d,serial,comment_content,comment_fanwei,comment_count,comment_time,comments):
    if ("com.ss.android.ugc.aweme" in d.app_list()):
        d.app_start(package_name="com.ss.android.ugc.aweme")
        print("启动抖音")
    elif ("com.ss.android.ugc.aweme.lite" in d.app_list()):
        d.app_start(package_name="com.ss.android.ugc.aweme.lite")
        print("启动抖音极速版")
    else:
        print("当前没有安装app")
        return "99"

    result_back = backToHome(d)
    d.press("back")
    if (result_back != "1"):
        print("aaa tuichu")
        return "99"
    city = "666"

    result_tongcheng = gotoTongcheng(d, serial)
    if (result_tongcheng != "1"):
        return "99"

    if (d(text='同城发现').exists(timeout=3)):
        print("同城发现")
    else:
        print("当前没有同城发现")
        return 0

    count_f = 0
    pinglun_couont = 0
    count_all = int(comment_count)
    # if(count_all < 150):
    #     count_all = 150
    while(pinglun_couont < count_all):
        if(count_f != 0 ):
            result_back = backToTongcheng(d)
            print("result_back=",result_back)
            if (result_back != 1):
                return

            d.swipe_ext(Direction.FORWARD)
            time.sleep(2)
        count_f += 1
        if(comment_time != "不筛选"):
            if (d(descriptionStartsWith='发布时间：').exists(timeout=3)):
                print("，按钮")
                public_time = d(descriptionStartsWith='发布时间：').get_text()
                time.sleep(2)
                print("public_time=",public_time)

                if(str(public_time).count("日")):
                    print("you ri")
                    continue
                if (str(public_time).count("年")):
                    print("you nian")
                    continue
                if (str(public_time).count("月")):
                    print("you yue")
                    continue

                if(comment_time == "一天内"):
                    if(str(public_time).count("小时")):
                        print("时间满足")
                    else:
                        print("时间不满足")
                        continue

                if (comment_time == "一周内"):
                    if (str(public_time).count("小时")):
                        print("时间满足")
                    elif(str(public_time).count("天")):
                        print("时间满足")
                    else:
                        print("时间不满足")
                        continue
            else:
                print("当前没有，发布时间")
                continue


        if (d(descriptionStartsWith='评论').exists(timeout=3)):
            print("，按钮")
            d(descriptionStartsWith='评论').click()
            time.sleep(2)
        else:
            print("当前没有，按钮")
            continue

        if (d(text='作者').exists(timeout=1)):
            print("有作者")
            #d(text='作者').click()
            continue

        if (d(textContains='条评论').exists(timeout=1)):
            print("d(textContains='条评论').get_text()=")
            print(d(textContains='条评论').get_text())
            pinglun_temp = d(textContains='条评论').get_text()

            pinglun_count = str(pinglun_temp)[:-3]
            print("pinglun_count=",pinglun_count)
            if(str(pinglun_count).count("万") or (str(pinglun_count).count("."))):
                print("评论个数满足")
            else:
                if(pinglun_count.isdigit()):
                    if(int(pinglun_count)>int(comment_fanwei)):
                        print("评论个数满足")
                    else:
                        print("评论个数bu满足")
                        continue
                else:
                    print("fanwei 配置的不对，重新配置")
                    continue
        else:
            print("当前条评论")
            continue


        if (d(textContains='善语结善缘').exists(timeout=1)):
            print("，按钮")
            d(textContains='善语结善缘').click()
            time.sleep(1)

            d(textContains='善语结善缘').set_text(random.choice(comments))
            time.sleep(1)

        else:
            print("当前没有善缘按钮")
            continue

        if (d(text='发送').exists(timeout=3)):
            pinglun_couont += 1
            print("发送")
            d(text='发送').click()
            time.sleep(2)
            update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        else:
            print("当前没有发送，按钮")
            return 0
def backToTongcheng(d):
    dd = 0
    time.sleep(1)
    while (dd < 10):
        elements = d(text='同城发现')  # 获取所有文本为'some_text'的元素
        print("----len----",len(elements))
        if (len(elements) > 0):
            print("tuichu")
            return 1
        dd += 1
        #time.sleep(0.5)
        d.press("back")
        time.sleep(1)
    return 2

def douyin_public(d, count, zuopinmiaoshu):
    d.app_start(package_name="com.ss.android.ugc.aweme")
    backToHome(d)

    if (d(descriptionContains='拍摄').exists(timeout=3)):
        print("点击评论")
        d(descriptionContains='拍摄').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0
    print("4")
    if (d(descriptionContains='相册').exists(timeout=5)):
        print("点击评论")
        d(descriptionContains='相册').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    elif (d(text='相册').exists(timeout=5)):
        print("点击评论")
        d(text='相册').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    else:
        print("当前没有相册文字 。。。。。。。。")
        return 0

    if (d(text='视频').exists(timeout=6)):
        print("点击评论")
        d(text='视频').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0

    if (d(descriptionContains='未选中').exists(timeout=5)):
        print("点击评论")
        print("count=", count)
        weixuanzhong = d(descriptionContains='未选中')
        print("点击评论")
        print("len(weixuanzhong)=", len(weixuanzhong))
        for mmm in weixuanzhong:
            print("mmm=", mmm)
        if (count >= len(weixuanzhong)):
            return 0
        weixuanzhong[count].click()
        time.sleep(random.randint(15, 25))

    if (d(text='下一步').exists(timeout=5)):
        print("点击评论")
        d(text='下一步').click()
        print("点击评论")
        time.sleep(random.randint(10, 25))
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0

    if (d(text='下一步').exists(timeout=5)):
        print("点击评论")
        d(text='下一步').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0

    if (d(textContains='添加作品描述').exists(timeout=5)):
        print("点击评论")
        d(textContains='添加作品描述').click()
        print("点击评论")
        time.sleep(3)
        d(textContains='添加作品描述').set_text(zuopinmiaoshu)
        time.sleep(3)
        d.press("back")
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0

    if (d(text='发作品').exists(timeout=5)):
        print("发作品")
        d(text='发作品').click()
        print("发布作品")
        time.sleep(random.randint(1, 5))
        return 1
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0


def getCount_videos(d):
    print("3")
    d.app_start(package_name="com.ss.android.ugc.aweme")
    backToHome(d)

    if (d(descriptionContains='拍摄').exists(timeout=3)):
        print("点击评论")
        d(descriptionContains='拍摄').click()
        print("点击评论")
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0
    print("4")
    if (d(descriptionContains='相册').exists(timeout=5)):
        print("点击评论")
        d(descriptionContains='相册').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    elif (d(text='相册').exists(timeout=5)):
        print("点击评论")
        d(text='相册').click()
        print("点击评论")
        time.sleep(random.randint(1, 5))
    else:
        print("当前没有相册文字 。。。。。。。。")
        return 0

    if (d(text='视频').exists(timeout=6)):
        print("点击评论")
        d(text='视频').click()
        print("点击评论")
    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0

    if (d(descriptionContains='未选中').exists(timeout=5)):
        print("点击评论")
        weixuanzhong = d(descriptionContains='未选中')
        print("点击评论")
        videos = len(weixuanzhong)

        return videos

    else:
        print("当前没有拍摄论a 。。。。。。。。")
        return 0


def pengyouquan(d, shifou_pengyouquan, shifou_shipinhao, serial):
    task_yanghao = []
    if (shifou_pengyouquan):
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

        if (task_temp == "朋友圈"):
            filepath = './shuju/' + serial + ".pkl"
            print("filepath-->", filepath)
            if (os.path.isfile(filepath)):
                updata_pkl(filepath, "进行的任务", "vx养号-朋友圈")
            pengyouquan_huadong_cishu_xiao = read_config("pengyouquan_huadong_cishu_xiao")
            if (pengyouquan_huadong_cishu_xiao == None):
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
                bb += 1
                if (random.randint(1, 11) > 10 - int(pengyouquan_dianzan_gailv)):
                    if (d(resourceId='com.tencent.mm:id/r2').exists(timeout=3)):
                        dianzans = d(resourceId='com.tencent.mm:id/r2')
                        if (len(dianzans) > 1):
                            dianzans[1].click()
                            time.sleep(random.randint(1, 2))
                            if (d(text="赞").exists(timeout=3)):
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
                if (random.randint(1, 11) > 10 - int(shipinhao_dianzai_gailv)):
                    if (d(resourceId='com.tencent.mm:id/ng5').exists(timeout=3)):
                        d(resourceId='com.tencent.mm:id/ng5').click()
                        time.sleep(random.randint(3, 5))
                    else:
                        print("首页没有朋友圈")
                        # return 0
                d.swipe_ext("up", scale=0.9)
                time.sleep(random.randint(10, 20))
        time.sleep(random.randint(2, 5))


def yanghao_gongzhonghao(d, comment_path, serial):
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
    gongzhonghao_count = random.randint(int(gongzhonghao_zhanghao_liulan_xiao), int(gongzhonghao_zhanghao_liulan_da))
    temp_count = 0
    while (temp_count < gongzhonghao_count):
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


def yanghao_xinwen(d, serial):
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


def into_qunfa(d, serial):
    if (d(text='我').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='我').info)
        time.sleep(random.randint(1, 3))
    else:
        print("meiyou 搜索按钮1")
        return 0

    if (d(text='设置').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='设置').info)
        time.sleep(random.randint(1, 5))
    else:
        print("meiyou 搜索按钮2")
        return 0

    if (d(text='通用').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='通用').info)
        time.sleep(random.randint(1, 5))
    else:
        print("meiyou 搜索按钮2")
        return 0

    time.sleep(1)
    d.swipe_ext(Direction.FORWARD)  # 页面下翻, 等价于 d.swipe_ext("up"), 只是更好理解
    time.sleep(1)

    if (d(text='辅助功能').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='辅助功能').info)
        time.sleep(random.randint(1, 5))
    else:
        print("meiyou 搜索按钮2")
        return 0

    if (d(text='群发助手').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='群发助手').info)
        time.sleep(random.randint(1, 5))
    else:
        print("meiyou 搜索按钮2")
        return 0

    if (d(text='开始群发').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        random_click_view(d, d(text='开始群发').info)
        time.sleep(random.randint(1, 5))
    else:
        print("meiyou 搜索按钮2")
        return 0

    return 1


def qunfa(d, serial, shifouqufnawenzi, shifouqunfashoucang, qunfaneirong, qunfajiangeshijian):
    global added_friend
    result_into_qunfa = into_qunfa(d, serial)
    while (True):
        if (d(text='新建群发').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(text='新建群发').info)
            time.sleep(random.randint(3, 10))
        else:
            print("meiyou 搜索按钮")
            return 0
        if (result_into_qunfa != 1):
            return 0

        max_add_friend = 1000
        added_count = 0
        circle_flag = True
        while (added_count <= max_add_friend):
            friends = d(resourceId='com.tencent.mm:id/kbq')
            print("meng=", friends)
            print(len(friends))
            count = 0
            small_count = 0
            for fridend in friends:
                print(fridend.info["text"])
                if (count < len(friends) - 2):  # 最后一个不让点击，点击会出问题
                    if (fridend.info["text"] not in added_friend):
                        added_friend.append(fridend.info["text"])
                        random_click_view(d, fridend.info)
                        time.sleep(0.1)
                        # result_sixin= sixin_fri(d,shifouqufnawenzi,shifouqunfashoucang,qunfaneirong,qunfajiangeshijian)
                        # if(result_sixin == 1):
                        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                        # back_to_home(d)
                        time.sleep(0.1)
                        small_count += 1
                        added_count += 1
                count += 1

            time.sleep(1)
            if (small_count < -1):
                circle_flag = False
                break
            # if(d(textContains = "个朋友").exists(timeout=1)):
            #     print("已经到底了")
            #     return 99
            # d.swipe_ext(Direction.FORWARD)
            d.swipe_ext("up", scale=0.6)
            time.sleep(1)

        if (d(textContains='选中(').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(textContains='选中(').info)
            time.sleep(random.randint(3, 10))
        else:
            print("meiyou 搜索按钮")
            return 0

        sixin_fri(d, shifouqufnawenzi, shifouqunfashoucang, qunfaneirong, qunfajiangeshijian)

        if (circle_flag == False):
            return 99


def sixin_fri(d, shifouqufnawenzi, shifouqunfashoucang, qunfaneirong, qunfajiangeshijian):
    biaoqing = ["[得意]", "[微笑]", "[色]", "[呲牙]", "[调皮]", "[偷笑]", "[愉快]", "[憨笑]", "[亲亲]", "[笑脸]",
                "[奸笑]", "[捂脸]", "[嘿哈]", "[破涕为笑]", "[机智]", "[皱眉]", "[耶]", "[吃瓜]", "[加油]", "[Emm]",
                "[666]", "[让我看看]", "[哇]", "[好的]", "[社会社会]", "[旺柴]", "[握手]", "[抱拳]", "[拳头]", "[OK]",
                "[合十]", "[啤酒]", "[咖啡]", "[蛋糕]", "[玫瑰]", "[太阳]", "[庆祝]", "[礼物]", "[红包]", "[發]",
                "[福]", "[烟花]", "[爆竹]"]
    # if (d(text='发消息').exists(timeout=3)):
    #     # d(resourceId='com.tencent.mm:id/plus_icon').click()
    #     print(d(text='发消息').info)
    #     random_click_view(d, d(text='发消息').info)
    #     time.sleep(random.randint(3, 10))
    # else:
    #     print("没有发消息按钮")
    #     return 0

    if (shifouqufnawenzi):
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
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='发送').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            print(d(text='发送').info)
            random_click_view(d, d(text='发送').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0
    if (shifouqufnawenzi):
        if (shifouqunfashoucang):
            # sixin_shoucang(d, nick_name)
            print("shoucang")
            if (d(text='再发一条').exists(timeout=3)):
                # d(resourceId='com.tencent.mm:id/plus_icon').click()
                # print(d(text='再发一条').info)
                # random_click_view(d, d(text='再发一条').info)
                nn = d(text='再发一条')
                nn[len(nn) - 1].click()
                time.sleep(random.randint(3, 10))
            else:
                print("首页没有加号按钮")
                return 0
    else:
        if (shifouqunfashoucang):
            # sixin_shoucang(d, nick_name)
            print("shoucang")
            if (d(text='新建转发').exists(timeout=3)):
                # d(resourceId='com.tencent.mm:id/plus_icon').click()
                print(d(text='新建转发').info)
                random_click_view(d, d(text='新建转发').info)
                time.sleep(random.randint(3, 10))
            else:
                print("首页没有加号按钮")
                return 0

    if (shifouqunfashoucang):
        if (d(resourceId='com.tencent.mm:id/bjz').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(resourceId='com.tencent.mm:id/bjz').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='相册').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(text='相册').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(resourceId='com.tencent.mm:id/jdh').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(resourceId='com.tencent.mm:id/jdh').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='原图').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(text='原图').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='发送').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(text='发送').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

        if (d(text='发送').exists(timeout=3)):
            # d(resourceId='com.tencent.mm:id/plus_icon').click()
            random_click_view(d, d(text='发送').info)
            time.sleep(random.randint(3, 10))
        else:
            print("首页没有加号按钮")
            return 0

    if (str(qunfajiangeshijian).isdigit()):
        sleep_time_temp = random.randint(int(qunfajiangeshijian) - 10, int(qunfajiangeshijian))
        if (int(sleep_time_temp) > 0):
            time.sleep(int(sleep_time_temp))
    else:
        time.sleep(10)
    return 1


def sixin_shoucang(d, nick_name):
    if (d(resourceId='com.tencent.mm:id/bkk').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/bkk').info)
        random_click_view(d, d(resourceId='com.tencent.mm:id/bkk').info)
        time.sleep(1)
        d(resourceId='com.tencent.mm:id/bkk').set_text("")
        time.sleep(2)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(resourceId='com.tencent.mm:id/bjz').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(resourceId='com.tencent.mm:id/bjz').info)
        random_click_view(d, d(resourceId='com.tencent.mm:id/bjz').info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text='我的收藏').exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text='我的收藏').info)
        random_click_view(d, d(text='我的收藏').info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text=nick_name).exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text=nick_name).info)
        random_click_view(d, d(text=nick_name).info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0

    if (d(text="发送").exists(timeout=3)):
        # d(resourceId='com.tencent.mm:id/plus_icon').click()
        print(d(text="发送").info)
        random_click_view(d, d(text="发送").info)
        time.sleep(3)
    else:
        print("首页没有加号按钮")
        return 0


def xiaoyewu(d, serial, search_path, sixin_comment):
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
        # d(textContains='查找手机').click()

        random_click_view(d, d(textContains='查找手机').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有搜索按钮")
        return 0
    time.sleep(random.randint(1, 10))

    # d.click(528,969)
    if (d(text='添加到通讯录').exists(timeout=3)):
        # d(textStartsWith='搜索').click()
        # d(text='添加到通讯录').click()

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
        # return 0

    if (d(resourceId='com.tencent.mm:id/m_1').exists(timeout=3)):  # 出现这种情况证明已经加过好友啦
        # d(text='该用户不存在').click()
        beizhu = str(search_key) + d(resourceId='com.tencent.mm:id/m_1').get_text()
        d(resourceId='com.tencent.mm:id/m_1').set_text(beizhu)
        time.sleep(random.randint(3, 10))
    else:
        print("meiyou 备注view")
        # return 0

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

        # random_click_view(d,d(text='发送').info)

        time.sleep(random.randint(3, 10))
    else:
        print("首页没有加号按钮")
        return 0
    # d.click(528, 2009)
    time.sleep(random.randint(3, 10))
    if (d(resourceId='com.tencent.mm:id/jlh').exists(timeout=5)):
        # d(text='该用户不存在').click()
        # time.sleep(3)3
        print("用户不存在")
        return 88
    # d.click(506, 668)
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


def conpare_dif(big, small):
    bigs = str(big).split("/")
    for big_t in bigs:
        if (str(small).count(big_t) > 0):
            return 0
    return 1


def sixin(d, serial, sixin_comment, home_filter, c_t, age_small, age_big, fans_count_small, fans_count_big):
    biaoqing = ["[龇牙]", "[哼]", "[哦]", "[呆住]", "[贴贴]", "[有八卦]", "[尊嘟假嘟]", "[你好呀]", "[吹口哨]",
                "[元旦快乐]", "[新年快乐]", "[出去丸]", "[放假啦]", "[进度50]", "[我看行]", "[稍等]", "[让人头大]",
                "[进度99]", "[柴犬]", "[羞涩]", "[头盔]", "[求求了]", "[美滋滋]", "[点点关注]", "[星星眼]", "[抱抱]",
                "[放轻松]", "[健身]", "[礼花]", "[稳]", "[get]", "[龇牙]", "[皇冠]", "[双鸡]", "[发]", "[灯笼]",
                "[福字]", "[鞭炮]", "[元宝]", "[钱]", "[气球]", "[赞]", "[肌肉]", "[早上好]", "[优秀]", "[网红]"]
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


def backToHome(d):
    dd = 0
    time.sleep(3)
    while (dd < 10):
        elements = d(text='首页')  # 获取所有文本为'some_text'的元素
        # print(len(elements))
        if (len(elements) > 0):
            return "1"
        time.sleep(0.8)
        d.press("back")
        time.sleep(0.8)
        dd += 1


class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("微信业务")
        self.setGeometry(100, 100, 700, 300)
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
        self.caozuo_tiel = QLabel("*" * 55 + "操       作" + "*" * 55)
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
        self.table_widget.setHorizontalHeaderLabels(
            ['选中', '编号', '昵称', '连接状态', '运行状态', '当前任务', "业务数量统计"])
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
        self.scroll_area.setFixedWidth(700)

        self.horizontal_layout = QHBoxLayout()
        # self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button0 = QLabel(" ")
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("dy极速版同城评论")
        self.radio_button1.setChecked(False)
        self.radio_button8 = QCheckBox("dy私信回复-极速")
        self.radio_button8.setChecked(False)
        self.radio_button10 = QCheckBox("dy私信回复-正版")
        self.radio_button10.setChecked(False)
        self.radio_button9 = QCheckBox("群发图片")
        self.radio_button9.setChecked(False)
        self.radio_button2 = QCheckBox("养号")
        self.radio_button2.setChecked(False)
        self.radio_button3 = QCheckBox("朋友圈")
        self.radio_button3.setChecked(False)
        self.radio_button4 = QCheckBox("视频号")
        self.radio_button4.setChecked(False)
        self.radio_button6 = QCheckBox("公众号")
        self.radio_button6.setChecked(True)
        self.radio_button7 = QCheckBox("新闻")
        self.radio_button7.setChecked(False)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addWidget(self.radio_button10)
        self.horizontal_layout.addWidget(self.radio_button8)
        self.horizontal_layout.addStretch(1)
        #
        # self.horizontal_layout.addWidget(self.radio_button9)
        # self.horizontal_layout.addWidget(self.radio_button2)
        # self.horizontal_layout.addWidget(self.radio_button3)
        # self.horizontal_layout.addWidget(self.radio_button4)
        # self.horizontal_layout.addWidget(self.radio_button6)
        # self.horizontal_layout.addWidget(self.radio_button7)
        # self.horizontal_layout.addWidget(self.radio_button5)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
        # This will add the horizontal layout with the title and radio buttons
        self.horizontal_layout_2 = QHBoxLayout()
        self.radio_button2_0 = QLabel("              ")
        self.radio_button2_00 = QLabel("     ")
        self.radio_button2_1 = QCheckBox("抖音同城粉丝点赞")
        self.radio_button2_1.setChecked(False)
        self.radio_button2_8 = QCheckBox("抖音同城粉丝点赞-极速")
        self.radio_button2_8.setChecked(False)
        self.radio_button2_10 = QCheckBox("搜索进入同城")
        self.radio_button2_10.setChecked(False)
        self.horizontal_layout_2.addWidget(self.radio_button2_0)
        self.horizontal_layout_2.addWidget(self.radio_button2_1)
        self.horizontal_layout_2.addWidget(self.radio_button2_10)
        self.horizontal_layout_2.addWidget(self.radio_button2_00)

        self.label_from = QLabel('                      评论条数限制:')

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
        self.label_seconds = QLabel(
            '               ', self)

        self.label_from111 = QLabel('   视频发布时间筛选:')

        # huadongcishuxiao = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuxiao")
        # if (huadongcishuxiao != None):
        #     self.jiarenshurukuang = QLineEdit(huadongcishuxiao)
        # else:
        #     self.jiarenshurukuang = QLineEdit("8")
        # self.jiarenshurukuang.setFixedWidth(50)

        self.jiarenshurukuang = QComboBox()

        # 添加选项到下拉框
        self.jiarenshurukuang.addItem("不筛选")
        self.jiarenshurukuang.addItem("一天内")
        self.jiarenshurukuang.addItem("一周内")



        self.label_from222 = QLabel('至')
        self.label_from222.setFixedWidth(15)

        huadongcishuda = get_value_by_key_pkl("shuju_config.pkl", "huadongcishuda")
        if (huadongcishuda != None):
            self.huadongcishu_big = QLineEdit(huadongcishuda)
        else:
            self.huadongcishu_big = QLineEdit("20")
        self.huadongcishu_big.setFixedWidth(40)
        self.label_fromci = QLabel('                       ')

        self.label_from_time = QLabel('                      评论内容配置:')

        yunxingshichang = get_value_by_key_pkl("shuju_config.pkl", "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("多条评论内容用'-'隔开")
        self.run_time.setFixedWidth(180)

        self.label_from_search = QLabel('        视频评论条数范围：')

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
        self.label_seconds_search = QLabel('条     ', self)
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout_diyihang = QHBoxLayout()
        self.h_layout_diyihang.addWidget(self.label_from_time)
        self.h_layout_diyihang.addWidget(self.run_time)
        self.h_layout_diyihang.addWidget(self.label_from_search)
        self.h_layout_diyihang.addWidget(self.line_edit_from_search)
        # self.h_layout_diyihang.addWidget(self.label_to_search)
        # self.h_layout_diyihang.addWidget(self.line_edit_to_search)
        self.h_layout_diyihang.addWidget(self.label_seconds_search)
        self.label_from111_kongge = QLabel('                             ')
        self.label_from111_shoucang = QLabel('抖音私信话术：')
        self.label_from111_shoucang.setFixedWidth(80)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv")
        if (shoucanggailv != None):
            self.shoucang_gailv = QLineEdit(shoucanggailv)
        else:
            self.shoucang_gailv = QLineEdit("请输入抖音私信话术")
        self.shoucang_gailv.setFixedWidth(300)
        self.label_from222_shoucang = QLabel('')
        self.label_from222_pinglun = QLabel('   ')

        self.label_from111_dianzan = QLabel('群发间隔时间：')
        self.label_from111_dianzan.setFixedWidth(80)

        dianzangailv = get_value_by_key_pkl("shuju_config.pkl", "dianzangailv")
        if (dianzangailv != None):
            self.shoucang_dianzan = QLineEdit(dianzangailv)
        else:
            self.shoucang_dianzan = QLineEdit("50")
        self.shoucang_dianzan.setFixedWidth(50)
        self.label_from222_dianzan = QLabel('秒     ')

        self.label_from111_kongge222 = QLabel('           ')
        self.h_layout_disanhang = QHBoxLayout()
        self.h_layout_disanhang.addWidget(self.label_from111_kongge)
        self.h_layout_disanhang.addWidget(self.label_from111_shoucang)
        self.h_layout_disanhang.addWidget(self.shoucang_gailv)
        self.h_layout_disanhang.addWidget(self.label_from222_shoucang)
        # self.h_layout_disanhang.addWidget(self.label_from111_pinglun)
        # self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        # self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        # self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        self.h_layout_disanhang.addWidget(self.label_from222_pinglun)

        # self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        # self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from111_kongge222)

        self.label_from111_kongge_diwuhang = QLabel('                                     ')
        self.label_from111_shoucang_diwuhang = QLabel('同城粉丝点赞个数：')
        self.label_from111_shoucang_diwuhang.setFixedWidth(105)

        douyinfabushuliang = get_value_by_key_pkl("shuju_config.pkl", "douyinfabushuliang")
        if (douyinfabushuliang != None):
            self.douyinfabushuliang = QLineEdit(douyinfabushuliang)
        else:
            self.douyinfabushuliang = QLineEdit("请输入同城粉丝点赞个数")
        self.douyinfabushuliang.setFixedWidth(140)
        self.label_from222_shoucang_diwuhang = QLabel('')
        self.label_from222_pinglun_diwuhang = QLabel('        ')

        self.label_from111_dianzan_diwuhang = QLabel('单个作者粉丝视频点赞个数：')
        self.label_from111_dianzan_diwuhang.setFixedWidth(160)

        qunfashijiajiange = get_value_by_key_pkl("shuju_config.pkl", "qunfashijianjiange")
        print("qunfashijiajiange=",qunfashijiajiange)
        if (qunfashijiajiange != None):
            self.qunfashijianjiange = QLineEdit(qunfashijiajiange)
        else:
            self.qunfashijianjiange = QLineEdit("50")
        self.qunfashijianjiange.setFixedWidth(70)
        self.label_from222_dianzan_diwuhang = QLabel('个')

        self.label_from111_kongge222_wiwuhang = QLabel('           ')

        self.h_layout_disanhang_diwuhang = QHBoxLayout()
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from111_kongge_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from111_shoucang_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.douyinfabushuliang)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from222_shoucang_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from222_pinglun_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from111_dianzan_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.qunfashijianjiange)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from222_dianzan_diwuhang)
        self.h_layout_disanhang_diwuhang.addWidget(self.label_from111_kongge222_wiwuhang)

        # 抖音私信文案配置
        self.h_layout_douyinsixinneirong = QHBoxLayout()
        self.label_from111_douyinsixinneirong22 = QLabel('                  ')
        self.label_from111_douyinsixinneirong = QLabel('抖音私信内容：')
        self.label_from111_douyinsixinneirong.setFixedWidth(80)

        douyinsixinneirong = get_value_by_key_pkl("shuju_config.pkl", "douyinsixinneirong")
        if (douyinsixinneirong != None):
            self.douyinsixinneirong = QLineEdit(douyinsixinneirong)
        else:
            self.douyinsixinneirong = QLineEdit("请输入抖音私信内容(用'-'分割)")
        self.douyinsixinneirong.setFixedWidth(450)
        self.label_from222_douyinsixinneirong = QLabel('')
        self.label_from222_douyinsixinneirong1 = QLabel('        ')

        self.h_layout_douyinsixinneirong.addWidget(self.label_from111_douyinsixinneirong22)
        self.h_layout_douyinsixinneirong.addWidget(self.label_from111_douyinsixinneirong)
        self.h_layout_douyinsixinneirong.addWidget(self.douyinsixinneirong)
        self.h_layout_douyinsixinneirong.addWidget(self.label_from222_douyinsixinneirong)

        # 抖音私信搜索关键字配置
        self.h_layout_douyinsixinguanjianzi = QHBoxLayout()
        self.label_from111_douyinsixinguanjianzi22 = QLabel('                  ')
        self.label_from111_douyinsixinguanjianzi = QLabel('dy私信搜索词:')
        self.label_from111_douyinsixinguanjianzi.setFixedWidth(85)

        douyinsixinguanjianzi = get_value_by_key_pkl("shuju_config.pkl", "douyinsixinguanjianzi")
        if (douyinsixinguanjianzi != None):
            self.douyinsixinguanjianzi = QLineEdit(douyinsixinguanjianzi)
        else:
            self.douyinsixinguanjianzi = QLineEdit("请输入抖音私信搜索词配置(用'-'分割)")
        self.douyinsixinguanjianzi.setFixedWidth(450)
        self.label_from222_douyinsixinguanjianzi = QLabel('')
        self.label_from222_douyinsixinguanjianzi1 = QLabel('        ')

        self.h_layout_douyinsixinguanjianzi.addWidget(self.label_from111_douyinsixinguanjianzi22)
        self.h_layout_douyinsixinguanjianzi.addWidget(self.label_from111_douyinsixinguanjianzi)
        self.h_layout_douyinsixinguanjianzi.addWidget(self.douyinsixinguanjianzi)
        self.h_layout_douyinsixinguanjianzi.addWidget(self.label_from222_douyinsixinguanjianzi)

        # 抖音私信时间间隔 以及抖音私信个数限制
        self.h_layout_douyinsixinsixinshijianjiange = QHBoxLayout()
        self.label_from111_douyinsixinsixinshijianjiange22 = QLabel('                  ')
        self.label_from111_douyinsixinsixinshijianjiange = QLabel('dy私信时间间隔:')
        self.label_from111_douyinsixinsixinshijianjiange.setFixedWidth(88)

        douyinsixinsixinshijianjiange = get_value_by_key_pkl("shuju_config.pkl", "douyinsixinsixinshijianjiange")
        if (douyinsixinsixinshijianjiange != None):
            self.douyinsixinsixinshijianjiange = QLineEdit(douyinsixinsixinshijianjiange)
        else:
            self.douyinsixinsixinshijianjiange = QLineEdit("请输入抖音私信时间间隔")
        self.douyinsixinsixinshijianjiange.setFixedWidth(150)
        self.label_from222_douyinsixinsixinshijianjiange = QLabel('秒')
        self.label_from222_douyinsixinsixinshijianjiange1 = QLabel('            ')

        self.label_from111_douyinsixinsixingeshuxianzhi = QLabel('dy私信个数:')
        self.label_from111_douyinsixinsixingeshuxianzhi.setFixedWidth(80)

        douyinsixinsixingeshuxianzhi = get_value_by_key_pkl("shuju_config.pkl", "douyinsixinsixingeshuxianzhi")
        if (douyinsixinsixingeshuxianzhi != None):
            self.douyinsixinsixingeshuxianzhi = QLineEdit(douyinsixinsixingeshuxianzhi)
        else:
            self.douyinsixinsixingeshuxianzhi = QLineEdit("请输入抖音私信个数限制")
        self.douyinsixinsixingeshuxianzhi.setFixedWidth(150)
        self.label_from222_douyinsixinsixingeshuxianzhi = QLabel('个')

        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from111_douyinsixinsixinshijianjiange22)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from111_douyinsixinsixinshijianjiange)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.douyinsixinsixinshijianjiange)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from222_douyinsixinsixinshijianjiange)

        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from111_douyinsixinsixingeshuxianzhi)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.douyinsixinsixingeshuxianzhi)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from222_douyinsixinsixingeshuxianzhi)
        self.h_layout_douyinsixinsixinshijianjiange.addWidget(self.label_from222_douyinsixinsixinshijianjiange1)

        self.h_layout = QHBoxLayout()
        self.h_layout.setSpacing(5)
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        self.h_layout.addWidget(self.label_to)
        # self.h_layout.addWidget(self.line_edit_to)
        self.h_layout.addWidget(self.label_seconds)
        #
        self.h_layout.addWidget(self.label_from111)
        self.h_layout.addWidget(self.jiarenshurukuang)
        # self.h_layout.addWidget(self.label_from222)
        # self.h_layout.addWidget(self.huadongcishu_big)
        self.h_layout.addWidget(self.label_fromci)

        # self.h_layout.setSpacing(5)
        # 设置布局与窗口边框之间的边距（例如，设置为 0 像素）
        # self.h_layout.setContentsMargins(0, 0, 0, 0)

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

        self.h_layout_kongge9 = QHBoxLayout()
        self.label_file_kongge9 = QLabel("                          ")
        self.h_layout_kongge9.addWidget(self.label_file_kongge9)

        self.h_layout_kongge10 = QHBoxLayout()
        self.label_file_kongge10 = QLabel("                          ")
        self.h_layout_kongge10.addWidget(self.label_file_kongge10)

        self.h_layout_kongge11 = QHBoxLayout()
        self.label_file_kongge11 = QLabel("                          ")
        self.h_layout_kongge11.addWidget(self.label_file_kongge11)

        self.h_layout_kongge12 = QHBoxLayout()
        self.label_file_kongge12 = QLabel("                          ")
        self.h_layout_kongge12.addWidget(self.label_file_kongge12)

        self.h_layout_kongge13 = QHBoxLayout()
        self.label_file_kongge13 = QLabel("                          ")
        self.h_layout_kongge13.addWidget(self.label_file_kongge13)

        # 这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择好友文件路径配置:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
        if (file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入搜索文件路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件", self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

        # 以下是评论文件选择器
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
        self.label_file_gouwu = QLabel("                      请选择抖音私信文件路径:")
        self.h_layout_dir_gouwu.addWidget(self.label_file_gouwu)

        file_temp_path_gouwu = get_value_by_key_pkl("shuju_config.pkl", "file_path_gouwu")
        if (file_temp_path_gouwu != None):
            self.file_textbox_gouwu = QLineEdit(file_temp_path_gouwu)
        else:
            self.file_textbox_gouwu = QLineEdit("请选择抖音私信文件路径")
        self.h_layout_dir_gouwu.addWidget(self.file_textbox_gouwu)
        self.file_button_gouwu = QPushButton("选择文件", self)
        self.temp_gouwu = QLabel("                          ")
        self.h_layout_dir_gouwu.addWidget(self.file_button_gouwu)
        self.h_layout_dir_gouwu.addWidget(self.temp_gouwu)

        self.clear_task_config_button = QPushButton('一键清除任务列表', self)
        self.clear_task_config_button.clicked.connect(self.clear_task)

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

        # 这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择配置文件夹:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl", "file_path")
        if (file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入文件夹路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件", self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

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
        layout.addLayout(self.h_layout_kongge9)
        layout.addLayout(self.horizontal_layout_2)
        layout.addWidget(self.caozuo_config)

        layout.addLayout(self.h_layout_kongge)
        #layout.addLayout(self.h_layout_dir)
        #layout.addLayout(self.h_layout_kongge1)
        #layout.addLayout(self.h_layout_dir_comment)
        #layout.addLayout(self.h_layout_kongge2)
        #layout.addLayout(self.h_layout_dir_gouwu)
        layout.addLayout(self.h_layout_kongge8)
        layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge3)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge5)
        layout.addLayout(self.h_layout_disanhang_diwuhang)
        layout.addLayout(self.h_layout_kongge4)
        layout.addLayout(self.h_layout_dir)
        layout.addLayout(self.h_layout_disanhang)
        layout.addWidget(self.scroll_area_task)


        # layout.addLayout(self.h_layout_kongge10)
        # layout.addLayout(self.h_layout_douyinsixinneirong)
        # layout.addLayout(self.h_layout_kongge11)
        # layout.addLayout(self.h_layout_douyinsixinguanjianzi)
        # layout.addLayout(self.h_layout_kongge12)
        #layout.addLayout(self.h_layout_douyinsixinsixinshijianjiange)
        layout.addLayout(self.h_layout_kongge13)

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
        self.execute_button.resize(100, 30)

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
        # layout.addWidget(self.execute_button_reset)

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
                self.excel_file = selected_file
                self.import_config()
                self.refresh_pkl_files_test()

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
        print("")
        path_dir = "task_config"
        create_directory_if_not_exists(path_dir)

        # path = path_dir+"/"+"config.pkl"
        # self.judge_pkl_creat(path)
        # 指定文件的路径
        with video_lock:
            file_path = self.file_textbox.text()
            # 使用 with 语句打开文件，这样可以确保文件在读取完毕后自动关闭
            with open(file_path, 'r') as file:
                # 逐行读取文件内容并打印
                for line in file:
                    # print(line, end='')  # 使用 end='' 是为了避免打印每行末尾的额外换行符
                    # if ((str(line).count("_") > 0) and (str(line).count("/") > 0)):
                    #     file_name = str(line).split("/")[-2]
                    #     new_data = {"url": str(line).split("_")[0], "BIG_COUNT": int(str(line).split("_")[1]),
                    #                 "TONGJI": 0}
                        temps = str(line).split("_")
                        if(len(temps)>2):
                            new_data = {"url":str(line).split("_")[1]+ str(line).split("_")[2], "BIG_COUNT": 10,
                                        "TONGJI": 0}
                            file_name = str(line).split("_")[0]
                            print("newdata=", new_data)
                            file_name = path_dir + "/" + file_name + ".pkl"
                            print("file_name=", file_name)
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
            chosen_file = pkl_files[0]
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
        print("---------------")

        updata_pkl_config_mianban("jiaobenyunxingshichang", self.run_time.text())
        updata_pkl_config_mianban("sousuocipinlvxiao", self.line_edit_from_search.text())
        # updata_pkl_config_mianban("sousuocipinlvda", self.line_edit_to_search.text())
        updata_pkl_config_mianban("huadongjiangexiao", self.line_edit_from.text())
        # updata_pkl_config_mianban("huadongjiangeda", self.line_edit_to.text())
        updata_pkl_config_mianban("huadongcishuxiao", self.jiarenshurukuang.currentText())
        # updata_pkl_config_mianban("huadongcishuda", self.huadongcishu_big.text())
        updata_pkl_config_mianban("shoucanggailv", self.shoucang_gailv.text())
        # # updata_pkl_config_mianban("guanzhugailv", self.shoucang_guanzhu.text())
        # updata_pkl_config_mianban("dianzangailv", self.shoucang_dianzan.text())
        updata_pkl_config_mianban("douyinfabushuliang", self.douyinfabushuliang.text())
        updata_pkl_config_mianban("qunfashijianjiange", self.qunfashijianjiange.text())
        #
        # updata_pkl_config_mianban("douyinsixinguanjianzi", self.douyinsixinguanjianzi.text())
        # updata_pkl_config_mianban("douyinsixinsixingeshuxianzhi", self.douyinsixinsixingeshuxianzhi.text())
        # updata_pkl_config_mianban("douyinsixinneirong", self.douyinsixinneirong.text())
        # updata_pkl_config_mianban("douyinsixinsixinshijianjiange", self.douyinsixinsixinshijianjiange.text())
        # updata_pkl_config_mianban("pinglungailv", self.shoucang_pinglun.text())
        print("888")

        if (self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            # print(temp)
            updata_pkl("./shuju/" + temp + ".pkl", "执行状态", "运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "dy极速同城评论")
        # self.scroll_area.widget().layout().item_list()[0].widget()
        print("999")

        self.refresh_pkl_files()
        tasks = []
        # self.scroll_area.ensureWidgetVisible(100)
        if (self.radio_button1.isChecked() == True):
            tasks.append("sixin")
        if (self.radio_button8.isChecked() == True):
            tasks.append("sixin_reply")
        if (self.radio_button10.isChecked() == True):
            tasks.append("sixin_reply_zhengban")
        if (self.radio_button2_1.isChecked() == True):
            tasks.append("tongcheng_fansi_like")
        if (self.radio_button2_10.isChecked() == True):
            tasks.append("sousuojinru")
        # if (self.radio_button2_8.isChecked() == True):
        #     tasks.append("tongcheng_fansi_like_douyin")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")
        print("tasks------------", tasks)
        # if (os.path.isfile(self.file_textbox.text())):
        #     print("手机号配置文件加载")
        # else:
        #     print("手机号配置文件buzai")
        #     return
        # if (os.path.isfile(self.file_textbox_comment.text())):视频
        #     print("评论文件加载")
        # else:
        #     print("公众号配置文件不在")
        #     return
        # if (os.path.isfile(self.file_textbox_gouwu.text())):
        #     print("抖音私信文件加载完毕")
        # else:
        #     print("抖音私信文件不在")
        #     return

        thread = threading.Thread(target=self.thread_temp, args=(tasks,self.run_time.text(),self.line_edit_from_search.text(),self.line_edit_from.text(),self.jiarenshurukuang.currentText(),self.shoucang_gailv.text(),self.douyinfabushuliang.text(),self.qunfashijianjiange.text()))
        thread.start()

        self.selected_ids = []

    def thread_temp(self, tasks,comment_content,comment_fanwei,comment_count,comment_time,douyinsixinhuashu,tongchengdianzanzongshu,tongchengdianzandage):
        count_phone = 0

        # if(("sixin_reply" in tasks) or ("sixin_reply_zhengban" in tasks)):
        #     for serial in self.selected_ids:
        #         print("fudai_path")
        #         # thread = threading.Thread(target=operate_device, args=(
        #         # serial, tasks, comment_content, comment_fanwei, comment_count, comment_time, douyinsixinhuashu))
        #         try:
        #             tongbu_flag = 1
        #             operate_device(serial, tasks, comment_content, comment_fanwei, comment_count, comment_time,douyinsixinhuashu, tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage)
        #         except:
        #             print()
        #         print("同步执行完了")
        #
        #
        #         time.sleep(random.randint(2, 5))
        # else:
        #     if (("sixin" in tasks) or ("tongcheng_fansi_like" in tasks) or ("tongcheng_fansi_like_douyin" in tasks)):
        for serial in self.selected_ids:
            print("fudai_path")
            tongbu_flag = 0
            thread = threading.Thread(target=operate_device, args=(serial, tasks, comment_content, comment_fanwei, comment_count, comment_time, douyinsixinhuashu,tongbu_flag,tongchengdianzanzongshu,tongchengdianzandage))
            # 手机号文件配置路径、评论文件路径---不用、任务列表、添加好友申请语、添加好友时间间隔小、添加好友时间间隔大、添加好友限制个数、粉丝数量大、年龄限制小、收藏、评论、点赞、关注，年龄限制大，购物文件配置路径、是否私信视频作者，是否私信视频评论用户
            # threads.append(thread)
            thread.start()
            time.sleep(random.randint(2, 5))
            count_phone += 1


    def add_text(self):
        print("")


    def clear_task(self):
        print("")

        if (os.path.isdir("./task_config")):
            self.delete_all_files_in_folder("task_config")
            self.refresh_pkl_files_test()

    def delete_all_files_in_folder(self,folder_path):
        # 确保文件夹存在
        if not os.path.exists(folder_path):
            print(f"文件夹 {folder_path} 不存在")
            return

        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # 如果是文件则删除
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除 {file_path} 时出错: {e}")

    def execute_delete_button_clicked(self):
        print("---------------")
        if (self.selected_ids == []):
            toast("请选择删除的机型")
            return
        for temp in self.selected_ids:
            # print(temp)
            if (os.path.isfile("./shuju/" + temp + ".pkl")):
                os.remove("./shuju/" + temp + ".pkl")
        self.refresh_pkl_files()
        self.selected_ids = []

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
        directory = './task_config'
        row_index = 0
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                print("filename---", filename)
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'rb') as file:
                        data = pickle.load(file)
                        print("data=", data)
                        print("row_index=", row_index)

                        # 假设数据是一个字典
                        if isinstance(data, dict):
                            print("进来了")
                            print("-----", data.get('url', 'N/A'))

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

                                self.task_widget.setItem(row_index, 2,
                                                         QTableWidgetItem(str(data.get('BIG_COUNT', 'N/A'))))
                                self.task_widget.setItem(row_index, 3, QTableWidgetItem(str(data.get('TONGJI', 'N/A'))))


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
                            phone_name = get_value_by_key_pkl("config.pkl", data.get('name', 'N/A'))
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
    if (os.path.exists("config.pkl")):
        print()

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
