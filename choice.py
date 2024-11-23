import os

APPDATA_PATH = os.getenv('APPDATA')

def first_init_choice():
    os.system("cls")
    if not os.path.exists(APPDATA_PATH + "\\CML\\ok"):
        input("我们检测到您是第一次启动本程序, 需要初始化配置, 请尽量不要将本程序放置在temp目录或downloads等系统级目录, 若没有做到这一点, 你随时可以退出, 请按任意键继续。")
        answer = input("是否进行初始化配置？(y/N)\n")
        if answer == "y" or answer == "Y":
            os.makedirs(APPDATA_PATH + "\\CML")
            with open(APPDATA_PATH + "\\CML\\ok", "w") as f:
                f.write("ok")
            with open(APPDATA_PATH + "\\CML\\config.json", "w") as f:
                f.write("{}")
        else:
            exit()
    else:
        return


def main_menu():
    os.system("cls")
    answer = input("1.下载\n2.启动\n3.设置\n4.退出\n")
    match answer:
        case "1":
            pass
        case "2":
            pass
        case "3":
            pass
        case "4":
            exit()
        case _:
            main_menu()