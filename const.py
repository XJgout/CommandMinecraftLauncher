import os

CONNECTED = False
WORKING_PATH = os.getcwd()
MINECRAFT_PATH = os.path.join(WORKING_PATH, ".minecraft")
APPDATA_PATH = os.getenv('APPDATA')
DEBUG = False