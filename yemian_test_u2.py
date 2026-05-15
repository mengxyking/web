import shutil
import sys
import threading
import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer
import os
import pickle
current_scroll_position = 0
import time
def get_device(serial):
    #d = ""
    #print("之前的d", d)
    print(f"正在连接设备: {serial}")
    d = u2.connect(serial)
    d.watcher.remove()
    return d
def operate_device(serial):
    # d = ""
    # print("之前的d",d)
    # print(f"正在连接设备: {serial}")
    d = get_device(serial)
    print("之后的的", d)
    print("----------------------")
    print(get_value_by_key_pkl("./shuju/"+serial+".pkl","执行状态"))
    if(str(get_value_by_key_pkl("./shuju/"+serial+".pkl","执行状态")) != "运行中"):
        print("结束了。。。")
        d.watcher.remove()
        d.stop_uiautomator(True)

        return
    # 创建线程列表
    # 常用写法，注册匿名监控
    while(True):
        # d.watcher("休眠").when("高级").click()
        # d.watcher("ANR").when(xpath="ANR").when("Force Close").click()
        # d.watcher("显示").when("显示").click()
        # # 其他回调例子
        # d.watcher.when("休眠").press("back")
        # d.watcher.when("屏保").press("back")
        # d.watcher.when("//*[@text = 'Out of memory']").call(lambda d: d.shell('am force-stop com.im.qq'))
        # # d.xpath("继续").click()  # 使用d.xpath检查元素的时候，会触发watcher（目前最多触发5次）
        # d.watcher.start()
        if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
            print("结束了。。。")
            d.watcher.remove()
            d.stop_uiautomator(True)
            break

            # 注册名为ANR的监控，当出现ANR和Force Close时，点击Force Close


        if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
            print("结束了。。。")
            d.watcher.remove()
            d.stop_uiautomator(False)
            break


        # 开始后台监控
        # 打开微信应用
        wechat = d(text="设置")

        if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
            print("结束了。。。")
            d.watcher.remove()
            d.stop_uiautomator(True)
            break

            # wechat = d(path="设置")
        if wechat.exists(timeout=0):  # 使用exists来检查元素是否存在，无需再次wait
            wechat.click()
        time.sleep(2)
        if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
            print("结束了。。。")
            d.watcher.remove()
            d.stop_uiautomator(True)
            break
            # 等待微信主界面加载（这里使用简单的sleep）
        # 点击“订阅号”（假设它在微信的主界面上）
        subscribe = d(text="显示")
        if subscribe.exists(timeout=3):
            subscribe.click()
        time.sleep(3)
        if (get_value_by_key_pkl("./shuju/" + serial + ".pkl", "执行状态") != "运行中"):
            print("结束了。。。")
            d.watcher.remove()
            d.stop_uiautomator(True)
            break
        d.press("back")
        time.sleep(3)


