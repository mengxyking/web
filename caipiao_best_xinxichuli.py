import os
import requests
import time
import datetime
import json
from PyQt6.QtCore import pyqtSignal
import uiautomator2 as u2
import subprocess


class LotteryLogic:
    def __init__(self):
        # 接收界面传递的日志信号（由主程序赋值）
        self.log_signal = None
        self.profit_update_signal = None
        # 初始化实例变量（替代原全局变量）
        self.current_bet = None  # 当前待判定的投注目标
        self.current_stake_group = 0  # 当前使用的金额组索引（0-3，对应第1-4组）
        self.current_stake_index = 0  # 当前组内的金额索引（0-2，对应第1-3个金额）
        self.total_win_count = 0  # 累计赢局次数（仅第2/3/4组生效，第1组赢局不累计）
        self.bet_history = []  # 投注历史记录

    def load_config(self):
        """加载本地配置（新增接口URL和测试模式的加载）"""
        if os.path.exists("lottery_simple_config.json"):
            try:
                with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.log_signal.emit("info", f"配置加载成功：{config}")
                return config
            except Exception as e:
                self.log_signal.emit("error", f"配置加载失败：{str(e)}")
                return None
        else:
            self.log_signal.emit("warning", "未找到本地配置文件，使用空配置")
            return None

    def fetch_lottery_data(self, TEST_MODE, TARGET_SINGLE, API_URL):
        """从接口获取彩票数据，测试模式下手动输入"""
        try:
            if TEST_MODE:
                # 测试模式：手动输入结果，显示当前组和累计赢局状态
                self.log_signal.emit("info", "\n" + "=" * 40)
                self.log_signal.emit("info", "        测试模式 - 请输入模拟结果")
                self.log_signal.emit("info", "=" * 40)
                if self.current_stake_group == 0:
                    msg = f"当前状态：第1组（无需累计赢局） | 待判定投注：{self.current_bet if self.current_bet else '无'}"
                    self.log_signal.emit("info", msg)
                else:
                    msg = f"当前状态：第{self.current_stake_group + 1}组 | 累计赢局{self.total_win_count}/3次 | 待判定投注：{self.current_bet if self.current_bet else '无'}"
                    self.log_signal.emit("info", msg)
                self.log_signal.emit("info", "请输入模拟结果（例如：单、双、单,双 或 q退出测试）:")

                while True:
                    user_input = input("> ").strip()
                    if user_input.lower() == 'q':
                        self.log_signal.emit("info", "退出测试模式")
                        exit()
                    # 验证输入是否有效（仅允许单/双或多值组合）
                    parts = [p.strip() for p in user_input.split(",")]
                    valid = all(part in TARGET_SINGLE for part in parts)
                    if valid:
                        self.log_signal.emit("info", f"测试模式输入结果：{user_input}")
                        return user_input
                    self.log_signal.emit("warning", "无效输入，请输入 '单'、'双' 或 用逗号分隔的组合（如'单,双'）")
            else:
                # 正常模式：从API获取真实数据
                response = requests.get(API_URL, verify=False, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "0" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
                    latest_result = str(data["data"][0]).strip()
                    self.log_signal.emit("success", f"【数据提取】最新结果: {latest_result}")
                    return latest_result
                self.log_signal.emit("error", f"【数据异常】格式错误: {data}")
                return None
        except Exception as e:
            self.log_signal.emit("error", f"【数据获取异常】{str(e)}")
            return None

    def wait_until_target_second(self, target_second, TEST_MODE):
        """等待到当前分钟的目标秒数，测试模式下跳过等待"""
        if TEST_MODE:
            return  # 测试模式无需等待，直接执行
        # 正常模式：精准等待到目标秒数
        try:
            bbb = self.load_config()
            CHECK_SECOND = bbb.get("check_second", 33)
            if CHECK_SECOND is not None:
                target_second = CHECK_SECOND
            while True:
                now = datetime.datetime.now()
                if now.second == target_second:
                    return
                sleep_seconds = (target_second - now.second) % 60
                if sleep_seconds > 0:
                    next_minute = (now.minute % 60) + (1 if now.second > target_second else 0)
                    msg = f"【等待执行】需等待 {sleep_seconds} 秒到{next_minute}分{target_second}秒..."
                    self.log_signal.emit("info", msg)
                    time.sleep(sleep_seconds)
        except Exception as e:
            self.log_signal.emit("error", f"【等待机制异常】{str(e)}")
            time.sleep(1)  # 异常时休眠1秒避免死循环

    def get_current_stake(self, bet_type, dan, shuang):
        """根据投注类型（单/双）获取当前投注金额，确保索引合法"""
        try:
            # 选择对应的金额组（双/单）
            group_list = shuang if bet_type == "双" else dan

            # 确保金额组至少有4组（防止组索引越界）
            if len(group_list) < 4:
                group_list += [[0]] * (4 - len(group_list))
            adjusted_group = min(self.current_stake_group, len(group_list) - 1)

            # 确保当前组至少有3个金额（防止组内索引越界）
            current_group = group_list[adjusted_group]
            if len(current_group) < 3:
                current_group += [0] * (3 - len(current_group))
            adjusted_index = min(self.current_stake_index, len(current_group) - 1)

            return current_group[adjusted_index]
        except Exception as e:
            self.log_signal.emit("error", f"【获取投注金额异常】{str(e)}")
            return 0  # 异常时返回默认值

    def update_stake_position(self, win, shuang, dan):
        """根据输赢结果更新金额组位置（核心逻辑：第1组不累计，2-4组累计）"""
        try:
            if win:
                # 赢局处理：区分当前组是否为第1组
                if self.current_stake_group == 0:
                    # 第1组赢局：无需累计，直接重置为本组第1个金额
                    self.current_stake_index = 0
                    self.log_signal.emit("info", "【金额更新】第1组赢局 → 保持第1组第1个金额（无需累计）")
                else:
                    # 第2/3/4组赢局：累计赢局次数，满3次回溯到第1组
                    self.total_win_count += 1
                    self.log_signal.emit("success",
                                         f"【金额更新】第{self.current_stake_group + 1}组赢局 → 累计赢局{self.total_win_count}/3次")

                    # 累计满3次：回溯到第1组，重置所有计数
                    if self.total_win_count >= 3:
                        self.current_stake_group = 0
                        self.current_stake_index = 0
                        self.total_win_count = 0
                        self.log_signal.emit("success", "【金额回溯】累计赢3次 → 回到第1组第1个金额，累计数重置为0")
                    else:
                        # 未满3次：保持当前组，回到本组第1个金额
                        self.current_stake_index = 0
                        self.log_signal.emit("info",
                                             f"【金额更新】未累计3次 → 留在第{self.current_stake_group + 1}组第1个金额")
            else:
                # 输局处理：累计数不变，组内递进，超界升级组（第四组输光回第1组）
                self.current_stake_index += 1
                current_group = shuang if self.current_bet == "双" else dan

                # 确保当前组存在（防止索引越界）
                if len(current_group) <= self.current_stake_group:
                    current_group += [[0]] * (self.current_stake_group - len(current_group) + 1)

                # 组内金额用尽（索引超界）：升级到下一组或重置到第1组
                if self.current_stake_index >= len(current_group[self.current_stake_group]):
                    self.current_stake_index = 0  # 重置组内索引为第1个金额
                    if self.current_stake_group == len(current_group) - 1:
                        # 第四组输光：回到第1组
                        self.current_stake_group = 0
                        msg = f"【金额重置】第4组输光 → 回到第1组第1个金额（累计赢局数仍为{self.total_win_count}）"
                        self.log_signal.emit("warning", msg)
                    else:
                        # 其他组输光：升级到下一组
                        self.current_stake_group += 1
                        # 确保升级后的组存在
                        if self.current_stake_group >= len(current_group):
                            current_group.append([0, 0, 0])
                        msg = f"【金额升级】第{self.current_stake_group}组输光 → 升级到第{self.current_stake_group + 1}组第1个金额（累计赢局数{self.total_win_count}）"
                        self.log_signal.emit("warning", msg)
                else:
                    # 组内还有金额：递进至下一个金额
                    msg = f"【金额递进】第{self.current_stake_group + 1}组输局 → 组内递进至第{self.current_stake_index + 1}个金额（累计赢局数不变）"
                    self.log_signal.emit("warning", msg)
        except Exception as e:
            self.log_signal.emit("error", f"【更新金额位置异常】{str(e)}")

    def calculate_bet_target(self, latest_single_result, genfan):
        """根据“跟/反”策略计算当前投注目标（跟=同结果，反=反结果）"""
        try:
            # 确保策略组至少有4组
            if len(genfan) < 4:
                genfan += [["跟"]] * (4 - len(genfan))
            adjusted_group = min(self.current_stake_group, len(genfan) - 1)

            # 确保当前组至少有3个策略
            current_group = genfan[adjusted_group]
            if len(current_group) < 3:
                current_group += ["跟"] * (3 - len(current_group))
            adjusted_index = min(self.current_stake_index, len(current_group) - 1)

            current_strategy = current_group[adjusted_index]
            self.log_signal.emit("info",
                                 f"【策略计算】当前策略: {current_strategy} | 上一轮单值结果: {latest_single_result}")

            # 策略执行逻辑
            if current_strategy == "跟":
                return latest_single_result
            elif current_strategy == "反":
                return "双" if latest_single_result == "单" else "单"
            else:
                # 异常策略默认用“跟”
                self.log_signal.emit("warning", f"【策略异常】未知策略{current_strategy} → 默认使用“跟”策略")
                return latest_single_result
        except Exception as e:
            self.log_signal.emit("error", f"【计算投注目标异常】{str(e)}")
            return "单"  # 异常时返回默认值

    def execute_betting_logic(self, latest_result, API_URL, CHECK_SECOND, TEST_MODE, shuang, dan, genfan,
                              TARGET_SINGLE, d, wallet_address, trade_password):
        """执行完整投注逻辑：结果分类→输赢判定→金额更新→新投注生成"""
        try:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_signal.emit("info", "\n" + "=" * 50)
            self.log_signal.emit("info", f"【投注逻辑】开始执行 - {current_time}")
            msg = f"【当前状态】最新结果: {latest_result} | 待判定投注: {self.current_bet if self.current_bet else '无'}"
            self.log_signal.emit("info", msg)

            # 状态显示：区分第1组和2-4组的累计状态
            if self.current_stake_group == 0:
                status_text = f"【金额状态】当前组: 1 | 组内位置: {self.current_stake_index + 1} | 第1组无需累计"
            else:
                status_text = f"【金额状态】当前组: {self.current_stake_group + 1} | 组内位置: {self.current_stake_index + 1} | 累计赢局: {self.total_win_count}"
            self.log_signal.emit("info", status_text)

            # 1. 结果分类：单值（可投注+判定）/多值（仅判定不投注）
            is_single_result = (latest_result in TARGET_SINGLE)
            multi_result_list = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            msg = f"【结果分类】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list if not is_single_result else '无'}"
            self.log_signal.emit("info", msg)

            # 2. 输赢判定（仅当有“待判定投注”时触发）
            judge_triggered = False
            win = False
            stake_amount = 0

            if self.current_bet is not None:
                judge_triggered = True
                stake_amount = self.get_current_stake(self.current_bet, dan, shuang)
                self.log_signal.emit("info",
                                     f"\n【判定环节】触发！上一轮投注: {self.current_bet} | 投注金额: {stake_amount}")

                # 单值结果：直接对比；多值结果：检查是否包含投注目标
                if is_single_result:
                    win = (latest_result == self.current_bet)
                    judge_detail = f"单值对比（{self.current_bet} vs {latest_result}）"
                else:
                    win = (self.current_bet in multi_result_list)
                    judge_detail = f"多值包含检查（{self.current_bet} in {multi_result_list}）"

                # 输赢结果提示（突出显示）
                if win:
                    self.log_signal.emit("info", "\n" + "=" * 30)
                    self.log_signal.emit("success", "🎉🎉🎉 【判定结果】赢了！🎉🎉🎉")
                    self.log_signal.emit("success", f"✅ 判定逻辑: {judge_detail}")
                    self.log_signal.emit("success", f"✅ 赢得金额: {stake_amount}")
                    self.log_signal.emit("info", "=" * 30 + "\n")
                    self.profit_update_signal.emit("success", f"✅ 赢得金额: {stake_amount}")
                else:
                    self.log_signal.emit("info", "\n" + "=" * 30)
                    self.log_signal.emit("error", "❌❌❌ 【判定结果】输了！❌❌❌")
                    self.log_signal.emit("error", f"❌ 判定逻辑: {judge_detail}")
                    self.log_signal.emit("error", f"❌ 输掉金额: {stake_amount}")
                    self.profit_update_signal.emit("error", f"❌ 输掉金额: {stake_amount}")
                    self.log_signal.emit("info", "=" * 30 + "\n")

                # 更新金额位置（根据输赢结果）
                self.update_stake_position(win, shuang, dan)

                # 记录投注历史（用于统计）
                self.bet_history.append({
                    "time": current_time,
                    "bet_target": self.current_bet,
                    "stake_amount": stake_amount,
                    "actual_result": latest_result,
                    "win": win,
                    "current_group": self.current_stake_group + 1
                })
                self.show_bet_statistics()
                self.current_bet = None  # 判定完成后清空待判定投注

            # 3. 新投注生成（仅单值结果可投注，按跟反策略计算目标）
            if is_single_result:
                self.current_bet = self.calculate_bet_target(latest_result, genfan)
                next_stake = self.get_current_stake(self.current_bet, dan, shuang)
                current_strategy = genfan[self.current_stake_group][self.current_stake_index] if (
                        0 <= self.current_stake_group < len(genfan) and
                        0 <= self.current_stake_index < len(genfan[self.current_stake_group])
                ) else "跟"
                self.log_signal.emit("info", f"\n【投注环节】触发投注！")
                self.log_signal.emit("info", f"  上一轮结果: {latest_result} | 当前策略: {current_strategy}")
                self.log_signal.emit("info", f"  投注目标: {self.current_bet} | 投注金额: {next_stake}")
                self.log_signal.emit("info",
                                     f"  金额状态: 第{self.current_stake_group + 1}组第{self.current_stake_index + 1}个金额")
                self.log_signal.emit("info",
                                     f"这个时候开始投注对吧。。。。。。。。。。。。。。。。。。。。。。。。。")
                result_back = backToTpHome(d)

                if (result_back != 1):
                    self.log_signal.emit("error", f"回到钱包首页失败，继续下一轮\n")
                    return None
                self.log_signal.emit("info", f"回到钱包首页\n")
                if (d(text='转账').exists(timeout=3)):
                    print("转账")
                    d(text='转账').click()
                    time.sleep(0.5)
                    self.log_signal.emit("info", f"点击转账按钮\n")
                else:
                    print("当前没有转账")
                    self.log_signal.emit("error", f"点击转账失败，继续下一轮\n")
                    return None

                if (d(text='TRX').exists(timeout=5)):
                    print("TRX")
                    d(text='TRX').click()
                    time.sleep(0.5)
                    self.log_signal.emit("info", f"点击TRX按钮\n")
                else:
                    print("当前没有TRX")
                    self.log_signal.emit("error", f"点击TRX按钮失败，继续下一轮\n")
                    return None

                if (d(textContains='输入或粘贴').exists(timeout=3)):
                    print("输入钱包地址")
                    self.log_signal.emit("info", f"输入钱包地址\n")
                    d(textContains='输入或粘贴').set_text(wallet_address)
                    time.sleep(1)
                else:
                    self.log_signal.emit("error", f"输入钱包地址失败，继续下一轮\n")
                    return None

                if (d(textContains='请输入数量').exists(timeout=3)):
                    print("输入数量")
                    self.log_signal.emit("info", f"输入数量\n")
                    d(textContains='请输入数量').set_text(str(next_stake))
                    time.sleep(1)
                else:
                    self.log_signal.emit("error", f"输入数量失败，继续下一轮\n")
                    return None

                if (d(textContains='确认').exists(timeout=3)):
                    print("点击确认按钮")
                    self.log_signal.emit("info", f"点击确认按钮\n")
                    d(textContains='确认').click()
                    time.sleep(4)
                else:
                    self.log_signal.emit("error", f"点击确认按钮失败，继续下一轮\n")
                    return None

                if (d(textContains='继续转账').exists(timeout=3)):
                    print("点击继续转账")
                    self.log_signal.emit("info", f"点击继续转账\n")
                    d(textContains='继续转账').click()
                    time.sleep(1)
                else:
                    self.log_signal.emit("warning", f"没有继续转账按钮，尝试跳过\n")

                if (d(textContains='确认支付').exists(timeout=3)):
                    print("确认支付")
                    self.log_signal.emit("info", f"确认支付\n")
                    d(textContains='确认支付').click()
                    time.sleep(1)
                else:
                    self.log_signal.emit("error", f"没有确认支付按钮，继续下一轮\n")
                    return None

                if (d(textContains='不需要再次输入密码').exists(timeout=3)):
                    print("勾选不需要再次输入密码")
                    self.log_signal.emit("info", f"勾选不需要再次输入密码\n")
                    d(textContains='不需要再次输入密码').click()
                    time.sleep(1.5)

                    if (d(textContains='勾选了此选项').exists(timeout=2)):
                        print("点击不需要输入密码的确认按钮")
                        self.log_signal.emit("info", f"点击不需要输入密码的确认按钮\n")
                        d(textContains='确认').click()
                        time.sleep(1)
                else:
                    self.log_signal.emit("warning", f"没有不需要再次输入密码选项，尝试跳过\n")

                if (d(textContains='请输入钱包密码').exists(timeout=3)):
                    print("输入密码")
                    self.log_signal.emit("info", f"输入密码\n")
                    d(textContains='请输入钱包密码').click()
                    time.sleep(1)
                    d(textContains='请输入钱包密码').set_text(str(trade_password))
                    time.sleep(1)
                else:
                    self.log_signal.emit("error", f"没有输入密码框，继续下一轮\n")
                    return None

                if (d(text='确认').exists(timeout=3)):
                    print("最后点击确认")
                    self.log_signal.emit("info", f"最后点击确认\n")
                    d(text='确认').click()
                    time.sleep(3)
                else:
                    self.log_signal.emit("error", f"没有最后确认按钮，继续下一轮\n")
                    return None

            else:
                self.log_signal.emit("info", f"\n【投注环节】结果 '{latest_result}' 是多值，不符合投注条件，不投注")

            self.log_signal.emit("info", "=" * 50 + "\n")
            return None
        except Exception as e:
            self.log_signal.emit("error", f"【投注逻辑执行异常】{str(e)}")
            return None  # 异常时返回None，不中断主循环

    def show_bet_statistics(self):
        """显示投注历史统计（总次数、胜率、盈亏等）"""
        try:
            if not self.bet_history:
                return

            total = len(self.bet_history)
            wins = sum(1 for record in self.bet_history if record["win"])
            losses = total - wins
            win_rate = (wins / total) * 100 if total > 0 else 0

            # 计算盈亏（赢局加金额，输局减金额）
            profit = sum(record["stake_amount"] for record in self.bet_history if record["win"])
            loss = sum(record["stake_amount"] for record in self.bet_history if not record["win"])
            net_profit = profit - loss

            # 打印统计信息
            self.log_signal.emit("info", "【历史统计】" + "-" * 40)
            self.log_signal.emit("info", f"总投注次数: {total} | 赢局: {wins}次 🎉 | 输局: {losses}次 ❌")
            self.log_signal.emit("info", f"胜率: {win_rate:.2f}% | 总盈利: {profit} | 总亏损: {loss}")

            if net_profit > 0:
                self.log_signal.emit("success", f"净盈亏: {net_profit} 🎉")
                self.profit_update_signal.emit("success", f"✅ 净盈亏: {net_profit}")
            elif net_profit < 0:
                self.log_signal.emit("error", f"净盈亏: {net_profit} ❌")
                self.profit_update_signal.emit("error", f"❌净盈亏: {net_profit} ")
            else:
                self.log_signal.emit("info", f"净盈亏: {net_profit}")

            # 补充当前组和累计状态
            if self.current_stake_group == 0:
                self.log_signal.emit("info", f"当前状态: 第1组（无需累计赢局）")
            else:
                self.log_signal.emit("info",
                                     f"当前状态: 第{self.current_stake_group + 1}组 | 累计赢局{self.total_win_count}/3次")
            self.log_signal.emit("info", "-" * 40)
        except Exception as e:
            self.log_signal.emit("error", f"【统计信息显示异常】{str(e)}")

    def yewu(self, config_c=None):
        """业务入口方法"""
        # 优先使用界面传递的config，避免重复加载
        if config_c is None:
            config_c = self.load_config()
        if not config_c:
            self.log_signal.emit("error", "配置为空，无法启动业务逻辑")
            return
        d = None
        devices = get_connected_devices()
        if (len(devices) > 0):
            try:
                d = u2.connect(devices[0])
                self.log_signal.emit("info", "当前手机连接成功，开始")
            except BaseException as e:
                self.log_signal.emit("error", f"当前手机连接失败：{str(e)}，无法启动业务逻辑")
                return
        else:
            self.log_signal.emit("error", "当前连接手机为空，无法启动业务逻辑")
            return

        # 解析配置参数
        API_URL = config_c.get("api_url", "")
        CHECK_SECOND = config_c.get("check_second", 33)
        TEST_MODE = config_c.get("test_mode", "否")
        shuang_str = config_c.get("shuang", "")
        dan_str = config_c.get("dan", "")
        genfan_str = config_c.get("genfan", "")
        wallet_address = config_c.get("wallet_address", "")
        trade_password = config_c.get("trade_password", "")

        # 转换测试模式（字符串→布尔值）
        TEST_MODE = True if TEST_MODE == "是" else False

        # 转换金额组和策略（字符串→二维列表）
        try:
            dan = [[int(num) for num in part.split(',')] for part in dan_str.split('-') if part.strip()]
            shuang = [[int(num) for num in part1.split(',')] for part1 in shuang_str.split('-') if part1.strip()]
            genfan = [[num.strip() for num in part2.split(',')] for part2 in genfan_str.split('-') if part2.strip()]

            # 确保金额组和策略组至少有4组，每组至少3个元素（防止索引越界）
            # 补全单金额组
            if len(dan) < 4:
                dan += [[0, 0, 0]] * (4 - len(dan))
            for i in range(len(dan)):
                if len(dan[i]) < 3:
                    dan[i] += [0] * (3 - len(dan[i]))

            # 补全双金额组
            if len(shuang) < 4:
                shuang += [[0, 0, 0]] * (4 - len(shuang))
            for i in range(len(shuang)):
                if len(shuang[i]) < 3:
                    shuang[i] += [0] * (3 - len(shuang[i]))

            # 补全跟反策略组
            if len(genfan) < 4:
                genfan += [["跟", "跟", "跟"]] * (4 - len(genfan))
            for i in range(len(genfan)):
                if len(genfan[i]) < 3:
                    genfan[i] += ["跟"] * (3 - len(genfan[i]))

            self.log_signal.emit("info", f"解析配置：单金额组={dan}，双金额组={shuang}，跟反策略={genfan}")
        except Exception as e:
            self.log_signal.emit("error", f"配置解析失败（金额组/策略格式错误）：{str(e)}")
            return

        TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件

        # 脚本启动提示
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", "          彩票跟随投注监控脚本（带测试模式）")
        self.log_signal.emit("info", f"          当前模式: {'测试模式' if TEST_MODE else '正常模式'}")
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", f"监控接口: {API_URL}")
        self.log_signal.emit("info", f"检查时间: 每分钟第{CHECK_SECOND}秒")
        self.log_signal.emit("info", "核心规则:")
        self.log_signal.emit("info", "1. 单值结果（单/双）→ 按跟反策略投注；多值结果→只判定不投注")
        self.log_signal.emit("info", "2. 第1组赢局：无需累计，直接保持本组第1个金额")
        self.log_signal.emit("info", "3. 第2-4组赢局：累计赢3次→回溯到第1组，输局不清零累计数")
        self.log_signal.emit("info", "4. 输局处理：组内递进→升级组→第四组输光回第1组")
        self.log_signal.emit("info", "5. 跟反策略：跟=投上一轮结果，反=投上一轮相反结果")
        self.log_signal.emit("info", "判定提示: 赢局 🎉 | 输局 ❌")

        # 测试模式说明（仅测试模式显示）
        if TEST_MODE:
            self.log_signal.emit("info", "\n测试模式说明:")
            self.log_signal.emit("info", "- 无需等待开奖，手动输入结果即可测试")
            self.log_signal.emit("info", "- 输入 '单'/'双' 模拟单值结果，'单,双' 模拟多值结果")
            self.log_signal.emit("info", "- 输入 'q' 直接退出测试模式")
        self.log_signal.emit("info", "=" * 60 + "\n")

        try:
            d.app_start(package_name="vip.mytokenpocket")
            time.sleep(2)
        except Exception as e:
            self.log_signal.emit("error", f"启动钱包应用异常：{str(e)}")

        # 主循环：持续检查数据并执行投注逻辑（永不中断）
        while True:
            try:
                result_back = backToTpHome(d)
                if (result_back != 1):
                    self.log_signal.emit("error", f"回到钱包首页失败，等待下一轮重试\n")
                    time.sleep(5)  # 失败后等待5秒再重试
                    continue

                self.wait_until_target_second(CHECK_SECOND, TEST_MODE)
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                self.log_signal.emit("info", f"【主流程】[{current_time}] 开始检查数据...")

                # 获取结果（测试模式手动输入，正常模式API获取）
                latest_result = self.fetch_lottery_data(TEST_MODE, TARGET_SINGLE, API_URL)
                if not latest_result:
                    self.log_signal.emit("warning", f"【主流程】未获取到有效数据，等待下一轮\n")
                    time.sleep(1)
                    continue

                # 执行核心投注逻辑
                self.execute_betting_logic(
                    latest_result, API_URL, CHECK_SECOND, TEST_MODE,
                    shuang, dan, genfan, TARGET_SINGLE, d,
                    wallet_address, trade_password
                )

                if TEST_MODE:
                    # 测试模式增加短暂停顿，方便查看输出
                    time.sleep(0.5)
                else:
                    # 正常模式等待1秒，避免频繁请求
                    time.sleep(1)

            except KeyboardInterrupt:
                # 手动停止脚本（Ctrl+C），显示最终统计
                self.log_signal.emit("info", "\n" + "=" * 50)
                self.log_signal.emit("info", "脚本已手动停止")
                if self.bet_history:
                    self.log_signal.emit("info", "\n【最终统计】")
                    self.show_bet_statistics()
                self.log_signal.emit("info", "=" * 50)
                break  # 手动停止时才退出
            except Exception as e:
                # 捕获所有异常，记录日志后继续下一轮
                self.log_signal.emit("error", f"\n【主流程异常】{str(e)}，继续下一轮执行\n")
                time.sleep(5)  # 异常后等待5秒再重试


def get_connected_devices():
    """获取当前连接的安卓设备列表"""
    try:
        # 执行adb命令获取设备列表
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        # 检查命令是否执行成功
        if result.returncode != 0:
            print(f"ADB命令执行失败: {result.stderr.strip()}")
            return []

        # 解析输出结果
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
        for line in lines:
            line = line.strip()
            if line and 'device' in line:
                device_id = line.split()[0]
                devices.append(device_id)

        return devices

    except FileNotFoundError:
        print("未找到ADB工具，请确保ADB已安装并添加到系统PATH")
        return []
    except Exception as e:
        print(f"获取设备列表时发生错误: {str(e)}")
        return []


def backToTpHome(d):
    """返回钱包首页，最多尝试10次返回键"""
    try:
        dd = 0
        time.sleep(1)
        while dd < 10:
            # 安全检查元素列表是否存在
            # elements = d(text='我的', timeout=1)  # 1秒超时，避免阻塞
            # if len(elements) > 0:
            #     return 1
            if(d(text='我的').exists(timeout=1)):
                return 1
            dd += 1
            d.press("back")
            time.sleep(1)
        return 2
    except Exception as e:
        print(f"返回首页异常: {str(e)}")
        return 2