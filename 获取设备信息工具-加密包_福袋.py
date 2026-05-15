import sys
import base64
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import QFile, QTextStream


class EncryptionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("设备码加密工具")
        self.setGeometry(100, 100, 400, 200)  # 设置窗口大小和位置

        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 创建结果标签，用于显示加密后的字符串
        self.result_label = QLabel("加密结果将显示在这里...")
        layout.addWidget(self.result_label)

        # 创建提示标签和文本输入框的水平布局
        hbox = QHBoxLayout()

        # 创建提示标签
        self.prompt_label = QLabel("请输入需要加密的设备码:")
        hbox.addWidget(self.prompt_label)

        # 创建文本输入框
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("在此输入设备码...")
        hbox.addWidget(self.text_input)

        layout.addLayout(hbox)

        # 创建执行按钮
        self.execute_button = QPushButton("执行加密")
        self.execute_button.clicked.connect(self.encrypt_and_modify)
        layout.addWidget(self.execute_button)

        # 设置主部件的布局
        central_widget.setLayout(layout)

    def encrypt_and_modify(self):
        """对输入的字符串进行Base64编码，并在特定位置插入字符"""
        input_text = self.text_input.text()

        if not input_text:
            self.result_label.setText("请输入设备码")
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

        # 显示结果
        self.result_label.setText(f"加密后的结果: {final_str}")

        # 创建文件，文件名以加密后的字符串命名
        self.create_file(final_str)

    def create_file(self, file_name):
        """创建一个文件，文件名以加密后的字符串命名"""
        file = QFile(f"{file_name}")
        if not file.open(QFile.OpenModeFlag.WriteOnly | QFile.OpenModeFlag.Text):
            self.result_label.setText(f"无法创建文件: {file_name}")
            return

        out = QTextStream(file)
        out << f"加密后的内容: {file_name}"
        file.close()
        self.result_label.setText(f"文件已创建: {file_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EncryptionApp()
    window.show()
    sys.exit(app.exec())