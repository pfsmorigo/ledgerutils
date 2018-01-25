#!/usr/bin/env python
# coding=utf-8

import sys
import os
import configparser
import argparse
import dateutil.parser

from modules import Alelo
from modules import Itau
from modules import Nubank
from modules import QIF

from ledger import load_list_csv

def convert(module, account_type, args):
    input_file = None

    # Command line has priority over config file
    if args.input_file:
        input_file = args.input_file
    elif 'input_file' in conf:
        input_file = open(conf['input_file'], "r")

    if input_file:
        module.read_file(input_file)
        module.write_entry()

def online(module, account_type, args):
    if account_type == "alelo" and len(args.info) == 1:
        module.online(args.info[0])
        module.write_entry()
    else:
        print "Something went wrong... Check your parameters"

parser = argparse.ArgumentParser(
        description="Utilities to help with plaintext accounting.")
parser.add_argument("-d", type=str, metavar="DATE", dest="date",
        help="Start parsing from this date")

subparsers = parser.add_subparsers(help="Command to run")

parser_convert = subparsers.add_parser("convert", help="Convert file into ledger format")
parser_convert.add_argument("account", type=str, help="Format name")
parser_convert.add_argument("-i", type=argparse.FileType("r"), default=None,
        dest="input_file", metavar="INPUT",
        help="Input file used by the parser")
parser_convert.add_argument("-o", type=argparse.FileType("r"), default=None,
        dest="output_file", metavar="OUTPUT",
        help="Output file to write new entries")
parser_convert.set_defaults(func=convert)

parser_online = subparsers.add_parser("online", help="Get information online")
parser_online.add_argument("account", type=str, help="Format name")
parser_online.add_argument("info", type=str, nargs='*', help="Infos to access")
parser_online.add_argument("-o", type=argparse.FileType("r"), default=None,
        dest="output_file", metavar="OUTPUT",
        help="Output file to write new entries")
parser_online.set_defaults(func=online)

args = parser.parse_args()

CONFIG = configparser.ConfigParser()
conf = None
from_date = None
output_file = None
account_type = args.account

load_list_csv()

if os.path.isfile('ledgerutils.conf'):
    CONFIG.read('ledgerutils.conf')

if args.account in CONFIG.sections():
    conf = CONFIG[args.account]

if args.date:
    from_date = dateutil.parser.parse(args.date).timetuple()

if args.output_file:
    output_file = args.output_file
elif conf and 'output_file' in conf:
    output_file = open(conf['output_file'], "r")

if conf and "account_type" in conf:
    account_type = conf["account_type"]

MODULES = {
    'alelo': Alelo.Alelo(conf, output_file=output_file, from_date=from_date),
    'itau': Itau.Itau(conf, output_file=output_file, from_date=from_date),
    'nubank': Nubank.Nubank(conf, output_file=output_file, from_date=from_date),
    'qif': QIF.QIF(conf, output_file=output_file, from_date=from_date)
}

args.func(MODULES[account_type], account_type, args)
