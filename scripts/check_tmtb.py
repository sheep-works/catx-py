from getpass import getpass
from mthandler import ATMAN

atman = ATMAN()

user = input("Please input username: ")
pw = getpass("your password: ")

isOk = atman.prepare(user, pw, "", "")

if isOk == False:
    print("incorrect")
else:
    atman.get_config()
    # atman.get_tmtbinfo()
