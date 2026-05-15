import sys
import json
import os
import threading
import time
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTextEdit, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor

import caipiao_best


# 实际手机连接状态检测线程（通过ADB命令）
class PhoneConnectionChecker(QThread):
    connection_status = pyqtSignal(bool)
    adb_not_found = pyqtSignal()  # ADB未找到信号
    log_signal = pyqtSignal(str, str)  # 日志信号（日志类型, 日志内容）
    interrupt_signal = pyqtSignal(str)  # 中断信号（中断信息）

    def run(self):
        """通过adb devices命令检测手机连接状态，并发送日志和中断信号"""
        self.log_signal.emit("info", "ADB连接检测线程已启动，每5秒检测一次...")
        while True:
            is_connected = False
            try:
                # 执行adb devices命令
                self.log_signal.emit("info", "正在执行ADB命令检测手机连接...")
                result = subprocess.run(
                    ["adb", "devices"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )

                # 命令执行失败（返回码非0）
                if result.returncode != 0:
                    err_msg = f"ADB命令执行失败：{result.stderr.strip()}"
                    self.log_signal.emit("error", err_msg)
                    self.adb_not_found.emit()
                    self.interrupt_signal.emit("ADB命令执行失败，无法检测手机连接")
                    time.sleep(10)
                    continue

                # 解析输出结果
                output_lines = result.stdout.strip().split('\n')[1:]
                for line in output_lines:
                    line_stripped = line.strip()
                    if line_stripped and line_stripped.split()[-1] == "device":
                        is_connected = True
                        device_id = line_stripped.split()[0]
                        self.log_signal.emit("success", f"检测到已连接的设备：{device_id}")
                        self.interrupt_signal.emit("")  # 清除中断信息
                        break

                # 未检测到设备
                if not is_connected:
                    self.log_signal.emit("warning", "未检测到已连接的手机设备")
                    self.interrupt_signal.emit("未检测到已连接的手机设备")

            except FileNotFoundError:
                err_msg = "未找到ADB工具，请检查是否安装并配置环境变量"
                self.log_signal.emit("error", err_msg)
                self.adb_not_found.emit()
                self.interrupt_signal.emit(err_msg)
                time.sleep(10)
                continue
            except Exception as e:
                err_msg = f"ADB检测异常：{str(e)}"
                self.log_signal.emit("error", err_msg)
                self.interrupt_signal.emit(err_msg)
                time.sleep(5)
                continue

            # 发送连接状态
            self.connection_status.emit(is_connected)
            time.sleep(5)


class LotterySimpleConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.phone_connected = False  # 手机连接状态
        self.adb_available = True  # ADB是否可用
        self.init_ui()  # 初始化界面
        self.load_config()  # 加载配置
        self.start_phone_checker()  # 启动检测线程

    def init_ui(self):
        """初始化界面：新增接口URL和测试模式配置项"""
        # 窗口基础设置（微调高度容纳新增配置）
        self.setWindowTitle("彩票投注简化配置界面")
        self.setGeometry(150, 150, 750, 660)
        self.setFixedSize(750, 660)

        # 中心组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主水平布局（左右分栏）
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ---------------------- 左侧：配置和日志区 ----------------------
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)

        # 配置区（新增接口URL和测试模式）
        config_layout = QVBoxLayout()
        config_layout.setSpacing(18)

        # 1.1 手机连接状态
        phone_layout = QHBoxLayout()
        phone_label = QLabel("手机是否连接：")
        phone_label.setFixedWidth(100)
        self.phone_status_label = QLabel("手机已断开")
        self.phone_status_label.setStyleSheet("color: red;")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_status_label)
        phone_layout.addStretch()
        config_layout.addLayout(phone_layout)

        # ---------------------- 新增：1.2 接口URL配置 ----------------------
        api_url_layout = QHBoxLayout()
        api_url_label = QLabel("接口URL配置：")
        api_url_label.setFixedWidth(100)  # 与手机连接标签宽度一致，保持对齐
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("示例：http://xxx.xxx.xxx/api/latest-result")
        self.api_url_input.setToolTip("输入获取开奖结果的接口URL")
        api_url_layout.addWidget(api_url_label)
        api_url_layout.addWidget(self.api_url_input)
        config_layout.addLayout(api_url_layout)

        # ---------------------- 新增：1.3 测试模式下拉框 ----------------------
        test_mode_layout = QHBoxLayout()
        test_mode_label = QLabel("测试模式：")
        test_mode_label.setFixedWidth(100)
        # 下拉单选框（选项：是/否，默认选“否”）
        self.test_mode_combo = QComboBox()
        self.test_mode_combo.addItems(["否", "是"])  # 第一个选项为默认值
        self.test_mode_combo.setFixedWidth(100)
        self.test_mode_combo.setToolTip("选择是否启用测试模式（测试模式不调用真实接口）")
        test_mode_layout.addWidget(test_mode_label)
        test_mode_layout.addWidget(self.test_mode_combo)
        test_mode_layout.addStretch()  # 拉伸空白，避免下拉框过长
        config_layout.addLayout(test_mode_layout)

        # 1.4 单金额组
        dan_layout = QHBoxLayout()
        dan_label = QLabel("单：")
        dan_label.setFixedWidth(50)
        self.dan_input = QLineEdit()
        self.dan_input.setPlaceholderText("示例：11,21,41-25,53,fudai_path-91,187,385")
        dan_layout.addWidget(dan_label)
        dan_layout.addWidget(self.dan_input)
        config_layout.addLayout(dan_layout)

        # 1.5 双金额组
        shuang_layout = QHBoxLayout()
        shuang_label = QLabel("双：")
        shuang_label.setFixedWidth(50)
        self.shuang_input = QLineEdit()
        self.shuang_input.setPlaceholderText("示例：10,20,40-24,52,110-90,186,384")
        shuang_layout.addWidget(shuang_label)
        shuang_layout.addWidget(self.shuang_input)
        config_layout.addLayout(shuang_layout)

        # 1.6 跟反策略
        genfan_layout = QHBoxLayout()
        genfan_label = QLabel("跟反：")
        genfan_label.setFixedWidth(50)
        self.genfan_input = QLineEdit()
        self.genfan_input.setPlaceholderText("示例：跟,跟,反-跟,跟,跟-跟,跟,跟")
        genfan_layout.addWidget(genfan_label)
        genfan_layout.addWidget(self.genfan_input)
        config_layout.addLayout(genfan_layout)

        # 1.7 开奖秒数
        second_layout = QHBoxLayout()
        second_label = QLabel("开奖秒数：")
        second_label.setFixedWidth(50)
        self.second_input = QLineEdit()
        self.second_input.setPlaceholderText("示例：33")
        self.second_input.setFixedWidth(80)
        second_unit = QLabel("秒")
        second_layout.addWidget(second_label)
        second_layout.addWidget(self.second_input)
        second_layout.addWidget(second_unit)
        second_layout.addStretch()
        config_layout.addLayout(second_layout)

        # 1.8 功能按钮
        button_layout = QHBoxLayout()
        self.execute_btn = QPushButton("执行")
        self.execute_btn.setFixedSize(90, 35)
        self.execute_btn.clicked.connect(self.on_execute)

        self.save_btn = QPushButton("保存配置")
        self.save_btn.setFixedSize(90, 35)
        self.save_btn.clicked.connect(self.on_save_config)

        button_layout.addStretch()
        button_layout.addWidget(self.execute_btn)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.save_btn)
        config_layout.addLayout(button_layout)

        left_layout.addLayout(config_layout)

        # 日志面板（高度保持不变，适配新增配置后的布局）
        log_title = QLabel("执行日志")
        log_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(180)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")
        left_layout.addWidget(self.log_text)

        main_layout.addLayout(left_layout, 7)  # 左侧占70%宽度

        # ---------------------- 右侧：中断信息展示区 ----------------------
        right_layout = QVBoxLayout()

        interrupt_title = QLabel("中断信息")
        interrupt_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(interrupt_title)

        # 中断信息展示框（带边框和背景色）
        self.interrupt_frame = QFrame()
        self.interrupt_frame.setFrameShape(QFrame.Shape.Box)
        self.interrupt_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.interrupt_frame.setStyleSheet("""
            background-color: #fff0f0; 
            border: 1px solid #ffcccc;
            border-radius: 4px;
        """)
        self.interrupt_frame.setMinimumWidth(200)

        # 中断信息标签（居中显示，自动换行）
        self.interrupt_label = QLabel("暂无中断信息")
        self.interrupt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.interrupt_label.setWordWrap(True)
        self.interrupt_label.setFont(QFont("Arial", 10))
        self.interrupt_label.setStyleSheet("color: #cc0000; padding: 10px;")

        # 中断信息框布局
        interrupt_inner_layout = QVBoxLayout(self.interrupt_frame)
        interrupt_inner_layout.addWidget(self.interrupt_label)

        right_layout.addWidget(self.interrupt_frame)
        right_layout.addStretch()

        main_layout.addLayout(right_layout, 3)  # 右侧占30%宽度

        # 初始化日志格式
        self.init_log_formats()

    def init_log_formats(self):
        """初始化不同类型日志的文本格式"""
        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QColor(100, 100, 100))  # 深灰色

        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QColor(0, 150, 0))  # 深绿色

        self.warning_format = QTextCharFormat()
        self.warning_format.setForeground(QColor(255, 127, 0))  # 橙色

        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor(200, 0, 0))  # 深红色

    def add_log(self, log_type, content):
        """添加日志到面板"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        prefix_map = {
            "info": "[信息]",
            "success": "[成功]",
            "warning": "[警告]",
            "error": "[错误]"
        }
        prefix = prefix_map.get(log_type, "[信息]")
        log_content = f"[{timestamp}] {prefix} {content}\n"

        # 移动光标到末尾
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

        # 设置格式并插入日志
        if log_type == "success":
            self.log_text.setCurrentCharFormat(self.success_format)
        elif log_type == "warning":
            self.log_text.setCurrentCharFormat(self.warning_format)
        elif log_type == "error":
            self.log_text.setCurrentCharFormat(self.error_format)
        else:
            self.log_text.setCurrentCharFormat(self.info_format)

        self.log_text.insertPlainText(log_content)
        self.log_text.ensureCursorVisible()

    def update_interrupt_info(self, info):
        """更新右侧中断信息展示"""
        if not info:  # 空信息表示清除
            self.interrupt_label.setText("暂无中断信息")
            self.interrupt_frame.setStyleSheet("""
                background-color: #f8fff8; 
                border: 1px solid #ccffcc;
                border-radius: 4px;
            """)
            self.interrupt_label.setStyleSheet("color: #006600; padding: 10px;")
        else:
            self.interrupt_label.setText(info)
            self.interrupt_frame.setStyleSheet("""
                background-color: #fff0f0; 
                border: 1px solid #ffcccc;
                border-radius: 4px;
            """)
            self.interrupt_label.setStyleSheet("color: #cc0000; padding: 10px;")

    def start_phone_checker(self):
        """启动ADB检测线程，绑定所有信号"""
        self.phone_checker = PhoneConnectionChecker()
        self.phone_checker.connection_status.connect(self.update_phone_status)
        self.phone_checker.adb_not_found.connect(self.handle_adb_not_found)
        self.phone_checker.log_signal.connect(self.add_log)
        self.phone_checker.interrupt_signal.connect(self.update_interrupt_info)  # 绑定中断信息信号
        self.phone_checker.start()
        self.add_log("info", "应用已启动，正在加载配置...")

    def update_phone_status(self, is_connected):
        """更新手机连接状态"""
        self.phone_connected = is_connected
        if is_connected:
            self.phone_status_label.setText("手机已连接")
            self.phone_status_label.setStyleSheet("color: green;")
            self.add_log("success", "手机已成功连接！")
        else:
            self.phone_status_label.setText("手机已断开")
            self.phone_status_label.setStyleSheet("color: red;")
            self.add_log("warning", "手机连接已断开")

    def handle_adb_not_found(self):
        """处理ADB不可用情况"""
        if self.adb_available:
            self.adb_available = False
            QMessageBox.warning(
                self,
                "ADB工具未就绪",
                "未检测到ADB工具，请按以下步骤操作：\n"
                "1. 下载Android SDK Platform Tools（含ADB）\n"
                "2. 将ADB所在目录添加到系统PATH环境变量\n"
                "3. 重启本应用"
            )
        self.phone_status_label.setText("ADB不可用")
        self.phone_status_label.setStyleSheet("color: orange;")
        self.add_log("error", "ADB工具不可用，无法检测手机连接")

    def load_config(self):
        """加载本地配置（新增接口URL和测试模式的加载）"""
        if os.path.exists("lottery_simple_config.json"):
            try:
                with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 原有配置加载
                self.dan_input.setText(config.get("dan", ""))
                self.shuang_input.setText(config.get("shuang", ""))
                self.genfan_input.setText(config.get("genfan", ""))
                self.second_input.setText(str(config.get("check_second", "")) if config.get("check_second") else "")
                # 新增配置加载：接口URL
                self.api_url_input.setText(config.get("api_url", ""))
                # 新增配置加载：测试模式（根据保存的字符串设置下拉框选中项）
                test_mode = config.get("test_mode", "否")
                self.test_mode_combo.setCurrentText(test_mode)

                self.add_log("success", "本地配置加载成功（含接口URL和测试模式）")
            except Exception as e:
                err_msg = f"配置加载失败：{str(e)}"
                QMessageBox.warning(self, "配置错误", err_msg + "\n将使用空配置")
                self.add_log("error", err_msg)
                self.update_interrupt_info(err_msg)
        else:
            self.add_log("info", "未找到本地配置文件，使用空配置")

    def on_save_config(self):
        """保存配置到本地文件（新增接口URL和测试模式的保存）"""
        # 获取所有配置项（含新增项）
        dan = self.dan_input.text().strip()
        shuang = self.shuang_input.text().strip()
        genfan = self.genfan_input.text().strip()
        second_text = self.second_input.text().strip()
        api_url = self.api_url_input.text().strip()  # 新增：接口URL
        test_mode = self.test_mode_combo.currentText()  # 新增：测试模式（获取下拉框选中值）

        # 校验开奖秒数
        check_second = None
        if second_text:
            try:
                check_second = int(second_text)
                if not (0 <= check_second <= 59):
                    err_msg = "保存配置失败：开奖秒数必须是0-59的整数"
                    QMessageBox.warning(self, "输入错误", err_msg)
                    self.add_log("warning", err_msg)
                    self.update_interrupt_info(err_msg)
                    return
            except ValueError:
                err_msg = "保存配置失败：开奖秒数必须是整数"
                QMessageBox.warning(self, "输入错误", err_msg)
                self.add_log("warning", err_msg)
                self.update_interrupt_info(err_msg)
                return

        # 组装配置（含新增的api_url和test_mode）
        config = {
            "dan": dan,
            "shuang": shuang,
            "genfan": genfan,
            "check_second": check_second if check_second is not None else "",
            "api_url": api_url,  # 新增：接口URL
            "test_mode": test_mode  # 新增：测试模式（字符串“是”/“否”）
        }

        # 保存文件
        try:
            with open("lottery_simple_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "保存成功", "配置已保存到本地（含接口URL和测试模式）")
            self.add_log("success", "配置保存成功：接口URL={}, 测试模式={}".format(
                api_url[:30] + "..." if len(api_url) > 30 else api_url,
                test_mode
            ))
            self.update_interrupt_info("")  # 清除中断信息
        except Exception as e:
            err_msg = f"保存配置失败：{str(e)}"
            QMessageBox.critical(self, "保存错误", err_msg)
            self.add_log("error", err_msg)
            self.update_interrupt_info(err_msg)

    def on_execute(self):
        """执行按钮逻辑（新增接口URL和测试模式的参数传递）"""
        # 1. 检查ADB可用性
        self.on_save_config()
        if not self.adb_available:
            err_msg = "执行失败：ADB工具未就绪"
            QMessageBox.warning(self, "无法执行", err_msg)
            self.add_log("error", err_msg)
            self.update_interrupt_info(err_msg)
            return

        # 2. 检查手机连接
        if not self.phone_connected:
            err_msg = "执行失败：手机未连接"
            QMessageBox.warning(self, "无法执行", err_msg)
            self.add_log("error", err_msg)
            self.update_interrupt_info(err_msg)
            return

        # 3. 获取所有配置信息（含新增的接口URL和测试模式）
        dan = self.dan_input.text().strip() or "未设置"
        shuang = self.shuang_input.text().strip() or "未设置"
        genfan = self.genfan_input.text().strip() or "未设置"
        second = self.second_input.text().strip() or "33（默认）"
        api_url = self.api_url_input.text().strip() or "未设置"  # 新增：接口URL
        test_mode = self.test_mode_combo.currentText()  # 新增：测试模式

        # 4. 确认执行（展示所有配置，含新增项）
        preview_info = f"""
