import threading
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from fake_useragent import UserAgent
ua = UserAgent()
# 设置Chrome选项以启动无痕模式
elements = ['https://v.douyin.com/iUjAMYeg/', 'https://v.douyin.com/iUjAMYeg/']
import requests


def get_response(url):

    # 定义要访问的 URL
    url = url

    try:
        # 发送 GET 请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 获取响应内容
            content = response.text
            print("响应内容:")
            print(content)
            return content
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        # 捕获并打印请求异常
        print(f"请求异常: {e}")
count_bofang = 0
def meng(dizhi):
    print(dizhi)
    #dizhisss = "http://api2.xkdaili.com/tools/XApi.ashx?apikey=XKED4D736DFC49863081&qty=1&format=txt&split=0&sign=1d1eaa382ba32b934782fdcd894e0bf5&time=3"
    #ips = get_response(dizhisss)
    dizhi =  random.choice(elements)

    options = Options()
    #proxy = ips  # 合并IP和端口号，但通常不需要在代码中这样写，除非有特殊格式要求
    # 注意：如果代理需要身份验证，这种简单的设置方式可能不起作用
    #options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument('--incognito')
    #options.add_argument("--headless")
    options.add_argument('--disable-extensions')
    #options.add_argument(f'--user-agent={ua.random}')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 启动Chrome浏览器
    while (True):
        
        countbb = 0
        driver = webdriver.Chrome(options=options)
        monidizhi = dizhi
        driver.get(random.choice(elements))  # 替换为你要打开的网页链接

        while (countbb < 2):
            flag = True
            while (True):
                window_handles1 = driver.window_handles
                if (len(window_handles1) < 12):
                    count = 0
                    #driver.execute_script("window.open('https://v.douyin.com/iUjAMYeg/');")
                    driver.execute_script("window.open('" + random.choice(elements) + "');")
                    global count_bofang
                    print("count_bofang=",count_bofang)
                    count_bofang += 1

                    if(count_bofang > 800):
                        return

                    window_handles1 = driver.window_handles
                    # 切换到新窗口
                    driver.switch_to.window(window_handles1[-1])
                    time.sleep(3)
                window_handles1 = driver.window_handles
                if (len(window_handles1) > 10):
                    while (flag):
                        window_handles1 = driver.window_handles
                        if (len(window_handles1) < 3):
                            flag = False
                            break
                        print("可以关闭窗口了")
                        driver.switch_to.window(window_handles1[1])
                        driver.close()
                        time.sleep(3)
                        driver.switch_to.window(window_handles1[-1])
                if (flag == False):
                    break
            print("-----------------最小循环结束------------------------")
            countbb += 1
        print("---------------------第二循环结束-----------------------")
        print("关闭")
        time.sleep(15)
        driver.quit()




# 创建一个线程列表
threads = []

# 为集合中的每个元素创建一个线程
for element in elements:
    thread = threading.Thread(target=meng, args=(element,))
    threads.append(thread)
    # 启动线程
    thread.start()
    time.sleep(5)

# 等待所有线程完成
for thread in threads:
    thread.join()

# 执行其他操作...
# 最后关闭浏览器
#driver.quit()