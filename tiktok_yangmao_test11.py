# import random
#
#
# def random_boolean_with_probability(probability):
#     """
#     根据给定的概率返回 True 或 False。
#
#     :param probability: 成功的概率（0 到 1 之间的浮点数）
#     :return: 如果随机数小于或等于概率则返回 True，否则返回 False
#     """
#     if not (1 <= probability <= 100):
#         raise ValueError("概率必须在 0 到 1 之间")
#
#     return random.random()*100 <= probability
#
#
# # 示例用法
# probability = 99  # 50% 的概率
# result = random_boolean_with_probability(probability)
# print(result)  # 输出可能是 True 或 False
import uiautomator2 as u2


d = u2.connect("384da6")
meng  = d(text="频道")
a,b,c,d = meng.bounds()
print(a,b,c,d)