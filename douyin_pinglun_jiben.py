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
    QFileDialog, QTextEdit, QTabWidget, QFrame, QSpinBox
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
def operate_device(serial):
    print("1")
    shifouguanbidouyin_v = get_value_by_key_pkl("shuju_config.pkl", "shifouguanbidouyin")
    if(shifouguanbidouyin_v == "1"):
        shifouguanbidouyin = True
    else:
        shifouguanbidouyin = False
    print("shifouguanbidouyin=",shifouguanbidouyin)
    count_zong = 0
    print("2")
    while(True):
        #try:
            import datetime
            import time
            if(int(datetime.datetime.now().timestamp()) > 1842548805):
                return

            result = main_douyin(serial)
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
        # except BaseException as ee:
        #     print("崩溃了",ee)
        #     operate_device(serial)


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
# def main_control(serial):
#     task = get_value_by_key_pkl("shuju_config.pkl", "task")
#     print("task=",task)
#     d = get_device(serial)
#     if(str(task).count("douyinyanghao")):
#
#         print("")
#
#         len_douyins = 1
#         #d.app_start(package_name="com.ss.android.ugc.aweme")
#         #cmd = f'adb -s {serial} shell am start -n "com.ss.android.ugc.aweme/.splash.SplashActivity"'
#         cmd = f'adb -s {serial} shell input keyevent 3'
#
#         shell_neibu(cmd)
#         shell_neibu(cmd)
#         time.sleep(2)
#         douyinicons = d(text='抖音')
#         if (len(douyinicons) >= 1):
#             print("当前有最少两个抖音",len(douyinicons))
#
#             for i in range(len(douyinicons)):
#                 #cmd = f'adb -s {serial} shell am start -n "com.ss.android.ugc.aweme/.splash.SplashActivity"'
#                 cmd = f'adb -s {serial} shell input keyevent 3'
#                 shell_neibu(cmd)
#                 shell_neibu(cmd)
#                 time.sleep(2)
#                 d(text='抖音')[i].click()
#                 backToHome(d)
#                 time.sleep(1)
#                 d.press("back")
#                 time.sleep(1)
#                 main_douyin(serial, d)
#
#         # else:
#         #     backToHome(d)
#         #     if(d(text='首页').exists(timeout=3)):
#         #         d.press("back")
#         #     main_douyin(serial, d)
#         return "88"
#
#     if (str(task).count("xiaohongshuyanghao")):
#
#         print("")
#         d.app_start(package_name="com.xingin.xhs")
#         time.sleep(2)
#
#         if (d(text='发现').exists(timeout=3)):
#             print("当前在首页了。。。。。。。。")
#             main_xiaohongshu(serial, d)
#         else:
#             print("当前bu在首页了。。。。。。。。")
#
#             douyinicons = d(text='小红书')
#             if (len(douyinicons) > 1):
#                 print("当前有最少两个小红书")
#
#             for i in range(len(douyinicons)):
#                 d(text='小红书')[i].click()
#                 main_xiaohongshu(serial, d)
#     return "88"
def main_xiaohongshu(serial,d):
    print("")

def main_douyin(serial):
    d = get_device(serial)
    task = get_value_by_key_pkl("shuju_config.pkl", "task_douyin")
    print("task-----------",task)
    tasks = str(task).split("_")
    print("task=", tasks)
    if (len(tasks) == 0):
        return


    d.watcher.when("以后再说").click()
    d.watcher.when("忽略").click()
    d.watcher.when("残忍放弃").click()
    d.watcher.start()
    d.app_start(package_name="com.ss.android.ugc.aweme")
    backToHome(d)
    d.press("back")
    time.sleep(2)
    print("task-sousuo")
    updata_pkl("./shuju/" + serial + ".pkl", "进行的任务", "搜索任务中")
    # try:
    douyin_sousuo(serial,d)
    return "88"
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

        beisaier(d)
        time.sleep(2)



