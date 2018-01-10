#!/usr/bin/env python
"""
Module import
"""

import sys
import os
import configparser

from ledger import load_list_csv
from ledger import Itau
from ledger import Nubank
from ledger import QIF

if len(sys.argv) < 3:
    print(
        "Need arguments! {} <account> <input_file> <ledger_file>".format(
            sys.argv[0]))
else:
    CONFIG = configparser.ConfigParser()
    CONF_ACCOUNT = None
    LEDGER_FILE = None

    load_list_csv()
    ACCOUNT = sys.argv[1]

    if os.path.isfile('ledgerutils.conf'):
        CONFIG.read('ledgerutils.conf')

    if ACCOUNT in CONFIG.sections():
        CONF_ACCOUNT = CONFIG[ACCOUNT]

    if len(sys.argv) > 3:
        LEDGER_FILE = sys.argv[3] if os.path.isfile(sys.argv[3]) else None

    LIST_BANKS = {
        'itau': Itau(LEDGER_FILE, CONF_ACCOUNT),
        'nubank': Nubank(LEDGER_FILE, CONF_ACCOUNT),
        'qif': QIF(LEDGER_FILE, CONF_ACCOUNT)
    }

    BANK = LIST_BANKS[ACCOUNT]

    with open(sys.argv[2], 'r') as f:
        BANK.read_file(f)
        f.close()
    BANK.write_entry()
