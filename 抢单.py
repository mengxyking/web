import sys
import json
import os
import threading
import time

import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# 配置文件路径（保存在当前目录下的config.json）
CONFIG_FILE = "config.json"


def find_min_divisor_and_quotient(x):
    """
    计算x除以几余数大于15的最小除数，并返回该除数和对应的商
    :param x: 被除数（正整数）
    :return: 元组(最小除数, 对应商)；若x≤15，返回(x, 1)（x÷x=1余0）
    """
    # 情况1：x≤15，直接返回(x, 1)（除数=x，商=1）
    if x <= 15:
        return (x, 1)

    # 情况2：x>15，找最小除数d（d>16，且x%d>15）
    min_d = 17  # 除数必须>16（余数>15且余数<除数）
    while True:
        remainder = x % min_d
        quotient = x // min_d

        # 找到第一个余数>15的除数，返回(除数, 商)
        if remainder > 15:
            return (min_d, quotient + 1)

        # 边界：当除数>x时，余数=x（>15），商=0，必然满足条件
        if min_d > x:
            return (min_d, 0)

        # 继续检查下一个除数
        min_d += 1


# 测试示例

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()  # 启动时加载保存的配置

    def init_ui(self):
        # 主窗口设置（扩大尺寸适配日志区域）
        self.setWindowTitle("抢单配置工具")
        self.setFixedSize(900, 600)  # 调整窗口大小，适配日志区域
        self.center_window()  # 窗口居中

        # 中央部件和主布局（改为水平布局：左配置 + 右日志）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 整体边距
        main_layout.setSpacing(20)  # 配置区和日志区间距

        # -------------------- 左侧：配置区域（原有功能） --------------------
        config_layout = QVBoxLayout()
        config_layout.setSpacing(20)  # 配置项间距

        # 字体设置（统一字体大小，更整洁）
        label_font = QFont("微软雅黑", 10)
        edit_font = QFont("微软雅黑", 10)
        button_font = QFont("微软雅黑", 10, QFont.Weight.Bold)
        log_font = QFont("Consolas", 9)  # 日志用等宽字体，更易读

        # 1. COOKIE配置
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel("COOKIE配置：")
        cookie_label.setFont(label_font)
        cookie_label.setFixedWidth(100)  # 固定标签宽度，保证对齐
        self.cookie_edit = QLineEdit()
        self.cookie_edit.setFont(edit_font)
        self.cookie_edit.setPlaceholderText("请输入COOKIE内容")
        self.cookie_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_edit)
        config_layout.addLayout(cookie_layout)

        # 2. USER配置
        user_layout = QHBoxLayout()
        user_label = QLabel("USER：")
        user_label.setFont(label_font)
        user_label.setFixedWidth(100)
        self.user_edit = QLineEdit()
        self.user_edit.setFont(edit_font)
        self.user_edit.setPlaceholderText("请输入USER编号（如445）")
        self.user_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_edit)
        config_layout.addLayout(user_layout)

        # 3. 低于多少个不抢
        min_count_layout = QHBoxLayout()
        min_count_label = QLabel("低于多少个不抢：")
        min_count_label.setFont(label_font)
        min_count_label.setFixedWidth(100)
        self.min_count_edit = QLineEdit()
        self.min_count_edit.setFont(edit_font)
        self.min_count_edit.setPlaceholderText("请输入数字（如10）")
        self.min_count_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        min_count_layout.addWidget(min_count_label)
        min_count_layout.addWidget(self.min_count_edit)
        config_layout.addLayout(min_count_layout)

        # ========== 新增：高于多少个不抢 ==========
        max_count_layout = QHBoxLayout()
        max_count_label = QLabel("高于多少个不抢：")
        max_count_label.setFont(label_font)
        max_count_label.setFixedWidth(100)
        self.max_count_edit = QLineEdit()
        self.max_count_edit.setFont(edit_font)
        self.max_count_edit.setPlaceholderText("请输入数字（如100）")
        self.max_count_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        max_count_layout.addWidget(max_count_label)
        max_count_layout.addWidget(self.max_count_edit)
        config_layout.addLayout(max_count_layout)
        # =========================================

        # 4. 间隔时间
        interval_layout = QHBoxLayout()
        interval_label = QLabel("间隔时间(毫秒)：")
        interval_label.setFont(label_font)
        interval_label.setFixedWidth(100)
        self.interval_edit = QLineEdit()
        self.interval_edit.setFont(edit_font)
        self.interval_edit.setPlaceholderText("请输入秒数（如5）")
        self.interval_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_edit)
        config_layout.addLayout(interval_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.exec_btn = QPushButton("执行")
        self.exec_btn.setFont(button_font)
        self.exec_btn.setFixedSize(120, 40)
        self.exec_btn.clicked.connect(self.on_exec_click)

        self.save_btn = QPushButton("保存设置")
        self.save_btn.setFont(button_font)
        self.save_btn.setFixedSize(120, 40)
        self.save_btn.clicked.connect(self.save_config)

        button_layout.addWidget(self.exec_btn)
        button_layout.addWidget(self.save_btn)
        config_layout.addLayout(button_layout)

        # 配置区域添加伸缩项，让按钮居中，配置项更紧凑
        config_layout.addStretch(1)

        # -------------------- 右侧：日志显示区域（新增，占大空间） --------------------
        log_layout = QVBoxLayout()
        log_layout.setSpacing(10)

        # 日志标题
        log_title = QLabel("日志输出")
        log_title.setFont(QFont("微软雅黑", 14, QFont.Weight.Bold))
        log_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        log_layout.addWidget(log_title)

        # 日志文本框（核心，占最大空间）
        self.log_text = QTextEdit()
        self.log_text.setFont(log_font)
        self.log_text.setReadOnly(True)  # 只读，禁止编辑
        self.log_text.setPlaceholderText("程序日志将显示在这里...")
        # 设置日志区域占大空间
        self.log_text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 日志框样式优化
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f8f8;
            }
        """)
        log_layout.addWidget(self.log_text, stretch=1)  # stretch=1 让日志框占满剩余空间

        # -------------------- 组装主布局 --------------------
        # 配置区域占1份，日志区域占2份（日志更大）
        main_layout.addLayout(config_layout, stretch=1)
        main_layout.addLayout(log_layout, stretch=2)

    def center_window(self):
        """窗口居中显示"""
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def load_config(self):
        """加载保存的配置文件"""
        self.log_message("开始加载配置文件...")
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 填充到输入框
                self.cookie_edit.setText(config.get("cookie", ""))
                self.user_edit.setText(config.get("user", ""))
                self.min_count_edit.setText(config.get("min_count", ""))
                # ========== 新增：加载高于多少个不抢配置 ==========
                self.max_count_edit.setText(config.get("max_count", ""))
                # ===============================================
                self.interval_edit.setText(config.get("interval", ""))
                self.log_message("配置文件加载成功！")
            except Exception as e:
                self.log_message(f"加载配置失败：{str(e)}", level="error")
        else:
            self.log_message("未找到配置文件，将使用默认空配置")

    def save_config(self):
        """保存配置到文件"""
        self.log_message("开始保存配置文件...")
        config = {
            "cookie": self.cookie_edit.text().strip(),
            "user": self.user_edit.text().strip(),
            "min_count": self.min_count_edit.text().strip(),
            # ========== 新增：保存高于多少个不抢配置 ==========
            "max_count": self.max_count_edit.text().strip(),
            # ===============================================
            "interval": self.interval_edit.text().strip()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log_message("配置文件保存成功！")
        except Exception as e:
            self.log_message(f"保存配置失败：{str(e)}", level="error")

    def log_message(self, msg, level="info"):
        """
        日志输出方法
        :param msg: 日志内容
        :param level: 日志级别（info/warning/error）
        """
        # 时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 级别前缀
        level_prefix = {
            "info": "[INFO]",
            "warning": "[WARNING]",
            "error": "[ERROR]"
        }.get(level, "[INFO]")
        # 组装日志行
        log_line = f"{timestamp} {level_prefix} {msg}\n"
        # 追加到日志框
        self.log_text.append(log_line)
        # 自动滚屏到最后一行
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def on_exec_click(self):
        # if(time.time() > 1766068678):
        #    self.log_message("==================== 当前试用版 ====================")
        #    return
        """执行按钮点击事件（集成日志输出）"""
        if (self.exec_btn.text() == "执行"):
            self.exec_btn.setText("点击暂停")
        else:
            self.exec_btn.setText("执行")
        self.log_message("==================== 开始执行任务 ====================")
        # 获取当前配置值
        cookie = self.cookie_edit.text().strip()
        user = self.user_edit.text().strip()
        min_count = self.min_count_edit.text().strip()
        # ========== 新增：获取高于多少个不抢配置 ==========
        max_count = self.max_count_edit.text().strip()
        # ===============================================
        interval = self.interval_edit.text().strip()

        # 简单的参数校验
        if not cookie:
            self.log_message("校验失败：请输入COOKIE配置！", level="error")
            return
        if not user:
            self.log_message("校验失败：请输入USER！", level="error")
            return
        if not min_count.isdigit():
            self.log_message("校验失败：请输入有效的数字作为最低数量！", level="error")
            return
        # ========== 新增：校验高于多少个不抢配置 ==========
        if not max_count.isdigit():
            self.log_message("校验失败：请输入有效的数字作为最高数量！", level="error")
            return
        # ===============================================
        if not interval.isdigit():
            self.log_message("校验失败：请输入有效的数字作为间隔时间！", level="error")
            return

        # 输出配置信息到日志
        self.log_message("执行配置：")
        self.log_message(f"  - COOKIE：{cookie}")
        self.log_message(f"  - USER：{user}")
        self.log_message(f"  - 低于 {min_count} 个不抢")
        # ========== 新增：输出高于多少个不抢配置 ==========
        self.log_message(f"  - 高于 {max_count} 个不抢")
        # ===============================================
        self.log_message(f"  - 间隔时间：{interval} 秒")
        self.log_message("==================== 配置校验通过 ====================")

        # TODO: 替换为你的实际业务逻辑（如调用抢单接口）
        # 示例：模拟执行任务
        self.log_message("开始执行抢单任务...")

        # ========== 新增：传递max_count参数 ==========
        threading.Thread(target=self.get_t, args=(cookie, user, min_count, max_count, interval,)).start()
        # =============================================

        # 这里可以添加你的业务代码，比如循环调用接口、定时任务等
        # self.log_message("抢单任务执行完成！")

    def get_t(self, cookie, user, min_count, max_count, interval):  # 新增max_count参数
        totle = 0
        page = 1
        limit = 10

        # 1. 构造请求基础信息
        while True:
            print(f"page={page},limit={limit}")
            if (self.exec_btn.text() == "执行"):
                self.log_message("暂停中")
                time.sleep(10)
                continue
            url = "http://karajiek.asdy.xyz:32587/index/Order/getOrderData.html"

            # URL查询参数（拆分后更易维护）
            params = {
                "page": page,
                "limit": limit,
                "user": user
            }

            # 2. 请求头（完全对应curl的-H参数）
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Proxy-Connection": "keep-alive",  # 兼容代理连接标识
                "Referer": "http://karajiek.asdy.xyz:32587/index/order/index.html",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"  # AJAX请求标识
            }

            # 3. Cookies（对应curl的-b参数，拆分为键值对）
            cookies = {
                "ptgg": "on",
                "PHPSESSID": cookie
            }

            # 4. 发送请求（--insecure对应verify=False）
            try:
                # 发送GET请求（curl默认GET，无POST参数）
                response = requests.get(
                    url=url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    verify=False,  # 对应curl的--insecure，忽略SSL证书验证
                    timeout=15  # 超时时间，避免请求挂起
                )

                # 检查请求是否成功（状态码非200则抛出异常）
                response.raise_for_status()

                # 5. 处理响应（该接口返回JSON，直接解析）
                # 先设置响应编码（防止中文乱码）
                response.encoding = response.apparent_encoding
                # 解析JSON数据
                result = response.json()

                totle = result["data"]["total"]
                print(f"共有{totle}条数据")
                limit, page = find_min_divisor_and_quotient(int(totle))
                # page = page + 1

                print("请求成功！开始提取每条数据的count和sales_count：\n")
                # 提取订单列表（核心数据在 data->data 中）
                order_list = result["data"]["data"]

                # 遍历每条订单，提取目标字段
                for idx, order in enumerate(reversed(order_list), 1):
                    order_id = order["id"]  # 订单ID
                    create_time = order["create_time"]
                    order_sn = order["orderSN"]  # 订单编号
                    count = order["count"]  # 目标字段1：count create_time
                    sales_count = order["sales_count"]  # 目标字段2：sales_count

                    # ========== 可选：添加高低数量判断逻辑（如需生效请取消注释） ==========
                    # if int(sales_count) < int(min_count) or int(sales_count) > int(max_count):
                    #     self.log_message(f"id={id_t},编号={order_sn}数量{sales_count}不在[{min_count},{max_count}]范围内，跳过抢单")
                    #     continue
                    # ===============================================================

                    if int(sales_count) >= int(min_count) and int(sales_count) <= int(max_count):
                        threading.Thread(target=self.qiangdan,
                                         args=(cookie, order_id, sales_count, order_sn, user,)).start()

                    # 格式化输出
                    print(
                        f"第{idx}条订单 |创建时间{create_time}| ID:{order_id} | 编号:{order_sn} | count:{count} | sales_count:{sales_count}")

                # 可选：汇总统计
                total_count = sum([order["count"] for order in order_list])
                total_sales_count = sum([order["sales_count"] for order in order_list])
                print(f"\n汇总统计 | 总count: {total_count} | 总sales_count: {total_sales_count}")

            except requests.exceptions.RequestException as e:
                # 捕获所有请求相关异常（超时、连接失败、状态码错误等）
                print(f"请求失败！错误信息：{e}")
                # 若有响应内容，打印原始内容便于排查
                if hasattr(e, 'response') and e.response is not None:
                    print(f"响应状态码：{e.response.status_code}")
                    print(f"响应原始内容：{e.response.text}")
                self.get_t(cookie, user, min_count, max_count, interval)  # 传递max_count参数
            time.sleep(int(interval) / 1000)

    def qiangdan(self, PHPSESSID, id_t, order_Count, order_sn, user):
        import requests
        import json
        self.log_message(f"开始抢单id={id_t},编号={order_sn}")

        # 1. 构造请求基础信息
        url = "http://karajiek.asdy.xyz:32587/index/Order/action.html"

        # URL查询参数（?id=885258&user=445 拆分）
        params = {
            "id": id_t,
            "user": user
        }

        # 2. POST表单数据（对应--data-raw 'number=1'）
        post_data = {
            "number": order_Count
        }

        # 3. 请求头（完全对应curl的-H参数）
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "http://karajiek.asdy.xyz:32587",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://karajiek.asdy.xyz:32587/index/order/index.html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        # 4. Cookies（对应curl的-b参数）
        cookies = {
            "ptgg": "on",
            "PHPSESSID": PHPSESSID
        }

        # 5. 发送POST请求（--insecure对应verify=False）
        try:
            response = requests.post(
                url=url,
                params=params,  # URL后缀的查询参数
                data=post_data,  # POST表单数据（application/x-www-form-urlencoded）
                headers=headers,
                cookies=cookies,
                verify=False,  # 忽略SSL证书验证（对应--insecure）
                timeout=15  # 超时保护
            )

            # 检查请求是否成功（非200状态码抛出异常）
            response.raise_for_status()

            # 处理响应（根据接口返回格式调整，先尝试JSON解析，失败则返回原始文本）
            response.encoding = response.apparent_encoding  # 防止中文乱码
            try:
                result = response.json()
                print("请求成功！响应JSON数据：")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                if (result["msg"] == "抢单成功"):
                    self.log_message(f"id={id_t},编号={order_sn}抢单成功，抢了{order_Count}个")
                else:
                    self.log_message(f"id={id_t},编号={order_sn}抢单失败")
            except json.JSONDecodeError:
                print("请求成功！响应原始文本：")
                print(response.text)

        except requests.exceptions.RequestException as e:
            # 捕获所有请求异常（超时、连接失败、状态码错误等）
            print(f"请求失败！错误信息：{e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应状态码：{e.response.status_code}")
                print(f"响应原始内容：{e.response.text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置全局字体（可选，适配中文）
    app.setFont(QFont("微软雅黑", 10))
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())