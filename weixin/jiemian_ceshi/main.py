import sys
import json
from PyQt6.QtCore import (
    QObject, pyqtSignal, pyqtSlot, QUrl
)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

# 模拟从接口获取的 JSON 数据（你之前的实际数据）
SERVICE_JSON = {
    "code": 200,
    "data": {
        "192.168.11.163": "p8fe5e7ea13be7b5f2835f9aa3aac433",
        "192.168.11.214": "pcc5f3b6fcc1aff77c3385cee4ee944d"
    },
    "message": "success"
}

# 模拟 192.168.11.214 的设备详情 JSON（你提供的长列表，此处简化为3条示例）
DEVICE_JSON = {
    "code": 200,
    "data": [
        {
            "adb": 5001, "api_port": 10005, "ip": "192.168.11.214",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_1_70940889",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        },
        {
            "adb": 5002, "api_port": 10008, "ip": "192.168.11.214",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_2_94853717",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        },
        {
            "adb": 5003, "api_port": 10011, "ip": "192.168.11.214",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_3_95768373",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        }
    ],
    "message": "success"
}
DEVICE_JSON_163 = {
    "code": 200,
    "data": [
        {
            "adb": 111, "api_port": 10005, "ip": "192.168.11.163",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_1_70940889",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        },
        {
            "adb": 222, "api_port": 10008, "ip": "192.168.11.163",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_2_94853717",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        },
        {
            "adb": 333, "api_port": 10011, "ip": "192.168.11.163",
            "name": "p8fe5e7ea13be7b5f2835f9aa3aac433_3_95768373",
            "state": "exited", "status": "Exited (127) 46 hours ago",
            "width": "720", "height": "1280"
        }
    ],
    "message": "success"
}

# 定义与 QML 通信的后端类
class Backend(QObject):
    # 信号1：向 QML 发送服务列表 JSON 数据（字符串形式传递）
    sendServiceData = pyqtSignal(str)
    # 信号2：向 QML 发送设备详情 JSON 数据（字符串形式传递）
    sendDeviceData = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    # 槽函数1：QML 初始化后，主动请求服务列表
    @pyqtSlot()
    def requestServiceData(self):
        # 新增：打印发送的JSON数据，确认数据正确
        json_str = json.dumps(SERVICE_JSON)
        print(f"Python发送的服务列表数据：\n{json_str}")
        # 将 Python 字典转为 JSON 字符串，传递给 QML
        self.sendServiceData.emit(json_str)

    # 槽函数2：QML 点击左侧 IP 后，请求对应设备数据
    @pyqtSlot(str)
    def requestDeviceData(self, ip):
        print(f"Python接收的IP请求：{ip}") # 新增：打印接收的IP
        # 模拟根据 IP 筛选设备数据（实际可替换为接口请求）
        print("--",SERVICE_JSON["data"])
        if ip in DEVICE_JSON["data"]:
            print("214")
            self.sendDeviceData.emit(json.dumps(DEVICE_JSON))
        elif ip in DEVICE_JSON_163["data"]:
            print("163")
            self.sendDeviceData.emit(json.dumps(DEVICE_JSON_163))
        else:
            print("111")
            # 无数据时返回空
            self.sendDeviceData.emit(json.dumps({"code": 404, "data": [], "message": "IP不存在"}))

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # 初始化后端对象，并注册到 QML 上下文（QML 中通过 `backend` 调用）
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)

    # 加载 QML 文件（需与当前 Python 文件同目录，命名为 main.qml）
    # 优化：改用QUrl.fromLocalFile的绝对路径（可选，避免相对路径问题）
    import os
    qml_file = os.path.join(os.path.dirname(__file__), "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    print(f"加载的QML文件路径：{qml_file}") # 新增：打印QML路径

    # 检查 QML 加载是否成功
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())