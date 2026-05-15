def calculate_result(input_num):
    """
    根据规律计算输出结果
    :param input_num: 输入的整数（如11010、11100）
    :return: 输出的整数（如7101、7110）
    """
    # 步骤1：将输入转为字符串，便于字符操作
    input_str = str(input_num)
    # 步骤2：替换首位的1为7
    replaced_str = "7" + input_str[1:]
    # 步骤3：移除末尾的最后一个0
    result_str = replaced_str[:-1]  # 切片去掉最后一个字符
    # 步骤4：转为整数返回
    return int(result_str)

# 测试所有实例
test_cases = [11010, 11020, 11030, 11040, 11050, 11060, 11070, 11080, 11090, 11100, 11110, 11120, 11130, 11140, 11150]
for case in test_cases:
    print(f"{ca se}-----{calculate_result(case)}")