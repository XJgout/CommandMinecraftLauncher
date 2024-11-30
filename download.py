import json
import os
import shutil
import socket

import requests
import const
import threading
import urllib3
import time

import platform

import zipfile

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
    download_file(version_json["assetIndex"]["url"], version_json["assetIndex"]["id"] + ".json", const.MINECRAFT_PATH + "\\assets\\indexes\\", None, None, True, False)
    with open(const.MINECRAFT_PATH + "\\assets\\indexes\\" + version_json["assetIndex"]["id"] + ".json", "r") as f:
        version_assets_manifest = json.loads(f.read())
    with ThreadPoolExecutor() as executor:
        for assets in version_assets_manifest["objects"]:
            if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2]):
                os.makedirs(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2])
            if not os.path.exists(const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2] + "\\" + version_assets_manifest["objects"][assets]["hash"]):
                futures.append(executor.submit(download_file, f"https://resources.download.minecraft.net/{version_assets_manifest['objects'][assets]['hash'][:2]}/{version_assets_manifest['objects'][assets]['hash']}", version_assets_manifest["objects"][assets]["hash"], const.MINECRAFT_PATH + "\\assets\\objects\\" + version_assets_manifest["objects"][assets]["hash"][:2] + "\\", None, None, True, False))
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
        libraries_in_windows = True
        for libraries in version_json["libraries"]:
            if "rules" in libraries:
                for rule in libraries["rules"]:
                    if "action" in rule and rule["action"] == "disallow":
                        if rule["os"]["name"] != "windows":
                            libraries_in_windows = True
                        else:
                            libraries_in_windows = False
                    else:
                        libraries_in_windows = True

            if "linux" in libraries["name"] or "osx" in libraries["name"] or "unix" in libraries["name"]:
                libraries_in_windows = False

            if libraries_in_windows:
                if "classifiers" in libraries["downloads"]:
                    if libraries["downloads"]["classifiers"].get("natives-windows", None) is not None:
                        if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\"):
                            os.makedirs(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\", exist_ok=True)
                        if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["path"])):
                            futures.append(executor.submit(download_file, libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["url"], os.path.basename(libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["path"]), const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\", version, libraries, True, True))
                        else:
                            print("文件存在 " + libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["url"])
                if "artifact" in libraries["downloads"]:
                    if not "natives" in libraries["name"]:
                        if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\"):
                            os.makedirs(const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\", exist_ok=True)
                        if not os.path.exists(const.MINECRAFT_PATH + "\\libraries\\" + libraries["downloads"]["artifact"]["path"]):
                            futures.append(executor.submit(download_file, libraries["downloads"]["artifact"]["url"], os.path.basename(libraries["downloads"]["artifact"]["path"]), const.MINECRAFT_PATH + "\\libraries\\" + "/".join(libraries["downloads"]["artifact"]["path"].split("/")[:-1]) + "\\", None, None, True, False))
                        else:
                            print("文件存在 " + libraries["downloads"]["artifact"]["url"])
                    else:
                        if "windows" in libraries["name"]:
                            if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\"):
                                os.makedirs(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\", exist_ok=True)
                            if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["artifact"]["path"])):
                                futures.append(executor.submit(download_file, libraries["downloads"]["artifact"]["url"], os.path.basename(libraries["downloads"]["artifact"]["path"]), const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\", version, libraries, True, True))
                            else:
                                print("文件存在 " + libraries["downloads"]["artifact"]["url"])
        for future in futures:
            future.result()
            shutil.rmtree(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + "windows", ignore_errors=True)
            shutil.rmtree(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + "META-INF", ignore_errors=True)
            for root, dirs, files in os.walk(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\"):
                for file in files:
                    if '.' not in file:
                        os.remove(os.path.join(root, file))

def download_version_jar(version):
    with open(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json") as f:
        version_json = json.loads(f.read())
    if not os.path.exists(const.MINECRAFT_PATH + "\\versions\\"):
        os.makedirs(const.MINECRAFT_PATH + "\\versions\\")
    os.makedirs(const.MINECRAFT_PATH + f"\\versions\\{version}\\", exist_ok=True)
    if not os.path.exists(const.MINECRAFT_PATH + f"\\versions\\{version}\\{version}.jar"):
        download_file(version_json["downloads"]["client"]["url"], f"{version}.jar", const.MINECRAFT_PATH + f"\\versions\\{version}\\", None, None, True, False)
    else:
        print("文件存在 " + version_json["downloads"]["client"]["url"])
    shutil.copy2(const.APPDATA_PATH + f"\\CML\\versions_json\\{version}.json", const.MINECRAFT_PATH + f"\\versions\\{version}\\{version}.json")

def download_file(url, filename, path, version, libraries, is_print=False, is_natives=False):
    if is_print:
        print(f"正在下载 {url}...")
    response = requests.get(url, stream=True, verify=False)
    with open(path + filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    if is_print:
        print(f"下载完成 {url}...")
    if is_natives:
        try:
            if "classifiers" in libraries["downloads"]:
                with zipfile.ZipFile(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["path"]), 'r') as zip_ref:
                    zip_ref.extractall(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\")
                os.remove(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["classifiers"][libraries["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["path"]))
            else:
                with zipfile.ZipFile(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["artifact"]["path"])) as zip_ref:
                    zip_ref.extractall(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\")
                os.remove(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + os.path.basename(libraries["downloads"]["artifact"]["path"]))
                for root, dirs, files in os.walk(const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\" + "windows" + "\\" + "x64" if platform.machine().endswith("64") else "x86" if "amd" in platform.machine().lower() or "x86" in platform.machine().lower() else "arm64"):
                    for file in files:
                        if file.endswith('.dll'):
                            shutil.copy2(str(os.path.join(root, file)), const.MINECRAFT_PATH + "\\versions\\" + version + "\\" + version + "-natives" + "\\")
        except Exception:
            pass

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