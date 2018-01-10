#!/usr/bin/env python

import sys
import os

from ledger import load_list_csv
from ledger import Itau
from ledger import Nubank

if len(sys.argv) < 3:
    print("Need arguments! {} <account> <input_file> <ledger_file>".format(sys.argv[0]))
else:
    load_list_csv()
    ACCOUNT = sys.argv[1]

    LEDGER_FILE = None
    if len(sys.argv) > 3:
        LEDGER_FILE = sys.argv[3] if os.path.isfile(sys.argv[3]) else None

    LIST_BANKS = {
        'itau': Itau(LEDGER_FILE),
        'nubank': Nubank(LEDGER_FILE)
        }

    BANK = LIST_BANKS[ACCOUNT]

    with open(sys.argv[2], 'r') as f:
        BANK.read_file(f)
        f.close()
    BANK.write_entry()
