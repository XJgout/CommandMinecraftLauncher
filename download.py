import json
import os
import shutil
import socket

import requests
import const
import threading
import urllib3
import time

from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

threads = []
futures = []

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def download_assets(version):
    with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
        version_json = json.loads(f.read())
    if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\indexes"):
        os.makedirs(const.MINECRAFT_PATH + "\\assets\\indexes")
    if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\objects"):
        os.makedirs(const.MINECRAFT_PATH + "\\assets\\objects")
    download_file_print(version_json["assetIndex"]["url"], version_json["assetIndex"]["id"] + ".json", const.MINECRAFT_PATH + "\\assets\\indexes\\")
    with open(const.MINECRAFT_PATH + "\\assets\\indexes\\" + version_json["assetIndex"]["id"] + ".json", "r") as f:
        version_assets_manifest = json.loads(f.read())
    with ThreadPoolExecutor() as executor:
        for assets in version_assets_manifest["objects"]:
            if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2]):
                os.makedirs(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2])
            if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2] + "\\" + version_assets_manifest["objects"][assets]["hash"]):
                futures.append(executor.submit(download_file_print, f"https://resources.download.minecraft.net/{version_assets_manifest['objects'][assets]['hash'][:2]}/{version_assets_manifest['objects'][assets]['hash']}", version_assets_manifest["objects"][assets]["hash"], const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2] + "\\"))
            else:
                print("文件存在 " + f"https://resources.download.minecraft.net/{version_assets_manifest['objects'][assets]['hash'][:2]}/{version_assets_manifest['objects'][assets]['hash']}")

        for future in futures:
            future.result()

def download_libraries(version):
    with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
        version_json = json.loads(f.read())
    if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\"):
        os.makedirs(const.MINECRAFT_PATH + "\\libraries\\")
    with ThreadPoolExecutor() as executor:
        for libraries in version_json["libraries"]:
            if "rules" in libraries:
                for rule in libraries["rules"]:
                    if "action" in rule and rule["action"] == "allow" and "os" in rule and rule["os"]["name"] == "windows":
                        if not "native" in libraries["downloads"]["artifact"]["path"]:
                            if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\"):
                                os.makedirs(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\", exist_ok=True)
                            if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + libraries["downloads"]["artifact"]["path"]):
                                futures.append(executor.submit(download_file_print, libraries["downloads"]["artifact"]["url"], libraries["downloads"]["artifact"]["path"].split("/")[-1], const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\"))
                            else:
                                print("文件存在 " + libraries["downloads"]["artifact"]["url"])
            else:
                if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\"):
                    if not "native" in libraries["downloads"]["artifact"]["path"]:
                        os.makedirs(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\", exist_ok=True)
                if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + libraries["downloads"]["artifact"]["path"]):
                    if not "native" in libraries["downloads"]["artifact"]["path"]:
                        futures.append(executor.submit(download_file_print, libraries["downloads"]["artifact"]["url"], libraries["downloads"]["artifact"]["path"].split("/")[-1], const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\"))
                else:
                    print("文件存在 " + libraries["downloads"]["artifact"]["url"])

        for future in futures:
            future.result()

def download_version_jar(version):
    with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
        version_json = json.loads(f.read())
    if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\"):
        os.makedirs(const.MINECRAFT_PATH + "\\versions\\")
    os.makedirs(const.MINECRAFT_PATH + f"\\versions\\{version}\\", exist_ok=True)
    if not os.path.exists(const.MINECRAFT_PATH + f"\\versions\\{version}\\{version}.jar"):
        download_file_print(version_json["downloads"]["client"]["url"], f"{version}.jar", const.MINECRAFT_PATH + f"\\versions\\{version}\\")
    else:
        print("文件存在 " + version_json["downloads"]["client"]["url"])
    shutil.copy2(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json", const.MINECRAFT_PATH + f"\\versions\\{version}\\{version}.json")

def download_file(url, filename, path):
    response = requests.get(url, stream=True, verify=False)
    with open(path + filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def download_file_print(url, filename, path):
    print(f"正在下载 {url}...")
    response = requests.get(url, stream=True, verify=False)
    with open(path + filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print(f"下载完成 {url}...")

def download_version(answer):
    os.system("cls")
    for i in [download_assets, download_libraries, download_version_jar]:
        t = threading.Thread(target=i, args=(answer,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    os.system("cls")
    print("所有文件均已下载完成")
    time.sleep(3)