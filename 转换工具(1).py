import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPlainTextEdit, QComboBox, QLabel, QPushButton, QHBoxLayout,
    QLineEdit
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据分隔符转换工具")
        self.setGeometry(300, 300, 400, 500)

        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 创建输入编辑框
        self.input_edit = QPlainTextEdit()
        self.input_edit.setFixedHeight(250)
        self.input_edit.setPlaceholderText("请输入原始数据...")
        layout.addWidget(self.input_edit)

        # 创建分隔符编辑框（水平布局）
        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("老分隔符:"))
        self.old_sep_edit = QLineEdit("----")
        sep_layout.addWidget(self.old_sep_edit)
        layout.addLayout(sep_layout)

        # 创建新分隔符编辑框（水平布局）
        new_sep_layout = QHBoxLayout()
        new_sep_layout.addWidget(QLabel("新分隔符:"))
        self.new_sep_edit = QLineEdit("****")
        new_sep_layout.addWidget(self.new_sep_edit)
        layout.addLayout(new_sep_layout)

        # 创建新分隔符编辑框（水平布局）
        new_sep_layout_shunxu = QHBoxLayout()
        new_sep_layout_shunxu.addWidget(QLabel("顺序配置:"))
        self.new_sep_edit_shunxu = QLineEdit("1-2-3-4-5")
        new_sep_layout_shunxu.addWidget(self.new_sep_edit_shunxu)
        layout.addLayout(new_sep_layout_shunxu)

        # 创建选择顺序标题
        # layout.addWidget(QLabel("选择顺序:"))
        #
        # # 创建三个独立下拉框（水平布局）
        # combo_layout = QHBoxLayout()
        # self.combo1 = QComboBox()
        # self.combo2 = QComboBox()
        # self.combo3 = QComboBox()
        #
        # # 添加选项
        # options = ["手机号", "昵称", "链接"]
        # #for combo in [self.combo1, self.combo2, self.combo3]:
        # #    combo.addItems(options)
        # self.combo1.addItems(["昵称", "手机号", "链接"])
        # self.combo2.addItems([ "手机号","昵称", "链接"])
        # self.combo3.addItems([ "链接","手机号", "昵称"])
        # combo_layout.addWidget(self.combo1)
        # combo_layout.addWidget(self.combo2)
        # combo_layout.addWidget(self.combo3)
        # layout.addLayout(combo_layout)

        # 创建执行按钮
        self.execute_btn = QPushButton("执行转换")
        self.execute_btn.clicked.connect(self.handle_execute)
        layout.addWidget(self.execute_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def handle_execute(self):
        """处理执行按钮点击事件"""
        zong = ""
        # 获取输入数据
        input_text = self.input_edit.toPlainText()

        # 获取分隔符
        old_sep = self.old_sep_edit.text()
        new_sep = self.new_sep_edit.text()

        # 获取选择的字段
        fields = self.new_sep_edit_shunxu.text()

        # 简单验证
        if not all([old_sep, new_sep, input_text]):
            self.input_edit.appendPlainText("错误：所有字段都必须填写！")
            return

        # 这里可以添加实际的数据处理逻辑
        # 示例：简单替换分隔符
        list_temp = str(input_text).split("\n")
        fields = fields.split("-")
        for  temp in list_temp:
            print(temp)
            hang = ""
            yaosus = str(temp).split(old_sep)
            print("yaosus=",yaosus)

            for field in fields:
                print("field=",field)
                if(int(field)<=len(yaosus)):
                    print(hang ,yaosus[int(field)-1] ,str(new_sep))
                    hang = hang + yaosus[int(field)-1] + str(new_sep)

            if(str(hang).endswith(new_sep)):
                hang = str(hang)[0:-len(new_sep)]

            zong = zong + hang + "\n"


        output_text = input_text.replace(old_sep, new_sep)

        # 清空并显示结果
        self.input_edit.clear()
        #self.input_edit.appendPlainText("转换结果：")
        self.input_edit.appendPlainText(zong)
        #self.input_edit.appendPlainText("\n选择的字段顺序：")
        #self.input_edit.appendPlainText(", ".join(fields))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())