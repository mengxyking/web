# ─── 榜单 tab 映射 ───────────────────────────────────────────────────────────
BOARD_TABS = {
    "realtime":          "热搜榜",
    "livelihood":        "民生榜",
    "finance":           "财经榜",
    "sports":            "体育榜",
    "new_entertainment": "文娱榜",
    "internation_news":  "国际榜",
    "challenge":         "挑战榜",
    "movie":             "电影榜",
    "teleplay":          "电视剧榜",
    "novel":             "小说榜",
    "drama":             "短剧榜",
}

# 默认抓取的榜单（最常用的5个）
DEFAULT_BOARDS = ["realtime", "livelihood", "finance", "sports", "new_entertainment"]

# 城市榜使用城市中文名（非行政区划代码，需中国大陆IP）
CITIES = [
    "北京", "上海", "广州", "深圳", "成都",
    "杭州", "重庆", "武汉", "苏州", "西安",
    "南京", "长沙", "郑州", "天津", "合肥",
    "青岛", "东莞", "宁波", "佛山", "沈阳",
    "哈尔滨", "长春", "昆明", "福州", "厦门",
    "南昌", "济南", "石家庄", "太原", "贵阳",
]

API_URL = "https://top.baidu.com/api/board"

HEADERS = {
    "accept":          "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control":   "no-cache",
    "pragma":          "no-cache",
    "referer":         "https://top.baidu.com/board",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36"
    ),
}

# 请求间隔（秒）
REQUEST_DELAY = 0.5

# 默认每榜抓取条数
DEFAULT_TOP_N = 30
