import pickle

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFileDialog
import threading
import shutil
import hashlib
import platform
import time
import uuid
import jingdong_daoxu_aozhou_feiting888_suiji


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
    pklfile = "shuju_aozhou_feiting.pkl"
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
    pklfile = "shuju_aozhou_feiting.pkl"
    if not os.path.isfile(pklfile):
        my_dict = {"firefoxpath": "请输入exe地址", "tzjine": "0,1,2,3,4,5,6","tz_dizhi":"https://www.ip5276.com/member/index","jiekou_dizhi":"https://www.1689567.com/api/pks/getPksHistoryList.do?lotCode=10012","jiekou_dizhi_feiting":"https://www.1689567.com/api/pks/getPksHistoryList.do?lotCode=10058","guanya1":"冠军","guanya2":"亚军","guanya3":"第三名","guanya4":"第四名","guanya5":"第五名","guanya6":"第六名","guanya7":"第七名","guanya8":"第八名","guanya9":"第九名","guanya10":"第十名","daxiao1":"大","daxiao2":"小","daxiao3":"单","daxiao4":"双","daxiao5":"双","daxiao6":"双","daxiao7":"双","daxiao8":"双","daxiao9":"双","daxiao10":"双","daxiao11":"双","daxiao12":"双","daxiao13":"双","daxiao14":"双","daxiao15":"双","daxiao16":"双","daxiao17":"双","daxiao18":"双","daxiao19":"双","daxiao20":"双","celue1":"1,2,3,4,5","celue2":"1,2,3,4,5","celue3":"1,2,3,4,5","celue4":"1,2,3,4,5","celue5":"1,2,3,4,5","celue6":"1,2,3,4,5","celue7":"1,2,3,4,5","celue8":"1,2,3,4,5","celue9":"1,2,3,4,5","celue10":"1,2,3,4,5","celue11":"1,2,3,4,5","celue12":"1,2,3,4,5","celue13":"1,2,3,4,5","celue14":"1,2,3,4,5","celue15":"1,2,3,4,5","celue16":"1,2,3,4,5","celue17":"1,2,3,4,5","celue18":"1,2,3,4,5","celue19":"1,2,3,4,5","celue20":"1,2,3,4,5"}
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
    print("1")
    print("开始执行脚本")
    try:
        suiji_luzi_shuzi = []
        shuzu = []
        #print(checkbox222.checkState())
        if(checkbox222.isChecked() == True):
           dic111 = {"mingci":combo_box222.currentText(),"leixing":combo_box2222.currentText(),"zhengfan":zhengfan_box111.currentText(),"wangqi":wangqi_box111.currentText()}
           shuzu.append(dic111)
        if (checkbox333.isChecked() == True):
            dic222 = {"mingci": combo_box333.currentText(), "leixing": combo_box3333.currentText(),"zhengfan":zhengfan_box222.currentText(),"wangqi":wangqi_box222.currentText()}
            shuzu.append(dic222)
        if (checkbox444.isChecked() == True):
            dic333 = {"mingci": combo_box444.currentText(), "leixing": combo_box4444.currentText(),"zhengfan":zhengfan_box333.currentText(),"wangqi":wangqi_box333.currentText()}
            shuzu.append(dic333)
        if (checkbox555.isChecked() == True):
            dic333 = {"mingci": combo_box555.currentText(), "leixing": combo_box5555.currentText(),"zhengfan":zhengfan_box444.currentText(),"wangqi":wangqi_box444.currentText()}
            shuzu.append(dic333)
        if (checkbox555_add_1.isChecked() == True):
            dic333 = {"mingci": combo_box555_add_1.currentText(), "leixing": combo_box5555_add_1.currentText(),"zhengfan":zhengfan_box555.currentText(),"wangqi":wangqi_box555.currentText()}
            shuzu.append(dic333)
        if (checkbox666.isChecked() == True):
            dic333 = {"mingci": combo_box666.currentText(), "leixing": combo_box6666.currentText(),"zhengfan":zhengfan_box666.currentText(),"wangqi":wangqi_box666.currentText()}
            shuzu.append(dic333)
        if (checkbox777.isChecked() == True):
            dic333 = {"mingci": combo_box777.currentText(), "leixing": combo_box7777.currentText(),"zhengfan":zhengfan_box777.currentText(),"wangqi":wangqi_box777.currentText()}
            shuzu.append(dic333)
        if (checkbox888.isChecked() == True):
            dic333 = {"mingci": combo_box888.currentText(), "leixing": combo_box8888.currentText(),"zhengfan":zhengfan_box888.currentText(),"wangqi":wangqi_box888.currentText()}
            shuzu.append(dic333)
        if (checkbox999.isChecked() == True):
            dic333 = {"mingci": combo_box999.currentText(), "leixing": combo_box9999.currentText(),"zhengfan":zhengfan_box999.currentText(),"wangqi":wangqi_box999.currentText()}
            shuzu.append(dic333)
        if (checkbox101010.isChecked() == True):
            dic333 = {"mingci": combo_box101010.currentText(), "leixing": combo_box10101010.currentText(),"zhengfan":zhengfan_box101010.currentText(),"wangqi":wangqi_box101010.currentText()}
            shuzu.append(dic333)
        if (checkbox111111.isChecked() == True):
            dic333 = {"mingci": combo_box111111.currentText(), "leixing": combo_box11111111.currentText(),"zhengfan":zhengfan_box111111.currentText(),"wangqi":wangqi_box111111.currentText()}
            shuzu.append(dic333)
        if (checkbox121212.isChecked() == True):
            dic333 = {"mingci": combo_box121212.currentText(), "leixing": combo_box12121212.currentText(),"zhengfan":zhengfan_box121212.currentText(),"wangqi":wangqi_box121212.currentText()}
            shuzu.append(dic333)
        if (checkbox131313.isChecked() == True):
            dic333 = {"mingci": combo_box131313.currentText(), "leixing": combo_box13131313.currentText(),"zhengfan":zhengfan_box131313.currentText(),"wangqi":wangqi_box131313.currentText()}
            shuzu.append(dic333)
        if (checkbox141414.isChecked() == True):
            dic333 = {"mingci": combo_box141414.currentText(), "leixing": combo_box14141414.currentText(),"zhengfan":zhengfan_box141414.currentText(),"wangqi":wangqi_box141414.currentText()}
            shuzu.append(dic333)
        if (checkbox151515.isChecked() == True):
            dic333 = {"mingci": combo_box151515.currentText(), "leixing": combo_box15151515.currentText(),"zhengfan":zhengfan_box151515.currentText(),"wangqi":wangqi_box151515.currentText()}
            shuzu.append(dic333)
        if (checkbox161616.isChecked() == True):
            dic333 = {"mingci": combo_box161616.currentText(), "leixing": combo_box16161616.currentText(),"zhengfan":zhengfan_box161616.currentText(),"wangqi":wangqi_box161616.currentText()}
            shuzu.append(dic333)

        if (checkbox171717.isChecked() == True):
            dic333 = {"mingci": combo_box171717.currentText(), "leixing": combo_box17171717.currentText(),"zhengfan":zhengfan_box171717.currentText(),"wangqi":wangqi_box171717.currentText()}
            shuzu.append(dic333)
        if (checkbox181818.isChecked() == True):
            dic333 = {"mingci": combo_box181818.currentText(), "leixing": combo_box18181818.currentText(),"zhengfan":zhengfan_box181818.currentText(),"wangqi":wangqi_box181818.currentText()}
            shuzu.append(dic333)
        if (checkbox191919.isChecked() == True):
            dic333 = {"mingci": combo_box191919.currentText(), "leixing": combo_box19191919.currentText(),"zhengfan":zhengfan_box191919.currentText(),"wangqi":wangqi_box191919.currentText()}
            shuzu.append(dic333)
        if (checkbox202020.isChecked() == True):
            dic333 = {"mingci": combo_box202020.currentText(), "leixing": combo_box20202020.currentText(),"zhengfan":zhengfan_box202020.currentText(),"wangqi":wangqi_box202020.currentText()}
            shuzu.append(dic333)

        if (suijiluzi_diyizu_shuju_kuangjia.text() != ""):
            temp = {"diyizu":suijiluzi_diyizu_shuju_kuangjia.text()}
            suiji_luzi_shuzi.append(temp)
        if (suijiluzi_dierzu_shuju_kuangjia.text() != ""):
            temp = {"dierzu":suijiluzi_dierzu_shuju_kuangjia.text()}
            suiji_luzi_shuzi.append(temp)
        if (suijiluzi_disanzu_shuju_kuangjia.text() != ""):
            temp = {"disanzu":suijiluzi_disanzu_shuju_kuangjia.text()}
            suiji_luzi_shuzi.append(temp)
        if (suijiluzi_disizu_shuju_kuangjia.text() != ""):
            temp = {"disizu":suijiluzi_disizu_shuju_kuangjia.text()}
            suiji_luzi_shuzi.append(temp)
        if (suijiluzi_diwuzu_shuju_kuangjia.text() != ""):
            temp = {"diwuzu":suijiluzi_diwuzu_shuju_kuangjia.text()}
            suiji_luzi_shuzi.append(temp)

        for temp in shuzu:
            print(temp)
        print("开始执行脚本")
        print(file_textbox.text(),start_textbox_kami.text(),shuzu,file_textbox_tz_dizhi.text(),file_textbox_jiekou_dizhi.text(),"",touzhu_zhengfan.currentText(),suiji_luzi_shuzi)
        jingdong_daoxu_aozhou_feiting888_suiji.main_gui(file_textbox.text(),start_textbox_kami.text(),shuzu,file_textbox_tz_dizhi.text(),file_textbox_jiekou_dizhi.text(),"",touzhu_zhengfan.currentText(),suiji_luzi_shuzi)
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
window.setWindowTitle("模拟测试澳洲跟反往期")
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
label_file_jiekou_dizhi = QLabel("请输入澳洲模拟接口地址")
file_layout_jiekou_dizhi.addWidget(label_file_jiekou_dizhi)
path_jiekou_dizhi = get_value_by_key_pkl("jiekou_dizhi")
file_textbox_jiekou_dizhi = QLineEdit(path_jiekou_dizhi)
file_layout_jiekou_dizhi.addWidget(file_textbox_jiekou_dizhi)