当前配置：
1. 接口URL：{api_url[:40] + "..." if len(api_url) > 40 else api_url}
2. 测试模式：{test_mode}
3. 单金额组：{dan[:30] + "..." if len(dan) > 30 else dan}
4. 双金额组：{shuang[:30] + "..." if len(shuang) > 30 else shuang}
5. 跟反策略：{genfan[:30] + "..." if len(genfan) > 30 else genfan}
6. 开奖秒数：{second}
7. 手机状态：已连接

是否确认启动投注逻辑？
        """

        if QMessageBox.question(
                self, "执行确认", preview_info,
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel
        ) == QMessageBox.StandardButton.Ok:
            # 传递所有配置到执行逻辑（此处可根据test_mode判断是否调用真实接口）
            execute_msg = f"开始执行投注逻辑（测试模式：{test_mode}，接口URL：{api_url[:30]}...），监控开奖中..."
            self.add_log("success", execute_msg)
            self.update_interrupt_info("")  # 清除中断信息
            QMessageBox.information(self, "执行中", f"投注逻辑已启动（测试模式：{test_mode}），日志将实时更新")
            bbb = threading.Thread(target=caipiao_best.yewu)
            bbb.start()
        else:
            self.add_log("info", "用户取消执行操作")
            self.update_interrupt_info("用户取消执行操作")

    def closeEvent(self, event):
        """窗口关闭时停止线程"""
        self.add_log("info", "应用正在关闭，停止ADB检测线程...")
        self.phone_checker.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotterySimpleConfigWindow()
    window.show()
    sys.exit(app.exec())