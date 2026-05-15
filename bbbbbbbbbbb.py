import pyautogui
import time
 # 等待5秒钟，以便您有时间切换到需要模拟回车键的窗口
import uiautomator2 as u2

import lxml.etree as etree
def check_pop(d,  element_len=20):
    """
    检查当前界面元素数量，与指定长度比较，决定是否重建设备连接
    :param d: 现有uiautomator2设备对象
    :param element_len: 参考元素数量阈值
    :param device: 设备标识（序列号或IP:端口）
    :return: 处理后的uiautomator2设备对象（可能是原对象或重建的对象）
    """
    try:
        # 获取当前界面XML结构
        xml = d.dump_hierarchy()
        # 解析XML并获取所有node元素（即UI控件）
        tree = etree.fromstring(xml.encode('utf-8'))
        elements = tree.xpath('//node')
        current_len = len(elements)
        print(f"当前界面元素数量: {current_len}, 阈值: {element_len}")

        # 比较元素数量
        if current_len > element_len:
            # 元素数量大于阈值，返回原设备对象
            print("元素数量符合要求，使用原设备连接")
            return True
        else:
            return False

    except Exception as e:
        print(e)


import xml.etree.ElementTree as ET
import re


def count_nodes_with_y_gt_200(d):
    """
    统计XML中y坐标大于200的节点数量
    :param xml_content: XML内容字符串
    :return: 符合条件的节点数量
    """
    # 编译正则表达式提取bounds中的坐标
    xml_content = d.dump_hierarchy()
    bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
    # 解析XML
    root = ET.fromstring(xml_content)
    # 初始化计数器
    count = 0

    # 遍历所有node节点
    for node in root.iter('node'):

        bounds = node.get('bounds')
        if not bounds:
            continue

        # 提取坐标（x1, y1, x2, y2）
        match = bounds_pattern.match(bounds)
        title_text = node.get("text")
        if match:
            y1 = int(match.group(2))  # 取左上角y坐标作为判断依据
            if y1 > 200 and title_text != "":
                print(node.get("text"))
                count += 1

    return count

#
# d = u2.connect("ALTMVB3B17005679")
# print(count_nodes_with_y_gt_200(d))
#check_pop(d)
#print(d.dump_hierarchy())


def get_app_page(app_biaoji, target_app):
    """
    根据APP名称（key）获取对应的页面名称（value）
    :param app_biaoji: 原始APP-页面列表（如你的app_biaoji）
    :param target_app: 要查询的APP名称（key）
    :return: 对应的页面名称（value）/ None（未找到）
    """
    for item in app_biaoji:
        # 遍历每个字典项，取唯一的key-value对
        app_name = next(iter(item.keys()))
        page_name = next(iter(item.values()))
        if app_name == target_app:
            return page_name
    return None


app_biaoji = [{"红果免费短剧": "首页"}, {"木叶免费短剧": "首页"}, {"番茄常用": "首页"}, {"红果免费漫剧": "首页"},
              {"番茄音乐": "首页"}, {"抖音火山版": "首页"}, {"悟空浏览器": "首页"}, {"西瓜视频": "首页"},
              {"汽水音乐": "发现"}, {"蛋花免费小说": "书城"}, {"常读免费小说": "书城"}, {"番茄免费小说": "书城"},
              {"今日头条": "阅读赚金币"}]

print(get_app_page(app_biaoji,"红果免费短剧"))