# file_layout_jiekou_dizhi_feiting = QHBoxLayout()
# label_file_jiekou_dizhi_feiting = QLabel("请输入飞艇模拟接口地址")
# file_layout_jiekou_dizhi_feiting.addWidget(label_file_jiekou_dizhi_feiting)
# path_jiekou_dizhi_feiting = get_value_by_key_pkl("jiekou_dizhi_feiting")
# file_textbox_jiekou_dizhi_feiting = QLineEdit(path_jiekou_dizhi_feiting)
# file_layout_jiekou_dizhi_feiting.addWidget(file_textbox_jiekou_dizhi_feiting)

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
touzhu_zhengfan = QComboBox()
touzhu_zhengfan.addItems(["赢归位","赢继续"])
touzhu_zhengfan.setCurrentText(get_value_by_key_pkl("touzhu_zhengfan"))
extra_layout_kami.addWidget(touzhu_zhengfan)
#

luzi_zuiji_diwuzu = QHBoxLayout()
suijiluzi_diwuzu_mingzi = QLabel("随机路子第五组")
luzi_zuiji_diwuzu.addWidget(suijiluzi_diwuzu_mingzi)
suijiluzi_diwuzu_shuju = get_value_by_key_pkl("suijiluzi_diwuzu_shuju")
suijiluzi_diwuzu_shuju_kuangjia= QLineEdit(suijiluzi_diwuzu_shuju)
luzi_zuiji_diwuzu.addWidget(suijiluzi_diwuzu_shuju_kuangjia)

