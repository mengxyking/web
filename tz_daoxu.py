import pickle

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFileDialog
import threading
import shutil
import hashlib
import platform
import time
import uuid
import jingdong_daoxu
#import pjysdk as pjysdk
 # 获取MAC地址
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
    return mac
 # 获取硬盘序列号
def get_disk_serial():
    serial = os.popen('wmic diskdrive get serialnumber').read().split('\n')[1].strip()
    return serial
 # 获取CPU序列号
def get_cpu_serial():
    serial = os.popen('wmic cpu get processorid').read().split('\n')[1].strip()
    return serial
 # 获取计算机名
def get_computer_name():
    name = platform.node()
    return name
 # 叠加多种方式获取唯一标识
def get_unique_id():
    mac = get_mac_address()
    disk_serial = get_disk_serial()
    cpu_serial = get_cpu_serial()
    computer_name = get_computer_name()
    unique_id = mac + disk_serial + cpu_serial + computer_name
    unique_id_hash = hashlib.md5(unique_id.encode()).hexdigest()
    return unique_id_hash
def updata_pkl(key,value):
    pklfile = "shuju.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "请输入tz策略"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    dic[key]=value
    with open(pklfile, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
def get_value_by_key_pkl(key):
    pklfile = "shuju.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "0,1,2,3,4,5,6","tz_dizhi":"https://www.ip5276.com/member/index","jiekou_dizhi":"https://1689628.com/api/pks/getPksHistoryList.do?lotCode=10037","guanya1":"冠军","guanya2":"亚军","guanya3":"第三名","guanya4":"第四名","daxiao1":"大","daxiao2":"小","daxiao3":"单","daxiao4":"双","celue1":"1,2,3,4,5","celue2":"1,2,3,4,5","celue3":"1,2,3,4,5","celue4":"1,2,3,4,5"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    aaa = dic.get(key)
    return aaa
def get_value_by_key_pkl_dai_moren(key,moren):
    pklfile = "shuju.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "0,1,2,3,4,5,6","tz_dizhi":"https://www.ip5276.com/member/index","jiekou_dizhi":"https://1689628.com/api/pks/getPksHistoryList.do?lotCode=10037"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    aaa = dic.get(key)
    return aaa

def run_script():
    print("开始执行脚本")
    try:
        shuzu = []
        #print(checkbox222.checkState())
        if(checkbox222.isChecked() == True):
           dic111 = {"mingci":start_textbox_first.text(),"leixing":combo_box888.currentText()}
           shuzu.append(dic111)
        if (checkbox333.isChecked() == True):
            dic222 = {"mingci": start_textbox_secend.text(), "leixing": combo_box3333.currentText()}
            shuzu.append(dic222)
        if (checkbox444.isChecked() == True):
            dic333 = {"mingci": start_textbox_third.text(), "leixing": combo_box4444.currentText()}
            shuzu.append(dic333)
        if (checkbox555.isChecked() == True):
            dic333 = {"mingci": start_textbox_four.text(), "leixing": combo_box5555.currentText()}
            shuzu.append(dic333)
        for temp in shuzu:
            print(temp)
        print("开始执行脚本")
        jingdong_daoxu.main_gui(file_textbox.text(),start_textbox_kami.text(),shuzu,file_textbox_tz_dizhi.text(),file_textbox_jiekou_dizhi.text())
    except BaseException as e:
        print(e)
def heart():
    while True:
        print("-----")
        time.sleep(1)
import os

def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    print("00000000000000000000000000---------")
    print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def delete_file():
    path = getPhotoPath()
    print("开始删除文件----------"+str(path))
    folder_path = path  # 替换为你的文件夹路径
    # 删除文件夹下所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('无法删除 %s. 原因: %s' % (file_path, e))
def run_heart():
    # 在这里编写您的脚本代码
    print("开始执行脚本")
    try:
        t3 = threading.Thread(target=heart)
        t3.start()
    except BaseException as e:
        print(e)
def run_deleteFile():
    # 在这里编写您的脚本代码
    print("开始执行脚本")
    try:
        t3 = threading.Thread(target=delete_file)
        t3.start()
    except BaseException as e:
        print(e)


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
checked_options = []
app = QApplication([])
window = QWidget()
window.setWindowTitle("模拟测试")
button_layout = QHBoxLayout()
execute_button = QPushButton("执行")
button_layout.addWidget(execute_button)

file_layout_tz_dizhi = QHBoxLayout()
label_file_tz_dizhi = QLabel("请输入模拟测试地址")
file_layout_tz_dizhi.addWidget(label_file_tz_dizhi)
path_tz_dizhi = get_value_by_key_pkl("tz_dizhi")
file_textbox_tz_dizhi = QLineEdit(path_tz_dizhi)
file_layout_tz_dizhi.addWidget(file_textbox_tz_dizhi)

file_layout_jiekou_dizhi = QHBoxLayout()
label_file_jiekou_dizhi = QLabel("请输入模拟接口地址")
file_layout_jiekou_dizhi.addWidget(label_file_jiekou_dizhi)
path_jiekou_dizhi = get_value_by_key_pkl("jiekou_dizhi")
file_textbox_jiekou_dizhi = QLineEdit(path_jiekou_dizhi)
file_layout_jiekou_dizhi.addWidget(file_textbox_jiekou_dizhi)

file_layout = QHBoxLayout()
label_file = QLabel("请选择火狐浏览器exe目录")
file_layout.addWidget(label_file)
path = get_value_by_key_pkl("firefoxpath")
file_textbox = QLineEdit(path)
file_layout.addWidget(file_textbox)
file_button = QPushButton("选择文件")
file_layout.addWidget(file_button)

 #卡密
extra_layout_kami = QHBoxLayout()
labelc_kami = QLabel("请配置tz策略(例:0,0,1,1,3,4)")
extra_layout_kami.addWidget(labelc_kami)
tzjine = get_value_by_key_pkl("tzjine")
start_textbox_kami= QLineEdit(tzjine)
extra_layout_kami.addWidget(start_textbox_kami)
#
# bottom_layout1 = QHBoxLayout()
# label22 = QLabel("请输入模拟tz类型")
# bottom_layout1.addWidget(label22)
# combo_box1 = QComboBox()
# combo_box1.addItems(["大","小",  "单", "双"])
# bottom_layout1.addWidget(combo_box1)

bottom_layout2 = QHBoxLayout()
label2222 = QLabel("请输入第一名tz名次")
bottom_layout2.addWidget(label2222)
combo_box222 = QComboBox()
combo_box222.addItems(["冠军","亚军",  "第三名", "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名"])
#combo_box222.setCurrentText("第十名")
combo_box888 = QComboBox()
combo_box888.addItems(["大","小",  "单", "双"])
combo_box888.setCurrentText(get_value_by_key_pkl("daxiao1"))
checkbox222 = QCheckBox()
checkbox222.setChecked(True)
#bottom_layout2.addWidget(combo_box222)

#bottom_layout2.addWidget(checkbox222)

#配置低一个投注策略的顺序
tzjine_first = get_value_by_key_pkl("celue1")
start_textbox_first= QLineEdit(tzjine_first)
bottom_layout2.addWidget(start_textbox_first)
bottom_layout2.addWidget(combo_box888)
bottom_layout2.addWidget(checkbox222)


bottom_layout3 = QHBoxLayout()
label333 = QLabel("请输入第二名tz名次")
bottom_layout3.addWidget(label333)
combo_box333 = QComboBox()
combo_box333.addItems(["亚军",  "第三名", "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军"])
combo_box3333 = QComboBox()
combo_box3333.addItems(["小",  "单", "双","大"])
combo_box3333.setCurrentText(get_value_by_key_pkl("daxiao2"))
checkbox333 = QCheckBox()
checkbox333.setChecked(True)
#bottom_layout3.addWidget(combo_box333)

#配置低一个投注策略的顺序
tzjine_secend = get_value_by_key_pkl("celue2")
start_textbox_secend= QLineEdit(tzjine_secend)
bottom_layout3.addWidget(start_textbox_secend)
bottom_layout3.addWidget(combo_box3333)

bottom_layout3.addWidget(checkbox333)

bottom_layout4 = QHBoxLayout()
label444 = QLabel("请输入第三名tz名次")
bottom_layout4.addWidget(label444)
combo_box444 = QComboBox()
combo_box444.addItems([ "第三名", "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军"])
combo_box4444 = QComboBox()
combo_box4444.addItems([ "单", "双","大","小"])
combo_box4444.setCurrentText(get_value_by_key_pkl("daxiao3"))

checkbox444 = QCheckBox()
checkbox444.setChecked(True)
#bottom_layout4.addWidget(combo_box444)


tzjine_third = get_value_by_key_pkl("celue3")
start_textbox_third= QLineEdit(tzjine_third)
bottom_layout4.addWidget(start_textbox_third)
bottom_layout4.addWidget(combo_box4444)
bottom_layout4.addWidget(checkbox444)




bottom_layout5 = QHBoxLayout()
label555 = QLabel("请输入第四名tz名次")
bottom_layout5.addWidget(label555)
combo_box555 = QComboBox()
combo_box555.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box5555 = QComboBox()
combo_box5555.addItems(["双","大","小",  "单"])
combo_box5555.setCurrentText(get_value_by_key_pkl("daxiao4"))

checkbox555 = QCheckBox()
checkbox555.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_four = get_value_by_key_pkl("celue4")
start_textbox_four= QLineEdit(tzjine_four)
bottom_layout5.addWidget(start_textbox_four)
bottom_layout5.addWidget(combo_box5555)

bottom_layout5.addWidget(checkbox555)


 # 整体布局
layout = QVBoxLayout()
layout.addLayout(file_layout_jiekou_dizhi)
layout.addLayout(file_layout_tz_dizhi)
layout.addLayout(extra_layout_kami)
layout.addLayout(file_layout)
layout.addLayout(bottom_layout2)
layout.addLayout(bottom_layout3)
layout.addLayout(bottom_layout4)
layout.addLayout(bottom_layout5)
layout.addLayout(button_layout)


window.setLayout(layout)
window.show()
import requests
def is_url_accessible(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
def assert_file(filepath):
    import os
    # 设置文件路径
    file_path = filepath
    # 使用os.path.exists()检查文件是否存在
    if os.path.exists(file_path):
        return "1"
    else:
        return "0"
 # 按钮点击事件
def on_button_clicked():
    updata_pkl("firefoxpath",file_textbox.text())
    updata_pkl("tzjine", start_textbox_kami.text())
    updata_pkl("tz_dizhi", file_textbox_tz_dizhi.text())
    updata_pkl("jiekou_dizhi", file_textbox_jiekou_dizhi.text())

    updata_pkl("guanya1", combo_box222.currentText())
    updata_pkl("guanya2", combo_box333.currentText())
    updata_pkl("guanya3", combo_box444.currentText())
    updata_pkl("guanya4", combo_box555.currentText())
    updata_pkl("daxiao1", combo_box888.currentText())
    updata_pkl("daxiao2", combo_box3333.currentText())
    updata_pkl("daxiao3", combo_box4444.currentText())
    updata_pkl("daxiao4", combo_box5555.currentText())
    updata_pkl("celue1", start_textbox_first.text())
    updata_pkl("celue2", start_textbox_secend.text())
    updata_pkl("celue3", start_textbox_third.text())
    updata_pkl("celue4", start_textbox_four.text())

    if(is_url_accessible(file_textbox_tz_dizhi.text())!=True):
        toast("模拟测试地址无法访问")
        print("模拟测试地址无法访问")
        return
    if (is_url_accessible(file_textbox_jiekou_dizhi.text()) != True):
        toast("结果接口地址无法访问")
        print("结果接口地址无法访问")
        return



    execute_button.setEnabled(False)
    t1 = threading.Thread(target=run_script)
    t1.start()
def save_to_file():
    # data = {
    #     # "onVideoPlayTime": start_textbox.text() + "to" + end_textbox.text(),  # 每个视频播放时长
    #     # "commentCountOnce": comment_combo_box.currentText(),  # 每10个视频的评论数
    #     # "likeCountOnce": combo_box.currentText(),  # 每10个视频的点赞数
    #     # "followCountOnce": start_textbox1.text() + "to" + end_textbox1.text(),  # 每循环一次关注多少个作者
    #     # "afterFollowSleepTime": combo_box1.currentText(),  # 每循环一次 休息的时间
    #     "exePath": file_textbox.text(),  # 抖音exe文件路径
    #     # "task": str(follow_checkbox.isChecked())+"to"+str(unfollow_checkbox.isChecked()),  # 最外层循环控制
    #     # "cancleCount": start_textboxC.text(),  # cancleCount每次执行取消关注 执行多少个
    #     # "taskC": str(follow_checkboxC.isChecked())+"to"+str(unfollow_checkboxC.isChecked()),  # 最外层循环控制
    # }

    print("开始书写")
    # with open(file_zhanghao, "w", encoding="utf-8") as file:
    #     file.write(start_textbox_account.text())
    # with open(file_kami, "w", encoding="utf-8") as file:
    #     file.write(start_textbox_kami.text())
    # with open(file_mima, "w", encoding="utf-8") as file:
    #     file.write(start_textbox_secret.text())
    # with open(file_ck_config_path, "w", encoding="utf-8") as file:
    #     file.write(file_textbox_file.text())


def on_file_button_clicked():
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        file_names = file_dialog.selectedFiles()
        file_textbox.setText(file_names[0])

def toast(tishi):
    # import win32con
    # import ctypes
    # ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 3000)
    print()


file_button.clicked.connect(on_file_button_clicked)
# file_button_file.clicked.connect(on_file_button_clicked_file)
execute_button.clicked.connect(on_button_clicked)
sys.exit(app.exec_())
