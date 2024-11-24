import json
import os
import download
import launcher
import setting
import shutil
from datetime import datetime, timedelta

CONNECTED = False
WORKING_PATH = os.path.dirname(os.path.abspath(__file__))
APPDATA_PATH = os.getenv('APPDATA')

def first_init_choice():
    global CONNECTED
    if download.is_connected():
        CONNECTED = True
    else:
        CONNECTED = False
    os.system("cls")
    if not CONNECTED:
        input("哎呀，似乎好像没联网呢，已进入离线模式")
    shutil.rmtree(APPDATA_PATH + "\\CML\\versions_json", ignore_errors=True)

    os.makedirs(APPDATA_PATH + "\\CML\\versions_json", exist_ok=True)

    if not os.path.exists(APPDATA_PATH + "\\CML\\ok"):
        input("我们检测到您是第一次启动本程序, 需要初始化配置, 请尽量不要将本程序放置在temp目录或downloads等系统级目录, 我们将要在此目录创建.minecraft文件夹, 若没有做到这一点, 你随时可以退出, 请按任意键继续。")
        answer = input("是否进行初始化配置？(y/N)\n")
        if answer == "y" or answer == "Y":
            os.makedirs(APPDATA_PATH + "\\CML")
            with open(APPDATA_PATH + "\\CML\\ok", "w") as f:
                f.write("ok")
            if not os.path.exists(APPDATA_PATH + "\\CML\\config.json"):
                with open(APPDATA_PATH + "\\CML\\config.json", "w") as f:
                    f.write("{}")
            os.makedirs(WORKING_PATH + "\\.minecraft", exist_ok=True)
        else:
            exit()
    else:
        return


def custom_download_version_menu():
    version_id_list = []
    os.system("cls")
    with open(APPDATA_PATH + "\\CML\\version_manifest.json", "r") as f:
        version_manifest = json.loads(f.read())
        for version in version_manifest["versions"]:
            print(version["id"])
            print("|--版本类型: " + version["type"])
            print("|--更新时间: " + (datetime.fromisoformat(version["time"]) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S") + " UTC+8")
            print("|--发布时间: " + (datetime.fromisoformat(version["releaseTime"]) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S") + " UTC+8")
            print()
            version_id_list.append(version["id"])
        answer = input("请输入您想选择的版本的完整版本号, 或者随便输入任意字符以退出:\n")
        if answer in version_id_list:
            print(version_manifest["versions"][version_id_list.index(answer)]["url"])
            download.download_file(version_manifest["versions"][version_id_list.index(answer)]["url"], f"{answer}.json", APPDATA_PATH + "\\CML\\versions_json\\")
        else:
            download_menu()


def download_menu():
    os.system("cls")
    if CONNECTED:
        download.download_file("https://piston-meta.mojang.com/mc/game/version_manifest.json", "version_manifest.json", APPDATA_PATH + "\\CML\\")
    else:
        input("你正处于离线模式, 无法获取版本列表")
        main_menu()
    answer = input("1.下载最新正式版\n2.下载最新测试版\n3.下载自定义版本\n4.退出\n请输入您想选择的序号:\n")
    match answer:
        case "1":
            pass
        case "2":
            pass
        case "3":
            custom_download_version_menu()
        case "4":
            main_menu()
        case _:
            download_menu()


def main_menu():
    os.system("cls")
    answer = input("1.下载\n2.启动\n3.设置\n4.退出\n请输入您想选择的序号:\n")
    match answer:
        case "1":
            download_menu()
        case "2":
            pass
        case "3":
            pass
        case "4":
            os.system("cls")
            exit()
        case _:
            main_menu()