luzi_zuiji_disizu = QHBoxLayout()
suijiluzi_disizu_mingzi = QLabel("随机路子第四组")
luzi_zuiji_disizu.addWidget(suijiluzi_disizu_mingzi)
suijiluzi_disizu_shuju = get_value_by_key_pkl("suijiluzi_disizu_shuju")
suijiluzi_disizu_shuju_kuangjia= QLineEdit(suijiluzi_disizu_shuju)
luzi_zuiji_disizu.addWidget(suijiluzi_disizu_shuju_kuangjia)


luzi_zuiji_disanzu = QHBoxLayout()
suijiluzi_disanzu_mingzi = QLabel("随机路子第三组")
luzi_zuiji_disanzu.addWidget(suijiluzi_disanzu_mingzi)
suijiluzi_disanzu_shuju = get_value_by_key_pkl("suijiluzi_disanzu_shuju")
suijiluzi_disanzu_shuju_kuangjia= QLineEdit(suijiluzi_disanzu_shuju)
luzi_zuiji_disanzu.addWidget(suijiluzi_disanzu_shuju_kuangjia)

luzi_zuiji_dierzu = QHBoxLayout()
suijiluzi_dierzu_mingzi = QLabel("随机路子第二组")
luzi_zuiji_dierzu.addWidget(suijiluzi_dierzu_mingzi)
suijiluzi_dierzu_shuju = get_value_by_key_pkl("suijiluzi_dierzu_shuju")
suijiluzi_dierzu_shuju_kuangjia= QLineEdit(suijiluzi_dierzu_shuju)
luzi_zuiji_dierzu.addWidget(suijiluzi_dierzu_shuju_kuangjia)

luzi_zuiji_diyizu = QHBoxLayout()
suijiluzi_diyizu_mingzi = QLabel("随机路子第一组")
luzi_zuiji_diyizu.addWidget(suijiluzi_diyizu_mingzi)
suijiluzi_diyizu_shuju = get_value_by_key_pkl("suijiluzi_diyizu_shuju")
suijiluzi_diyizu_shuju_kuangjia= QLineEdit(suijiluzi_diyizu_shuju)
luzi_zuiji_diyizu.addWidget(suijiluzi_diyizu_shuju_kuangjia)


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
combo_box222.addItems(["1","2",  "3", "4", "5", "6", "7", "8", "9", "10"])
combo_box222.setCurrentText(get_value_by_key_pkl("guanya1"))
combo_box2222 = QComboBox()
combo_box2222.addItems(["大小","单双"])
combo_box2222.setCurrentText(get_value_by_key_pkl("daxiao1"))

zhengfan_box111 = QComboBox()
zhengfan_box111.addItems(["跟","反"])
zhengfan_box111.setCurrentText(get_value_by_key_pkl("zhengfan1"))

wangqi_box111 = QComboBox()
wangqi_box111.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box111.setCurrentText(get_value_by_key_pkl("wangqi1"))

checkbox222 = QCheckBox()
checkbox222.setChecked(True)
bottom_layout2.addWidget(combo_box222)
#bottom_layout2.addWidget(checkbox222)

#配置低一个投注策略的顺序
tzjine_first = get_value_by_key_pkl("celue1")
start_textbox_first= QLineEdit(tzjine_first)
#bottom_layout2.addWidget(start_textbox_first)
bottom_layout2.addWidget(combo_box2222)
# bottom_layout2.addWidget(zhengfan_box111)
# bottom_layout2.addWidget(wangqi_box111)
bottom_layout2.addWidget(checkbox222)


bottom_layout3 = QHBoxLayout()
label333 = QLabel("请输入第二名tz名次")
bottom_layout3.addWidget(label333)
combo_box333 = QComboBox()
combo_box333.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box333.setCurrentText(get_value_by_key_pkl("guanya2"))
combo_box3333 = QComboBox()
combo_box3333.addItems(["大小",  "单双"])
combo_box3333.setCurrentText(get_value_by_key_pkl("daxiao2"))
checkbox333 = QCheckBox()
checkbox333.setChecked(True)
bottom_layout3.addWidget(combo_box333)

zhengfan_box222 = QComboBox()
zhengfan_box222.addItems(["跟","反"])
zhengfan_box222.setCurrentText(get_value_by_key_pkl("zhengfan2"))

wangqi_box222 = QComboBox()
wangqi_box222.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box222.setCurrentText(get_value_by_key_pkl("wangqi2"))

#配置低一个投注策略的顺序
tzjine_secend = get_value_by_key_pkl("celue2")
start_textbox_secend= QLineEdit(tzjine_secend)
#bottom_layout3.addWidget(start_textbox_secend)
bottom_layout3.addWidget(combo_box3333)
# bottom_layout3.addWidget(zhengfan_box222)
# bottom_layout3.addWidget(wangqi_box222)
bottom_layout3.addWidget(checkbox333)

bottom_layout4 = QHBoxLayout()
label444 = QLabel("请输入第三名tz名次")
bottom_layout4.addWidget(label444)
combo_box444 = QComboBox()
combo_box444.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box444.setCurrentText(get_value_by_key_pkl("guanya3"))
combo_box4444 = QComboBox()
combo_box4444.addItems(["大小",  "单双"])
combo_box4444.setCurrentText(get_value_by_key_pkl("daxiao3"))
zhengfan_box333 = QComboBox()
zhengfan_box333.addItems(["跟","反"])
zhengfan_box333.setCurrentText(get_value_by_key_pkl("zhengfan3"))

