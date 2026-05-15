import cv2
import shutil
import sys
import threading
import random
import glob
import uiautomator2 as u2

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QScrollArea, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QPushButton, QLabel, QRadioButton, QLineEdit,
    QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QDir
import os
import pickle
current_scroll_position = 0
import time
total_dict = {}
alldata = ""
file_lock = threading.Lock()
video_lock = threading.Lock()


def empty_folder(folder_path):
    """
    清空指定文件夹里的所有内容和子文件夹。

    :param folder_path: 要清空的文件夹路径
    """
    # 检查文件夹是否存在
    if os.path.exists(folder_path):
        # 遍历文件夹中的所有文件和子文件夹
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # 如果它是一个文件，则删除它
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # 删除文件或链接
                # 如果它是一个文件夹，则递归地删除它的内容，然后删除它本身
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # 递归地删除文件夹及其内容
            except Exception as e:
                print(f"无法删除 {file_path}。错误: {e}")
    else:
        print(f"文件夹 {folder_path} 不存在。")
def create_file_if_not_exists_2(file_path,content):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            # 这里可以写入一些初始内容（可选）
            file.write(str(content))
        print(f"文件 '{file_path}' 已创建。")
    else:
        print(f"文件 '{file_path}' 已经存在。")
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
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    #print("00000000000000000000000000---------")
    #print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path


def list_files_in_directory(directory_path):
    # 获取目录中的所有条目（文件和子目录）
    entries = os.listdir(directory_path)
    print("entries--",entries)
    # 创建一个空列表来存储文件
    files = []
    # 遍历每个条目，并检查它是否是一个文件
    for entry in entries:
        # 使用 os.path.join 来构建完整的文件路径
        full_path = os.path.join(directory_path, entry)

        # 检查该路径是否是一个文件
        if os.path.isfile(full_path):
            files.append(entry)  # 如果是文件，则添加到列表中

    return files


def list_files_in_directory_pic(directory_path):
    # 获取目录中的所有条目（文件和子目录）
    entries = os.listdir(directory_path)
    print("entries--", entries)

    # 创建一个空列表来存储文件
    files = []

    # 遍历每个条目，并检查它是否是一个文件以及是否具有所需的后缀
    for entry in entries:
        # 使用 os.path.join 来构建完整的文件路径
        full_path = os.path.join(directory_path, entry)

        # 检查该路径是否是一个文件以及是否具有 .jpg 或 .png 后缀
        if os.path.isfile(full_path) and (entry.lower().endswith('.jpg') or entry.lower().endswith('.png')):
            files.append(entry)  # 如果是文件且后缀正确，则添加到列表中

    return files
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


def create_file_if_not_exists(file_path):
    if not os.path.isfile(file_path):
        # 如果文件不存在，则创建它（这里只是创建一个空文件）
        with open(file_path, 'w') as file:
            file.write('')  # 或者你可以写入一些初始内容
        print(f"File '{file_path}' created.")



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

def shell_neibu(cmd):
    os.system(cmd)

def load_pkl(pklfile):
    with video_lock:
        if(os.path.exists(pklfile)):
            with open(pklfile, 'rb') as pkl_file:
                my_object111 = pickle.load(pkl_file)
                return my_object111
        else:
            return None
import requests
def upload(image_path,fuwuqi):
    upload_url = fuwuqi
    with open(image_path, 'rb') as image_file:
        files = {'file': (os.path.basename(image_path), image_file)}  # 注意：这里不需要指定MIME类型，requests会自动处理
        response = requests.post(upload_url, files=files)
        return response
def get_result(YOUR_API_KEY,YOUR_TASK_ID):
    # API请求的URL
    url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{YOUR_TASK_ID}'

    # 设置请求头部
    headers = {
        'Authorization': f'Bearer {YOUR_API_KEY}'
    }
    # 发送GET请求
    response = requests.get(url, headers=headers)
    # 处理响应
    if response.status_code == 200:
        # 请求成功，打印响应内容（假设服务器返回JSON格式的数据）
        response_data = response.json()
        print('请求成功，响应内容：', response_data)
        return response.status_code,response_data
    else:
        # 请求失败，打印错误信息
        print(f'请求失败，状态码：{response.status_code}，响应内容：{response.text}')
        return response.status_code, response.text
