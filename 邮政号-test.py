import requests
import json


def yunda_record_search():
    # 请求URL
    url = "https://web.yundaex.com/index.php/api/v2.record/search"

    # 请求头（从抓包内容中提取，需根据实际情况更新Cookie）
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryORjUAqQBthfnFa2B",
        "Cookie": "Hm_lvt_b28b26d0567a88813853e0e3614b46a0=1765084542; Hm_lpvt_b28b26d0567a88813853e0e3614b46a0=1765084542; HMACCOUNT=FD42DEADBF19F22C; SECKEY_ABVK=bxHzW1ZUIeMhPtKkbheeIPwtWJsCS+XLsR5Ii3LQoVQy+HHSxmDpD5ZrvTbjsBBWm/36nPoDhm7wFppqJW82rw%3D%3D; BMAP_SECKEY=bxHzW1ZUIeMhPtKkbheeIPwtWJsCS-XLsR5Ii3LQoVRdhtHcYGUK4tBQZ6-3yCiAEmzCV7W2w_By2togY7UkZcgjVE9f4XGrPm5u_ZIz-a0g72Px1NXYdV_8NuzIzHJpW-lDPPa0mPU6bxmOFbo64jD371cbobYQjhv8xECqGRAJ2j_VYA91RuSKKPDKM1GEy_w4Uk-FeXoEGuXtSTIVDkGEu8jCkBJfUN_X8oPdDpk; ydgw=9s9ljgvdnhqcmvaihod487lbe9",
        "Host": "web.yundaex.com",
        "Origin": "https://web.yundaex.com",
        "Pragma": "no-cache",
        "Referer": "https://web.yundaex.com/infoInquiry?nav_id=262&cid=0&homeWaybill=434927098758859",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }

    # 构造multipart/form-data请求体（boundary需和请求头一致）
    # 注意：实际业务参数需根据接口要求补充，此处为示例模板
    boundary = "----WebKitFormBoundaryORjUAqQBthfnFa2B"
    payload_parts = [
        f"--{boundary}",
        # 示例参数1：运单号（根据实际接口字段调整）
        'Content-Disposition: form-data; name="waybillNo"',
        "",
        "434927098758859",  # 示例运单号，从Referer中提取
        f"--{boundary}",
        # 示例参数2：查询类型（可根据接口文档补充其他参数）
        'Content-Disposition: form-data; name="queryType"',
        "",
        "1",
        f"--{boundary}--"  # 结束标记
    ]
    payload = "\r\n".join(payload_parts)

    try:
        # 发送POST请求
        response = requests.post(
            url=url,
            headers=headers,
            data=payload,
            verify=False,  # 忽略SSL证书验证（生产环境建议开启）
            timeout=30
        )

        # 输出响应结果
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}")
        print(f"响应内容: {response.text}")

        # 若返回JSON格式，可解析为字典
        if response.headers.get("Content-Type", "").startswith("application/json"):
            response_json = response.json()
            print(f"JSON响应: {json.dumps(response_json, indent=2, ensure_ascii=False)}")

        return response

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        return None


if __name__ == "__main__":
    # 禁用requests的SSL警告
    #requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    # 执行请求
    yunda_record_search()