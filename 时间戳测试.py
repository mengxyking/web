import time


def calculate_time_difference(initial_timestamp):
    # 获取当前时间戳（精确到秒）
    current_timestamp = int(time.time())

    # 计算时间差（秒）
    time_difference = current_timestamp - initial_timestamp

    # 除以140取整和取余
    print(time_difference)
    quotient = time_difference // 140
    quotient1 = time_difference // 140 % 6
    remainder = time_difference % 140

    return quotient,quotient1, remainder
init_time = 1740237875
def calculate_time_difference11():
    global global_time,global_zong
    # 获取当前时间戳（精确到秒）
    current_timestamp = int(time.time())

    # 计算时间差（秒）
    time_difference = current_timestamp - init_time
    print(time_difference)

    # 除以140取整和取余
    #quotient = time_difference // 140
    quotient1 = time_difference // int(140) % int(6)
    #remainder = time_difference % 140
    print(quotient1)
    return quotient1
# 示例使用
if __name__ == "__main__":
    # print(int(time.time()))
    # # 假设这是初始时间戳（可以用 time.time() 获取当前时间戳作为示例）
    # initial_timestamp = int(time.time()) - 1740238381  # 假设这是1000秒前的时间戳
    #
    # # 调用方法
    # quotient,quotient1, remainder = calculate_time_difference(initial_timestamp)
    #
    # #print(f"时间差（秒）: {current_timestamp - initial_timestamp}")
    # print(f"除以140取整: {quotient}")
    # print(f"除以140取整: {quotient1}")
    # print(f"除以140取余: {remainder}")
    calculate_time_difference11()