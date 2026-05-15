import cv2
import shutil
import sys
import threading
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

alldata = ""
file_lock = threading.Lock()

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
def get_count_account(d,ocr_processor):
    elements = d(text="我的",resourceId='com.alipay.android.phone.wealth.home:id/tab_description')  # 获取所有文本为'some_text'的元素
    # print(len(elements))
    # for element in elements:
    #     # 对每个元素进行操作，例如获取属性信息
    #     info = element.info
    #     print(info)
    # print(subscribe)
    # if subscribe.exists(timeout=3):
    #     print("开始点击我的")
    #     subscribe.click()
    # print(subscribe.info)
    #print(elements[len(elements) - 1].bounds())
    elements.click()
    time.sleep(3)
    # d(resourceId="com.alipay.android.phone.wealth.home:id/arrow").click()
    elements2 = d(text="设置", className='android.widget.TextView')
    # for element in elements2:
    #     # 对每个元素进行操作，例如获取属性信息
    #     info = element.info
    #     print(info)
    elements2.click()
    time.sleep(3)

    # path = photo()
    # screenshot_image = d.screenshot()
    # screenshot_image.save(path)
    #
    # global alldata
    # if (alldata == ""):
    #     alldata = ocr_processor.getAllData_test(path)
    #     print(alldata)
    #
    # if (alldata == ""):
    #     print("")
    #     return
    # else:
    #     fanhuishouye = ocr_processor.getPoint_by_data(alldata, "登录其他账号")
    #     print(fanhuishouye)
    #     d.click(fanhuishouye[0], fanhuishouye[1])
    #     time.sleep(3)
    elements3 = d(resourceId="com.alipay.mobile.antui:id/list_left_stub")
    #print("elements3=", len(elements3))
    if(len(elements3)>2):
        elements3[len(elements3)-2].click()
        time.sleep(2)

    elements3 = d(resourceId="com.alipay.mobile.antui:id/item_left_text")
    #print("elements3=", len(elements3))
    for element in elements3:
        #print(element)
        print()
    # 打印所有元素的属性
    return len(elements3)-1


from pathlib import Path

from pathlib import Path


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

import random
def random_click_view(d,view):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left)+random.randint(2,15)
    random_y = int(bottom) + random.randint(2,15)
    print("开始点击")
    print(random_x,random_y)

    d.click(random_x,random_y)

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

def add_account_while(d,serial,real_file_path,task,dir_path_shang,big,small,jiarenshuliang):
    failed_count = 0
    count_temp = 0
    while(count_temp<int(jiarenshuliang)):
        phone_temp = get_top_line_and_del(real_file_path)
        if(phone_temp == None):
            pkl_add_log("log.pkl", str(serial), "配置文件空了。。。。返回了")
            return "配置文件空了"
        backToHome(d)
        result_addfriend = addFriend(d, phone_temp,task,serial)
        if(result_addfriend == "88"):
            return "88"
        print("result_addfriend---------",result_addfriend)
        if(result_addfriend == None):
            failed_count += 1
        else:
            failed_count = 0

            if(len(result_addfriend)>2):
                shenqing_done_path = dir_path_shang + "/申请添加成功的联系人"
                create_directory_if_not_exists(shenqing_done_path)

                pkl_file_path = "config.pkl"

                shenqing_done_path = shenqing_done_path + "/"+str(get_value_by_key_pkl(pkl_file_path,str(serial)))+"_"+str(serial)+".txt"
                create_file_if_not_exists(shenqing_done_path)
                #result_temp = compare_with_file(result_addfriend[1],shenqing_done_path)
                result_temp = 1
                if(result_temp == 2):
                    with open(shenqing_done_path, 'a', encoding='utf-8') as file:
                        file.write(result_addfriend[1]+"aaaaa" + "+" + phone_temp + "\n")
                else:
                    with open(shenqing_done_path, 'a', encoding='utf-8') as file:
                        file.write(result_addfriend[2]+"|"+result_addfriend[1]+"|"+phone_temp+"\n")
        if(failed_count>=3):
            pkl_add_log("log.pkl", str(serial), "失败次数过多，切号")
            return "失败次数过多，切号"
        #这里需要等待
        import random
        print("-----------------")
        print(big)
        print(small)
        random_value = random.randint(int(big), int(small))
        pkl_add_log("log.pkl", str(serial), "开始等待，等待时间为：" + str(random_value))
        time.sleep(random_value)
        backToHome(d)
        update_pkl_add_one("./shuju/" + str(serial) + ".pkl", "tongji")
        count_temp+=1
    return
# 示例用法
def add_big(d,serial,dir_path,ocr_processor,task,big,small,jiarenshuliang):
    print("开始打开")
    # d.app_stop("com.eg.android.AlipayGphone")
    d.app_start(package_name="com.eg.android.AlipayGphone")
    time.sleep(3)
    real_file_path = ""
    dir_path_shang = dir_path
    dir_path = dir_path + "/需要添加的联系人"
    if (not os.path.isdir(dir_path)):
        pkl_add_log("log.pkl", serial, "路径不对:" + dir_path)
        return
    file_path_phone = get_files_in_directory(dir_path)
    print("---", file_path_phone)
    for file_name in file_path_phone:
        #print(file_name)
        if (str("phone") in str(file_name)):
            print("真命天子找到了")
            pkl_add_log("log.pkl", str(serial), "找到路径："+str(file_name))
            real_file_path = file_name
    if (real_file_path == ""):
        pkl_add_log("log.pkl", str(serial), str("没找到配置文件"))
        return

    result_back = backToHome(d)
    if (result_back != "1"):
        return "0"
    result_add_while = add_account_while(d, serial, real_file_path,task,dir_path_shang,big,small,jiarenshuliang)
    if(result_add_while == "88"):
        return "88"
    print("result_add_while===", result_add_while)


