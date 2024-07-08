import os
pack_list = ["pymel", "ctypes", "sys", "pickle", "termcolor", "yaml", "zipfile", "shutil", "webbrowser", "subprocess", "random", "time", "tqdm", "functools", "pathlib", "watchdog", "json", "scandir",]


for pack in pack_list:
	os.system("mayapy -m pip install %s"%pack)