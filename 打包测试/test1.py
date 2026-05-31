import random
import time

import numpy as np
import uiautomator2 as u2

res = random.sample([1,2,3], 2)
print(res)
if(1 in res):
    print("zai")

def get_video_progress(d):
    # 通过 resource-id 自动获取进度条坐标，不用硬编码
    bar_el = d(resourceId="com.ss.android.ugc.aweme.id/ceo")
    if not bar_el.exists():
        print("bucunzai")
        return -1

    bounds = bar_el.info['bounds']
    x1, y1, x2, y2 = bounds['left'], bounds['top'], bounds['right'], bounds['bottom']
    w = x2 - x1

    screenshot = d.screenshot()
    img = np.array(screenshot.crop((x1, y1, x2, y2)))

    # 进度条是白色/亮色（不是红色）
    white_mask = (img[:, :, 0] > 150) & (img[:, :, 1] > 150) & (img[:, :, 2] > 150)
    col_white = white_mask.any(axis=0).astype(float)

    # 20px 滑动窗口过滤孤立的章节点（章节点只有几px宽，播放区域是连续的）
    smooth = np.convolve(col_white, np.ones(20) / 20, mode='same')

    # 找最右边密度>0.6的列 = 已播放区域结束位置
    played_cols = np.where(smooth > 0.6)[0]

    if len(played_cols) == 0:
        return 0

    return round(played_cols.max() / w * 100, 1)





str_t = "😂 这个工具 搭配uiautomator2 效率翻倍啊"

d = u2.connect("ALTMVB3B17005679")
print(get_video_progress(d))
# for tt in str_t:
#
#     d.send_keys(tt)
#     time.sleep(0.1)
