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
        self.last_round_result = "输"  # 新增：记录上一轮输赢结果（用于判断是否强制投注）
        self.initial_bet_triggered = False  # 新增：标记初始投注是否已触发（需单值结果）

    def load_config(self):
        """加载本地配置（新增接口URL和测试模式的加载）"""
        if os.path.exists("lottery_simple_config.json"):
            try:
                with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.log_signal.emit("info", f"配置加载成功：{config}")
                # 新增：打印策略配置详情（方便核对是否为“反反跟-跟跟跟-跟跟跟-跟跟跟”）
                if "genfan" in config:
                    self.log_signal.emit("info", f"【配置校验】跟反策略原始配置：{config['genfan']}")
                return config
            except Exception as e:
                self.log_signal.emit("error", f"配置加载失败：{str(e)}")
                return None
        else:
            self.log_signal.emit("warning", "未找到本地配置文件，使用空配置")
            return None

    def fetch_lottery_data(self, TEST_MODE, TARGET_SINGLE, API_URL, genfan):
        """从接口获取彩票数据，测试模式下手动输入，新增genfan参数"""
        if TEST_MODE:
            # 测试模式：手动输入结果，显示当前组和累计赢局状态
            self.log_signal.emit("info", "\n" + "=" * 40)
            self.log_signal.emit("info", "        测试模式 - 请输入模拟结果")
            self.log_signal.emit("info", "=" * 40)
            init_status = "未触发（需单值结果）" if not self.initial_bet_triggered else "已触发"
            # 显示当前策略索引和策略值（核心跟踪点1：确认策略是否取错）
            current_strategy = ""
            if self.current_stake_group < len(genfan) and self.current_stake_index < len(
                    genfan[self.current_stake_group]):
                current_strategy = genfan[self.current_stake_group][self.current_stake_index]
            else:
                self.log_signal.emit("warning",
                                     f"【策略索引异常】组索引{self.current_stake_group}或组内索引{self.current_stake_index}超出策略长度")

            if self.current_stake_group == 0:
                msg = f"当前状态：第1组（无需累计赢局） | 初始投注：{init_status} | 待判定投注：{self.current_bet if self.current_bet else '无'} | 上一轮结果：{self.last_round_result} | 当前策略：{current_strategy}（组{self.current_stake_group + 1}索引{self.current_stake_index}）"
                self.log_signal.emit("info", msg)
            else:
                msg = f"当前状态：第{self.current_stake_group + 1}组 | 累计赢局{self.total_win_count}/3次 | 初始投注：{init_status} | 待判定投注：{self.current_bet if self.current_bet else '无'} | 上一轮结果：{self.last_round_result} | 当前策略：{current_strategy}（组{self.current_stake_group + 1}索引{self.current_stake_index}）"
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
                    # 打印输入结果的拆分详情（核心跟踪点2：多值结果是否正确拆分）
                    self.log_signal.emit("info",
                                         f"测试模式输入结果：{user_input} | 拆分后有效结果：{parts} | 结果类型：{'多值' if len(parts) > 1 else '单值'}")
                    return user_input
                self.log_signal.emit("warning", "无效输入，请输入 '单'、'双' 或 用逗号分隔的组合（如'单,双'）")
        else:
            # 正常模式：从API获取真实数据
            try:
                response = requests.get(API_URL, verify=False, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "0" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
                    latest_result = str(data["data"][0]).strip()
                    # 打印API结果的拆分详情（核心跟踪点2：多值结果是否正确拆分）
                    parts = [p.strip() for p in latest_result.split(",")]
                    self.log_signal.emit("success",
                                         f"【数据提取】最新结果: {latest_result} | 拆分后有效结果：{parts} | 结果类型：{'多值' if len(parts) > 1 else '单值'}")
                    return latest_result
                self.log_signal.emit("error", f"【数据异常】格式错误: {data}")
                return None
            except requests.exceptions.RequestException as e:
                self.log_signal.emit("error", f"【请求失败】{str(e)}")
                return None

    def wait_until_target_second(self, target_second, TEST_MODE):
        """等待到当前分钟的目标秒数，测试模式下跳过等待"""
        if TEST_MODE:
            return  # 测试模式无需等待，直接执行
        # 正常模式：精准等待到目标秒数
        bbb = self.load_config()
        CHECK_SECOND = bbb.get("check_second", 33)

        if (CHECK_SECOND != None):
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

    def get_current_stake(self, bet_type, dan, shuang):
        """根据投注类型（单/双）获取当前投注金额，确保索引合法"""
        group = shuang if bet_type == "双" else dan
        # 防止索引越界（极端情况下的安全处理）
        adjusted_group = min(self.current_stake_group, len(group) - 1)
        adjusted_index = min(self.current_stake_index, len(group[adjusted_group]) - 1)
        # 打印金额索引匹配过程（核心跟踪点3：金额组是否正确对应）
        self.log_signal.emit("info",
                             f"【金额计算】投注类型：{bet_type} | 对应金额组：{group} | 调整后组索引：{adjusted_group} | 组内索引：{adjusted_index} | 最终金额：{group[adjusted_group][adjusted_index]}")
        return group[adjusted_group][adjusted_index]

    def update_stake_position(self, win, shuang, dan):
        """根据输赢结果更新金额组位置（核心逻辑：第1组不累计，2-4组累计）"""
        # 先更新上一轮输赢记录
        old_last_result = self.last_round_result  # 记录更新前的输赢状态
        self.last_round_result = "赢" if win else "输"
        # 打印输赢状态变更（核心跟踪点4：确保输赢状态正确传递）
        self.log_signal.emit("info",
                             f"【输赢状态更新】上一轮原始结果：{'赢' if win else '输'} | 更新前状态：{old_last_result} | 更新后状态：{self.last_round_result}")

        if win:
            # 赢局处理：区分当前组是否为第1组
            if self.current_stake_group == 0:
                # 第1组赢局：无需累计，直接重置为本组第1个金额
                old_index = self.current_stake_index  # 记录更新前的索引
                self.current_stake_index = 0
                self.log_signal.emit("info",
                                     f"【金额更新】第1组赢局 → 组内索引：{old_index} → 0（保持第1组第1个金额，无需累计）")
            else:
                # 第2/3/4组赢局：累计赢局次数，满3次回溯到第1组
                old_win_count = self.total_win_count  # 记录更新前的累计赢局
                self.total_win_count += 1
                self.log_signal.emit("success",
                                     f"【金额更新】第{self.current_stake_group + 1}组赢局 → 累计赢局：{old_win_count} → {self.total_win_count}/3次")

                # 累计满3次：回溯到第1组，重置所有计数
                if self.total_win_count >= 3:
                    old_group = self.current_stake_group  # 记录更新前的组索引
                    old_index = self.current_stake_index  # 记录更新前的组内索引
                    self.current_stake_group = 0
                    self.current_stake_index = 0
                    self.total_win_count = 0
                    self.log_signal.emit("success",
                                         f"【金额回溯】累计赢3次 → 组索引：{old_group} → 0 | 组内索引：{old_index} → 0 | 累计数重置为0")
                else:
                    # 未满3次：保持当前组，回到本组第1个金额
                    old_index = self.current_stake_index  # 记录更新前的索引
                    self.current_stake_index = 0
                    self.log_signal.emit("info",
                                         f"【金额更新】未累计3次 → 组内索引：{old_index} → 0（留在第{self.current_stake_group + 1}组第1个金额）")
        else:
            # 输局处理：累计数不变，组内递进，超界升级组（第四组输光回第1组）
            old_index = self.current_stake_index  # 记录更新前的索引
            self.current_stake_index += 1
            current_group = shuang if self.current_bet == "双" else dan
            self.log_signal.emit("info",
                                 f"【金额递进】第{self.current_stake_group + 1}组输局 → 组内索引：{old_index} → {self.current_stake_index}（累计赢局数不变：{self.total_win_count}）")

            # 组内金额用尽（索引超界）：升级到下一组或重置到第1组
            if self.current_stake_index >= len(current_group[self.current_stake_group]):
                self.current_stake_index = 0  # 重置组内索引为第1个金额
                old_group = self.current_stake_group  # 记录更新前的组索引
                if self.current_stake_group == len(current_group) - 1:
                    # 第四组输光：回到第1组
                    self.current_stake_group = 0
                    msg = f"【金额重置】第4组输光 → 组索引：{old_group} → 0 | 组内索引：{old_index} → 0（累计赢局数仍为{self.total_win_count}）"
                    self.log_signal.emit("warning", msg)
                else:
                    # 其他组输光：升级到下一组
                    self.current_stake_group += 1
                    msg = f"【金额升级】第{old_group}组输光 → 组索引：{old_group} → {self.current_stake_group} | 组内索引：{old_index} → 0（累计赢局数{self.total_win_count}）"
                    self.log_signal.emit("warning", msg)
            else:
                # 组内还有金额：递进至下一个金额
                msg = f"【金额递进】第{self.current_stake_group + 1}组输局 → 组内索引：{old_index} → {self.current_stake_index + 1}个金额（累计赢局数不变：{self.total_win_count}）"
                self.log_signal.emit("warning", msg)

    def calculate_bet_target(self, latest_result, genfan, TARGET_SINGLE):
        """
        修复：输局时无需等待单值结果，直接从多值结果中提取目标；赢局仍用单值结果
        """
        # 1. 处理结果：赢局用单值，输局从多值中取第一个有效值
        # 打印结果处理过程（核心跟踪点5：多值结果是否取第一个有效值）
        parts = [p.strip() for p in latest_result.split(",")]
        self.log_signal.emit("info",
                             f"【策略计算-结果处理】原始结果：{latest_result} | 拆分后：{parts} | 上一轮输赢状态：{self.last_round_result}")

        if self.last_round_result == "赢":
            # 赢局：必须用单值结果计算（原逻辑）
            if latest_result not in TARGET_SINGLE:
                self.log_signal.emit("warning", "【策略计算】赢局需单值结果，当前为多值 → 取第一个有效值")
                latest_single_result = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE][0]
                # 打印取第一个有效值的过程
                self.log_signal.emit("info",
                                     f"【策略计算-赢局多值处理】有效结果列表：{[p.strip() for p in latest_result.split(',') if p.strip() in TARGET_SINGLE]} → 取第一个：{latest_single_result}")
            else:
                latest_single_result = latest_result
                self.log_signal.emit("info", f"【策略计算-赢局单值处理】直接使用单值结果：{latest_single_result}")
        else:
            # 输局：无论单/多值，直接取第一个有效值
            valid_results = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            latest_single_result = valid_results[0] if valid_results else "单"  # 极端情况默认单
            # 打印输局多值处理过程（核心跟踪点6：输局多值是否正确取第一个）
            self.log_signal.emit("info",
                                 f"【策略计算-输局处理】有效结果列表：{valid_results} → 取第一个：{latest_single_result}（极端情况默认单）")

        # 2. 按跟反策略计算投注目标
        # 校验策略索引合法性（防止越界导致策略取错）
        if self.current_stake_group >= len(genfan):
            self.log_signal.emit("error",
                                 f"【策略索引异常】金额组索引{self.current_stake_group}超出策略组数{len(genfan)} → 强制使用第1组策略")
            self.current_stake_group = 0
        if self.current_stake_index >= len(genfan[self.current_stake_group]):
            self.log_signal.emit("error",
                                 f"【策略索引异常】组内索引{self.current_stake_index}超出策略组长度{len(genfan[self.current_stake_group])} → 强制使用第1个策略")
            self.current_stake_index = 0

        current_strategy = genfan[self.current_stake_group][self.current_stake_index]
        self.log_signal.emit("info",
                             f"【策略计算】当前策略: {current_strategy} | 基准结果: {latest_single_result} | 上一轮输赢: {self.last_round_result}")

        # 策略执行逻辑
        target = ""
        if current_strategy == "跟":
            target = latest_single_result
            # 打印跟策略的计算结果
            self.log_signal.emit("info", f"【策略执行-跟】投注目标 = 基准结果 → {target} = {latest_single_result}")
        elif current_strategy == "反":
            target = "双" if latest_single_result == "单" else "单"
            # 打印反策略的计算结果
            self.log_signal.emit("info", f"【策略执行-反】基准结果{latest_single_result} → 反转后目标：{target}")
        else:
            # 异常策略默认用“跟”
            target = latest_single_result
            self.log_signal.emit("warning",
                                 f"【策略异常】未知策略{current_strategy} → 默认使用“跟”策略，投注目标：{target}")

        # 校验最终投注目标有效性
        if target not in TARGET_SINGLE:
            self.log_signal.emit("error", f"【目标异常】计算后目标{target}无效 → 强制重置为'单'")
            target = "单"
        return target

    def execute_betting_logic(self, latest_result, API_URL, CHECK_SECOND, TEST_MODE, shuang, dan, genfan,
                              TARGET_SINGLE, d, wallet_address, trade_password):
        try:
            """执行完整投注逻辑：结果分类→输赢判定→金额更新→新投注生成（输局强制投注）"""
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_signal.emit("info", "\n" + "=" * 50)
            self.log_signal.emit("info", f"【投注逻辑】开始执行 - {current_time}")
            # 打印完整当前状态（核心跟踪点7：全量状态回溯）
            parts = [p.strip() for p in latest_result.split(",")]
            is_single_result = (latest_result in TARGET_SINGLE)
            msg = f"【当前状态-全量】最新结果: {latest_result}（拆分后：{parts} | 类型：{'多值' if len(parts) > 1 else '单值'}） | 待判定投注: {self.current_bet if self.current_bet else '无'} | 上一轮输赢: {self.last_round_result} | 初始投注: {'已触发' if self.initial_bet_triggered else '未触发（需单值）'} | 金额组：{self.current_stake_group + 1} | 组内索引：{self.current_stake_index} | 累计赢局：{self.total_win_count}"
            self.log_signal.emit("info", msg)

            # 状态显示：区分第1组和2-4组的累计状态
            if self.current_stake_group == 0:
                status_text = f"【金额状态】当前组: 1 | 组内位置: {self.current_stake_index + 1} | 第1组无需累计"
            else:
                status_text = f"【金额状态】当前组: {self.current_stake_group + 1} | 组内位置: {self.current_stake_index + 1} | 累计赢局: {self.total_win_count}"
            self.log_signal.emit("info", status_text)

            # 1. 结果分类：单值/多值（仅用于赢局判定，输局不限制）
            is_single_result = (latest_result in TARGET_SINGLE)
            multi_result_list = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            # 打印结果分类详情
            self.log_signal.emit("info",
                                 f"【结果分类-详情】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list} | 有效结果总数：{len(multi_result_list)} | 多值是否包含上一轮投注：{self.current_bet in multi_result_list if self.current_bet else '无待判定投注'}")
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

                # 更新金额位置（根据输赢结果，同时更新last_round_result）
                self.update_stake_position(win, shuang, dan)

                # 记录投注历史（用于统计）
                # 加入策略信息（方便后续统计分析）
                current_strategy = genfan[self.current_stake_group][self.current_stake_index] if (
                        self.current_stake_group < len(genfan) and self.current_stake_index < len(
                    genfan[self.current_stake_group])) else "未知"
                self.bet_history.append({
                    "time": current_time,
                    "bet_target": self.current_bet,
                    "stake_amount": stake_amount,
                    "actual_result": latest_result,
                    "win": win,
                    "current_group": self.current_stake_group + 1,
                    "used_strategy": current_strategy,  # 记录本次使用的策略
                    "result_type": "多值" if len(parts) > 1 else "单值"  # 记录结果类型
                })
                self.show_bet_statistics(genfan)
                self.current_bet = None  # 判定完成后清空待判定投注

            # 3. 新投注生成（核心修改：初始需单值触发，后续赢局单值投，输局单/多值都投）
            # 先判断是否有有效结果（避免极端情况无有效值）
            valid_results = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            if not valid_results:
                self.log_signal.emit("error", f"【投注环节】结果 '{latest_result}' 无有效单/双值，不投注")
                self.log_signal.emit("info", "=" * 50 + "\n")
                return

            # 核心逻辑：区分“初始投注”和“后续投注”
            # 打印投注触发前的核心条件（核心跟踪点8：判断是否满足投注条件）
            self.log_signal.emit("info",
                                 f"【投注触发条件】初始投注状态：{self.initial_bet_triggered} | 上一轮输赢：{self.last_round_result} | 结果类型：{'多值' if len(parts) > 1 else '单值'} | 有效结果数：{len(valid_results)}")
            if not self.initial_bet_triggered:
                # 初始投注：必须单值结果才触发（与赢局规则一致）
                if is_single_result:
                    self.current_bet = self.calculate_bet_target(latest_result, genfan, TARGET_SINGLE)
                    next_stake = self.get_current_stake(self.current_bet, dan, shuang)
                    current_strategy = genfan[self.current_stake_group][self.current_stake_index]
                    self.log_signal.emit("info", f"\n【投注环节】初始投注触发！（单值结果符合要求）")
                    self.log_signal.emit("info", f"  基准结果: {latest_result} | 当前策略: {current_strategy}")
                    self.log_signal.emit("info", f"  投注目标: {self.current_bet} | 投注金额: {next_stake}")
                    self.log_signal.emit("info",
                                         f"  金额状态: 第{self.current_stake_group + 1}组第{self.current_stake_index + 1}个金额")
                    # 标记初始投注已触发
                    self.initial_bet_triggered = True
                    # 打印初始投注触发状态变更
                    self.log_signal.emit("success", f"【初始投注状态】未触发 → 已触发（后续输局将强制投注）")
                    # 执行UI自动化投注流程
                    result_back = backToTpHome(d, self.log_signal)
                    if result_back != 1:
                        self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                        return "66"
                    self.log_signal.emit("info", f"回到钱包首页\n")
                    if (d(text='转账').exists(timeout=3)):
                        print("转账")
                        d(text='转账').click()
                        time.sleep(0.5)
                        self.log_signal.emit("info", f"点击转账按钮\n")
                    else:
                        print("当前没有转账")
                        self.log_signal.emit("error", f"点击转账失败，退出\n")
                        return "66"

                    if (d(text='TRX').exists(timeout=5)):
                        print("TRX")
                        d(text='TRX').click()
                        time.sleep(0.5)
                        self.log_signal.emit("info", f"点击TRX按钮\n")
                    else:
                        print("当前没有TRX")
                        self.log_signal.emit("error", f"点击TRX按钮，失败\n")
                        return "66"

                    if (d(textContains='输入或粘贴').exists(timeout=3)):
                        print("，按钮")
                        self.log_signal.emit("info", f"输入钱包地址\n")
                        d(textContains='输入或粘贴').set_text(wallet_address)
                        time.sleep(1)
                    else:
                        self.log_signal.emit("error", f"输入钱包地址失败，退出\n")
                        print("当前没有善缘按钮")
                        return "66"

                    if (d(textContains='请输入数量').exists(timeout=3)):
                        print("，按钮")
                        self.log_signal.emit("info", f"输入数量\n")
                        d(textContains='请输入数量').set_text(str(next_stake))
                        time.sleep(1)
                    else:
                        self.log_signal.emit("error", f"输入数量，失败\n")
                        print("当前没有善缘按钮")
                        return "66"

                    if (d(textContains='确认').exists(timeout=3)):
                        print("，确认")
                        self.log_signal.emit("info", f"点击确认按钮\n")
                        d(textContains='确认').click()
                        time.sleep(4)
                    else:
                        self.log_signal.emit("error", f"点击确认按钮，失败\n")
                        print("当前没有善缘按钮")
                        return "66"

                    if (d(textContains='继续转账').exists(timeout=3)):
                        print("，继续转账")
                        self.log_signal.emit("info", f"点击继续转账\n")
                        d(textContains='继续转账').click()
                        time.sleep(1)
                    else:
                        self.log_signal.emit("error", f"没有继续转账\n")
                        print("当前没有继续转账")

                    if (d(textContains='确认支付').exists(timeout=3)):
                        print("，继续转账")
                        self.log_signal.emit("info", f"确认支付\n")
                        d(textContains='确认支付').click()
                        time.sleep(3)
                    else:
                        self.log_signal.emit("error", f"没有确认支付\n")
                        # return "66"

                    if (d(textContains='请输入钱包密码').exists(timeout=1)):
                        print("，请输入钱包密码")
                        self.log_signal.emit("info", f"输入密码\n")
                        d(textContains='请输入钱包密码').click()
                        time.sleep(0.5)
                    else:
                        self.log_signal.emit("error", f"没有输入密码\n")

                    if (d(textContains='请输入钱包密码').exists(timeout=1)):
                        print("，请输入钱包密码")
                        self.log_signal.emit("info", f"输入密码\n")
                        d(textContains='请输入钱包密码').set_text(str(trade_password))
                        time.sleep(1)
                    else:
                        self.log_signal.emit("error", f"没有输入密码\n")

                    if (d(text='确认').exists(timeout=3)):
                        print("，确认")
                        self.log_signal.emit("info", f"最后点击确认\n")
                        d(text='确认').click()
                        time.sleep(1.5)
                    else:
                        self.log_signal.emit("error", f"没有最后确认，退出\n")
                        # return "66"
                else:
                    self.log_signal.emit("info",
                                         f"\n【投注环节】初始投注未触发！结果 '{latest_result}' 是多值（拆分后：{parts}），需单值结果才开始")
            else:
                # 后续投注：区分赢局/输局
                if self.last_round_result == "赢":
                    # 赢局：仅单值结果投注（原逻辑）
                    if is_single_result:
                        self.current_bet = self.calculate_bet_target(latest_result, genfan, TARGET_SINGLE)
                        next_stake = self.get_current_stake(self.current_bet, dan, shuang)
                        current_strategy = genfan[self.current_stake_group][self.current_stake_index]
                        self.log_signal.emit("info", f"\n【投注环节】赢局→单值投注触发！")
                        self.log_signal.emit("info", f"  基准结果: {latest_result} | 当前策略: {current_strategy}")
                        self.log_signal.emit("info", f"  投注目标: {self.current_bet} | 投注金额: {next_stake}")
                        self.log_signal.emit("info",
                                             f"  金额状态: 第{self.current_stake_group + 1}组第{self.current_stake_index + 1}个金额")
                        # 执行UI自动化投注流程
                        result_back = backToTpHome(d, self.log_signal)
                        if result_back != 1:
                            self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                            return "66"
                        self.log_signal.emit("info", f"回到钱包首页\n")
                        if (d(text='转账').exists(timeout=3)):
                            print("转账")
                            d(text='转账').click()
                            time.sleep(0.5)
                            self.log_signal.emit("info", f"点击转账按钮\n")
                        else:
                            print("当前没有转账")
                            self.log_signal.emit("error", f"点击转账失败，退出\n")
                            return "66"

                        if (d(text='TRX').exists(timeout=5)):
                            print("TRX")
                            d(text='TRX').click()
                            time.sleep(0.5)
                            self.log_signal.emit("info", f"点击TRX按钮\n")
                        else:
                            print("当前没有TRX")
                            self.log_signal.emit("error", f"点击TRX按钮，失败\n")
                            return "66"

                        if (d(textContains='输入或粘贴').exists(timeout=3)):
                            print("，按钮")
                            self.log_signal.emit("info", f"输入钱包地址\n")
                            d(textContains='输入或粘贴').set_text(wallet_address)
                            time.sleep(1)
                        else:
                            self.log_signal.emit("error", f"输入钱包地址失败，退出\n")
                            print("当前没有善缘按钮")
                            return "66"

                        if (d(textContains='请输入数量').exists(timeout=3)):
                            print("，按钮")
                            self.log_signal.emit("info", f"输入数量\n")
                            d(textContains='请输入数量').set_text(str(next_stake))
                            time.sleep(1)
                        else:
                            self.log_signal.emit("error", f"输入数量，失败\n")
                            print("当前没有善缘按钮")
                            return "66"

                        if (d(textContains='确认').exists(timeout=3)):
                            print("，确认")
                            self.log_signal.emit("info", f"点击确认按钮\n")
                            d(textContains='确认').click()
                            time.sleep(4)
                        else:
                            self.log_signal.emit("error", f"点击确认按钮，失败\n")
                            print("当前没有善缘按钮")
                            return "66"

                        if (d(textContains='继续转账').exists(timeout=3)):
                            print("，继续转账")
                            self.log_signal.emit("info", f"点击继续转账\n")
                            d(textContains='继续转账').click()
                            time.sleep(1)
                        else:
                            self.log_signal.emit("error", f"没有继续转账\n")
                            print("当前没有继续转账")

                        if (d(textContains='确认支付').exists(timeout=3)):
                            print("，继续转账")
                            self.log_signal.emit("info", f"确认支付\n")
                            d(textContains='确认支付').click()
                            time.sleep(3)
                        else:
                            self.log_signal.emit("error", f"没有确认支付\n")
                            # return "66"

                        if (d(textContains='请输入钱包密码').exists(timeout=3)):
                            print("，请输入钱包密码")
                            self.log_signal.emit("info", f"输入密码\n")
                            d(textContains='请输入钱包密码').click()
                            time.sleep(1)
                        else:
                            self.log_signal.emit("error", f"没有输入密码\n")

                        if (d(textContains='请输入钱包密码').exists(timeout=3)):
                            print("，请输入钱包密码")
                            self.log_signal.emit("info", f"输入密码\n")
                            d(textContains='请输入钱包密码').set_text(str(trade_password))
                            time.sleep(1)
                        else:
                            self.log_signal.emit("error", f"没有输入密码\n")

                        if (d(text='确认').exists(timeout=3)):
                            print("，确认")
                            self.log_signal.emit("info", f"最后点击确认\n")
                            d(text='确认').click()
                            time.sleep(3)
                        else:
                            self.log_signal.emit("error", f"没有最后确认，退出\n")
                            # return "66"
                    else:
                        self.log_signal.emit("info",
                                             f"\n【投注环节】赢局→结果 '{latest_result}' 是多值（拆分后：{parts}），不符合投注条件，不投注")
                else:
                    # 输局：强制投注，无论单/多值（核心需求）
                    # 打印输局强制投注的触发标识（核心跟踪点9：确认是否进入输局强制逻辑）
                    self.log_signal.emit("info",
                                         f"【投注环节-输局强制触发】上一轮输赢为'输' → 无论单/多值均强制投注（当前结果：{latest_result} | 拆分后：{parts}）")
                    self.current_bet = self.calculate_bet_target(latest_result, genfan, TARGET_SINGLE)
                    next_stake = self.get_current_stake(self.current_bet, dan, shuang)
                    current_strategy = genfan[self.current_stake_group][self.current_stake_index]
                    self.log_signal.emit("info", f"\n【投注环节】输局→强制投注触发！（单/多值均支持）")
                    self.log_signal.emit("info",
                                         f"  基准结果: {latest_result}（取第一个有效值：{valid_results[0]}） | 当前策略: {current_strategy}")
                    self.log_signal.emit("info", f"  投注目标: {self.current_bet} | 投注金额: {next_stake}")
                    self.log_signal.emit("info",
                                         f"  金额状态: 第{self.current_stake_group + 1}组第{self.current_stake_index + 1}个金额")
                    # 执行UI自动化投注流程（与赢局流程一致）
                    result_back = backToTpHome(d, self.log_signal)
                    if result_back != 1:
                        self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                        return "66"
                    self.log_signal.emit("info", f"回到钱包首页\n")
                    if d(text='转账').exists(timeout=3):
                        d(text='转账').click()
                        time.sleep(1)
                        self.log_signal.emit("info", f"点击转账按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击转账失败，退出\n")
                        return "66"
                    if d(text='TRX').exists(timeout=3):
                        d(text='TRX').click()
                        time.sleep(1)
                        self.log_signal.emit("info", f"点击TRX按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击TRX按钮失败，退出\n")
                        return "66"
                    if d(textContains='输入或粘贴').exists(timeout=3):
                        d(textContains='输入或粘贴').set_text(wallet_address)
                        time.sleep(2)
                        self.log_signal.emit("info", f"输入钱包地址\n")
                    else:
                        self.log_signal.emit("error", f"输入钱包地址失败，退出\n")
                        return "66"
                    if d(textContains='请输入数量').exists(timeout=3):
                        d(textContains='请输入数量').set_text(str(next_stake))
                        time.sleep(2)
                        self.log_signal.emit("info", f"输入数量\n")
                    else:
                        self.log_signal.emit("error", f"输入数量失败，退出\n")
                        return "66"
                    if d(textContains='确认').exists(timeout=3):
                        d(textContains='确认').click()
                        time.sleep(5)
                        self.log_signal.emit("info", f"点击确认按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击确认按钮失败，退出\n")
                        return "66"
                    if d(textContains='继续转账').exists(timeout=3):
                        d(textContains='继续转账').click()
                        time.sleep(2)
                        self.log_signal.emit("info", f"点击继续转账\n")
                    else:
                        self.log_signal.emit("warning", f"未找到继续转账按钮，继续下一步\n")
                    if d(textContains='确认支付').exists(timeout=3):
                        d(textContains='确认支付').click()
                        time.sleep(2)
                        self.log_signal.emit("info", f"确认支付\n")
                    else:
                        self.log_signal.emit("error", f"未找到确认支付按钮，退出\n")
                        # return "66"
                    if d(textContains='请输入钱包密码').exists(timeout=3):
                        d(textContains='请输入钱包密码').set_text(str(trade_password))
                        time.sleep(2)
                        self.log_signal.emit("info", f"输入钱包密码\n")
                    else:
                        self.log_signal.emit("warning", f"未找到密码输入框，尝试直接确认\n")
                    if d(text='确认').exists(timeout=3):
                        d(text='确认').click()
                        time.sleep(2)
                        self.log_signal.emit("info", f"最后点击确认\n")
                    else:
                        self.log_signal.emit("error", f"未找到最后确认按钮，退出\n")
                        # return "66"
                    # 投注后返回首页
                    result_back = backToTpHome(d, self.log_signal)
                    if result_back != 1:
                        self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                        return "66"

            self.log_signal.emit("info", "=" * 50 + "\n")
        except BaseException as e:
            print(e)

    def show_bet_statistics(self, genfan):
        """显示投注历史统计（总次数、胜率、盈亏等）"""
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

        # 按结果类型统计（核心跟踪点10：多值/单值结果的投注次数）
        single_count = sum(1 for record in self.bet_history if record.get("result_type") == "单值")
        multi_count = sum(1 for record in self.bet_history if record.get("result_type") == "多值")
        # 按策略统计（核心跟踪点10：各策略的使用次数）
        strategy_count = {}
        for record in self.bet_history:
            strategy = record.get("used_strategy", "未知")
            strategy_count[strategy] = strategy_count.get(strategy, 0) + 1

        # 打印统计信息
        self.log_signal.emit("info", "【历史统计】" + "-" * 40)
        self.log_signal.emit("info", f"总投注次数: {total} | 赢局: {wins}次 🎉 | 输局: {losses}次 ❌")
        self.log_signal.emit("info", f"结果类型统计: 单值{single_count}次 | 多值{multi_count}次")  # 新增
        self.log_signal.emit("info", f"策略使用统计: {strategy_count}")  # 新增
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
        # 显示当前策略信息
        current_strategy = ""
        if self.current_stake_group < len(genfan) and self.current_stake_index < len(genfan[self.current_stake_group]):
            current_strategy = genfan[self.current_stake_group][self.current_stake_index]
        if self.current_stake_group == 0:
            self.log_signal.emit("info",
                                 f"当前状态: 第1组（无需累计赢局） | 上一轮输赢: {self.last_round_result} | 当前策略: {current_strategy}")
        else:
            self.log_signal.emit("info",
                                 f"当前状态: 第{self.current_stake_group + 1}组 | 累计赢局{self.total_win_count}/3次 | 上一轮输赢: {self.last_round_result} | 当前策略: {current_strategy}")
        self.log_signal.emit("info", "-" * 40)

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
        if len(devices) > 0:
            try:
                d = u2.connect(devices[0])
                self.log_signal.emit("info", "当前手机连接成功，开始")
                # 打印连接的设备ID（方便多设备时区分）
                self.log_signal.emit("info", f"【设备信息】连接设备ID：{devices[0]} | 设备数量：{len(devices)}")
            except BaseException as e:
                self.log_signal.emit("error", f"当前手机连接失败，无法启动业务逻辑: {str(e)}")
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
            self.log_signal.emit("info", f"解析配置：单金额组={dan}，双金额组={shuang}，跟反策略={genfan}")
            # 校验策略格式是否符合“4组3策略”（你的配置是反反跟-跟跟跟-跟跟跟-跟跟跟）
            if len(genfan) != 4:
                self.log_signal.emit("warning", f"【策略格式警告】跟反策略应为4组（当前{len(genfan)}组），可能导致索引异常")
            for i, g in enumerate(genfan):
                if len(g) != 3:
                    self.log_signal.emit("warning",
                                         f"【策略格式警告】第{i + 1}组策略应为3个（当前{len(g)}个），可能导致索引异常")
        except Exception as e:
            self.log_signal.emit("error", f"配置解析失败（金额组/策略格式错误）：{str(e)}")
            return

        TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件

        # 脚本启动提示（补充初始投注规则）
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", "          彩票跟随投注监控脚本（输局强制投注版）")
        self.log_signal.emit("info", f"          当前模式: {'测试模式' if TEST_MODE else '正常模式'}")
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", f"监控接口: {API_URL}")
        self.log_signal.emit("info", f"检查时间: 每分钟第{CHECK_SECOND}秒")
        self.log_signal.emit("info", "核心规则（重点修改）:")
        self.log_signal.emit("info", "1. 初始投注：必须单值结果（单/双）才触发，与赢局规则一致")
        self.log_signal.emit("info", "2. 赢局后续：仅单值结果投注；多值结果不投注")
        self.log_signal.emit("info", "3. 输局后续：无论单值（单/双）还是多值（单,单/双,双），均强制投注")
        self.log_signal.emit("info", "4. 输局投注逻辑：从结果中取第一个有效值，按跟反策略计算目标")
        self.log_signal.emit("info", "5. 金额组规则不变：赢局累计回溯，输局组内递进/升级")
        self.log_signal.emit("info", "判定提示: 赢局 🎉 | 输局 ❌")
        # 日志查看指引（告诉如何定位漏投）
        self.log_signal.emit("info",
                             "【日志排查指引】漏投时重点看：1.输局是否打印'强制触发' 2.策略索引是否正确 3.多值是否取第一个有效值")

        # 测试模式说明（仅测试模式显示）
        if TEST_MODE:
            self.log_signal.emit("info", "\n测试模式说明:")
            self.log_signal.emit("info", "- 初始阶段：仅输入单/双会触发投注，输入单,双不触发")
            self.log_signal.emit("info", "- 初始触发后：输局时输入单/双/单,双都会强制投注")
            self.log_signal.emit("info", "- 初始触发后：赢局时仅输入单/双会投注，输入单,双不投注")
            self.log_signal.emit("info", "- 输入 'q' 直接退出测试模式")
            # 测试模式下模拟漏投场景的指引
            self.log_signal.emit("info", "- 测试漏投场景：连续输入'双'→'双'→'双双双双'，观察第三次是否打印'输局强制触发'")
        self.log_signal.emit("info", "=" * 60 + "\n")

        # 启动钱包APP并返回首页
        try:
            d.app_start(package_name="vip.mytokenpocket")
            time.sleep(2)
            back_result = backToTpHome(d, self.log_signal)
            if back_result != 1:
                self.log_signal.emit("error", "启动钱包APP后无法返回首页，退出")
                return
        except Exception as e:
            self.log_signal.emit("error", f"启动钱包APP失败: {str(e)}")
            return

        try:
            # 主循环：持续检查数据并执行投注逻辑
            while True:
                result_back = backToTpHome(d, self.log_signal)
                if result_back != 1:
                    self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                    return "66"
                self.wait_until_target_second(CHECK_SECOND, TEST_MODE)
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                self.log_signal.emit("info", f"【主流程】[{current_time}] 开始检查数据...")

                # 获取结果（测试模式手动输入，正常模式API获取），传入genfan参数
                latest_result = self.fetch_lottery_data(TEST_MODE, TARGET_SINGLE, API_URL, genfan)
                if not latest_result:
                    self.log_signal.emit("warning", f"【主流程】未获取到有效数据，跳过本次\n")
                    time.sleep(1)
                    continue

                # 执行核心投注逻辑
                result_betting = self.execute_betting_logic(
                    latest_result, API_URL, CHECK_SECOND, TEST_MODE, shuang, dan, genfan,
                    TARGET_SINGLE, d, wallet_address, trade_password
                )
                if result_betting == "66":
                    self.log_signal.emit("error", "\n************************投注流程失败，返回**********************")
                    continue
                if TEST_MODE:
                    # 测试模式增加短暂停顿，方便查看输出
                    time.sleep(0.5)

        except KeyboardInterrupt:
            # 手动停止脚本（Ctrl+C），显示最终统计
            self.log_signal.emit("info", "\n" + "=" * 50)
            self.log_signal.emit("info", "脚本已手动停止")
            if self.bet_history:
                self.log_signal.emit("info", "\n【最终统计】")
                self.show_bet_statistics(genfan)
            self.log_signal.emit("info", "=" * 50)
        except Exception as e:
            # 捕获其他异常，避免脚本崩溃
            self.log_signal.emit("error", f"\n【脚本异常】{str(e)}")
            # 打印异常堆栈（方便定位代码错误）
            import traceback
            self.log_signal.emit("error", f"【异常堆栈】{traceback.format_exc()}")


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


def backToTpHome(d, log_signal):
    """返回钱包首页（通过点击“我的”验证），新增log_signal参数"""
    dd = 0
    time.sleep(1)
    while dd < 10:
        # 检查是否已在首页（存在“我的”按钮）
        if d(text='我的').exists(timeout=1):
            print("已回到钱包首页---shuzhui")
            # 打印首页验证日志
            log_signal.emit("info", "【首页验证】成功找到'我的'按钮，确认已回到钱包首页")
            return 1
        # 未在首页，按返回键
        d.press("back")
        # 打印返回键操作日志
        log_signal.emit("info", f"【首页返回】未找到'我的'按钮，按返回键（当前尝试次数：{dd + 1}/10）")
        time.sleep(1)
        dd += 1
    print("尝试返回首页失败（超过10次）")
    log_signal.emit("error", "【首页返回失败】尝试10次仍未找到'我的'按钮，可能APP界面异常")
    return 2
