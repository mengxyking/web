import time
from selenium import webdriver
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

def run_browser(url, browser_type):
    print(f"{browser_type} browser opened and navigated to {url}")
    if browser_type == 'chrome':
        driver = webdriver.Chrome()
    elif browser_type == 'firefox':
        options = Options()
        # options.add_argument('-headless')
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        gecko_driver_path = r"D:\pycharm\Project\wb\dist\tz_9\geckodriver.exe"
        options._binary_location = r"D:\pycharm\Project\wb\dist\tz_9\geckodriver.exe"
        # 固定搭配直接用就行了
        service = Service(executable_path=gecko_driver_path)
        driver = webdriver.Firefox(options=options, service=service)
    else:
        raise ValueError("Unsupported browser type")
    print(f"{browser_type} browser opened and navigated to {url}")
    driver.get(url)
    time.sleep(10)
    driver.find_element(By.XPATH,'//*[@id="search-kw"]').send_keys("mengmengmeng")
    time.sleep(10)
    # 这里可以添加更多的操作
    driver.quit()


# 定义要打开的URL和浏览器类型
urls = ['https://hao.360.com', 'https://hao.360.com']
browser_types = ['chrome', 'firefox']

# 创建并启动线程
threads = []
for url, browser_type in zip(urls, browser_types):
    thread = threading.Thread(target=run_browser, args=(url, browser_type))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()