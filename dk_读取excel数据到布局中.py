import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QLineEdit, QMessageBox, QStyledItemDelegate
)
from PyQt6.QtCore import QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.excel_file = None
        self.data = pd.DataFrame()
        self.update_interval = 3000  # 更新间隔，单位为毫秒
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_excel_and_update_table)

        self.setWindowTitle('Excel Data Updater')
        self.setGeometry(100, 100, 800, 600)
        # 主布局

        self.main_layout_douyin = QVBoxLayout()
        self.main_layout_douyin.setGeometry(100, 100, 800, 600)
        self.table_widget = QTableWidget(self)
        self.initialize_table_structure()  # 初始化表格结构
        self.table_widget.setItemDelegate(MyItemDelegate(self))  # 可选：自定义委托以处理空值显示
        self.main_layout_douyin.addWidget(self.table_widget)

        self.h_layout_dir_douyin = QHBoxLayout()
        self.file_textbox_douyin = QLineEdit("请输入文件夹路径")
        self.h_layout_dir_douyin.addWidget(self.file_textbox_douyin)
        self.file_button_douyin = QPushButton("选择文件", self)
        self.temp_douyin = QLabel("                          ")
        self.h_layout_dir_douyin.addWidget(self.file_button_douyin)
        self.main_layout_douyin.addLayout(self.h_layout_dir_douyin)
        self.file_button_douyin.clicked.connect(self.showDialog)

        # 创建容器小部件并设置布局
        container = QWidget(self)
        container.setLayout(self.main_layout_douyin)
        #self.setCentralWidget(container)



        # 开始定时器
        self.timer.start(self.update_interval)

    def initialize_table_structure(self):
        # 假设初始的列头是 ['编号', 'uid', '私信状态', '关注状态', '任务倒计时']
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['编号', 'uid', '私信状态', '关注状态', '任务倒计时'])
    def showDialog(self):
        # 设置文件过滤器
        print("1")
        filters = "Excel Files (*.xlsx);;All Files (*)"

        # 创建文件对话框
        dialog = QFileDialog(self, "Open Excel File", "", filters)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setDefaultSuffix("xlsx")
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        # 显示对话框并获取用户选择
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                selected_file = selected_files[0]  # 获取第一个选中的文件（假设只选择一个文件）
                self.file_textbox_douyin.setText(selected_file)
                self.excel_file = selected_file
                self.read_excel_and_update_table()

    def read_excel_and_update_table(self):
        print("fudai_path")
        if self.excel_file:
            try:
                print("222")
                # 读取Excel文件，假设第一行是列标题
                new_data = pd.read_excel(self.excel_file)
                new_data=new_data.drop(new_data.columns[0], axis=1)
                print("new_data",new_data)
                print("----------------------")
                print(new_data.columns)
                print(self.data.columns)
                # 如果数据框为空或列不匹配，则重新初始化表头和数据
                if self.data.empty or not new_data.columns.equals(self.data.columns):
                    print("是空的。。。。。。")
                    self.data = new_data.copy()
                    print("self.data---->",self.data)
                    print("jieshu")
                    self.update_table_structure()

                else:
                    print("不是空的")
                    # 否则，只更新数据（这里假设Excel文件的行数不会改变）
                    self.data.loc[:, :] = new_data.values

                self.update_table_data()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法读取Excel文件: {e}")

    def update_table_structure(self):
        # 根据数据框的列数设置表格的列数
        print("888")
        print("self.data.columns--------->",self.data.columns)
        self.table_widget.setHorizontalHeaderLabels(self.data.columns)
        self.table_widget.setColumnCount(len(self.data.columns))
        # 根据数据框的行数设置表格的行数
        self.table_widget.setRowCount(len(self.data))
    def update_table_data(self):
        # 清除表格中除了第一行之外的所有现有项
        #self.table_widget.setRowCount(1)  # 重置行数到只有一行（标题行）

        # 根据数据框的行数设置表格的行数（不包括标题行）
        row_count = len(self.data)
        self.table_widget.setRowCount(row_count)  # +1 是为了包含标题行

        # 填充表格数据（从第二行开始）
        for row_idx, row_data in self.data.iterrows():
            row_in_table = row_idx   # 表格中的行索引（从1开始，因为0是标题行）
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if pd.notna(value) else '')  # 空值显示为空字符串
                self.table_widget.setItem(row_in_table, col_idx, item)

    def modify_data(self):
        uid = self.uid_input.text().strip()
        new_message_status = self.new_message_status.text().strip()

        if not uid or not new_message_status:
            QMessageBox.warning(self, "警告", "UID和新的私信状态不能为空！")
            return

        # 查找UID对应的行（这里假设UID是唯一的）
        row = self.data[self.data['uid'] == uid]
        if row.empty:
            QMessageBox.warning(self, "警告", f"未找到UID为{uid}的数据！")
        else:
            # 修改私信状态
            self.data.loc[self.data['uid'] == uid, '私信状态'] = new_message_status

            # 更新表格数据
            self.update_table_data()

            # 自动保存修改到Excel文件（这里为了简化，每次修改都立即保存）
            try:
                self.data.to_excel(self.excel_file, index=False)
                QMessageBox.information(self, "成功", "数据已成功修改并保存到Excel文件！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存Excel文件: {e}")

# 可选：自定义委托以处理空值显示（这里为了简单起见，没有真正实现委托的逻辑）
class MyItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    # 这里可以重写paint和createEditor等方法来自定义单元格的显示和编辑行为
    # 但在这个示例中，我们没有真正实现这些逻辑，而是直接在update_table_data中处理了空值显示

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())