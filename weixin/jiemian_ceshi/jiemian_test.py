import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSplitter)
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl, Qt


class WeChatDeviceManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeChat 设备管理")
        self.resize(1200, 800)

        # 网络请求管理器
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_reply)

        # 初始化界面
        self.init_ui()
        # 加载数据
        self.load_service_data()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 分割布局（左右区域）
        splitter = QSplitter()

        # 左侧：服务列表
        self.service_table = QTableWidget(0, 5)
        self.service_table.setHorizontalHeaderLabels(["#", "地址", "数量", "端口", "运行"])
        splitter.addWidget(self.service_table)

        # 右侧：设备列表
        self.device_table = QTableWidget(0, 10)
        self.device_table.setHorizontalHeaderLabels(
            ["#", "IP", "端口", "端口(备)", "状态", "任务", "号码", "卡号", "进度", "操作"])
        splitter.addWidget(self.device_table)

        main_layout.addWidget(splitter)

        # 底部：统计信息和日志
        bottom_layout = QHBoxLayout()

        # 号码统计
        self.number_stats = QLabel("号码 统计: 141 成功: 1 异常: 5 编辑 未用: 48 占用: 87 超时: 0")
        bottom_layout.addWidget(self.number_stats)

        # 卡号统计
        self.card_stats = QLabel("卡号 统计: 66 成功: 1 异常: 1 编辑 未用: 0 占用: 53 等待: 11")
        bottom_layout.addWidget(self.card_stats)

        # 运行日志
        self.log_label = QLabel("运行日志\n2025-11-19 16:04:20 平台 => 设置 -> 成功\n...")
        bottom_layout.addWidget(self.log_label)

        main_layout.addLayout(bottom_layout)

        # 设置中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_service_data(self):
        # 请求服务列表接口
        url = QUrl("http://127.0.0.1:5000/host_api/v1/query_myt")
        request = QNetworkRequest(url)
        self.network_manager.get(request)

    def handle_reply(self, reply):
        url = reply.url().toString()
        if url.endswith("query_myt"):
            # 处理服务列表响应
            data = reply.readAll().data().decode()
            json_data = json.loads(data)
            if json_data.get("code") == 200:
                services = json_data.get("data", {})
                self.service_table.setRowCount(len(services))
                for row, (ip, _) in enumerate(services.items()):
                    # 模拟数据（根据实际业务补充数量、端口、运行状态）
                    self.service_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    self.service_table.setItem(row, 1, QTableWidgetItem(ip))
                    self.service_table.setItem(row, 2, QTableWidgetItem("0" if ip == "192.168.11.163" else "15"))
                    self.service_table.setItem(row, 3, QTableWidgetItem("0" if ip == "192.168.11.163" else "7100"))
                    self.service_table.setItem(row, 4, QTableWidgetItem("" if ip == "192.168.11.163" else "√"))
                # 加载对应IP的设备列表
                self.load_device_data("192.168.11.214")
        elif url.endswith("list/192.168.11.214"):
            # 处理设备列表响应
            data = reply.readAll().data().decode()
            json_data = json.loads(data)
            if json_data.get("code") == 200:
                devices = json_data.get("data", [])
                self.device_table.setRowCount(len(devices))
                for row, device in enumerate(devices):
                    self.device_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    self.device_table.setItem(row, 1, QTableWidgetItem(device.get("ip", "")))
                    self.device_table.setItem(row, 2, QTableWidgetItem(str(device.get("adb", ""))))
                    self.device_table.setItem(row, 3, QTableWidgetItem(str(device.get("api_port", ""))))
                    self.device_table.setItem(row, 4,
                                              QTableWidgetItem("在线" if row < 12 or row in [13, 14] else "离线"))
                    self.device_table.setItem(row, 5, QTableWidgetItem("√"))
                    self.device_table.setItem(row, 6, QTableWidgetItem(
                        device.get("name", "").split("_")[-1] if device.get("name") else ""))
                    self.device_table.setItem(row, 7, QTableWidgetItem(""))  # 卡号模拟
                    self.device_table.setItem(row, 8, QTableWidgetItem(""))  # 进度模拟

    def load_device_data(self, ip):
        # 请求设备列表接口
        url = QUrl(f"http://127.0.0.1:5000/dc_api/v1/list/{ip}")
        request = QNetworkRequest(url)
        self.network_manager.get(request)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeChatDeviceManager()
    window.show()
    sys.exit(app.exec())