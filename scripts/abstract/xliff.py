from collections import defaultdict
from scripts.abstract.config import MyConfig
import glob
from scripts.abstract.terms import Termlist
from typing import List, Tuple, Optional, Any
import xml.etree.ElementTree as ET


class XliffLogger():
    def __init__(self) -> None:
        self.lockedseg: defaultdict[str, int] = defaultdict(int)
        self.suggestseg: defaultdict[str, int] = defaultdict(int)
        self.unlockseg: defaultdict[str, int] = defaultdict(int)

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


class XmlSpec():
    def __init__(self, prefix: str, url: str) -> None:
        self.prefix = prefix
        self.url = url
        pass


class XliffHandler():
    def __init__(self) -> None:
        self.config: MyConfig = MyConfig()
        self.tb: Termlist = Termlist()

        self.spec: XmlSpec = XmlSpec()

        # ログ出力用の辞書
        self.log = XliffLogger()

        # 粗解析用のtxtファイルのための辞書
        self.alltext: defaultdict[str, int] = defaultdict(int)

        self.overwrite_xliff = False

    def display_config(self) -> None:
        self.config.display_config()

    def read_terms(self, path: str) -> None:
        self.tb.set_langs(
            self.config.src_lang, self.config.tgt_lang)
        files = glob.glob(f"{path}/*")
        self.tb.read_tbs(files)


    def write_log(self) -> None:
        self.log.write_log()

    def walker(self, element: ET.Element) -> None:
        """再帰的にXML要素を処理する関数"""
        for child in element:
            # 子要素に対して何らかの処理を行う
            self.process_element(child)
            # 再帰的に子要素を処理
            self.walker(child)

    def process_element(self, element: ET.Element) -> None:
        """要素ごとの処理を行うメソッド"""
        # ここに要素に対する処理を実装
        pass

    def load_plugin(self, plugin_name: str) -> Any:
        """プラグインを動的にインポートするメソッド"""
        module = __import__(plugin_name)
        return module.PluginClass()  # プラグインのクラス名を適宜変更

    def get_xlifflist(self) -> List[str]:
        print("Please use this class as a Superclass")
        return []


    def exec_parse(self) -> None:
        super.exec_prase()
        # ファイルリストの取得
        xliffs = self.get_xlifflist()
        if len(xliffs) == 0:
            print("NO xliff file in 'source' directory")
            eof = input("(type any key to exit)")
            exit()

        print("start analysis: {} files".format(len(xliffs)))

        # 名前空間の設定
        ET.register_namespace(self.spec.prefix, self.spec.url)

        # 処理の開始
        for xliff in xliffs:
            print(f"PROCESSING: {xliff}")
            xmlroot = ET.ElementTree()
            xmlroot.parse(xliff)
            self.walker(xmlroot.getroot())  # ルート要素からwalkerを開始

        # xliffを保存する
        if self.overwrite_xliff:
            self.write_xliff(xliff, xmlroot)


    def write_xliff(self, xliff: str, xmlroot: ET.ElementTree):
        filename = xliff.replace("\\", "/").split("/")[-1]
        xmlroot.write(f"{self.config.result}{filename}",
                        encoding="utf-8", default_namespace=None)

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

