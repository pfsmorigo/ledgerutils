#!/usr/bin/env python

import csv
import time
import re
import os
import ledger

import sys
sys.path.append("..")
from ledger import *

class Itau(Ledger):
    """Docstring for Itau. """

    _account_name = "Assets:Checking"
    _from_date = None

    def __init__(self, conf, output_file=None, from_date=None):
        """Init Itau"""
        Ledger.__init__(self, conf, output_file)

        if conf and 'account_name' in conf:
            self._account_name = conf['account_name']

        self._from_date = from_date

    def read_file(self, _file):
        """Read file

        :file: File to be read
        :returns: None

        """
        for line in _file:
            line_split = line.split(";")
            date = time.strptime(line_split[0], '%d/%m/%Y')

            if date is not None and date < self._from_date:
                continue

            desc = line_split[1].strip()
            value = float(line_split[2].strip().replace(",", "."))
            desc, account = translate(desc, "Expenses:Unknown")
            eff_date = None

            if desc[len(desc) - 3] == '/' and desc[len(desc) - 6] == '-':
                eff_date = date
                date = time.strptime(desc[len(desc) - 5:], '%d/%m')
                desc = desc[:-6]

            new_entry = Transaction(date, desc, eff_date)
            if value > 0:
                new_entry.add(Account(self._account_name, value))
                new_entry.add(Account(account))
            else:
                new_entry.add(Account(account, value*(-1)))
                new_entry.add(Account(self._account_name))
            self._list_entry.append(new_entry)
        self.write_entry()
