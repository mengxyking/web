import urllib
from tools import read_jscode
import requests

import os
import sys
import datetime
import threading
from flask_cors import CORS
from flask import copy_current_request_context
from flask import Flask, render_template, request, redirect, url_for

import random
import time
import json
import requests

# flask所在根目录为站点根目录
app = Flask(__name__)
# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')

# 测试全局变量
strAll = 'it is str all'
modelnamenow = '';  # 代号46
isrunnow = 0;
pipelinenow = '';


@app.route('/testnow')
def testnow():
    global strAll
    name = request.args.get('strall')
    if (name):
        strAll = name
    else:
        teststr = 'hello'
    print("strAll is ", strAll)
    return strAll


@app.route('/predict/getImage', methods=['post'])
def predictImage():
    try:
        log_path = r"./CPM_main/log.txt"
        # counter_(log_path)
        with open(log_path, "r", encoding='utf8') as f:
            counter = int(float(f.read()))

        # if counter > number:
        # return

        data = request.form
        title = data["title"]
        imgsurl = '';
        # imgsurl = getImage(title)
        print("imgsurl", imgsurl)
        num = random.randint(0, len(imgsurl) - 1)
        return imgsurl[num]
    except Exception as e:
        return f"ERROR :{e}"


def testgo():
    maketxt()


@app.route('/maketxt', methods=['get'])
def maketxt():
    try:
        global modelnamenow
        global pipelinenow

        return ''

        api_key1 = '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'
        api_key2 = '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'
        api_key3 = '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'
        api_key4 = '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'
        api_key5 = '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'
        listkey = []
        listkey.append(api_key1)
        listkey.append(api_key2)
        listkey.append(api_key3)
        listkey.append(api_key4)
        listkey.append(api_key5)

        # url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
        # # Set the headers and payload for the API request
        # headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key}
        # payload = {'prompt': 'Hello, what is your name,how old r u?', 'max_tokens': 50, 'temperature': 0.7}

        # Make the API request
        # response = requests.post(url, headers=headers, data=json.dumps(payload))
        # # Parse the response and extract the generated text
        # response_data = json.loads(response.text)
        # generated_text = response_data['choices'][0]['message']
        # print(generated_text)

        name = request.args.get('model')
        title = request.args.get('title')
        keyidinput = request.args.get('apikey')
        keynow = listkey[0]
        if (name and name.isdigit()):
            kid = int(keyidinput)
            if ((kid > listkey.count()) or kid == 0):
                keynow = listkey[0]
            else:
                keynow = listkey[kid - 1]

        if (name and name.isdigit() and (name + "") == "49"):
            isgo = 1
        else:
            rest = {'code': '501', 'time': '', 'article': '', 'role': ''}
            txt = json.dumps(rest)
            # return "bye"
            return txt

        # print(f"title:{title}",end="  ")
        str = [{"role": "system", "content": "You are a helpful assistant."}, \
               {"role": "user", "content": "Who are you"}, \
               {"role": "assistant", "content": "you are a new ai."}, \
               {"role": "user", "content": "where are u"}];
        strsep = '-t^t-'
        # strarr = json.loads(str)
        strarr = []
        if (title):
            str = title.split(strsep)
            if (str):
                for i, string in enumerate(str):
                    str[i] = string.replace(strsep, '')
                    strarr.append(json.loads(str[i]))
            else:
                return '';
        else:
            print('err input')
            return 'bye'
        stime = time.time()

        # gpt-3.5-turbo
        openai.api_key = keynow
        resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=strarr)

        # article=article.replace('"','“')

        gen_text = resp['choices'][0]['message']
        # print(gen_text)
        # print(gen_text['role'])
        # print(gen_text['content'])

        endtime = time.time()
        dotime = endtime - stime
        strtmp = '19991231666';
        rest = {'code': 'ok', 'time': dotime, 'article': strtmp, 'role': gen_text['role']}
        txt = json.dumps(rest)
        txt = txt.replace(strtmp, gen_text['content']);
        print(txt)
        return txt

    except Exception as e:
        return f"ERROR :{e}"
    finally:
        print('')


