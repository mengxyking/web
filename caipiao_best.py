import os
import requests
import time
import datetime
import json


def load_config():
    """加载本地配置（新增接口URL和测试模式的加载）"""
    if os.path.exists("lottery_simple_config.json"):
        try:
            with open("lottery_simple_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                print("config=",config)
                return config
        except BaseException as e:
            print("")
#load_config()

# 全局变量
current_bet = None  # 当前待判定的投注目标
current_stake_group = 0  # 当前使用的金额组索引（0-3，对应第1-4组）
current_stake_index = 0  # 当前组内的金额索引（0-2，对应第1-3个金额）
total_win_count = 0  # 累计赢局次数（仅第2/3/4组生效，第1组赢局不累计）
bet_history = []  # 投注历史记录


def fetch_lottery_data(TEST_MODE,TARGET_SINGLE,API_URL):
    """从接口获取彩票数据，测试模式下手动输入"""
    if TEST_MODE:
        # 测试模式：手动输入结果，显示当前组和累计赢局状态
        print("\n" + "=" * 40)
        print("        测试模式 - 请输入模拟结果")
        print("=" * 40)
        if current_stake_group == 0:
            print(f"当前状态：第1组（无需累计赢局） | 待判定投注：{current_bet if current_bet else '无'}")
        else:
            print(
                f"当前状态：第{current_stake_group + 1}组 | 累计赢局{total_win_count}/3次 | 待判定投注：{current_bet if current_bet else '无'}")
        print("请输入模拟结果（例如：单、双、单,双 或 q退出测试）:")

        while True:
            user_input = input("> ").strip()
            if user_input.lower() == 'q':
                print("退出测试模式")
                exit()
            # 验证输入是否有效（仅允许单/双或多值组合）
            parts = [p.strip() for p in user_input.split(",")]
            valid = all(part in TARGET_SINGLE for part in parts)
            if valid:
                return user_input
            print("无效输入，请输入 '单'、'双' 或 用逗号分隔的组合（如'单,双'）")
    else:
        # 正常模式：从API获取真实数据
        try:
            response = requests.get(API_URL, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == "0" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
                latest_result = str(data["data"][0]).strip()
                print(f"【数据提取】最新结果: {latest_result}")
                return latest_result
            print(f"【数据异常】格式错误: {data}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"【请求失败】{str(e)}")
            return None


def wait_until_target_second(target_second,TEST_MODE):
    """等待到当前分钟的目标秒数，测试模式下跳过等待"""
    if TEST_MODE:
        return  # 测试模式无需等待，直接执行
    # 正常模式：精准等待到目标秒数
    while True:
        now = datetime.datetime.now()
        if now.second == target_second:
            return
        sleep_seconds = (target_second - now.second) % 60
        if sleep_seconds > 0:
            next_minute = (now.minute % 60) + (1 if now.second > target_second else 0)
            print(f"【等待执行】需等待 {sleep_seconds} 秒到{next_minute}分{target_second}秒...")
            time.sleep(sleep_seconds)


def get_current_stake(bet_type,dan,shuang):
    """根据投注类型（单/双）获取当前投注金额，确保索引合法"""
    global current_stake_group, current_stake_index

    group = shuang if bet_type == "双" else dan
    # 防止索引越界（极端情况下的安全处理）
    adjusted_group = min(current_stake_group, len(group) - 1)
    adjusted_index = min(current_stake_index, len(group[adjusted_group]) - 1)

    return group[adjusted_group][adjusted_index]


def update_stake_position(win,shuang,dan):
    """根据输赢结果更新金额组位置（核心逻辑：第1组不累计，2-4组累计）"""
    global current_stake_group, current_stake_index, total_win_count

    if win:
        # 赢局处理：区分当前组是否为第1组
        if current_stake_group == 0:
            # 第1组赢局：无需累计，直接重置为本组第1个金额
            current_stake_index = 0
            print(f"【金额更新】第1组赢局 → 保持第1组第1个金额（无需累计）")
        else:
            # 第2/3/4组赢局：累计赢局次数，满3次回溯到第1组
            total_win_count += 1
            print(f"【金额更新】第{current_stake_group + 1}组赢局 → 累计赢局{total_win_count}/3次")

            # 累计满3次：回溯到第1组，重置所有计数
            if total_win_count >= 3:
                current_stake_group = 0
                current_stake_index = 0
                total_win_count = 0
                print(f"【金额回溯】累计赢3次 → 回到第1组第1个金额，累计数重置为0")
            else:
                # 未满3次：保持当前组，回到本组第1个金额
                current_stake_index = 0
                print(f"【金额更新】未累计3次 → 留在第{current_stake_group + 1}组第1个金额")
    else:
        # 输局处理：累计数不变，组内递进，超界升级组（第四组输光回第1组）
        current_stake_index += 1
        current_group = shuang if current_bet == "双" else dan

        # 组内金额用尽（索引超界）：升级到下一组或重置到第1组
        if current_stake_index >= len(current_group[current_stake_group]):
            current_stake_index = 0  # 重置组内索引为第1个金额
            if current_stake_group == len(current_group) - 1:
                # 第四组输光：回到第1组
                current_stake_group = 0
                print(f"【金额重置】第4组输光 → 回到第1组第1个金额（累计赢局数仍为{total_win_count}）")
            else:
                # 其他组输光：升级到下一组
                current_stake_group += 1
                print(
                    f"【金额升级】第{current_stake_group}组输光 → 升级到第{current_stake_group + 1}组第1个金额（累计赢局数{total_win_count}）")
        else:
            # 组内还有金额：递进至下一个金额
            print(
                f"【金额递进】第{current_stake_group + 1}组输局 → 组内递进至第{current_stake_index + 1}个金额（累计赢局数不变）")


def calculate_bet_target(latest_single_result,genfan):
    """根据“跟/反”策略计算当前投注目标（跟=同结果，反=反结果）"""
    global current_stake_group, current_stake_index

    # 获取当前金额组对应的策略（genfan[组索引][组内金额索引]）
    current_strategy = genfan[current_stake_group][current_stake_index]
    print(f"【策略计算】当前策略: {current_strategy} | 上一轮单值结果: {latest_single_result}")

    # 策略执行逻辑
    if current_strategy == "跟":
        return latest_single_result
    elif current_strategy == "反":
        return "双" if latest_single_result == "单" else "单"
    else:
        # 异常策略默认用“跟”
        print(f"【策略异常】未知策略{current_strategy} → 默认使用“跟”策略")
        return latest_single_result


def execute_betting_logic(latest_result,API_URL,CHECK_SECOND,TEST_MODE,shuang,dan,genfan,TARGET_SINGLE):
    """执行完整投注逻辑：结果分类→输赢判定→金额更新→新投注生成"""
    global current_bet, bet_history, current_stake_group, current_stake_index, total_win_count

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n" + "=" * 50)
    print(f"【投注逻辑】开始执行 - {current_time}")
    print(f"【当前状态】最新结果: {latest_result} | 待判定投注: {current_bet if current_bet else '无'}")
    # 状态显示：区分第1组和2-4组的累计状态
    if current_stake_group == 0:
        status_text = f"【金额状态】当前组: 1 | 组内位置: {current_stake_index + 1} | 第1组无需累计"
    else:
        status_text = f"【金额状态】当前组: {current_stake_group + 1} | 组内位置: {current_stake_index + 1} | 累计赢局: {total_win_count}"
    print(status_text)

    # 1. 结果分类：单值（可投注+判定）/多值（仅判定不投注）
    is_single_result = (latest_result in TARGET_SINGLE)
    multi_result_list = [p.strip() for p in latest_result.split(",") if p.strip() in TARGET_SINGLE]
    print(
        f"【结果分类】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list if not is_single_result else '无'}")

    # 2. 输赢判定（仅当有“待判定投注”时触发）
    judge_triggered = False
    win = False
    stake_amount = 0

    if current_bet is not None:
        judge_triggered = True
        stake_amount = get_current_stake(current_bet,dan,shuang)
        print(f"\n【判定环节】触发！上一轮投注: {current_bet} | 投注金额: {stake_amount}")

        # 单值结果：直接对比；多值结果：检查是否包含投注目标
        if is_single_result:
            win = (latest_result == current_bet)
            judge_detail = f"单值对比（{current_bet} vs {latest_result}）"
        else:
            win = (current_bet in multi_result_list)
            judge_detail = f"多值包含检查（{current_bet} in {multi_result_list}）"

        # 输赢结果提示（突出显示）
        if win:
            print("\n" + "=" * 30)
            print("🎉🎉🎉 【判定结果】赢了！🎉🎉🎉")
            print(f"✅ 判定逻辑: {judge_detail}")
            print(f"✅ 赢得金额: {stake_amount}")
            print("=" * 30 + "\n")
        else:
            print("\n" + "=" * 30)
            print("❌❌❌ 【判定结果】输了！❌❌❌")
            print(f"❌ 判定逻辑: {judge_detail}")
            print(f"❌ 输掉金额: {stake_amount}")
            print("=" * 30 + "\n")

        # 更新金额位置（根据输赢结果）
        update_stake_position(win,shuang,dan)

        # 记录投注历史（用于统计）
        bet_history.append({
            "time": current_time,
            "bet_target": current_bet,
            "stake_amount": stake_amount,
            "actual_result": latest_result,
            "win": win,
            "current_group": current_stake_group + 1
        })
        show_bet_statistics()
        current_bet = None  # 判定完成后清空待判定投注

    # 3. 新投注生成（仅单值结果可投注，按跟反策略计算目标）
    if is_single_result:
        current_bet = calculate_bet_target(latest_result,genfan)
        next_stake = get_current_stake(current_bet,dan,shuang)
        current_strategy = genfan[current_stake_group][current_stake_index]
        print(f"\n【投注环节】触发投注！")
        print(f"  上一轮结果: {latest_result} | 当前策略: {current_strategy}")
        print(f"  投注目标: {current_bet} | 投注金额: {next_stake}")
        print(f"  金额状态: 第{current_stake_group + 1}组第{current_stake_index + 1}个金额")
    else:
        print(f"\n【投注环节】结果 '{latest_result}' 是多值，不符合投注条件，不投注")

    print("=" * 50 + "\n")


def show_bet_statistics():
    """显示投注历史统计（总次数、胜率、盈亏等）"""
    if not bet_history:
        return

    total = len(bet_history)
    wins = sum(1 for record in bet_history if record["win"])
    losses = total - wins
    win_rate = (wins / total) * 100 if total > 0 else 0

    # 计算盈亏（赢局加金额，输局减金额）
    profit = sum(record["stake_amount"] for record in bet_history if record["win"])
    loss = sum(record["stake_amount"] for record in bet_history if not record["win"])
    net_profit = profit - loss

    # 打印统计信息
    print("【历史统计】" + "-" * 40)
    print(f"总投注次数: {total} | 赢局: {wins}次 🎉 | 输局: {losses}次 ❌")
    print(f"胜率: {win_rate:.2f}% | 总盈利: {profit} | 总亏损: {loss}")
    print(f"净盈亏: {net_profit} {'🎉' if net_profit > 0 else '❌' if net_profit < 0 else ''}")
    # 补充当前组和累计状态
    if current_stake_group == 0:
        print(f"当前状态: 第1组（无需累计赢局）")
    else:
        print(f"当前状态: 第{current_stake_group + 1}组 | 累计赢局{total_win_count}/3次")
    print("-" * 40)

def yewu():
    config_c = load_config()
    print("config_c=",config_c)
    # 配置参数,
    # API_URL = "https://api.trpsp.com/api/lottery_logs/ds/one/chart?limit=150&page=1"
    TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件
    # CHECK_SECOND = 3  # 每分钟检查的秒数
    # TEST_MODE = False  # 测试模式开关，True为测试模式，False为正常模式
    #
    # # 投注金额配置（4个组，每组3个金额）
    # shuang = [[10, 20, 40], [24, 52, 110], [90, 186, 384], [324, 666, 1342]]  # 双的金额组
    # dan = [[11, 21, 41], [25, 53, fudai_path], [91, 187, 385], [325, 667, 1343]]  # 单的金额组
    # genfan = [["跟", "跟", "反"], ["跟", "跟", "跟"], ["跟", "跟", "跟"], ["跟", "跟", "跟"]]  # 每组的跟反策略
    API_URL = config_c["api_url"]
    CHECK_SECOND = config_c["check_second"]
    TEST_MODE = config_c["test_mode"]
    shuang = config_c["shuang"]
    dan = config_c["dan"]
    genfan = config_c["genfan"]
    if(TEST_MODE == "否"):
        TEST_MODE = False
    else:
        TEST_MODE = True
    print(API_URL,CHECK_SECOND,TEST_MODE,shuang,dan,genfan)

    dan = [[int(num) for num in part.split(',')] for part in dan.split('-')]
    print(dan)
    shuang = [[int(num) for num in part1.split(',')] for part1 in shuang.split('-')]
    print(shuang)
    genfan = [[num for num in part2.split(',')] for part2 in genfan.split('-')]
    print(dan,shuang,genfan)

    # 脚本启动提示
    print("=" * 60)
    print("          彩票跟随投注监控脚本（带测试模式）")
    print(f"          当前模式: {'测试模式' if TEST_MODE else '正常模式'}")
    print("=" * 60)
    print(f"监控接口: {API_URL}")
    print(f"检查时间: 每分钟第{CHECK_SECOND}秒")
    print("核心规则:")
    print("1. 单值结果（单/双）→ 按跟反策略投注；多值结果→只判定不投注")
    print("2. 第1组赢局：无需累计，直接保持本组第1个金额")
    print("3. 第2-4组赢局：累计赢3次→回溯到第1组，输局不清零累计数")
    print("4. 输局处理：组内递进→升级组→第四组输光回第1组")
    print("5. 跟反策略：跟=投上一轮结果，反=投上一轮相反结果")
    print("判定提示: 赢局 🎉 | 输局 ❌")

    # 测试模式说明（仅测试模式显示）
    if TEST_MODE:
        print("\n测试模式说明:")
        print("- 无需等待开奖，手动输入结果即可测试")
        print("- 输入 '单'/'双' 模拟单值结果，'单,双' 模拟多值结果")
        print("- 输入 'q' 直接退出测试模式")
    print("=" * 60 + "\n")

    try:
        # 主循环：持续检查数据并执行投注逻辑
        while True:
            wait_until_target_second(CHECK_SECOND,TEST_MODE)
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"【主流程】[{current_time}] 开始检查数据...")

            # 获取结果（测试模式手动输入，正常模式API获取）
            latest_result = fetch_lottery_data(TEST_MODE,TARGET_SINGLE,API_URL)
            if not latest_result:
                print(f"【主流程】未获取到有效数据，跳过本次\n")
                time.sleep(1)
                continue

            # 执行核心投注逻辑
            execute_betting_logic(latest_result,API_URL,CHECK_SECOND,TEST_MODE,shuang,dan,genfan,TARGET_SINGLE)
            if TEST_MODE:
                # 测试模式增加短暂停顿，方便查看输出
                time.sleep(0.5)

    except KeyboardInterrupt:
        # 手动停止脚本（Ctrl+C），显示最终统计
        print("\n" + "=" * 50)
        print("脚本已手动停止")
        if bet_history:
            print("\n【最终统计】")
            show_bet_statistics()
        print("=" * 50)
    except Exception as e:
        # 捕获其他异常，避免脚本崩溃
        print(f"\n【脚本异常】{str(e)}")
#yewu()
# if __name__ == "__main__":
#     # 脚本启动提示
#     print("=" * 60)
#     print("          彩票跟随投注监控脚本（带测试模式）")
#     print(f"          当前模式: {'测试模式' if TEST_MODE else '正常模式'}")
#     print("=" * 60)
#     print(f"监控接口: {API_URL}")
#     print(f"检查时间: 每分钟第{CHECK_SECOND}秒")
#     print("核心规则:")
#     print("1. 单值结果（单/双）→ 按跟反策略投注；多值结果→只判定不投注")
#     print("2. 第1组赢局：无需累计，直接保持本组第1个金额")
#     print("3. 第2-4组赢局：累计赢3次→回溯到第1组，输局不清零累计数")
#     print("4. 输局处理：组内递进→升级组→第四组输光回第1组")
#     print("5. 跟反策略：跟=投上一轮结果，反=投上一轮相反结果")
#     print("判定提示: 赢局 🎉 | 输局 ❌")
#
#     # 测试模式说明（仅测试模式显示）
#     if TEST_MODE:
#         print("\n测试模式说明:")
#         print("- 无需等待开奖，手动输入结果即可测试")
#         print("- 输入 '单'/'双' 模拟单值结果，'单,双' 模拟多值结果")
#         print("- 输入 'q' 直接退出测试模式")
#     print("=" * 60 + "\n")
#
#     try:
#         # 主循环：持续检查数据并执行投注逻辑
#         while True:
#             wait_until_target_second(CHECK_SECOND)
#             current_time = datetime.datetime.now().strftime('%H:%M:%S')
#             print(f"【主流程】[{current_time}] 开始检查数据...")
#
#             # 获取结果（测试模式手动输入，正常模式API获取）
#             latest_result = fetch_lottery_data()
#             if not latest_result:
#                 print(f"【主流程】未获取到有效数据，跳过本次\n")
#                 time.sleep(1)
#                 continue
#
#             # 执行核心投注逻辑
#             execute_betting_logic(latest_result)
#             if TEST_MODE:
#                 # 测试模式增加短暂停顿，方便查看输出
#                 time.sleep(0.5)
#
#     except KeyboardInterrupt:
#         # 手动停止脚本（Ctrl+C），显示最终统计
#         print("\n" + "=" * 50)
#         print("脚本已手动停止")
#         if bet_history:
#             print("\n【最终统计】")
#             show_bet_statistics()
#         print("=" * 50)
#     except Exception as e:
#         # 捕获其他异常，避免脚本崩溃
#         print(f"\n【脚本异常】{str(e)}")