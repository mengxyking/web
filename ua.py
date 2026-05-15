from fake_useragent import UserAgent
import re

# 创建一个UserAgent对象
ua = UserAgent()

# 定义一个函数来检查User-Agent是否为桌面端
def is_desktop_ua(user_agent_string):
    # 这里使用正则表达式来检查User-Agent字符串中是否包含常见的移动端标识
    mobile_keywords = ['Mobile', 'Android', 'iPhone', 'iPad', 'iPod', 'Windows Phone']
    for keyword in mobile_keywords:
        if keyword in user_agent_string:
            return False
    return True

# 获取User-Agent字符串，并循环直到得到一个桌面端的User-Agent
while True:
    user_agent_string = ua.random
    if is_desktop_ua(user_agent_string):
        break

# 打印桌面端的User-Agent字符串
print("fudai_path-",user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)
print(user_agent_string)