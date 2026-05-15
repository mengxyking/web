import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QMessageBox

class ConfigCheckBoxApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('读取配置的多选框')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        # 读取配置文件
        config_file = 'config.txt'
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    # 分割 'name-模版id'，只取 'name' 部分
                    name, _ = line.strip().split('-')
                    check_box = QCheckBox(name)
                    layout.addWidget(check_box)
        except FileNotFoundError:
            QMessageBox.warning(self, '警告', f'文件 {config_file} 未找到！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'读取文件时出错: {e}')

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConfigCheckBoxApp()
    ex.show()
    sys.exit(app.exec())