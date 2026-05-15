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
    QFileDialog, QTextEdit
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
def operate_device(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri):
    # 搜索路径、评论文件路径---不用、任务列表、私信内容配置、每个关键字搜索滑动视频数量小、每个关键字搜索滑动视频数量大、粉丝数量小、粉丝数量大、年龄限制小、收藏、评论、点赞、关注，年龄限制大，购物文件配置路径、是否私信视频作者，是否私信视频评论用户

    count_zong = 0
    while(True):
        try:
            result = main(serial, search_path, comment_path, task, run_time, change_small, chang_big, swipe_small,
                          swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu, count_zong,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri)
            if (result == "88"):
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
                           swipe_big, swipe_count, shoucang, pinglun, dianzan, guanzhu,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri)


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
        if (d(text='首页').exists(timeout=3)):
            print("当前在首页了。。。。。。。。")
            d.press("back")
            time.sleep(3)
            d.press("back")
            time.sleep(3)
            return 1
        else:
            print("当前bu在首页了。。。。。。。。")
        count += 1
        d.press("back")
    return 0
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
#搜索路径、评论文件路径、任务列表、运行时长、更换频率小、更换频率大、视频滑动间隔小、视频滑动间隔大、视频滑动次数、收藏、评论、点赞、关注
def main(serial, search_path,comment_path, task,run_time,change_small,chang_big,swipe_small,swipe_big,swipe_count,shoucang,pinglun,dianzan,guanzhu,count_zong,shipinhuadongcishu,gouwu,shifousixinzuozhe,shifousixinpinglunyonghu,shifouzuixin,jinyiri,jinqiri):
    # 搜索路径、评论文件路径---不用、任务列表、私信内容配置、每个关键字搜索滑动视频数量小、每个关键字搜索滑动视频数量大、粉丝数量小、粉丝数量大、年龄限制小、评论关键字过滤、评论、点赞、关注，年龄限制大，购物文件配置路径、是否私信视频作者，是否私信视频评论用户

    if(len(task) == 0):
        return
    chat_content = "你好/在么/真棒/哈喽"
    home_filter = shoucang

    d = get_device(serial)
    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    if("sixin" in task):
        sixin_comment = run_time
        search_key_count_video_small = int(change_small)
        search_key_count_video_big = int(chang_big)
        fans_count_small = int(swipe_small)
        fans_count_big = int(swipe_big)
        age_small = int(swipe_count)
        age_big = int(shipinhuadongcishu)
        comment_filter = shoucang
        pinglun = int(pinglun)
        dianzan = int(dianzan)
        guanzhu = int(guanzhu)
        shipinhuadongcishu = int(shipinhuadongcishu)

        # if (check_time_difference(run_time * 60)):
        #     return "88"

        # ocr_processor = OCRProcessor()
        print("开始了。。。")
        ocr_processor = ""

        comment_count_zong = 0
        random_integer = random.randint(search_key_count_video_small, search_key_count_video_big)
        big_wai_count = 0
        while(big_wai_count<random_integer):
            if (count_zong == 0):
                d.app_start(package_name="ca.zgrs.clipper")
                time.sleep(1)
                d.app_start(package_name="com.smile.gifmaker")
                result_back = back_to_home(d)
                if (result_back != 1):
                    return 0
            else:
                d.app_start(package_name="ca.zgrs.clipper")
                time.sleep(1)
                d.app_start(package_name="com.smile.gifmaker")
                backToHome(d)
                result_back = back_to_home(d)
                if (result_back != 1):
                    return 0

            # if (d(resourceId='com.smile.gifmaker:id/nasa_featured_default_search_view').exists(timeout=3)):
            #     d(resourceId='com.smile.gifmaker:id/nasa_featured_default_search_view').click()
            #     time.sleep(3)
            # else:
            #     print("首页没有搜索按钮")
            #     return 0
            d.click(d.info["displayWidth"]-80,155)
            time.sleep(5)

            search_key = get_random_line_from_file(search_path)
            shell_neibu(f"adb -s {serial} shell  am broadcast -a clipper.set -e text " + str(search_key))
            shell_neibu(f"adb -s {serial} shell input  keyevent 279")
            time.sleep(2)

            if (d(text='搜索').exists(timeout=3)):
                d(text='搜索').click()
                time.sleep(3)
            else:
                print("没有搜索按钮")
                return 0

            if (d(resourceId='com.smile.gifmaker:id/tab_filter_image').exists(timeout=8)):
                print("当前搜索成功")
            else:
                print("当前搜索失败啦")
                return 0

            if (d(resourceId='com.smile.gifmaker:id/tab_filter_image').exists(timeout=1)):
                d(resourceId='com.smile.gifmaker:id/tab_filter_image').click()

                time.sleep(3)
                if(shifouzuixin == True):
                    if (d(text='最新发布').exists(timeout=3)):
                        d(text='最新发布').click()
                        time.sleep(1)
                if (jinyiri == True):
                    if (d(text='近1日').exists(timeout=3)):
                        d(text='近1日').click()
                        time.sleep(1)
                if (jinqiri == True):
                    if (d(text='近7日').exists(timeout=3)):
                        d(text='近7日').click()
                        time.sleep(1)
                if (d(text='确定').exists(timeout=3)):
                    d(text='确定').click()
                    time.sleep(3)
            else:
                print("当前搜索失败啦")
                return 0

            swipe_count111 = 0
            # d.swipe(int(d.info["displayWidth"]) - 100, 600, 100, 800, 0.3)
            # time.sleep(1)
            while (swipe_count111 < 10):

                if (d(resourceId='com.smile.gifmaker:id/avatar').exists(timeout=3)):
                    d(resourceId='com.smile.gifmaker:id/avatar').click()
                    break
                d.swipe_ext("up", scale=0.8)
                #d.swipe_ext("left", scale=0.8)

                time.sleep(1)
                swipe_count111 += 1
            meigeshiphuadongjici = 0
            while (meigeshiphuadongjici < 10):
                if (d(text='抢首评').exists(timeout=1)):  # 当前视频没有评论，直接退出
                    print("当前视频没有评论，直接退出")
                else:
                    sixinzuozhe = shifousixinzuozhe
                    if (sixinzuozhe == True):
                        if (d(resourceId='com.smile.gifmaker:id/slide_play_avatar_click_area').exists(timeout=5)):
                            d(resourceId='com.smile.gifmaker:id/slide_play_avatar_click_area').click()
                            time.sleep(3)
                            c_t = ""
                            if(d(resourceId='com.smile.gifmaker:id/comment').exists(timeout=2)):
                                c_t = d(resourceId='com.smile.gifmaker:id/comment').get_text()

                            result_sixin = sixin(d,serial,sixin_comment,home_filter,c_t,age_small,age_big,fans_count_small,fans_count_big)

                            back_to_video(d)

                        else:
                            print("当前找不到坐着头像")
                            # return 0
                    sixinpinglunyonghu = shifousixinpinglunyonghu
                    if (sixinpinglunyonghu == True):  # 开始私信评论用户
                        if (d(resourceId='com.smile.gifmaker:id/comment_icon').exists(timeout=5)):
                            d(resourceId='com.smile.gifmaker:id/comment_icon').click()
                            time.sleep(3)
                        else:
                            print("当前找不到评论按钮啊")
                            continue

                        if (d(resourceId='com.smile.gifmaker:id/tabs_panel_full').exists(timeout=5)):
                            d(resourceId='com.smile.gifmaker:id/tabs_panel_full').click()
                            time.sleep(3)
                        else:
                            print("当前找不到评论按钮啊111")
                            # return 0
                        if (d(text='暂无评论').exists(timeout=2)):
                            print("暂无评论")
                            time.sleep(3)
                            continue

                        single_video_count = 0
                        while (single_video_count < 15):

                            print(f"当前视频的第{single_video_count}个评论")
                            # if (d(textContains='条回复').exists(timeout=5)):
                            #     d(textContains='条回复').click()
                            #     time.sleep(2)
                            time.sleep(2)
                            pingluns = d(resourceId='com.smile.gifmaker:id/comment')

                            for touxiang in pingluns:
                                info_t = touxiang.info
                                c_t = touxiang.get_text()
                                if (single_video_count != 0):
                                    time.sleep(random.randint(1, 30))

                                if (str(c_t) not in clicked_touxiang):
                                    top = info_t["bounds"]['top']
                                    left = info_t["bounds"]['left']
                                    d.click(int(int(left) - 80), int(top))
                                    clicked_touxiang.append(c_t)
                                    time.sleep(3)
                                    result_sixin = sixin(d,serial,sixin_comment,home_filter,c_t,age_small,age_big,fans_count_small,fans_count_big)
                                    single_video_count += 1
                                    if (result_sixin == 1):
                                        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
                                back_to_comment(d)
                            if (d(resourceId='com.smile.gifmaker.comment_detail:id/no_more_content').exists(timeout=1)):
                                break

                            d.swipe_ext("up", scale=0.8)
                            time.sleep(1)
                    time.sleep(1)
                back_to_video(d)
                time.sleep(2)
                d.swipe(500, int(d.info["displayHeight"])-300, 500, 50, 0.3)
                time.sleep(2)
                print(f"当前关键字的的第{meigeshiphuadongjici}个视频")
                meigeshiphuadongjici += 1
                tongji = get_value_by_key_pkl("./shuju/" + str(serial) + ".pkl", "tongji")
                if (int(tongji) > 100):
                    return "88"
            big_wai_count += 1


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
        self.setWindowTitle("ks业务")
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
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"私信统计"])
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

        self.radio_button1 = QCheckBox("快手私信")
        self.radio_button1.setChecked(True)
        self.radio_button2 = QCheckBox("私信视频作者")
        self.radio_button2.setChecked(True)
        self.radio_button3 = QCheckBox("私信评论用户")
        self.radio_button3.setChecked(True)
        self.radio_button4 = QCheckBox("最新发布")
        self.radio_button4.setChecked(True)
        self.radio_button6 = QCheckBox("近一日")
        self.radio_button6.setChecked(True)
        self.radio_button7 = QCheckBox("近七日")
        self.radio_button7.setChecked(False)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button4)
        self.horizontal_layout.addWidget(self.radio_button6)
        self.horizontal_layout.addWidget(self.radio_button7)
        self.horizontal_layout.addWidget(self.radio_button5)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
          # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('                      粉丝数量')

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
        self.label_seconds = QLabel('个之间', self)

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




        self.label_from_time = QLabel('                      私信内容:')

        yunxingshichang = get_value_by_key_pkl("shuju_config.pkl", "jiaobenyunxingshichang")
        if (yunxingshichang != None):
            self.run_time = QLineEdit(yunxingshichang)
        else:
            self.run_time = QLineEdit("0")
        self.run_time.setFixedWidth(180)

        self.label_from_search = QLabel('        每个搜索词刷')

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
        self.label_seconds_search = QLabel('个视频     ', self)
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout_diyihang = QHBoxLayout()
        self.h_layout_diyihang.addWidget(self.label_from_time)
        self.h_layout_diyihang.addWidget(self.run_time)
        self.h_layout_diyihang.addWidget(self.label_from_search)
        self.h_layout_diyihang.addWidget(self.line_edit_from_search)
        self.h_layout_diyihang.addWidget(self.label_to_search)
        self.h_layout_diyihang.addWidget(self.line_edit_to_search)
        self.h_layout_diyihang.addWidget(self.label_seconds_search)
        self.label_from111_kongge = QLabel('')
        self.label_from111_shoucang = QLabel('评论过滤')
        self.label_from111_shoucang.setFixedWidth(50)

        shoucanggailv = get_value_by_key_pkl("shuju_config.pkl", "shoucanggailv")
        if (shoucanggailv != None):
            self.shoucang_gailv = QLineEdit(shoucanggailv)
        else:
            self.shoucang_gailv = QLineEdit("加盟/广告/最强")
        self.shoucang_gailv.setFixedWidth(320)
        self.label_from222_shoucang = QLabel('                                 ')

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
        # self.h_layout_disanhang.addWidget(self.label_from111_pinglun)
        # self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        # self.h_layout_disanhang.addWidget(self.label_from222_pinglun)
        # self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        # self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        # self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
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

        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择搜索文件路径配置:")
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
        # layout.addLayout(self.h_layout_kongge1)
        # layout.addLayout(self.h_layout_dir_comment)
        # layout.addLayout(self.h_layout_kongge2)
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
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "ks业务")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        #self.scroll_area.ensureWidgetVisible(100)
        if(self.radio_button1.isChecked() == True):
            tasks.append("sixin")
        if (self.radio_button2.isChecked() == True):
            tasks.append("gouwu")
        # if (self.radio_button3.isChecked() == True):
        #     tasks.append("pinglun")
        # if (self.radio_button4.isChecked() == True):
        #     tasks.append("delete_zhitong")
        print("tasks------------",tasks)
        if(os.path.isfile(self.file_textbox.text())):
            print("搜索文件加载")
        else:
            print("搜索文件buzai")
            return
        # if (os.path.isfile(self.file_textbox_comment.text())):
        #     print("评论文件加载")
        # else:
        #     print("评论文件不在")
        #     return
        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,self.file_textbox.text(),self.file_textbox_comment.text(),tasks,self.run_time.text(),self.line_edit_from_search.text(),self.line_edit_to_search.text(),self.line_edit_from.text(),self.line_edit_to.text(),self.jiarenshurukuang.text(),self.shoucang_gailv.text(),self.shoucang_pinglun.text(),self.shoucang_dianzan.text(),self.shoucang_guanzhu.text(),self.huadongcishu_big.text(),self.file_textbox_gouwu.text(),self.radio_button2.isChecked(),self.radio_button3.isChecked(),self.radio_button4.isChecked(),self.radio_button6.isChecked(),self.radio_button7.isChecked()))
            #搜索路径、评论文件路径---不用、任务列表、私信内容配置、每个关键字搜索滑动视频数量小、每个关键字搜索滑动视频数量大、粉丝数量小、粉丝数量大、年龄限制小、收藏、评论、点赞、关注，年龄限制大，购物文件配置路径、是否私信视频作者，是否私信视频评论用户
            #threads.append(thread)
            thread.start()

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