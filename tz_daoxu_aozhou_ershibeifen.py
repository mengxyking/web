import pickle

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFileDialog
import threading
import shutil
import hashlib
import platform
import time
import uuid
import jingdong_daoxu_aozhou


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
    pklfile = "shuju_aozhou.pkl"
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
    pklfile = "shuju_aozhou.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "0,1,2,3,4,5,6","tz_dizhi":"https://www.ip5276.com/member/index","jiekou_dizhi":"https://www.1689628.com/api/pks/getPksHistoryList.do?lotCode=10012","guanya1":"冠军","guanya2":"亚军","guanya3":"第三名","guanya4":"第四名","guanya5":"第五名","guanya6":"第六名","guanya7":"第七名","guanya8":"第八名","guanya9":"第九名","guanya10":"第十名","daxiao1":"大","daxiao2":"小","daxiao3":"单","daxiao4":"双","daxiao5":"双","daxiao6":"双","daxiao7":"双","daxiao8":"双","daxiao9":"双","daxiao10":"双","daxiao11":"双","daxiao12":"双","daxiao13":"双","daxiao14":"双","daxiao15":"双","daxiao16":"双","daxiao17":"双","daxiao18":"双","daxiao19":"双","daxiao20":"双","celue1":"1,2,3,4,5","celue2":"1,2,3,4,5","celue3":"1,2,3,4,5","celue4":"1,2,3,4,5","celue5":"1,2,3,4,5","celue6":"1,2,3,4,5","celue7":"1,2,3,4,5","celue8":"1,2,3,4,5","celue9":"1,2,3,4,5","celue10":"1,2,3,4,5","celue11":"1,2,3,4,5","celue12":"1,2,3,4,5","celue13":"1,2,3,4,5","celue14":"1,2,3,4,5","celue15":"1,2,3,4,5","celue16":"1,2,3,4,5","celue17":"1,2,3,4,5","celue18":"1,2,3,4,5","celue19":"1,2,3,4,5","celue20":"1,2,3,4,5"}
        # If it doesn't exist, create the file
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(my_dict, pkl_file)
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    aaa = dic.get(key)
    return aaa
# def get_value_by_key_pkl_dai_moren(key,moren):
#     pklfile = "shuju.pkl"
#     if not os.path.isfile(pklfile):
#         my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "0,1,2,3,4,5,6","tz_dizhi":"https://www.ip5276.com/member/index","jiekou_dizhi":"https://1689628.com/api/pks/getPksHistoryList.do?lotCode=10037"}
#         # If it doesn't exist, create the file
#         with open(pklfile, 'wb') as pkl_file:
#             pickle.dump(my_dict, pkl_file)
#     dic = {}
#     with open(pklfile, 'rb') as pkl_file:
#         dic = pickle.load(pkl_file)
#     aaa = dic.get(key)
#     return aaa

