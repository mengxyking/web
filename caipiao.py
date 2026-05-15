import requests
import time
import datetime
import json

# 配置参数
API_URL = "https://api.trpsp.com/api/lottery_logs/ds/one/chart?limit=150&page=1"
TARGET_SINGLE = ["单", "双"]  # 仅单个"单/双"为有效投注条件
CHECK_SECOND = 3  # 每分钟检查的秒数

# 投注金额配置（4个组，每组3个金额）
shuang = [[10, 20, 40], [24, 52, 110], [90, 186, 384], [324, 666, 1342]]  # 双的金额组
dan = [[11, 21, 41], [25, 53, 111], [91, 187, 385], [325, 667, 1343]]    # 单的金额组
genfan = [["跟", "反", "跟"], ["跟", "跟", "跟"], ["跟", "跟", "跟"], ["跟", "跟", "跟"]]  # 每组的跟反策略

# 全局变量
current_bet = None  # 当前待判定的投注目标
current_stake_group = 0  # 当前使用的金额组索引（0-3，对应第1-4组）
current_stake_index = 0  # 当前组内的金额索引（0-2，对应第1-3个金额）
consecutive_wins_in_group = 0  # 当前组内的连续赢次数（用于累计3次回溯）
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
            next_minute = (now.minute % 60) + (1 if now.second > target_second else 0)
            print(f"【等待执行】需等待 {sleep_seconds} 秒到{next_minute}分{target_second}秒...")
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
    """根据输赢结果更新投注金额位置（核心修改：所有组累计3次赢均回到第1组）"""
    global current_stake_group, current_stake_index, consecutive_wins_in_group

    if win:
        # 赢了的情况：更新当前组内连续赢次数
        consecutive_wins_in_group += 1
        print(f"【金额更新】当前组{current_stake_group+1}内连续赢: {consecutive_wins_in_group}/3次")

        # 第1组特殊：赢了保持组不变，重置组内索引和连续赢次数
        if current_stake_group == 0:
            current_stake_index = 0
            consecutive_wins_in_group = 0
        else:
            # 第2/3/4组：累计赢3次 → 回到第1组，重置所有计数
            if consecutive_wins_in_group >= 3:
                current_stake_group = 0  # 回到第1组
                current_stake_index = 0   # 从第1组第1个金额开始
                consecutive_wins_in_group = 0  # 重置组内连续赢次数
                print(f"【金额回溯】当前组{current_stake_group+1}累计赢3次 → 回到第1组第1个金额")
            else:
                # 未累计3次赢：保持当前组，回到组内第1个金额
                current_stake_index = 0
                print(f"【金额更新】未累计3次赢 → 留在第{current_stake_group+1}组第1个金额")
    else:
        # 输了的情况：重置组内连续赢次数，组内金额递进，超界则升级组
        consecutive_wins_in_group = 0
        current_stake_index += 1
        current_group = shuang if current_bet == "双" else dan

        # 组内索引超界 → 升级到下一组，从第1个金额开始
        if current_stake_index >= len(current_group[current_stake_group]):
            current_stake_index = 0
            if current_stake_group < len(current_group) - 1:
                current_stake_group += 1
                print(f"【金额升级】当前组{current_stake_group}输光 → 升级到第{current_stake_group+1}组第1个金额")
            else:
                print(f"【金额状态】已达最高第{current_stake_group+1}组 → 留在本组第1个金额")


def calculate_bet_target(latest_single_result):
    """根据“跟/反”策略计算当前投注目标"""
    global current_stake_group, current_stake_index

    # 获取当前金额组对应的跟反策略
    current_strategy = genfan[current_stake_group][current_stake_index]
    print(f"【策略计算】当前策略: {current_strategy} | 上一轮单值结果: {latest_single_result}")

    # 策略逻辑：跟=同结果，反=反结果
    if current_strategy == "跟":
        return latest_single_result
    elif current_strategy == "反":
        return "双" if latest_single_result == "单" else "单"
    else:
        print(f"【策略异常】未知策略{current_strategy} → 默认用“跟”策略")
        return latest_single_result


def execute_betting_logic(latest_result):
    """执行跟随投注逻辑（包含跟反策略和金额管理）"""
    global current_bet, bet_history, current_stake_group, current_stake_index, consecutive_wins_in_group

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n" + "=" * 50)
    print(f"【投注逻辑】开始执行 - {current_time}")
    print(f"【当前状态】最新结果: {latest_result} | 待判定投注: {current_bet if current_bet else '无'}")
    print(f"【金额状态】当前组: {current_stake_group + 1} | 组内位置: {current_stake_index + 1} | 组内连续赢: {consecutive_wins_in_group}")

    # 1. 结果分类：单值（如"单"）/多值（如"单,双"）
    is_single_result = (latest_result in TARGET_SINGLE)
    multi_result_list = [item.strip() for item in latest_result.split(",") if item.strip() in TARGET_SINGLE]
    print(f"【结果分类】单值结果: {is_single_result} | 多值拆分列表: {multi_result_list if not is_single_result else '无'}")

    # 2. 判定输赢（单值/多值通用逻辑）
    judge_triggered = False
    win = False
    stake_amount = 0

    if current_bet is not None:
        judge_triggered = True
        stake_amount = get_current_stake(current_bet)
        print(f"\n【判定环节】触发！上一次投注: {current_bet} | 投注金额: {stake_amount}")

        # 单值结果：直接对比；多值结果：检查是否包含
        if is_single_result:
            win = (latest_result == current_bet)
            judge_detail = f"单值对比（{current_bet} vs {latest_result}）"
        else:
            win = (current_bet in multi_result_list)
            judge_detail = f"多值包含检查（{current_bet} in {multi_result_list}）"

        # 输赢提示
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

        # 更新金额位置（按新回溯规则）
        update_stake_position(win)

        # 记录历史
        bet_history.append({
            "time": current_time,
            "bet_target": current_bet,
            "stake_amount": stake_amount,
            "actual_result": latest_result,
            "win": win,
            "current_group": current_stake_group + 1
        })
        show_bet_statistics()
        current_bet = None  # 判定后清空待判定投注

    # 3. 新投注环节（仅单值结果可投注，且按跟反策略计算目标）
    if is_single_result:
        # 按当前策略计算投注目标
        current_bet = calculate_bet_target(latest_result)
        next_stake = get_current_stake(current_bet)
        current_strategy = genfan[current_stake_group][current_stake_index]
        print(f"\n【投注环节】触发投注！")
        print(f"  上一轮结果: {latest_result} | 当前策略: {current_strategy}")
        print(f"  投注目标: {current_bet} | 投注金额: {next_stake}")
        print(f"  金额状态: 第{current_stake_group + 1}组第{current_stake_index + 1}个金额")
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
    print(f"当前所在组: 第{current_stake_group + 1}组")
    print("-" * 40)


if __name__ == "__main__":
    print("=" * 60)
    print("          彩票跟随投注监控脚本（带跟反策略+金额管理）")
    print("=" * 60)
    print(f"监控接口: {API_URL}")
    print(f"检查时间: 每分钟第{CHECK_SECOND}秒")
    print("核心规则:")
    print("1. 单值结果（单/双）→ 按跟反策略投注；多值结果→只判定不投注")
    print("2. 输赢规则：赢→当前组内累计赢次数，满3次回到第1组；输→组内递进，超界升级组")
    print("3. 跟反策略：跟=投上一轮结果，反=投上一轮相反结果")
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
