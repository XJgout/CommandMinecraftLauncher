import json
import os
import shutil
import socket
import time

import requests
import const
import threading

threads = []

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def download_assets(version):
    # with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
    #     version_json = json.loads(f.read())
    print("Assets downloading...")
    time.sleep(6)
    print("Assets downloaded.")

def download_libraries(version):
    print("Libraries downloading...")
    time.sleep(4)
    print("Libraries downloaded.")

def download_version_jar(version):
    print("版本文件下载中")
    with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
        version_json = json.loads(f.read())
    if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\"):
        os.makedirs(const.MINECRAFT_PATH + "\\versions\\")
    os.makedirs(const.MINECRAFT_PATH + f"\\versions\\{version}\\", exist_ok=True)
    download_file(version_json["downloads"]["client"]["url"], f"{version}.jar", const.MINECRAFT_PATH + f"\\versions\\{version}\\")
    shutil.copy2(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json", const.MINECRAFT_PATH + f"\\versions\\{version}\\{version}.json")
    print("版本文件下载完成")

def download_file(url, filename, path):
    response = requests.get(url, stream=True)
    with open(path + filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def download_version(answer):
    for i in [download_assets, download_libraries, download_version_jar]:
        t = threading.Thread(target=i, args=(answer,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()