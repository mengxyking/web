import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def web_automation_with_xpath():
    with sync_playwright() as p:
        # 启动浏览器（带调试参数，避免启动报错）
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        # 创建页面并设置超时
        page = browser.new_page()
        page.set_default_timeout(30000)  # 全局超时30秒

        try:
            # 访问目标网页（等待页面加载完成）
            page.goto(
                "https://trend-01-955256821.ap-east-1.elb.amazonaws.com:8888/",
                wait_until="networkidle"  # 等待网络空闲，替代time.sleep
            )

            # ==================== 核心：定位父元素（标准写法） ====================
            # 父元素XPath（你指定的）
            for i in range(100):
                parent_xpath = '//*[@id="app"]/div[1]/div[4]/div/div[1]/div/div/div'
                # 显式声明XPath，等待元素可见
                parent_locator = page.locator(f"xpath={parent_xpath}")
                parent_locator.wait_for(state="visible", timeout=20000)
                print(f"✅ 父元素定位成功，是否可见：{parent_locator.is_visible()}")

                # ==================== 1. 获取父元素下【所有第一级子元素】（标准XPath） ====================
                # 核心修复：使用标准XPath语法 ./* （去掉括号，这是所有浏览器通用的写法）
                all_direct_children = parent_locator.locator("xpath=./*")
                child_count = all_direct_children.count()
                print(f"\n📊 父元素下第一级子元素总数：{child_count}")

                # 遍历所有第一级子元素（完善的异常处理）
                if child_count == 0:
                    print("⚠️ 未找到第一级子元素！请按以下步骤排查：")
                    print("  1. 打开网页F12 → Elements → Ctrl+F → 粘贴父元素XPath验证是否存在")
                    print("  2. 粘贴父元素XPath+/*（如{}/*）验证是否有子元素".format(parent_xpath))
                else:
                    # for i in range(child_count):
                    #     try:
                    #         child = all_direct_children.nth(i)
                    #         # 获取子元素信息（兼容空值）
                    #         child_tag = child.evaluate("el => el.tagName")  # 标签名
                    #         child_text = child.text_content().strip() or "无文本"
                    #         child_class = child.get_attribute("class") or "无class属性"
                    #         child_xpath = f"{parent_xpath}/*[{i + 1}]"  # 子元素完整XPath
                    #
                    #         print(f"\n--- 第{i + 1}个第一级子元素 ---")
                    #         print(f"完整XPath：{child_xpath}")
                    #         print(f"标签名：{child_tag}")
                    #         print(f"文本内容：{child_text}")
                    #         print(f"Class属性：{child_class}")
                    #     except Exception as e:
                    #         print(f"❌ 处理第{i + 1}个子元素时出错：{str(e)}")
                    #         continue
                    #print(all_direct_children.nth(child_count-1))

                    child = all_direct_children.nth(child_count-1)
                    # 获取子元素信息（兼容空值）
                    child_tag = child.evaluate("el => el.tagName")  # 标签名
                    child_text = child.text_content().strip() or "无文本"
                    child_class = child.get_attribute("class") or "无class属性"
                    #child_xpath = f"{parent_xpath}/*[{child_count + 1}]"  # 子元素完整XPath

                    print(f"\n--- 第{child_count-1 + 1}个第一级子元素 ---")
                    #print(f"完整XPath：{child_xpath}")
                    print(f"标签名：{child_tag}")
                    print(f"文本内容：{child_text}")
                    print(f"Class属性：{child_class}")
                    time.sleep(2)

                # ==================== 2. 精准获取某类第一级子元素（示例：div标签） ====================
                print("\n" + "-" * 50)
                # 标准XPath：定位父元素下第一级div子元素
                direct_div_children = parent_locator.locator("xpath=./div")
                div_count = direct_div_children.count()
                print(f"\n📌 父元素下第一级div子元素数量：{div_count}")

                if div_count > 0:
                    first_div = direct_div_children.first
                    first_div_html = first_div.inner_html()[:200]  # 只显示前200字符
                    print(f"第一个div子元素的HTML：{first_div_html}...")

            # ==================== 调试辅助：手动验证XPath（可选） ====================
            # 取消下面注释，运行后会暂停，可在Playwright调试面板手动输入XPath验证
            # page.pause()

        except PlaywrightTimeoutError:
            print("\n❌ 超时错误：父元素未加载！")
            print(f"  父元素XPath：{parent_xpath}")
            print("  检查：网页是否能打开？XPath是否正确？是否需要登录？")
        except Exception as e:
            print(f"\n❌ 程序执行出错：{type(e).__name__} - {str(e)}")
        finally:
            # 截图保存（便于排查元素结构）
            page.screenshot(path="children_screenshot.png")
            print("\n📸 已保存页面截图到：children_screenshot.png")
            # 关闭浏览器
            browser.close()
            print("🔚 浏览器已关闭")


if __name__ == "__main__":
    # 解决中文打印乱码问题
    import sys

    sys.stdout.reconfigure(encoding='utf-8')
    web_automation_with_xpath()