def post_image(key,url_image,temlate_id):
    DASHSCOPE_API_KEY = key
    print("DASHSCOPE_API_KEY---",DASHSCOPE_API_KEY)

    # API请求的URL
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/'

    # 要发送的JSON数据
    data = {
        "model": "animate-anyone-gen2",
        "input": {
            "image_url": url_image,
            "template_id": temlate_id
        },
        "parameters": {
            "use_ref_img_bg": True,
            "video_ratio": "9:16"
        }
    }

    # 设置请求头部
    headers = {
        'X-DashScope-Async': 'enable',
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 处理响应
    if response.status_code == 200:
        # 请求成功，打印响应内容（假设服务器返回JSON格式的数据）
        response_data = response.json()
        print('请求成功，响应内容：', response_data)
        return response.status_code,response_data
    else:
        # 请求失败，打印错误信息
        print(f'请求失败，状态码：{response.status_code}，响应内容：{response.text}')
        return response.status_code,response.text
import random
def download_video(video_url,save_path,file_name):
    # 视频下载地址
    video_url = video_url
    # 本地保存路径和文件名
    save_folder = save_path  # 替换为您想要保存的文件夹路径
    save_filename = str(file_name)+"_"+str(time.time())+'.mp4'  # 您可以根据需要更改文件名

    # 确保保存文件夹存在
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 完整的保存路径
    save_path = os.path.join(save_folder, save_filename)

    # 发送HTTP GET请求下载视频
    response = requests.get(video_url, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"视频已成功保存到 {save_path}")
        return 1
    else:
        print(f"下载失败，状态码：{response.status_code}")
        return 0
import json
def process_file(file_path,file_name,task,apikey,fuwuqi,save_path):
    key = apikey
    # 在这里添加处理文件的代码
    #第一步先把图片上传到服务器
    files_image_path = get_value_by_key_pkl(file_path,"file_path")
    result = upload(files_image_path,fuwuqi)

    print("result========",result)
    print(result.status_code)
    print(result.text)

    if(result.status_code == 201):
        print("上传服务器成功")
        updata_pkl(file_path,"zhuangtai","上传至服务器成功")
    else:
        print("上传服务器失败")
        updata_pkl(file_path, "zhuangtai", "上传服务器失败")
        return
    data = json.loads(result.text)
    file_url = data['file_url']
    updata_pkl(file_path, "zhuangtai", "获取图片地址成功")

    length_temp = len(task)
    count_big = 0
    updata_pkl(file_path, "beizhu", f"一共{str(length_temp)}个模板")
    while(count_big < length_temp):
        print("task[count_big]------------>",task[count_big])
        count_bb = 0
        txt = {}
        while (count_bb < 8):
            code, txt = post_image(key, file_url,
                                   task[count_big])
            print("code,txt=", code, txt)
            if (code == 200):
                updata_pkl(file_path, "zhuangtai", f"视频排队中,{count_big+1}")
                break
            else:
                updata_pkl(file_path, "zhuangtai", f"视频生成失败，重试中,{count_big+1}")
                time.sleep(10)
            if (count_bb > 6):
                updata_pkl(file_path, "zhuangtai", f"视频生成失败，重试好几次也不行，失败,{count_big+1}")
                return
            count_bb += 1
        print("txt====", txt)
        # data = json.loads(txt)
        task_id = txt["output"]["task_id"]
        print("task_id=", task_id)
        count_small = 0
        while (count_small < 200):
            code, result_txt = get_result(key, task_id)
            print("code,result_txt=", code, result_txt)
            if (code == 200):
                task_status = result_txt["output"]["task_status"]
                if (task_status == "PENDING"):
                    updata_pkl(file_path, "zhuangtai", f"视频排队中中,{count_big+1}")
                if (task_status == "PRE-PROCESSING"):
                    updata_pkl(file_path, "zhuangtai", f"视频前置处理中,{count_big+1}")
                if (task_status == "RUNNING"):
                    print("视频处理中")
                    updata_pkl(file_path, "zhuangtai", f"视频处理中,{count_big+1}")
                if (task_status == "POST-PROCESSING"):
                    updata_pkl(file_path, "zhuangtai", f"视频后置处理中,{count_big+1}")
                if (task_status == "FAILED"):
                    updata_pkl(file_path, "zhuangtai", f"视频处理失败,{count_big+1}")
                    return
                if (task_status == "UNKNOWN"):
                    updata_pkl(file_path, "zhuangtai", f"未知状态,{count_big+1}")
                if (task_status == "SUCCEEDED"):
                    updata_pkl(file_path, "zhuangtai", f"视频处理成功,{count_big+1}")

                    video_url = result_txt["output"]["video_url"]
                    result_aa = download_video(video_url, save_path,str(file_name).split(".")[0])
                    if (result_aa == 1):
                        updata_pkl(file_path, "zhuangtai", f"视频下载保存成功,{count_big+1}")
                    else:
                        updata_pkl(file_path, "zhuangtai", f"视频下载失败,{count_big+1}")
                    break
            time.sleep(30)
            count_small += 1
        count_big+=1



    # 例如，您可以打开文件、读取内容、进行处理等
def operate_device(dir_path,task,api_key,fuwuqi,save_path):
    #第一步 先把图片上传到服务器
    files = list_files_in_directory(dir_path)
    print("files---",files)
    threads = []
    for file_name in files:
        file_path = os.path.join(dir_path, file_name)
        thread = threading.Thread(target=process_file, args=(file_path,file_name,task,api_key,fuwuqi,save_path))
        threads.append(thread)
        # 启动线程
        thread.start()
        time.sleep(5)

    # 等待所有线程完成（可选，但通常推荐）
    for thread in threads:
        thread.join()



class PklViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("阿里百炼api辅助工具")
        self.setGeometry(100, 100, 500, 300)
        #layout = QVBoxLayout()
        self.titleLabel = QLabel("*"*40+"手机列表"+"*"*40)
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
        self.titleLabel_renwu = QLabel("*"*40+"运行进度"+"*"*40)
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
        self.caozuo_tiel = QLabel("*"*40+"请选择模板"+"*"*40)
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
        self.caozuo_config = QLabel("*" * 40 + "脚本配置" + "*" * 40)
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



        # Scroll area
        self.horizontal_layout = QHBoxLayout()
        self.radio_button0 = QLabel("           ")
        # self.radio_button_select = QPushButton("全选")
        #
        # self.radio_button_dingshi = QPushButton("定时重启app")
        self.checkboxes = {}
        config_file = 'config.txt'
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    # 分割 'name-模版id'，只取 'name' 部分
                    name, template_id = line.strip().split(':')
                    check_box = QCheckBox(name)
                    check_box.stateChanged.connect(self.on_checkbox_state_changed)  # 连接信号和槽
                    self.checkboxes[name] = (check_box, template_id)  # 存储复选框和模版id
                    self.horizontal_layout.addWidget(check_box)
        except FileNotFoundError:
            QMessageBox.warning(self, '警告', f'文件 {config_file} 未找到！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取文件时出错: {e}')

        self.label_from = QLabel('请配置百炼API KEY')

        api_key = get_value_by_key_pkl("shuju_config.pkl", "api_key")
        if (api_key != None):
            self.line_edit_from = QLineEdit(api_key)
        else:
            self.line_edit_from = QLineEdit("请输入api key")
        self.line_edit_from.setFixedWidth(380)

        self.label_from111 = QLabel('请配置图片服务器地址')

        fuwuqi_url = get_value_by_key_pkl("shuju_config.pkl", "fuwuqi_url")
        if (fuwuqi_url != None):
            self.jiarenshurukuang = QLineEdit(fuwuqi_url)
        else:
            self.jiarenshurukuang = QLineEdit("请输入图片服务器地址")
        self.jiarenshurukuang.setFixedWidth(380)
        # 使用 QHBoxLayout 将 "加人间隔：" 输入框 和 "至" 组合在一起
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.label_from)
        self.h_layout.addWidget(self.line_edit_from)
        #self.h_layout.addWidget(self.label_to)
        #self.h_layout.addWidget(self.line_edit_to)

        self.h_layout111 = QHBoxLayout()
        self.h_layout111.addWidget(self.label_from111)
        self.h_layout111.addWidget(self.jiarenshurukuang)

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

        # 这个是文件选择框
        self.h_layout_dir_save = QHBoxLayout()
        self.label_file_save = QLabel("请选择输出文件夹:")
        self.h_layout_dir_save.addWidget(self.label_file_save)

        file_temp_path_save = get_value_by_key_pkl("shuju_config.pkl", "file_path_save")
        if (file_temp_path_save != None):
            self.file_textbox_save = QLineEdit(file_temp_path_save)
        else:
            self.file_textbox_save = QLineEdit("请输入文件夹路径")
        self.h_layout_dir_save.addWidget(self.file_textbox_save)
        self.file_button_save = QPushButton("选择文件", self)
        self.temp_save = QLabel("                          ")
        self.h_layout_dir_save.addWidget(self.file_button_save)
        self.h_layout_dir_save.addWidget(self.temp_save)
        # clicked.connect(self.showDialog)
        self.file_button_save.clicked.connect(self.showDialog_save)



        #这个是文件选择框
        self.h_layout_dir = QHBoxLayout()
        self.label_file = QLabel("请选择配置文件夹:")
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
        #clicked.connect(self.showDialog)
        self.file_button.clicked.connect(self.showDialog)


        #下面是观看任务列表
        self.task_widget = QTableWidget(self)
        self.task_widget.setColumnCount(3)  # Increase column count for checkboxes
        self.task_widget.setHorizontalHeaderLabels(['编号', '运行状态', '备注'])
        self.task_widget.setColumnWidth(0, 200)
        self.task_widget.setColumnWidth(1, 150)
        self.task_widget.setColumnWidth(2, 83)
        self.task_widget.setShowGrid(True)

        self.scroll_area_task = QScrollArea(self)
        self.scroll_area_task.setWidget(self.task_widget)
        self.scroll_area_task.setWidgetResizable(True)  # Allow widget to resize
        self.scroll_area_task.setFixedHeight(200)  # Set fixed height for the scroll area
        self.scroll_area_task.setFixedWidth(500)



        # Set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)  # 设置布局间距为0
        #layout.addWidget(self.titleLabel)
        #layout.addWidget(self.scroll_area)
        layout.addWidget(self.caozuo_tiel)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.caozuo_config)
        #layout.addLayout(self.h_layout_diyihang)
        layout.addLayout(self.h_layout_kongge1)
        layout.addLayout(self.h_layout)
        layout.addLayout(self.h_layout_kongge3)
        layout.addLayout(self.h_layout111)
        layout.addLayout(self.h_layout_kongge2)
        layout.addLayout(self.h_layout_dir_save)
        layout.addLayout(self.h_layout_kongge)
        layout.addLayout(self.h_layout_dir)
        layout.addWidget(self.titleLabel_renwu)
        layout.addWidget(self.scroll_area_task)
        #layout.addWidget(self.scroll_area_log)

        # Variable to store the selected IDs
        self.selected_ids = []
        # Timer to refresh every three seconds
        self.timer = QTimer(self)
        self.refresh_pkl_files_test()
        self.timer.timeout.connect(self.refresh_pkl_files_test)
        self.timer.start(2000)

        self.timer1 = QTimer(self)
        self.timer1.start(1300)

        # Initial load
        self.button_gang = QHBoxLayout()
        self.execute_button = QPushButton("点击开始生成视频")
        self.execute_button.resize(90,30)

        self.button_gang.addWidget(self.execute_button)
        layout.addLayout(self.button_gang)
        self.execute_button.clicked.connect(self.execute_button_clicked)
        #layout.addWidget(self.execute_button_reset)

    def on_checkbox_state_changed(self, state):
        # 这个槽函数会在任何复选框的状态改变时被调用
        # 但是由于我们连接时没有传递额外的参数来标识哪个复选框触发了信号
        # 所以我们需要遍历字典来检查哪个复选框的状态与传递的状态相匹配
        # 然而，这种方法效率不高，更好的做法是使用lambda函数或functools.partial来传递额外的参数
        # 但为了简单起见，这里我们采用一种不那么优雅的方法：
        # 当需要知道哪个复选框被勾选时，我们可以遍历字典并检查状态
        #print(self.checkboxes)

        checked_items = {name: (check_box, template_id) for name, (check_box, template_id) in
                         self.checkboxes.items() if check_box.isChecked()}
        # 现在 checked_items 包含了所有被勾选的复选框及其对应的模版id
        # 您可以在这里添加代码来处理这些被勾选的复选框和模版id
        # 例如，打印它们：
        for name, (check_box, template_id) in checked_items.items():
            print(f'Checked: {name}, Template ID: {template_id}')
    def on_item_changed(self,item: QTableWidgetItem):
        if self.table_widget.currentColumn() == 2:
            # 获取新的数据并打印（或保存到其他地方）
            new_data = item.text()

            item.row()
            phone_name = self.table_widget.item(item.row(),1).text()
            # 你可以在这里添加保存数据的逻辑，比如保存到数据库或文件中
            updata_pkl_config("config.pkl",phone_name,new_data)
    def delete_file_from_dir(self,start_c):
        folders_to_search = [
            'pulled_files',
            'task_config',
            'task_config_txt'
        ]
        # 定义要删除的文件名的模式
        file_pattern = start_c
        # 遍历每个文件夹
        for folder in folders_to_search:
            # 使用 glob 查找匹配的文件
            for filepath in list_files_in_directory(folder):
                if(filepath.startswith(start_c)):
                    try:
                        # 删除文件
                        filepath = folder +"/"+ filepath
                        os.remove(filepath)
                    except OSError as e:
                        print(f"Error deleting file {filepath}: {e.strerror}")

    def shell_neibu(self,cmd):
        os.system(cmd)

    def showDialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            # If a folder is selected, update the QLabel
            self.file_textbox.setText(folder_path)
            self.import_config_ali()
            updata_pkl_config_mianban("file_path",folder_path)
            self.refresh_pkl_files_test()




        else:
            self.file_textbox.setText('No folder selected')
    def showDialog_save(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            # If a folder is selected, update the QLabel
            self.file_textbox_save.setText(folder_path)
            updata_pkl_config_mianban("file_path_save",folder_path)
        else:
            self.file_textbox.setText('No folder selected')


    def showDialog_file(self):
        # 设置文件过滤器
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
                self.import_config()
                self.refresh_pkl_files_test()
    def import_config(self):
        path_dir = "task_config"
        create_directory_if_not_exists(path_dir)

        path_dir_txt = "task_config_txt"
        create_directory_if_not_exists(path_dir_txt)

        with video_lock:
            file_path = self.file_textbox.text()
            # 使用 with 语句打开文件，这样可以确保文件在读取完毕后自动关闭
            with open(file_path, 'r', encoding='utf-8') as file:
                # 逐行读取文件内容并打印
                for line in file:
                    if((str(line).count("_")>0) and (str(line).count("/")>0)):
                        file_name = str(line).split("/")[-2]
                        new_data = {"url":str(line).split("_")[0],"BIG_COUNT":int(str(line).split("_")[1]),"TONGJI":0}
                        file_name = path_dir + "/" +file_name +".pkl"
                        self.judge_pkl_creat(file_name,new_data)
                    if ((str(line).count("_") > 0) and (str(line).count("/") > 0)):
                        file_name = str(line).split("/")[-2]
                        new_data = "0"
                        create_file_if_not_exists_2(path_dir_txt+"/"+file_name,new_data)
        # 注意：使用 with 语句后，不需要手动关闭文件，它会在块结束时自动关闭
    def import_config_ali(self):
        path_dir = "ali"
        empty_folder(path_dir)
        create_directory_if_not_exists(path_dir)

        file_path = self.file_textbox.text()
        files = list_files_in_directory_pic(file_path)
        for file_temp in files:
            file_name = str(file_temp).split(".")[0]
            new_data = {"zhuangtai":"未开始","beizhu":"无","file_path":self.file_textbox.text()+"/"+file_temp}
            file_name = path_dir + "/" +file_name +".pkl"
            self.judge_pkl_creat(file_name,new_data)

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
            dic[key] = value
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)


    def execute_button_clicked(self):
        updata_pkl_config_mianban("api_key", self.line_edit_from.text())
        updata_pkl_config_mianban("fuwuqi_url", self.jiarenshurukuang.text())
        dir_path = "ali"
        task = []

        checked_items = {name: (check_box, template_id) for name, (check_box, template_id) in
                         self.checkboxes.items() if check_box.isChecked()}
        # 现在 checked_items 包含了所有被勾选的复选框及其对应的模版id
        # 您可以在这里添加代码来处理这些被勾选的复选框和模版id
        # 例如，打印它们：
        for name, (check_box, template_id) in checked_items.items():
            task.append(template_id)
        print("task=",task)
        thread = threading.Thread(target=operate_device,args=(dir_path,task,self.line_edit_from.text(),self.jiarenshurukuang.text(),self.file_textbox_save.text()))
        thread.start()
        self.execute_button.setText("执行中，勿重复操作")


        # self.selected_ids = []

    def add_text(self):
        print("")




    def refresh_pkl_files_video(self):
        # 保存当前滚动位置
        current_pos = self.task_widget.verticalScrollBar().value()

        # 清除旧数据
        #self.task_widget.setRowCount(0)
        # 遍历目录中的所有文件
        directory = './task_config'
        row_index = 0
        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.pkl'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'rb') as file:
                        data = pickle.load(file)

                        # 假设数据是一个字典
                        if isinstance(data, dict):


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

            self.task_widget.setRowCount(0)
            # 遍历目录中的所有文件
            directory = './ali'
            create_directory_if_not_exists(directory)
            row_index = 0


            for file_name in os.listdir(directory):
                task_name = file_name
                file_name = directory+"/"+str(file_name)
                if(os.path.isfile(file_name)):
                    try:
                        with open(file_name, 'rb') as file:
                            data = pickle.load(file)

                            # 假设数据是一个字典
                            if isinstance(data, dict):
                                # 插入新行
                                self.task_widget.insertRow(row_index)

                                self.task_widget.setItem(row_index, 0, QTableWidgetItem(str(task_name).split(".")[0]))
                                # 设置文件名（去除后缀）
                                self.task_widget.setItem(row_index, 1, QTableWidgetItem(data.get('zhuangtai', 'N/A')))

                                self.task_widget.setItem(row_index, 2, QTableWidgetItem(str(data.get('beizhu', 'N/A'))))
                                # self.task_widget.setItem(row_index, 3, QTableWidgetItem(str(data.get('TONGJI', 'N/A'))))
                                # self.task_widget.setItem(row_index, 4, QTableWidgetItem("删除"))
                                #
                                # global total_dict
                                # temp = str(str(task_name).split(".")[0])
                                # total_dict[temp] = {'url': data.get('url'), 'BIG_COUNT': str(data.get('BIG_COUNT', 'N/A')),"TONGJI":str(data.get('TONGJI', 'N/A'))}

                                row_index += 1
                    except Exception as e:
                        print(f"读取文件 {file_name} 时出错: {e}")
             # 恢复滚动位置
            self.task_widget.verticalScrollBar().setSliderPosition(current_pos)
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
    time = get_format_time()
    with open(pkl, 'wb') as pkl_file:
        pickle.dump({time:phone+"--->"+values}, pkl_file)