def find_string_in_file(file_path, search_string,phone_num):
    search_string = str(search_string).strip()
    phone_num = str(phone_num).strip()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if(str(line).count("@")>0):
                    line = str(line).strip()
                    #print("当前统计的邮箱")
                    temp1 = str(line).split("|")
                    #print("temp1=",temp1)
                    #print("temp1[0][0:3]=",temp1[0][0:3])
                    #print("phone_num[0:3]=", phone_num[0:3])
                    #print("str(temp1[2]=", str(temp1[2]))
                    #print("search_string=", search_string)
                    if((temp1[0][0:3] == phone_num[0:3]) and (str(temp1[1]).count(search_string)>0)):
                        return line.strip()
                else:
                    #print("当前统计的不是邮箱")
                    line = str(line).strip()
                    temp1 = str(line).split("|")

                    #print("temp1=", temp1)
                    #print("temp1[0][0:3]=", temp1[0][0:3])
                    #print("phone_num[0:3]=", phone_num[0:3])
                    #print("str(temp1[2]=", str(temp1[2]))
                    #print("search_string=", search_string)
                    #print("temp1[2][-2:]=",temp1[2][-2:])
                    #print("phone_num[-2:]=",phone_num[-2:])

                    if(temp1[0] == "***"):
                        if(str(phone_num).count("@") < 1 ):
                            #print("当前用户显示的是手机号，比对名字和前三后二")
                            if((temp1[2][-2:] == phone_num[-2:]) and (str(temp1[1]).count(search_string) > 0)):
                                return line.strip()
                        else:
                            #print("当前用户显示的是youxiang，zhi比对名字")
                            if(str(temp1[1]).count(search_string) > 0):
                                return line.strip()
                    #print("temp1[0][-2:]=",temp1[0][-2:])
                    #print("phone_num[-2:]=",phone_num[-2:])
                    if ((temp1[0][0:3] == phone_num[0:3]) and(temp1[0][-2:] == phone_num[-2:]) and (str(temp1[1]).count(search_string) > 0)):
                        return line.strip()


                # temps = line.split("+")
                # if(len(temps)>1):
                #     if((search_string == temps[0]) or (search_string+"aaaaa" == temps[0])):
                #         if ( (temps[1][0:3] == str(phone_num)[0:3])):
                #             #if (search_string == temps[0]):
                #             return line.strip()  # 使用strip()去掉行尾的换行符
        return None  # 如果没有找到，则返回None
    except FileNotFoundError:
        #print(f"The file {file_path} was not found.")
        return None

    # 示例用法


def delete(d, serial, dir_path, param, task, big, small, jiarenshuliang):
    print("开始删除好友")
    pkl_add_log("log.pkl", str(serial), "开始删除好友功能")
    list_mon = []
    flag = 0
    # elements = d(resourceId='android.widget.LinearLayout')  # 获取所有文本为'some_text'的元素
    # print(len(elements))
    # for ee in elements:
    #     print(ee.info)

    d.app_start(package_name="com.eg.android.AlipayGphone")
    backToHome(d)

    elements = d(text="朋友", resourceId='com.alipay.mobile.socialwidget:id/social_tab_text')  # 获取所有文本为'some_text'的元素
    #print(len(elements))
    if (len(elements) > 0):
        elements.click()
        time.sleep(2)
    zong_while = 0
    count_while_temp = 0

    while(zong_while<2):
        while (True):
            if (flag == 1):
                break
            red_point_list = []
            if (d(resourceId='com.alipay.mobile.socialwidget:id/red_dot_alert').exists(timeout=3)):
                elements = d(resourceId='com.alipay.mobile.socialwidget:id/red_dot_alert')  # 获取所有文本为'some_text'的元素
                print("红点个数为：", len(elements))
                for ee in elements:
                    print(ee.info["bounds"]["bottom"])
                    red_point_list.append(ee.info["bounds"]["bottom"])
            print(red_point_list)
            if (d(resourceId='com.alipay.mobile.socialwidget:id/item_memo').exists(timeout=3)):
                elements = d(resourceId='com.alipay.mobile.socialwidget:id/item_memo')  # 获取所有文本为'some_text'的元素
                print("日期个数为：", len(elements))
                for ee1 in elements:
                    print(ee1.info["bounds"]["top"])
                    result = is_close_to_any(int(ee1.info["bounds"]["top"]), red_point_list)
                    if (result):
                        print("当前这个有红点")
                        print(ee1.info)
                    else:
                        print("----name--->", ee1.get_text())
                        if (ee1.get_text() not in list_mon):
                            title_temp = ee1.get_text()
                            print("没有红点，可以删除")
                            # ee1.click()
                            list_mon.append(title_temp)
                time.sleep(3)
                first_mom = d(resourceId='com.alipay.mobile.socialwidget:id/item_memo')
                if(first_mom):
                    first_mom = d(resourceId='com.alipay.mobile.socialwidget:id/item_memo')[0].get_text()
                    d.swipe_points([(500, 1000), (600, 808)], 0.2)
                    d.swipe_points([(500, 1000), (600, 808)], 0.2)
                    d.swipe_points([(500, 1000), (600, 808)], 0.2)
                    d.swipe_points([(500, 1000), (600, 808)], 0.2)
                    time.sleep(1.5)
                    end_mom = d(resourceId='com.alipay.mobile.socialwidget:id/item_memo')[0].get_text()
                    print(list_mon)
                    if (end_mom == first_mom):
                        flag = 1
                else:
                    flag = 1

        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)
        d.swipe_points([(500, 400), (600, 1400)], 0.2)

        print(len(list_mon))
        for mon in list_mon:
            if (d(text=mon).exists(3)):
                print("找到了", mon)
                d(text=mon).click()
                time.sleep(3)
                ee = d(resourceId="com.alipay.mobile.chatapp:id/chat_msg_edit")
                if (len(ee) > 0):
                    print("当前是朋友")
                    print(ee.info)
                    delete_frind_entry(d, serial, ee)
                    backToHome(d)
                    time.sleep(1.5)
                else:
                    print("但是当前不是朋友")
                    backToHome(d)
                    time.sleep(1.5)
                d.swipe_points([(500, 1000), (600, 808)], 0.2)
                time.sleep(2)
            else:
                d.swipe_points([(500, 1000), (600, 808)], 0.2)
                d.swipe_points([(500, 1000), (600, 808)], 0.2)
        zong_while += 1



