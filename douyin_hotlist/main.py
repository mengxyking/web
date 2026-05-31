"""
抖音城市热榜抓取工具
用法:
  python main.py                  # 抓取全部城市，打印摘要并保存
  python main.py --top 10         # 每城市取 Top 10
  python main.py --format csv     # 只保存 CSV（默认同时保 JSON+CSV）
  python main.py --city 北京 上海 # 只抓指定城市
  python main.py --no-save        # 只打印，不保存文件
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import CITIES, DEFAULT_TOP_N
from fetcher import fetch_all_cities, fetch_city
from storage import save_json, save_csv, print_summary


def parse_args():
    p = argparse.ArgumentParser(description="抖音城市热榜抓取")
    p.add_argument("--top", type=int, default=DEFAULT_TOP_N, help="每城市取前 N 条（默认30）")
    p.add_argument("--city", nargs="+", help="指定城市名，如 北京 上海，默认全部")
    p.add_argument("--format", choices=["json", "csv", "both"], default="both", help="保存格式（默认both）")
    p.add_argument("--no-save", action="store_true", help="不保存文件，只打印")
    p.add_argument("--summary-top", type=int, default=5, help="摘要显示前 N 条（默认5）")
    return p.parse_args()


def resolve_cities(city_names: list[str] | None) -> dict:
    if not city_names:
        return CITIES
    name_to_code = {v: k for k, v in CITIES.items()}
    result = {}
    for name in city_names:
        code = name_to_code.get(name)
        if code:
            result[code] = name
        else:
            print(f"  [WARN] 未知城市: {name}，跳过")
    return result


def main():
    args = parse_args()
    cities = resolve_cities(args.city)

    if not cities:
        print("没有有效的城市，退出。")
        sys.exit(1)

    print(f"\n开始抓取 {len(cities)} 个城市的热榜（每城市 Top {args.top}）...")
    city_data = fetch_all_cities(cities, top_n=args.top)

    # 打印摘要
    print_summary(city_data, top_n=args.summary_top)

    # 保存
    if not args.no_save:
        if args.format in ("json", "both"):
            path = save_json({"cities": city_data}, out_dir="data")
            print(f"  JSON 已保存: {path}")
        if args.format in ("csv", "both"):
            path = save_csv(city_data, out_dir="data")
            print(f"  CSV  已保存: {path}")
        print()


if __name__ == "__main__":
    main()
