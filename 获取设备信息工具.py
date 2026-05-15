import sys
import platform
import hashlib
import os
import uuid
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout)


class DeviceInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("设备信息获取工具")
        self.setGeometry(100, 100, 300, 200)  # 调整窗口大小

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # 创建包含提示标签和文本输入框的水平布局
        hbox = QHBoxLayout()

        # 创建提示标签
        self.label = QLabel("设备码:")
        hbox.addWidget(self.label)

        # 创建文本输入框
        self.text_input = QLineEdit()
        self.text_input.setReadOnly(True)  # 设置为只读
        self.text_input.setPlaceholderText("设备码将显示在这里...")
        hbox.addWidget(self.text_input)

        main_layout.addLayout(hbox)

        # 创建按钮
        self.get_info_button = QPushButton("获取设备信息")
        self.get_info_button.clicked.connect(self.get_device_info)
        main_layout.addWidget(self.get_info_button)

        central_widget.setLayout(main_layout)

    def get_real_device_id(self):
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

    def get_device_info(self):
        """获取设备唯一标识码并显示在文本框中"""
        device_id = self.get_real_device_id()
        self.text_input.setText(device_id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceInfoApp()
    window.show()
    sys.exit(app.exec())