def is_close_to_any(num, B, tolerance=50):
    for b in B:
        if 0 < num - b <= tolerance:
            return True
    return False


def delete_frind_entry(d, serial,ee):
    print("")
    #ee.click()
    time.sleep(3)

    elements = d(text="\ue620",className='android.widget.TextView')
    if(len(elements)>0):
        elements.click()
        time.sleep(3)

    elements = d(resourceId='com.alipay.mobile.chatapp:id/user_icon')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    elements = d(text = "\ue620",className='android.widget.TextView')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)
        d.drag(500, 1200, 500, 500)
        time.sleep(2)
        d.drag(500, 1200, 500, 500)
        time.sleep(2)

    elements = d(resourceId='com.alipay.android.phone.wallet.profileapp:id/set_delete')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    elements = d(resourceId='com.alipay.mobile.antui:id/ensure')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    backToHome(d)
    time.sleep(3)

def operate_device(serial, dir_path, task,big,small,jiarenshuliang):
    #ocr_processor = OCRProcessor()

    ocr_processor = ""
    d = get_device(serial)
    print("之后的的", d)
    d.app_start(package_name="com.eg.android.AlipayGphone")
    time.sleep(5)

    # d.drag(500, 1200, 500, 500)
    # time.sleep(1)


    print("----------------------")
    #pkl_add_log("log.pkl",serial,"meng")
    d.watcher.when("稍后再说").click()
    d.watcher.start()
    #print("task-------------",task)
    backToHome(d)
    pkl_add_log("log.pkl", str(serial), "去获取一下当前的账号数量")
    #result_getcount = get_count_account(d, ocr_processor)
    result_getcount = 1 #现在不需要动态获取 账号的个数了。
    print("result_getcount=", result_getcount)
    #pkl_add_log("log.pkl", str(serial), "账号数量为:"+str(result_getcount))
    result_back = backToHome(d)
    if (result_back != "1"):
        pkl_add_log("log.pkl", str(serial), "返回主页失败")
        return "0"
    # count_switch_account = 0
    # while (count_switch_account < result_getcount):
    pkl_add_log("log.pkl", str(serial), "去加好友了")
    updata_pkl("./shuju/" + str(serial) + ".pkl", "进行的任务", "加好友中")
    if ("add" in task):
        updata_pkl("./shuju/" + str(serial) + ".pkl", "进行的任务", "加好友中")
        pkl_add_log("log.pkl", serial, "开始添加好友")
        add_big(d, serial, dir_path, "", task,big,small,jiarenshuliang)
    if ("delete" in task):
        updata_pkl("./shuju/" + str(serial) + ".pkl", "进行的任务", "删除好友")
        pkl_add_log("log.pkl", serial, "开始删除好友")
        delete(d, serial, dir_path, "", task,big,small,jiarenshuliang)

    if ("tongji" in task):
        updata_pkl("./shuju/" + str(serial) + ".pkl", "进行的任务", "好有统计")
        tongji(d, serial, dir_path)
    updata_pkl("./shuju/" + str(serial) + ".pkl", "进行的任务", "任务结束")
    updata_pkl("./shuju/" + str(serial) + ".pkl", "执行状态", "任务结束")
    "执行状态"
    return



        # count_switch_account += 1
        # backToHome(d)
        # pkl_add_log("log.pkl", str(serial), "切换账号" )
        #
        # result_switch = switch_account(d, ocr_processor, count_switch_account)
        # if (result_switch == "1"):
        #     print("成功切换")
        #     time.sleep(5)


    # print(get_value_by_key_pkl("./shuju/"+serial+".pkl","执行状态"))
    # if(str(get_value_by_key_pkl("./shuju/"+serial+".pkl","执行状态")) != "运行中"):
    #     print("结束了。。。")
    #     d.watcher.remove()
    #     d.stop_uiautomator(True)
    #
    #     return



    # while(True):

    # if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
    #     print("结束了。。。")
    #     d.watcher.remove()
    #     d.stop_uiautomator(True)
    #     break
    #
    #
    #
    # if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
    #     print("结束了。。。")
    #     d.watcher.remove()
    #     d.stop_uiautomator(False)
    #     break

        # 开始后台监控
        # 打开微信应用
        # wechat = d(text="设置")
        #
        # if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
        #     print("结束了。。。")
        #     d.watcher.remove()
        #     d.stop_uiautomator(True)
        #     break
        #
        #     # wechat = d(path="设置")
        # if wechat.exists(timeout=0):  # 使用exists来检查元素是否存在，无需再次wait
        #     wechat.click()
        # time.sleep(2)
        # if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
        #     print("结束了。。。")
        #     d.watcher.remove()
        #     d.stop_uiautomator(True)
        #     break
        #     # 等待微信主界面加载（这里使用简单的sleep）
        # # 点击“订阅号”（假设它在微信的主界面上）
        # subscribe = d(text="显示")
        # if subscribe.exists(timeout=3):
        #     subscribe.click()
        # time.sleep(3)
        # if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
        #     print("结束了。。。")
        #     d.watcher.remove()
        #     d.stop_uiautomator(True)
        #     break
        # d.press("back")
        # time.sleep(3)
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
def tongji(d,serial,dir_path):
    flag = 0
    tongjied = []
    pkl_add_log("log.pkl", str(serial), "开始统计功能")

    d.app_start(package_name="com.eg.android.AlipayGphone")
    backToHome(d)

    elements = d(text="消息", resourceId='com.alipay.mobile.socialwidget:id/social_tab_text')  # 获取所有文本为'some_text'的元素
    print(len(elements))
    if (len(elements) > 0):
        random_click_view(d, elements.info)
        time.sleep(2)
    else:
        print("没有消息tab")
        return

    elements = d( resourceId='com.alipay.mobile.socialwidget:id/contact_button')  # 点击通讯录
    print(len(elements))
    if (len(elements) > 0):
        random_click_view(d, elements.info)
        time.sleep(5)
    else:
        print("没有通讯录")
        return

    while(True):
        elements = d(resourceId='com.alipay.mobile.socialcontactsdk:id/list_item_title')  # 这是朋友列表的名称
        for element in elements:
            print("element=",element)
            print("element.get_text()=", element.get_text())
            acc_name = element.get_text()
            if("146454646546789" not in tongjied):
                random_click_view(d, element.info)
                #tongjied.append(acc_name)
                print("111222")
                time.sleep(1)
                tongji_temp(d,serial,dir_path)
                backToTongxunlu(d)
                time.sleep(1)
        if(d(resourceId='com.alipay.mobile.socialcontactsdk:id/tv_total_count').exists(timeout=1)):
            print("走到头了，退出")
            return

        d.swipe_ext(Direction.FORWARD)
        time.sleep(1)

