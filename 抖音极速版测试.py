import time

import uiautomator2 as u2

d = u2.connect("384da6")

d(textContains="确认聊天").click()
time.sleep(2)
d(textContains="发送消息").set_text("你好")

d(descriptionContains="发送").click()

