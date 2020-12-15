import math
import os
import urllib
import time
from pathlib import Path
import requests
import datetime


def start_download():
    gog_al_cookie = input('Input the "gog-al" Cookie value here:')
    url = 'https://www.gog.com/downloads/cyberpunk_2077_game'
    installer_base = '/en1installer'
    patch_base = '/en1patch'
    if check_cookie(url=url, installer_base=installer_base, gog_al_cookie=gog_al_cookie):
        Path("Cyberpunk_2077").mkdir(parents=True, exist_ok=True)
        print('Start downloading Game files')
        download_all_files(url=url, installer_base=installer_base, gog_al_cookie=gog_al_cookie)  # Download Game Files
        print('Start downloading Patch files')
        print('All Game Installer Downloaded')
        download_all_files(url=url, installer_base=patch_base, gog_al_cookie=gog_al_cookie)  # Download Patch Files
        print('All Patch Files')
        print('All Downloads Finished')
    else:
        print('Something went wrong with the cookie Value')
    input('Press Enter to close Console')


def check_cookie(url, installer_base, gog_al_cookie):
    installer_url = url + str(installer_base) + str(0)
    file_download_url = get_download_file_url(url=installer_url, gog_al_cookie=gog_al_cookie)
    if 'cdn-hw.gog.com/secure/offline' in file_download_url:
        return True
    else:
        return False


def download_all_files(url, installer_base, gog_al_cookie):
    installer_nr = 0
    while True:
        installer_url = url + str(installer_base) + str(installer_nr)
        file_download_url = get_download_file_url(url=installer_url, gog_al_cookie=gog_al_cookie)
        installer_nr += 1
        if 'cdn-hw.gog.com/secure/offline' not in file_download_url:
            print('No File Download url')
            break
        elif 'patch' in file_download_url and 'Build' not in file_download_url:
            print('Found GOG Patch')
            continue
        download_one_installer(url=file_download_url)


def get_download_file_url(url, gog_al_cookie):
    cookies = {'csrf': 'true', 'gog-al': gog_al_cookie}
    r = requests.get(url=url, cookies=cookies)
    download_url = r.url
    headers = {'Host': 'content-system.gog.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
               'Upgrade-Insecure-Requests': '1'}
    r = requests.get(url=download_url, headers=headers, allow_redirects=True)
    return r.url


def download_one_installer(url: str):
    file_name = get_file_name(url)
    path = 'Cyberpunk_2077/' + str(file_name)
    if os.path.exists(path):
        print(f'File {file_name} already exists')
        return
    r = requests.get(url=url, stream=True)
    print('Downloading: ' + file_name)
    byte_counter = 0
    start_time = time.time()
    download_start = start_time
    try:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                now = time.time()
                byte_counter += 8192
                if (now - start_time) >= 10:
                    start_time = now
                    print(f'Downloaded: {convert_size(byte_counter)}')
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    except:
        print('Internet Error waiting one min and trying again...')
        if os.path.exists(path):
            os.remove(path)
        time.sleep(60)
        download_one_installer(url)
    total_download_time = time.time() - download_start
    print(f'Download completed. Total File Size: {convert_size(byte_counter)}. Total download time: {str(datetime.timedelta(seconds=total_download_time))}')


def get_file_name(url):
    file_name = url.split('?')[0].split('/')
    return urllib.parse.unquote(file_name[len(file_name) - 1])


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


start_download()
