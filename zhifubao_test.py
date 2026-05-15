import uiautomator2 as u2
import time
def backToHome(d):
    dd =  0
    d.app_start(package_name="com.alipay.mobile.socialwidget")
    time.sleep(3)
    while(dd < 10):
        elements = d(resourceId='com.alipay.mobile.socialwidget:id/social_tab_text')  # 获取所有文本为'some_text'的元素
        #print(len(elements))
        if(len(elements)>0):
            return "1"
        time.sleep(1.5)
        d.press("back")
        time.sleep(1.5)


def are_last_three_elements_equal(lst):
    # 检查列表长度是否至少为3
    if len(lst) < 3:
        return False

        # 获取列表的最后三个元素
    last_three_elements = lst[-3:]

    # 检查这三个元素是否相等
    return last_three_elements[0] == last_three_elements[1] == last_three_elements[2]


def is_close_to_any(num, B, tolerance=30):
    for b in B:
        if abs(num - b) <= tolerance:
            return True
    return False
def delete_frind_entry(d, serial,ee):
    print("")


    elements = d(text="\ue620",className='android.widget.TextView')
    if(len(elements)>0):
        elements.click()
        time.sleep(3)

    elements = d(resourceId='com.alipay.mobile.chatapp:id/user_icon')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    elements = d(text = "\ue620",className='android.widget.TextView')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)
        d.drag(500, 1200, 500, 500)
        time.sleep(2)
        d.drag(500, 1200, 500, 500)
        time.sleep(2)

    elements = d(resourceId='com.alipay.android.phone.wallet.profileapp:id/set_delete')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    elements = d(resourceId='com.alipay.mobile.antui:id/ensure')
    if (len(elements) > 0):
        elements.click()
        time.sleep(3)

    backToHome(d)
    time.sleep(3)
import os
def getPhotoPath():
    pan = os.getcwd().split(':')[0] + ":"
    pic_path = pan + '//yangmao/pic'  # 标志图片文件 新路径
    #print("00000000000000000000000000---------")
    #print(pic_path)
    if (os.path.exists(pic_path) == False):
        os.makedirs(pic_path)
    return pic_path
def photo():
    Ui_file_Name =  str(int(time.time())) + "_ui.png"
    path = getPhotoPath()+"/"+Ui_file_Name
    return path
import cv2

def get_color_at_position(image, x, y):
    b, g, r = image[y, x]
    return (r, g, b)

# 读取图片

d = u2.connect("Q5S0219527003267")
ee = d(text = "\ue620",className="android.widget.TextView")

if(ee):
    ee.click()
    time.sleep(2)

    ee = d(resourceId="com.alipay.mobile.chatapp:id/user_icon")
    if (ee):
        ee.click()
        time.sleep(2)

        ee = d(text = "\ue620",className="android.widget.TextView")
        if (ee):
            ee.click()
            time.sleep(2)
#

