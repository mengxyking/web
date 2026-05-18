"""来喜投屏 - Android群控管理系统入口"""
import sys
import os

# 确保能找到src模块
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor

from src.core.adb_manager import AdbManager
from src.ui.main_window import MainWindow


def check_dependencies():
    missing = []
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")
    return missing


def create_splash() -> QSplashScreen:
    px = QPixmap(500, 300)
    px.fill(QColor("#0d1117"))
    painter = QPainter(px)
    painter.setPen(QColor("#e94560"))
    painter.setFont(QFont("Arial", 36, QFont.Bold))
    painter.drawText(px.rect(), Qt.AlignCenter, "来喜投屏")
    painter.setPen(QColor("#aaa"))
    painter.setFont(QFont("Arial", 14))
    painter.drawText(0, 220, 500, 40, Qt.AlignCenter, "Android群控管理系统 - 正在启动...")
    painter.end()
    splash = QSplashScreen(px)
    return splash


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("来喜投屏")
    app.setOrganizationName("LaixiTouping")
    app.setFont(QFont("Microsoft YaHei", 10))

    # 检查依赖
    missing = check_dependencies()
    if missing:
        QMessageBox.critical(None, "缺少依赖",
                             f"请先安装以下依赖:\n{chr(10).join(missing)}\n\npip install {' '.join(missing)}")
        sys.exit(1)

    # 启动画面
    splash = create_splash()
    splash.show()
    app.processEvents()

    # 初始化ADB
    adb_manager = AdbManager()
    splash.showMessage("正在启动ADB服务...", Qt.AlignBottom | Qt.AlignCenter, QColor("#aaa"))
    app.processEvents()
    AdbManager.start_server()

    if not AdbManager.check_adb():
        splash.close()
        QMessageBox.warning(None, "ADB未找到",
                            "未检测到ADB工具！\n\n请安装Android SDK Platform-Tools并添加到系统PATH。\n\n"
                            "下载地址: https://developer.android.com/studio/releases/platform-tools\n\n"
                            "程序将继续运行，但部分功能不可用。")

    # 创建主窗口
    splash.showMessage("正在加载界面...", Qt.AlignBottom | Qt.AlignCenter, QColor("#aaa"))
    app.processEvents()

    window = MainWindow(adb_manager)

    def show_main():
        splash.close()
        window.show()

    QTimer.singleShot(1500, show_main)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    print("test")
