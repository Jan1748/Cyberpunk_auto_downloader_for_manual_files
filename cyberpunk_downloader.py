import math
import os
import threading
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
    path = 'Cyberpunk_2077'
    if check_cookie(url=url, installer_base=installer_base, gog_al_cookie=gog_al_cookie):
        thread_amount = int(input('How many files to download at the same time? (Ca. 20 Mb per file)'))
        Path(path).mkdir(parents=True, exist_ok=True)
        files_in_directory = os.listdir(path)
        print('Start downloading Game files')
        download_all_files(url=url, installer_base=installer_base, gog_al_cookie=gog_al_cookie, thread_amount=thread_amount, files_in_directory=files_in_directory, path=path)  # Download Game Files
        print('All Game Installer Downloaded')
        print('Start downloading Patch files')
        download_all_files(url=url, installer_base=patch_base, gog_al_cookie=gog_al_cookie, thread_amount=thread_amount, files_in_directory=files_in_directory, path=path)  # Download Patch Files
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


def get_download_file_url(url, gog_al_cookie):
    cookies = {'csrf': 'true', 'gog-al': gog_al_cookie}
    r = requests.get(url=url, cookies=cookies)
    download_url = r.url
    headers = {'Host': 'content-system.gog.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
               'Upgrade-Insecure-Requests': '1'}
    r = requests.get(url=download_url, headers=headers, allow_redirects=True)
    return r.url


def check_file_exists(path: str, file_name: str, files_in_directory):
    to_search = []
    if '.bin' in file_name:
        if 'patch' in file_name:
            to_search.append(file_name.split('Build')[0])
        elif 'setup' in file_name:
            to_search.append(file_name.split('build')[0])
        to_search.append('-' + file_name.split('-')[1])
    elif '.exe' in file_name:
        if 'patch' in file_name:
            to_search.append(file_name.split('Build')[0])
        elif 'setup' in file_name:
            to_search.append(file_name.split('build')[0])
        to_search.append('.exe')
    for file in files_in_directory:
        counter = 0
        for p in to_search:
            if p in file:
                counter += 1
        if counter == len(to_search):
            return True
    return False


def download_one_installer(url: str, thread_id, files_in_directory, path):
    file_name = get_file_name(url)
    if check_file_exists(path, file_name, files_in_directory):
        print(f'Thread {thread_id} File {file_name} already exists')
        return
    path +='/' + str(file_name)
    r = requests.get(url=url, stream=True)
    print(f'Thread {thread_id} Downloading: ' + file_name)
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
                    print(f'Thread {thread_id} Downloaded: {convert_size(byte_counter)}')
                if chunk:
                    f.write(chunk)
    except:
        print(f'Thread {thread_id} Internet Error waiting one min and trying again...')
        if os.path.exists(path):
            os.remove(path)
        time.sleep(60)
        download_one_installer(url, thread_id, files_in_directory, path)
    total_download_time = time.time() - download_start
    print(f'Thread {thread_id} Download completed. Total File Size: {convert_size(byte_counter)}. Total download time: {str(datetime.timedelta(seconds=total_download_time))}')


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


def download_all_files(url, installer_base, gog_al_cookie, thread_amount, files_in_directory, path):
    threads = []
    for id in range(0, thread_amount):
        threads.append(DownloadThread(id, thread_amount, gog_al_cookie, installer_base, url, files_in_directory, path))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


class DownloadThread(threading.Thread):
    def __init__(self, id, total_threads, gog_al_cookie, installer_base, url, files_in_directory, path):
        threading.Thread.__init__(self)
        self.id = id
        self.total_threads = total_threads
        self.gog_al_cookie = gog_al_cookie
        self.installer_base = installer_base
        self.url = url
        self.files_in_directory = files_in_directory
        self.path = path

    def run(self):
        print(f'Thread {self.id} started')
        installer_nr = self.id
        while True:
            installer_url = self.url + str(self.installer_base) + str(installer_nr)
            file_download_url = get_download_file_url(url=installer_url, gog_al_cookie=self.gog_al_cookie)
            installer_nr += self.total_threads
            if 'cdn-hw.gog.com/secure/offline' not in file_download_url:
                print(f'Thread {self.id} No File Download url')
                break
            elif 'patch' in file_download_url and 'Build' not in file_download_url:
                print(f'Thread {self.id} Found GOG Patch')
                continue
            download_one_installer(url=file_download_url, thread_id=self.id, files_in_directory=self.files_in_directory, path=self.path)
        print(f'Thread {self.id} finished')


start_download()
