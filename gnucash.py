#!/usr/bin/env python

import sys
import subprocess

def account_list():
    ACCOUNT_LIST = subprocess.check_output(['ledger', 'accounts']).split("\n")
    CURRENCY = "BRL"

    print "type,full_name,name,code,description,color,notes,commoditym,commodityn,hidden,tax,place_holder"

    for LINE in ACCOUNT_LIST:
        if len(LINE):
            FULL_NAME = LINE
            NAME = FULL_NAME.split(":")[-1]
            FATHER_ACCOUNT = FULL_NAME.split(":")[0]
            account_type = "UNKNOW"

            if (NAME == FULL_NAME):
                continue

            if (FATHER_ACCOUNT == "Assets"):
                account_type = "ASSET"
            elif (FATHER_ACCOUNT == "Equity"):
                account_type = "EQUITY"
            elif (FATHER_ACCOUNT == "Expenses"):
                account_type = "EXPENSE"
            elif (FATHER_ACCOUNT == "Income"):
                account_type = "INCOME"
            elif (FATHER_ACCOUNT == "Liabilities"):
                account_type = "LIABILITY"

            print "%s,%s,%s,,%s,,,%s,CURRENCY,F,F,F" % (account_type, FULL_NAME, NAME, NAME,  CURRENCY)

if len(sys.argv) < 2:
    print "Need arguments! %s <option>" % sys.argv[0]
elif sys.argv[1] == "accounts":
    account_list()