def sendMessage(serial,d):

    huifucishu_t = random.randint(1,3)
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
            time.sleep(random.randint(3, 5))
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

    fenxianggei_y = 0
    if (d(text='综合').exists(timeout=3)):
        print("综合")
        fenxianggei_y = d(text='综合').info["bounds"]["top"]+5
        time.sleep(random.randint(1, 3))
    else:
        return

    if (fenxianggei_y == 0):
        return
    time.sleep(3)
    for i in range(10):
        if (d(text='话题').exists(timeout=1)):
            d(text='话题').click()
            time.sleep(3)
            break
        else:
            print("当前没有视频tab啊。。。。。。。。")
            #return

        d.swipe(800,fenxianggei_y,100,fenxianggei_y,0.5)
        time.sleep(1)

    # if (check_time_difference(run_time * 60)):
    #     return "88"
    if (d(textContains='次播放').exists(timeout=3)):
        d(textContains='次播放').click()
        print("当前在播放详情页里头")
        time.sleep(3)
    else:
        print("当前没有次  播放 。。。。。。。。")
        return
    if (d(resourceId='com.ss.android.ugc.aweme:id/cover').exists(timeout=10)):
        zonghe_y = d(text='综合').info["bounds"]["top"]+100
        random_click_view(d,d(resourceId='com.ss.android.ugc.aweme:id/cover'))
        print("当前在播放详情页里头")
        time.sleep(3)
    else:
        print("当前没有neirong 。。。。。。。。")
        return

    time.sleep(3)
    if (1 == 1):
        if (d(descriptionContains='点赞').exists(timeout=8)):
            # d(text='添加评论...').click()
            print("当前在播放详情页里头")
            time.sleep(3)
            print("当前在播放详情页里头")
            return "1"
        else:
            print("当前没有添加评论a 。。。。。。。。")
            return


def detail(serial,d,from_t="meng"):
    meicituijianhuadongcishu_xiao = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_xiao"))
    meicituijianhuadongcishu_da = int(get_value_by_key_pkl("shuju_config.pkl", "meicituijianhuadongcishu_da"))
    swipe_count_temp = random.uniform(meicituijianhuadongcishu_xiao, meicituijianhuadongcishu_da)
    print("swipe_count_temp--", swipe_count_temp)
    b_count = 0
    while (b_count < swipe_count_temp):
        # update_pkl_add_one("/shuju/"+serial+".pkl","tongji")
        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        douyinshipinguankanshichang_xiao = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao"))
        douyinshipinguankanshichang_da = int(get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da"))
        wait_time = random.uniform(douyinshipinguankanshichang_xiao, douyinshipinguankanshichang_da)
        print("wait_time=====", wait_time)
        time.sleep(wait_time)
        print("当前在循环里头")
        dianzan = int(get_value_by_key_pkl("shuju_config.pkl", "dianzan_gailv"))
        shoucang = int(get_value_by_key_pkl("shuju_config.pkl", "shoucang_gailv"))
        pinglun = int(get_value_by_key_pkl("shuju_config.pkl", "pinglun_gailv"))
        fenxiang_gailv = int(get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv"))

        dianzanyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "dianzanyuzhi"))
        shoucangyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "shoucangyuzhi"))
        pinglunyuzhi = int(get_value_by_key_pkl("shuju_config.pkl", "pinglunyuzhi"))

        print(shoucang, dianzan, pinglun, fenxiang_gailv)
        print("dianzanyuzhi=",dianzanyuzhi,shoucangyuzhi,pinglunyuzhi)
        pinglun_t = 0
        dianzan_t = 0
        shoucang_t = 0
        fenxiang_t = 0
        #try:

        #获取视频名称
        shipinbiaoti = "默认标题"
        if (d(resourceId='com.ss.android.ugc.aweme:id/desc').exists(timeout=3)):
            print("展开")
            shipinbiaoti = d(resourceId='com.ss.android.ugc.aweme:id/desc').get_text()
            time.sleep(random.randint(1, 3))
        else:
            return
        title_path = "title"
        create_directory_if_not_exists(title_path)
        print("shipinbiaoti=",shipinbiaoti)
        shipinbiaoti = clean_string(shipinbiaoti)
        file_path = title_path + "/" + shipinbiaoti
        if(not os.path.isfile(file_path)):
            create_file_if_not_exists(file_path)
            if (d(descriptionContains='评论评论').exists(timeout=1)):
                pinglun_t = 0
            elif (d(descriptionContains='评论').exists(timeout=3)):
                print("有评论")
                pinglun_t = str(d(descriptionContains='评论').info["contentDescription"])[2:-3]
                if (str(pinglun_t).count("万")):
                    pinglun_t = "10000"
                if (pinglun_t.isdigit()):
                    pinglun_t = int(pinglun_t)
                    print("pinglun_t=", pinglun_t)
            time.sleep(0.5)

            if (d(text='点击进入直播间').exists(timeout=2)):
                beisaier(d)
                time.sleep(2)
                b_count += 1
                continue
            #if (shoucang_t > shoucangyuzhi):
            if (random_boolean_with_probability(shoucang)):
                print("当前可以收藏")
                if (d(descriptionContains='收藏').exists(timeout=3)):
                    print("点击收藏")
                    d(descriptionContains='收藏').click()
                    print("点击收藏")
                time.sleep(1.5)
            #if (dianzan_t > dianzanyuzhi):
            if (random_boolean_with_probability(dianzan)):
                print("当前可以dianzan")
                if (d(descriptionContains='点赞').exists(timeout=3)):
                    print("点击点赞")
                    d(descriptionContains='点赞').click()
                    print("点击收藏")
                time.sleep(1.5)
            #if (dianzan_t > dianzanyuzhi):
            if (pinglun_t > pinglunyuzhi):
                if (random_boolean_with_probability(pinglun)):
                    print("当前可以pinglun")
                    language = 0
                    comment_path = 0
                    result = comment(d, language, serial, comment_path)
                    backTo_dy_detail(d)
                    if (result != "1"):
                        continue
                    time.sleep(1.5)
        else:
            print("当前视频已经处理过了")
        time.sleep(5.5)
        beisaier(d)
        time.sleep(2)
        b_count += 1
        # if (check_time_difference(run_time * 60)):
        #     return "88"
