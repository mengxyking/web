def getData(count,pos):
    import requests
    result = []
    # 接口的URL
    url = 'https://www.ip5276.com/member/dresult?lottery=PK10JSC'
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": "_skin_=blue; defaultSetting=5%2C10%2C20%2C50%2C100%2C200%2C500%2C1000; settingChecked=0; defaultLT=PK10JSC; 08062a46822a=149175e0b19d82c7d7819a8694acfdf58e62c854; _ga=GA1.2.243689521.1723263246; _gid=GA1.2.884956751.1723263246; _ga_MX33GN91MD=GS1.2.1723367198.8.0.1723367198.0.0.0; ssid1=2093db00014e9ff719b75e7a7835a889; random=838; token=149175e0b19d82c7d7819a8694acfdf58e62c854",
        "Host": "www.ip5276.com",
        "Priority": "u=0, i",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers:Upgrade-Insecure-Requests:1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
        # 添加更多的请求头信息...
    }

    # 发送GET请求
    response = requests.get(url, headers=header)

    # 检查请求是否成功
    if response.status_code == 200:
        # 获取返回的内容
        data = response.text
        # print(data)

        from bs4 import BeautifulSoup

        # 获取HTML页面源代码
        html = data
        # 使用BeautifulSoup解析HTML并提取特定数据
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        data = soup.find_all('td')
        # print(data[0])
        # print(data[2])
        # print(data[20])
        # print(data[22])
        count1 = 0

        while count1< count:
            # print(data[count1 * 20])
            # print(data[count1 * 20+2+pos-1])
            result.append(data[count1 * 20 + 2 + pos - 1].text)
            count1+=1

        # for temp in data:
        #     print(temp)
    else:
        print('请求失败，状态码：', response.status_code)
    return result

#print(getData(6,7))
def aaa():
    print("")
    print("")
    print("")
def judge_numbers(arr, criterion):
    if criterion == "odd":
        return all(num % 2 != 0 for num in arr)
    elif criterion == "even":
        return all(num % 2 == 0 for num in arr)
    elif criterion == "large":
        return all(num > 5 for num in arr)
    elif criterion == "small":
        return all(num <= 5 for num in arr)
    else:
        return False

# # 测试
# print(judge_numbers([1, 2, 5], "odd"))  # 输出: True
# print(judge_numbers([2, 4, 6], "even"))  # 输出: True
# print(judge_numbers([6, 7, 8], "large"))  # 输出: True
# print(judge_numbers([1, 2, 3], "small"))  # 输出: True
import time
count = 0
while True:  # 创建无限循环
    time.sleep(1)
    print("当前count值为:", count)
    count += 1
    if count > 10:
        count = 0  # 当count大于10时，‌重新赋值为0
