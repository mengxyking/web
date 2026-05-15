import win32clipboard
import win32con

def set_clipboard(text):
    """设置Windows剪贴板内容"""
    # 打开剪贴板
    win32clipboard.OpenClipboard()
    try:
        # 清空剪贴板
        win32clipboard.EmptyClipboard()
        # 将文本写入剪贴板（以Unicode格式）
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
    finally:
        # 关闭剪贴板（必须执行，否则其他程序无法访问剪贴板）
        win32clipboard.CloseClipboard()

def get_clipboard():
    """获取Windows剪贴板内容"""
    # 打开剪贴板
    win32clipboard.OpenClipboard()
    try:
        # 读取剪贴板的Unicode文本内容
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        else:
            content = "剪贴板中无文本内容"
    finally:
        # 关闭剪贴板
        win32clipboard.CloseClipboard()
    return content

# 调用函数测试
if __name__ == "__main__":
    # 设置剪贴板内容
    set_text = "使用win32clipboard操作111Windows剪贴板"
    set_clipboard(set_text)
    print(f"已写入剪贴板：{set_text}")

    # 获取剪贴板内容
    get_text = get_clipboard()
    print(f"读取剪贴板内容：{get_text}")