class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 PKL 文件查看器")
        self.setGeometry(100, 100, 850, 300)
        #layout = QVBoxLayout()
        self.titleLabel = QLabel("这里是小标题")
        self.titleLabel.setStyleSheet("""  
            QLabel {  
                font-size: 14px; /* 字体大小 */  
                font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                padding: 10px; /* 内边距 */  
                background-color: #f0f0f0; /* 背景色 */  
                color: #333; /* 文本颜色 */  
               
            }  
        """)
        self.titleLabel_renwu = QLabel("这里是renwu标题")
        self.titleLabel_renwu.setStyleSheet("""  
                    QLabel {  
                        font-size: 14px; /* 字体大小 */  
                        font-family: "Arial", sans-serif; /* 字体家族，使用Arial或系统默认的无衬线字体 */  
                        padding: 10px; /* 内边距 */  
                        background-color: #f0f0f0; /* 背景色 */  
                        color: #333; /* 文本颜色 */  

                    }  
                """)

        # Table widget to display pkl file information
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(9)  # Increase column count for checkboxes
        self.table_widget.setHorizontalHeaderLabels(['选中', '编号', '昵称','连接状态', '运行状态','Age', 'Address','当前任务',"操作"])
        self.table_widget.setColumnWidth(0,30)
        self.table_widget.setShowGrid(True)

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.table_widget)
        self.scroll_area.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area.setFixedHeight(200)  # Set fixed height for the scroll area
        self.scroll_area.setFixedWidth(800)
        #self.scroll_area.verticalScrollBar().setValue(3)
        #self.scroll_area

        #以下是内容相关的列表
        self.renwu_widget = QTableWidget(self)
        self.renwu_widget.setColumnCount(9)  # Increase column count for checkboxes
        self.renwu_widget.setHorizontalHeaderLabels(
            ['id', 'UID/抖音号', '私信', '关注', '留痕', '点赞', '头像点赞', '视频评论', "评论区艾特","任务状态"])
        self.renwu_widget.setColumnWidth(0, 30)
        self.renwu_widget.setShowGrid(True)

        # Scroll area
        self.scroll_area_renwu = QScrollArea(self)
        self.scroll_area_renwu.setWidget(self.renwu_widget)
        self.scroll_area_renwu.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area_renwu.setFixedHeight(200)  # Set fixed height for the scroll area
        self.scroll_area_renwu.setFixedWidth(600)
        # self.scroll_area.verticalScrollBar().setValue(3)
        # self.scroll_area



        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)  # 设置布局间距为0
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.titleLabel_renwu)
        layout.addWidget(self.scroll_area_renwu)

        # Variable to store the selected IDs
        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pkl_files)
        self.timer.start(30000)
        # Initial load
        self.refresh_pkl_files()
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("执行")
        self.execute_button.resize(100,30)
        self.button_gang.addWidget(self.execute_button)

        self.execute_button_delete = QPushButton("删除")
        self.execute_button_delete.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_delete)

        self.execute_button_reset = QPushButton("重置")
        self.execute_button_reset.resize(100, 30)
        self.button_gang.addWidget(self.execute_button_reset)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        self.execute_button_reset.clicked.connect(self.execute_reset_button_clicked)
        self.execute_button_delete.clicked.connect(self.execute_delete_button_clicked)
        layout.addLayout(self.button_gang)
        #layout.addWidget(self.execute_button_reset)
    def execute_button_clicked(self):
        print("---------------")
        if(self.selected_ids == []):
            toast("请选择机型")
            return
        for temp in self.selected_ids:
            print(temp)
            updata_pkl("./shuju/"+temp+".pkl","执行状态","运行中")
            updata_pkl("./shuju/" + temp + ".pkl", "进行的任务", "抖音")
        #self.scroll_area.widget().layout().item_list()[0].widget()

        self.refresh_pkl_files()
        #self.scroll_area.ensureWidgetVisible(100)


        for serial in self.selected_ids:
            thread = threading.Thread(target=operate_device, args=(serial,))
            #threads.append(thread)
            thread.start()

        self.selected_ids = []

    def execute_delete_button_clicked(self):
        print("---------------")
        if(self.selected_ids == []):
            toast("请选择删除的机型")
            return
        for temp in self.selected_ids:
            print(temp)
            if(os.path.isfile("./shuju/" + temp + ".pkl")):
                os.remove("./shuju/" + temp + ".pkl")
        self.refresh_pkl_files()
        self.selected_ids = []

    def execute_reset_button_clicked(self):
        print("execute_reset_button_clicked")
        directory = './shuju'
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                filepath = os.path.join(directory, filename)
                updata_pkl(filepath, "执行状态", "运行结束")
                updata_pkl(filepath, "进行的任务", "空闲")
        self.refresh_pkl_files()
    def refresh_pkl_files(self):
        # 保存当前滚动位置
        current_pos = self.table_widget.verticalScrollBar().value()

        print("current_scroll_position",current_scroll_position)
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
                            item_i = QTableWidgetItem(data.get('name', 'N/A'))
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

                            item_zhuangage = QTableWidgetItem(data.get('age', 'N/A'))
                            item_zhuangage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 5, item_zhuangage)

                            item_add = QTableWidgetItem(data.get('add', 'N/A'))
                            item_add.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 6, item_add)

                            item_renwu = QTableWidgetItem(data.get('进行的任务', 'N/A'))
                            item_renwu.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table_widget.setItem(row_index, 7, item_renwu)

                            button111 = QPushButton("编辑")
                            button111.clicked.connect(lambda: print("Button clicked!"))
                            self.table_widget.setItem(row_index, 8,button111)

                            row_index += 1
                except Exception as e:
                    print(f"读取文件 {filepath} 时出错: {e}")
         # 恢复滚动位置
        self.table_widget.verticalScrollBar().setSliderPosition(current_pos)

    def update_selected_ids(self, state, row):
        # 更新选中的编号
        item_id = self.table_widget.item(row, 1).text()  # 获取编号
        if item_id not in self.selected_ids:
            self.selected_ids.append(item_id)  # 添加到选中的编号
        else:
            if item_id in self.selected_ids:
                self.selected_ids.remove(item_id)  # 从选中的编号中移除
        # 打印当前选中的编号
        print("当前选中的编号:", self.selected_ids)
def pkl_add(pkl,dic):

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
    print("")
# 反序列化对象

def pkl_list(pklfile):
    with open(pklfile, 'rb') as pkl_file:
        my_object111 = pickle.load(pkl_file)
        return my_object111
#import pickle

# 修改Python对象
#my_object['age'] = 31

# 重新序列化对象
def get_value_by_key_pkl(pklfile,key):
    dic = {}
    with open(pklfile, 'rb') as pkl_file:
        dic = pickle.load(pkl_file)
    #dic.pop(key)
    print("0000000000000")
    print(dic)
    print(key)
    print(key in dic)
    if key in dic:
        print("zailimian")
        return dic[key]
def updata_pkl(pklfile,key,value):
    dic = {}
    if(os.path.isfile(pklfile)):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)
        dic[key] = value
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)
import subprocess
import time
def get_connected_devices():
    # Run the adb devices command
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)

    connected_devices = []
    for device in devices:
        if device.strip():
            device_info = device.split('\t')
            connected_devices.append((device_info[0], device_info[1]))  # (device_id, status)

    return connected_devices


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
            print(f"Device connected: {device_id}")
            dic = {"name":device_id,"连接状态":"已连接","执行状态":"空闲中","age":"1811","add":"bj1","xingbie":"nan","进行的任务":"空闲"}
            pkl_add("./shuju/"+device_id+".pkl",dic)
        # Check for disconnections
        disconnected_devices = known_devices - current_device_ids
        for device_id in disconnected_devices:
            print(f"Device disconnected: {device_id}")
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

if __name__ == "__main__":
    thread = threading.Thread(target=monitor_devices)
    thread.start()
    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())