def backToTongxunlu(d):
    dd =  0
    while(dd < 10):
        elements = d(text='通讯录')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)
tongjied = []
def tongji_temp(d,serial,dir_path):
    global tongjied
    if (d(resourceId='com.alipay.android.phone.wallet.profileapp:id/tv_name').exists(timeout=3)):
        print("22222222")
        title_text = d(resourceId='com.alipay.android.phone.wallet.profileapp:id/tv_name').get_text()
        print("title_text=",title_text)
        if (title_text == None):
            return
        print("333333")
        ee = d(resourceId="com.alipay.android.phone.wallet.profileapp:id/tv_right")
        if (ee):
            print("44444")
            phone_num = str(ee.get_text())
            time.sleep(1)
            print("phone_num=",phone_num)
            if (phone_num == None):
                return
            if(phone_num not in tongjied):
                tongjied.append(phone_num)
                dir_path_tongji = dir_path + "/" + "添加成功的联系人"
                create_directory_if_not_exists(dir_path_tongji)
                pkl_file_path = "config.pkl"
                file_path_tongji = dir_path_tongji + "/" + get_value_by_key_pkl(pkl_file_path,
                                                                                str(serial)) + "_" + serial + ".txt"
                create_file_if_not_exists(file_path_tongji)

                file_path_done = dir_path + "/" + "申请添加成功的联系人" + "/" + get_value_by_key_pkl(
                    pkl_file_path, str(serial)) + "_" + serial + ".txt"
                if (not os.path.isfile(file_path_done)):
                    print("当前页面的配置文件还没有呢")
                    return
                if (len(title_text) > 0):
                    success_string = find_string_in_file(file_path_done, title_text, phone_num)
                    if (success_string != None):

                        elements = d(resourceId='com.alipay.mobile.antui:id/right_container_2')
                        if (elements):
                            random_click_view(d, elements.info)
                            time.sleep(1)
                            result_judge = jundge(d, serial)
                            if (result_judge):

                                with open(file_path_tongji, 'a', encoding='utf-8') as file:
                                    file.write(str(success_string).strip() + "\n")
                            # d.press("back")
                            # time.sleep(1)
                # else:
                #     if (phone_num != ""):
                #         print(phone_num)
                #         result_temp_t = find_matching_lines(file_path_done, phone_num)
                #         if (result_temp_t != None):
                #             with open(file_path_tongji, 'a', encoding='utf-8') as file:
                #                 file.write(str(result_temp_t).strip() + "\n")






def find_matching_lines(file_path, target_string):
    # 提取目标字符串的前三个字符和后两个字符
    prefix = target_string[:3]
    suffix = target_string[-2:]

    # 存储匹配行的列表
    matching_lines = []

    # 打开文件并逐行读取
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去除行尾的换行符
            stripped_line = line.strip()
            # 检查行是否同时包含前缀和后缀
            if ((prefix in stripped_line) and (suffix in stripped_line)):
                matching_lines.append(stripped_line)
                return stripped_line

