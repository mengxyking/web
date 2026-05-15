import base64
import hashlib
import sys
import json
import os
import threading
import uuid
from util.paddleOCR_json_duixiang import OCRProcessor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGroupBox, QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator

import baijiahao_yewu


class RestTimeConfigurator(QMainWindow):
    """休息时间配置器主窗口"""

    def __init__(self):
        super().__init__()
        self.clicked_user = []

        # 配置文件路径
        self.config_file = "rest_time_config.json"
        self.ocr_processor = OCRProcessor()

        # 设置窗口基本属性
        self.setWindowTitle("休息时间配置器")
        self.setMinimumSize(800, 300)  # 增大窗口尺寸以容纳新配置项

        # 初始化UI
        self.init_ui()

        # 初始化配置数据
        self.init_config_data()

        # 加载保存的配置（如果存在）
        self.load_config()

    def init_ui(self):
        """初始化用户界面"""
        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 添加标题
        title_label = QLabel("百家号")
        title_font = QFont("SimHei", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # 创建间隔时间配置区域
        time_config_group = QGroupBox("时间配置")
        time_config_layout = QHBoxLayout()
        time_config_layout.setSpacing(30)
        time_config_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 大时间配置
        big_time_label = QLabel("间隔时间:")
        big_time_label.setFont(QFont("SimHei", 10))
        self.big_time_input = QLineEdit()
        self.big_time_input.setValidator(QIntValidator(1, 120))  # 限制为1-120的整数
        self.big_time_input.setText("5")  # 默认值
        self.big_time_input.setMinimumWidth(50)
        self.big_time_input.setPlaceholderText("输入分钟数")

        # 小时间配置
        small_time_label = QLabel("到")
        small_time_label.setFont(QFont("SimHei", 10))
        self.small_time_input = QLineEdit()
        self.small_time_input.setValidator(QIntValidator(1, 60))  # 限制为1-60的整数
        self.small_time_input.setText("30")  # 默认值
        self.small_time_input.setMinimumWidth(50)
        self.small_time_input.setPlaceholderText("输入分钟数")

        # 添加到时间配置布局
        time_config_layout.addWidget(big_time_label)
        time_config_layout.addWidget(self.big_time_input)
        time_config_layout.addWidget(small_time_label)
        time_config_layout.addWidget(self.small_time_input)
        time_config_layout.addStretch()  # 添加伸缩项，使内容居中

        time_config_group.setLayout(time_config_layout)
        main_layout.addWidget(time_config_group)

        # 创建EXE文件配置区域
        exe_config_group = QGroupBox("应用程序配置")
        exe_config_layout = QHBoxLayout()
        exe_config_layout.setSpacing(15)
        exe_config_layout.setContentsMargins(10, 10, 10, 10)

        # EXE路径输入框
        exe_label = QLabel("选择应用程序:")
        exe_label.setFont(QFont("SimHei", 10))
        self.exe_path_input = QLineEdit()
        self.exe_path_input.setMinimumWidth(300)
        self.exe_path_input.setReadOnly(True)  # 设为只读，只能通过按钮选择

        # 浏览按钮
        self.browse_button = QPushButton("浏览...")
        self.browse_button.setFont(QFont("SimHei", 10))
        self.browse_button.setMinimumWidth(80)
        self.browse_button.clicked.connect(self.browse_exe_file)

        # 添加到EXE配置布局
        exe_config_layout.addWidget(exe_label)
        exe_config_layout.addWidget(self.exe_path_input)
        exe_config_layout.addWidget(self.browse_button)

        exe_config_group.setLayout(exe_config_layout)
        main_layout.addWidget(exe_config_group)

        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)  # 按钮之间的间距

        # 保存配置按钮
        self.save_button = QPushButton("保存配置")
        self.save_button.setFont(QFont("SimHei", 10))
        self.save_button.setMinimumHeight(40)
        self.save_button.setMinimumWidth(120)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.save_button.clicked.connect(self.on_save_clicked)

        # 执行按钮
        self.execute_button = QPushButton("执行休息计划")
        self.execute_button.setFont(QFont("SimHei", 10))
        self.execute_button.setMinimumHeight(40)
        self.execute_button.setMinimumWidth(150)
        self.execute_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        # 绑定点击事件
        self.execute_button.clicked.connect(self.on_execute_clicked)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.execute_button)
        main_layout.addLayout(button_layout)

    def init_config_data(self):
        """初始化配置数据"""
        self.config_data = {
            "min_interval": 5,
            "max_interval": 30,
            "exe_path": ""  # 新增的exe路径配置
        }

    def browse_exe_file(self):
        """浏览并选择EXE文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择应用程序", "", "可执行文件 (*.exe);;所有文件 (*)"
        )
        if file_path:
            # 验证文件是否存在且是exe文件
            if os.path.isfile(file_path) and file_path.lower().endswith('.exe'):
                self.exe_path_input.setText(file_path)
            else:
                QMessageBox.warning(self, "选择错误", "请选择有效的EXE文件！")

    def on_save_clicked(self):
        """保存配置按钮点击事件处理"""
        try:
            # 获取并验证当前配置的时间
            min_interval = int(self.big_time_input.text())
            max_interval = int(self.small_time_input.text())
            exe_path = self.exe_path_input.text().strip()

            # 验证时间范围
            if not (1 <= min_interval <= 120 and 1 <= max_interval <= 60):
                QMessageBox.warning(self, "输入错误", "时间输入超出有效范围！")
                return

            # 确保最小值小于等于最大值
            if min_interval > max_interval:
                QMessageBox.warning(self, "输入错误", "最小值不能大于最大值！")
                return

            # 验证exe路径（如果提供）
            if exe_path and (not os.path.isfile(exe_path) or not exe_path.lower().endswith('.exe')):
                QMessageBox.warning(self, "路径错误", "选择的不是有效的EXE文件！")
                return

            # 更新配置数据
            self.config_data["min_interval"] = min_interval
            self.config_data["max_interval"] = max_interval
            self.config_data["exe_path"] = exe_path

            # 保存到文件
            if self.save_config():
                QMessageBox.information(
                    self, "保存成功",
                    f"配置已保存:\n间隔时间 {min_interval} 到 {max_interval} 分钟\n"
                    f"应用程序: {'未选择' if not exe_path else os.path.basename(exe_path)}"
                )

        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的整数时间！")

    def on_execute_clicked(self):

        result_j = judge()
        if (result_j == False):
            print("当前需要联系")
            #self.titleLabel.setText("*" * 55 + "当前需要联系作者" + "*" * 55)
            self.setWindowTitle("*" * 55 + "当前需要联系作者" + "*" * 55)
            #self.titleLabel.setStyleSheet("color: red;")
            return

        # 检查是否已选择exe文件（如果需要的话）
        if not self.config_data["exe_path"]:
            # 可以选择提示用户或继续执行
            reply = QMessageBox.question(
                self, "未选择应用程序",
                "尚未选择应用程序，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # 避免重复启动线程
        if hasattr(self, "auto_thread") and self.auto_thread.is_alive():
            QMessageBox.warning(self, "提示", "自动化任务已在运行中！")
            return

        # 启动线程，可将exe路径作为参数传递
        self.auto_thread = threading.Thread(
            target=baijiahao_yewu.control,
            args=(self.ocr_processor, self.config_data["exe_path"])
        )
        self.auto_thread.start()
        QMessageBox.information(self, "提示", "自动化任务已启动！")

    def save_config(self):
        """将配置保存到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"配置保存失败: {str(e)}")
            return False

    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)

                # 更新界面显示
                self.big_time_input.setText(str(self.config_data.get("min_interval", 5)))
                self.small_time_input.setText(str(self.config_data.get("max_interval", 30)))
                self.exe_path_input.setText(self.config_data.get("exe_path", ""))
                return True
        except Exception as e:
            print(f"配置加载失败: {str(e)}")
            QMessageBox.warning(self, "加载失败", f"配置加载失败: {str(e)}\n将使用默认配置")

        # 加载失败使用默认配置
        return False

    def get_current_config(self):
        """获取当前配置"""
        return self.config_data.copy()
