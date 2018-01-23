#!/usr/bin/env python
"""
Module import
"""

import sys
import os
import configparser
import argparse
import dateutil.parser

from ledger import load_list_csv
from ledger import Itau
from ledger import Nubank
from ledger import QIF

parser = argparse.ArgumentParser(
        description="Import files into ledger format.")
parser.add_argument("-d", type=str, metavar="DATE", dest="date",
        help="Start parsing from this date")
parser.add_argument("-o", type=argparse.FileType("w"), default=None,
        dest="output", metavar="OUTPUT",
        help="Output file to write new entries")
parser.add_argument("account",
        help="Format name. Currently supports: 'itau', 'nubank', 'qif'")
parser.add_argument("input_file", type=argparse.FileType('r'),
        help="Input file used by the parser")
args = parser.parse_args()

CONFIG = configparser.ConfigParser()
conf_account = None
from_date = None

load_list_csv()

if args.date:
    from_date = dateutil.parser.parse(args.date).timetuple()

if os.path.isfile('ledgerutils.conf'):
    CONFIG.read('ledgerutils.conf')

if args.account in CONFIG.sections():
    conf_account = CONFIG[args.account]

LIST_BANKS = {
    'itau': Itau(args.output, conf_account, from_date=from_date),
    'nubank': Nubank(args.output, conf_account, from_date=from_date),
    'qif': QIF(args.output, conf_account, from_date=from_date)
}

BANK = LIST_BANKS[args.account]
BANK.read_file(args.input_file)
BANK.write_entry()
