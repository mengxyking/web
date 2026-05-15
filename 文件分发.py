import os
import shutil
import sys
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QFileDialog, QMessageBox
)


class FolderSelectorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("文件分发工具")
        self.setFixedSize(400, 300)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # 第一个设置：选择文件夹
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("请你选择文件夹:")
        self.folder_edit = QLineEdit()
        self.folder_button = QPushButton("选择")
        self.folder_button.clicked.connect(self.select_folder)

        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)

        # 第二个设置：生成文件夹个数
        format_layout = QHBoxLayout()
        self.format_label = QLabel("生成文件夹个数:")
        self.format_edit = QLineEdit()

        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_edit)
        main_layout.addLayout(format_layout)

        # 第三个设置：文件夹存放数量
        count_layout = QHBoxLayout()
        self.count_label = QLabel("文件夹存放数量:")
        self.count_edit = QLineEdit()

        count_layout.addWidget(self.count_label)
        count_layout.addWidget(self.count_edit)
        main_layout.addLayout(count_layout)

        # 执行按钮
        self.execute_button = QPushButton("执行")
        self.execute_button.clicked.connect(self.execute)
        main_layout.addWidget(self.execute_button)

    def select_folder(self):
        # 打开文件夹选择对话框
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_edit.setText(folder)

    def execute(self):
        print("")
        th = threading.Thread(target=self.yewu())
        th.start()

    def yewu(self):
        self.execute_button.setEnabled(False)  # 置灰按钮
        # 获取配置文件夹路径
        folder_path = self.folder_edit.text()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "警告", "请先选择有效的文件夹")
            self.execute_button.setEnabled(True)
            return

        try:
            # 获取生成文件夹个数
            folder_count = int(self.format_edit.text()) if self.format_edit.text() else 1
            if folder_count <= 0:
                self.execute_button.setEnabled(True)
                raise ValueError("文件夹个数必须大于0")

            # 获取每个文件夹存放的文件数量
            files_per_folder = int(self.count_edit.text()) if self.count_edit.text() else 1
            if files_per_folder <= 0:
                self.execute_button.setEnabled(True)
                raise ValueError("每个文件夹存放的文件数量必须大于0")

            # 第一步：删除配置文件夹内的所有子文件夹
            self.clear_subfolders(folder_path)

            # 第二步：生成指定数量的子文件夹
            self.create_subfolders(folder_path, folder_count)

            # 第三步：分发文件
            self.distribute_files(folder_path, files_per_folder)

            QMessageBox.information(self, "成功", "文件分发完成！")
        except ValueError as e:
            self.execute_button.setEnabled(True)
            QMessageBox.warning(self, "错误", str(e))
        except BaseException as e:
            self.execute_button.setEnabled(True)
            print("----")
        self.execute_button.setEnabled(True)
    def clear_subfolders(self, folder_path):
        # 删除文件夹内的所有子文件夹
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)

    def create_subfolders(self, folder_path, count):
        # 创建指定数量的子文件夹，使用两位数编号
        for i in range(1, count + 1):
            folder_number = f"{i:02d}"  # 使用两位数格式
            subfolder_path = os.path.join(folder_path, f"{folder_number}")
            os.makedirs(subfolder_path, exist_ok=True)

    def distribute_files(self, folder_path, files_per_folder):
        # 获取所有非文件夹文件
        files = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                files.append(item_path)

        # 按顺序将文件移动到各个子文件夹
        for i in range(0, len(files), files_per_folder):
            batch = files[i:i + files_per_folder]
            if not batch:
                continue

            # 找到第i个文件夹（从1开始计数）
            folder_index = (i // files_per_folder) + 1
            folder_number = f"{folder_index:02d}"  # 使用两位数格式
            target_folder = os.path.join(folder_path, f"{folder_number}")

            for file_path in batch:
                shutil.move(file_path, os.path.join(target_folder, os.path.basename(file_path)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderSelectorApp()
    window.show()
    sys.exit(app.exec())