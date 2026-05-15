import uiautomator2 as u2
import pychrome
import subprocess

class HybridAutomation:
    def __init__(self, serial):
        self.d = u2.connect(serial)
        self.serial = serial
        self._cdp_tab = None

    def connect_webview(self):
        subprocess.run(['adb', '-s', self.serial, 'forward',
                        'tcp:9222', 'localabstract:webview_devtools_remote_31715'])
        browser = pychrome.Browser(url="http://127.0.0.1:9222")
        print(browser.dev_url)
        print(browser.list_tab())
        tab = browser.list_tab()[0]
        tab.start()
        self._cdp_tab = tab

    def native_click(self, text):
        self.d(text=text).click()

    def web_click(self, selector):
        self._cdp_tab.Runtime.evaluate(
            expression=f"document.querySelector('{selector}').click()"
        )

    def web_input(self, selector, value):
        self._cdp_tab.Runtime.evaluate(
            expression=f"""
                var el = document.querySelector('{selector}');
                el.value = '{value}';
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
            """
        )

    def web_get_text(self, selector):
        r = self._cdp_tab.Runtime.evaluate(
            expression=f"document.querySelector('{selector}').innerText"
        )
        return r['result'].get('value', '')

bb = HybridAutomation("ALTMVB3B17005679")
bb.connect_webview()
bb.native_click("签到")