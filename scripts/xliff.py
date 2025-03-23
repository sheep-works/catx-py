from collections import defaultdict
from config import MyConfig
import datetime
import glob
from mthandler import ATMAN, DeepL
import re
from terms import Termlist
from typing import Tuple
import xml.etree.ElementTree as ET


class XliffHandler():
    def __init__(self):
        self.config = MyConfig()
        self.tb = Termlist()

        self.engine = None

        # ログ出力用の辞書
        self.lockedseg = defaultdict(int)
        self.suggestseg = defaultdict(int)
        self.unlockseg = defaultdict(int)

        # 粗解析用のtxtファイルのための辞書
        self.alltext = defaultdict(int)

    def read_config(self, path):
        self.config.read_config(path)

    def display_config(self):
        self.config.display_config()

    def read_terms(self, path):
        self.tb.set_langs(
            self.config.tbx["src_lang"], self.config.tbx["tgt_lang"])
        files = glob.glob(f"{path}/*")
        self.tb.read_tbs(files)

    def set_mt_engine(self) -> bool:
        if self.config.mt["engine"] == "ATMAN":
            self.engine = ATMAN()
            return self.engine.prepare(
                self.config.mt["user"], self.config.mt["pw"],
                self.config.mt["src"], "", domain=self.config.mt["domain"])
        elif self.config.mt["engine"] == "DEEPL":
            self.engine = DeepL()
            return self.engine.prepare(
                self.config.mt["user"], self.config.mt["pw"],
                self.config.mt["src"], self.config.mt["tgt"])
        else:
            return False

    def write_log(self):
        with open(f"{self.config.result}log.txt", "w", encoding="utf-8") as f:
            if self.config.exclusion is not None:
                f.write("Excluded：{}\n".format(self.config.exclusion))

            f.write("\n-----<Full Match: these segments should be locked>-----\n")

            for key, val in self.lockedseg.items():
                f.write(f"{key}\t:::{val}回\n")

            f.write(
                f"\n-----<Match over {self.config.border * 100}% these segments can be locked>-----\n")
            for key, val in self.suggestseg.items():
                f.write(f"{key}\t:::{val}回\n")

            f.write(
                "-----<Match less than border: these segments could be kept unlock>-----\n")
            for key, val in self.unlockseg.items():
                f.write(f"{key}\t:::{val}回\n")


