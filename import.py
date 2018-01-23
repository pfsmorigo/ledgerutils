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
parser.add_argument("-i", type=argparse.FileType("r"), default=None,
        dest="input_file", metavar="INPUT",
        help="Input file used by the parser")
parser.add_argument("-o", type=argparse.FileType("w"), default=None,
        dest="output_file", metavar="OUTPUT",
        help="Output file to write new entries")
parser.add_argument("account",
        help="Format name. Currently supports: 'itau', 'nubank', 'qif'")
args = parser.parse_args()

CONFIG = configparser.ConfigParser()
conf = None
from_date = None
input_file = None

load_list_csv()

if args.date:
    from_date = dateutil.parser.parse(args.date).timetuple()

if os.path.isfile('ledgerutils.conf'):
    CONFIG.read('ledgerutils.conf')

if args.account in CONFIG.sections():
    conf = CONFIG[args.account]

# Command line has priority over config file
if args.input_file:
    input_file = args.input_file
elif 'input_file' in conf:
    input_file = open(conf['input_file'], "r")

LIST_BANKS = {
    'itau': Itau(args.output_file, conf, from_date=from_date),
    'nubank': Nubank(args.output_file, conf, from_date=from_date),
    'qif': QIF(args.output_file, conf, from_date=from_date)
}

if input_file:
    BANK = LIST_BANKS[args.account]
    BANK.read_file(input_file)
    BANK.write_entry()
