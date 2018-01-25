#!/usr/bin/env python

import csv
import time
import re
import os

import sys
sys.path.append("..")
from ledger import *

class QIF(Ledger):
    """
    Docstring for QIF.
    """

    def __init__(self, ledger_file, conf, from_date=None):
        """Init QIF"""
        Ledger.__init__(self, ledger_file, conf)

    def read_file(self, _file):
        """
        Read file
        """
        for line in _file:
            if line[0] == 'N':
                account1 = line[1:].strip()

            if line[0] == 'D':
                date = time.strptime(line[1:].strip(), '%Y/%m/%d')

            if line[0] == 'M':
                desc = line[1:].strip()

            if line[0] == 'S':
                account2 = line[1:].strip()

            if line[0] == '$' and desc != "Opening Balances":
                value = float(line[1:])
                new_entry = Transaction(date, desc)
                new_entry.add(Account(account1, value))
                new_entry.add(Account(account2))
                self._list_entry.append(new_entry)
