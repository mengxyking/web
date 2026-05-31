"""
百度热搜榜单抓取
tab 说明：
  realtime          → 热搜榜
  livelihood        → 民生榜
  finance           → 财经榜
  sports            → 体育榜
  new_entertainment → 文娱榜
  internation_news  → 国际榜
  challenge         → 挑战榜
  movie             → 电影榜
  teleplay          → 电视剧榜
  novel             → 小说榜
  drama             → 短剧榜
  city              → 城市榜（需中国大陆IP，使用城市中文名）
"""
import sys
import urllib.request
import urllib.parse
import json
import time

# 强制 UTF-8 输出，避免 Windows GBK 终端乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://top.baidu.com/api/board"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://top.baidu.com/board",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36"
    ),
}

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

# 城市榜使用城市中文名（非行政区划代码）
CITIES = [
    "北京", "上海", "广州", "深圳", "成都",
    "杭州", "武汉", "西安", "南京", "天津",
    "重庆", "苏州", "郑州", "长沙", "青岛",
    "厦门", "合肥", "济南", "哈尔滨", "昆明",
]


def fetch_board(tab: str, city: str = "", platform: str = "wise") -> dict:
    params: dict = {"platform": platform, "tab": tab}
    if city:
        params["city"] = city
    url = BASE_URL + "?" + urllib.parse.urlencode(params, encoding="utf-8")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("success"):
        err_msg = data.get("error", {}).get("message", "未知错误")
        raise RuntimeError(err_msg)
    return data


def _parse_items(data: dict) -> list:
    # 真实结构: cards[0].content[0].content → 实际条目列表
    for card in data.get("data", {}).get("cards", []):
        if card.get("component") == "tabTextList":
            for block in card.get("content", []):
                items = block.get("content", [])
                if items:
                    return items
    return []


def get_board(tab: str, top_n: int = 20) -> list:
    """获取指定榜单 top N"""
    data = fetch_board(tab)
    items = _parse_items(data)
    result = []
    rank = 0
    for item in items:
        if item.get("isTop"):
            result.append({
                "rank":      "置顶",
                "word":      item.get("word", ""),
                "hot_tag":   item.get("newHotName", ""),
                "label":     item.get("labelTagName", ""),
                "url":       item.get("url", ""),
            })
        else:
            rank += 1
            result.append({
                "rank":      item.get("index", rank),
                "word":      item.get("word", ""),
                "hot_tag":   item.get("newHotName", ""),
                "label":     item.get("labelTagName", ""),
                "url":       item.get("url", ""),
            })
        if len(result) >= top_n:
            break
    return result


def get_city_hot(city: str, top_n: int = 20) -> list:
    """城市热榜 top N（需要中国大陆IP）"""
    data = fetch_board(tab="city", city=city, platform="pc")
    items = _parse_items(data)
    result = []
    rank = 0
    for item in items:
        if not item.get("isTop"):
            rank += 1
        result.append({
            "rank":    item.get("index", rank) if not item.get("isTop") else "置顶",
            "city":    city,
            "word":    item.get("word", ""),
            "hot_tag": item.get("newHotName", ""),
            "label":   item.get("labelTagName", ""),
            "url":     item.get("url", ""),
        })
        if len(result) >= top_n:
            break
    return result


def print_board(tab: str, top_n: int = 10):
    board_name = BOARD_TABS.get(tab, tab)
    print(f"\n{'=' * 62}")
    print(f"  百度{board_name} TOP {top_n}  ({time.strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'=' * 62}")
    print(f"  {'排名':<4} {'热度':<4} {'标签':<5} {'话题'}")
    print(f"  {'-'*4} {'-'*4} {'-'*5} {'-'*40}")
    try:
        for item in get_board(tab, top_n):
            rank = str(item["rank"])
            tag  = item["hot_tag"] or ""
            lbl  = f"[{item['label']}]" if item["label"] else ""
            print(f"  {rank:<4} {tag:<4} {lbl:<5} {item['word']}")
    except Exception as e:
        print(f"  获取失败: {e}")


def print_city_board(city: str, top_n: int = 10):
    print(f"\n{'=' * 62}")
    print(f"  百度【{city}】城市热榜 TOP {top_n}")
    print(f"{'=' * 62}")
    print(f"  {'排名':<4} {'热度':<4} {'标签':<5} {'话题'}")
    print(f"  {'-'*4} {'-'*4} {'-'*5} {'-'*40}")
    try:
        for item in get_city_hot(city, top_n):
            rank = str(item["rank"])
            tag  = item["hot_tag"] or ""
            lbl  = f"[{item['label']}]" if item["label"] else ""
            print(f"  {rank:<4} {tag:<4} {lbl:<5} {item['word']}")
    except Exception as e:
        # 城市榜在非中国大陆IP下会返回500，属正常现象
        print(f"  获取失败（需中国大陆IP）: {e}")


def compare_cities(cities: list, top_n: int = 10):
    """对比多城市热榜"""
    for city in cities:
        print_city_board(city, top_n)
        time.sleep(0.5)


def main():
    # 1. 全国热搜榜
    print_board("realtime", 10)

    # 2. 其他垂类榜单
    # for tab in ["finance", "sports", "new_entertainment"]:
    #     print_board(tab, 5)
    #     time.sleep(0.3)

    # 3. 城市榜（需中国大陆IP）
    compare_cities(["天津", "上海", "广州", "深圳", "成都"], top_n=10)


if __name__ == "__main__":
    main()
