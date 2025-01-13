import subprocess
import os
import const
import json
import uuid
import choice
import time

def launch(answer, username, java):
    uuid_str = uuid.uuid4().hex
    jvm_argument_list = []
    with open(const.MINECRAFT_PATH + f"\\versions\\{answer}\\{answer}.json", "rb") as f:
        version_libraries_json = json.loads(f.read())
    classpath_list = [const.MINECRAFT_PATH + "\\libraries\\" + library["downloads"]["artifact"]["path"] for library in version_libraries_json["libraries"]]
    with open(const.MINECRAFT_PATH + "\\versions\\" + answer + f"\\{answer}.json", "rb") as f:
        game_version_json = json.loads(f.read())
    if "arguments" in game_version_json:
        jvm_arguments_json = game_version_json["arguments"]["jvm"]
        for jvm_argument in jvm_arguments_json:
            if isinstance(jvm_argument, str):
                jvm_argument_list.append(jvm_argument.replace("${natives_directory}", const.MINECRAFT_PATH + "\\versions\\" + answer + f"\\{answer}-natives").replace("${launcher_name}", "CML").replace("${launcher_version}", "0.0.1").replace("${classpath}", "\"" + ";".join(classpath_list)))
    else:
        jvm_argument_list.append(f"-Djava.library.path={const.MINECRAFT_PATH}\\versions\\{answer}\\{answer}-natives" + f" -cp \" {';'.join(classpath_list)}")

    game_argument_tuple = {
        '--username': username,
        '--version': answer,
        '--gameDir': const.MINECRAFT_PATH,
        '--assetsDir': const.MINECRAFT_PATH + "\\assets",
        '--assetIndex': game_version_json["assetIndex"]["id"],
        '--uuid': uuid_str,
        '--accessToken': uuid_str,
        '--userType': 'msa',
        '--versionType': 'CML'
    }

    try:
        game_argument_list = [f"{key} {value}" for key, value in game_argument_tuple.items()]
        process = subprocess.Popen(java + " " + " ".join(jvm_argument_list) + ";" + const.MINECRAFT_PATH + "\\versions\\" + answer + "\\" + answer + ".jar" + "\"" + " " + game_version_json["mainClass"] + " " + " ".join(game_argument_list), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')
        process.wait()
    except FileNotFoundError:
        os.system("cls")
        print("Java路径有误")
        time.sleep(3)
        choice.main_menu()
    choice.main_menu()