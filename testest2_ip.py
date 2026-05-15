import threading
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
# 设置Chrome选项以启动无痕模式
elements = ['https://v.douyin.com/iUraYPj3/', 'https://v.douyin.com/iUrYChbm/']
def meng(dizhi):
    print(dizhi)
    dizhi =  random.choice(elements)
    options = Options()
    options.add_argument('--incognito')
    #options.add_argument("--headless")
    options.add_argument('--disable-extensions')
    options.add_experimental_option("excludeSwitches", ['enable-automation'])

    # proxy = '14.116.219.46'
    # # 设置代理
    # options.add_argument('--proxy-server=http://14.116.219.46:16911')
    # # 注意options的参数用之前定义的chrome_options
    # driver = webdriver.Chrome(options=options)

    proxy = '49.71.161.148:40067'  # 合并IP和端口号，但通常不需要在代码中这样写，除非有特殊格式要求
    # 注意：如果代理需要身份验证，这种简单的设置方式可能不起作用
    options.add_argument(f'--proxy-server=http://{proxy}')
    driver = webdriver.Chrome(options=options)

    monidizhi = dizhi
    driver.get("https://v.douyin.com/iUraYPj3/")  # 替换为你要打开的网页链接
    time.sleep(30)





# 创建一个线程列表
# threads = []
#
# # 为集合中的每个元素创建一个线程
# for element in elements:
#     thread = threading.Thread(target=meng, args=(element,))
#     threads.append(thread)
#     # 启动线程
#     thread.start()
#     time.sleep(5)
#
# # 等待所有线程完成
# for thread in threads:
#     thread.join()
meng('https://v.douyin.com/iUraYPj3/')
# 执行其他操作...
# 最后关闭浏览器
#driver.quit()