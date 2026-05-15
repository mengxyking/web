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


import caipiao_best_xinxichuli


# 实际手机连接状态检测线程（通过ADB命令）
class PhoneConnectionChecker(QThread):
    connection_status = pyqtSignal(bool)
    adb_not_found = pyqtSignal()  # ADB未找到信号
    log_signal = pyqtSignal(str, str)  # 日志信号（日志类型, 日志内容）
    interrupt_signal = pyqtSignal(str)  # 中断信号（中断信息）

    def run(self):
        """通过adb devices命令检测手机连接状态，并发送日志和中断信号"""
        while True:
            is_connected = False
            try:
                # 执行adb devices命令
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
    # 1. 原有日志信号：接收外部日志
    log_signal = pyqtSignal(str, str)
    # 2. 新增盈利更新信号：供外部（如caipiao_best_xinxichuli）调用，更新盈利显示
    profit_update_signal = pyqtSignal(str, str)  # 参数：(显示类型, 盈利内容)，类型同log（success/error/info）

    def __init__(self):
        super().__init__()
        self.phone_connected = False  # 手机连接状态
        self.adb_available = True  # ADB是否可用
        self.init_ui()  # 初始化界面
        self.load_config()  # 加载配置
        self.start_phone_checker()  # 启动检测线程
        # 绑定信号
        self.log_signal.connect(self.add_log)
        self.profit_update_signal.connect(self.update_profit_display)  # 绑定盈利更新逻辑

    def init_ui(self):
        """初始化界面：保留右侧中断区，左侧新增盈利情况显示"""
        # 窗口尺寸：高度增加80px容纳盈利模块
        self.setWindowTitle("彩票投注简化配置界面")
        self.setGeometry(150, 150, 800, 820)
        self.setFixedSize(800, 820)

        # 中心组件与主布局（上下结构：上层配置+中断 | 下层日志）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setSpacing(20)
        main_v_layout.setContentsMargins(20, 20, 20, 20)

        # ---------------------- 上层：左侧配置区 + 右侧中断区（核心布局） ----------------------
        top_h_layout = QHBoxLayout()
        top_h_layout.setSpacing(20)

        # ===================================== 左侧：配置区（新增盈利模块） =====================================
        config_layout = QVBoxLayout()
        config_layout.setSpacing(18)

        # 1.1 手机连接状态（原有）
        phone_layout = QHBoxLayout()
        phone_label = QLabel("手机是否连接：")
        phone_label.setFixedWidth(100)
        self.phone_status_label = QLabel("手机已断开")
        self.phone_status_label.setStyleSheet("color: red;")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_status_label)
        phone_layout.addStretch()
        config_layout.addLayout(phone_layout)

        # ---------------------- 新增：1.2 盈利情况显示模块（支持外部控制） ----------------------
        profit_module_layout = QVBoxLayout()
        # 盈利标题行
        profit_title_layout = QHBoxLayout()
        profit_label = QLabel("盈利(仅供参考)：")
        profit_label.setFixedWidth(100)  # 与其他配置标签对齐
        # 盈利内容显示框（模仿日志格式，支持颜色区分）
        self.profit_display = QTextEdit()
        self.profit_display.setReadOnly(True)
        self.profit_display.setFixedHeight(80)  # 固定高度，外部可通过代码修改（如setFixedHeight(120)）
        self.profit_display.setFont(QFont("Consolas", 9))
        self.profit_display.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")
        # 标题行组装
        profit_title_layout.addWidget(profit_label)
        profit_title_layout.addWidget(self.profit_display)
        # 盈利说明（提示用户颜色规则）
        profit_note = QLabel("注：绿色=盈利，红色=亏损，深灰色=普通信息")
        profit_note.setFont(QFont("Arial", 8))
        profit_note.setStyleSheet("color: #666;")
        # 盈利模块组装到配置区
        profit_module_layout.addLayout(profit_title_layout)
        profit_module_layout.addWidget(profit_note)
        config_layout.addLayout(profit_module_layout)

        # 1.3 钱包地址（原有）
        wallet_addr_layout = QHBoxLayout()
        wallet_addr_label = QLabel("钱包地址：")
        wallet_addr_label.setFixedWidth(100)
        self.wallet_addr_input = QLineEdit()
        self.wallet_addr_input.setPlaceholderText("示例：0x1234567890abcdef1234567890abcdef12345678")
        wallet_addr_layout.addWidget(wallet_addr_label)
        wallet_addr_layout.addWidget(self.wallet_addr_input)
        config_layout.addLayout(wallet_addr_layout)

        # 1.4 交易密码（原有）
        trade_pwd_layout = QHBoxLayout()
        trade_pwd_label = QLabel("交易密码：")
        trade_pwd_label.setFixedWidth(100)
        self.trade_pwd_input = QLineEdit()
        self.trade_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.trade_pwd_input.setPlaceholderText("输入钱包交易密码（输入时隐藏）")
        trade_pwd_layout.addWidget(trade_pwd_label)
        trade_pwd_layout.addWidget(self.trade_pwd_input)
        config_layout.addLayout(trade_pwd_layout)

        # 1.5 接口URL（原有）
        api_url_layout = QHBoxLayout()
        api_url_label = QLabel("接口URL配置：")
        api_url_label.setFixedWidth(100)
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("示例：http://xxx.xxx.xxx/api/latest-result")
        api_url_layout.addWidget(api_url_label)
        api_url_layout.addWidget(self.api_url_input)
        config_layout.addLayout(api_url_layout)

        # 1.6 测试模式（原有）
        test_mode_layout = QHBoxLayout()
        test_mode_label = QLabel("测试模式：")
        test_mode_label.setFixedWidth(100)
        self.test_mode_combo = QComboBox()
        self.test_mode_combo.addItems(["否", "是"])
        self.test_mode_combo.setFixedWidth(100)
        test_mode_layout.addWidget(test_mode_label)
        test_mode_layout.addWidget(self.test_mode_combo)
        test_mode_layout.addStretch()
        config_layout.addLayout(test_mode_layout)

        # 1.7 单金额组（原有）
        dan_layout = QHBoxLayout()
        dan_label = QLabel("单：")
        dan_label.setFixedWidth(50)
        self.dan_input = QLineEdit()
        self.dan_input.setPlaceholderText("示例：11,21,41-25,53,fudai_path-91,187,385")
        dan_layout.addWidget(dan_label)
        dan_layout.addWidget(self.dan_input)
        config_layout.addLayout(dan_layout)

        # 1.8 双金额组（原有）
        shuang_layout = QHBoxLayout()
        shuang_label = QLabel("双：")
        shuang_label.setFixedWidth(50)
        self.shuang_input = QLineEdit()
        self.shuang_input.setPlaceholderText("示例：10,20,40-24,52,110-90,186,384")
        shuang_layout.addWidget(shuang_label)
        shuang_layout.addWidget(self.shuang_input)
        config_layout.addLayout(shuang_layout)

        # 1.9 跟反策略（原有）
        genfan_layout = QHBoxLayout()
        genfan_label = QLabel("跟反：")
        genfan_label.setFixedWidth(50)
        self.genfan_input = QLineEdit()
        self.genfan_input.setPlaceholderText("示例：跟,跟,反-跟,跟,跟-跟,跟,跟")
        genfan_layout.addWidget(genfan_label)
        genfan_layout.addWidget(self.genfan_input)
        config_layout.addLayout(genfan_layout)

        # 1.10 开奖秒数（原有）
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

        # 1.11 功能按钮（原有）
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

        # 左侧配置区占比70%
        top_h_layout.addLayout(config_layout, 7)

        # ===================================== 右侧：中断信息区（保留原有逻辑） =====================================
        right_interrupt_layout = QVBoxLayout()
        # 中断标题
        interrupt_title = QLabel("中断信息")
        interrupt_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_interrupt_layout.addWidget(interrupt_title)
        # 中断显示框
        self.interrupt_frame = QFrame()
        self.interrupt_frame.setFrameShape(QFrame.Shape.Box)
        self.interrupt_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.interrupt_frame.setStyleSheet("""
            background-color: #fff0f0; 
            border: 1px solid #ffcccc;
            border-radius: 4px;
        """)
        self.interrupt_frame.setMinimumWidth(200)
        # 中断内容标签
        self.interrupt_label = QLabel("暂无中断信息")
        self.interrupt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.interrupt_label.setWordWrap(True)
        self.interrupt_label.setFont(QFont("Arial", 10))
        self.interrupt_label.setStyleSheet("color: #cc0000; padding: 10px;")
        # 中断框组装
        interrupt_inner_layout = QVBoxLayout(self.interrupt_frame)
        interrupt_inner_layout.addWidget(self.interrupt_label)
        right_interrupt_layout.addWidget(self.interrupt_frame)
        right_interrupt_layout.addStretch()

        # 右侧中断区占比30%
        top_h_layout.addLayout(right_interrupt_layout, 3)

        # 上层布局加入主布局
        main_v_layout.addLayout(top_h_layout)

        # ---------------------- 下层：日志区（通栏，原有逻辑） ----------------------
        log_v_layout = QVBoxLayout()
        log_title = QLabel("执行日志（通栏）")
        log_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        log_v_layout.addWidget(log_title)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd;")
        log_v_layout.addWidget(self.log_text)
        main_v_layout.addLayout(log_v_layout)

        # 初始化文本格式（日志+盈利共用）
        self.init_text_formats()

    def init_text_formats(self):
        """初始化日志和盈利显示的文本格式（统一风格）"""
        # 普通信息（深灰色）
        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QColor(100, 100, 100))
        # 盈利（深绿色）
        self.profit_format = QTextCharFormat()
        self.profit_format.setForeground(QColor(0, 150, 0))
        # 亏损（深红色）
        self.loss_format = QTextCharFormat()
        self.loss_format.setForeground(QColor(200, 0, 0))

    def add_log(self, log_type, content):
        """原有日志显示逻辑（不变）"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        prefix = {"info": "[信息]", "success": "[成功]", "warning": "[警告]", "error": "[错误]"}.get(log_type, "[信息]")
        log_content = f"[{timestamp}] {prefix} {content}\n"

        # 设置格式
        if log_type == "success":
            self.log_text.setCurrentCharFormat(self.profit_format)
        elif log_type in ["error", "warning"]:
            self.log_text.setCurrentCharFormat(self.loss_format)
        else:
            self.log_text.setCurrentCharFormat(self.info_format)

        # 插入日志
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.insertPlainText(log_content)
        self.log_text.ensureCursorVisible()

    def update_profit_display(self, display_type, content):
        """盈利显示更新逻辑（外部通过profit_update_signal调用）"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        profit_content = f"[{timestamp}] {content}\n"

        # 根据类型设置格式（success=盈利，error=亏损，info=普通信息）
        if display_type == "success":
            self.profit_display.setCurrentCharFormat(self.profit_format)
        elif display_type == "error":
            self.profit_display.setCurrentCharFormat(self.loss_format)
        else:
            self.profit_display.setCurrentCharFormat(self.info_format)

        # 插入盈利内容（自动滚动到底部）
        cursor = self.profit_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.profit_display.setTextCursor(cursor)
        self.profit_display.insertPlainText(profit_content)
        self.profit_display.ensureCursorVisible()

    def update_interrupt_info(self, info):
        """原有中断信息更新逻辑（不变）"""
        if not info:
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
        """原有ADB检测线程启动逻辑（不变）"""
        self.phone_checker = PhoneConnectionChecker()
        self.phone_checker.connection_status.connect(self.update_phone_status)
        self.phone_checker.adb_not_found.connect(self.handle_adb_not_found)
        self.phone_checker.log_signal.connect(self.add_log)
        self.phone_checker.interrupt_signal.connect(self.update_interrupt_info)
        self.phone_checker.start()
        self.add_log("info", "应用已启动，正在加载配置...")

    def update_phone_status(self, is_connected):
        """原有手机状态更新逻辑（不变）"""
        self.phone_connected = is_connected
        if is_connected:
            self.phone_status_label.setText("手机已连接")
            self.phone_status_label.setStyleSheet("color: green;")
        else:
            self.phone_status_label.setText("手机已断开")
            self.phone_status_label.setStyleSheet("color: red;")
            self.add_log("warning", "手机连接已断开")

    def handle_adb_not_found(self):
        """原有ADB异常处理逻辑（不变）"""
        if self.adb_available:
            self.adb_available = False
            QMessageBox.warning(
                self, "ADB工具未就绪",
                "未检测到ADB工具，请按以下步骤操作：\n"
                "1. 下载Android SDK Platform Tools（含ADB）\n"
                "2. 将ADB所在目录添加到系统PATH环境变量\n"
                "3. 重启本应用"
            )
        self.phone_status_label.setText("ADB不可用")
        self.phone_status_label.setStyleSheet("color: orange;")
        self.add_log("error", "ADB工具不可用，无法检测手机连接")

    def load_config(self):
        """原有配置加载逻辑（不变）"""
        if os.path.exists("lottery_simple_config.json"):
            try:
                with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 加载原有配置
                self.dan_input.setText(config.get("dan", ""))
                self.shuang_input.setText(config.get("shuang", ""))
                self.genfan_input.setText(config.get("genfan", ""))
                self.second_input.setText(str(config.get("check_second", "")) if config.get("check_second") else "")
                self.api_url_input.setText(config.get("api_url", ""))
                self.test_mode_combo.setCurrentText(config.get("test_mode", "否"))
                # 加载新增的钱包和密码配置
                self.wallet_addr_input.setText(config.get("wallet_address", ""))
                self.trade_pwd_input.setText(config.get("trade_password", ""))
                self.add_log("success", "本地配置加载成功（含钱包地址、交易密码）")
                return config
            except Exception as e:
                err_msg = f"配置加载失败：{str(e)}"
                QMessageBox.warning(self, "配置错误", err_msg + "\n将使用空配置")
                self.add_log("error", err_msg)
                self.update_interrupt_info(err_msg)
        else:
            self.add_log("info", "未找到本地配置文件，使用空配置")
        return None

    def on_save_config(self):
        """原有配置保存逻辑（不变）"""
        # 获取所有配置项
        config = {
            "dan": self.dan_input.text().strip(),
            "shuang": self.shuang_input.text().strip(),
            "genfan": self.genfan_input.text().strip(),
            "check_second": int(self.second_input.text().strip()) if self.second_input.text().strip() else "",
            "api_url": self.api_url_input.text().strip(),
            "test_mode": self.test_mode_combo.currentText(),
            "wallet_address": self.wallet_addr_input.text().strip(),
            "trade_password": self.trade_pwd_input.text().strip()
        }
        # 校验开奖秒数
        if config["check_second"] != "" and not (0 <= config["check_second"] <= 59):
            err_msg = "保存配置失败：开奖秒数必须是0-59的整数"
            QMessageBox.warning(self, "输入错误", err_msg)
            self.add_log("warning", err_msg)
            self.update_interrupt_info(err_msg)
            return None
        # 保存配置
        try:
            with open("lottery_simple_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "保存成功", "配置已保存到本地（含钱包地址、交易密码）")
            self.add_log("success", f"配置保存成功：钱包地址={config['wallet_address'][:20]}...")
            self.update_interrupt_info("")
            return config
        except Exception as e:
            err_msg = f"保存配置失败：{str(e)}"
            QMessageBox.critical(self, "保存错误", err_msg)
            self.add_log("error", err_msg)
            self.update_interrupt_info(err_msg)
        return None

    def on_execute(self):
        """执行按钮逻辑：传递盈利更新信号给caipiao_best_xinxichuli"""
        saved_config = self.on_save_config()
        if not self.adb_available or not self.phone_connected:
            err_msg = "执行失败：ADB未就绪或手机未连接"
            QMessageBox.warning(self, "无法执行", err_msg)
            self.add_log("error", err_msg)
            self.update_interrupt_info(err_msg)
            return

        # 确认执行
        preview_info = f"""当前配置：
        1. 钱包地址：{self.wallet_addr_input.text().strip()[:25] + "..." if self.wallet_addr_input.text().strip() else "未设置"}
        2. 交易密码：{"***" if self.trade_pwd_input.text().strip() else "未设置"}
        3. 接口URL：{self.api_url_input.text().strip()[:40] + "..." if self.api_url_input.text().strip() else "未设置"}
        4. 测试模式：{self.test_mode_combo.currentText()}
        5. 手机状态：已连接
        是否确认启动投注逻辑？"""
        if QMessageBox.question(self, "执行确认", preview_info) != QMessageBox.StandardButton.Ok:
            self.add_log("info", "用户取消执行操作")
            self.update_interrupt_info("用户取消执行操作")
            #return

        # 关键：创建业务逻辑实例，传递日志信号和盈利更新信号
        self.lottery_logic = caipiao_best_xinxichuli.LotteryLogic()
        self.lottery_logic.log_signal = self.log_signal  # 日志信号
        self.lottery_logic.profit_update_signal = self.profit_update_signal  # 盈利更新信号

        # 启动业务线程
        self.add_log("success", f"投注逻辑启动（测试模式：{self.test_mode_combo.currentText()}）")
        QMessageBox.information(self, "执行中", "投注逻辑已启动，日志和盈利将实时更新")
        threading.Thread(target=self.lottery_logic.yewu, args=(saved_config,)).start()

    def closeEvent(self, event):
        """原有窗口关闭逻辑（不变）"""
        self.add_log("info", "应用关闭，停止ADB检测线程...")
        self.phone_checker.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotterySimpleConfigWindow()
    window.show()
    sys.exit(app.exec())