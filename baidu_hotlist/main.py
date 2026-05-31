"""
百度热搜榜抓取工具
用法:
  python main.py                          # 抓取默认5个榜单，打印摘要并保存
  python main.py --all                    # 抓取全部11个榜单
  python main.py --top 10                 # 每榜取 Top 10
  python main.py --board 热搜榜 财经榜    # 只抓指定榜单
  python main.py --city 北京 上海         # 抓城市榜（需中国大陆IP）
  python main.py --city-all               # 抓全部城市榜（需中国大陆IP）
  python main.py --format csv             # 只保存 CSV（默认同时保 JSON+CSV）
  python main.py --no-save                # 只打印，不保存文件
  python main.py --summary-top 10        # 摘要显示前 10 条
"""
import argparse
import sys
import os
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import BOARD_TABS, DEFAULT_BOARDS, CITIES, DEFAULT_TOP_N
from fetcher import fetch_all_boards, fetch_all_cities
from storage import save_json, save_csv, print_summary


def parse_args():
    p = argparse.ArgumentParser(description="百度热搜榜抓取")
    p.add_argument("--top",         type=int, default=DEFAULT_TOP_N,
                   help="每榜取前 N 条（默认30）")
    p.add_argument("--all",         action="store_true",
                   help="抓取全部11个榜单")
    p.add_argument("--board",       nargs="+",
                   help="指定榜单名，如 热搜榜 财经榜")
    p.add_argument("--city",        nargs="+",
                   help="指定城市，如 北京 上海（需中国大陆IP）")
    p.add_argument("--city-all",    action="store_true",
                   help="抓取全部城市榜（需中国大陆IP）")
    p.add_argument("--format",      choices=["json", "csv", "both"], default="both",
                   help="保存格式（默认both）")
    p.add_argument("--no-save",     action="store_true",
                   help="不保存文件，只打印")
    p.add_argument("--summary-top", type=int, default=5,
                   help="摘要显示前 N 条（默认5）")
    p.add_argument("--out-dir",     default="data",
                   help="输出目录（默认 data/）")
    return p.parse_args()


def resolve_boards(args) -> dict:
    name_to_tab = {v: k for k, v in BOARD_TABS.items()}

    if args.board:
        result = {}
        for name in args.board:
            tab = name_to_tab.get(name)
            if tab:
                result[tab] = name
            else:
                avail = "、".join(BOARD_TABS.values())
                print(f"  [WARN] 未知榜单: {name}，可用：{avail}")
        return result

    if getattr(args, "all"):
        return BOARD_TABS.copy()

    return {tab: BOARD_TABS[tab] for tab in DEFAULT_BOARDS}


def resolve_cities(args) -> list:
    if getattr(args, "city_all"):
        return list(CITIES)
    if args.city:
        result = []
        for name in args.city:
            if name in CITIES:
                result.append(name)
            else:
                print(f"  [WARN] 未知城市: {name}，可用城市共 {len(CITIES)} 个")
        return result
    return []


def main():
    args         = parse_args()
    boards       = resolve_boards(args)
    cities       = resolve_cities(args)
    all_data     = {}

    # ── 抓榜单 ──
    if boards:
        print(f"\n开始抓取 {len(boards)} 个榜单（每榜 Top {args.top}）...")
        all_data.update(fetch_all_boards(boards, top_n=args.top))

    # ── 抓城市榜 ──
    if cities:
        print(f"\n开始抓取 {len(cities)} 个城市热榜（每城 Top {args.top}，需中国大陆IP）...")
        all_data.update(fetch_all_cities(cities, top_n=args.top))

    if not all_data:
        print("没有指定任何榜单或城市，退出。")
        sys.exit(1)

    # ── 打印摘要 ──
    print_summary(all_data, top_n=args.summary_top)

    # ── 保存 ──
    if not args.no_save:
        batch_id     = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4())[:6]
        collect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if args.format in ("json", "both"):
            path = save_json({"boards": all_data, "batch_id": batch_id,
                              "collect_time": collect_time}, out_dir=args.out_dir)
            print(f"  JSON 已保存: {path}")
        if args.format in ("csv", "both"):
            path = save_csv(all_data, out_dir=args.out_dir)
            print(f"  CSV  已保存: {path}")
        print()


if __name__ == "__main__":
    main()
