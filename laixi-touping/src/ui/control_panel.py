"""群控操作面板"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLineEdit, QLabel, QTextEdit, QGroupBox,
                              QFileDialog, QComboBox, QSpinBox, QTabWidget,
                              QListWidget, QListWidgetItem, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ControlPanel(QWidget):
    # 信号：通知主窗口执行操作
    do_tap = pyqtSignal(int, int)
    do_swipe = pyqtSignal(int, int, int, int, int)
    do_input_text = pyqtSignal(str)
    do_keyevent = pyqtSignal(int)
    do_shell = pyqtSignal(str)
    do_install_apk = pyqtSignal(str)
    do_push_file = pyqtSignal(str, str)
    do_pull_file = pyqtSignal(str, str)

    def __init__(self, adb_manager, task_manager, quick_reply_manager, parent=None):
        super().__init__(parent)
        self._adb = adb_manager
        self._task_mgr = task_manager
        self._qr_mgr = quick_reply_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        tabs = QTabWidget()
        tabs.addTab(self._build_control_tab(), "群控操作")
        tabs.addTab(self._build_adb_tab(), "ADB指令")
        tabs.addTab(self._build_file_tab(), "文件管理")
        tabs.addTab(self._build_quick_reply_tab(), "快捷话术")
        tabs.addTab(self._build_task_tab(), "定时任务")

        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #0f3460; background: #16213e; }
            QTabBar::tab { background: #0f3460; color: #aaa; padding: 6px 12px; }
            QTabBar::tab:selected { background: #e94560; color: white; }
        """)

        layout.addWidget(tabs)

    def _btn(self, text, color="#e94560") -> QPushButton:
        b = QPushButton(text)
        b.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 4px;
                padding: 6px 12px; font-size: 12px;
            }}
            QPushButton:hover {{ background: #c73652; }}
            QPushButton:pressed {{ background: #a02040; }}
        """)
        return b

    def _input(self, placeholder="") -> QLineEdit:
        e = QLineEdit()
        e.setPlaceholderText(placeholder)
        e.setStyleSheet("""
            QLineEdit {
                background: #0f3460; color: #e0e0e0;
                border: 1px solid #1a4a80; border-radius: 4px;
                padding: 4px 8px;
            }
        """)
        return e

    def _label(self, text) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("color: #aaa; font-size: 11px;")
        return l

    def _build_control_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # 点击
        tap_box = QGroupBox("点击操作")
        tap_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                              "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        tap_layout = QHBoxLayout(tap_box)
        self.tap_x = QSpinBox()
        self.tap_x.setRange(0, 9999)
        self.tap_x.setPrefix("X: ")
        self.tap_y = QSpinBox()
        self.tap_y.setRange(0, 9999)
        self.tap_y.setPrefix("Y: ")
        for sp in [self.tap_x, self.tap_y]:
            sp.setStyleSheet("background: #0f3460; color: #e0e0e0; border: 1px solid #1a4a80; padding: 2px;")
        tap_btn = self._btn("批量点击")
        tap_btn.clicked.connect(lambda: self.do_tap.emit(self.tap_x.value(), self.tap_y.value()))
        tap_layout.addWidget(self.tap_x)
        tap_layout.addWidget(self.tap_y)
        tap_layout.addWidget(tap_btn)
        layout.addWidget(tap_box)

        # 滑动
        swipe_box = QGroupBox("滑动操作")
        swipe_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                                "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        swipe_layout = QVBoxLayout(swipe_box)
        row1 = QHBoxLayout()
        self.swipe_x1 = QSpinBox()
        self.swipe_x1.setRange(0, 9999)
        self.swipe_x1.setPrefix("X1: ")
        self.swipe_y1 = QSpinBox()
        self.swipe_y1.setRange(0, 9999)
        self.swipe_y1.setPrefix("Y1: ")
        self.swipe_x2 = QSpinBox()
        self.swipe_x2.setRange(0, 9999)
        self.swipe_x2.setPrefix("X2: ")
        self.swipe_y2 = QSpinBox()
        self.swipe_y2.setRange(0, 9999)
        self.swipe_y2.setPrefix("Y2: ")
        self.swipe_dur = QSpinBox()
        self.swipe_dur.setRange(100, 5000)
        self.swipe_dur.setValue(300)
        self.swipe_dur.setSuffix("ms")
        for sp in [self.swipe_x1, self.swipe_y1, self.swipe_x2, self.swipe_y2, self.swipe_dur]:
            sp.setStyleSheet("background: #0f3460; color: #e0e0e0; border: 1px solid #1a4a80; padding: 2px;")
        row1.addWidget(self.swipe_x1)
        row1.addWidget(self.swipe_y1)
        row1.addWidget(self.swipe_x2)
        row1.addWidget(self.swipe_y2)
        row1.addWidget(self.swipe_dur)
        swipe_btn = self._btn("批量滑动")
        swipe_btn.clicked.connect(lambda: self.do_swipe.emit(
            self.swipe_x1.value(), self.swipe_y1.value(),
            self.swipe_x2.value(), self.swipe_y2.value(),
            self.swipe_dur.value()
        ))
        swipe_layout.addLayout(row1)
        swipe_layout.addWidget(swipe_btn)
        layout.addWidget(swipe_box)

        # 文字输入
        text_box = QGroupBox("文字输入")
        text_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                               "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        text_layout = QHBoxLayout(text_box)
        self.input_text_edit = self._input("输入文字内容...")
        text_btn = self._btn("批量输入")
        text_btn.clicked.connect(lambda: self.do_input_text.emit(self.input_text_edit.text()))
        text_layout.addWidget(self.input_text_edit)
        text_layout.addWidget(text_btn)
        layout.addWidget(text_box)

        # 按键
        key_box = QGroupBox("按键操作")
        key_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                              "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        key_layout = QHBoxLayout(key_box)
        for name, code in [("返回", 4), ("HOME", 3), ("菜单", 82), ("电源", 26), ("音量+", 24), ("音量-", 25)]:
            b = self._btn(name, "#0f3460")
            b.clicked.connect(lambda _, c=code: self.do_keyevent.emit(c))
            key_layout.addWidget(b)
        layout.addWidget(key_box)

        layout.addStretch()
        return w

    def _build_adb_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(self._label("输入ADB Shell指令："))
        self.adb_input = self._input("例如：pm list packages")
        layout.addWidget(self.adb_input)

        btn_row = QHBoxLayout()
        run_btn = self._btn("批量执行")
        run_btn.clicked.connect(lambda: self.do_shell.emit(self.adb_input.text()))
        clear_btn = self._btn("清空日志", "#555")
        clear_btn.clicked.connect(lambda: self.adb_log.clear())
        btn_row.addWidget(run_btn)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

        layout.addWidget(self._label("常用指令："))
        quick_cmds = QHBoxLayout()
        for label, cmd in [("重启", "reboot"), ("截图", "screencap /sdcard/screen.png"),
                            ("查包", "pm list packages"), ("电量", "dumpsys battery | grep level")]:
            b = self._btn(label, "#0f3460")
            b.clicked.connect(lambda _, c=cmd: self._quick_cmd(c))
            quick_cmds.addWidget(b)
        layout.addLayout(quick_cmds)

        layout.addWidget(self._label("执行结果："))
        self.adb_log = QTextEdit()
        self.adb_log.setReadOnly(True)
        self.adb_log.setStyleSheet("background: #0a0a1a; color: #00ff41; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.adb_log)

        return w

    def _quick_cmd(self, cmd: str):
        self.adb_input.setText(cmd)
        self.do_shell.emit(cmd)

    def append_adb_log(self, text: str):
        self.adb_log.append(text)

    def _build_file_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # 安装APK
        apk_box = QGroupBox("批量安装APK")
        apk_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                              "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        apk_layout = QHBoxLayout(apk_box)
        self.apk_path = self._input("APK文件路径...")
        browse_apk = self._btn("浏览", "#0f3460")
        browse_apk.clicked.connect(self._browse_apk)
        install_btn = self._btn("批量安装")
        install_btn.clicked.connect(lambda: self.do_install_apk.emit(self.apk_path.text()))
        apk_layout.addWidget(self.apk_path)
        apk_layout.addWidget(browse_apk)
        apk_layout.addWidget(install_btn)
        layout.addWidget(apk_box)

        # 推送文件
        push_box = QGroupBox("批量推送文件")
        push_box.setStyleSheet("QGroupBox { color: #e0e0e0; border: 1px solid #0f3460; margin-top: 8px; }"
                               "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        push_layout = QVBoxLayout(push_box)
        row1 = QHBoxLayout()
        self.push_local = self._input("本地文件路径...")
        browse_push = self._btn("浏览", "#0f3460")
        browse_push.clicked.connect(self._browse_push)
        row1.addWidget(self.push_local)
        row1.addWidget(browse_push)
        row2 = QHBoxLayout()
        self.push_remote = self._input("设备路径 (例如: /sdcard/Download/)")
        push_btn = self._btn("批量推送")
        push_btn.clicked.connect(lambda: self.do_push_file.emit(
            self.push_local.text(), self.push_remote.text()
        ))
        row2.addWidget(self.push_remote)
        row2.addWidget(push_btn)
        push_layout.addLayout(row1)
        push_layout.addLayout(row2)
        layout.addWidget(push_box)

        # 文件操作日志
        layout.addWidget(self._label("操作日志："))
        self.file_log = QTextEdit()
        self.file_log.setReadOnly(True)
        self.file_log.setStyleSheet("background: #0a0a1a; color: #00ff41; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.file_log)

        return w

    def _browse_apk(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择APK", "", "APK文件 (*.apk)")
        if path:
            self.apk_path.setText(path)

    def _browse_push(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if path:
            self.push_local.setText(path)

    def append_file_log(self, text: str):
        self.file_log.append(text)

    def _build_quick_reply_tab(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)

        # 分组列表
        left = QVBoxLayout()
        left.addWidget(self._label("话术分组："))
        self.group_list = QListWidget()
        self.group_list.setStyleSheet("background: #0f3460; color: #e0e0e0; border: none;")
        self.group_list.currentTextChanged.connect(self._on_group_select)
        left.addWidget(self.group_list)
        row = QHBoxLayout()
        add_grp = self._btn("+分组", "#0f3460")
        add_grp.clicked.connect(self._add_group)
        del_grp = self._btn("-分组", "#555")
        del_grp.clicked.connect(self._del_group)
        row.addWidget(add_grp)
        row.addWidget(del_grp)
        left.addLayout(row)

        # 话术列表
        right = QVBoxLayout()
        right.addWidget(self._label("话术内容："))
        self.reply_list = QListWidget()
        self.reply_list.setStyleSheet("background: #0f3460; color: #e0e0e0; border: none;")
        right.addWidget(self.reply_list)

        btn_row = QHBoxLayout()
        send_btn = self._btn("发送所选话术")
        send_btn.clicked.connect(self._send_reply)
        add_reply = self._btn("+话术", "#0f3460")
        add_reply.clicked.connect(self._add_reply)
        del_reply = self._btn("-话术", "#555")
        del_reply.clicked.connect(self._del_reply)
        btn_row.addWidget(send_btn)
        btn_row.addWidget(add_reply)
        btn_row.addWidget(del_reply)
        right.addLayout(btn_row)

        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        self._refresh_groups()
        return w

    def _refresh_groups(self):
        self.group_list.clear()
        for g in self._qr_mgr.get_groups():
            self.group_list.addItem(g.name)

    def _on_group_select(self, name: str):
        self.reply_list.clear()
        for g in self._qr_mgr.get_groups():
            if g.name == name:
                for r in g.replies:
                    self.reply_list.addItem(r)
                break

    def _add_group(self):
        text, ok = QInputDialog.getText(self, "新建分组", "分组名称：")
        if ok and text:
            self._qr_mgr.add_group(text)
            self._refresh_groups()

    def _del_group(self):
        item = self.group_list.currentItem()
        if item:
            self._qr_mgr.remove_group(item.text())
            self._refresh_groups()

    def _add_reply(self):
        group = self.group_list.currentItem()
        if not group:
            return
        text, ok = QInputDialog.getText(self, "新建话术", "话术内容：")
        if ok and text:
            self._qr_mgr.add_reply(group.text(), text)
            self._on_group_select(group.text())

    def _del_reply(self):
        group = self.group_list.currentItem()
        reply = self.reply_list.currentItem()
        if group and reply:
            self._qr_mgr.remove_reply(group.text(), reply.text())
            self._on_group_select(group.text())

    def _send_reply(self):
        item = self.reply_list.currentItem()
        if item:
            self.do_input_text.emit(item.text())

    def _build_task_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(self._label("定时/循环任务管理"))

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background: #0f3460; color: #e0e0e0; border: none;")
        layout.addWidget(self.task_list)

        btn_row = QHBoxLayout()
        stop_btn = self._btn("停止所选任务", "#555")
        stop_btn.clicked.connect(self._stop_selected_task)
        refresh_btn = self._btn("刷新", "#0f3460")
        refresh_btn.clicked.connect(self.refresh_tasks)
        btn_row.addWidget(stop_btn)
        btn_row.addWidget(refresh_btn)
        layout.addLayout(btn_row)

        layout.addStretch()
        return w

    def refresh_tasks(self):
        self.task_list.clear()
        for t in self._task_mgr.get_tasks():
            text = f"[{t.id}] {t.name} - {t.status.value} (执行{t.run_count}次)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, t.id)
            self.task_list.addItem(item)

    def _stop_selected_task(self):
        item = self.task_list.currentItem()
        if item:
            tid = item.data(Qt.UserRole)
            self._task_mgr.stop_task(tid)
            self.refresh_tasks()
