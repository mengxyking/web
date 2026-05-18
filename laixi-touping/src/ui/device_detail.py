"""
设备详情窗口 — 内嵌投屏画面
- 左侧内嵌实时画面（QTimer 轮询镜像最新帧，30fps，不干扰主窗口缩略图）
- 鼠标点击 → tap，拖拽 → swipe
- 右侧：竖向排列的控制面板（参考来喜投屏布局）
"""
import threading
from typing import Optional

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit,
                              QWidget, QSizePolicy, QFrame, QGridLayout,
                              QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QPixmap, QImage

from ..core.screen_mirror import ScrcpyServerMirror, ScreenshotMirror, _SCRCPY_SERVER_LOCAL, _FFMPEG


class ScreenView(QLabel):
    """内嵌投屏画面 + 鼠标坐标映射"""
    tap_requested   = pyqtSignal(int, int)
    swipe_requested = pyqtSignal(int, int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(270, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background:#000; color:#555; font-size:13px;")
        self.setText("正在连接设备画面…")
        self._phys_w: int = 0
        self._phys_h: int = 0
        self._press_pos: Optional[QPoint] = None

    def set_device_resolution(self, w: int, h: int):
        if self._phys_w != w or self._phys_h != h:
            self._phys_w = w
            self._phys_h = h

    def show_frame(self, img):
        try:
            rgb = img.convert("RGB")
            enc_w, enc_h = rgb.size
            if not self._phys_w:
                self._phys_w, self._phys_h = enc_w, enc_h
            data = rgb.tobytes("raw", "RGB")
            qimg = QImage(data, enc_w, enc_h, enc_w * 3, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pix)
        except Exception:
            pass

    def _to_device(self, pos: QPoint):
        if not self._phys_w or not self._phys_h:
            return None, None
        ww, wh = self.width(), self.height()
        scale = min(ww / self._phys_w, wh / self._phys_h)
        img_w = int(self._phys_w * scale)
        img_h = int(self._phys_h * scale)
        ox = (ww - img_w) // 2
        oy = (wh - img_h) // 2
        lx = pos.x() - ox
        ly = pos.y() - oy
        if not (0 <= lx < img_w and 0 <= ly < img_h):
            return None, None
        return int(lx / img_w * self._phys_w), int(ly / img_h * self._phys_h)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_pos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or self._press_pos is None:
            return
        p0, p1 = self._press_pos, e.pos()
        dx, dy = p1.x() - p0.x(), p1.y() - p0.y()
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 8:
            x, y = self._to_device(p1)
            if x is not None:
                self.tap_requested.emit(x, y)
        else:
            x1, y1 = self._to_device(p0)
            x2, y2 = self._to_device(p1)
            if None not in (x1, x2):
                self.swipe_requested.emit(x1, y1, x2, y2, max(100, int(dist * 2)))
        self._press_pos = None


class DeviceDetailWindow(QDialog):
    _log_signal = pyqtSignal(str)

    def __init__(self, device, adb_manager, mirror_manager, parent=None):
        super().__init__(parent)
        self._device      = device
        self._adb         = adb_manager
        self._mirror_mgr  = mirror_manager
        self._mirror      = None
        self._owns_mirror = False

        self.setWindowTitle(f"{device.display_name()} — 控制面板")
        self.setMinimumSize(920, 640)
        self.setStyleSheet("background:#0d1117; color:#e0e0e0;")
        self._setup_ui()
        self._log_signal.connect(self._append_log)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_frame)
        self._attach_mirror()

    # ── UI ──────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧：投屏画面
        self._screen_view = ScreenView()
        dw = getattr(self._device, 'screen_width', 0)
        dh = getattr(self._device, 'screen_height', 0)
        if dw and dh:
            self._screen_view.set_device_resolution(dw, dh)
        self._screen_view.tap_requested.connect(self._on_tap)
        self._screen_view.swipe_requested.connect(self._on_swipe)
        root.addWidget(self._screen_view, stretch=1)

        # 右侧：竖向控制面板
        right = QWidget()
        right.setFixedWidth(260)
        right.setStyleSheet("background:#161b22; border-left:1px solid #21262d;")
        col = QVBoxLayout(right)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        col.addWidget(self._build_device_header())
        col.addWidget(self._divider())
        col.addWidget(self._build_nav_section())
        col.addWidget(self._divider())
        col.addWidget(self._build_input_section())
        col.addWidget(self._divider())
        col.addWidget(self._build_adb_section())
        col.addWidget(self._divider())
        col.addWidget(self._build_log_section(), stretch=1)
        col.addWidget(self._divider())
        col.addWidget(self._build_footer())

        root.addWidget(right)

    def _build_device_header(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        h = QHBoxLayout(w)
        h.setContentsMargins(12, 10, 12, 10)
        h.setSpacing(6)

        name_lbl = QLabel(self._device.display_name())
        name_lbl.setFont(QFont("Arial", 10, QFont.Bold))
        name_lbl.setStyleSheet("color:#e0e0e0;")
        name_lbl.setWordWrap(True)
        h.addWidget(name_lbl, stretch=1)

        self._status_label = QLabel("正在连接…")
        self._status_label.setStyleSheet(
            "color:#f0a500; font-size:10px; padding:2px 5px;"
            "background:#1a1200; border-radius:3px;")
        h.addWidget(self._status_label)
        return w

    def _build_nav_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(5)

        lbl = QLabel("导航按键")
        lbl.setStyleSheet("color:#888; font-size:10px;")
        v.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(5)
        nav_keys = [
            ("返回", 4,  0, 0), ("HOME", 3,   0, 1), ("菜单", 82, 0, 2),
            ("电源", 26, 1, 0), ("音量+", 24, 1, 1), ("音量-", 25, 1, 2),
        ]
        for name, code, row, col in nav_keys:
            btn = self._nav_btn(name, lambda _, c=code: self._key(c))
            grid.addWidget(btn, row, col)
        v.addLayout(grid)
        return w

    def _build_input_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(5)

        lbl = QLabel("文字输入")
        lbl.setStyleSheet("color:#888; font-size:10px;")
        v.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(4)
        self._text_input = QLineEdit()
        self._text_input.setPlaceholderText("输入文字…")
        self._text_input.setStyleSheet(self._input_style())
        self._text_input.returnPressed.connect(self._send_text)
        row.addWidget(self._text_input)
        row.addWidget(self._action_btn("发送", self._send_text, "#238636"))
        v.addLayout(row)
        return w

    def _build_adb_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(5)

        lbl = QLabel("ADB 指令")
        lbl.setStyleSheet("color:#888; font-size:10px;")
        v.addWidget(lbl)

        row1 = QHBoxLayout()
        row1.setSpacing(4)
        self._adb_input = QLineEdit()
        self._adb_input.setPlaceholderText("shell 指令…")
        self._adb_input.setStyleSheet(self._input_style())
        self._adb_input.returnPressed.connect(self._run_adb)
        row1.addWidget(self._adb_input)
        row1.addWidget(self._action_btn("执行", self._run_adb, "#0f3460"))
        v.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        for label, cmd in [("截图", "screencap /sdcard/screen.png"),
                            ("电量", "dumpsys battery|grep level"),
                            ("包名", "pm list packages")]:
            row2.addWidget(self._action_btn(label,
                                            lambda _, c=cmd: self._quick_adb(c),
                                            "#21262d"))
        v.addLayout(row2)
        return w

    def _build_log_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(5)

        lbl = QLabel("操作日志")
        lbl.setStyleSheet("color:#888; font-size:10px;")
        v.addWidget(lbl)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setStyleSheet(
            "background:#0a0a1a; color:#00ff41;"
            "font-family:monospace; font-size:10px; border:none;")
        v.addWidget(self._log, stretch=1)
        return w

    def _build_footer(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#161b22;")
        h = QHBoxLayout(w)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(6)
        h.addWidget(self._action_btn("重连投屏", self._reattach, "#0f3460"))
        h.addStretch()
        h.addWidget(self._action_btn("关闭", self.close, "#555"))
        return w

    @staticmethod
    def _divider() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("background:#21262d; border:none;")
        return line

    @staticmethod
    def _nav_btn(text, slot=None) -> QPushButton:
        b = QPushButton(text)
        b.setFixedHeight(34)
        b.setStyleSheet("""
            QPushButton {
                background:#21262d; color:#e0e0e0;
                border:none; border-radius:4px; font-size:11px;
            }
            QPushButton:hover { background:#30363d; }
            QPushButton:pressed { background:#0f3460; }
        """)
        if slot:
            b.clicked.connect(slot)
        return b

    @staticmethod
    def _action_btn(text, slot=None, color="#e94560") -> QPushButton:
        b = QPushButton(text)
        b.setFixedHeight(30)
        b.setStyleSheet(f"""
            QPushButton {{
                background:{color}; color:white;
                border:none; border-radius:4px;
                padding:0 10px; font-size:11px;
            }}
            QPushButton:hover {{ background:#30363d; }}
            QPushButton:pressed {{ background:#0d1117; }}
        """)
        if slot:
            b.clicked.connect(slot)
        return b

    @staticmethod
    def _input_style() -> str:
        return ("background:#0d1117; color:#e0e0e0; border:1px solid #30363d;"
                "border-radius:4px; padding:4px 8px; font-size:11px;")

    # ── 投屏连接 ─────────────────────────────────────────────────────────────

    def _attach_mirror(self):
        self._poll_timer.stop()
        serial = self._device.serial

        existing = self._mirror_mgr.get_mirror(serial)
        if existing:
            self._mirror = existing
            self._owns_mirror = False
            self._set_status("复用投屏流", False)
        else:
            w = getattr(self._device, 'screen_width', 0)
            h = getattr(self._device, 'screen_height', 0)
            if _SCRCPY_SERVER_LOCAL and _FFMPEG:
                self._mirror = ScrcpyServerMirror(serial, w, h)
            else:
                self._mirror = ScreenshotMirror(self._adb, serial)
            self._mirror.start()
            self._owns_mirror = True
            self._set_status("正在启动投屏…", False)

        self._poll_timer.start(33)

    def _reattach(self):
        self._poll_timer.stop()
        if self._owns_mirror and self._mirror:
            self._mirror.stop()
        self._mirror = None
        self._owns_mirror = False
        self._attach_mirror()

    def _poll_frame(self):
        if self._mirror is None:
            return
        dw = getattr(self._device, 'screen_width', 0)
        dh = getattr(self._device, 'screen_height', 0)
        if dw and dh:
            self._screen_view.set_device_resolution(dw, dh)
        img = self._mirror.get_last_frame()
        if img is not None:
            self._screen_view.show_frame(img)
            pw, ph = self._screen_view._phys_w, self._screen_view._phys_h
            self._set_status(f"● 投屏中  {pw}×{ph}", False)

    # ── 鼠标 → ADB ──────────────────────────────────────────────────────────

    def _on_tap(self, x: int, y: int):
        serial = self._device.serial
        pw, ph = self._screen_view._phys_w, self._screen_view._phys_h
        self._log_signal.emit(f"[tap] ({x},{y})  {pw}×{ph}")
        def _do():
            out = self._adb.shell(serial, f"input tap {x} {y}")
            if out.strip():
                self._log_signal.emit(f"  → {out.strip()}")
        threading.Thread(target=_do, daemon=True).start()

    def _on_swipe(self, x1: int, y1: int, x2: int, y2: int, dur: int):
        threading.Thread(
            target=self._adb.swipe,
            args=(self._device.serial, x1, y1, x2, y2, dur), daemon=True
        ).start()
        self._log_signal.emit(f"[swipe] ({x1},{y1})→({x2},{y2}) {dur}ms")

    # ── 按键 / 输入 / ADB ────────────────────────────────────────────────────

    def _key(self, code: int):
        threading.Thread(
            target=self._adb.key_event, args=(self._device.serial, code), daemon=True
        ).start()

    def _send_text(self):
        text = self._text_input.text().strip()
        if not text:
            return
        threading.Thread(
            target=self._adb.input_text, args=(self._device.serial, text), daemon=True
        ).start()
        self._log_signal.emit(f"[输入] {text}")
        self._text_input.clear()

    def _run_adb(self):
        cmd = self._adb_input.text().strip()
        if not cmd:
            return
        self._log_signal.emit(f"$ {cmd}")
        def _exec():
            out = self._adb.shell(self._device.serial, cmd)
            self._log_signal.emit(out.strip() if out.strip() else "(无输出)")
        threading.Thread(target=_exec, daemon=True).start()

    def _quick_adb(self, cmd: str):
        self._adb_input.setText(cmd)
        self._run_adb()

    # ── 状态 / 日志 ──────────────────────────────────────────────────────────

    def _set_status(self, msg: str, error: bool = False):
        color = "#e94560" if error else "#4CAF50"
        bg    = "#1a0010" if error else "#001a0a"
        self._status_label.setText(msg)
        self._status_label.setStyleSheet(
            f"color:{color}; font-size:10px; padding:2px 5px;"
            f"background:{bg}; border-radius:3px;")

    def _append_log(self, text: str):
        self._log.append(text)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum())

    def closeEvent(self, event):
        self._poll_timer.stop()
        if self._owns_mirror and self._mirror:
            self._mirror.stop()
        event.accept()
