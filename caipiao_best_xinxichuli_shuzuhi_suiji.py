import os
import requests
import time
import datetime
import json
import random
from PyQt6.QtCore import pyqtSignal
import uiautomator2 as u2
import subprocess


class LotteryLogic:
    def __init__(self):
        # 接收界面传递的日志信号（由主程序赋值）
        self.log_signal = None
        self.profit_update_signal = None
        # 初始化实例变量（核心修改：移除跟反/金额组，新增单双序列+单/双金额列表）
        self.current_bet = None  # 当前待判定的投注目标
        self.last_round_result = "输"  # 记录上一轮输赢结果（用于判断是否强制投注）
        self.initial_bet_triggered = False  # 标记初始投注是否已触发（需单值结果）
        self.bet_history = []  # 投注历史记录

        # 新增：单双序列相关（替代跟反策略）
        self.bet_sequence = []  # 生成的50个单双方案列表（核心）
        self.current_sequence_index = 0  # 当前使用的单双序列索引（显式初始化为0）
        # 新增：单/双金额列表（核心修改：分单/双存储金额）
        self.dan_amounts = []  # 单路金额列表（对应dan_str）
        self.shuang_amounts = []  # 双路金额列表（对应shuang_str）
        self.current_stake_index = 0  # 当前金额索引（与单双索引同步，显式初始化为0）

    def load_config(self):
        """加载本地配置（新增danshuang1-6、dan_str、shuang_str的加载）"""
        if os.path.exists("lottery_simple_config.json"):
            try:
                with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.log_signal.emit("info", f"配置加载成功：{config}")
                # 打印关键配置（方便核对）
                for i in range(1, 7):
                    key = f"danshuang{i}"
                    if key in config:
                        self.log_signal.emit("info", f"【配置校验】{key}原始配置：{config[key]}")
                # 新增：校验单/双金额配置
                if "dan" in config:
                    self.log_signal.emit("info", f"【配置校验】单路金额(dan)原始配置：{config['dan']}")
                if "shuang" in config:
                    self.log_signal.emit("info", f"【配置校验】双路金额(shuang)原始配置：{config['shuang']}")
                return config
            except Exception as e:
                self.log_signal.emit("error", f"配置加载失败：{str(e)}")
                return None
        else:
            self.log_signal.emit("warning", "未找到本地配置文件，使用空配置")
            return None

    def generate_bet_sequence(self, danshuang1, danshuang2, danshuang3, danshuang4, danshuang5, danshuang6):
        """
        生成50个单双的投注序列（核心函数）
        规则：以danshuang1为起点，后面随机拼接danshuang2-6的内容，直到总长度≥50
        """
        try:
            # 拆分各单双配置为列表
            seq1 = [p.strip() for p in danshuang1.split(',') if p.strip() in ["单", "双"]]
            seq2 = [p.strip() for p in danshuang2.split(',') if p.strip() in ["单", "双"]]
            seq3 = [p.strip() for p in danshuang3.split(',') if p.strip() in ["单", "双"]]
            seq4 = [p.strip() for p in danshuang4.split(',') if p.strip() in ["单", "双"]]
            seq5 = [p.strip() for p in danshuang5.split(',') if p.strip() in ["单", "双"]]
            seq6 = [p.strip() for p in danshuang6.split(',') if p.strip() in ["单", "双"]]

            # 验证基础序列有效性
            if not seq1:
                self.log_signal.emit("error", "danshuang1配置无效（无单/双值），默认使用['单']")
                seq1 = ["单"]
            candidate_seqs = [seq2, seq3, seq4, seq5, seq6]
            # 过滤空的候选序列
            candidate_seqs = [s for s in candidate_seqs if s]
            if not candidate_seqs:
                self.log_signal.emit("warning", "danshuang2-6均无效，仅使用danshuang1填充")
                candidate_seqs = [seq1]

            # 生成50长度的序列
            final_seq = seq1.copy()
            while len(final_seq) < 50:
                # 随机选择一个候选序列拼接
                random_seq = random.choice(candidate_seqs)
                final_seq.extend(random_seq)

            # 截断到50个（防止超出）
            self.bet_sequence = final_seq[:50]
            self.log_signal.emit("success", f"【序列生成】成功生成50个单双投注序列：{self.bet_sequence}")
            self.log_signal.emit("info",
                                 f"【序列详情】起点（danshuang1）：{seq1} | 后续随机拼接：{[len(s) for s in candidate_seqs]}个元素的序列")
            return self.bet_sequence
        except Exception as e:
            self.log_signal.emit("error", f"生成单双序列失败：{str(e)}")
            # 异常时生成默认序列
            self.bet_sequence = ["单", "双"] * 25  # 单双交替填充50个
            self.log_signal.emit("warning", f"使用默认序列：{self.bet_sequence}")
            return self.bet_sequence

    def fetch_lottery_data(self, TEST_MODE, TARGET_SINGLE, API_URL):
        """从接口获取彩票数据，测试模式下手动输入（移除genfan参数）"""
        if TEST_MODE:
            # 测试模式：显示当前序列/金额索引状态
            self.log_signal.emit("info", "\n" + "=" * 40)
            self.log_signal.emit("info", "        测试模式 - 请输入模拟结果")
            self.log_signal.emit("info", "=" * 40)
            init_status = "未触发（需单值结果）" if not self.initial_bet_triggered else "已触发"
            # 显示核心状态（序列索引+金额索引+当前单/双金额）
            current_seq_value = self.bet_sequence[self.current_sequence_index] if self.current_sequence_index < len(
                self.bet_sequence) else "无"
            current_stake_value = self.get_current_stake()

            msg = f"当前状态：序列索引{self.current_sequence_index}/50（值：{current_seq_value}） | 金额索引{self.current_stake_index} | 当前金额：{current_stake_value} | 初始投注：{init_status} | 待判定投注：{self.current_bet if self.current_bet else '无'} | 上一轮结果：{self.last_round_result}"
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
                print(f"获取的结果是=",data)

                if data.get("code") == "0" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
                    latest_result = str(data["data"][0]).strip()
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

    def get_current_stake(self):
        """
        核心修改：优化金额索引循环逻辑，避免索引无限递增导致的状态错乱
        - 单：取dan_amounts对应索引值
        - 双：取shuang_amounts对应索引值
        - 索引越界时：自动重置为0并循环
        """
        try:
            # 先获取当前投注目标（单/双）
            current_target = self.get_current_bet_target()
            # 选择对应的金额列表
            if current_target == "单":
                target_amounts = self.dan_amounts
                amount_type = "单路"
            else:
                target_amounts = self.shuang_amounts
                amount_type = "双路"

            # 索引越界保护：空列表返回0
            if not target_amounts:
                self.log_signal.emit("error", f"{amount_type}金额列表为空，默认返回0")
                return 0

            # 核心优化：索引越界时重置为0，保证索引始终在列表范围内
            list_length = len(target_amounts)
            if self.current_stake_index >= list_length:
                self.current_stake_index = 0  # 重置为0
                self.log_signal.emit("warning",
                                     f"{amount_type}金额索引超出列表长度{list_length}，已重置为0并循环")

            current_amount = target_amounts[self.current_stake_index]
            self.log_signal.emit("info",
                                 f"【获取金额】{amount_type} | 当前索引{self.current_stake_index} → 金额{current_amount}")
            return current_amount
        except Exception as e:
            self.log_signal.emit("error", f"【获取金额异常】{str(e)}")
            return 0

    def update_sequence_and_stake_index(self, win):
        """
        核心规则：赢则重置索引+重新生成序列，输则递进索引（保证序列/金额索引同步）
        :param win: 是否赢局
        """
        # 先更新上一轮输赢记录
        old_last_result = self.last_round_result
        self.last_round_result = "赢" if win else "输"
        self.log_signal.emit("info",
                             f"【输赢状态更新】上一轮原始结果：{'赢' if win else '输'} | 更新前状态：{old_last_result} | 更新后状态：{self.last_round_result}")

        if win:
            print("赢了之后重新排序")
            # 赢局：重置所有索引+重新生成单双序列
            old_seq_index = self.current_sequence_index
            old_stake_index = self.current_stake_index
            self.current_sequence_index = 0
            self.current_stake_index = 0
            # 重新生成50个单双序列
            config = self.load_config()
            if config:
                self.generate_bet_sequence(
                    config.get("danshuang1", ""),
                    config.get("danshuang2", ""),
                    config.get("danshuang3", ""),
                    config.get("danshuang4", ""),
                    config.get("danshuang5", ""),
                    config.get("danshuang6", "")
                )
            print(self.bet_sequence)
            self.log_signal.emit("success",
                                 f"【赢局重置】序列索引：{old_seq_index}→0 | 金额索引：{old_stake_index}→0 | 已重新生成50个单双序列")
        else:
            # 输局：递进索引（同步递增，且序列索引越界时重置为0，保证和金额索引同步）
            old_seq_index = self.current_sequence_index
            old_stake_index = self.current_stake_index

            # 序列索引递进（50个为一轮，越界重置）
            self.current_sequence_index += 1
            if self.current_sequence_index >= 50:
                self.current_sequence_index = 0
                self.log_signal.emit("warning", f"序列索引超出50，重置为0")

            # 金额索引递进（和序列索引同步，由get_current_stake保证越界重置）
            self.current_stake_index += 1

            self.log_signal.emit("warning",
                                 f"【输局递进】序列索引：{old_seq_index}→{self.current_sequence_index} | 金额索引：{old_stake_index}→{self.current_stake_index}")

    def get_current_bet_target(self):
        """获取当前投注目标（直接从预生成的单双序列取）"""
        try:
            if not self.bet_sequence:
                self.log_signal.emit("error", "单双序列为空，默认投注'单'")
                return "单"
            # 索引越界保护
            if self.current_sequence_index >= len(self.bet_sequence):
                self.current_sequence_index = 0
                self.log_signal.emit("warning", f"序列索引超出长度，重置为0")
            target = self.bet_sequence[self.current_sequence_index]
            self.log_signal.emit("info", f"【获取投注目标】序列索引{self.current_sequence_index} → {target}")
            return target
        except Exception as e:
            self.log_signal.emit("error", f"【获取投注目标异常】{str(e)}")
            return "单"

    def execute_betting_logic(self, latest_result, API_URL, CHECK_SECOND, TEST_MODE, TARGET_SINGLE, d, wallet_address,
                              trade_password):
        try:
            """执行完整投注逻辑：结果分类→输赢判定→索引更新→新投注生成（输局强制投注）"""
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_signal.emit("info", "\n" + "=" * 50)
            self.log_signal.emit("info", f"【投注逻辑】开始执行 - {current_time}")

            # 打印核心状态（序列+金额索引+单/双金额）
            parts = [p.strip() for p in latest_result.split(",")]
            is_single_result = (latest_result in TARGET_SINGLE)
            current_seq_value = self.bet_sequence[self.current_sequence_index] if self.current_sequence_index < len(
                self.bet_sequence) else "无"
            current_stake_value = self.get_current_stake()

            msg = f"【当前状态-全量】最新结果: {latest_result}（拆分后：{parts} | 类型：{'多值' if len(parts) > 1 else '单值'}） | 待判定投注：{self.current_bet if self.current_bet else '无'} | 上一轮输赢：{self.last_round_result} | 初始投注：{'已触发' if self.initial_bet_triggered else '未触发（需单值）'} | 序列索引：{self.current_sequence_index}/50（值：{current_seq_value}） | 金额索引：{self.current_stake_index}（值：{current_stake_value}）"
            self.log_signal.emit("info", msg)

            # 1. 结果分类：单值/多值（仅用于赢局判定，输局不限制）
            is_single_result = (latest_result in TARGET_SINGLE)
            multi_result_list = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            self.log_signal.emit("info",
                                 f"【结果分类-详情】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list} | 有效结果总数：{len(multi_result_list)} | 多值是否包含上一轮投注：{self.current_bet in multi_result_list if self.current_bet else '无待判定投注'}")

            # 2. 输赢判定（仅当有“待判定投注”时触发）
            judge_triggered = False
            win = False
            stake_amount = 0

            if self.current_bet is not None:
                judge_triggered = True
                stake_amount = self.get_current_stake()
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

                # 关键修复：保存更新前的旧索引（用于投注历史）
                old_seq_index = self.current_sequence_index
                old_stake_index = self.current_stake_index

                # 更新序列和金额索引（核心规则）
                self.update_sequence_and_stake_index(win)

                # 记录投注历史（用于统计）
                self.bet_history.append({
                    "time": current_time,
                    "bet_target": self.current_bet,
                    "stake_amount": stake_amount,
                    "actual_result": latest_result,
                    "win": win,
                    "seq_index": old_seq_index,  # 已定义的旧索引
                    "stake_index": old_stake_index,  # 已定义的旧索引
                    "result_type": "多值" if len(parts) > 1 else "单值"
                })
                self.show_bet_statistics()
                self.current_bet = None  # 判定完成后清空待判定投注

            # 3. 新投注生成（核心修改：取预生成的单双序列）
            # 先判断是否有有效结果（避免极端情况无有效值）
            valid_results = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
            if not valid_results:
                self.log_signal.emit("error", f"【投注环节】结果 '{latest_result}' 无有效单/双值，不投注")
                self.log_signal.emit("info", "=" * 50 + "\n")
                return

            # 核心逻辑：区分“初始投注”和“后续投注”
            self.log_signal.emit("info",
                                 f"【投注触发条件】初始投注状态：{self.initial_bet_triggered} | 上一轮输赢：{self.last_round_result} | 结果类型：{'多值' if len(parts) > 1 else '单值'} | 有效结果数：{len(valid_results)}")

            if not self.initial_bet_triggered:
                # 初始投注：必须单值结果才触发
                if is_single_result:
                    self.current_bet = self.get_current_bet_target()
                    next_stake = self.get_current_stake()
                    self.log_signal.emit("info", f"\n【投注环节】初始投注触发！（单值结果符合要求）")
                    self.log_signal.emit("info",
                                         f"  投注目标: {self.current_bet}（序列索引{self.current_sequence_index}） | 投注金额: {next_stake}（{self.current_bet}路金额索引{self.current_stake_index}）")
                    # 标记初始投注已触发
                    self.initial_bet_triggered = True
                    self.log_signal.emit("success", f"【初始投注状态】未触发 → 已触发（后续输局将强制投注）")
                    # 执行UI自动化投注流程
                    result_back = backToTpHome(d, self.log_signal)
                    if result_back != 1:
                        self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                        return "66"
                    self.log_signal.emit("info", f"回到钱包首页\n")
                    if (d(text='转账').exists(timeout=3)):
                        d(text='转账').click()
                        time.sleep(0.5)
                        self.log_signal.emit("info", f"点击转账按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击转账失败，退出\n")
                        return "66"

                    if (d(text='TRX').exists(timeout=5)):
                        d(text='TRX').click()
                        time.sleep(0.5)
                        self.log_signal.emit("info", f"点击TRX按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击TRX按钮失败，退出\n")
                        return "66"

                    if (d(textContains='输入或粘贴').exists(timeout=3)):
                        d(textContains='输入或粘贴').set_text(wallet_address)
                        time.sleep(1)
                        self.log_signal.emit("info", f"输入钱包地址\n")
                    else:
                        self.log_signal.emit("error", f"输入钱包地址失败，退出\n")
                        return "66"

                    if (d(textContains='请输入数量').exists(timeout=3)):
                        d(textContains='请输入数量').set_text(str(next_stake))
                        time.sleep(1)
                        self.log_signal.emit("info", f"输入数量\n")
                    else:
                        self.log_signal.emit("error", f"输入数量失败，退出\n")
                        return "66"

                    if (d(textContains='确认').exists(timeout=3)):
                        d(textContains='确认').click()
                        time.sleep(4)
                        self.log_signal.emit("info", f"点击确认按钮\n")
                    else:
                        self.log_signal.emit("error", f"点击确认按钮失败，退出\n")
                        return "66"

                    if (d(textContains='继续转账').exists(timeout=3)):
                        d(textContains='继续转账').click()
                        time.sleep(1)
                        self.log_signal.emit("info", f"点击继续转账\n")
                    else:
                        self.log_signal.emit("warning", f"未找到继续转账按钮，继续下一步\n")

                    if (d(textContains='确认支付').exists(timeout=3)):
                        d(textContains='确认支付').click()
                        time.sleep(3)
                        self.log_signal.emit("info", f"确认支付\n")
                    else:
                        self.log_signal.emit("warning", f"未找到确认支付按钮，继续下一步\n")

                    if (d(textContains='请输入钱包密码').exists(timeout=1)):
                        d(textContains='请输入钱包密码').click()
                        time.sleep(0.5)
                        d(textContains='请输入钱包密码').set_text(str(trade_password))
                        time.sleep(1)
                        self.log_signal.emit("info", f"输入密码\n")
                    else:
                        self.log_signal.emit("warning", f"未找到密码输入框，尝试直接确认\n")

                    if (d(text='确认').exists(timeout=3)):
                        d(text='确认').click()
                        time.sleep(1.5)
                        self.log_signal.emit("info", f"最后点击确认\n")
                    else:
                        self.log_signal.emit("error", f"未找到最后确认按钮，退出\n")
                        return "66"
                else:
                    self.log_signal.emit("info",
                                         f"\n【投注环节】初始投注未触发！结果 '{latest_result}' 是多值（拆分后：{parts}），需单值结果才开始")
            else:
                # 后续投注：区分赢局/输局
                if self.last_round_result == "赢":
                    # 赢局：无论单值/多值都投注（用户要求）
                    self.current_bet = self.get_current_bet_target()
                    next_stake = self.get_current_stake()
                    self.log_signal.emit("info", f"\n【投注环节】赢局→投注触发！（单/多值均支持）")
                    self.log_signal.emit("info",
                                         f"  投注目标: {self.current_bet}（序列索引{self.current_sequence_index}） | 投注金额: {next_stake}（{self.current_bet}路金额索引{self.current_stake_index}）")
                    # 执行UI自动化投注流程
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
                        self.log_signal.emit("warning", f"未找到确认支付按钮，继续下一步\n")
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
                        self.log_signal.emit("warning", f"未找到最后确认按钮，继续下一步\n")
                else:
                    # 输局：强制投注，无论单/多值
                    self.log_signal.emit("info",
                                         f"【投注环节-输局强制触发】上一轮输赢为'输' → 无论单/多值均强制投注（当前结果：{latest_result} | 拆分后：{parts}）")
                    self.current_bet = self.get_current_bet_target()
                    next_stake = self.get_current_stake()
                    self.log_signal.emit("info", f"\n【投注环节】输局→强制投注触发！（单/多值均支持）")
                    self.log_signal.emit("info",
                                         f"  投注目标: {self.current_bet}（序列索引{self.current_sequence_index}） | 投注金额: {next_stake}（{self.current_bet}路金额索引{self.current_stake_index}）")
                    # 执行UI自动化投注流程
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
                        self.log_signal.emit("warning", f"未找到确认支付按钮，继续下一步\n")
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
                        self.log_signal.emit("warning", f"未找到最后确认按钮，继续下一步\n")
                    # 投注后返回首页
                    result_back = backToTpHome(d, self.log_signal)
                    if result_back != 1:
                        self.log_signal.emit("error", f"回到钱包首页失败，退出\n")
                        return "66"

            self.log_signal.emit("info", "=" * 50 + "\n")
        except BaseException as e:
            self.log_signal.emit("error", f"【投注逻辑异常】{str(e)}")
            import traceback
            self.log_signal.emit("error", f"【异常堆栈】{traceback.format_exc()}")

    def show_bet_statistics(self):
        """显示投注历史统计（适配单/双金额）"""
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

        # 按结果类型统计
        single_count = sum(1 for record in self.bet_history if record.get("result_type") == "单值")
        multi_count = sum(1 for record in self.bet_history if record.get("result_type") == "多值")

        # 按单/双投注统计
        dan_bet_count = sum(1 for record in self.bet_history if record.get("bet_target") == "单")
        shuang_bet_count = sum(1 for record in self.bet_history if record.get("bet_target") == "双")

        # 打印统计信息
        self.log_signal.emit("info", "【历史统计】" + "-" * 40)
        self.log_signal.emit("info", f"总投注次数: {total} | 赢局: {wins}次 🎉 | 输局: {losses}次 ❌")
        self.log_signal.emit("info", f"投注类型统计: 单路{dan_bet_count}次 | 双路{shuang_bet_count}次")
        self.log_signal.emit("info", f"结果类型统计: 单值{single_count}次 | 多值{multi_count}次")
        self.log_signal.emit("info", f"胜率: {win_rate:.2f}% | 总盈利: {profit} | 总亏损: {loss}")

        if net_profit > 0:
            self.log_signal.emit("success", f"净盈亏: {net_profit} 🎉")
            self.profit_update_signal.emit("success", f"✅ 净盈亏: {net_profit}")
        elif net_profit < 0:
            self.log_signal.emit("error", f"净盈亏: {net_profit} ❌")
            self.profit_update_signal.emit("error", f"❌净盈亏: {net_profit} ")
        else:
            self.log_signal.emit("info", f"净盈亏: {net_profit}")

        # 补充当前索引状态+单/双金额
        current_seq_value = self.bet_sequence[self.current_sequence_index] if self.current_sequence_index < len(
            self.bet_sequence) else "无"
        current_stake_value = self.get_current_stake()
        self.log_signal.emit("info",
                             f"当前状态: 序列索引{self.current_sequence_index}/50（值：{current_seq_value}） | 金额索引：{self.current_stake_index}（{current_seq_value}路金额：{current_stake_value}） | 上一轮输赢: {self.last_round_result}")
        self.log_signal.emit("info", "-" * 40)

    def yewu(self, config_c=None):
        """业务入口方法（核心修改：加载dan_str/shuang_str金额列表）"""
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
        wallet_address = config_c.get("wallet_address", "")
        trade_password = config_c.get("trade_password", "")

        # 解析单双序列配置
        danshuang1 = config_c.get("danshuang1", "")
        danshuang2 = config_c.get("danshuang2", "")
        danshuang3 = config_c.get("danshuang3", "")
        danshuang4 = config_c.get("danshuang4", "")
        danshuang5 = config_c.get("danshuang5", "")
        danshuang6 = config_c.get("danshuang6", "")

        # 核心修改：解析单/双金额配置（dan_str/shuang_str）
        # 单路金额（dan）
        dan_str = config_c.get("dan", "1,2,3,4,5,6,7,8,9,9,9,9,9")
        try:
            self.dan_amounts = [int(num.strip()) for num in dan_str.split(',') if num.strip().isdigit()]
            if not self.dan_amounts:
                self.dan_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9]
                self.log_signal.emit("warning", "单路金额(dan)配置无效，使用默认列表：[1,2,3,4,5,6,7,8,9,9,9,9,9]")
            self.log_signal.emit("info", f"解析单路金额(dan)成功：{self.dan_amounts}")
        except Exception as e:
            self.dan_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9]
            self.log_signal.emit("error", f"解析单路金额(dan)失败：{str(e)}，使用默认列表")

        # 双路金额（shuang）
        shuang_str = config_c.get("shuang", "1,2,3,4,5,6,7,8,9,9,9,9,9")
        try:
            self.shuang_amounts = [int(num.strip()) for num in shuang_str.split(',') if num.strip().isdigit()]
            if not self.shuang_amounts:
                self.shuang_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9]
                self.log_signal.emit("warning", "双路金额(shuang)配置无效，使用默认列表：[1,2,3,4,5,6,7,8,9,9,9,9,9]")
            self.log_signal.emit("info", f"解析双路金额(shuang)成功：{self.shuang_amounts}")
        except Exception as e:
            self.shuang_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9]
            self.log_signal.emit("error", f"解析双路金额(shuang)失败：{str(e)}，使用默认列表")
        print("--------------------")
        print(self.dan_amounts)
        print(self.shuang_amounts)

        # 转换测试模式（字符串→布尔值）
        TEST_MODE = True if TEST_MODE == "是" else False

        # 生成初始的50个单双序列
        self.generate_bet_sequence(danshuang1, danshuang2, danshuang3, danshuang4, danshuang5, danshuang6)
        print("----", self.bet_sequence)
        TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件

        # 脚本启动提示（更新规则说明）
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", "          彩票投注脚本（单/双金额分离版）")
        self.log_signal.emit("info", f"          当前模式: {'测试模式' if TEST_MODE else '正常模式'}")
        self.log_signal.emit("info", "=" * 60)
        self.log_signal.emit("info", f"监控接口: {API_URL}")
        self.log_signal.emit("info", f"检查时间: 每分钟第{CHECK_SECOND}秒")
        self.log_signal.emit("info", "核心规则（单/双金额分离）:")
        self.log_signal.emit("info", "1. 单双序列：以danshuang1为起点，随机拼接danshuang2-6生成50个单双值")
        self.log_signal.emit("info", "2. 金额规则：单路取dan配置，双路取shuang配置，索引越界时自动重置为0")
        self.log_signal.emit("info", "3. 赢局规则：重置序列/金额索引为0 + 重新生成50个单双序列")
        self.log_signal.emit("info", "4. 输局规则：序列/金额索引同步递进（索引越界自动重置）")
        self.log_signal.emit("info", "5. 初始投注：必须单值结果（单/双）才触发")
        self.log_signal.emit("info", "6. 赢局后续：单/多值均投注；输局后续：单/多值均强制投注")
        self.log_signal.emit("info", "判定提示: 赢局 🎉 | 输局 ❌")

        # 测试模式说明（仅测试模式显示）
        if TEST_MODE:
            self.log_signal.emit("info", "\n测试模式说明:")
            self.log_signal.emit("info", "- 初始阶段：仅输入单/双会触发投注，输入单,双不触发")
            self.log_signal.emit("info", "- 初始触发后：输局时输入单/双/单,双都会强制投注")
            self.log_signal.emit("info", "- 初始触发后：赢局时输入单/双/单,双都会投注")
            self.log_signal.emit("info", "- 赢局后会重新生成50个单双序列，索引重置为0")
            self.log_signal.emit("info", "- 金额规则：投注单取dan，投注双取shuang，索引越界自动重置为0")
            self.log_signal.emit("info", "- 输入 'q' 直接退出测试模式")
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
                    self.log_signal.emit("error", f"回到钱包首页失败，等待5秒重试\n")
                    time.sleep(5)
                    continue
                self.wait_until_target_second(CHECK_SECOND, TEST_MODE)
                print("时间等待完成")
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                self.log_signal.emit("info", f"【主流程】[{current_time}] 开始检查数据...")

                # 获取结果（测试模式手动输入，正常模式API获取）
                latest_result = self.fetch_lottery_data(TEST_MODE, TARGET_SINGLE, API_URL)
                print("latest_result=", latest_result)
                if not latest_result:
                    self.log_signal.emit("warning", f"【主流程】未获取到有效数据，跳过本次\n")
                    time.sleep(1)
                    continue
                print("======")
                print(latest_result, API_URL, CHECK_SECOND, TEST_MODE, TARGET_SINGLE, d,
                      wallet_address, trade_password)
                # 执行核心投注逻辑
                result_betting = self.execute_betting_logic(
                    latest_result, API_URL, CHECK_SECOND, TEST_MODE, TARGET_SINGLE, d,
                    wallet_address, trade_password
                )
                if result_betting == "66":
                    self.log_signal.emit("error",
                                         "\n************************投注流程失败，5秒后重试**********************")
                    time.sleep(5)
                    continue
                if TEST_MODE:
                    # 测试模式增加短暂停顿，方便查看输出
                    time.sleep(0.5)
                else:
                    time.sleep(1)

        except KeyboardInterrupt:
            # 手动停止脚本（Ctrl+C），显示最终统计
            self.log_signal.emit("info", "\n" + "=" * 50)
            self.log_signal.emit("info", "脚本已手动停止")
            if self.bet_history:
                self.log_signal.emit("info", "\n【最终统计】")
                self.show_bet_statistics()
            self.log_signal.emit("info", "=" * 50)
        except Exception as e:
            # 捕获其他异常，避免脚本崩溃
            self.log_signal.emit("error", f"\n【脚本异常】{str(e)}")
            import traceback
            self.log_signal.emit("error", f"【异常堆栈】{traceback.format_exc()}")
            # 异常后等待5秒继续循环
            time.sleep(5)


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
    """返回钱包首页（通过点击“我的”验证）"""
    dd = 0
    time.sleep(1)
    while dd < 10:
        # 检查是否已在首页（存在“我的”按钮）
        if d(text='我的').exists(timeout=1):
            print("已回到钱包首页---shuzhui")
            log_signal.emit("info", "【首页验证】成功找到'我的'按钮，确认已回到钱包首页")
            return 1
        # 未在首页，按返回键
        d.press("back")
        log_signal.emit("info", f"【首页返回】未找到'我的'按钮，按返回键（当前尝试次数：{dd + 1}/10）")
        time.sleep(1)
        dd += 1
    print("尝试返回首页失败（超过10次）")
    log_signal.emit("error", "【首页返回失败】尝试10次仍未找到'我的'按钮，可能APP界面异常")
    return 2