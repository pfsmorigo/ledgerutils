#!/usr/bin/env python
# coding=utf-8

import time
import re
import os

import sys
sys.path.append("..")
from ledger import *

class Fuel(Ledger):
    """Docstring for Fuel. """

    _account_name = "Expenses:Auto:Fuel"
    _credit_account = "Assets"
    _from_date = None

    def __init__(self, conf, output_file=None, from_date=None):
        """Init Fuel"""
        Ledger.__init__(self, conf, output_file)

        if conf:
            if 'account_name' in conf:
                self._account_name = conf['account_name']
            if 'credit_account' in conf:
                self._credit_account = conf['credit_account']

        self._from_date = from_date

    def read_file(self, _file):
        """
        Read files
        """
        TABLE, SIZE = load_csv(_file)
        for i in range(0, SIZE):
            DATE = import_date(TABLE['date'][i])

            if DATE < self._from_date:
                continue

            WHERE = TABLE['where'][i] if TABLE['where'][i] else "Unknown Place"
            TYPE = TABLE['type'][i] if TABLE['type'][i] else None
            PRICE = float(TABLE['price'][i]) if TABLE['price'][i] else 0.0
            LITERS = float(TABLE['liters'][i]) if TABLE['liters'][i] else 0.0
            PAID = float(TABLE['paid'][i]) if TABLE['paid'][i] else 0.0
            TOTAL = float(TABLE['total'][i]) if TABLE['total'][i] else 0.0
            DISCOUNT_NAME = TABLE['discount_name'][i] if TABLE['discount_name'][i] else None
            DISCOUNT_POINTS = TABLE['discount_points'][i] if TABLE['discount_points'][i] else None

            new_entry = Transaction(DATE, WHERE)
            if LITERS:
                new_entry.add(Account(self._account_name, TOTAL/PRICE,
                    eff_date = DATE, currency = "GAS", decimals = 6,
                    fixed_price = PRICE, fixed_price_decimals = 3,
                    total_price = TOTAL, comments = TYPE))
            else:
                new_entry.add(Account(self._account_name, TOTAL, comments = TYPE))

            if PAID and PAID < TOTAL:
                comments = "Discount: {} {}pts".format(DISCOUNT_NAME, DISCOUNT_POINTS)
                new_entry.add(Account(self._account_name, PAID-TOTAL, comments = comments))

            new_entry.add(Account(self._credit_account))
            self._list_entry.append(new_entry)

        self.write_entry()