wangqi_box333 = QComboBox()
wangqi_box333.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box333.setCurrentText(get_value_by_key_pkl("wangqi3"))

checkbox444 = QCheckBox()
checkbox444.setChecked(True)
bottom_layout4.addWidget(combo_box444)

tzjine_third = get_value_by_key_pkl("celue3")
start_textbox_third= QLineEdit(tzjine_third)
#bottom_layout4.addWidget(start_textbox_third)
bottom_layout4.addWidget(combo_box4444)
# bottom_layout4.addWidget(zhengfan_box333)
# bottom_layout4.addWidget(wangqi_box333)
bottom_layout4.addWidget(checkbox444)




bottom_layout5 = QHBoxLayout()
label555 = QLabel("请输入第四名tz名次")
bottom_layout5.addWidget(label555)
combo_box555 = QComboBox()
combo_box555.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box555.setCurrentText(get_value_by_key_pkl("guanya4"))

combo_box5555 = QComboBox()
combo_box5555.addItems(["大小",  "单双"])
combo_box5555.setCurrentText(get_value_by_key_pkl("daxiao4"))

checkbox555 = QCheckBox()
checkbox555.setChecked(True)
bottom_layout5.addWidget(combo_box555)
zhengfan_box444 = QComboBox()
zhengfan_box444.addItems(["跟","反"])
zhengfan_box444.setCurrentText(get_value_by_key_pkl("zhengfan4"))


wangqi_box444 = QComboBox()
wangqi_box444.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box444.setCurrentText(get_value_by_key_pkl("wangqi4"))

tzjine_four = get_value_by_key_pkl("celue4")
start_textbox_four= QLineEdit(tzjine_four)
#bottom_layout5.addWidget(start_textbox_four)
bottom_layout5.addWidget(combo_box5555)
# bottom_layout5.addWidget(zhengfan_box444)
# bottom_layout5.addWidget(wangqi_box444)
bottom_layout5.addWidget(checkbox555)


bottom_layout5_add_1 = QHBoxLayout()
label555_add_1 = QLabel("请输入第五名tz名次")
bottom_layout5_add_1.addWidget(label555_add_1)
combo_box555_add_1 = QComboBox()
combo_box555_add_1.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box555_add_1.setCurrentText(get_value_by_key_pkl("guanya5"))
combo_box5555_add_1 = QComboBox()

zhengfan_box555 = QComboBox()
zhengfan_box555.addItems(["跟","反"])
zhengfan_box555.setCurrentText(get_value_by_key_pkl("zhengfan5"))

wangqi_box555 = QComboBox()
wangqi_box555.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box555.setCurrentText(get_value_by_key_pkl("wangqi5"))


combo_box5555_add_1.addItems(["大小",  "单双"])
combo_box5555_add_1.setCurrentText(get_value_by_key_pkl("daxiao5"))
checkbox555_add_1 = QCheckBox()
checkbox555_add_1.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_five = get_value_by_key_pkl("celue5")
start_textbox_five= QLineEdit(tzjine_five)
bottom_layout5_add_1.addWidget(combo_box555_add_1)
bottom_layout5_add_1.addWidget(combo_box5555_add_1)
# bottom_layout5_add_1.addWidget(zhengfan_box555)
# bottom_layout5_add_1.addWidget(wangqi_box555)
bottom_layout5_add_1.addWidget(checkbox555_add_1)

bottom_layout6 = QHBoxLayout()
label666 = QLabel("请输入第六名tz名次")
bottom_layout6.addWidget(label666)
combo_box666 = QComboBox()
combo_box666.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box666.setCurrentText(get_value_by_key_pkl("guanya6"))
combo_box6666 = QComboBox()
combo_box6666.addItems(["大小",  "单双"])
combo_box6666.setCurrentText(get_value_by_key_pkl("daxiao6"))

zhengfan_box666 = QComboBox()
zhengfan_box666.addItems(["跟","反"])
zhengfan_box666.setCurrentText(get_value_by_key_pkl("zhengfan6"))

wangqi_box666 = QComboBox()
wangqi_box666.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box666.setCurrentText(get_value_by_key_pkl("wangqi6"))


checkbox666 = QCheckBox()
checkbox666.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_six = get_value_by_key_pkl("celue6")
start_textbox_six= QLineEdit(tzjine_six)
bottom_layout6.addWidget(combo_box666)
bottom_layout6.addWidget(combo_box6666)
# bottom_layout6.addWidget(zhengfan_box666)
# bottom_layout6.addWidget(wangqi_box666)
bottom_layout6.addWidget(checkbox666)

bottom_layout7 = QHBoxLayout()
label777 = QLabel("请输入第七名tz名次")
bottom_layout7.addWidget(label777)
combo_box777 = QComboBox()
combo_box777.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box7777 = QComboBox()
combo_box777.setCurrentText(get_value_by_key_pkl("guanya7"))

combo_box7777.addItems(["大小",  "单双"])
combo_box7777.setCurrentText(get_value_by_key_pkl("daxiao7"))
zhengfan_box777 = QComboBox()
zhengfan_box777.addItems(["跟","反"])
zhengfan_box777.setCurrentText(get_value_by_key_pkl("zhengfan7"))

wangqi_box777 = QComboBox()
wangqi_box777.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box777.setCurrentText(get_value_by_key_pkl("wangqi7"))