def run_script():
    print("开始执行脚本")
    try:
        shuzu = []
        #print(checkbox222.checkState())
        if(checkbox222.isChecked() == True):
           dic111 = {"mingci":start_textbox_first.text(),"leixing":combo_box2222.currentText()}
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
        if (checkbox555_add_1.isChecked() == True):
            dic333 = {"mingci": start_textbox_five.text(), "leixing": combo_box5555_add_1.currentText()}
            shuzu.append(dic333)
        if (checkbox666.isChecked() == True):
            dic333 = {"mingci": start_textbox_six.text(), "leixing": combo_box6666.currentText()}
            shuzu.append(dic333)
        if (checkbox777.isChecked() == True):
            dic333 = {"mingci": start_textbox_seven.text(), "leixing": combo_box7777.currentText()}
            shuzu.append(dic333)
        if (checkbox888.isChecked() == True):
            dic333 = {"mingci": start_textbox_aight.text(), "leixing": combo_box8888.currentText()}
            shuzu.append(dic333)
        if (checkbox999.isChecked() == True):
            dic333 = {"mingci": start_textbox_nine.text(), "leixing": combo_box9999.currentText()}
            shuzu.append(dic333)
        if (checkbox101010.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten.text(), "leixing": combo_box10101010.currentText()}
            shuzu.append(dic333)
        if (checkbox111111.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_1.text(), "leixing": combo_box11111111.currentText()}
            shuzu.append(dic333)
        if (checkbox121212.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_2.text(), "leixing": combo_box12121212.currentText()}
            shuzu.append(dic333)
        if (checkbox131313.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_3.text(), "leixing": combo_box13131313.currentText()}
            shuzu.append(dic333)
        if (checkbox141414.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_4.text(), "leixing": combo_box14141414.currentText()}
            shuzu.append(dic333)
        if (checkbox151515.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_5.text(), "leixing": combo_box15151515.currentText()}
            shuzu.append(dic333)
        if (checkbox161616.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_6.text(), "leixing": combo_box16161616.currentText()}
            shuzu.append(dic333)
        if (checkbox171717.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_7.text(), "leixing": combo_box17171717.currentText()}
            shuzu.append(dic333)
        if (checkbox181818.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_8.text(), "leixing": combo_box18181818.currentText()}
            shuzu.append(dic333)
        if (checkbox191919.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_9.text(), "leixing": combo_box19191919.currentText()}
            shuzu.append(dic333)
        if (checkbox202020.isChecked() == True):
            dic333 = {"mingci": start_textbox_ten_10.text(), "leixing": combo_box20202020.currentText()}
            shuzu.append(dic333)
        for temp in shuzu:
            print(temp)
        print("开始执行脚本")
        jingdong_daoxu_aozhou.main_gui(file_textbox.text(),start_textbox_kami.text(),shuzu,file_textbox_tz_dizhi.text(),file_textbox_jiekou_dizhi.text())
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
combo_box2222 = QComboBox()
combo_box2222.addItems(["大","小",  "单", "双"])
combo_box2222.setCurrentText(get_value_by_key_pkl("daxiao1"))
checkbox222 = QCheckBox()
checkbox222.setChecked(True)
#bottom_layout2.addWidget(combo_box222)

#bottom_layout2.addWidget(checkbox222)

#配置低一个投注策略的顺序
tzjine_first = get_value_by_key_pkl("celue1")
start_textbox_first= QLineEdit(tzjine_first)
bottom_layout2.addWidget(start_textbox_first)
bottom_layout2.addWidget(combo_box2222)
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


bottom_layout5_add_1 = QHBoxLayout()
label555_add_1 = QLabel("请输入第五名tz名次")
bottom_layout5_add_1.addWidget(label555_add_1)
combo_box555_add_1 = QComboBox()
combo_box555_add_1.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box5555_add_1 = QComboBox()
combo_box5555_add_1.addItems(["双","大","小",  "单"])
combo_box5555_add_1.setCurrentText(get_value_by_key_pkl("daxiao5"))
checkbox555_add_1 = QCheckBox()
checkbox555_add_1.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_five = get_value_by_key_pkl("celue5")
start_textbox_five= QLineEdit(tzjine_five)
bottom_layout5_add_1.addWidget(start_textbox_five)
bottom_layout5_add_1.addWidget(combo_box5555_add_1)
bottom_layout5_add_1.addWidget(checkbox555_add_1)

bottom_layout6 = QHBoxLayout()
label666 = QLabel("请输入第六名tz名次")
bottom_layout6.addWidget(label666)
combo_box666 = QComboBox()
combo_box666.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box6666 = QComboBox()
combo_box6666.addItems(["双","大","小",  "单"])
combo_box6666.setCurrentText(get_value_by_key_pkl("daxiao6"))

checkbox666 = QCheckBox()
checkbox666.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_six = get_value_by_key_pkl("celue6")
start_textbox_six= QLineEdit(tzjine_six)
bottom_layout6.addWidget(start_textbox_six)
bottom_layout6.addWidget(combo_box6666)
bottom_layout6.addWidget(checkbox666)

bottom_layout7 = QHBoxLayout()
label777 = QLabel("请输入第七名tz名次")
bottom_layout7.addWidget(label777)
combo_box777 = QComboBox()
combo_box777.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box7777 = QComboBox()
combo_box7777.addItems(["双","大","小",  "单"])
combo_box7777.setCurrentText(get_value_by_key_pkl("daxiao7"))

checkbox777 = QCheckBox()
checkbox777.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_seven = get_value_by_key_pkl("celue7")
start_textbox_seven= QLineEdit(tzjine_seven)
bottom_layout7.addWidget(start_textbox_seven)
bottom_layout7.addWidget(combo_box7777)
bottom_layout7.addWidget(checkbox777)

