import os
import re
import json
import glob
from typing import List

class MyConfig():
    def __init__(self, path=""):
        # self.mode = "ALL"
        # self.border = .0
        # self.skip = 0
        self.path = path
        self.source = "./source/"
        self.extension = ".xliff"
        self.result = "./result/"
        self.log = "./log/"
        self.src_lang = "zh-cn"
        self.tgt_lang = "ja"
        self.files: List[str] = []
        self.custom = {}
        if path == "":
            confpath = os.path.join(self.source, "config.json")
            if glob.glob(confpath):
                self.path = confpath
        self._read_config(path)
        self._set_filelist()
        
    def _read_config(self):
        if self.path.ednsWith(".json"):
            f = open(self.path, "r", encoding="utf-8")
            self.custom = json.loads(f.read())
            f.close()
            self._overwrite()
        else:
            return
            
    def _overwrite(self):
        for key in list(vars(self).keys()):
            if key == "custom":
                pass
            elif self.custom.get(key):
                self[key] = self.custom[key]

    def write(self):
        path = self.path.replace(".json", "_rev.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(vars(self), f, ensure_ascii=False, indent=4)

    def _set_filelist(self):
        filepath = os.path.join(self.source, f"*{self.extension}")
        self.files = glob.glob(filepath)


    def check_dirs(self):
        # 書き出しフォルダがなければ作成しておく
        if not os.path.exists("./result/"):
            print("Created a directory 'result'")
            os.makedirs("./result/")
        if not os.path.exists("./log/"):
            print("Created a directory 'log'")
            os.makedirs("./log/")
        if not os.path.exists():
            os.makedirs("./source/")
            print("Please set xliff files in 'source' directory")
