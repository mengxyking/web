from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bit_api import *
from selenium.webdriver.chrome.service import Service

# /browser/open 接口会返回 selenium使用的http地址，以及webdriver的path，直接使用即可
res = openBrowser()
driverPath = res['data']['driver']
debuggerAddress = res['data']['http']

print(driverPath)
print(debuggerAddress)

# 创建一个自定义的 Service 对象
service = Service(executable_path=driverPath)

chrome_options = Options()
chrome_options.debugger_address = debuggerAddress

# slenium4之后版本不能在这里直接通过executable_path定义driverPath
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get('https://www.baidu.com/')