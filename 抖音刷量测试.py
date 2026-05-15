import requests

def increase_views(video_url, num_views):
    for _ in range(num_views):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(video_url, headers=headers)
        if response.status_code == 200:
            print('Successfully increased view count.')
        else:
            print('Failed to increase view count.')

# 测试代码
video_url = 'https://v.douyin.com/iUjAMYeg/'
num_views = 10
increase_views(video_url, num_views)