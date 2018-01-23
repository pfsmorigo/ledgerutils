#!/usr/bin/env python
"""
Module import
"""

import sys
import os
import configparser
import argparse

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
CONF_ACCOUNT = None

load_list_csv()

if os.path.isfile('ledgerutils.conf'):
    CONFIG.read('ledgerutils.conf')

if args.account in CONFIG.sections():
    CONF_ACCOUNT = CONFIG[args.account]

LIST_BANKS = {
    'itau': Itau(args.output, CONF_ACCOUNT),
    'nubank': Nubank(args.output, CONF_ACCOUNT),
    'qif': QIF(args.output, CONF_ACCOUNT)
}

BANK = LIST_BANKS[args.account]
BANK.read_file(args.input_file)
BANK.write_entry()
