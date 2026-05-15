import json
def getData(count,pos):
    import requests
    result = []
    # 接口的URL
    url = 'https://1689628.com/api/pks/getPksHistoryList.do?lotCode=10037'
    # header = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    #     "Accept-Encoding": "gzip, deflate, br, zstd",
    #     "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    #     "Connection": "keep-alive",
    #     "Cookie": "_skin_=blue; defaultSetting=5%2C10%2C20%2C50%2C100%2C200%2C500%2C1000; settingChecked=0; defaultLT=PK10JSC; 08062a46822a=149175e0b19d82c7d7819a8694acfdf58e62c854; _ga=GA1.2.243689521.1723263246; _gid=GA1.2.884956751.1723263246; _ga_MX33GN91MD=GS1.2.1723367198.8.0.1723367198.0.0.0; ssid1=2093db00014e9ff719b75e7a7835a889; random=838; token=149175e0b19d82c7d7819a8694acfdf58e62c854",
    #     "Host": "www.ip5276.com",
    #     "Priority": "u=0, i",
    #     "Sec-Fetch-Dest": "document",
    #     "Sec-Fetch-Mode": "navigate",
    #     "Sec-Fetch-Site": "none",
    #     "Sec-Fetch-User": "?1",
    #     "TE": "trailers:Upgrade-Insecure-Requests:1",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
    #     # 添加更多的请求头信息...
    # }
    #
    # 发送GET请求
    response = requests.get(url)
    result111 = []
    # 检查请求是否成功
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        small_count = 0
        while(small_count < count):
            print(json.loads(data)["result"]["data"][small_count])
            print(json.loads(data)["result"]["data"][small_count]["preDrawIssue"])
            print(json.loads(data)["result"]["data"][small_count]["preDrawCode"])
            print(json.loads(data)["result"]["data"][small_count]["preDrawCode"].split(",")[pos-1])
            result111.append(int(json.loads(data)["result"]["data"][small_count]["preDrawCode"].split(",")[pos-1]))
            small_count += 1
    return result111
print(getData(3,3))