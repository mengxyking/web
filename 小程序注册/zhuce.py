import requests
import time
import re


def get_shoulvrujia_code(api_token, phone_number, timeout=60, interval=10):
    """
    循环请求取码接口，查找符合条件的首旅如家电码
    :param api_token: 接口的token（比如 cVtxsWiCzzWf7fjf4QKqm5）
    :param phone_number: 手机号（比如 18222225079）
    :param timeout: 总超时时间（默认60秒）
    :param interval: 每次请求间隔（默认10秒）
    :return: 验证码（字符串）或 None
    """
    # 1. 提取手机号后四位
    phone_last4 = phone_number[-4:]
    if len(phone_last4) != 4 or not phone_last4.isdigit():
        print("❌ 手机号格式错误，无法提取后四位")
        return None

    # 2. 构造接口URL
    api_url = f"http://sms.szfangmm.com:3000/api/smslist?token={api_token}"

    # 3. 循环请求（最多60秒，每10秒一次）
    start_time = time.time()
    max_attempts = timeout // interval  # 最多请求次数（60/10=6次）

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\n🔍 第{attempt}次请求接口（已耗时{(time.time() - start_time):.0f}秒）")
            # 请求接口
            resp = requests.get(api_url, timeout=10)
            resp.raise_for_status()  # 捕获HTTP错误（4xx/5xx）
            sms_list = resp.json()

            # 校验返回数据格式
            if not isinstance(sms_list, list):
                print("⚠️ 接口返回非列表格式，跳过本次")
                time.sleep(interval)
                continue

            # 4. 遍历短信列表匹配条件
            for sms in sms_list:
                # 提取simnum后四位（simnum格式：18****5097）
                simnum = sms.get("simnum", "")
                simnum_last4 = simnum[-4:] if len(simnum) >= 4 else ""

                # 匹配条件：simnum后四位一致 + content含“首旅如家”
                content = sms.get("content", "")
                if simnum_last4 == phone_last4 and "首旅如家" in content:
                    # 5. 提取验证码（匹配数字串，适配不同格式：验证码:698702 / 验证码：698702）
                    code_match = re.search(r'验证码[:：](\d+)', content)
                    if code_match:
                        code = code_match.group(1)
                        print(f"✅ 找到匹配验证码：{code}")
                        return code
                    else:
                        print("⚠️ 找到首旅如家短信，但未提取到验证码")
                        continue

            # 本次没找到，等待interval秒后重试
            print("❌ 本次未找到符合条件的短信，等待10秒重试...")
            time.sleep(interval)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 接口请求失败：{str(e)}，等待10秒重试...")
            time.sleep(interval)
        except Exception as e:
            print(f"⚠️ 未知错误：{str(e)}，等待10秒重试...")
            time.sleep(interval)

    # 60秒内未找到
    print(f"\n❌ 超时{timeout}秒，未找到符合条件的首旅如家电码")
    return None


# ====================== 使用示例 ======================
if __name__ == "__main__":
    # 替换成你的实际参数
    API_TOKEN = "cVtxsWiCzzWf7fjf4QKqm5"
    PHONE_NUMBER = "13037178295"

    # 调用方法获取验证码
    verify_code = get_shoulvrujia_code(API_TOKEN, PHONE_NUMBER)

    if verify_code:
        print(f"\n🎉 最终获取到验证码：{verify_code}")
    else:
        print("\n❌ 未获取到验证码")