checkbox777 = QCheckBox()
checkbox777.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_seven = get_value_by_key_pkl("celue7")
start_textbox_seven= QLineEdit(tzjine_seven)
bottom_layout7.addWidget(combo_box777)
bottom_layout7.addWidget(combo_box7777)
# bottom_layout7.addWidget(zhengfan_box777)
# bottom_layout7.addWidget(wangqi_box777)
bottom_layout7.addWidget(checkbox777)

bottom_layout8 = QHBoxLayout()
label888 = QLabel("请输入第八名tz名次")
bottom_layout8.addWidget(label888)
combo_box888 = QComboBox()
combo_box888.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box8888 = QComboBox()
combo_box888.setCurrentText(get_value_by_key_pkl("guanya8"))

zhengfan_box888 = QComboBox()
zhengfan_box888.addItems(["跟","反"])
zhengfan_box888.setCurrentText(get_value_by_key_pkl("zhengfan8"))

wangqi_box888 = QComboBox()
wangqi_box888.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box888.setCurrentText(get_value_by_key_pkl("wangqi8"))


combo_box8888.addItems(["大小",  "单双"])
combo_box8888.setCurrentText(get_value_by_key_pkl("daxiao8"))

checkbox888 = QCheckBox()
checkbox888.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_aight = get_value_by_key_pkl("celue8")
start_textbox_aight= QLineEdit(tzjine_aight)
bottom_layout8.addWidget(combo_box888)
bottom_layout8.addWidget(combo_box8888)
# bottom_layout8.addWidget(zhengfan_box888)
# bottom_layout8.addWidget(wangqi_box888)
bottom_layout8.addWidget(checkbox888)

bottom_layout9 = QHBoxLayout()
label999 = QLabel("请输入第九名tz名次")
bottom_layout9.addWidget(label999)
combo_box999 = QComboBox()
combo_box999.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box999.setCurrentText(get_value_by_key_pkl("guanya9"))

combo_box9999 = QComboBox()
combo_box9999.addItems(["大小",  "单双"])
combo_box9999.setCurrentText(get_value_by_key_pkl("daxiao9"))
zhengfan_box999 = QComboBox()
zhengfan_box999.addItems(["跟","反"])
zhengfan_box999.setCurrentText(get_value_by_key_pkl("zhengfan9"))

wangqi_box999 = QComboBox()
wangqi_box999.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box999.setCurrentText(get_value_by_key_pkl("wangqi9"))


checkbox999 = QCheckBox()
checkbox999.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_nine = get_value_by_key_pkl("celue9")
start_textbox_nine= QLineEdit(tzjine_nine)
bottom_layout9.addWidget(combo_box999)
bottom_layout9.addWidget(combo_box9999)
# bottom_layout9.addWidget(zhengfan_box999)
# bottom_layout9.addWidget(wangqi_box999)
bottom_layout9.addWidget(checkbox999)

bottom_layout10 = QHBoxLayout()
label101010 = QLabel("请输入第十名tz名次")
bottom_layout10.addWidget(label101010)
combo_box101010 = QComboBox()
combo_box101010.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box101010.setCurrentText(get_value_by_key_pkl("guanya10"))

combo_box10101010 = QComboBox()
combo_box10101010.addItems(["大小",  "单双"])
combo_box10101010.setCurrentText(get_value_by_key_pkl("daxiao10"))
zhengfan_box101010 = QComboBox()
zhengfan_box101010.addItems(["跟","反"])
zhengfan_box101010.setCurrentText(get_value_by_key_pkl("zhengfan10"))

wangqi_box101010 = QComboBox()
wangqi_box101010.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box101010.setCurrentText(get_value_by_key_pkl("wangqi10"))


checkbox101010 = QCheckBox()
checkbox101010.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten = get_value_by_key_pkl("celue10")
start_textbox_ten= QLineEdit(tzjine_ten)
bottom_layout10.addWidget(combo_box101010)
bottom_layout10.addWidget(combo_box10101010)
# bottom_layout10.addWidget(zhengfan_box101010)
# bottom_layout10.addWidget(wangqi_box101010)
bottom_layout10.addWidget(checkbox101010)



bottom_layout11 = QHBoxLayout()
label111111 = QLabel("请输入第十一名tz名次")
bottom_layout11.addWidget(label111111)


combo_box111111 = QComboBox()
combo_box111111.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box111111.setCurrentText(get_value_by_key_pkl("guanya11"))

combo_box11111111 = QComboBox()
combo_box11111111.addItems(["大小",  "单双"])
combo_box11111111.setCurrentText(get_value_by_key_pkl("daxiao11"))

zhengfan_box111111 = QComboBox()
zhengfan_box111111.addItems(["跟","反"])
zhengfan_box111111.setCurrentText(get_value_by_key_pkl("zhengfan11"))

wangqi_box111111 = QComboBox()
wangqi_box111111.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box111111.setCurrentText(get_value_by_key_pkl("wangqi11"))


checkbox111111 = QCheckBox()
checkbox111111.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_1 = get_value_by_key_pkl("celue11")
start_textbox_ten_1= QLineEdit(tzjine_ten_1)
bottom_layout11.addWidget(combo_box111111)
bottom_layout11.addWidget(combo_box11111111)
# bottom_layout11.addWidget(zhengfan_box111111)
# bottom_layout11.addWidget(wangqi_box111111)
bottom_layout11.addWidget(checkbox111111)


bottom_layout12 = QHBoxLayout()
label121212 = QLabel("请输入第十二名tz名次")
bottom_layout12.addWidget(label121212)
combo_box12121212 = QComboBox()
combo_box12121212.addItems(["大小",  "单双"])

