import os
import sys

CONNECTED = False
if getattr(sys, 'frozen', False):
    WORKING_PATH = os.path.dirname(sys.executable)
else:
    WORKING_PATH = os.path.dirname(os.path.abspath(__file__))
MINECRAFT_PATH = os.path.join(WORKING_PATH, ".minecraft")
APPDATA_PATH = os.getenv('APPDATA')
DEBUG = True