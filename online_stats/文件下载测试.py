import requests

def download_with_progress(url, save_path):
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()

    # 从响应头获取文件总大小
    total = int(resp.headers.get('Content-Length', 0))
    downloaded = 0

    with open(save_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024 * 64):  # 每次 64KB
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

                if total > 0:
                    percent = downloaded / total * 100
                    print(f'\r下载进度：{percent:.1f}%  ({downloaded}/{total} bytes)', end='', flush=True)

    print(f'\n下载完成！已保存到 {save_path}')

download_with_progress('http://127.0.0.1:5003/api/v1/download/3', './update.apk')
