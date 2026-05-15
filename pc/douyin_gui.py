from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QFileDialog
import sys
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
import threading
import time
import os
import shutil
checked_options = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"]
def readFileByName(txt):
    file_path = "data.txt"  # 文件路径
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # 按行读取文件内容
            for line in lines:
                if(str(txt) in str(line)):
                    templist = line.split(":")
                    if(len(templist)==2):
                        return templist[1]
                    elif(len(templist)==3):
                        return str(templist[1])+":"+str(templist[2])
    except FileNotFoundError:
     print("文件不存在")
    except IOError:
     print("文件读取错误")
def run_script():
    import baijiahao
    # 在这里编写您的脚本代码
    print("开始执行脚本")
    try:
      print("开始执行脚本")
      save_to_file()
      baijiahao.main_baijiahao(checked_options)
    except BaseException as e:
        print(e)
def heart():
    while True:
        print("-----")
        time.sleep(1)
import os

def creat_file(filename):
    # 检查文件是否存在
    if not os.path.exists(filename):
        # 如果文件不存在，则创建它
        with open(filename, 'w') as file:
            file.write('')
    print(f'文件 {filename} 已经被创建或已经存在。')
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


def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return None
def on_checkbox_changed(state, idx):
    global checked_options
    if state == Qt.Checked:
        if f"{idx+1}" not in checked_options:
            checked_options.append(f"{idx+1}")
    else:
        if f"{idx+1}" in checked_options:
            checked_options.remove(f"{idx+1}")

    print(checked_options)
run_heart()
run_deleteFile()

file_zhanghao = "zhanghao.txt"
file_mima = "mima.txt"
file_ck_path = "ck.txt"
file_ck_config_path = "ck_config.txt"
file_baijiahao_nick = "nick.txt"
file_baijiahao_video_path = "video.txt"
file_baijiahao_title_path = "title.txt"
file_baijiahao_sleep_time = "sleep_time.txt"
file_zong_time = "zong_time.txt"

creat_file(file_zhanghao)
creat_file(file_mima)
creat_file(file_ck_path)
creat_file(file_ck_config_path)
creat_file(file_baijiahao_nick)
creat_file(file_baijiahao_sleep_time)
creat_file(file_baijiahao_video_path)
creat_file(file_baijiahao_title_path)
creat_file(file_zong_time)

app = QApplication([])
window = QWidget()
window.setWindowTitle("百家号")
button_layout = QHBoxLayout()
execute_button = QPushButton("执行")
button_layout.addWidget(execute_button)
# 任务之间休息时间设置
extra_layout = QHBoxLayout()
label11 = QLabel("任务之间休息时间设置(单位:s)")
extra_layout.addWidget(label11)
start_textbox1 = QLineEdit("30")
extra_layout.addWidget(start_textbox1)
extra_layout.addWidget(QLabel("到"))
end_textbox1 = QLineEdit("80")
extra_layout.addWidget(end_textbox1)
 # 文件选择布局

file_layout = QHBoxLayout()
label_file = QLabel("请选择CK exe")
file_layout.addWidget(label_file)
file_textbox = QLineEdit()
file_layout.addWidget(file_textbox)
ck_config_ui = read_txt_file(file_ck_path)
if((ck_config_ui != None)&(ck_config_ui != "")):
    file_textbox.setText(ck_config_ui)
file_button = QPushButton("选择文件")
file_layout.addWidget(file_button)


 # 选择ck 账号配置目录
file_layout_file = QHBoxLayout()
label_file_file = QLabel("请选择CK账号配置文件目录")
file_layout_file.addWidget(label_file_file)
file_textbox_file = QLineEdit()
file_layout_file.addWidget(file_textbox_file)
ck_config_2_ui = read_txt_file(file_ck_config_path)
if((ck_config_2_ui != None)&(ck_config_2_ui != "")):
    file_textbox_file.setText(ck_config_2_ui)
file_button_file = QPushButton("选择文件")
file_layout_file.addWidget(file_button_file)


mima_UI = read_txt_file(file_mima)
 # 选择ck 用户昵称
