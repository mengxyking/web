from functools import wraps

import uiautomator2 as u2
import time
import random
import socket
from functools import wraps

import os
def timeout(seconds):
    """超时装饰器，限制函数执行时间"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 保存原始超时设置
            original_timeout = socket.getdefaulttimeout()
            try:
                # 设置超时时间
                socket.setdefaulttimeout(seconds)
                # 执行被装饰的函数
                return func(*args, **kwargs)
            finally:
                # 恢复原始超时设置
                socket.setdefaulttimeout(original_timeout)
        return wrapper
    return decorator


# 清除无效的 PYTHONUTF8 变量
@timeout(10)  # 设置30秒连接超时
def get_device(serial):
    """
    连接指定设备并返回设备对象
    :param serial: 设备序列号
    :return: uiautomator2设备对象
    :raises: ADBError 当连接失败或超时
    """
    try:
        # 尝试连接设备
        d = u2.connect(serial)
        # 验证连接是否有效（获取设备信息）
        print(d.info)
        # 移除所有监听器
        d.watcher.remove()
        return d
    except BaseException as e:
        # 捕获ADB错误和超时错误
        print(f"设备 {serial} 连接超时或失败: {str(e)}")
        #get_device(serial)

d = get_device("ALTMVB3B17005679")

d.swipe(500, 500, 500, 1500, 0.1)

print(d.app_current())
#d(descriptionContains='分享').click()

#
# print(d.app_current())
#
#
# if (d(text='抖音').exists(timeout=3)):
#     print("有 抖音")
#     mengs = d(text='抖音')
#     print("mengs ===", len(mengs))
#     if (d(textContains='使用主应用打开').exists(timeout=3)):
#         print("d(textContains='使用主应用打开')",d(textContains='使用主应用打开').info)
#     for meng in mengs:
#         print(meng.info)
#
#
#     d(text='抖音').click()
#     time.sleep(3)
# else:
#     print("当前没有添加评论a 。。。。。。。。")
#
#
# if (d(descriptionContains='抖音').exists(timeout=3)):
#     print("有 抖音descriptionContains")
#     mengs = d(descriptionContains='抖音')
#     print("mengs ===", len(mengs))
#     for meng in mengs:
#         print(meng.info)
# else:
#     print("当前没有添加评论a 。。。。。。。。")
#
# if (d(description='抖音').exists(timeout=3)):
#     print("有 抖音sdescription")
#     mengs = d(description='抖音')
#     print("mengs ===", len(mengs))
#     for meng in mengs:
#         print(meng.info)
# else:
#     print("当前没有添加评论a 。。。。。。。。")
#
# if (d(textContains='抖音').exists(timeout=3)):
#     print("有 抖音textContains")
#     mengs = d(textContains='抖音')
#     print("mengs ===", len(mengs))
#     for meng in mengs:
#         print(meng.info)
# else:
#     print("当前没有添加评论a 。。。。。。。。")
#
#
#
# #fudai(d)