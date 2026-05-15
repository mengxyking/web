import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bit_api import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class public_tk():
    def public_tk_m(self,win_key,video_path,video_info,shangpin_id,public_time):
        # /browser/open 接口会返回 selenium使用的http地址，以及webdriver的path，直接使用即可
        res = openBrowser(str(win_key).strip())  # 窗口ID从窗口配置界面中复制，或者api创建后返回
        shangpin_id = str(shangpin_id).strip()
        print(res)

        driverPath = res['data']['driver']
        debuggerAddress = res['data']['http']

        # selenium 连接代码
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debuggerAddress)

        chrome_service = Service(driverPath)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # 以下为PC模式下，打开baidu，输入 BitBrowser，点击搜索的案例
        driver.get('https://www.tiktok.com/tiktokstudio/upload?from=webapp')

        # time.sleep(7)
        # while (True):
        #     try:
        #         yue = driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div/div/div[3]/div[1]/div[5]/a/button/div/div[2]")
        #         print("判断是否是澳洲10")
        #         yue.click()
        #     except:
        #         print("还不在啊")
        #     time.sleep(5)

        time.sleep(7)

        # 直接向隐藏输入框发送文件路径（即使display:none也可操作）
        hidden_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='video/*']")
        hidden_input.send_keys(video_path)

        flag = 0
        while (True):
            try:
                yue = driver.find_element(By.CSS_SELECTOR,
                                          '#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-1810272162.container > div.jsx-1810272162.main > div:nth-child(2) > div.jsx-1601248207.caption-container.caption-markup-container > div.jsx-1601248207.caption-markup > div.jsx-1601248207.caption-editor > div > div > div > div > div > div > span > span')
                yue.send_keys(Keys.CONTROL + 'a')
                yue.send_keys(Keys.DELETE)
                time.sleep(3)
                break
            except:
                time.sleep(2)
                print("还不在啊00000000")
                flag+=1
                if(flag>10):
                    return
        flag = 0
        while (True):
            try:
                yue = driver.find_element(By.CSS_SELECTOR,
                                          '#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-1810272162.container > div.jsx-1810272162.main > div:nth-child(2) > div.jsx-1601248207.caption-container.caption-markup-container > div.jsx-1601248207.caption-markup > div.jsx-1601248207.caption-editor > div > div.DraftEditor-editorContainer > div > div > div > div > span')
                time.sleep(3)
                # 输入新内容
                yue.send_keys(video_info)
                break
            except:
                time.sleep(2)
                print("还不在啊11111")
                flag += 1
                if (flag > 10):
                    return

        if(shangpin_id != None and len(shangpin_id)>6):
            while (True):  # 点击商品
                try:
                    yue = driver.find_element(By.CSS_SELECTOR,
                                              '#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-1810272162.container > div.jsx-1810272162.main > div:nth-child(2) > div.jsx-3052464240.anchor-entry-container > div.jsx-1777402656.anchor-tag-container > button > div.Button__content.Button__content--shape-default.Button__content--size-medium.Button__content--type-neutral.Button__content--loading-false > span')
                    time.sleep(3)
                    # 输入新内容
                    yue.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")

            while (True):  # 点击下一个
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div/div/div[2]/div/div[2]/button[2]/div/div")
                    next_button.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")

            flag = 0
            while (True):  # 输入商品ID
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/input")
                    next_button.send_keys(shangpin_id)
                    time.sleep(6)
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 10):
                        return

            flag = 0
            while (True):  # 点击搜索按钮
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div[2]/div/div/div[2]/div/div[2]/div/div[2]/div/div")
                    next_button.click()
                    time.sleep(12)
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 10):
                        return

            # /html/body/div[6]/div[2]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/div/div[1]/div[1]/input

            flag = 0
            while (True):  # 点击选中按钮
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div[2]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/div/div[1]/div[1]/input")
                    next_button.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 5):
                        # return

                        flag1 = 0
                        try:  # 没有选中按钮的话 点击取消按钮
                            next_button = driver.find_element(By.XPATH,
                                                              "/html/body/div[6]/div[2]/div/div/div[3]/button[1]/div/div")
                            next_button.click()
                            break
                        except:
                            time.sleep(2)
                            print("还不在啊11111")
                            flag += 1
                            if (flag1 > 10):
                                return

            # /html/body/div[6]/div[2]/div/div/div[3]/button[2]/div/div

            flag = 0
            while (True):  # 点击下一步
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div[2]/div/div/div[3]/button[2]/div/div")
                    next_button.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 10):
                        return
            # /html/body/div[6]/div[2]/div/div/div[3]/button[2]/div/div
            flag = 0
            while (True):  # 点击添加
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div[2]/div/div/div[3]/button[2]/div/div")
                    next_button.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 10):
                        return
            # /html/body/div[6]/div/div/div[3]/button[2]/div[2]

            flag = 0
            while (True):  # 点击允许
                try:
                    next_button = driver.find_element(By.XPATH,
                                                      "/html/body/div[6]/div/div/div[3]/button[2]/div[2]")
                    next_button.click()
                    break
                except:
                    time.sleep(2)
                    print("还不在啊11111")
                    flag += 1
                    if (flag > 5):
                        break
            # /html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div[2]/span[2]

        flag = 0
        while (True):  # 检查是不是上传完成
            try:
                next_button = driver.find_element(By.XPATH,
                                                  "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div[2]/span[2]")
                next_button.click()
                time.sleep(5)
                break
            except:
                time.sleep(2)
                print("还不在啊11111")
                flag += 1
                if (flag > 10):
                    return


        flag = 0
        while (True):  # 点击发布
            try:
                next_button = driver.find_element(By.XPATH,
                                                  "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[4]/div/button[1]/div[2]")
                next_button.click()
                break
            except:
                time.sleep(2)
                print("还不在啊11111")
                flag += 1
                if (flag > 10):
                    return
        # flag = 0
        # while (True):  # 点击小时分钟
        #     try:
        #         next_button = driver.find_element(By.XPATH,
        #                                           "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[4]/div[1]/div[1]/div/div[3]/div[1]/div[1]/div/div/div/input")
        #         next_button.click()
        #         time.sleep(3)
        #         break
        #     except:
        #         time.sleep(2)
        #         print("还不在啊11111")
        #         flag += 1
        #         if (flag > 10):
        #             return


        # while (True):  # 这个点击具体的数据可以成功
        #     try:
        #         next_button = driver.find_element(By.XPATH,
        #                                           "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[4]/div[1]/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[10]/span")
        #         next_button.click()
        #         break
        #     except:
        #         time.sleep(2)
        #         print("还不在啊55555")
        #         flag += 1
        #         if (flag > 10):
        #             return


        return 1







