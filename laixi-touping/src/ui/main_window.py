"""主窗口"""
import threading
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QScrollArea, QLabel, QPushButton, QCheckBox,
                              QStatusBar, QToolBar, QAction, QMessageBox,
                              QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon

from .device_card import DeviceCard
from .control_panel import ControlPanel
from .wifi_connect_dialog import WifiConnectDialog
from .device_detail import DeviceDetailWindow
from ..core.screen_mirror import MirrorManager
from ..core.task_manager import TaskManager, TaskType
from ..utils.quick_reply import QuickReplyManager


class Signals(QObject):
    devices_changed = pyqtSignal(list)
    frame_received = pyqtSignal(str, object)
    log_message = pyqtSignal(str, str)  # category, message


class MainWindow(QMainWindow):
    def __init__(self, adb_manager):
        super().__init__()
        self._adb = adb_manager
        self._signals = Signals()
        self._device_cards: dict[str, DeviceCard] = {}
        self._selected_serials: set[str] = set()
        self._mirror_mgr = MirrorManager(adb_manager)
        self._task_mgr = TaskManager()
        self._qr_mgr = QuickReplyManager("quick_replies.json")

        self._setup_ui()
        self._connect_signals()
        self._adb.add_callback(lambda devs: self._signals.devices_changed.emit(devs))
        self._adb.start_monitor()

        # 定时刷新任务列表
        self._task_refresh_timer = QTimer(self)
        self._task_refresh_timer.timeout.connect(self._control_panel.refresh_tasks)
        self._task_refresh_timer.start(3000)

    def _setup_ui(self):
        self.setWindowTitle("来喜投屏 - Android群控管理系统")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("background: #0d1117; color: #e0e0e0;")

        # 工具栏
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("background: #161b22; border-bottom: 1px solid #21262d; padding: 4px;")
        self.addToolBar(toolbar)

        def make_action(text, slot, color="#e94560"):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color}; color: white;
                    border: none; border-radius: 4px;
                    padding: 6px 14px; margin: 2px; font-size: 12px;
                }}
                QPushButton:hover {{ opacity: 0.8; }}
            """)
            btn.clicked.connect(slot)
            return btn

        toolbar.addWidget(make_action("刷新设备", self._refresh_devices, "#21262d"))
        toolbar.addWidget(make_action("WiFi连接", self._wifi_connect, "#0f3460"))
        toolbar.addWidget(make_action("全选", self._select_all, "#21262d"))
        toolbar.addWidget(make_action("全不选", self._deselect_all, "#21262d"))
        toolbar.addWidget(make_action("开启全部投屏", self._start_all_mirror, "#238636"))
        toolbar.addWidget(make_action("停止全部投屏", self._stop_all_mirror, "#555"))

        self._selected_count_label = QLabel("已选: 0 台 | 连接: 0 台")
        self._selected_count_label.setStyleSheet("color: #aaa; margin-left: 10px; font-size: 12px;")
        toolbar.addWidget(self._selected_count_label)

        # 主内容区
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet("QSplitter::handle { background: #21262d; }")

        # 左侧：设备列表
        left_frame = QFrame()
        left_frame.setStyleSheet("background: #0d1117;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(8, 8, 8, 8)

        device_header = QHBoxLayout()
        dev_title = QLabel("设备列表")
        dev_title.setFont(QFont("Arial", 13, QFont.Bold))
        dev_title.setStyleSheet("color: #e0e0e0;")
        device_header.addWidget(dev_title)
        left_layout.addLayout(device_header)

        self._device_scroll = QScrollArea()
        self._device_scroll.setWidgetResizable(True)
        self._device_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._device_scroll.setStyleSheet("border: none; background: #0d1117;")

        self._device_container = QWidget()
        self._device_layout = QHBoxLayout(self._device_container)
        self._device_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._device_layout.setSpacing(8)
        self._device_layout.setContentsMargins(4, 4, 4, 4)

        no_device = QLabel("暂无连接设备\n\n请使用USB连接Android设备\n或使用WiFi连接功能")
        no_device.setAlignment(Qt.AlignCenter)
        no_device.setStyleSheet("color: #555; font-size: 14px;")
        self._no_device_label = no_device
        self._device_layout.addWidget(no_device)

        self._device_scroll.setWidget(self._device_container)
        left_layout.addWidget(self._device_scroll)

        # 右侧：控制面板
        right_frame = QFrame()
        right_frame.setStyleSheet("background: #161b22; border-left: 1px solid #21262d;")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_title = QLabel("群控操作面板")
        right_title.setFont(QFont("Arial", 13, QFont.Bold))
        right_title.setStyleSheet("color: #e0e0e0; padding: 10px 12px; background: #161b22; border-bottom: 1px solid #21262d;")
        right_layout.addWidget(right_title)

        self._control_panel = ControlPanel(self._adb, self._task_mgr, self._qr_mgr)
        right_layout.addWidget(self._control_panel)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([800, 400])

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

        # 状态栏
        status_bar = QStatusBar()
        status_bar.setStyleSheet("background: #161b22; color: #aaa; border-top: 1px solid #21262d;")
        self.setStatusBar(status_bar)
        self._status_bar = status_bar
        self._status_bar.showMessage("就绪 | ADB已启动")

    def _connect_signals(self):
        self._signals.devices_changed.connect(self._on_devices_changed)
        self._signals.frame_received.connect(self._on_frame_received)
        self._signals.log_message.connect(self._on_log_message)

        cp = self._control_panel
        cp.do_tap.connect(self._on_tap)
        cp.do_swipe.connect(self._on_swipe)
        cp.do_input_text.connect(self._on_input_text)
        cp.do_keyevent.connect(self._on_keyevent)
        cp.do_shell.connect(self._on_shell)
        cp.do_install_apk.connect(self._on_install_apk)
        cp.do_push_file.connect(self._on_push_file)

    def _get_targets(self) -> list:
        if self._selected_serials:
            return list(self._selected_serials)
        return [d.serial for d in self._adb.get_devices()]

    def _on_devices_changed(self, devices):
        serials = {d.serial for d in devices}

        # 移除断开的设备卡片
        for s in list(self._device_cards.keys()):
            if s not in serials:
                card = self._device_cards.pop(s)
                card.setParent(None)
                card.deleteLater()
                self._selected_serials.discard(s)
                self._mirror_mgr.stop_mirror(s)

        # 添加新设备卡片，并自动开始镜像
        for dev in devices:
            if dev.serial not in self._device_cards:
                card = DeviceCard(dev)
                card.selected_changed.connect(self._on_card_selected)
                card.clicked.connect(self._on_card_clicked)
                card.double_clicked.connect(self._on_card_double_clicked)
                self._device_cards[dev.serial] = card
                self._device_layout.addWidget(card)
                self._start_mirror_for(dev.serial, dev)

        # 更新设备信息
        for dev in devices:
            if dev.serial in self._device_cards:
                self._device_cards[dev.serial].update_device_info()

        # 显示/隐藏无设备提示
        if self._device_cards:
            self._no_device_label.hide()
        else:
            self._no_device_label.show()

        self._update_status_count()

    def _on_frame_received(self, serial: str, img):
        if serial in self._device_cards:
            self._device_cards[serial].update_frame(img)

    def _on_log_message(self, category: str, msg: str):
        if category == "adb":
            self._control_panel.append_adb_log(msg)
        elif category == "file":
            self._control_panel.append_file_log(msg)
        elif category == "mirror_err":
            self._status_bar.showMessage(msg)

    def _on_card_selected(self, serial: str, selected: bool):
        if selected:
            self._selected_serials.add(serial)
        else:
            self._selected_serials.discard(serial)
        self._update_status_count()

    def _on_card_clicked(self, serial: str):
        pass

    def _on_card_double_clicked(self, serial: str):
        device = self._adb.get_device(serial)
        if not device:
            return
        dlg = DeviceDetailWindow(device, self._adb, self._mirror_mgr, parent=self)
        dlg.show()  # 非模态，可同时开多个

    def _start_mirror_for(self, serial: str, device=None):
        def _cb(s, img):
            self._signals.frame_received.emit(s, img)

        def _err_cb(s, msg):
            self._signals.log_message.emit("mirror_err", f"[{s}] 投屏错误: {msg}")

        self._mirror_mgr.start_mirror(serial, device=device, callback=_cb, error_callback=_err_cb)

    def _update_status_count(self):
        total = len(self._device_cards)
        selected = len(self._selected_serials)
        self._selected_count_label.setText(f"已选: {selected} 台 | 连接: {total} 台")

    def _refresh_devices(self):
        self._adb.refresh_devices()
        self._status_bar.showMessage("已刷新设备列表")

    def _wifi_connect(self):
        dlg = WifiConnectDialog(self._adb, self)
        dlg.exec_()

    def _select_all(self):
        for card in self._device_cards.values():
            card.set_selected(True)

    def _deselect_all(self):
        for card in self._device_cards.values():
            card.set_selected(False)

    def _start_all_mirror(self):
        for serial, card in self._device_cards.items():
            self._start_mirror_for(serial, card.device)
        self._status_bar.showMessage("已开启全部设备投屏")

    def _stop_all_mirror(self):
        self._mirror_mgr.stop_all()
        self._status_bar.showMessage("已停止全部投屏")

    # ---- 群控操作 ----

    def _on_tap(self, x, y):
        targets = self._get_targets()
        if not targets:
            self._status_bar.showMessage("没有可操作的设备")
            return
        threading.Thread(target=self._adb.batch_tap, args=(targets, x, y), daemon=True).start()
        self._status_bar.showMessage(f"批量点击 ({x},{y}) → {len(targets)} 台设备")

    def _on_swipe(self, x1, y1, x2, y2, dur):
        targets = self._get_targets()
        if not targets:
            return
        threading.Thread(target=self._adb.batch_swipe, args=(targets, x1, y1, x2, y2, dur), daemon=True).start()
        self._status_bar.showMessage(f"批量滑动 → {len(targets)} 台设备")

    def _on_input_text(self, text):
        targets = self._get_targets()
        if not targets or not text:
            return
        threading.Thread(target=self._adb.batch_input_text, args=(targets, text), daemon=True).start()
        self._status_bar.showMessage(f"批量输入 '{text}' → {len(targets)} 台设备")

    def _on_keyevent(self, code):
        targets = self._get_targets()
        if not targets:
            return
        def run():
            for s in targets:
                self._adb.key_event(s, code)
        threading.Thread(target=run, daemon=True).start()
        self._status_bar.showMessage(f"批量按键 keyevent {code} → {len(targets)} 台设备")

    def _on_shell(self, cmd):
        targets = self._get_targets()
        if not targets or not cmd:
            return
        def run():
            results = self._adb.batch_shell(targets, cmd)
            for serial, output in results.items():
                msg = f"[{serial}] $ {cmd}\n{output}\n{'─'*40}"
                self._signals.log_message.emit("adb", msg)
        threading.Thread(target=run, daemon=True).start()
        self._status_bar.showMessage(f"执行指令: {cmd} → {len(targets)} 台设备")

    def _on_install_apk(self, path):
        targets = self._get_targets()
        if not targets or not path:
            self._status_bar.showMessage("请选择APK文件")
            return
        def cb(serial, success, output):
            status = "成功" if success else "失败"
            self._signals.log_message.emit("file", f"[{serial}] 安装 {status}\n{output}")
        self._adb.batch_install_apk(targets, path, cb)
        self._status_bar.showMessage(f"正在为 {len(targets)} 台设备安装APK...")

    def _on_push_file(self, local, remote):
        targets = self._get_targets()
        if not targets or not local or not remote:
            self._status_bar.showMessage("请填写文件路径")
            return
        def cb(serial, success, output):
            status = "成功" if success else "失败"
            self._signals.log_message.emit("file", f"[{serial}] 推送 {status}")
        self._adb.batch_push_file(targets, local, remote, cb)
        self._status_bar.showMessage(f"正在推送文件到 {len(targets)} 台设备...")

    def closeEvent(self, event):
        self._mirror_mgr.stop_all()
        self._adb.stop_monitor()
        self._task_mgr.stop_all()
        event.accept()
