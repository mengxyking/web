"""
通过 uiautomator UI 层级 XML 定位福袋按钮
比图色识别更稳定，适合 ADB 自动化场景

使用方式：
  python fudai_ui_finder.py                    # 自动 adb dump 并查找
  python fudai_ui_finder.py --file dump.xml    # 解析本地 XML 文件
  python fudai_ui_finder.py --loop 3           # 每隔3秒自动检测并点击
"""

import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass


# ── 数据结构 ───────────────────────────────────────────

@dataclass
class UINode:
    text: str
    content_desc: str
    resource_id: str
    class_name: str
    clickable: bool
    bounds: tuple[int, int, int, int]   # x1, y1, x2, y2

    @property
    def center(self) -> tuple[int, int]:
        x1, y1, x2, y2 = self.bounds
        return (x1 + x2) // 2, (y1 + y2) // 2

    @property
    def area(self) -> int:
        x1, y1, x2, y2 = self.bounds
        return (x2 - x1) * (y2 - y1)


# ── XML 解析 ───────────────────────────────────────────

def parse_bounds(bounds_str: str) -> tuple[int, int, int, int]:
    """解析 '[x1,y1][x2,y2]' 格式"""
    nums = list(map(int, re.findall(r'\d+', bounds_str)))
    return nums[0], nums[1], nums[2], nums[3]


def parse_hierarchy(xml_content: str) -> list[UINode]:
    """解析 uiautomator dump XML，返回所有节点列表"""
    root = ET.fromstring(xml_content)
    nodes = []

    for elem in root.iter('node'):
        bounds_str = elem.get('bounds', '[0,0][0,0]')
        try:
            bounds = parse_bounds(bounds_str)
        except Exception:
            continue

        nodes.append(UINode(
            text         = elem.get('text', ''),
            content_desc = elem.get('content-desc', ''),
            resource_id  = elem.get('resource-id', ''),
            class_name   = elem.get('class', ''),
            clickable    = elem.get('clickable', 'false').lower() == 'true',
            bounds       = bounds,
        ))

    return nodes


# ── 福袋定位策略 ────────────────────────────────────────

# 匹配关键词（按优先级排列）
FUDAI_KEYWORDS = [
    "福袋",
    "抢福袋",
    "领福袋",
    "开福袋",
    "fudai",
]

def find_fudai_nodes(nodes: list[UINode], screen_height: int = 2412) -> list[UINode]:
    """
    从节点列表中找出福袋候选节点
    策略：text 或 content_desc 包含关键词，且节点可见（area > 0）
    """
    candidates = []

    for node in nodes:
        combined = node.text + node.content_desc
        if not combined:
            continue

        for kw in FUDAI_KEYWORDS:
            if kw in combined:
                x1, y1, x2, y2 = node.bounds
                if (x2 - x1) > 0 and (y2 - y1) > 0:   # 排除不可见节点
                    candidates.append(node)
                break

    # 优先选可点击的，其次选面积最小的（精确命中按钮本身，不选父容器）
    if candidates:
        clickable = [n for n in candidates if n.clickable]
        pool = clickable if clickable else candidates
        pool.sort(key=lambda n: n.area)

    return candidates


def find_best_fudai(nodes: list[UINode]) -> UINode | None:
    candidates = find_fudai_nodes(nodes)
    if not candidates:
        return None
    clickable = [n for n in candidates if n.clickable]
    pool = clickable if clickable else candidates
    pool.sort(key=lambda n: n.area)
    return pool[0]


# ── ADB 工具函数 ────────────────────────────────────────

def adb_dump_hierarchy(save_path: str = "/tmp/ui_dump.xml") -> str:
    """通过 ADB 获取当前界面的 UI 层级 XML"""
    subprocess.run(
        ["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"],
        check=True, capture_output=True
    )
    subprocess.run(
        ["adb", "pull", "/sdcard/ui_dump.xml", save_path],
        check=True, capture_output=True
    )
    with open(save_path, encoding="utf-8") as f:
        return f.read()


def adb_tap(x: int, y: int):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
    print(f"[ADB] 点击坐标: ({x}, {y})")


# ── 主逻辑 ──────────────────────────────────────────────

def detect_from_xml(xml_content: str, verbose: bool = True) -> tuple[int, int] | None:
    nodes = parse_hierarchy(xml_content)
    node  = find_best_fudai(nodes)

    if node:
        cx, cy = node.center
        if verbose:
            print(f"[找到] 福袋节点")
            print(f"  text        : {node.text!r}")
            print(f"  content_desc: {node.content_desc[:60]!r}")
            print(f"  clickable   : {node.clickable}")
            print(f"  bounds      : {node.bounds}")
            print(f"  中心坐标    : ({cx}, {cy})")
        return cx, cy

    if verbose:
        print("[未找到] 当前界面没有包含福袋关键词的节点")
        # 打印所有有文字的可点击节点，辅助调试
        print("\n[调试] 当前可点击节点 (前20个):")
        clickable = [n for n in nodes if n.clickable and (n.text or n.content_desc)]
        for n in clickable[:20]:
            label = (n.text or n.content_desc)[:50]
            print(f"  {n.bounds}  {label!r}")

    return None


def auto_detect_and_click(loop_interval: float = 0):
    """
    loop_interval=0  → 只执行一次
    loop_interval>0  → 每隔 N 秒循环检测，找到就点击
    """
    while True:
        try:
            print("\n正在获取 UI 层级...")
            xml = adb_dump_hierarchy()
            coord = detect_from_xml(xml)
            if coord:
                adb_tap(*coord)
        except subprocess.CalledProcessError as e:
            print(f"[ADB错误] {e}")
        except Exception as e:
            print(f"[错误] {e}")

        if loop_interval <= 0:
            break
        print(f"等待 {loop_interval} 秒后重试...")
        time.sleep(loop_interval)


# ── 坐标筛选：正方形节点 ────────────────────────────────

def find_square_nodes(xml_content: str,
                      cx_min: int = 30,  cx_max: int = 500,
                      cy_min: int = 300, cy_max: int = 500) -> list[dict]:
    """
    从 UI 层级 XML 中筛选满足条件的正方形节点：
      cx_min < 中心x < cx_max
      cy_min < 中心y < cy_max
      宽 == 高

    返回: [{'bounds','cx','cy','size','clickable','class','resource_id','content_desc'}, ...]
    """
    nodes = parse_hierarchy(xml_content)
    results = []
    for n in nodes:
        x1, y1, x2, y2 = n.bounds
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0 or w != h:
            continue
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if not (cx_min < cx < cx_max and cy_min < cy < cy_max):
            continue
        results.append({
            'bounds':       f"[{x1},{y1}][{x2},{y2}]",
            'cx':           cx,
            'cy':           cy,
            'size':         w,
            'clickable':    n.clickable,
            'class':        n.class_name.split('.')[-1],
            'resource_id':  n.resource_id,
            'content_desc': n.content_desc,
            'text':         n.text,
        })
    return results


# ── 入口 ───────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    # 解析本地 XML 文件
    if "--file" in args:
        idx = args.index("--file")
        path = args[idx + 1]
        with open(path, encoding="utf-8") as f:
            xml_content = f.read()
        detect_from_xml(xml_content)

    # 循环模式
    elif "--loop" in args:
        idx = args.index("--loop")
        interval = float(args[idx + 1]) if idx + 1 < len(args) else 3.0
        auto_detect_and_click(loop_interval=interval)

    # 默认：一次性 ADB 检测
    else:
        auto_detect_and_click(loop_interval=0)
