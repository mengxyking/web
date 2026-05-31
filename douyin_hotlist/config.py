CITIES = {
    "110000": "北京",
    "310000": "上海",
    # "440100": "广州",
    # "440300": "深圳",
    # "510100": "成都",
    # "330100": "杭州",
    # "500000": "重庆",
    # "420100": "武汉",
    # "320500": "苏州",
    # "610100": "西安",
    # "320100": "南京",
    # "430100": "长沙",
    # "410100": "郑州",
    # "120000": "天津",
    # "340100": "合肥",
    # "370200": "青岛",
    # "441900": "东莞",
    # "330200": "宁波",
    # "440600": "佛山",
}

API_URL = "https://so-landing.douyin.com/aweme/v1/hot/search/list/"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://so-landing.douyin.com/landings/hotlist",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36"
    ),
}

# 每次请求之间的间隔（秒）
REQUEST_DELAY = 0.5

# 默认抓取每个城市 Top N 条
DEFAULT_TOP_N = 30
