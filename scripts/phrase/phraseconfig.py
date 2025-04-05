import os
import re


class MyConfig():
    def __init__(self):
        self.mode = "ALL"
        self.phase = ""
        self.border = .0
        self.skip = 0
        self.to_lock = True
        self.exclusion = None  # 正規表現
        self.source = "./source/"
        self.result = "./result/"
        self.log = "./log/"
        self.keys = {
            "mode": "MODE:",
            "phase": "PHASE:",
            "border": "BORDER:",
            "skip": "SKIP:",
            "to_lock": "LOCK:",
            "exclusion": "EXCLUSION:",
            "tb_src": "TBX_SOURCE:",
            "tb_tgt": "TBX_TARGET:",
            "mt": "MT_ENGINE:",
            "mt_user": "MT_USERNAME:",
            "mt_pw": "MT_PASSWORD:",
            "mt_source": "MT_SOURCE:",
            "mt_target": "MT_TARGET:",
            "mt_domain": "MT_DOMAIN:"
        }
        self.tbx = {
            "src_lang": "ja",
            "tgt_lang": "zh-cn"
        }
        self.mt = {
            "engine": "",
            "user": "",
            "pw": "",
            "src": "",
            "tgt": "",
            "domain": "medical",
        }

    def read_config(self, path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith(self.keys["mode"]):
                    mode = line.replace(self.keys["mode"], "").strip().upper()
                    if mode == "MT":
                        self.mode = "MT"
                    elif mode == "REPLACE":
                        self.mode = "REPLACE"
                    else:
                        self.mode = "ALL"
                elif line.startswith(self.keys["phase"]):
                    self.phase = line.replace(self.keys["phase"], "").strip()
                elif line.startswith(self.keys["border"]):
                    self.border = float(line.replace(
                        self.keys["border"], "").strip())
                elif line.startswith(self.keys["skip"]):
                    self.skip = line.replace(self.keys["skip"], "").strip()
                elif line.startswith(self.keys["to_lock"]):
                    self.to_lock = line.replace(
                        self.keys["to_lock"], "").strip() == "True"
                elif line.startswith(self.keys["exclusion"]):
                    e = line.replace(self.keys["exclusion"], "").strip()
                    self.exclusion = re.compile(e)

                elif line.startswith(self.keys["tb_src"]):
                    self.tbx["src_lang"] = line.replace(
                        self.keys["tb_src"], "").strip()
                elif line.startswith(self.keys["tb_tgt"]):
                    self.tbx["tgt_lang"] = line.replace(
                        self.keys["tb_tgt"], "").strip()

                elif line.startswith(self.keys["mt"]):
                    self.mt["engine"] = line.replace(
                        self.keys["mt"], "").strip().upper()
                elif line.startswith(self.keys["mt_user"]):
                    self.mt["user"] = line.replace(
                        self.keys["mt_user"], "").strip()
                elif line.startswith(self.keys["mt_pw"]):
                    self.mt["pw"] = line.replace(
                        self.keys["mt_pw"], "").strip()
                elif line.startswith(self.keys["mt_source"]):
                    self.mt["src"] = line.replace(
                        self.keys["mt_source"], "").strip()
                elif line.startswith(self.keys["mt_target"]):
                    self.mt["tgt"] = line.replace(
                        self.keys["mt_target"], "").strip()
                elif line.startswith(self.keys["mt_domain"]):
                    self.mt["domain"] = line.replace(
                        self.keys["mt_domain"], "").strip()

    def display_config(self):
        print("---BASIC---")
        print(f"MODE: {self.mode}")
        print(f"PHASE: {self.phase}")
        print(f"BORDER: {self.border}")
        print(f"SKIP: {self.skip}")
        print(f"LOCK: {self.to_lock}")
        print(f"EX: {self.exclusion}")
        print("---DIRECTORIES---")
        print(f"SOURCE: {self.source}")
        print(f"RESULT: {self.result}")
        print("--TBX---")
        print(f"SOURCE: {self.tbx['src_lang']}")
        print(f"TARGET: {self.tbx['tgt_lang']}")
        if self.mode == "MT" or self.mode == "ALL":
            print("---MT---")
            print(f"ENGINE: {self.mt['engine']}")
            print(f"USER NAME: {self.mt['user']}")
            print(f"PASSWORD: {self.mt['pw']}")
            print(f"SOURCE: {self.mt['src']}")
            print(f"TARGET: {self.mt['tgt']}")

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
