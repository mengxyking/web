import time
from datetime import datetime

import uiautomator2 as u2
import re
from lxml import etree


current_datetime = datetime.now()

# 格式1：年-月-日（最常用，如：2026-01-03）
format1 = current_datetime.strftime("%Y.%m.%d")
print(format1)

d = u2.connect("4EV0222B17004876")
print(d.app_current())
print(str(d.app_current()["activity"]).count("LivePlayActivity"))




# print("开始1")
# d.swipe(500,1200,500,500,0.3)
# time.sleep(10)
#
# print("开始2")
# d.swipe(500,1200,500,500,1)
# time.sleep(10)
#
# print("开始3")
# d.swipe(500,1200,500,500,5)
# time.sleep(10)
#
# print("开始4")
# d.swipe(500,1200,500,500,10)
# time.sleep(10)
#
#
# print("开始5")
# d.swipe(100,1500,100,500,10)
# time.sleep(10)
#
# print(d.dump_hierarchy())
# #
# # if (d(description='说点什么...').exists(timeout=1)):
# #     print("you")
# # target_point = (105, 413)
# # def find_id_from_area(d,x1,y1):
# #     xml = d.dump_hierarchy()
# #
# #     tree = etree.fromstring(xml.encode('utf-8'))
# #
# #     # 目标坐标范围：判断控件是否包含该坐标
# #     target_point = (x1, y1)  # 你需要检查的点
# #
# #     # 存储符合条件的控件信息 (面积, 控件, 中心坐标)
# #     candidates = []
# #
# #     elements = tree.xpath('//node')
# #     for elem in elements:
# #         bounds_str = elem.get('bounds', '')
# #         resource_id = elem.get('resource-id', '')
# #         if not bounds_str:
# #             continue
# #
# #         # 解析bounds坐标 [x1,y1][x2,y2]
# #         coords = re.findall(r'\[(\d+),(\d+)]\[(\d+),(\d+)]', bounds_str)
# #         if not coords:
# #             continue
# #
# #         x1, y1, x2, y2 = map(int, coords[0])
# #
# #         # 过滤条件：
# #         # 1. 控件包含目标点
# #         # 2. 排除全屏或无效控件（x1,y1不为0，避免最外层大容器）
# #         if (x1 <= target_point[0] <= x2
# #                 and y1 <= target_point[1] <= y2
# #                 and x1 != 0
# #                 and y1 != 0
# #                 and resource_id != ""):
# #             # 计算控件面积 (宽×高)
# #             width = x2 - x1
# #             height = y2 - y1
# #             area = width * height
# #
# #             # 计算中心坐标（用于点击）
# #             center_x = (x1 + x2) // 2
# #             center_y = (y1 + y2) // 2
# #
# #             # 存入候选列表
# #             candidates.append((area, elem, center_x, center_y))
# #
# #     if candidates:
# #         # 按面积升序排序，取第一个（面积最小）
# #         candidates.sort(key=lambda x: x[0])
# #         min_area, min_elem, min_center_x, min_center_y = candidates[0]
# #
# #         # 执行点击
# #         #d.click(min_center_x, min_center_y)
# #         print(f"找到面积最小的控件（面积：{min_area}），已点击")
# #         print(f"控件信息：resource-id={min_elem.get('resource-id', '')}，bounds={min_elem.get('bounds')}")
# #         return min_elem.get('resource-id', '')
# #     else:
# #         print("未找到符合条件的控件")
#
# #d.click(100,1500)
# #print(d.dump_hierarchy())
# #
# # if (d(text='一键发表评论').exists(timeout=3)):  # com.ss.android.ugc.aweme:id/yxl
# #     print("，按钮")
# #     d(text='一键发表评论').click()
# #     time.sleep(2)
# # else:
# #     print("当前没有善缘按钮")
#
# if (d(className='android.widget.HorizontalScrollView').exists(timeout=3)):#com.ss.android.ugc.aweme:id/yxl
#     print("，按钮")
#     view_temp = None
#     bb = d(className='android.widget.HorizontalScrollView')
#     print(len(bb))
#     if(len(bb)>0):
#         for t in bb:
#             print("t=",t.info)
#             fudai_length = t.info["bounds"]["right"] - t.info["bounds"]["left"]
#             print(fudai_length)
#             if((fudai_length<150) and (t.info["bounds"]["right"]<500) and (t.info["bounds"]["bottom"]<800)):
#                 view_temp = t
#                 break
#
#     if(view_temp != None):
#         view_temp.click()
#
#     # print(len(d(className='android.widget.HorizontalScrollView')))
#     # d(className='android.widget.HorizontalScrollView').click()
#     # time.sleep(2)
#     # pingluns = d(textContains='评论')
#     # pingluns[-1].set_text(random.choice(comments))   className="android.widget.EditText"
#     time.sleep(1)
# else:
#     print("当前没有善缘按钮")

#d.long_click(100, 1500, 1.5)
# huifus = d(descriptionContains="回复 按钮")
# print(huifus.child()[0].child()[4].get_text())
# #print(huifus.child(text="回复"))
# for huifu in huifus:
#     # print("-------------------------")
#     #print(huifu.child())
#     i = 0
#     print(huifu.child()[0].child()[4].get_text())
#
#
# # def get_specific_children(parent, target_id=None, target_text=None):
#
# #     conditions = {}
# #     if target_id:
# #         conditions["resourceId"] = target_id
# #     if target_text:
# #         conditions["text"] = target_text
# #
# #     if not conditions:
# #         raise ValueError("至少需要指定target_id或target_text中的一个")
# #
# #     # 获取所有符合条件的后代控件（包含子控件、孙控件等）
# #     # 如果只想获取直接子控件，可改用 parent.child(**conditions)
# #     matched_children = parent.descendants(**conditions)
# #
# #     return matched_children
# #
# # if (d(descriptionContains="回复 按钮").exists(timeout=3)):
# #     print("回复 按钮")
#
# # huifus = d(text="具体地址").right().child().child().get_text()
# # print(huifus)
# #d.swipe_ext("up", scale=0.9)
# # w,h = d.window_size()
# # d.swipe(300, h-500, 300, 200, 0.2) # swipe for 0.5s (default)
#
# # d.press("recent")
# # meng = huifus.parent
# # if(meng):
# #     print(meng)
# # for huifu in huifus:
# #     print("-------------------------------------------------------------------------------")
# #     print(len(huifu.child()))
# #     print(huifu.info)
# #     for child_t in huifu.child():
# #         print(child_t.info["text"])
# #         if(child_t.info["text"] == "回复"):
# #             child_t.click()
# #             time.sleep(2)
# #             d.press("back")
# #             time.sleep(2)
# #             d.press("back")
# #             time.sleep(2)
# #             break
# #
#         # print(child_t.info["contentDescription"])
#         # print(child_t.info["text"])