combo_box12121212.setCurrentText(get_value_by_key_pkl("daxiao12"))
combo_box121212 = QComboBox()
combo_box121212.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box121212.setCurrentText(get_value_by_key_pkl("guanya12"))

zhengfan_box121212 = QComboBox()
zhengfan_box121212.addItems(["跟","反"])
zhengfan_box121212.setCurrentText(get_value_by_key_pkl("zhengfan12"))

wangqi_box121212 = QComboBox()
wangqi_box121212.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box121212.setCurrentText(get_value_by_key_pkl("wangqi12"))


checkbox121212 = QCheckBox()
checkbox121212.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_2 = get_value_by_key_pkl("celue12")
start_textbox_ten_2= QLineEdit(tzjine_ten_2)
bottom_layout12.addWidget(combo_box121212)
bottom_layout12.addWidget(combo_box12121212)
# bottom_layout12.addWidget(zhengfan_box121212)
# bottom_layout12.addWidget(wangqi_box121212)
bottom_layout12.addWidget(checkbox121212)

bottom_layout13 = QHBoxLayout()
label131313 = QLabel("请输入第十三名tz名次")
bottom_layout13.addWidget(label131313)
combo_box13131313 = QComboBox()
combo_box13131313.addItems(["大小",  "单双"])
combo_box13131313.setCurrentText(get_value_by_key_pkl("daxiao13"))
combo_box131313 = QComboBox()
combo_box131313.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box131313.setCurrentText(get_value_by_key_pkl("guanya13"))

zhengfan_box131313 = QComboBox()
zhengfan_box131313.addItems(["跟","反"])
zhengfan_box131313.setCurrentText(get_value_by_key_pkl("zhengfan13"))

wangqi_box131313 = QComboBox()
wangqi_box131313.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box131313.setCurrentText(get_value_by_key_pkl("wangqi13"))


checkbox131313 = QCheckBox()
checkbox131313.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_3 = get_value_by_key_pkl("celue13")
start_textbox_ten_3= QLineEdit(tzjine_ten_3)
bottom_layout13.addWidget(combo_box131313)
bottom_layout13.addWidget(combo_box13131313)
# bottom_layout13.addWidget(zhengfan_box131313)
# bottom_layout13.addWidget(wangqi_box131313)
bottom_layout13.addWidget(checkbox131313)

bottom_layout14 = QHBoxLayout()
label141414 = QLabel("请输入第十四名tz名次")
bottom_layout14.addWidget(label141414)
combo_box14141414 = QComboBox()
combo_box14141414.addItems(["大小",  "单双"])
combo_box14141414.setCurrentText(get_value_by_key_pkl("daxiao14"))
combo_box141414 = QComboBox()
combo_box141414.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box141414.setCurrentText(get_value_by_key_pkl("guanya14"))

zhengfan_box141414 = QComboBox()
zhengfan_box141414.addItems(["跟","反"])
zhengfan_box141414.setCurrentText(get_value_by_key_pkl("zhengfan14"))

wangqi_box141414 = QComboBox()
wangqi_box141414.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box141414.setCurrentText(get_value_by_key_pkl("wangqi14"))


checkbox141414 = QCheckBox()
checkbox141414.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_4 = get_value_by_key_pkl("celue14")
start_textbox_ten_4= QLineEdit(tzjine_ten_4)
bottom_layout14.addWidget(combo_box141414)
bottom_layout14.addWidget(combo_box14141414)
# bottom_layout14.addWidget(zhengfan_box141414)
# bottom_layout14.addWidget(wangqi_box141414)
bottom_layout14.addWidget(checkbox141414)


bottom_layout15 = QHBoxLayout()
label151515 = QLabel("请输入第十五名tz名次")
bottom_layout15.addWidget(label151515)
combo_box15151515 = QComboBox()
combo_box15151515.addItems(["大小",  "单双"])
combo_box15151515.setCurrentText(get_value_by_key_pkl("daxiao15"))
combo_box151515 = QComboBox()
combo_box151515.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box151515.setCurrentText(get_value_by_key_pkl("guanya15"))

zhengfan_box151515 = QComboBox()
zhengfan_box151515.addItems(["跟","反"])
zhengfan_box151515.setCurrentText(get_value_by_key_pkl("zhengfan15"))

wangqi_box151515 = QComboBox()
wangqi_box151515.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box151515.setCurrentText(get_value_by_key_pkl("wangqi15"))


checkbox151515 = QCheckBox()
checkbox151515.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_5 = get_value_by_key_pkl("celue15")
start_textbox_ten_5= QLineEdit(tzjine_ten_5)
bottom_layout15.addWidget(combo_box151515)
bottom_layout15.addWidget(combo_box15151515)
# bottom_layout15.addWidget(zhengfan_box151515)
# bottom_layout15.addWidget(wangqi_box151515)
bottom_layout15.addWidget(checkbox151515)


bottom_layout16 = QHBoxLayout()
label161616 = QLabel("请输入第十六名tz名次")
bottom_layout16.addWidget(label161616)
combo_box16161616 = QComboBox()
combo_box16161616.addItems(["大小",  "单双"])
combo_box16161616.setCurrentText(get_value_by_key_pkl("daxiao16"))
combo_box161616 = QComboBox()
combo_box161616.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box161616.setCurrentText(get_value_by_key_pkl("guanya16"))

zhengfan_box161616 = QComboBox()
zhengfan_box161616.addItems(["跟","反"])
zhengfan_box161616.setCurrentText(get_value_by_key_pkl("zhengfan16"))

wangqi_box161616 = QComboBox()
wangqi_box161616.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box161616.setCurrentText(get_value_by_key_pkl("wangqi16"))


