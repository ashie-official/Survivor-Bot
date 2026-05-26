import os
import json

# 1. Calculate the path to the data folder dynamically
_TOOLKIT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TOOLKIT_DIR)
_INFO_FILE_PATH = os.path.join(_ROOT_DIR, "data", "command_info.json")

with open(_INFO_FILE_PATH, "r", encoding="utf-8") as f:
    CMD_INFO = json.load(f)