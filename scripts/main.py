# Memsource XLIFF Version2.4対応型

from xliff import Mxliff

if __name__ == "__main__":
    mxliff = Mxliff()
    mxliff.read_config("./configs/init.txt")
    mxliff.display_config()
    if mxliff.config.mode == "REPLACE" or mxliff.config.mode == "ALL":
        mxliff.read_terms("./configs")
        mxliff.tb.export_tsv()
    if mxliff.config.mode == "MT" or mxliff.config.mode == "ALL":
        isMtOk = mxliff.set_mt_engine()
        if isMtOk == False:
            print("MT Engine settings are not correct")
            eof = input("(type any key to exit)")
            exit()

    mxliff.exec_parse()
    mxliff.write_alltext()
    mxliff.write_log()
    eof = input("(type any key to exit)")
    exit()
