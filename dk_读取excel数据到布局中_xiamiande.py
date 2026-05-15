import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QSpinBox

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建标题标签
        title_label = QLabel("配置区", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建复选框布局（水平布局）
        checkbox_layout = QHBoxLayout()
        self.checkbox1 = QCheckBox("给力给力", self)
        self.checkbox2 = QCheckBox("开启发送私信功能", self)
        self.checkbox3 = QCheckBox("开启关注私信用户", self)
        checkbox_layout.addWidget(self.checkbox1)
        checkbox_layout.addWidget(self.checkbox2)
        checkbox_layout.addWidget(self.checkbox3)
        checkbox_layout.addStretch()  # 添加一个伸缩因子以填充剩余空间

        main_layout.addLayout(checkbox_layout)

        # 创建表单布局（输入框和间隔选择器）
        form_layout = QFormLayout()
        self.nickname_label = QLabel("昵称不含：", self)
        self.nickname_spinbox = QSpinBox(self)
        self.nickname_spinbox.setRange(0, 9999)  # 设置范围（可选）
        self.nickname_spinbox.setValue(5)  # 设置默认值
        form_layout.addRow(self.nickname_label, self.nickname_spinbox)

        self.interval_label = QLabel("私信间隔：", self)
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setRange(1, 60)  # 假设最小间隔为1分钟，最大为60分钟
        self.interval_spinbox.setSuffix(" 分")  # 设置后缀以显示分钟
        self.interval_spinbox.setValue(5)  # 设置默认值
        form_layout.addRow(self.interval_label, self.interval_spinbox)

        main_layout.addLayout(form_layout)

        # 创建按钮布局（水平布局）
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始私信", self)
        self.stop_button = QPushButton("停止", self)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()  # 添加一个伸缩因子以填充剩余空间

        main_layout.addLayout(button_layout)

        # 设置窗口的主布局
        self.setLayout(main_layout)

        # 设置窗口标题和大小
        self.setWindowTitle("配置窗口")
        self.setGeometry(100, 100, 400, 300)

# 创建应用程序对象
app = QApplication(sys.argv)

# 创建并显示窗口
window = ConfigWindow()
window.show()

# 运行应用程序的事件循环
sys.exit(app.exec())