file_layout_nick = QHBoxLayout()
label_file_nick = QLabel("请选择百家号用户昵称配置文件")
file_layout_nick.addWidget(label_file_nick)
file_textbox_nick = QLineEdit()
file_layout_nick.addWidget(file_textbox_nick)
ck_nick_ui = read_txt_file(file_baijiahao_nick)
if((ck_nick_ui != None)&(ck_nick_ui != "")):
    file_textbox_nick.setText(ck_nick_ui)
file_button_nick = QPushButton("选择文件")
file_layout_nick.addWidget(file_button_nick)

# 选择ck 视频文件
file_layout_video = QHBoxLayout()
label_file_video = QLabel("请选择百家号视频文件配置目录")
file_layout_video.addWidget(label_file_video)
file_textbox_video = QLineEdit()
file_layout_video.addWidget(file_textbox_video)
ck_video_ui = read_txt_file(file_baijiahao_video_path)
if((ck_video_ui != None)&(ck_video_ui != "")):
    file_textbox_video.setText(ck_video_ui)
file_button_video = QPushButton("选择文件")
file_layout_video.addWidget(file_button_video)

# 选择ck 视频文件
file_layout_title = QHBoxLayout()
label_file_title = QLabel("请选择百家号视频标题配置文件")
file_layout_title.addWidget(label_file_title)
file_textbox_title = QLineEdit()
file_layout_title.addWidget(file_textbox_title)
ck_title_ui = read_txt_file(file_baijiahao_title_path)
if((ck_title_ui != None)&(ck_title_ui != "")):
    file_textbox_title.setText(ck_title_ui)
file_button_title = QPushButton("选择文件")
file_layout_title.addWidget(file_button_title)

#取消关注一次取消关注的个数
 # 账号
extra_layout_account = QHBoxLayout()
labelc_account = QLabel("请输入账号")
extra_layout_account.addWidget(labelc_account)
start_textbox_account= QLineEdit("")

ck_account_ui = read_txt_file(file_zhanghao)
if((ck_account_ui != None)&(ck_account_ui != "")):
    start_textbox_account.setText(ck_account_ui)

extra_layout_account.addWidget(start_textbox_account)

 # 账号
extra_layout_secret = QHBoxLayout()
labelc_account_secret = QLabel("请输入密码")
extra_layout_secret.addWidget(labelc_account_secret)
start_textbox_secret= QLineEdit("")

ck_mima_ui = read_txt_file(file_mima)
if((ck_mima_ui != None)&(ck_mima_ui != "")):
    start_textbox_secret.setText(ck_mima_ui)

extra_layout_secret.addWidget(start_textbox_secret)
 # 运行时间配置
extra_layout_time = QHBoxLayout()
labelc_account_time = QLabel("运行总时长配置(单位:分钟)")
extra_layout_time.addWidget(labelc_account_time)
start_textbox_time= QLineEdit("2000")
ck_zong_time_ui = read_txt_file(file_zong_time)
if((ck_zong_time_ui != None)&(ck_zong_time_ui != "")):
    start_textbox_time.setText(ck_zong_time_ui)
extra_layout_time.addWidget(start_textbox_time)

checkbox_container = QWidget()
checkbox_layout = QVBoxLayout(checkbox_container)

# 初始化复选框并添加到容器中，默认为勾选
for i in range(4):  # 四行
    row_layout = QHBoxLayout()
    for j in range(6):  # 每行六个复选框
        checkbox_index = i * 6 + j  # 计算复选框的索引
        checkbox = QCheckBox(f" {checkbox_index + 1}"+"点")
        checkbox.setChecked(True)  # 默认勾选
        checkbox.stateChanged.connect(lambda state, idx=checkbox_index: on_checkbox_changed(state, idx))
        row_layout.addWidget(checkbox)
    checkbox_layout.addLayout(row_layout)  # 将每行的水平布局添加到垂直布局中

 # 整体布局