def clean_string(input_str):
    """
    该函数用于清除字符串中的杂质，仅保留汉字、数字和字母
    参数:
        input_str (str): 待处理的输入字符串
    返回:
        str: 仅包含汉字、数字和字母的字符串
    """
    cleaned_chars = []
    for char in input_str:
        # 检查字符是否为字母或数字
        if char.isalnum():
            cleaned_chars.append(char)
        # 检查字符是否为汉字
        elif '\u4e00' <= char <= '\u9fff':
            cleaned_chars.append(char)
    return ''.join(cleaned_chars)

def fenxiang(serial,d):
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

def comment(d,language,serial,comment_path):
    file_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
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

    for i in range(random.randint(1,2)):
        beisaier(d)
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

    # if (d(resourceId="com.ss.android.ugc.aweme:id/content").exists(timeout=3)):
    #     print("有评论")
    #     contents = d(resourceId="com.ss.android.ugc.aweme:id/content")
    #     comment_t = contents[random.randint(0,len(contents)-1)].get_text()
    #     time.sleep(1.5)
    # else:
    #     print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
    #     #return

    comment_t = get_random_line_from_file(file_path_comment)

    if (d(text="善语结善缘，恶言伤人心").exists(timeout=3)):
        print("善语结善缘，恶言伤人心")
        d(text="善语结善缘，恶言伤人心").set_text(str(comment_t)+biaoqing[biaoqing_int] * biaoqing_count)
        time.sleep(1.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return

    result_i = insert_image(serial, d)
    print("result_i=",result_i)
    if(result_i == "1"):
        print("")
    duoxuan_image(serial, d)
    backTo_comment_list(d)


    time.sleep(1)

    if(d(text="发送").exists(timeout=2)):
        #d(text="发送").click()
        print("")
    else:
        d.press("back")
        return

    time.sleep(2)
    d.press("back")
    time.sleep(2)

    return "1"
def duoxuan_image(serial,d):
    if (d(text="多选").exists(timeout=3)):
        print("多选")
        random_click_view(d, d(text="多选"))
        time.sleep(1.5)
    else:
        print("当前没有多选")
        return

    weixuanzhongs = d(descriptionContains=", 未选中")
    if(weixuanzhongs):
        print("ok")
    else:
        return
    weixuanzhongs_l = len(weixuanzhongs)
    if(weixuanzhongs_l>=6):
        weixuanzhongs_l = 6

    for i in range(weixuanzhongs_l):
        print("i=",i)
        random_click_view(d,d(descriptionContains=", 未选中"))
        time.sleep(1)

    if (d(textContains="下一步").exists(timeout=3)):
        print("下一步")
        random_click_view(d, d(textContains="下一步"))
        time.sleep(1.5)
        return "1"
    else:
        print("当前没有下一步")
        return
def insert_image(serial,d):
    tupianwenjianjiapeizhi = get_value_by_key_pkl("shuju_config.pkl", "tupianwenjianjiapeizhi")
    if(tupianwenjianjiapeizhi):
        wenjianjias = str(tupianwenjianjiapeizhi).split("_")
    else:
        return

    wenjianjia = random.choice(wenjianjias)
    # 下面开始添加图片
    if (d(descriptionContains="插入图片").exists(timeout=3)):
        print("当前有图片")
        random_click_view(d, d(descriptionContains="插入图片"))
        time.sleep(2.5)
    else:
        print("当前没有善语结善缘，恶言伤人心a 。。。。。。。。")
        return

    # 下面开始添加图片
    if (d(text="所有照片").exists(timeout=3)):
        print("所有照片")
        random_click_view(d, d(text="所有照片"))
        time.sleep(2.5)
    else:
        print("当前没有所有照片 。。。。。。。。")
        return

    for i in range(10):
        if (d(text=wenjianjia).exists(timeout=1)):
            random_click_view(d,d(text=wenjianjia))
            return "1"
        beisaier_small(d)
        time.sleep(2)



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

                if (d(descriptionContains=desc_t).exists(timeout=10)):
                    print("当前确实在同城了，需要划一下。。。。。。。。")
                    beisaier(d)
                    time.sleep(2)
                    beisaier(d)
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
        time.sleep(2)

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
def backTo_comment_list(d):
    dd =  0
    time.sleep(2)
    while(dd < 10):
        elements = d(descriptionContains='插入图片')  # 获取所有文本为'some_text'的元素
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
    dd =  0
    time.sleep(2)
    while(dd < 10):
        elements = d(descriptionContains='点赞')  # 获取所有文本为'some_text'的元素
        elements11 = d(descriptionContains='评论')
        #print(len(elements))
        if(len(elements)>0):
            if (len(elements11) > 0):
                return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
        dd += 1
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

        beisaier(d)
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

            beisaier(d)
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

        beisaier(d)
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

            beisaier(d)
            time.sleep(random.randint(1, 3))

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
    swipe_along_bezier(d, start_point, end_point, control_points, steps=15, duration=0.8)

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

class PklViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_ids = []
        self.init_ui()



    def init_ui(self):
        self.setWindowTitle("抖音评论")
        self.setGeometry(100, 100, 550, 500)  # 适当增大窗口尺寸

        # ====== 顶部标题和手机列表区域 ======
        self.titleLabel = QLabel("*" * 55 + "手机列表" + "*" * 55)
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
        self.caozuo_tiel = QLabel("*" * 55 + "操     作" + "*" * 55)
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
        self.radio_button1 = QCheckBox("抖音评论")
        self.radio_button1.setChecked(False)
        self.radio_button2 = QCheckBox("小红书养号")
        self.radio_button2.setChecked(False)
        self.radio_button3 = QCheckBox("任务完成之后是否关闭抖音")
        self.radio_button3.setChecked(True)
        self.radio_button5 = QLabel("           ")

        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        #self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button5)

        # ====== Tab布局区域 ======
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)  # 标签在顶部

        # 添加各个Tab页
        self.init_douyin_tab()  # 抖音配置Tab
        # self.init_xhs_tab()  # 小红书配置Tab
        # self.init_advanced_tab()  # 高级设置Tab
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

        # ====== 主布局组装 ======
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self.titleLabel)
        main_layout.addWidget(self.scroll_area)
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
        self.radio_button_dy_task2.setChecked(False)
        self.radio_button_dy_task3 = QCheckBox("搜索")
        self.radio_button_dy_task3.setChecked(False)
        self.radio_button_dy_task4 = QCheckBox("清理")
        self.radio_button_dy_task4.setChecked(False)
        self.radio_button_dy_task5 = QCheckBox("消息回复")
        self.radio_button_dy_task5.setChecked(False)
        self.radio_button_dy_task6 = QCheckBox("随机三条任务")
        self.radio_button_dy_task6.setChecked(False)

        self.radio_button_dy_task1.setFixedWidth(50)
        self.radio_button_dy_task2.setFixedWidth(50)
        self.radio_button_dy_task3.setFixedWidth(50)
        self.radio_button_dy_task4.setFixedWidth(50)
        self.radio_button_dy_task5.setFixedWidth(70)
        self.radio_button_dy_task6.setFixedWidth(250)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task0)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task1)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task2)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task3)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task4)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task5)
        self.horizontal_layout_dy_task.addWidget(self.radio_button_dy_task6)

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
        self.label_file_comment = QLabel("请选择评论文件路径:")

        file_temp_path_comment = get_value_by_key_pkl("shuju_config.pkl", "file_path_comment")
        if (file_temp_path_comment != None):
            self.file_textbox_comment = QLineEdit(file_temp_path_comment)
        else:
            self.file_textbox_comment = QLineEdit("请输入回复文件路径")
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

        self.douyin_guanjianzi_wenben = QLabel('抖音视频观看时长:')
        self.douyin_guanjianzi_wenben.setFixedWidth(110)

        douyinshipinguankanshichang_xiao = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_xiao")
        if (douyinshipinguankanshichang_xiao != None):
            self.douyinshipinguankanshichang_xiao = QLineEdit(douyinshipinguankanshichang_xiao)
        else:
            self.douyinshipinguankanshichang_xiao = QLineEdit("50")
        self.douyinshipinguankanshichang_xiao.setFixedWidth(40)
        self.baifenbi_1 = QLabel("至")

        douyinshipinguankanshichang_da = get_value_by_key_pkl("shuju_config.pkl", "douyinshipinguankanshichang_da")
        if (douyinshipinguankanshichang_da != None):
            self.douyinshipinguankanshichang_da = QLineEdit(douyinshipinguankanshichang_da)
        else:
            self.douyinshipinguankanshichang_da = QLineEdit("50")
        self.douyinshipinguankanshichang_da.setFixedWidth(40)

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

        self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_wenben_huadongcishu)
        self.h_layout_diwuhang.addWidget(self.meicituijianhuadongcishu_xiao)
        self.h_layout_diwuhang.addWidget(self.baifenbi_6)

        self.h_layout_diwuhang.addWidget(self.meicituijianhuadongcishu_da)
        self.h_layout_diwuhang.addWidget(self.baifenbi_7)

        self.h_layout_diwuhang.addStretch(1)

        #同城相关配置
        self.h_layout_tongcheng = QHBoxLayout()
        self.h_layout_tongcheng.setContentsMargins(1, 0, 0, 0)  # 设置布局边距
        self.h_layout_tongcheng.setSpacing(0)  # 设置控件间距

        self.douyin_guanjianzi_wenben_tongcheng = QLabel('图片文件夹配置:')
        self.douyin_guanjianzi_wenben_tongcheng.setFixedWidth(105)

        tupianwenjianjiapeizhi = get_value_by_key_pkl("shuju_config.pkl", "tupianwenjianjiapeizhi")
        if (tupianwenjianjiapeizhi != None):
            self.tupianwenjianjiapeizhi = QLineEdit(tupianwenjianjiapeizhi)
        else:
            self.tupianwenjianjiapeizhi = QLineEdit("多个城市用'_'隔开")
        self.tupianwenjianjiapeizhi.setFixedWidth(350)

        self.h_layout_tongcheng.addWidget(self.douyin_guanjianzi_wenben_tongcheng)
        self.h_layout_tongcheng.addWidget(self.tupianwenjianjiapeizhi)
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

        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi)
        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.dianzanyuzhi)
        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_dianzan_yuzhi_budianzan)


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

        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_shoucang)
        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.shoucangyuzhi)
        # self.h_layout_shoucang_dianzan_yuzhi.addWidget(self.douyin_guanjianzi_wenben_shoucang_yuzhi_budianzan)


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
        self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv)
        self.h_layout_gailv.addWidget(self.dianzan_gailv)
        self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao)

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
        self.h_layout_gailv.addWidget(self.douyin_shoucang_gailv)
        self.h_layout_gailv.addWidget(self.shoucang_gailv)
        self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao1)

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

        self.douyin_fenxiang_gailv = QLabel('分享概率')
        self.douyin_fenxiang_gailv.setFixedWidth(50)

        fenxiang_gailv = get_value_by_key_pkl("shuju_config.pkl", "fenxiang_gailv")
        if (fenxiang_gailv != None):
            self.fenxiang_gailv = QLineEdit(fenxiang_gailv)
        else:
            self.fenxiang_gailv = QLineEdit("50")
        self.fenxiang_gailv.setFixedWidth(50)

        self.douyin_dianzan_gailv_baifenhao3 = QLabel('%')
        self.douyin_dianzan_gailv_baifenhao3.setFixedWidth(50)
        # self.h_layout_gailv.addWidget(self.douyin_fenxiang_gailv)
        # self.h_layout_gailv.addWidget(self.fenxiang_gailv)
        # self.h_layout_gailv.addWidget(self.douyin_dianzan_gailv_baifenhao3)


        #layout.addLayout(self.horizontal_layout_dy_task)
        #layout.addLayout(self.renwushichang_layout)
        layout.addLayout(self.h_layout_dir)
        layout.addLayout(self.h_layout_dir_comment)
        layout.addLayout(self.h_layout_diwuhang)
        layout.addLayout(self.h_layout_tongcheng)
        #layout.addLayout(self.h_layout_xiaoxihuifu)
        #layout.addLayout(self.h_layout_fenxianggei)
        layout.addLayout(self.h_layout_shoucang_dianzan_yuzhi)
        layout.addLayout(self.h_layout_gailv)
        # layout.addLayout(self.h_layout)
        layout.addStretch()  # 底部留白

        # 绑定文件选择事件
        self.file_button.clicked.connect(self.showDialog)
        self.file_button_comment.clicked.connect(self.showDialog_comment)

        self.tab_widget.addTab(douyin_tab, "抖音评论配置")

    def init_xhs_tab(self):
        """小红书配置Tab页"""
        xhs_tab = QWidget()
        layout = QVBoxLayout(xhs_tab)

        # 行为概率设置
        # self.h_layout_disanhang = QHBoxLayout()
        # self.label_from111_shoucang = QLabel('收藏概率')
        # self.shoucang_gailv = QLineEdit("50")
        # self.shoucang_gailv.setFixedWidth(30)
        # self.label_from222_shoucang = QLabel('%')
        # self.label_from111_pinglun = QLabel('评论概率')
        # self.shoucang_pinglun = QLineEdit("50")
        # self.shoucang_pinglun.setFixedWidth(30)
        # self.label_from222_pinglun = QLabel('%')
        # self.label_from111_dianzan = QLabel('点赞概率')
        # self.shoucang_dianzan = QLineEdit("50")
        # self.shoucang_dianzan.setFixedWidth(30)
        # self.label_from222_dianzan = QLabel('%')
        # self.label_from111_guanzhu = QLabel('关注概率')
        # self.shoucang_guanzhu = QLineEdit("50")
        # self.shoucang_guanzhu.setFixedWidth(30)
        # self.label_from222_guanzhu = QLabel('%')
        #
        # self.h_layout_disanhang.addWidget(self.label_from111_shoucang)
        # self.h_layout_disanhang.addWidget(self.shoucang_gailv)
        # self.h_layout_disanhang.addWidget(self.label_from222_shoucang)
        # self.h_layout_disanhang.addWidget(self.label_from111_pinglun)
        # self.h_layout_disanhang.addWidget(self.shoucang_pinglun)
        # self.h_layout_disanhang.addWidget(self.label_from222_pinglun)
        # self.h_layout_disanhang.addWidget(self.label_from111_dianzan)
        # self.h_layout_disanhang.addWidget(self.shoucang_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from222_dianzan)
        # self.h_layout_disanhang.addWidget(self.label_from111_guanzhu)
        # self.h_layout_disanhang.addWidget(self.shoucang_guanzhu)
        # self.h_layout_disanhang.addWidget(self.label_from222_guanzhu)
        #
        # # 滑动概率设置
        # self.h_layout_diwuhang = QHBoxLayout()
        # self.douyin_guanjianzi_wenben = QLabel('图文相册左滑概率:')
        # self.douyinguanjianzi_zuohua = QLineEdit("50")
        # self.douyinguanjianzi_zuohua.setFixedWidth(40)
        # self.baifenbi_1 = QLabel('%')
        # self.douyin_guanjianzi_kongge = QLabel('  ')
        # self.douyin_shanghua_wenben = QLabel('图文上划概率:')
        # self.douyinguanjianzi_shanghua = QLineEdit("50")
        # self.douyinguanjianzi_shanghua.setFixedWidth(40)
        # self.baifenbi_2 = QLabel('%')
        # self.douyin_guanjianzi_kongge111 = QLabel('  ')
        # self.douyin_shanghua_xhs_liulan_wenben = QLabel('滑动浏览概率:')
        # self.douyinguanjianzi_shanghua_xhs_liulan = QLineEdit("50")
        # self.douyinguanjianzi_shanghua_xhs_liulan.setFixedWidth(30)
        # self.baifenbi_3 = QLabel('%')
        #
        # self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_wenben)
        # self.h_layout_diwuhang.addWidget(self.douyinguanjianzi_zuohua)
        # self.h_layout_diwuhang.addWidget(self.baifenbi_1)
        # self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_kongge)
        # self.h_layout_diwuhang.addWidget(self.douyin_shanghua_wenben)
        # self.h_layout_diwuhang.addWidget(self.douyinguanjianzi_shanghua)
        # self.h_layout_diwuhang.addWidget(self.baifenbi_2)
        # self.h_layout_diwuhang.addWidget(self.douyin_guanjianzi_kongge111)
        # self.h_layout_diwuhang.addWidget(self.douyin_shanghua_xhs_liulan_wenben)
        # self.h_layout_diwuhang.addWidget(self.douyinguanjianzi_shanghua_xhs_liulan)
        # self.h_layout_diwuhang.addWidget(self.baifenbi_3)
        #
        # # 购物文件选择
        # self.h_layout_dir_gouwu = QHBoxLayout()
        # self.label_file_gouwu = QLabel("请选择购物文件路径:")
        # self.file_textbox_gouwu = QLineEdit("请输入购物文件路径")
        # self.file_button_gouwu = QPushButton("选择文件", self)
        # self.temp_gouwu = QLabel("                          ")
        # self.h_layout_dir_gouwu.addWidget(self.label_file_gouwu)
        # self.h_layout_dir_gouwu.addWidget(self.file_textbox_gouwu)
        # self.h_layout_dir_gouwu.addWidget(self.file_button_gouwu)
        # self.h_layout_dir_gouwu.addWidget(self.temp_gouwu)
        # self.file_button_gouwu.clicked.connect(self.showDialog_gouwu)
        #
        # # 添加到布局
        # layout.addWidget(create_row_container(self.h_layout_dir, "搜索文件配置"))
        # layout.addWidget(create_row_container(self.h_layout_dir_comment, "评论文件配置"))
        # layout.addWidget(create_row_container(self.h_layout_diwuhang, "操作概率设置"))
        #
        # layout.addStretch()  # 底部留白

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
                task_config = "task_config"
                create_directory_if_not_exists(task_config)
                clean_folder(task_config)
                process_file(task_config)

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


    def save_config(self):
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
        updata_pkl_config_mianban("tupianwenjianjiapeizhi", self.tupianwenjianjiapeizhi.text())
        updata_pkl_config_mianban("dianzanyuzhi", self.dianzanyuzhi.text())
        updata_pkl_config_mianban("shoucangyuzhi", self.shoucangyuzhi.text())
        updata_pkl_config_mianban("dianzan_gailv", self.dianzan_gailv.text())
        updata_pkl_config_mianban("shoucang_gailv", self.shoucang_gailv.text())
        updata_pkl_config_mianban("pinglun_gailv", self.pinglun_gailv.text())
        updata_pkl_config_mianban("fenxiang_gailv", self.fenxiang_gailv.text())
        updata_pkl_config_mianban("pinglunyuzhi", self.pinglunyuzhi.text())
        updata_pkl_config_mianban("fenxiangyonghunicheng", self.fenxiangyonghunicheng.text())
        updata_pkl_config_mianban("huifuxiaoxiyonghunicheng", self.huifuxiaoxiyonghunicheng.text())


    def execute_button_clicked(self):
        #print("---------------")
        self.save_config()


        if(self.selected_ids == []):
            toast("请选择机型")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "dy业务")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        print("tasks------------",tasks)
        if(os.path.isfile(self.file_textbox.text())):
            print("搜索文件加载")
        else:
            print("搜索文件buzai")
            return
        if (os.path.isfile(self.file_textbox_comment.text())):
            print("评论文件加载")
        else:
            print("评论文件不在")
            return
        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,))
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