def pkl_add(pkl,dic):
    with open(pkl, 'wb') as pkl_file:
        pickle.dump(dic, pkl_file)
#import pickle

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
        print("崩溃了")
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
        dic[key] = value
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)

def updata_pkl(pklfile,key,value):
    #dic = {}
    if(os.path.isfile(pklfile)):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)
        dic[key] = value
        with open(pklfile, 'wb') as pkl_file:
            pickle.dump(dic, pkl_file)
import subprocess
import time

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
def delete_directory_contents(directory):
    shutil.rmtree(directory)
    os.makedirs(directory)  # 重新创建空文件夹
import os
import pickle

def update_pkl_values(pklfile, key,values):
    if os.path.isfile(pklfile):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)

            # 检查键是否存在，并更新其值
        if key in dic:
            dic[key] = str(values)
            #print("----------------------------------", dic)
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)
        else:
            print(f"Key '{key}' not found in the pickle file.")
    else:
        print(f"The file '{pklfile}' does not exist.")
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
def update_pkl_add_count(pklfile, key,add_count):
    if os.path.isfile(pklfile):
        with open(pklfile, 'rb') as pkl_file:
            dic = pickle.load(pkl_file)

            # 检查键是否存在，并更新其值
        if key in dic:
            dic[key] = str(int(dic[key])+int(add_count))
            #print("----------------------------------", dic)
            with open(pklfile, 'wb') as pkl_file:
                pickle.dump(dic, pkl_file)
        else:
            print(f"Key '{key}' not found in the pickle file.")
    else:
        print(f"The file '{pklfile}' does not exist.")


if __name__ == "__main__":
    path_dir = "ali"
    empty_folder(path_dir)
    app = QApplication(sys.argv)
    viewer = PklViewer()
    viewer.show()
    sys.exit(app.exec())

    #sorted_data = dict(sorted(pkl_list("config.pkl").items(), key=lambda item: item[1]))

    #print(sorted_data)



    # d = u2.connect("Q5S0219527003267")
    # tongji(d,"Q5S0219527003267",r"C:\Users\Administrator\Desktop\config")