checkbox161616 = QCheckBox()
checkbox161616.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_6 = get_value_by_key_pkl("celue16")
start_textbox_ten_6= QLineEdit(tzjine_ten_6)
bottom_layout16.addWidget(combo_box161616)
bottom_layout16.addWidget(combo_box16161616)
# bottom_layout16.addWidget(zhengfan_box161616)
# bottom_layout16.addWidget(wangqi_box161616)
bottom_layout16.addWidget(checkbox161616)


bottom_layout17 = QHBoxLayout()
label171717 = QLabel("请输入第十七名tz名次")
bottom_layout17.addWidget(label171717)
combo_box17171717 = QComboBox()
combo_box17171717.addItems(["大小",  "单双"])
combo_box17171717.setCurrentText(get_value_by_key_pkl("daxiao17"))
combo_box171717 = QComboBox()
combo_box171717.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box171717.setCurrentText(get_value_by_key_pkl("guanya17"))

zhengfan_box171717 = QComboBox()
zhengfan_box171717.addItems(["跟","反"])
zhengfan_box171717.setCurrentText(get_value_by_key_pkl("zhengfan17"))

wangqi_box171717 = QComboBox()
wangqi_box171717.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box171717.setCurrentText(get_value_by_key_pkl("wangqi17"))

checkbox171717 = QCheckBox()
checkbox171717.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_7 = get_value_by_key_pkl("celue17")
start_textbox_ten_7= QLineEdit(tzjine_ten_7)
bottom_layout17.addWidget(combo_box171717)
bottom_layout17.addWidget(combo_box17171717)
# bottom_layout17.addWidget(zhengfan_box171717)
# bottom_layout17.addWidget(wangqi_box171717)
bottom_layout17.addWidget(checkbox171717)


bottom_layout18 = QHBoxLayout()
label181818 = QLabel("请输入第十八名tz名次")
bottom_layout18.addWidget(label181818)
combo_box18181818 = QComboBox()
combo_box18181818.addItems(["大小",  "单双"])
combo_box18181818.setCurrentText(get_value_by_key_pkl("daxiao18"))
combo_box181818 = QComboBox()
combo_box181818.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box181818.setCurrentText(get_value_by_key_pkl("guanya18"))

zhengfan_box181818 = QComboBox()
zhengfan_box181818.addItems(["跟","反"])
zhengfan_box181818.setCurrentText(get_value_by_key_pkl("zhengfan18"))

wangqi_box181818 = QComboBox()
wangqi_box181818.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box181818.setCurrentText(get_value_by_key_pkl("wangqi18"))


checkbox181818 = QCheckBox()
checkbox181818.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_8 = get_value_by_key_pkl("celue18")
start_textbox_ten_8= QLineEdit(tzjine_ten_8)
bottom_layout18.addWidget(combo_box181818)
bottom_layout18.addWidget(combo_box18181818)
# bottom_layout18.addWidget(zhengfan_box181818)
# bottom_layout18.addWidget(wangqi_box181818)
bottom_layout18.addWidget(checkbox181818)

bottom_layout19 = QHBoxLayout()
label191919 = QLabel("请输入第十九名tz名次")
bottom_layout19.addWidget(label191919)
combo_box19191919 = QComboBox()
combo_box19191919.addItems(["大小",  "单双"])
combo_box19191919.setCurrentText(get_value_by_key_pkl("daxiao19"))
combo_box191919 = QComboBox()
combo_box191919.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box191919.setCurrentText(get_value_by_key_pkl("guanya19"))

zhengfan_box191919 = QComboBox()
zhengfan_box191919.addItems(["跟","反"])
zhengfan_box191919.setCurrentText(get_value_by_key_pkl("zhengfan19"))

wangqi_box191919 = QComboBox()
wangqi_box191919.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box191919.setCurrentText(get_value_by_key_pkl("wangqi19"))


checkbox191919 = QCheckBox()
checkbox191919.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_9 = get_value_by_key_pkl("celue19")
start_textbox_ten_9= QLineEdit(tzjine_ten_9)
bottom_layout19.addWidget(combo_box191919)
bottom_layout19.addWidget(combo_box19191919)
# bottom_layout19.addWidget(zhengfan_box191919)
# bottom_layout19.addWidget(wangqi_box191919)
bottom_layout19.addWidget(checkbox191919)


bottom_layout20 = QHBoxLayout()
label202020 = QLabel("请输入第二十名tz名次")
bottom_layout20.addWidget(label202020)
combo_box20202020 = QComboBox()
combo_box20202020.addItems(["大小",  "单双"])
combo_box20202020.setCurrentText(get_value_by_key_pkl("daxiao20"))
combo_box202020 = QComboBox()
combo_box202020.addItems(["1",  "2", "3", "4", "5", "6", "7", "8", "9","10"])
combo_box202020.setCurrentText(get_value_by_key_pkl("guanya20"))

zhengfan_box202020 = QComboBox()
zhengfan_box202020.addItems(["跟","反"])
zhengfan_box202020.setCurrentText(get_value_by_key_pkl("zhengfan20"))

wangqi_box202020 = QComboBox()
wangqi_box202020.addItems(["1","2","3","4","5","6","7","8","9","10"])
wangqi_box202020.setCurrentText(get_value_by_key_pkl("wangqi20"))


checkbox202020 = QCheckBox()
checkbox202020.setChecked(True)
#bottom_layout5.addWidget(combo_box555)

tzjine_ten_10 = get_value_by_key_pkl("celue20")
start_textbox_ten_10= QLineEdit(tzjine_ten_10)
bottom_layout20.addWidget(combo_box202020)
bottom_layout20.addWidget(combo_box20202020)
# bottom_layout20.addWidget(zhengfan_box202020)
# bottom_layout20.addWidget(wangqi_box202020)
bottom_layout20.addWidget(checkbox202020)

 # 整体布局
