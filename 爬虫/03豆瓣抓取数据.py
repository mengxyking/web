import re
import requests
# lists = re.findall(r"\d+","aaaabbbbccc11111")
# print(lists)
#
#
# s = '<div class="西游记"><span id="10010">中国联通</span></div>'
# obj = re.compile(r'<span id="(\d+)">(.*?)</span>')
# print(obj.findall(s))
#
#
#
# s = '<div class="西游记"><span id="10010">中国联通</span></div>'
# obj = re.compile(r'<span id="(?P<id>\d+)">(?P<name>.*?)</span>')
# #print(obj.findall(s))
# result = obj.finditer(s)
#
# for temp in result:
#     print(temp.group("id"))
url = "https://movie.douban.com/top250"
header = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}
pageResourse = requests.get(url,headers=header).text
#print(pageResourse.text)

obj = re.compile('<div class="item">.*?<span class="title">(?P<filmName>.*?)</span>.*?',re.S)
filts = re.finditer(obj,pageResourse)
for temp in filts:
    print(temp.group("filmName"))