import platform
def get_real_device_id():
    """获取更真实的设备唯一标识，并返回缩短后的版本"""
    try:
        # 收集各种硬件和系统信息
        info = [
            platform.node(),  # 计算机名
            platform.machine(),  # 机器类型
            platform.processor(),  # 处理器信息
            platform.system(),  # 操作系统名称
            platform.release(),  # 操作系统版本
            str(os.environ.get('COMPUTERNAME', '')),  # Windows计算机名
            str(os.environ.get('USERNAME', ''))
        ]
        # 创建哈希作为设备ID
        hash_obj = hashlib.sha256()
        hash_obj.update(''.join(info).encode('utf-8'))
        full_hash = hash_obj.hexdigest()

        # 返回缩短后的唯一码（例如前8个字符）
        return full_hash[:18]  # 取前8个字符作为缩短的唯一码
    except Exception as e:
        return f"ERR-{str(e)[:18]}"  # 错误情况下也返回缩短的字符串



def encrypt_and_modify(shebeima):
    """对输入的字符串进行Base64编码，并在特定位置插入字符"""
    input_text = shebeima

    if not input_text:
        return

    # 进行Base64编码
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')

    # 在特定位置插入字符
    modified_str = list(encoded_str)

    # 确保字符串足够长，以避免索引错误
    if len(modified_str) >= 1:
        modified_str[0] += 'a'
    if len(modified_str) >= 3:
        modified_str[2] += 'b'
    if len(modified_str) >= 5:
        modified_str[4] += 'f'
    if len(modified_str) >= 2:
        modified_str[-2] += 'g'

    # 将列表转换回字符串
    final_str = ''.join(modified_str)
    return final_str
def judge():
    shebeima = get_real_device_id()
    final_str = encrypt_and_modify(shebeima)
    print(shebeima,final_str)
    print(os.path.isfile(final_str))
    if(os.path.isfile(final_str)):
        return True
    else:
        return False
if __name__ == "__main__":
    # 确保中文显示正常
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("SimHei")
    app.setFont(font)

    window = RestTimeConfigurator()
    window.show()

    sys.exit(app.exec())
