import json
import csv
import os
from datetime import datetime


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_json(data: dict, out_dir: str = "data") -> str:
    """保存为 JSON，文件名含时间戳"""
    _ensure_dir(out_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"hotlist_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def save_csv(city_data: dict[str, list[dict]], out_dir: str = "data") -> str:
    """将所有城市数据合并保存为单个 CSV"""
    _ensure_dir(out_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"hotlist_{ts}.csv")
    fields = ["city", "city_code", "rank", "word", "hot_value", "view_count", "video_count", "sentence_id"]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for items in city_data.values():
            writer.writerows(items)
    return path


def print_summary(city_data: dict[str, list[dict]], top_n: int = 5):
    """控制台打印各城市 Top N 摘要"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "=" * 62
    print(f"\n{line}")
    print(f"  抖音城市热榜  {ts}")
    print(line)
    for city, items in city_data.items():
        if not items:
            print(f"\n  【{city}】 无数据")
            continue
        print(f"\n  【{city}】TOP {min(top_n, len(items))}")
        for item in items[:top_n]:
            hv = f"{item['hot_value']:,}" if item["hot_value"] else "—"
            print(f"    {item['rank']:>2}. {item['word']}  ({hv})")
    print(f"\n{line}\n")
