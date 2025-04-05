import re
import datetime
from xliff import XmlSpec, XliffHandler
import glob
from typing import List, Tuple, Optional, Any

class MxliffSpec(XmlSpec):
    def __init__(self):
        super().__init__(self, "m", "http://www.memsource.com/mxlf/2.0")
        self.NS: str = "{urn:oasis:names:tc:xliff:document:1.2}"
        self.CONFIRM: str = "confirmed"
        self.LOCK: str = "locked"
        self.M_CONFIRM: str = "{" + self.M_NS + "}" + self.CONFIRM
        self.M_LOCK: str = "{" + self.M_NS + "}" + self.LOCK
        self.TAGS: re.Pattern = re.compile("({[0-9^_biu]+>)|({[0-9]+})|(<[0-9^_biu]+})")
        DT = datetime.datetime.now()
        self.FILENAME: str = "./log/loginfo{}.txt".format(DT.strftime("%m%d%H%M"))


class Mxliff(XliffHandler):
    # 定数の初期化 変更のない部分
    def __init__(self) -> None:
        self.spec = MxliffSpec()

    def get_xlifflist(self) -> List[str]:
        return glob.glob("./source/*.mxliff")

    def exec_parse(self) -> None:
        super.exec_parse()

    def exec_replace(self, st: str, p_st: str) -> Tuple[str, int]:
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
        if self.config.exclusion is not None:
            for match in self.config.exclusion.finditer(p_st2):
                p_st2 = p_st2.replace(match.group(), "")

        # 用語集と正規表現で削除後の文字数を数える。
        remain = len(p_st2)

        return (p_st1, remain)

    def write_alltext(self) -> None:
        # その他のログファイルを保存する
        with open(f"{self.config.result}/alltext.txt", "w", encoding="utf-8") as f:
            for key, val in self.alltext.items():
                f.write("{k}\t:::{v}回\n".format(k=key, v=val))
