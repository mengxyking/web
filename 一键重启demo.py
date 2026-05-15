import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RestartableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 主窗口设置
        self.setWindowTitle("PyQt6 程序重启示例")
        self.setGeometry(100, 100, 400, 250)  # 坐标(x,y) + 宽高(w,h)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # 添加提示标签
        label = QLabel("点击下方按钮重启当前程序")
        label.setFont(QFont("Arial", 14))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # 添加重启按钮
        self.restart_btn = QPushButton("一键重启")
        self.restart_btn.setFont(QFont("Arial", 12))
        self.restart_btn.setFixedSize(120, 50)
        # 绑定点击事件
        self.restart_btn.clicked.connect(self.restart_program)
        layout.addWidget(self.restart_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def restart_program(self):
        """核心重启函数"""
        try:
            # 1. 获取当前程序路径和运行参数
            # sys.executable 打包后指向exe文件，开发时指向python.exe
            exe_path = sys.executable
            args = sys.argv  # 保留原运行参数

            # 2. 启动新的程序实例（非阻塞）
            # creationflags=0x08000000：Windows下隐藏控制台窗口（GUI程序必备）
            # 非Windows系统删除该参数即可
            if sys.platform == "win32":
                subprocess.Popen(
                    [exe_path] + args,
                    creationflags=0x08000000  # 隐藏控制台窗口
                )
            else:
                subprocess.Popen([exe_path] + args)

            # 3. 提示并关闭当前实例
            #QMessageBox.information(self, "提示", "程序即将重启...")
            # 退出当前程序
            QApplication.quit()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"重启失败：{str(e)}")

if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)
    # 启动主窗口
    window = RestartableApp()
    window.show()
    # 运行应用循环
    sys.exit(app.exec())