class Mxliff(XliffHandler):
    # 定数の初期化 変更のない部分
    def __init__(self):
        super().__init__()
        self.NS = "{urn:oasis:names:tc:xliff:document:1.2}"
        self.M_NS = "http://www.memsource.com/mxlf/2.0"
        self.CONFIRM = "confirmed"
        self.LOCK = "locked"
        self.M_CONFIRM = "{" + self.M_NS + "}" + self.CONFIRM
        self.M_LOCK = "{" + self.M_NS + "}" + self.LOCK
        self.TAGS = re.compile("({[0-9^_biu]+>)|({[0-9]+})|(<[0-9^_biu]+})")
        DT = datetime.datetime.now()
        self.FILENAME = "./log/loginfo{}.txt".format(DT.strftime("%m%d%H%M"))

    def exec_parse(self):
        # ファイルリストの取得
        xliffs = glob.glob("./source/*.mxliff")
        if len(xliffs) == 0:
            print("NO mxliff file in 'source' directory")
            eof = input("(type any key to exit)")
            exit()

        print("start analysis: {} files".format(len(xliffs)))

        # 名前空間の設定
        ET.register_namespace("m", self.M_NS)

        # 処理の開始
        for xliff in xliffs:
            print(f"PROCESSING: {xliff}")
            counter = 0
            xmlroot = ET.ElementTree()
            xmlroot.parse(xliff)
            # xliffタグの下にfileタグがある。（head body よりも上位）
            # mxliffが結合されていた場合、fileタグが複数あるので、ここを起点とする
            for e_file in xmlroot.iterfind(self.NS + "file"):
                # fileタグ＞bodyタグ＞groupタグが実際に処理するべき部分
                e_groups = e_file.find(
                    self.NS + "body").findall(self.NS + "group")
                for group in e_groups:
                    counter += 1
                    if counter % 100 == 0:
                        print(f"NOW: {counter}")
                    unit = group.find(self.NS + "trans-unit")
                    if unit is None:
                        continue
                    # すでにロックされているセグメントは処理をしない
                    if unit.get(self.M_LOCK) == "true":
                        continue
                    # 原文と異なる訳文がすでに入っている場合は、TMの適用だと考えられるので処理をしない
                    st = unit.findtext(self.NS + "source")
                    tt = unit.findtext(self.NS + "target")
                    if tt != "" and st != tt:
                        continue

                    # 解析用にタグをすべて外したp_stを作る
                    p_st = self.TAGS.sub("", st)
                    # p_stの長さが0の場合、そのセグメントにはタグしか入っていないということなので、処理をしない
                    if len(p_st) == 0:
                        unit.find(self.NS + "target").text = st
                        if self.config.to_lock:
                            unit.set(self.M_CONFIRM, self.config.phase)
                            unit.set(self.M_LOCK, "true")
                    else:
                        self.alltext[p_st] += 1
                        # 置換モード
                        if self.config.mode == "REPLACE":
                            (processed, remain) = self.exec_replace(st, p_st)
                            unit.find(self.NS + "target").text = processed
                            # 置換できなかった残りが「0」の場合、タグと用語と英数字しかないことになるので、
                            # targetを置き換えて確定・ロックする
                            if self.config.to_lock:
                                if remain == 0:
                                    self.lockedseg[processed] += 1
                                    unit.set(self.M_LOCK, "true")
                                    unit.set(self.M_CONFIRM, self.config.phase)
                                elif remain <= self.config.border:
                                    self.suggestseg[processed] += 1
                                else:
                                    self.unlockseg[p_st] += 1

                        # 機械翻訳モード
                        elif self.config.mode == "MT":
                            unit.find(
                                self.NS + "target").text = self.engine.get_mt(p_st)

                        # ハイブリッドモード
                        elif self.config.mode == "ALL":
                            (processed, remain) = self.exec_replace(st, p_st)
                            # 完全に置換ができた場合は機械翻訳をしない
                            if remain == 0:
                                unit.find(self.NS + "target").text = processed
                                # 置換できなかった残りが「0」の場合、タグと用語と英数字しかないことになるので、
                                # targetを置き換えて確定・ロックする
                                if self.config.to_lock:
                                    if remain == 0:
                                        self.lockedseg[processed] += 1
                                        unit.set(self.M_LOCK, "true")
                                        unit.set(self.M_CONFIRM,
                                                 self.config.phase)
                                    elif remain <= self.config.border:
                                        self.suggestseg[processed] += 1
                                    else:
                                        self.unlockseg[p_st] += 1
                            else:
                                unit.find(
                                    self.NS + "target").text = self.engine.get_mt(p_st)

            # xmliffを保存する
            filename = xliff.replace("\\", "/").split("/")[-1]
            xmlroot.write(f"{self.config.result}{filename}",
                          encoding="utf-8", default_namespace=None)

    def exec_replace(self, st: str, p_st: str) -> Tuple:
        # タグを外したセグメントをalltextに一旦入れておく
        # 用語集で一括置換をする。
        # 実際に置換して使用する「p_st1」（タグ付き）と、削除してしまって完全一致かどうかを確認するための「p_st2」（タグなし）を作る
        p_st1 = st
        p_st2 = p_st
        for term in self.tb.tb:
            p_st1 = p_st1.replace(term.s, term.t)
            p_st2 = p_st2.replace(term.s, "")

        # 正規表現で削除を試みる
        # なぜかfindallはうまくいかないので、finditerでマッチオブジェクトを取得して処理
        if self.config.exclusion != None:
            for match in self.config.exclusion.finditer(p_st2):
                p_st2 = p_st2.replace(match.group(), "")

        # 用語集と正規表現で削除後の文字数を数える。
        remain = len(p_st2)

        return (p_st1, remain)

    def write_alltext(self):
        # その他のログファイルを保存する
        with open(f"{self.config.result}/alltext.txt", "w", encoding="utf-8") as f:
            for key, val in self.alltext.items():
                f.write("{k}\t:::{v}回\n".format(k=key, v=val))
