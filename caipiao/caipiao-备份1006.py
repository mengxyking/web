import requests
import time
import datetime
import json

# 配置参数
API_URL = "https://api.trpsp.com/api/lottery_logs/ds/one/chart?limit=150&page=1"
TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件
CHECK_SECOND = 33  # 每分钟检查的秒数

# 投注金额配置
shuang = [[10, 20, 40], [24, 52, 110], [90, 186, 384], [324, 666, 1342]]
dan = [[11, 21, 41], [25, 53, 111], [91, 187, 385], [325, 667, 1343]]
genfan = [["跟", "跟", "反"], ["跟", "跟", "跟"], ["跟", "跟", "跟"], ["跟", "跟", "跟"]]

# 全局变量
current_bet = None  # 当前待判定的投注目标
current_stake_group = 0  # 当前使用的金额组索引（0-3）
current_stake_index = 0  # 当前组内的金额索引（0-2）
consecutive_wins = 0  # 连续赢的次数，用于组级回溯
bet_history = []  # 投注历史记录


def fetch_lottery_data():
    """从接口获取彩票数据"""
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


def wait_until_target_second(target_second):
    """等待到当前分钟的目标秒数"""
    while True:
        now = datetime.datetime.now()
        if now.second == target_second:
            return
        sleep_seconds = (target_second - now.second) % 60
        if sleep_seconds > 0:
            print(
                f"【等待执行】需等待 {sleep_seconds} 秒到{(now.minute % 60) + (1 if now.second > target_second else 0)}分{target_second}秒...")
            time.sleep(sleep_seconds)


def get_current_stake(bet_type):
    """根据投注类型获取当前投注金额"""
    global current_stake_group, current_stake_index

    # 确保索引在有效范围内
    group = shuang if bet_type == "双" else dan
    adjusted_group = min(current_stake_group, len(group) - 1)
    adjusted_index = min(current_stake_index, len(group[adjusted_group]) - 1)

    return group[adjusted_group][adjusted_index]


def update_stake_position(win):
    """根据输赢结果更新投注金额位置"""
    global current_stake_group, current_stake_index, consecutive_wins

    if win:
        # 赢了的情况
        consecutive_wins += 1

        # 组级回溯逻辑
        if current_stake_group > 0:
            # 从第4组赢了回到第3组
            if current_stake_group == 3:
                current_stake_group = 2
            # 从第3组赢了且连续赢3次回到第2组
            elif current_stake_group == 2 and consecutive_wins >= 3:
                current_stake_group = 1
                consecutive_wins = 0  # 重置连续赢计数
            # 从第2组赢了回到第1组
            elif current_stake_group == 1:
                current_stake_group = 0

            # 回到上一组后从第一个金额开始
            current_stake_index = 0
        else:
            # 从第1组赢了，保持组不变，回到组内第一个金额
            current_stake_index = 0
    else:
        # 输了的情况，重置连续赢计数
        consecutive_wins = 0

        # 组内索引增加，如果超过当前组长度则切换到下一组
        current_stake_index += 1
        current_group = shuang if current_bet == "双" else dan

        if current_stake_index >= len(current_group[current_stake_group]):
            current_stake_index = 0
            # 组索引增加，不超过最大组索引
            if current_stake_group < len(current_group) - 1:
                current_stake_group += 1