layout = QVBoxLayout()
layout.addLayout(extra_layout_account)
layout.addLayout(extra_layout_secret)
layout.addLayout(file_layout)
layout.addLayout(file_layout_file)
layout.addLayout(file_layout_nick)
layout.addLayout(file_layout_video)
layout.addLayout(file_layout_title)
layout.addLayout(extra_layout)
layout.addLayout(extra_layout_time)
layout.addWidget(checkbox_container)
layout.addLayout(button_layout)


window.setLayout(layout)
window.show()
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

    if(check_connected_android_devices() != True):
        print("当前没有手机连接")
        toast("当前没有手机连接")
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
    with open(file_zhanghao, "w", encoding="utf-8") as file:
        file.write(start_textbox_account.text())
    with open(file_mima, "w", encoding="utf-8") as file:
        file.write(start_textbox_secret.text())
    with open(file_ck_path, "w", encoding="utf-8") as file:
        file.write(file_textbox.text())
    with open(file_ck_config_path, "w", encoding="utf-8") as file:
        file.write(file_textbox_file.text())
    with open(file_baijiahao_nick, "w", encoding="utf-8") as file:
        file.write(file_textbox_nick.text())
    with open(file_baijiahao_title_path, "w", encoding="utf-8") as file:
        file.write(file_textbox_title.text())
    with open(file_baijiahao_sleep_time, "w", encoding="utf-8") as file:
        file.write(start_textbox1.text()+"-"+end_textbox1.text())
    with open(file_baijiahao_video_path, "w", encoding="utf-8") as file:
        file.write(file_textbox_video.text())
    with open(file_zong_time, "w", encoding="utf-8") as file:
        file.write(start_textbox_time.text())


def on_file_button_clicked():
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        file_names = file_dialog.selectedFiles()
        file_textbox.setText(file_names[0])
def on_file_button_clicked_file():
    print("选择2")
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        file_names = file_dialog.selectedFiles()
        file_textbox_file.setText(file_names[0])

def toast(tishi):
    import win32con
    import ctypes
    ctypes.windll.user32.MessageBoxTimeoutW(0, f'{tishi}\n', '提示', win32con.MB_YESNO, 0, 3000)
def on_file_button_clicked_folder():
    folder_dialog = QFileDialog()
    folder_dialog.setFileMode(QFileDialog.Directory)
    folder_dialog.setOption(QFileDialog.ShowDirsOnly)  # 只显示文件夹
    if folder_dialog.exec_():
        folder_selected = folder_dialog.selectedFiles()[0]  # 获取选中的文件夹路径
        file_textbox_video.setText(QDir.toNativeSeparators(folder_selected))  # 设置到 QLineEdit 中，并转换为本地路径分隔符
def check_connected_android_devices():
    import subprocess
    # 调用adb devices命令并获取输出
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # 如果命令执行失败（例如adb未安装或未找到设备），则返回False
    if result.returncode != 0:
        return False

        # 移除输出中的表头（如果有的话）
    output = result.stdout.strip().split('\n')[1:]

    # 计数连接的设备数量
    device_count = 0
    for line in output:
        # adb devices的输出通常格式是：<设备ID>\t<设备状态>
        # 如果状态是device，则它是一个连接的设备
        if line and 'device' in line.split('\t')[1]:
            device_count += 1

            # 如果有且仅有一个设备连接，则返回True，否则返回False
    return device_count == 1

def on_file_button_clicked_nick():
    print("xuanze")
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        file_names = file_dialog.selectedFiles()
        file_textbox_nick.setText(file_names[0])
def on_file_button_clicked_title():
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    if file_dialog.exec_():
        file_names = file_dialog.selectedFiles()
        file_textbox_title.setText(file_names[0])
file_button.clicked.connect(on_file_button_clicked)
file_button_file.clicked.connect(on_file_button_clicked_file)
file_button_video.clicked.connect(on_file_button_clicked_folder)
file_button_title.clicked.connect(on_file_button_clicked_title)
file_button_nick.clicked.connect(on_file_button_clicked_nick)
execute_button.clicked.connect(on_button_clicked)
sys.exit(app.exec_())