import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('Multi-Tab Layout Example')
        self.setGeometry(100, 100, 600, 400)

        # 创建 QTabWidget
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # 创建第一个标签页
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1_layout.addWidget(QLabel('This is Tab 1'))
        tab1_layout.addWidget(QPushButton('Button in Tab 1'))
        tab1.setLayout(tab1_layout)
        self.tab_widget.addTab(tab1, 'Tab 1')

        # 创建第二个标签页
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2_layout.addWidget(QLabel('This is Tab 2'))
        tab2_layout.addWidget(QPushButton('Button in Tab 2'))
        tab2.setLayout(tab2_layout)
        self.tab_widget.addTab(tab2, 'Tab 2')

        # 创建第三个标签页
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_layout.addWidget(QLabel('This is Tab 3'))
        tab3_layout.addWidget(QPushButton('Button in Tab 3'))
        tab3.setLayout(tab3_layout)
        self.tab_widget.addTab(tab3, 'Tab 3')

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())