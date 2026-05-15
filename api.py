import re
import time
from datetime import datetime, timedelta
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def extract_number_from_string(text):
    """从字符串中提取数字（支持整数、多位数）"""
    number_matches = re.findall(r'\d+', text)
    if number_matches:
        return int(number_matches[0])
    else:
        return None


def extract_continuous_single_double_prefix(text):
    """提取字符串开头连续的“单/双”文字"""
    match = re.match(r'^(单|双)+', text)
    if match:
        return match.group()
    else:
        return ""


def aaa():
    with sync_playwright() as p:
        # 启动浏览器（带调试参数）
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()
        page.set_default_timeout(90000)  # 全局超时90秒

        try:
            # 首次访问目标网页
            page.goto(
                "https://trend-01-955256821.ap-east-1.elb.amazonaws.com:8888/",
                wait_until="networkidle"
            )

            # 初始化变量
            a = -1
            b = -1
            refresh_interval = 120  # 刷新间隔：2分钟（120秒）
            last_refresh_time = datetime.now()  # 记录最后一次刷新时间

            for i in range(1000000000000):
                b = a
                current_time = datetime.now()
                print(
                    f"\n>>>>>>>>>>>>>>> 第{i}次循环 | 当前时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')} <<<<<<<<<<<<<<<<<")

                # ==================== 定位并提取数据 ====================
                parent_xpath = '//*[@id="app"]/div[1]/div[4]/div/div[1]/div/div/div'
                parent_locator = page.locator(f"xpath={parent_xpath}")

                try:
                    parent_locator.wait_for(state="visible", timeout=30000)
                except PlaywrightTimeoutError:
                    print(f"⚠️ 父元素加载超时，跳过本次循环")
                    time.sleep(5)  # 短暂等待后继续
                    continue

                # 获取最后一个子元素文本
                all_direct_children = parent_locator.locator("xpath=./*")
                child_count = all_direct_children.count()
                child_text = "无文本"
                shuzi = None
                danshuang = ""

                if child_count > 0:
                    child = all_direct_children.nth(child_count - 1)
                    child_text = child.text_content().strip() or "无文本"
                    print(f"文本内容：{child_text}")

                    # 提取数字和单双标识
                    if "单" in child_text or "双" in child_text:
                        shuzi = extract_number_from_string(child_text)
                        danshuang = extract_continuous_single_double_prefix(child_text)
                        print(f"提取到数字：{shuzi} | 单双标识：{danshuang}")

                # ==================== 核心逻辑：数字>50时的操作 ====================
                if shuzi and shuzi > 50:
                    danshuang_TT = str(danshuang).strip()
                    print("📢 数字大于50，开始执行10秒等待+刷新逻辑...")

                    # 第一步：先判断是否满足2分钟刷新间隔条件
                    time_condition = (current_time - last_refresh_time) >= timedelta(seconds=refresh_interval)
                    if time_condition:
                        try:
                            print("✅ 满足2分钟刷新间隔，开始刷新页面...")
                            # 执行页面刷新，等待网络空闲确保加载完成
                            page.reload(wait_until="networkidle", timeout=30000)
                            last_refresh_time = datetime.now()  # 更新最后刷新时间
                            print(f"✅ 页面刷新完成，最新刷新时间：{last_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        except PlaywrightTimeoutError:
                            print(f"⚠️ 页面刷新超时，保留上次刷新时间")
                    else:
                        # 不满足2分钟间隔，提示剩余时间
                        remaining = refresh_interval - (current_time - last_refresh_time).total_seconds()
                        print(f"⏸️  未满足2分钟刷新间隔，距离下次可刷新还需{remaining:.0f}秒")

                    # 第二步：执行原本的10秒等待逻辑
                    print("⏳ 开始10秒等待...")
                    time.sleep(10)
                    print("✅ 10秒等待完成")
                else:
                    # 数字≤50或无数字时，短间隔轮询
                    time.sleep(5)

        except Exception as e:
            print(f"\n❌ 程序执行出错：{type(e).__name__} - {str(e)}")
        finally:
            # 截图保存
            page.screenshot(path="children_screenshot.png")
            print("\n📸 已保存页面截图到：children_screenshot.png")
            # 关闭浏览器
            browser.close()


if __name__ == "__main__":
    aaa()