bottom_layout8 = QHBoxLayout()
label888 = QLabel("请输入第八名tz名次")
bottom_layout8.addWidget(label888)
combo_box888 = QComboBox()
combo_box888.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box8888 = QComboBox()
combo_box8888.addItems(["双","大","小",  "单"])
combo_box8888.setCurrentText(get_value_by_key_pkl("daxiao8"))

checkbox888 = QCheckBox()
checkbox888.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_aight = get_value_by_key_pkl("celue8")
start_textbox_aight= QLineEdit(tzjine_aight)
bottom_layout8.addWidget(start_textbox_aight)
bottom_layout8.addWidget(combo_box8888)
bottom_layout8.addWidget(checkbox888)

bottom_layout9 = QHBoxLayout()
label999 = QLabel("请输入第九名tz名次")
bottom_layout9.addWidget(label999)
combo_box999 = QComboBox()
combo_box999.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box9999 = QComboBox()
combo_box9999.addItems(["双","大","小",  "单"])
combo_box9999.setCurrentText(get_value_by_key_pkl("daxiao9"))

checkbox999 = QCheckBox()
checkbox999.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_nine = get_value_by_key_pkl("celue9")
start_textbox_nine= QLineEdit(tzjine_nine)
bottom_layout9.addWidget(start_textbox_nine)
bottom_layout9.addWidget(combo_box9999)
bottom_layout9.addWidget(checkbox999)

bottom_layout10 = QHBoxLayout()
label101010 = QLabel("请输入第十名tz名次")
bottom_layout10.addWidget(label101010)
combo_box101010 = QComboBox()
combo_box101010.addItems([  "第四名", "第五名", "第六名", "第七名", "第八名", "第九名", "第十名","冠军","亚军","第三名"])
combo_box10101010 = QComboBox()
combo_box10101010.addItems(["双","大","小",  "单"])
combo_box10101010.setCurrentText(get_value_by_key_pkl("daxiao10"))

checkbox101010 = QCheckBox()
checkbox101010.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten = get_value_by_key_pkl("celue10")
start_textbox_ten= QLineEdit(tzjine_ten)
bottom_layout10.addWidget(start_textbox_ten)
bottom_layout10.addWidget(combo_box10101010)
bottom_layout10.addWidget(checkbox101010)



bottom_layout11 = QHBoxLayout()
label111111 = QLabel("请输入第十一名tz名次")
bottom_layout11.addWidget(label111111)
combo_box11111111 = QComboBox()
combo_box11111111.addItems(["双","大","小",  "单"])
combo_box11111111.setCurrentText(get_value_by_key_pkl("daxiao11"))

checkbox111111 = QCheckBox()
checkbox111111.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_1 = get_value_by_key_pkl("celue11")
start_textbox_ten_1= QLineEdit(tzjine_ten_1)
bottom_layout11.addWidget(start_textbox_ten_1)
bottom_layout11.addWidget(combo_box11111111)
bottom_layout11.addWidget(checkbox111111)


bottom_layout12 = QHBoxLayout()
label121212 = QLabel("请输入第十二名tz名次")
bottom_layout12.addWidget(label121212)
combo_box12121212 = QComboBox()
combo_box12121212.addItems(["双","大","小",  "单"])
combo_box12121212.setCurrentText(get_value_by_key_pkl("daxiao12"))

checkbox121212 = QCheckBox()
checkbox121212.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_2 = get_value_by_key_pkl("celue12")
start_textbox_ten_2= QLineEdit(tzjine_ten_2)
bottom_layout12.addWidget(start_textbox_ten_2)
bottom_layout12.addWidget(combo_box12121212)
bottom_layout12.addWidget(checkbox121212)

bottom_layout13 = QHBoxLayout()
label131313 = QLabel("请输入第十三名tz名次")
bottom_layout13.addWidget(label131313)
combo_box13131313 = QComboBox()
combo_box13131313.addItems(["双","大","小",  "单"])
combo_box13131313.setCurrentText(get_value_by_key_pkl("daxiao13"))

checkbox131313 = QCheckBox()
checkbox131313.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_3 = get_value_by_key_pkl("celue13")
start_textbox_ten_3= QLineEdit(tzjine_ten_3)
bottom_layout13.addWidget(start_textbox_ten_3)
bottom_layout13.addWidget(combo_box13131313)
bottom_layout13.addWidget(checkbox131313)

