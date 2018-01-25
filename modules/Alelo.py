#!/usr/bin/env python

import csv
import time
import re
import os
import ledger

import sys
sys.path.append("..")
from ledger import *

class Alelo(Ledger):
    """Docstring for Alelo. """

    _account_name = "Assets:Alelo"
    _from_date = None

    def __init__(self, conf, output_file=None, from_date=None):
        """Init Alelo"""
        Ledger.__init__(self, conf, output_file)

        if conf and 'account_name' in conf:
            self._account_name = conf['account_name'].encode('utf-8')

        self._from_date = from_date

    def read_file(self, _file):
        """Read file

        :file: File to be read
        :returns: None

        """
        for line in _file:
            line_split = line.split(";")
            date = time.strptime("%s/%s" % (line_split[0], "2018"), '%d/%m/%Y')

            if date is not None and date < self._from_date:
                continue

            desc = str(line_split[1].strip())
            value = float(line_split[2].strip().replace("R$ ", "").replace(",", "."))
            desc, account = translate(desc, "Expenses:Unknown")

            new_entry = Transaction(date, desc, None)
            new_entry.add(Account(account, value))
            new_entry.add(Account(self._account_name))
            # since entries are from newer to older, insert entry at the beggining
            self._list_entry.insert(0, new_entry)
