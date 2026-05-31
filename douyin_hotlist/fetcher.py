import urllib.request
import urllib.parse
import json
import time

from config import API_URL, HEADERS, REQUEST_DELAY


def _request(board_type: int, board_sub_type: str = "") -> dict:
    params = urllib.parse.urlencode({
        "aid": "581610",
        "detail_list": "1",
        "board_type": str(board_type),
        "board_sub_type": board_sub_type,
        "need_board_tab": "true",
        "need_covid_tab": "false",
        "version_code": "32.3.0",
    })
    req = urllib.request.Request(API_URL + "?" + params, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_city(city_code: str, city_name: str, top_n: int = 30) -> list[dict]:
    """
    抓取单个城市热榜，返回标准化的条目列表。
    失败时返回空列表并打印错误。
    """
    try:
        data = _request(board_type=1, board_sub_type=city_code)
        items = data.get("data", {}).get("word_list", [])
        result = []
        for item in items[:top_n]:
            result.append({
                "city_code": city_code,
                "city": city_name,
                "rank": item.get("position", 0),
                "word": item.get("word", ""),
                "hot_value": item.get("hot_value", 0),
                "view_count": item.get("view_count", 0),
                "video_count": item.get("video_count", 0),
                "sentence_id": item.get("sentence_id", ""),
            })
        return result
    except Exception as e:
        print(f"  [ERROR] {city_name}({city_code}) 获取失败: {e}")
        return []


def fetch_all_cities(cities: dict, top_n: int = 30) -> dict[str, list[dict]]:
    """
    批量抓取所有城市，返回 {city_name: [条目列表]}。
    """
    result = {}
    total = len(cities)
    for idx, (code, name) in enumerate(cities.items(), 1):
        print(f"  [{idx}/{total}] 正在抓取 {name}...")
        result[name] = fetch_city(code, name, top_n)
        if idx < total:
            time.sleep(REQUEST_DELAY)
    return result


def fetch_national(top_n: int = 50) -> list[dict]:
    """抓取全国热搜榜"""
    try:
        data = _request(board_type=0)
        items = data.get("data", {}).get("trending_list", [])
        result = []
        for i, item in enumerate(items[:top_n], 1):
            result.append({
                "rank": i,
                "word": item.get("word", ""),
                "hot_value": item.get("hot_value", 0),
                "video_count": item.get("video_count", 0),
                "sentence_id": item.get("sentence_id", ""),
            })
        return result
    except Exception as e:
        print(f"  [ERROR] 全国热搜获取失败: {e}")
        return []