bottom_layout14 = QHBoxLayout()
label141414 = QLabel("请输入第十四名tz名次")
bottom_layout14.addWidget(label141414)
combo_box14141414 = QComboBox()
combo_box14141414.addItems(["双","大","小",  "单"])
combo_box14141414.setCurrentText(get_value_by_key_pkl("daxiao14"))

checkbox141414 = QCheckBox()
checkbox141414.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_4 = get_value_by_key_pkl("celue14")
start_textbox_ten_4= QLineEdit(tzjine_ten_4)
bottom_layout14.addWidget(start_textbox_ten_4)
bottom_layout14.addWidget(combo_box14141414)
bottom_layout14.addWidget(checkbox141414)


bottom_layout15 = QHBoxLayout()
label151515 = QLabel("请输入第十五名tz名次")
bottom_layout15.addWidget(label151515)
combo_box15151515 = QComboBox()
combo_box15151515.addItems(["双","大","小",  "单"])
combo_box15151515.setCurrentText(get_value_by_key_pkl("daxiao15"))

checkbox151515 = QCheckBox()
checkbox151515.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_5 = get_value_by_key_pkl("celue15")
start_textbox_ten_5= QLineEdit(tzjine_ten_5)
bottom_layout15.addWidget(start_textbox_ten_5)
bottom_layout15.addWidget(combo_box15151515)
bottom_layout15.addWidget(checkbox151515)


bottom_layout16 = QHBoxLayout()
label161616 = QLabel("请输入第十六名tz名次")
bottom_layout16.addWidget(label161616)
combo_box16161616 = QComboBox()
combo_box16161616.addItems(["双","大","小",  "单"])
combo_box16161616.setCurrentText(get_value_by_key_pkl("daxiao16"))

checkbox161616 = QCheckBox()
checkbox161616.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_6 = get_value_by_key_pkl("celue16")
start_textbox_ten_6= QLineEdit(tzjine_ten_6)
bottom_layout16.addWidget(start_textbox_ten_6)
bottom_layout16.addWidget(combo_box16161616)
bottom_layout16.addWidget(checkbox161616)


bottom_layout17 = QHBoxLayout()
label171717 = QLabel("请输入第十七名tz名次")
bottom_layout17.addWidget(label171717)
combo_box17171717 = QComboBox()
combo_box17171717.addItems(["双","大","小",  "单"])
combo_box17171717.setCurrentText(get_value_by_key_pkl("daxiao17"))

checkbox171717 = QCheckBox()
checkbox171717.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_7 = get_value_by_key_pkl("celue17")
start_textbox_ten_7= QLineEdit(tzjine_ten_7)
bottom_layout17.addWidget(start_textbox_ten_7)
bottom_layout17.addWidget(combo_box17171717)
bottom_layout17.addWidget(checkbox171717)


bottom_layout18 = QHBoxLayout()
label181818 = QLabel("请输入第十八名tz名次")
bottom_layout18.addWidget(label181818)
combo_box18181818 = QComboBox()
combo_box18181818.addItems(["双","大","小",  "单"])
combo_box18181818.setCurrentText(get_value_by_key_pkl("daxiao18"))

checkbox181818 = QCheckBox()
checkbox181818.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_8 = get_value_by_key_pkl("celue18")
start_textbox_ten_8= QLineEdit(tzjine_ten_8)
bottom_layout18.addWidget(start_textbox_ten_8)
bottom_layout18.addWidget(combo_box18181818)
bottom_layout18.addWidget(checkbox181818)

bottom_layout19 = QHBoxLayout()
label191919 = QLabel("请输入第十九名tz名次")
bottom_layout19.addWidget(label191919)
combo_box19191919 = QComboBox()
combo_box19191919.addItems(["双","大","小",  "单"])
combo_box19191919.setCurrentText(get_value_by_key_pkl("daxiao19"))

checkbox191919 = QCheckBox()
checkbox191919.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_9 = get_value_by_key_pkl("celue19")
start_textbox_ten_9= QLineEdit(tzjine_ten_9)
bottom_layout19.addWidget(start_textbox_ten_9)
bottom_layout19.addWidget(combo_box19191919)
bottom_layout19.addWidget(checkbox191919)


