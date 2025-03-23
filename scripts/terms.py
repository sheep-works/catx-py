import xml.etree.ElementTree as ET

# 変換用の用語集のためのクラス


class Termpair():
    def __init__(self, s, t):
        self.s = s.rstrip()
        self.t = t.rstrip()
        self.l = len(s)

    def get_tsv_line(self):
        return f"{self.s}\t{self.t}"


class Termlist():
    def __init__(self):
        self.src_lang = "ja"
        self.tgt_lang = "zh"
        self.tb = []
        self.tb_attr = "{http://www.w3.org/XML/1998/namespace}lang"

    def set_langs(self, src_lang, tgt_lang):
        if src_lang != "":
            self.src_lang = src_lang
        if tgt_lang != "":
            self.tgt_lang = tgt_lang

    def read_tbs(self, paths):
        for path in paths:
            self.read_tb(path)

        self.tb_sort()

    def read_tb(self, path: str):
        if path.endswith("txt"):
            pass
        elif path.endswith("tsv"):
            with open(path, "r", encoding="utf-8") as f:
                terms = self.read_from_plaintext(f.readlines())
                if len(terms) > 0:
                    self.tb += terms
        elif path.endswith("csv"):
            with open(path, "r", encoding="utf-8") as f:
                terms = self.read_from_plaintext(f.readlines(), ",")
                if len(terms) > 0:
                    self.tb += terms
        elif path.endswith("tbx"):
            terms = self.read_from_tbx(path)
            if len(terms) > 0:
                self.tb += terms
        else:
            print("invalid file path")

    # 用語集を作成するための関数

    def read_from_plaintext(self, lines: list, delimiter="/t"):
        termlist_ = []
        for line in lines:
            if line != "":
                terms = line.strip().split("\t")
                if len(terms) < 2:
                    continue
                else:
                    termlist_.append(Termpair(terms[0], terms[1]))
        return termlist_

    def read_from_tbx(self, path: str):
        termlist_ = []
        if self.src_lang == "" or self.tgt_lang == "":
            return []
        else:
            xmlroot = ET.ElementTree()
            xmlroot.parse(path)
            root = xmlroot.getroot()
            body = root[0].find("body")
            for entry in body.iterfind("termEntry"):
                st = ""
                tt = ""
                for langset in entry.iterfind("langSet"):
                    lang = langset.attrib[self.tb_attr]
                    if lang == self.src_lang:
                        tig = langset.find("tig")
                        st = tig.find("term").text

                    elif lang == self.tgt_lang:
                        tig = langset.find("tig")
                        tt = tig.find("term").text

                if st != "" and tt != "":
                    termlist_.append(Termpair(st, tt))
            return termlist_

    def tb_sort(self):
        self.tb = sorted(self.tb, key=lambda x: x.l, reverse=True)

    def export_tsv(self):
        termlist = []
        for term in self.tb:
            termlist.append(term.get_tsv_line())


if __name__ == "__main__":
    tb = Termlist()
    tb.read_tb("./configs/tb.tsv")
    tb.export_tsv()
