import sys
import configparser
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLineEdit, QPushButton
)
from PyQt6.QtCore import QTimer, Qt

# 配置文件路径（保存在程序同目录下的clipboard_config.ini）
CONFIG_FILE = "clipboard_config.ini"

class ClipboardTool(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化配置解析器
        self.config = configparser.ConfigParser()
        # 加载本地配置文件（若不存在则自动创建）
        self.load_config()
        # 存储七列控件：[(输入框1行, 输入框2行, 粘贴按钮), ...]
        self.clipboard_groups = []
        self.init_ui()

    def load_config(self):
        """加载本地配置文件，不存在则创建"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE, encoding="utf-8")
        else:
            # 新建配置文件并初始化七列的空内容
            self.config["INPUT_CONTENT"] = {f"col_{i}_row_0": "" for i in range(7)}
            self.config["INPUT_CONTENT"].update({f"col_{i}_row_1": "" for i in range(7)})
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                self.config.write(f)

    def save_config(self, col, row, content):
        """保存指定列、行的输入框内容到配置文件"""
        key = f"col_{col}_row_{row}"
        if "INPUT_CONTENT" not in self.config:
            self.config["INPUT_CONTENT"] = {}
        self.config["INPUT_CONTENT"][key] = content
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)

    def init_ui(self):
        # 设置窗口标题，按控件缩小比例调整窗口尺寸（原1200*280 → 900*220，四分之三比例）
        self.setWindowTitle("clipboardtool")
        self.resize(800, 130)

        # 初始化网格布局（3行7列）
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # 间距调整：列间隙原10→5（1/2），行间隙原10→3（1/3）
        grid_layout.setHorizontalSpacing(5)   # 列（水平）间隙：原10的1/2
        grid_layout.setVerticalSpacing(3)     # 行（垂直）间隙：原10的1/3
        # 窗口内边距原20→15（四分之三比例）
        grid_layout.setContentsMargins(15, 15, 15, 15)

        # 控件尺寸基准值（原按钮最小宽度80 → 60，四分之三）
        base_btn_width = 120
        base_input_width = 120  # 输入框最大宽度，按四分之三比例设定

        # 循环创建七列控件
        for col in range(7):
            # 第一行输入框（可编辑，用于复制）
            input_row0 = QLineEdit()
            input_row0.setPlaceholderText(f"第{col+1}列 第一行输入框")
            input_row0.setMaximumWidth(base_input_width)  # 输入框宽度缩为四分之三
            # 新增：设置输入框文本水平居中
            input_row0.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 加载历史内容
            history_row0 = self.config["INPUT_CONTENT"].get(f"col_{col}_row_0", "")
            input_row0.setText(history_row0)
            # 绑定文本变化保存事件
            input_row0.textChanged.connect(lambda text, c=col, r=0: self.save_config(c, r, text))
            grid_layout.addWidget(input_row0, 0, col)

            # 第二行输入框（可编辑，仅存储）
            input_row1 = QLineEdit()
            input_row1.setPlaceholderText(f"第{col+1}列 第二行输入框")
            input_row1.setMaximumWidth(base_input_width)  # 输入框宽度缩为四分之三
            # 新增：设置输入框文本水平居中
            input_row1.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 加载历史内容
            history_row1 = self.config["INPUT_CONTENT"].get(f"col_{col}_row_1", "")
            input_row1.setText(history_row1)
            # 绑定文本变化保存事件
            input_row1.textChanged.connect(lambda text, c=col, r=1: self.save_config(c, r, text))
            grid_layout.addWidget(input_row1, 1, col)

            # 第三行粘贴按钮
            paste_btn = QPushButton(f"粘贴{col+1}")
            paste_btn.clicked.connect(lambda checked, c=col: self.copy_col_content(c))
            # 按钮宽度缩为四分之三（原80→60）
            paste_btn.setMinimumWidth(base_btn_width)
            paste_btn.setMaximumWidth(base_btn_width)
            # 样式表设置按钮文字居中，避免挤压
            paste_btn.setStyleSheet("text-align: center; font-size: 12px;")
            grid_layout.addWidget(paste_btn, 2, col)

            # 存入控件列表
            self.clipboard_groups.append((input_row0, input_row1, paste_btn))

    def copy_col_content(self, col_index):
        """点击对应列按钮，复制该列第一行输入框内容到剪贴板"""
        input_row0, _, paste_btn = self.clipboard_groups[col_index]
        content = input_row0.text().strip()

        if content:
            # 复制到系统剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            # 按钮提示反馈
            paste_btn.setText("已复制！")
            QTimer.singleShot(1000, lambda: paste_btn.setText(f"粘贴{col_index+1}"))
        else:
            # 输入框为空提示
            paste_btn.setText("内容为空！")
            QTimer.singleShot(1000, lambda: paste_btn.setText(f"粘贴{col_index+1}"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipboardTool()
    window.show()
    sys.exit(app.exec())