bottom_layout20 = QHBoxLayout()
label202020 = QLabel("请输入第二十名tz名次")
bottom_layout20.addWidget(label202020)
combo_box20202020 = QComboBox()
combo_box20202020.addItems(["双","大","小",  "单"])
combo_box20202020.setCurrentText(get_value_by_key_pkl("daxiao20"))

checkbox202020 = QCheckBox()
checkbox202020.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_10 = get_value_by_key_pkl("celue20")
start_textbox_ten_10= QLineEdit(tzjine_ten_10)
bottom_layout20.addWidget(start_textbox_ten_10)
bottom_layout20.addWidget(combo_box20202020)
bottom_layout20.addWidget(checkbox202020)

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
layout.addLayout(bottom_layout5_add_1)
layout.addLayout(bottom_layout6)
layout.addLayout(bottom_layout7)
layout.addLayout(bottom_layout8)
layout.addLayout(bottom_layout9)
layout.addLayout(bottom_layout10)
layout.addLayout(bottom_layout11)
layout.addLayout(bottom_layout12)
layout.addLayout(bottom_layout13)
layout.addLayout(bottom_layout14)
layout.addLayout(bottom_layout15)
layout.addLayout(bottom_layout16)
layout.addLayout(bottom_layout17)
layout.addLayout(bottom_layout18)
layout.addLayout(bottom_layout19)
layout.addLayout(bottom_layout20)
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
    updata_pkl("guanya5", combo_box555_add_1.currentText())
    updata_pkl("guanya6", combo_box666.currentText())
    updata_pkl("guanya7", combo_box777.currentText())
    updata_pkl("guanya8", combo_box888.currentText())
    updata_pkl("guanya9", combo_box999.currentText())
    updata_pkl("guanya10", combo_box101010.currentText())
    updata_pkl("daxiao1", combo_box888.currentText())
    updata_pkl("daxiao2", combo_box3333.currentText())
    updata_pkl("daxiao3", combo_box4444.currentText())
    updata_pkl("daxiao4", combo_box5555.currentText())
    updata_pkl("daxiao5", combo_box5555_add_1.currentText())
    updata_pkl("daxiao6", combo_box6666.currentText())
    updata_pkl("daxiao7", combo_box7777.currentText())
    updata_pkl("daxiao8", combo_box8888.currentText())
    updata_pkl("daxiao9", combo_box9999.currentText())
    updata_pkl("daxiao10", combo_box10101010.currentText())
    updata_pkl("daxiao11", combo_box11111111.currentText())
    updata_pkl("daxiao12", combo_box12121212.currentText())
    updata_pkl("daxiao13", combo_box13131313.currentText())
    updata_pkl("daxiao14", combo_box14141414.currentText())
    updata_pkl("daxiao15", combo_box15151515.currentText())
    updata_pkl("daxiao16", combo_box16161616.currentText())
    updata_pkl("daxiao17", combo_box17171717.currentText())
    updata_pkl("daxiao18", combo_box18181818.currentText())
    updata_pkl("daxiao19", combo_box19191919.currentText())
    updata_pkl("daxiao20", combo_box20202020.currentText())

    updata_pkl("celue1", start_textbox_first.text())
    updata_pkl("celue2", start_textbox_secend.text())
    updata_pkl("celue3", start_textbox_third.text())
    updata_pkl("celue4", start_textbox_four.text())
    updata_pkl("celue5", start_textbox_five.text())
    updata_pkl("celue6", start_textbox_six.text())
    updata_pkl("celue7", start_textbox_seven.text())
    updata_pkl("celue8", start_textbox_aight.text())
    updata_pkl("celue9", start_textbox_nine.text())
    updata_pkl("celue10", start_textbox_ten.text())
    updata_pkl("celue11", start_textbox_ten_1.text())
    updata_pkl("celue12", start_textbox_ten_2.text())
    updata_pkl("celue13", start_textbox_ten_3.text())
    updata_pkl("celue14", start_textbox_ten_4.text())
    updata_pkl("celue15", start_textbox_ten_5.text())
    updata_pkl("celue16", start_textbox_ten_6.text())
    updata_pkl("celue17", start_textbox_ten_7.text())
    updata_pkl("celue18", start_textbox_ten_8.text())
    updata_pkl("celue19", start_textbox_ten_9.text())
    updata_pkl("celue20", start_textbox_ten_10.text())

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