layout = QVBoxLayout()
layout.addLayout(file_layout_jiekou_dizhi)
#layout.addLayout(file_layout_jiekou_dizhi_feiting)
layout.addLayout(file_layout_tz_dizhi)
layout.addLayout(extra_layout_kami)
layout.addLayout(file_layout)#luzi_zuiji
layout.addLayout(luzi_zuiji_diyizu)
layout.addLayout(luzi_zuiji_dierzu)
layout.addLayout(luzi_zuiji_disanzu)
layout.addLayout(luzi_zuiji_disizu)
layout.addLayout(luzi_zuiji_diwuzu)
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
    print("1")
    updata_pkl("firefoxpath",file_textbox.text())
    updata_pkl("tzjine", start_textbox_kami.text())
    updata_pkl("tz_dizhi", file_textbox_tz_dizhi.text())
    updata_pkl("jiekou_dizhi", file_textbox_jiekou_dizhi.text())
    print("1")
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
    updata_pkl("guanya11", combo_box111111.currentText())
    updata_pkl("guanya12", combo_box121212.currentText())
    updata_pkl("guanya13", combo_box131313.currentText())
    updata_pkl("guanya14", combo_box141414.currentText())
    updata_pkl("guanya15", combo_box151515.currentText())
    updata_pkl("guanya16", combo_box161616.currentText())
    updata_pkl("guanya17", combo_box171717.currentText())
    updata_pkl("guanya18", combo_box181818.currentText())
    updata_pkl("guanya19", combo_box191919.currentText())
    updata_pkl("guanya20", combo_box202020.currentText())
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
    print("1")
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
    print("1")
    # updata_pkl("zhengfan1", zhengfan_box111.currentText())
    # updata_pkl("zhengfan2", zhengfan_box222.currentText())
    # updata_pkl("zhengfan3", zhengfan_box333.currentText())
    # updata_pkl("zhengfan4", zhengfan_box444.currentText())
    # updata_pkl("zhengfan5", zhengfan_box555.currentText())
    # updata_pkl("zhengfan6", zhengfan_box666.currentText())
    # updata_pkl("zhengfan7", zhengfan_box777.currentText())
    # updata_pkl("zhengfan8", zhengfan_box888.currentText())
    # updata_pkl("zhengfan9", zhengfan_box999.currentText())
    # updata_pkl("zhengfan10", zhengfan_box101010.currentText())
    # updata_pkl("zhengfan11", zhengfan_box111111.currentText())
    # updata_pkl("zhengfan12", zhengfan_box121212.currentText())
    # updata_pkl("zhengfan13", zhengfan_box131313.currentText())
    # updata_pkl("zhengfan14", zhengfan_box141414.currentText())
    # updata_pkl("zhengfan15", zhengfan_box151515.currentText())
    # updata_pkl("zhengfan16", zhengfan_box161616.currentText())
    # updata_pkl("zhengfan17", zhengfan_box171717.currentText())
    # updata_pkl("zhengfan18", zhengfan_box181818.currentText())
    # updata_pkl("zhengfan19", zhengfan_box191919.currentText())
    # updata_pkl("zhengfan20", zhengfan_box202020.currentText())
    #
    # updata_pkl("wangqi1", wangqi_box111.currentText())
    # updata_pkl("wangqi2", wangqi_box222.currentText())
    # updata_pkl("wangqi3", wangqi_box333.currentText())
    # updata_pkl("wangqi4", wangqi_box444.currentText())
    # updata_pkl("wangqi5", wangqi_box555.currentText())
    # updata_pkl("wangqi6", wangqi_box666.currentText())
    # updata_pkl("wangqi7", wangqi_box777.currentText())
    # updata_pkl("wangqi8", wangqi_box888.currentText())
    # updata_pkl("wangqi9", wangqi_box999.currentText())
    # updata_pkl("wangqi10", wangqi_box101010.currentText())
    # updata_pkl("wangqi11", wangqi_box111111.currentText())
    # updata_pkl("wangqi12", wangqi_box121212.currentText())
    # updata_pkl("wangqi13", wangqi_box131313.currentText())
    # updata_pkl("wangqi14", wangqi_box141414.currentText())
    # updata_pkl("wangqi15", wangqi_box151515.currentText())
    # updata_pkl("wangqi16", wangqi_box161616.currentText())
    # updata_pkl("wangqi17", wangqi_box171717.currentText())
    # updata_pkl("wangqi18", wangqi_box181818.currentText())
    # updata_pkl("wangqi19", wangqi_box191919.currentText())
    # updata_pkl("wangqi20", wangqi_box202020.currentText())

    updata_pkl("suijiluzi_diyizu_shuju", suijiluzi_diyizu_shuju_kuangjia.text())
    updata_pkl("suijiluzi_dierzu_shuju", suijiluzi_dierzu_shuju_kuangjia.text())
    updata_pkl("suijiluzi_disanzu_shuju", suijiluzi_disanzu_shuju_kuangjia.text())
    updata_pkl("suijiluzi_disizu_shuju", suijiluzi_disizu_shuju_kuangjia.text())
    updata_pkl("suijiluzi_diwuzu_shuju", suijiluzi_diwuzu_shuju_kuangjia.text())
    print("1")
    updata_pkl("touzhu_zhengfan", touzhu_zhengfan.currentText())
    print("1")
    if(is_url_accessible(file_textbox_tz_dizhi.text())!=True):
        toast("模拟测试地址无法访问")
        print("模拟测试地址无法访问")
        #return
    if (is_url_accessible(file_textbox_jiekou_dizhi.text()) != True):
        toast("结果接口地址无法访问")
        print("结果接口地址无法访问")
        #return
    print("1")
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