def execute_betting_logic(latest_result):
    """执行跟随投注逻辑（包含投注金额管理）"""
    global current_bet, bet_history, current_stake_group, current_stake_index, consecutive_wins

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n" + "=" * 50)
    print(f"【投注逻辑】开始执行 - {current_time}")
    print(f"【当前状态】最新结果: {latest_result} | 待判定投注: {current_bet if current_bet else '无'}")
    print(
        f"【金额状态】当前组: {current_stake_group + 1} | 组内位置: {current_stake_index + 1} | 连续赢: {consecutive_wins}")

    # 1. 结果分类：判断是单值（如"单"）还是多值（如"单,单"）
    is_single_result = (latest_result in TARGET_SINGLE)  # 单值结果标记
    # 多值结果拆分（仅用于判定输赢）
    multi_result_list = [item.strip() for item in latest_result.split(",") if item.strip() in TARGET_SINGLE]

    print(
        f"【结果分类】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list if not is_single_result else '无'}")

    # 2. 判定输赢（关键：单值/多值都能判定，用对应逻辑）
    judge_triggered = False
    win = False
    stake_amount = 0

    if current_bet is not None:
        judge_triggered = True
        stake_amount = get_current_stake(current_bet)
        print(f"\n【判定环节】触发！上一次投注: {current_bet} | 投注金额: {stake_amount}")

        # 单值结果：直接对比
        if is_single_result:
            win = (latest_result == current_bet)
            judge_detail = f"单值对比（{current_bet} vs {latest_result}）"
        # 多值结果：看是否包含投注目标
        else:
            win = (current_bet in multi_result_list)
            judge_detail = f"多值包含检查（{current_bet} in {multi_result_list}）"

        # 强化判定提示
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

        # 更新投注金额位置
        update_stake_position(win)

        # 记录历史
        bet_history.append({
            "time": current_time,
            "bet_target": current_bet,
            "stake_amount": stake_amount,
            "actual_result": latest_result,
            "win": win
        })
        show_bet_statistics()
        current_bet = None  # 判定后清空待判定投注

    # 3. 未触发判定的场景
    elif current_bet is None:
        print(f"\n【判定环节】未触发！无待判定投注")

    # 4. 新投注环节（核心：仅单值结果才投注）
    if is_single_result:
        current_bet = latest_result
        next_stake = get_current_stake(current_bet)
        current_genfan = genfan[current_stake_group][current_stake_index]
        print(f"\n【投注环节】已投注新目标: {latest_result} | 投注金额: {next_stake} | 策略: {current_genfan}")
        print(f"【金额预告】当前组: {current_stake_group + 1} | 组内位置: {current_stake_index + 1}")
    else:
        print(f"\n【投注环节】结果 '{latest_result}' 是多值，不符合投注条件，不投注")

    print("=" * 50 + "\n")


def show_bet_statistics():
    """显示投注历史统计及盈亏情况"""
    if not bet_history:
        return

    total = len(bet_history)
    wins = sum(1 for record in bet_history if record["win"])
    losses = total - wins
    win_rate = (wins / total) * 100 if total > 0 else 0

    # 计算盈亏
    profit = sum(record["stake_amount"] for record in bet_history if record["win"])
    loss = sum(record["stake_amount"] for record in bet_history if not record["win"])
    net_profit = profit - loss

    print("【历史统计】" + "-" * 40)
    print(f"总投注次数: {total} | 赢局: {wins}次 🎉 | 输局: {losses}次 ❌")
    print(f"胜率: {win_rate:.2f}% | 总盈利: {profit} | 总亏损: {loss}")
    print(f"净盈亏: {net_profit} {'🎉' if net_profit > 0 else '❌' if net_profit < 0 else ''}")
    print("-" * 40)


if __name__ == "__main__":
    print("=" * 60)
    print("          彩票跟随投注监控脚本（带金额管理）")
    print("=" * 60)
    print(f"监控接口: {API_URL}")
    print(f"检查时间: 每分钟第{CHECK_SECOND}秒")
    print("核心规则:")
    print("1. 单值结果（单/双）→ 判定+投注 ；多值结果→只判定不投注")
    print("2. 赢则保持当前组，回到组内第一个金额；输则组内递进，超界则升级组")
    print("3. 从第N组赢则回到第N-1组；第3组赢需累计3次才回到第2组")
    print("判定提示: 赢局 🎉 | 输局 ❌")
    print("=" * 60 + "\n")

    try:
        while True:
            wait_until_target_second(CHECK_SECOND)
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"【主流程】[{current_time}] 开始检查数据...")

            latest_result = fetch_lottery_data()
            if not latest_result:
                print(f"【主流程】未获取到数据，跳过本次\n")
                time.sleep(1)
                continue

            execute_betting_logic(latest_result)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("脚本已手动停止")
        if bet_history:
            print("\n【最终统计】")
            show_bet_statistics()
        print("=" * 50)
    except Exception as e:
        print(f"\n【脚本异常】{str(e)}")
