from urllib.request import urlopen
import requests

url = "http://www.baidu.com"
res = urlopen(url)

#print(res.read().decode("utf-8"))

html_content = res.read().decode("utf-8")

with open(file="baidu.html",mode="w",encoding="utf-8") as f:
    f.write(html_content)


#requests
res_t = requests.get(url)
res_t.encoding = "utf-8"
print(res_t.text)