def switch_account(d,ocr_processor,count_swich):
    elements = d(text="我的",
                 resourceId='com.alipay.android.phone.wealth.home:id/tab_description')  # 获取所有文本为'some_text'的元素
    # print(len(elements))
    # for element in elements:
    #     # 对每个元素进行操作，例如获取属性信息
    #     info = element.info
    #     print(info)
    # print(subscribe)
    # if subscribe.exists(timeout=3):
    #     print("开始点击我的")
    #     subscribe.click()
    # print(subscribe.info)
    # print(elements[len(elements) - 1].bounds())
    elements.click()
    time.sleep(3)
    # d(resourceId="com.alipay.android.phone.wealth.home:id/arrow").click()
    elements2 = d(text="设置", className='android.widget.TextView')
    # for element in elements2:
    #     # 对每个元素进行操作，例如获取属性信息
    #     info = element.info
    #     print(info)
    elements2.click()
    time.sleep(3)

    # path = photo()
    # screenshot_image = d.screenshot()
    # screenshot_image.save(path)
    #
    # global alldata
    # if (alldata == ""):
    #     alldata = ocr_processor.getAllData_test(path)
    #     print(alldata)
    #
    # if (alldata == ""):
    #     print("")
    #     return
    # else:
    #     fanhuishouye = ocr_processor.getPoint_by_data(alldata, "登录其他账号")
    #     print(fanhuishouye)
    #     d.click(fanhuishouye[0], fanhuishouye[1])
    #     time.sleep(3)
    elements3 = d(resourceId="com.alipay.mobile.antui:id/list_left_stub")
    #print("elements3=", len(elements3))
    if (len(elements3) > 2):
        elements3[len(elements3) - 2].click()
        time.sleep(2)

    elements3 = d(resourceId="com.alipay.mobile.antui:id/item_left_text")
    #print("elements3=", len(elements3))
    for element in elements3:
        print(element)
    # 打印所有元素的属性
    # 打印所有元素的属性

    if(elements3.get_text() == "换个新账号登录"):
        print()
    else:
        elements3[count_swich].click()

    return "1"
def backToHome(d):
    dd =  0
    d.app_start(package_name="com.alipay.mobile.socialwidget")
    time.sleep(3)
    while(dd < 10):
        elements = d(resourceId='com.alipay.android.tablauncher:id/tab_icon')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        print("返回----")
        d.press("back")
        time.sleep(1.5)
def addFriend(d,no,task,serial):
    account_name = ""
    print("有消息111")
    #elements = d(text="消息")  # 获取所有文本为'some_text'的元素
    #print(len(elements))
    if(d(text="消息").exists(timeout=15)):
        print("有消息")
        print(d(text="消息").info)
        random_click_view(d,d(text="消息").info)
        time.sleep(2)

    if (d(description="更多操作", resourceId='com.alipay.mobile.socialwidget:id/title_more_menu_button').exists(timeout=3)):
        elements = d(description="更多操作", resourceId='com.alipay.mobile.socialwidget:id/title_more_menu_button')  # 获取所有文本为'some_text'的元素
        random_click_view(d,elements.info)
        time.sleep(2)
    else:
        return

    if (d(text="添加朋友", resourceId="com.alipay.mobile.antui:id/item_name").exists(timeout=3)):
        elements = d(text="添加朋友", resourceId="com.alipay.mobile.antui:id/item_name")  # 获取所有文本为'some_text'的元素
        random_click_view(d,elements.info)
        time.sleep(2)
    else:
        return

    if (d(resourceId="com.alipay.mobile.antui:id/search_input_box").exists(timeout=3)):
        elements = d(resourceId="com.alipay.mobile.antui:id/search_input_box")  # 获取所有文本为'some_text'的元素
        random_click_view(d,elements.info)
        time.sleep(5)
    else:
        return

    #d.send_keys(str(no).strip())
    if (d(resourceId="com.alipay.mobile.ui:id/social_search_normal_input").exists(timeout=3)):
        elements = d(resourceId="com.alipay.mobile.ui:id/social_search_normal_input")  # 获取所有文本为'some_text'的元素
        elements.set_text(str(no).strip())
        time.sleep(2)
    else:
        print("当前没有找到输入框啊")
        return


    time.sleep(3)
    #d.press('enter')
    if (d(textContains="搜索",resourceId="com.alipay.mobile.contactsapp:id/leftText").exists(timeout=3)):
        #elements = d(textContains="搜索",resourceId="com.alipay.mobile.contactsapp:id/leftText")  # 获取所有文本为'some_text'的元素
        random_click_view(d,d(textContains="搜索",resourceId="com.alipay.mobile.contactsapp:id/leftText").info)
        time.sleep(2)
    else:
        return
    time.sleep(3)

    if(d(text="你搜索的账号不存在，请更换手机号或邮箱后重新搜索").exists(timeout=3)):#如果账号不存在，则弹窗 点击确定按钮
        #d(resourceId="com.alipay.mobile.antui:id/ensure").click()
        random_click_view(d, d(resourceId="com.alipay.mobile.antui:id/ensure").info)
        time.sleep(3)
        return



    if (d(resourceId="com.alipay.mobile.contactsapp:id/user_name").exists(timeout=1)):
        #d(resourceId="com.alipay.mobile.contactsapp:id/user_name").click()  # 当前 如果有弹窗，多个联系人的话 则点第一个
        random_click_view(d, d(resourceId="com.alipay.mobile.contactsapp:id/user_name").info)
        time.sleep(3)

    #获取昵称的名称
    nick_name = ""
    if (d(resourceId="com.alipay.android.phone.wallet.profileapp:id/display_name").exists(timeout=3)):
        nick_name_temp = d(resourceId="com.alipay.android.phone.wallet.profileapp:id/display_name").get_text()
        #if(str(nick_name_temp).startswith("支付宝账户:")):
            #nick_name = str(nick_name_temp[6:]).strip()
        nick_name = nick_name_temp
        time.sleep(3)
    print("nick_name=",nick_name)

    account_name = ""
    if (d(resourceId="com.alipay.android.phone.wallet.profileapp:id/alipay_account").exists(timeout=3)):
        account_name_temp = d(resourceId="com.alipay.android.phone.wallet.profileapp:id/alipay_account").get_text()  # 获取当前支付宝账号的名字
        print("account_name------------------",account_name_temp)
        if(account_name_temp):
            account_name = account_name_temp[6:]
    else:
        #下面是通过点击备注里面的名字来获取
        ee = d(className="android.widget.TextView")
        if (len(ee)>3):
            ee[len(ee)-1].click()
            time.sleep(2)
            ee = d(text="备注他的信息")
            if (ee):
                ee.click()
                time.sleep(2)
                ee = d(resourceId="com.alipay.mobile.ui:id/content")
                if (ee):
                    account_name = ee.get_text()
                d.press("back")
                time.sleep(1)
            d.press("back")
            time.sleep(2)

    if (d(text="加好友").exists(timeout=3)):
        elements = d(text="加好友")  # 获取所有文本为'some_text'的元素
        random_click_view(d,elements.info)
        time.sleep(5)
    elif(d(text="发消息").exists(timeout=1)):#当前已经加过好友了
        print("#当前已经加过好友了")
        return "aa"
    else:
        return

    if (d(textContains="今天已经发送").exists(timeout=3)):
        elements = d(textContains="确定")  # 获取所有文本为'some_text'的元素
        if(len(elements)>0):
            random_click_view(d,elements.info)
            return "88"
    pkl_add_log("log.pkl", str(serial), "开始添加好友")
    if (d(text="发送").exists(timeout=3)):
        elements = d(text="发送")  # 获取所有文本为'some_text'的元素
        random_click_view(d,elements.info)
        time.sleep(2)
        pkl_add_log("log.pkl", str(serial), "添加好友完成")
        return "1",account_name,nick_name
    elif (d(text="加好友").exists(timeout=1)):
        print("对方设置了隐私")
        return "1"
    elif (d(text="发消息").exists(timeout=1)):
        print("当前有发消息")
        if("delete_zhitong" in str(task)):
            print("当前是直通用户")
            pkl_add_log("log.pkl", str(serial), "当前是直通用户,需要删除")
            elements3 = d(resourceId="com.alipay.mobile.antui:id/right_container_2")
            print("elements3=", len(elements3))
            if (len(elements3) > 0):
                #elements3.click()
                random_click_view(d, elements3.info)
            else:
                return
            time.sleep(2)
            d.drag(500, 1200, 500, 500)
            time.sleep(2)
            d.drag(500, 1200, 500, 500)
            time.sleep(2)

            elements3 = d(text="删除", resourceId="com.alipay.android.phone.wallet.profileapp:id/set_delete")
            print("elements3=", len(elements3))
            if (len(elements3) > 0):
                random_click_view(d, elements3.info)
                time.sleep(3)
            else:
                return

            elements3 = d(text="删除", resourceId="com.alipay.mobile.antui:id/ensure")
            print("elements3=", len(elements3))
            if (len(elements3) > 0):
                random_click_view(d, elements3.info)
                return "aaa"
            else:
                return
        else:
            return "1",account_name,nick_name
    else:
        return "1",account_name,nick_name