def clean_folder(folder_path):
    """
    清空指定文件夹中的所有内容（保留文件夹本身）

    参数:
        folder_path (str): 要清空的文件夹路径
    """
    # 确保路径存在且是一个目录
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return
    if not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}' 不是一个有效的文件夹")
        return

    try:
        # 遍历文件夹中的所有内容
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            # 如果是文件，直接删除
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"已删除文件: {item_path}")

            # 如果是文件夹，递归删除
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"已删除文件夹: {item_path}")

        print(f"文件夹 '{folder_path}' 已清空")

    except Exception as e:
        print(f"清空文件夹时发生错误: {e}")
import chardet


def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read(1024)  # 读取部分内容用于检测
        result = chardet.detect(raw_data)
        return result['encoding']


def process_file(input_file_path, encoding=None):
    """
    读取txt文件并按行创建对应文件
    参数:
        input_file_path (str): 输入txt文件的路径
        encoding (str, optional): 文件编码，若为None则自动检测
    """
    try:
        # 自动检测文件编码（如果未指定）
        if encoding is None:
            detected_encoding = detect_encoding(input_file_path)
            print(f"检测到的文件编码: {detected_encoding}")
            encoding = detected_encoding or 'utf-8'  # 默认使用utf-8

        # 读取txt文件内容
        with open(input_file_path, 'r', encoding=encoding) as file:
            lines = file.read().splitlines()
            print("lines=",lines)


        # 打印读取的内容数组
        print(f"从文件中读取的内容数组: {lines}")

        # 按行创建文件
        for line in lines:
            # 移除行内容中的非法文件名字符
            safe_filename = line.strip()
            # 替换或移除Windows系统中的非法文件名字符
            safe_filename = safe_filename.replace('/', '_').replace('\\', '_')
            safe_filename = safe_filename.replace(':', '_').replace('*', '_')
            safe_filename = safe_filename.replace('?', '_').replace('"', '_')
            safe_filename = safe_filename.replace('<', '_').replace('>', '_')
            safe_filename = safe_filename.replace('|', '_')

            if safe_filename:  # 确保文件名不为空
                try:
                    safe_filename = "task_config" +"/"+safe_filename

                    # 创建并写入新文件
                    with open(f"{safe_filename}", 'w', encoding='utf-8') as new_file:
                        new_file.write(f"文件名来自: {line}\n")
                    print(f"成功创建文件: {safe_filename}.txt")
                except Exception as e:
                    print(f"创建文件 {safe_filename}.txt 失败: {e}")
            else:
                print("跳过空行，不创建文件")

    except FileNotFoundError:
        print(f"错误: 文件未找到 - {input_file_path}")
    except UnicodeDecodeError:
        print(f"错误: 使用 {encoding} 编码读取文件失败。请尝试指定其他编码。")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
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
