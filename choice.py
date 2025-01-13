import json
import os
import const
import download
import shutil
import launcher
from datetime import datetime, timedelta

def first_init_choice():
    if download.is_connected():
        const.CONNECTED = True
    else:
        const.CONNECTED = False
    os.system("cls")
    if not const.CONNECTED:
        input("哎呀，似乎好像没联网呢，已进入离线模式")
    shutil.rmtree(const.APPDATA_PATH + "\\CML\\versions_json", ignore_errors=True)

    os.makedirs(const.APPDATA_PATH + "\\CML\\versions_json", exist_ok=True)

    os.makedirs(const.APPDATA_PATH + "\\CML\\versions_libraries", exist_ok=True)

    if not os.path.exists(const.APPDATA_PATH + "\\CML\\ok"):
        input("我们检测到您是第一次启动本程序, 需要初始化配置, 请尽量不要将本程序放置在temp目录或downloads等系统级目录, 我们将要在此目录创建.minecraft文件夹, 若没有做到这一点, 您随时可以退出, 请按任意键继续。")
        answer = input("是否进行初始化配置？(y/N)\n")
        if answer == "y" or answer == "Y":
            os.makedirs(const.APPDATA_PATH + "\\CML", exist_ok=True)
            with open(const.APPDATA_PATH + "\\CML\\ok", "w") as f:
                f.write("ok")
            if not os.path.exists(const.APPDATA_PATH + "\\CML\\config.json"):
                with open(const.APPDATA_PATH + "\\CML\\config.json", "w") as f:
                    f.write("{}")
            os.makedirs(const.WORKING_PATH + "\\.minecraft", exist_ok=True)
        else:
            exit()
    else:
        return

def launch_menu():
    os.system("cls")
    version_id_list = []
    for version in os.listdir(const.MINECRAFT_PATH + "\\versions"):
        version_id_list.append(version)

    print(version_id_list)
    answer = input("请选择要启动的版本, 或者随便输入任意字符以退出:\n")
    if answer in version_id_list:
        username = input("输入您的用户名, 或者不输入任何内容直接回车退出:\n")
        if not username:
            main_menu()
        java = input("输入您的Java路径(带java.exe), 或者不输入任何内容直接回车退出:\n")
        if not java:
            main_menu()
        launcher.launch(answer, username, java)
    else:
        main_menu()

def custom_download_version_menu():
    version_id_list = []
    os.system("cls")
    with open(const.APPDATA_PATH + "\\CML\\version_manifest.json", "r") as f:
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
        download.download_file(version_manifest["versions"][version_id_list.index(answer)]["url"], f"{answer}.json", const.APPDATA_PATH + "\\CML\\versions_json\\", None, None, False)
        download.download_version(answer)
    else:
        download_menu()


def download_menu():
    os.system("cls")
    if const.CONNECTED:
        download.download_file("https://piston-meta.mojang.com/mc/game/version_manifest.json", "version_manifest.json", const.APPDATA_PATH + "\\CML\\", None, None, False)
    else:
        input("您正处于离线模式, 无法获取版本列表")
        main_menu()
    answer = input("1.下载最新正式版\n2.下载最新测试版\n3.下载自定义版本\n4.退出\n请输入您想选择的序号:\n")
    match answer:
        case "1":
            version_id_list = []
            with open(const.APPDATA_PATH + "\\CML\\version_manifest.json", "r") as f:
                version_manifest = json.loads(f.read())
            latest_version = version_manifest["latest"]["release"]
            for version in version_manifest["versions"]:
                version_id_list.append(version["id"])
            download.download_file(version_manifest["versions"][version_id_list.index(version_manifest["latest"]["release"])]["url"], f"{latest_version}.json", const.APPDATA_PATH + "\\CML\\versions_json\\", None, None, False)
            download.download_version(version_manifest["latest"]["release"])
        case "2":
            version_id_list = []
            with open(const.APPDATA_PATH + "\\CML\\version_manifest.json", "r") as f:
                version_manifest = json.loads(f.read())
            latest_version = version_manifest["latest"]["snapshot"]
            for version in version_manifest["versions"]:
                version_id_list.append(version["id"])
            download.download_file(version_manifest["versions"][version_id_list.index(version_manifest["latest"]["snapshot"])]["url"],f"{latest_version}.json", const.APPDATA_PATH + "\\CML\\versions_json\\", None, None, False)
            download.download_version(version_manifest["latest"]["snapshot"])
        case "3":
            custom_download_version_menu()
        case "4":
            main_menu()
        case _:
            download_menu()
    download_menu()



def main_menu():
    os.system("cls")
    answer = input("1.下载\n2.启动\n3.设置\n4.退出\n请输入您想选择的序号:\n")
    match answer:
        case "1":
            download_menu()
        case "2":
            launch_menu()
        case "3":
            pass
        case "4":
            os.system("cls")
            exit()
        case _:
            main_menu()