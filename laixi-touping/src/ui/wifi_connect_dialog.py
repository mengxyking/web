"""WiFi ADB连接对话框"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QSpinBox)
from PyQt5.QtCore import Qt


class WifiConnectDialog(QDialog):
    def __init__(self, adb_manager, parent=None):
        super().__init__(parent)
        self._adb = adb_manager
        self.setWindowTitle("WiFi连接设备")
        self.setFixedSize(360, 180)
        self.setStyleSheet("background: #16213e; color: #e0e0e0;")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("设备IP地址："))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("例如: 192.168.1.100")
        self.ip_input.setStyleSheet("background: #0f3460; color: #e0e0e0; padding: 6px; border-radius: 4px;")
        layout.addWidget(self.ip_input)

        layout.addWidget(QLabel("端口 (默认5555)："))
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(5555)
        self.port_input.setStyleSheet("background: #0f3460; color: #e0e0e0; padding: 4px;")
        layout.addWidget(self.port_input)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        connect_btn = QPushButton("连接")
        connect_btn.setStyleSheet("background: #e94560; color: white; padding: 6px 16px; border-radius: 4px;")
        connect_btn.clicked.connect(self._connect)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background: #555; color: white; padding: 6px 16px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(connect_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _connect(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.value()
        if not ip:
            self.status_label.setText("请输入IP地址")
            self.status_label.setStyleSheet("color: #e94560;")
            return
        self.status_label.setText("连接中...")
        self.status_label.setStyleSheet("color: #aaa;")
        ok = self._adb.connect_wifi(ip, port)
        if ok:
            self.status_label.setText(f"连接成功: {ip}:{port}")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("连接失败，请检查IP和端口")
            self.status_label.setStyleSheet("color: #e94560;")
