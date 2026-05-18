"""单设备显示卡片"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QCheckBox, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PIL import Image
import io


def pil_to_qpixmap(img: Image.Image, max_w: int, max_h: int) -> QPixmap:
    img = img.convert("RGB")
    img.thumbnail((max_w, max_h), Image.BILINEAR)
    data = img.tobytes("raw", "RGB")
    qimg = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


class DeviceCard(QFrame):
    selected_changed = pyqtSignal(str, bool)  # serial, selected
    clicked = pyqtSignal(str)
    double_clicked = pyqtSignal(str)

    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.device = device
        self._current_frame = None
        self._selected = False
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setFixedWidth(180)
        self.setMinimumHeight(280)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        top = QHBoxLayout()
        self.check = QCheckBox()
        self.check.stateChanged.connect(self._on_check)
        top.addWidget(self.check)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #4CAF50; font-size: 10px;")
        top.addWidget(self.status_dot)
        top.addStretch()
        layout.addLayout(top)

        # 屏幕预览区
        self.screen_label = QLabel()
        self.screen_label.setFixedSize(160, 200)
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.screen_label.setStyleSheet("background: #1a1a2e; border-radius: 4px;")
        self.screen_label.setText("等待截图...")
        self.screen_label.setFont(QFont("Arial", 8))
        layout.addWidget(self.screen_label, alignment=Qt.AlignCenter)

        # 设备名
        self.name_label = QLabel(self.device.display_name())
        self.name_label.setFont(QFont("Arial", 8))
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)

        # 系统信息
        self.info_label = QLabel("Android " + (self.device.android_version or "?"))
        self.info_label.setFont(QFont("Arial", 7))
        self.info_label.setStyleSheet("color: gray;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.setStyleSheet("""
            DeviceCard {
                background: #16213e;
                border: 1px solid #0f3460;
                border-radius: 8px;
            }
            DeviceCard:hover {
                border: 1px solid #e94560;
            }
            QLabel { color: #e0e0e0; }
        """)

    def update_frame(self, img: Image.Image):
        self._current_frame = img
        px = pil_to_qpixmap(img, 160, 200)
        self.screen_label.setPixmap(px)
        self.screen_label.setText("")

    def update_device_info(self):
        self.name_label.setText(self.device.display_name())
        self.info_label.setText("Android " + (self.device.android_version or "?"))

    def _on_check(self, state):
        self._selected = (state == Qt.Checked)
        self.selected_changed.emit(self.device.serial, self._selected)
        self._update_style()

    def _update_style(self):
        if self._selected:
            self.setStyleSheet("""
                DeviceCard {
                    background: #16213e;
                    border: 2px solid #e94560;
                    border-radius: 8px;
                }
                QLabel { color: #e0e0e0; }
            """)
        else:
            self.setStyleSheet("""
                DeviceCard {
                    background: #16213e;
                    border: 1px solid #0f3460;
                    border-radius: 8px;
                }
                DeviceCard:hover {
                    border: 1px solid #e94560;
                }
                QLabel { color: #e0e0e0; }
            """)

    def set_selected(self, val: bool):
        self.check.setChecked(val)

    def is_selected(self) -> bool:
        return self._selected

    def mousePressEvent(self, event):
        self.clicked.emit(self.device.serial)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.device.serial)
        super().mouseDoubleClickEvent(event)
