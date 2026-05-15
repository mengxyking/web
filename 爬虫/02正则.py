import re

lists = re.findall(r"\d+","aaaabbbbccc11111")
print(lists)


s = '<div class="西游记"><span id="10010">中国联通</span></div>'
obj = re.compile(r'<span id="(\d+)">(.*?)</span>')
print(obj.findall(s))



s = '<div class="西游记"><span id="10010">中国联通</span></div>'
obj = re.compile(r'<span id="(?P<id>\d+)">(?P<name>.*?)</span>')
#print(obj.findall(s))
result = obj.finditer(s)

for temp in result:
    print(temp.group("id"))