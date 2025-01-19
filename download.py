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
import hashlib
import sys
import logging
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG if const.DEBUG else logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

threads = []
futures = []

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def calculate_file_hash(filepath, hash_algorithm='sha1'):
    hash_func = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def download_file(url, filename, path, libraries=None, is_print=False, is_natives=False, expected_hash=None, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        if const.DEBUG and is_print:
            logging.info(f"正在下载 {url}")
        try:
            response = requests.get(url, stream=True, verify=False, timeout=10)
            with open(os.path.join(path, filename), "wb") as f:
                for chunk in response.iter_content(chunk_size=2048):
                    if chunk:
                        f.write(chunk)
            if const.DEBUG and is_print:
                logging.info(f"下载完成 {url}...")

            if expected_hash:
                file_hash = calculate_file_hash(os.path.join(path, filename))
                if file_hash != expected_hash:
                    if const.DEBUG:
                        logging.warning(f"哈希校验失败 {url}: 预期 {expected_hash}, 实际 {file_hash}")
                    attempt += 1
                    continue

            if is_natives:
                extract_natives(libraries, path, filename)
            return
        except Exception as e:
            if const.DEBUG:
                logging.error(f"下载失败 {url}: {e}")
            attempt += 1

    logging.critical(f"下载失败 {url}, 已关闭程序, 检查网络连接或稍后重试")
    sys.exit(1)

def extract_natives(libraries, path, filename):
    try:
        with zipfile.ZipFile(os.path.join(path, filename), 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(os.path.join(path, filename))
        if "classifiers" in libraries["downloads"]:
            native_path = os.path.join(path, "windows", "x64" if platform.machine().endswith("64") else "x86")
            for root, _, files in os.walk(native_path):
                for file in files:
                    if file.endswith('.dll'):
                        shutil.copy2(os.path.join(root, file), path)
            for root, dirs, files in os.walk(native_path, topdown=False):
                for file in files:
                    if not file.endswith('.dll'):
                        os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
    except Exception as e:
        if const.DEBUG:
            logging.error(f"解压失败 {filename}: {e}")

def download_assets(version):
    with open(os.path.join(const.APPDATA_PATH, f"CML\\versions_json\\{version}.json")) as f:
        version_json = json.load(f)
    ensure_directory_exists(os.path.join(const.MINECRAFT_PATH, "assets\\indexes"))
    ensure_directory_exists(os.path.join(const.MINECRAFT_PATH, "assets\\objects"))
    download_file(version_json["assetIndex"]["url"], f"{version_json['assetIndex']['id']}.json", os.path.join(const.MINECRAFT_PATH, "assets\\indexes"), is_print=True, expected_hash=version_json["assetIndex"]["sha1"])
    with open(os.path.join(const.MINECRAFT_PATH, "assets\\indexes", f"{version_json['assetIndex']['id']}.json"), "r") as f:
        version_assets_manifest = json.load(f)
    with ThreadPoolExecutor() as executor:
        for asset, details in version_assets_manifest["objects"].items():
            asset_path = os.path.join(const.MINECRAFT_PATH, "assets\\objects", details["hash"][:2])
            ensure_directory_exists(asset_path)
            if not os.path.exists(os.path.join(asset_path, details["hash"])) or calculate_file_hash(os.path.join(asset_path, details["hash"])) != details["hash"]:
                futures.append(executor.submit(download_file, f"https://resources.download.minecraft.net/{details['hash'][:2]}/{details['hash']}", details["hash"], asset_path, is_print=True, expected_hash=details["hash"]))
            else:
                if const.DEBUG:
                    logging.info(f"文件存在 https://resources.download.minecraft.net/{details['hash'][:2]}/{details['hash']}")
        for future in futures:
            future.result()

def download_libraries(version):
    libraries_list = []
    with open(os.path.join(const.APPDATA_PATH, f"CML\\versions_json\\{version}.json")) as f:
        version_json = json.load(f)
    ensure_directory_exists(os.path.join(const.MINECRAFT_PATH, "libraries"))
    with ThreadPoolExecutor() as executor:
        for library in version_json["libraries"]:
            if should_download_library(library):
                download_library_files(library, version, executor, libraries_list)
        for future in futures:
            future.result()
    with open(os.path.join(const.APPDATA_PATH, f"CML\\versions_libraries\\{version}.json"), "w+") as f:
        json.dump(libraries_list, f)
    clean_up_natives(version)

def should_download_library(library):
    if "rules" in library:
        for rule in library["rules"]:
            if rule.get("action") == "disallow" and rule["os"]["name"] == "windows":
                return False
    if any(os_name in library["name"] for os_name in ["linux", "osx", "unix"]):
        return False
    return True

def download_library_files(library, version, executor, libraries_list):
    if "classifiers" in library["downloads"]:
        try:
            native_path = os.path.join(const.MINECRAFT_PATH, "versions", version, f"{version}-natives")
            ensure_directory_exists(native_path)
            native_file = os.path.basename(library["downloads"]["classifiers"][library["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["path"])
            if not os.path.exists(os.path.join(native_path, native_file)) or calculate_file_hash(os.path.join(native_path, native_file)) != library["downloads"]["classifiers"][library["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["sha1"]:
                futures.append(executor.submit(download_file, library["downloads"]["classifiers"][library["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["url"], native_file, native_path, library, is_print=False, is_natives=True, expected_hash=library["downloads"]["classifiers"][library["natives"]["windows"].replace("${arch}", "64" if platform.machine().endswith('64') else "32")]["sha1"]))
            else:
                if const.DEBUG:
                    logging.info(f"文件存在 {library['downloads']['classifiers'][library['natives']['windows'].replace('${arch}', '64' if platform.machine().endswith('64') else '32')]['url']}")
        except KeyError:
            pass

    if "artifact" in library["downloads"]:
        artifact_path = os.path.join(const.MINECRAFT_PATH, "libraries", "/".join(library["downloads"]["artifact"]["path"].split("/")[:-1]))
        ensure_directory_exists(artifact_path)
        if not os.path.exists(os.path.join(artifact_path, os.path.basename(library["downloads"]["artifact"]["path"]))) or calculate_file_hash(os.path.join(artifact_path, os.path.basename(library["downloads"]["artifact"]["path"]))) != library["downloads"]["artifact"]["sha1"]:
            futures.append(executor.submit(download_file, library["downloads"]["artifact"]["url"], os.path.basename(library["downloads"]["artifact"]["path"]), artifact_path, is_print=False, expected_hash=library["downloads"]["artifact"]["sha1"]))
        else:
            if const.DEBUG:
                logging.info(f"文件存在 {library['downloads']['artifact']['url']}")
        libraries_list.append(library)

def clean_up_natives(version):
    native_path = os.path.join(const.MINECRAFT_PATH, "versions", version, f"{version}-natives")
    shutil.rmtree(os.path.join(native_path, "windows"), ignore_errors=True)
    shutil.rmtree(os.path.join(native_path, "META-INF"), ignore_errors=True)
    for root, _, files in os.walk(native_path):
        for file in files:
            if '.' not in file:
                os.remove(os.path.join(root, file))

def download_version_jar(version):
    with open(os.path.join(const.APPDATA_PATH, f"CML\\versions_json\\{version}.json")) as f:
        version_json = json.load(f)
    ensure_directory_exists(os.path.join(const.MINECRAFT_PATH, "versions"))
    version_path = os.path.join(const.MINECRAFT_PATH, "versions", version)
    ensure_directory_exists(version_path)
    if not os.path.exists(os.path.join(version_path, f"{version}.jar")) or calculate_file_hash(os.path.join(version_path, f"{version}.jar")) != version_json["downloads"]["client"]["sha1"]:
        download_file(version_json["downloads"]["client"]["url"], f"{version}.jar", version_path, is_print=False, expected_hash=version_json["downloads"]["client"]["sha1"])
    else:
        if const.DEBUG:
            logging.info(f"文件存在 {version_json['downloads']['client']['url']}")
    shutil.copy2(os.path.join(const.APPDATA_PATH, f"CML\\versions_json\\{version}.json"), os.path.join(version_path, f"{version}.json"))

def download_version(answer):
    os.system("cls")
    if not const.DEBUG:
        print("正在下载中...")
    for func in [download_assets, download_version_jar, download_libraries]:
        t = threading.Thread(target=func, args=(answer,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    os.system("cls")
    print("所有文件均已下载完成")
    time.sleep(3)