@app.route('/train', methods=['post'])
def Train_model():
    try:
        return ''
        log_path = r"./CPM_main/log.txt"
        counter_(log_path)
        with open(log_path, "r", encoding='utf8') as f:
            counter = int(float(f.read()))
        # if counter > number:
        # return

        data = request.form
        model_name = data["model_name"]
        # print(model_name)
        subpath = str(get_subpath(ori_path=r"./model"))
        vocab_file = r"./vocab/chinese_vocab.model"
        log_path = r"./CPM_main/log/generate.log"
        info = train_data2generate_model(subpath, vocab_file, log_path, model_name)
        return info
    except Exception as e:
        return f"ERROR :{e}"
    finally:
        print('')


def duqu():
    # 读取txt文件，以二维列表形式输出，每一个元素为一行
    file = open('./model/model_name', mode='r', encoding='UTF-8')
    list = []
    # 读取所有行(直到结束符 EOF)并返回列表
    contents = file.readlines()
    print(contents)
    for msg in contents:
        list = msg.split(',')
        # 字符串根据空格进行分割
    file.close()
    print(list)
    return list



@app.route('/douyinfind', methods=['post', 'get'])
def douyinff():
    try:
        info = ''
        data = request.get_json()
        key = data["key"]
        if (key != 'douyinauto'):
            return ''

        surl = data["url1"]
        # print('stp1:'+surl)
        #sort_type = 2 & filter_duration = 0-1 & keyword = 月牙包
        sort_type = data["sort_type"]
        filter_duration = data["filter_duration"]
        keyword = data["keyword"]
        publish_time=data["publish_time"]
        offset=data["offset"]
        count=data["count"]
        search_id=data["search_id"]

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            # 'cookie': '__ac_nonce=0668618c4005119f5340d; __ac_signature=_02B4Z6wo00f01h8bUvAAAIDDw2LNRhYyjoofO1ZAAOFO4a; SEARCH_RESULT_LIST_TYPE=%22single%22; ttwid=1%7Co0FlryLLbADdey5T-oKIiep8pw9a58UVFTIjJ-gtLA4%7C1720064197%7Cca75a7c6c9075ef75f0b6d96a9a17aa690a13d43d86d09d45f6074ccb4bb9518; x-web-secsdk-uid=a250ab50-550a-48ec-becb-d5038d3d6b29; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; device_web_cpu_core=16; device_web_memory_size=8; architecture=amd64; publish_badge_show_info=%221%2C%22; my_rd=2; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAYhICYl8ryfLoHHiivyLLMuU-3bfJMAe6qqrmpY7V3kToJXReFKoklOsST1qETZk9%2F1720108800000%2F0%2F1720064245191%2F0%22; passport_csrf_token=f78d99693de3a7f1fbd2a5d8dc1d7d8b; passport_csrf_token_default=f78d99693de3a7f1fbd2a5d8dc1d7d8b; sso_uid_tt=c7ec5b3e12cc561e081535d84bc11e6a; sso_uid_tt_ss=c7ec5b3e12cc561e081535d84bc11e6a; toutiao_sso_user=897ca17053846bf58f221a77eb53aaaa; toutiao_sso_user_ss=897ca17053846bf58f221a77eb53aaaa; sid_ucp_sso_v1=1.0.0-KDA4M2FlNGUxZGI1MzliOGM1ZjZkY2ZmZDZhMDliZjI2NTZkNDlmN2EKCRDysZi0BhjvMRoCbGYiIDg5N2NhMTcwNTM4NDZiZjU4ZjIyMWE3N2ViNTNhYWFh; ssid_ucp_sso_v1=1.0.0-KDA4M2FlNGUxZGI1MzliOGM1ZjZkY2ZmZDZhMDliZjI2NTZkNDlmN2EKCRDysZi0BhjvMRoCbGYiIDg5N2NhMTcwNTM4NDZiZjU4ZjIyMWE3N2ViNTNhYWFh; odin_tt=a015f33f1a9ef23a98f1ba6766b64ad38063f685130fc12938b7aeddb3b158c2; sid_guard=a116e791c5c77b3bf462d5f59cbf6263%7C1720064242%7C21600%7CThu%2C+04-Jul-2024+09%3A37%3A22+GMT; uid_tt=8fa5210b38176a6ee0968f61541e15fd; uid_tt_ss=8fa5210b38176a6ee0968f61541e15fd; sid_tt=a116e791c5c77b3bf462d5f59cbf6263; sessionid=a116e791c5c77b3bf462d5f59cbf6263; sessionid_ss=a116e791c5c77b3bf462d5f59cbf6263; sid_ucp_v1=1.0.0-KGJjNDA4NzBkMzc5ZDU0ZmFiMGUxNzY0NjBjMjA5ZDBmOTEyYWVlOGIKCBDysZi0BhgNGgJscSIgYTExNmU3OTFjNWM3N2IzYmY0NjJkNWY1OWNiZjYyNjM; ssid_ucp_v1=1.0.0-KGJjNDA4NzBkMzc5ZDU0ZmFiMGUxNzY0NjBjMjA5ZDBmOTEyYWVlOGIKCBDysZi0BhgNGgJscSIgYTExNmU3OTFjNWM3N2IzYmY0NjJkNWY1OWNiZjYyNjM; UIFID_TEMP=3c3e9d4a635845249e00419877a3730e2149197a63ddb1d8525033ea2b3354c241393d868f95548dd290c26c84fa8787604ddd1211f3d0efa25450721b2351d6b090504d4eadc8f258b93f38a67555c1d680b7f494d3146a3d0ef2704a05dc209a69facf5a1f7e73caa9147d54debaad; dy_swidth=1920; dy_sheight=1080; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; csrf_session_id=b9d30736d2d0c635b7566167c1e1779f; fpk1=U2FsdGVkX19HhaFbwlg0GePbxuqHJfX2OdeOZ1TkZck6RhXurOn+A6Yfk7iCYvPaKPORyVWJRkqdJDEyjs9hHg==; fpk2=f1f6b29a6cc1f79a0fea05b885aa33d0; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQUp1UDNFa1p2bnE5dmNBR0gvYlNtSUtQM3B1R2gzbGx1bGtMdkkvcHlmUE10OEtzMUUyUVNWLzFBOXRRVTRzQjRPYTNVNkVQOFQ4ZExud1h5ZEtobEk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; bd_ticket_guard_client_web_domain=2; biz_trace_id=09f24ce3; s_v_web_id=verify_ly6puls7_Nbl4e9BE_QnUp_4Ebv_BM40_391OsTET46Zy; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; home_can_add_dy_2_desktop=%221%22; IsDouyinActive=true',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.douyin.com/search/%E6%9C%88%E7%89%99%E6%B9%BE?aid=528703e2-96f3-4531-bd9a-8f261cf74c50&type=general',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }


        # print('headers1: '+data["headers1"])
        #headers = json.loads(data["headers1"])
        # print('stp35')
        params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'search_channel': 'aweme_general',
            'enable_history': '1',
            'keyword': '月牙包',
            'search_source': 'normal_search',
            'query_correct_type': '1',
            'is_filter_search': '0',
            'from_group_id': '',
            'offset': '0',
            'count': '10',
            'need_filter_settings': '1',
            'list_type': 'single',
            'update_version_code': '170400',
            'pc_client_type': '1',
            'version_code': '190600',
            'version_name': '19.6.0',
            'cookie_enabled': 'true',
            'screen_width': '1920',
            'screen_height': '1080',
            'browser_language': 'zh-CN',
            'browser_platform': 'Win32',
            'browser_name': 'Chrome',
            'browser_version': '126.0.0.0',
            'browser_online': 'true',
            'engine_name': 'Blink',
            'engine_version': '126.0.0.0',
            'os_name': 'Windows',
            'os_version': '10',
            'cpu_core_num': '16',
            'device_memory': '8',
            'platform': 'PC',
            'downlink': '10',
            'effective_type': '4g',
            'round_trip_time': '50',
            'webid': '7387619381264205351',
            'msToken': 'Lr1tfYiOTbOpakIaBbG3gTTGKqtElcDOmhx37bUTA0ELlNp25y7wKNUY70Ya59swSZt7fFfgUCdeBaRl40nym6txkdWGUgm_jFcUySWH0dRpV3yNhj0fhOsaVo2VWg==',
        }
        #publish_time=0 0不限制7天180180天内sort_type=20综合排序1最新发布2最多点赞filter_duration 视频时长0-1 1分钟内1-5 1-5分钟内5-10000  5分钟以上

        if(keyword):
            params['keyword'] = keyword
        if(sort_type):
            params['sort_type'] = sort_type
        if(filter_duration):
            params['filter_duration'] = filter_duration
        if(publish_time):
            params['publish_time'] = publish_time
        if(offset):
            params['offset'] = offset
        if(count):
            params['count'] = count
        if(search_id):
            params['search_id'] = search_id

        #params = json.loads(data["params1"])
        # print('stp4')

        cookies = {
            '__ac_nonce': '0668618c4005119f5340d',
            '__ac_signature': '_02B4Z6wo00f01h8bUvAAAIDDw2LNRhYyjoofO1ZAAOFO4a',
            'SEARCH_RESULT_LIST_TYPE': '%22single%22',
            'ttwid': '1%7Co0FlryLLbADdey5T-oKIiep8pw9a58UVFTIjJ-gtLA4%7C1720064197%7Cca75a7c6c9075ef75f0b6d96a9a17aa690a13d43d86d09d45f6074ccb4bb9518',
            'x-web-secsdk-uid': 'a250ab50-550a-48ec-becb-d5038d3d6b29',
            'stream_player_status_params': '%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22',
            'device_web_cpu_core': '16',
            'device_web_memory_size': '8',
            'architecture': 'amd64',
            'publish_badge_show_info': '%221%2C%22',
            'my_rd': '2',
            'FOLLOW_LIVE_POINT_INFO': '%22MS4wLjABAAAAYhICYl8ryfLoHHiivyLLMuU-3bfJMAe6qqrmpY7V3kToJXReFKoklOsST1qETZk9%2F1720108800000%2F0%2F1720064245191%2F0%22',
            'passport_csrf_token': 'f78d99693de3a7f1fbd2a5d8dc1d7d8b',
            'passport_csrf_token_default': 'f78d99693de3a7f1fbd2a5d8dc1d7d8b',
            'sso_uid_tt': 'c7ec5b3e12cc561e081535d84bc11e6a',
            'sso_uid_tt_ss': 'c7ec5b3e12cc561e081535d84bc11e6a',
            'toutiao_sso_user': '897ca17053846bf58f221a77eb53aaaa',
            'toutiao_sso_user_ss': '897ca17053846bf58f221a77eb53aaaa',
            'sid_ucp_sso_v1': '1.0.0-KDA4M2FlNGUxZGI1MzliOGM1ZjZkY2ZmZDZhMDliZjI2NTZkNDlmN2EKCRDysZi0BhjvMRoCbGYiIDg5N2NhMTcwNTM4NDZiZjU4ZjIyMWE3N2ViNTNhYWFh',
            'ssid_ucp_sso_v1': '1.0.0-KDA4M2FlNGUxZGI1MzliOGM1ZjZkY2ZmZDZhMDliZjI2NTZkNDlmN2EKCRDysZi0BhjvMRoCbGYiIDg5N2NhMTcwNTM4NDZiZjU4ZjIyMWE3N2ViNTNhYWFh',
            'odin_tt': 'a015f33f1a9ef23a98f1ba6766b64ad38063f685130fc12938b7aeddb3b158c2',
            'sid_guard': 'a116e791c5c77b3bf462d5f59cbf6263%7C1720064242%7C21600%7CThu%2C+04-Jul-2024+09%3A37%3A22+GMT',
            'uid_tt': '8fa5210b38176a6ee0968f61541e15fd',
            'uid_tt_ss': '8fa5210b38176a6ee0968f61541e15fd',
            'sid_tt': 'a116e791c5c77b3bf462d5f59cbf6263',
            'sessionid': 'a116e791c5c77b3bf462d5f59cbf6263',
            'sessionid_ss': 'a116e791c5c77b3bf462d5f59cbf6263',
            'sid_ucp_v1': '1.0.0-KGJjNDA4NzBkMzc5ZDU0ZmFiMGUxNzY0NjBjMjA5ZDBmOTEyYWVlOGIKCBDysZi0BhgNGgJscSIgYTExNmU3OTFjNWM3N2IzYmY0NjJkNWY1OWNiZjYyNjM',
            'ssid_ucp_v1': '1.0.0-KGJjNDA4NzBkMzc5ZDU0ZmFiMGUxNzY0NjBjMjA5ZDBmOTEyYWVlOGIKCBDysZi0BhgNGgJscSIgYTExNmU3OTFjNWM3N2IzYmY0NjJkNWY1OWNiZjYyNjM',
            'UIFID_TEMP': '3c3e9d4a635845249e00419877a3730e2149197a63ddb1d8525033ea2b3354c241393d868f95548dd290c26c84fa8787604ddd1211f3d0efa25450721b2351d6b090504d4eadc8f258b93f38a67555c1d680b7f494d3146a3d0ef2704a05dc209a69facf5a1f7e73caa9147d54debaad',
            'dy_swidth': '1920',
            'dy_sheight': '1080',
            'stream_recommend_feed_params': '%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22',
            'csrf_session_id': 'b9d30736d2d0c635b7566167c1e1779f',
            'fpk1': 'U2FsdGVkX19HhaFbwlg0GePbxuqHJfX2OdeOZ1TkZck6RhXurOn+A6Yfk7iCYvPaKPORyVWJRkqdJDEyjs9hHg==',
            'fpk2': 'f1f6b29a6cc1f79a0fea05b885aa33d0',
            'bd_ticket_guard_client_data': 'eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQUp1UDNFa1p2bnE5dmNBR0gvYlNtSUtQM3B1R2gzbGx1bGtMdkkvcHlmUE10OEtzMUUyUVNWLzFBOXRRVTRzQjRPYTNVNkVQOFQ4ZExud1h5ZEtobEk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D',
            'bd_ticket_guard_client_web_domain': '2',
            'biz_trace_id': '09f24ce3',
            's_v_web_id': 'verify_ly6puls7_Nbl4e9BE_QnUp_4Ebv_BM40_391OsTET46Zy',
            'FORCE_LOGIN': '%7B%22videoConsumedRemainSeconds%22%3A180%7D',
            'home_can_add_dy_2_desktop': '%221%22',
            'IsDouyinActive': 'true',
        }

        #cookies = json.loads(data["cookies1"])

        # print('stp3')

        new_params = urllib.parse.urlencode(params)
        # get请求

        # print('stp5')

        try:
            params['a_bogus'] = read_jscode(r'C:/main.js', 'fn', new_params)
            print(params['keyword'])
            # requests.get设置超时时间,timeout的单位
            surl = 'https://www.douyin.com/aweme/v1/web/general/search/single/'
            response = requests.get(surl, params=params, headers=headers, timeout=9)
            # raw_data = response.text
            response.encoding = 'utf-8'
            info = response.text
            #print(response.text)
        except Exception as e:
            print(e)

        return info
    except Exception as e:
        print(e)
        return f"ERROR :{e}"
    finally:
        print('')


if __name__ == '__main__':
    # number = 600
    # testgo()
    app.run(debug=True, host='0.0.0.0', port=8070)
    # app.run(debug=True, host='127.0.0.1', port=8080)
    # app.run(debug=True)

