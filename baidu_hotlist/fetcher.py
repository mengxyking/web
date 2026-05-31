import urllib.request
import urllib.parse
import json
import time

from config import API_URL, HEADERS, REQUEST_DELAY


def _request(tab: str, city: str = "", platform: str = "wise") -> dict:
    params: dict = {"platform": platform, "tab": tab}
    if city:
        params["city"] = city
    url = API_URL + "?" + urllib.parse.urlencode(params, encoding="utf-8")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("success"):
        err = data.get("error", {}).get("message", "未知错误")
        raise RuntimeError(err)
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


def fetch_board(tab: str, board_name: str, top_n: int = 30) -> list:
    """抓取单个榜单，返回标准化条目列表。失败时返回空列表并打印错误。"""
    try:
        data  = _request(tab)
        items = _parse_items(data)
        result = []
        rank   = 0
        for item in items:
            if item.get("isTop"):
                result.append({
                    "board":    board_name,
                    "city":     "",
                    "rank":     0,
                    "word":     item.get("word", ""),
                    "hot_tag":  item.get("newHotName", ""),
                    "label":    item.get("labelTagName", ""),
                    "url":      item.get("url", ""),
                })
            else:
                rank += 1
                result.append({
                    "board":    board_name,
                    "city":     "",
                    "rank":     item.get("index", rank),
                    "word":     item.get("word", ""),
                    "hot_tag":  item.get("newHotName", ""),
                    "label":    item.get("labelTagName", ""),
                    "url":      item.get("url", ""),
                })
            if len(result) >= top_n:
                break
        return result
    except Exception as e:
        print(f"  [ERROR] {board_name}({tab}) 获取失败: {e}")
        return []


def fetch_all_boards(boards: dict, top_n: int = 30) -> dict:
    """批量抓取多个榜单。boards = {tab: board_name}"""
    result = {}
    total  = len(boards)
    for idx, (tab, name) in enumerate(boards.items(), 1):
        print(f"  [{idx}/{total}] 正在抓取 {name}...")
        result[name] = fetch_board(tab, name, top_n)
        if idx < total:
            time.sleep(REQUEST_DELAY)
    return result


def fetch_city(city: str, top_n: int = 30) -> list:
    """抓取城市热榜（需中国大陆IP）。失败时返回空列表。"""
    try:
        data  = _request(tab="city", city=city, platform="pc")
        items = _parse_items(data)
        result = []
        rank   = 0
        for item in items:
            if item.get("isTop"):
                result.append({
                    "board":    "城市榜",
                    "city":     city,
                    "rank":     0,
                    "word":     item.get("word", ""),
                    "hot_tag":  item.get("newHotName", ""),
                    "label":    item.get("labelTagName", ""),
                    "url":      item.get("url", ""),
                })
            else:
                rank += 1
                result.append({
                    "board":    "城市榜",
                    "city":     city,
                    "rank":     item.get("index", rank),
                    "word":     item.get("word", ""),
                    "hot_tag":  item.get("newHotName", ""),
                    "label":    item.get("labelTagName", ""),
                    "url":      item.get("url", ""),
                })
            if len(result) >= top_n:
                break
        return result
    except Exception as e:
        print(f"  [ERROR] {city}城市榜 获取失败（需中国大陆IP）: {e}")
        return []


def fetch_all_cities(cities: list, top_n: int = 30) -> dict:
    """批量抓取所有城市热榜"""
    result = {}
    total  = len(cities)
    for idx, city in enumerate(cities, 1):
        print(f"  [{idx}/{total}] 正在抓取 {city} 城市榜...")
        result[city] = fetch_city(city, top_n)
        if idx < total:
            time.sleep(REQUEST_DELAY)
    return result