class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("zhifubao工具")
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
        self.titleLabel_renwu = QLabel("*"*55+"运行日志"+"*"*55)
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
        self.caozuo_config = QLabel("*" * 55 + "脚本配置" + "*" * 55)
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
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','当前任务',"统计"])
        self.table_widget.setColumnWidth(0,30)
        self.table_widget.setShowGrid(True)
        self.table_widget.itemChanged.connect(self.on_item_changed)
        #self.table_widget.itemClicked.connect(self.on_item_clicked)

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area.setFixedHeight(300)  # Set fixed height for the scroll area
        self.scroll_area.setFixedWidth(650)
        #self.scroll_area.verticalScrollBar().setValue(3)
        #self.scroll_area




        #以下是内容相关的列表
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Make the text edit read-only
        self.scroll_area_log = QScrollArea(self)
        self.scroll_area_log.setWidget(self.text_edit)
        self.scroll_area_log.setWidgetResizable(True)  # Allow the widget to resize
        self.scroll_area_log.setFixedHeight(200)  # Set a fixed height for the scroll area
        self.scroll_area_log.setFixedWidth(650)

        # self.scroll_area.verticalScrollBar().setValue(3)
        # self.scroll_area

        self.horizontal_layout = QHBoxLayout()
        #self.horizontal_layout.addWidget(self.caozuo_tiel)  # Add the operation title label
        # Create and add QRadioButtons to the horizontal layout
        # (You can customize the text and other properties as needed)
        self.radio_button0 = QLabel("           ")
        self.radio_button_select = QPushButton("全选")
        self.radio_button_select.clicked.connect(self.on_item_clicked)

        self.radio_button1 = QCheckBox("加好友")
        self.radio_button1.setChecked(True)
        self.radio_button2 = QCheckBox("删好友")
        self.radio_button3 = QCheckBox("统计")
        self.radio_button3.setChecked(True)
        self.radio_button4 = QCheckBox("删除直通")
        self.radio_button4.setChecked(True)
        self.radio_button5 = QLabel("           ")
        # Add the radio buttons to the horizontal layout
        self.horizontal_layout.addWidget(self.radio_button_select)
        self.horizontal_layout.addWidget(self.radio_button0)
        self.horizontal_layout.addWidget(self.radio_button1)
        #self.horizontal_layout.addWidget(self.radio_button2)
        self.horizontal_layout.addWidget(self.radio_button3)
        self.horizontal_layout.addWidget(self.radio_button4)
        self.horizontal_layout.addWidget(self.radio_button5)

        # Add the horizontal layout to the main vertical layout
        # Make sure to add it at the correct position, after the scroll area for the table widget
          # This will add the horizontal layout with the title and radio buttons
        self.label_from = QLabel('                          加人间隔：')
        self.line_edit_from = QLineEdit("8")
        self.line_edit_from.setFixedWidth(40)

        self.label_to = QLabel('至')
        self.line_edit_to = QLineEdit("20")
        self.line_edit_to.setFixedWidth(40)
        self.label_seconds = QLabel('秒', self)

        self.label_from111 = QLabel('                          每个账号加')
        self.jiarenshurukuang = QLineEdit("30")
        self.jiarenshurukuang.setFixedWidth(40)
        self.label_from222 = QLabel('人后,结束                      ')
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        self.h_layout.addWidget(self.label_to)
        self.h_layout.addWidget(self.line_edit_to)
        self.h_layout.addWidget(self.label_seconds)

        self.h_layout.addWidget(self.label_from111)
        self.h_layout.addWidget(self.jiarenshurukuang)
        self.h_layout.addWidget(self.label_from222)

        self.h_layout.setSpacing(5)
        # 设置布局与窗口边框之间的边距（例如，设置为 0 像素）
        self.h_layout.setContentsMargins(0, 0, 0, 0)

        self.h_layout_kongge = QHBoxLayout()
        self.label_file_kongge = QLabel("                          ")
        self.h_layout_kongge.addWidget(self.label_file_kongge)

        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("                          请选择配置文件夹:")
        self.h_layout_dir.addWidget(self.label_file)

        file_temp_path = get_value_by_key_pkl("shuju_config.pkl","file_path")
        if(file_temp_path != None):
            self.file_textbox = QLineEdit(file_temp_path)
        else:
            self.file_textbox = QLineEdit("请输入文件夹路径")
        self.h_layout_dir.addWidget(self.file_textbox)
        self.file_button = QPushButton("选择文件",self)
        self.temp = QLabel("                          ")
        self.h_layout_dir.addWidget(self.file_button)
        self.h_layout_dir.addWidget(self.temp)

        self.add_text_button = QPushButton('添加文本', self)
        self.add_text_button.clicked.connect(self.add_text)



        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)  # 设置布局间距为0
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.caozuo_config)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge)
        layout.addLayout(self.h_layout_dir)
        layout.addWidget(self.titleLabel_renwu)
        layout.addWidget(self.scroll_area_log)

        # Variable to store the selected IDs
        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(10000)

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.add_text)
        self.timer1.start(1300)

        # Initial load
        self.refresh_pkl_files()
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("执行")
        self.execute_button.resize(100,30)

        self.button_gang.addWidget(self.execute_button)

        self.button_gang.addWidget(self.add_text_button)
        self.execute_button_delete = QPushButton("删除")
        self.execute_button_delete.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_delete)

        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_reset)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.file_button.clicked.connect(self.on_file_button_clicked)
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



    def on_file_button_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            # If a folder is selected, update the QLabel
            self.file_textbox.setText(folder_path)
            updata_pkl_config_mianban("file_path",folder_path)
        else:
            self.file_textbox.setText('No folder selected')
    def execute_button_clicked(self):
        #print("---------------")
        if(self.selected_ids == []):
            toast("请选择机型")
            pkl_add_log("log.pkl", "全部--->", "请选择执行手机。。。。。。。。")
            return
        for temp in self.selected_ids:
            #print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "支付宝")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        tasks = []
        #self.scroll_area.ensureWidgetVisible(100)
        if(self.radio_button1.isChecked() == True):
            tasks.append("add")
        if (self.radio_button2.isChecked() == True):
            tasks.append("delete")
        if (self.radio_button3.isChecked() == True):
            tasks.append("tongji")
        if (self.radio_button4.isChecked() == True):
            tasks.append("delete_zhitong")
        print("tasks------------",tasks)

        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,self.file_textbox.text(),tasks,self.line_edit_from.text(),self.line_edit_to.text(),self.jiarenshurukuang.text()))
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
    # def refresh_pkl_files(self):
    #     # 保存当前滚动位置
    #     current_pos = self.table_widget.verticalScrollBar().value()
    #
    #     #print("current_scroll_position",current_scroll_position)
    #     # 清除旧数据
    #     self.table_widget.setRowCount(0)
    #     # 遍历目录中的所有文件
    #     directory = './shuju'
    #     row_index = 0
    #
    #     sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))
    #     #print("sorted_data=",sorted_data)
    #
    #     for device_id,v in sorted_data.items():
    #         #print("device_id---->",device_id)
    #         file_name = directory+"/"+str(device_id)+".pkl"
    #         #print("file_name---",file_name)
    #         if(os.path.isfile(file_name)):
    #             try:
    #                 with open(file_name, 'rb') as file:
    #                     data = pickle.load(file)
    #
    #                     #print("data-----------,",data)
    #
    #                     # 假设数据是一个字典
    #                     if isinstance(data, dict):
    #                         # 插入新行
    #                         self.table_widget.insertRow(row_index)
    #                         # 添加复选框
    #                         checkbox = QCheckBox(self)
    #                         #print("self.selected_ids=",self.selected_ids)
    #                         #print("os.path.splitext(file_name)[0]",os.path.splitext(file_name)[0].split("/")[2])
    #                         if os.path.splitext(file_name)[0].split("/")[2] in self.selected_ids:
    #                             checkbox.setChecked(True)
    #                         if(data.get('执行状态', 'N/A') == "运行中"):
    #                             checkbox.setEnabled(False)
    #                         else:
    #                             checkbox.setEnabled(True)
    #                         # if (data.get('连接状态', 'N/A') == "中断连接"):
    #                         #     checkbox.setEnabled(True)
    #                         # else:
    #                         #     checkbox.setEnabled(True)
    #                         checkbox.stateChanged.connect(lambda state, row=row_index: self.update_selected_ids(state, row))
    #                         self.table_widget.setCellWidget(row_index, 0, checkbox)
    #                         # 设置文件名（去除后缀）
    #                         self.table_widget.setItem(row_index, 1, QTableWidgetItem(device_id))
    #                         # 设置其他数据
    #                         print(data.get('name', 'N/A'))
    #                         phone_name = get_value_by_key_pkl("config.pkl",data.get('name', 'N/A'))
    #                         print("phone_name---------->",phone_name)
    #                         if(phone_name != None):
    #                             item_i = QTableWidgetItem(phone_name)
    #                         else:
    #                             item_i = QTableWidgetItem(data.get('nick_name', 'N/A'))
    #                         #item_i.setForeground(QBrush(QColor(255,0,0)))
    #
    #                         self.table_widget.setItem(row_index, 2, item_i)
    #                         if(data.get('连接状态', 'N/A') == "中断连接"):
    #                             item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
    #                             item_lianjie.setForeground(QBrush(QColor(255,0,0)))
    #                         else:
    #                             item_lianjie = QTableWidgetItem(data.get('连接状态', 'N/A'))
    #                             item_lianjie.setForeground(QBrush(QColor(0, 0, 0)))
    #                         item_lianjie.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                         self.table_widget.setItem(row_index, 3, item_lianjie)
    #
    #                         #item_i = QTableWidgetItem(data.get('执行状态', 'N/A'))
    #                         # item_i.setForeground(QBrush(QColor(255,0,0)))
    #                         item_zhuangtai = QTableWidgetItem(data.get('执行状态', 'N/A'))
    #                         item_zhuangtai.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                         self.table_widget.setItem(row_index, 4, item_zhuangtai)
    #
    #                         # item_zhuangage = QTableWidgetItem(data.get('age', 'N/A'))
    #                         # item_zhuangage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                         # self.table_widget.setItem(row_index, 5, item_zhuangage)
    #                         #
    #                         # item_add = QTableWidgetItem(data.get('add', 'N/A'))
    #                         # item_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                         # self.table_widget.setItem(row_index, 6, item_add)
    #
    #                         item_renwu = QTableWidgetItem(data.get('进行的任务', 'N/A'))
    #                         item_renwu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                         self.table_widget.setItem(row_index, 5, item_renwu)
    #
    #                         button111 = QTableWidgetItem(data.get('tongji', 'N/A'))
    #                         # button111.clicked.connect(lambda: print("Button clicked!"))
    #                         self.table_widget.setItem(row_index, 6,button111)
    #
    #                         row_index += 1
    #             except Exception as e:
    #                 print(f"读取文件 {file_name} 时出错: {e}")
    #      # 恢复滚动位置
    #     self.table_widget.verticalScrollBar().setSliderPosition(current_pos)

    def refresh_pkl_files(self):
        # 保存当前滚动位置
        current_pos = self.table_widget.verticalScrollBar().value()

        #print("current_scroll_position",current_scroll_position)
        # 清除旧数据
        self.table_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './shuju'
        row_index = 0
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'rb') as file:
                        data = pickle.load(file)

                        #print("data-----------,",data)

                        # 假设数据是一个字典
                        if isinstance(data, dict):
                            # 插入新行
                            self.table_widget.insertRow(row_index)
                            # 添加复选框
                            checkbox = QCheckBox(self)
                            if os.path.splitext(filename)[0] in self.selected_ids:
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
                            self.table_widget.setItem(row_index, 1, QTableWidgetItem(os.path.splitext(filename)[0]))
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
                    print(f"读取文件 {filepath} 时出错: {e}")
         # 恢复滚动位置
        self.table_widget.verticalScrollBar().setSliderPosition(current_pos)

    def update_selected_ids(self, state, row):
        # 更新选中的编号
        item_id = self.table_widget.item(row, 1).text()  # 获取编号
        print("item_id=",item_id)
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
    with lock111:
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
    while True:
        current_devices = get_connected_devices()
        current_device_ids = {device[0] for device in current_devices}

        # Check for new connections
        new_devices = current_device_ids - known_devices
        for device_id in new_devices:
            #print(f"Device connected: {device_id}")
            dic = {"name":device_id,"连接状态":"已连接","执行状态":"空闲中","age":"1811","add":"bj1","xingbie":"nan","进行的任务":"空闲","nick_name":"昵称点击可编辑","tongji":"0"}
            pkl_add("./shuju/"+device_id+".pkl",dic)
        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
            #print(f"Device disconnected: {device_id}")
            updata_pkl("./shuju/"+device_id+".pkl","连接状态","中断连接")
        # Update the known devices set
        known_devices = current_device_ids

        time.sleep(5)  # Check every 5 seconds
def delete_directory_contents(directory):
    shutil.rmtree(directory)
    os.makedirs(directory)  # 重新创建空文件夹
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")


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


    # d = u2.connect("Q5S0219527003267")
    # tongji(d,"Q5S0219527003267",r"C:\Users\Administrator\Desktop\config")