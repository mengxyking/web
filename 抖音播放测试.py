from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import pyautogui
pyautogui.FAILSAFE=False
import subprocess
def inter(monidizhi):
    # subprocess.run(['taskkill', '/F', '/IM', 'Firefox.exe'])
    # time.sleep(4)
    options = Options()
    options.add_argument('--incognito')
    options.add_argument('--disable-extensions')
    # 启动Chrome浏览器
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome()

    monidizhi = "https://v.douyin.com/iUjAMYeg/"
    driver.get(monidizhi)  # 替换为你要打开的网页链接
    flag = True
    while(True):
        count = 0
        driver.execute_script("window.open('https://v.douyin.com/iUjAMYeg/');")
        window_handles1 = driver.window_handles
        # 切换到新窗口
        driver.switch_to.window(window_handles1[-1])
        while (count < 10):
            driver.refresh()
            time.sleep(3)
            count += 1
        window_handles1 = driver.window_handles
        if(len(window_handles1) > 3):
            print("可以关闭窗口了")
            driver.switch_to.window(window_handles1[1])
            driver.close()
            time.sleep(2)
            driver.switch_to.window(window_handles1[-1])


import threading
import time


def print_message(thread_name, delay):
    time.sleep(delay)
    print(f"线程 {thread_name} 正在运行...")
    inter("http://www.baidu.com")


# 创建并启动十个线程
for i in range(8):
    thread = threading.Thread(target=print_message, args=("线程" + str(i + 1), i))
    thread.start()



