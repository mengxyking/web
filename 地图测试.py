import requests


def baidu_map_search(key):
    # 注册->新建应用 http://lbsyun.baidu.com/
    apk_key = "oUhdI1EUNvhhNQphyKelx5bAmxiqnHFP"

    url = "http://api.map.baidu.com/place/v2/search"

    params = {
        "query": key,
        "output": "json",
        "ak": apk_key,
        "region": "济宁市",
        "page_size": 20,
        "page_num": 1,
        "scope": 2
    }

    response = requests.get(url, params)
    result = response.json()
    status = result.get("status")
    message = result.get("message")

    if status != 0 and status != 2:
        raise Exception(message)

    data = result.get("results", {})
    for row in data:
        item = {
            "name": row.get("name", ""),
            "address": row.get("address", ""),
            "province": row.get("province", ""),
            "city": row.get("city", ""),
            "area": row.get("area", ""),
            "telephone": row.get("telephone", ""),
            "tag": row.get("detail_info", {}).get("tag", ""),
        }

        for k, v in item.items():
            print("{}: {}".format(k, v))


if __name__ == '__main__':
    baidu_map_search("成都小吃")

