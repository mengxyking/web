import random

# Unicode范围：基本汉字块（CJK Unified Ideographs）从0x4E00到0x9FFF
# 注意：这个范围内并非所有代码点都是有效汉字
start = 0x4E00
end = 0x9FFF

# 生成一个随机汉字（以Unicode码点形式）
random_unicode_code_point = random.randint(start, end)

# 将Unicode码点转换为字符（注意：可能不是有效汉字）
# 使用chr函数将Unicode码点转换为字符
try:
    random_chinese_character = chr(random_unicode_code_point)
    print(random_chinese_character)
except ValueError:
    # 如果chr函数抛出ValueError（尽管在这个特定范围内不太可能），则打印错误消息
    # 实际上，在这个Unicode范围内，chr函数通常不会抛出ValueError，但为了代码的健壮性，还是加上异常处理
    print("Generated an invalid Unicode code point.")