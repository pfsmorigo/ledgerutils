"""
Ledger module
"""
#!/usr/bin/env python
# coding=utf-8

import csv
import time
import re
import os
import dateutil.parser
from datetime import datetime

TRANSLATION_LIST = {}

class Ledger(object):
    """Docstring for Ledger. """

    def __init__(self, conf, output_file):
        """TODO: Docstring for __init__.
        :returns: TODO

        """
        self._list_entry = []
        self._output_file = output_file

    def list_entry(self):
        """List entry
        :returns: TODO

        """
        return self._list_entry

    def write_entry(self):
        """TODO: Docstring for write_entry.

        :new_entry:
        :returns: None

        """
        if self._output_file:
            print "Writing output to file '%s'... " % self._output_file.name
            for entry in self._list_entry:
                file_content = open(self._output_file.name, 'r').readlines()
                pattern = re.compile('(\d+-\d+-\d+)')
                done = False

                with open(self._output_file.name, 'w') as output_file:
                    for line in file_content:
                        if not done and pattern.match(line):
                            date_txt = line.split(' ', 1)[0].split('=', 1)[0]
                            if time.strptime(date_txt, '%Y-%m-%d') > entry.date:
                                output_file.write("%s\n\n" % entry)
                                done = True
                        output_file.write(line)

                    if not done:
                        output_file.write("\n%s\n" % entry)
        else:
            for entry in self._list_entry:
                print("\n%s" % entry)

class Transaction:
    """
    Transaction class
    """

    def __init__(self, date, desc, eff_date=None):
        self.date = date
        self.desc = desc
        self.eff_date = eff_date
        self.accounts = [Account() for _ in range(20)]
        self.total = 0

        while '  ' in self.desc:
            self.desc = self.desc.replace('  ', ' ').strip()

        # num = self.desc.rsplit(None, 1)[-1]
        # if num.isdigit():
            # self.desc = "(#%s) %s" % (num, self.desc[:-len(num) - 1])

        if self.eff_date and self.date.tm_year == 1900:
            date_str = "-%s" % time.strftime("%m-%d", self.date)
            year = self.eff_date.tm_year
            if int(self.eff_date.tm_yday) < int(self.date.tm_yday):
                year -= 1
            self.date = time.strptime(str(year) + date_str, '%Y-%m-%d')

    def add(self, account):
        """
        Add transaction
        """
        self.accounts[self.total] = account
        self.total += 1

    def __str__(self):
        output = "%s" % time.strftime("%Y-%m-%d", self.date)
        if self.eff_date and self.date != self.eff_date:
            output += "=%s" % time.strftime("%Y-%m-%d", self.eff_date)
        output += " %s" % self.desc

        for i in range(0, 20):
            output += "%s" % self.accounts[i]

        return output


class Account(object):
    """
    Class account
    """

    _format_account = "\n    {}"
    _format_ammount = "{:{acw}}{:{amw}.{d}f} {}"
    _format_fixed_price = " {{={:.{d}f} {}}}"
    _format_total_price = " @@ {:.{d}f} {}"
    _format_eff_date = " [{}]"
    _format_comment = "   ; {}"

    def __init__(self, name = None, value = None, comments = None ,
            currency = "BRL", decimals = 2, eff_date = None,
            fixed_price = None, fixed_price_currency = "BRL", fixed_price_decimals = 2,
            total_price = None, total_price_currency = "BRL", total_price_decimals = 2):
        self.name = str(name) if name else None
        self.value = value
        self.currency = currency
        self.decimals = decimals
        self.eff_date = eff_date
        self.account_width = 35
        self.ammount_width = 12+decimals # keep aligned at decimals
        self.comments = comments
        self.fixed_price = fixed_price
        self.fixed_price_currency = fixed_price_currency
        self.fixed_price_decimals = fixed_price_decimals
        self.total_price = total_price
        self.total_price_currency = total_price_currency
        self.total_price_decimals = total_price_decimals

    def __str__(self):
        if not self.name:
            return ""
        output = self._format_account.format(self.name)
        if self.value:
            output = self._format_ammount.format(
                output, self.value, self.currency,
                acw = self.account_width, amw = self.ammount_width, d = self.decimals)

        if self.fixed_price:
            output += self._format_fixed_price.format(
                self.fixed_price, self.fixed_price_currency, d = self.fixed_price_decimals)

        if self.eff_date:
            output += self._format_eff_date.format(time.strftime("%Y-%m-%d", self.eff_date))

        if self.total_price:
            output += self._format_total_price.format(
                self.total_price, self.total_price_currency, d = self.total_price_decimals)

        if self.comments:
            output += self._format_comment.format(self.comments)

        return output


def load_list_csv():
    """
    Load list csv
    """

    if not os.path.isfile("import.csv"):
        return
    csv_file = open("import.csv", 'rt')
    try:
        reader = csv.reader(csv_file, delimiter=';')
        for row in reader:
            TRANSLATION_LIST[row[0]] = [row[1], row[2]]
    finally:
        csv_file.close()


def pay_date(date, pay_day, best_day):
    """
    Pay date
    """
    month = date.tm_mon
    year = date.tm_year
    if date.tm_mday >= best_day:
        if date.tm_mon == 12:
            month = 1
            year += 1
        else:
            month += 1
    date = "%d-%02d-%02d" % (year, month, pay_day)
    return time.strptime(date, "%Y-%m-%d")


def import_date(datestr, year = datetime.now().year):
    translate = [
        ("Fev", "Feb"), ("Abr", "Apr"), ("Mai", "May"), ("Ago", "Aug"),
        ("Set", "Sep"), ("Out", "Oct"), ("Dez", "Dec"),]

    datestr = datestr.title()
    for item in translate:
        datestr = datestr.replace(item[0], item[1])
    date = dateutil.parser.parse(datestr)
    if date > datetime.now():
        date = date.replace(year = year-1)
    return date.timetuple()


def import_value(valuestr):
    return float(valuestr.replace("R$", "").replace(".", "").replace(",", "."))


def translate(desc, account="Unknown"):
    """
    Translate
    """
    for item in TRANSLATION_LIST:
        if item not in desc:
            continue
        if TRANSLATION_LIST[item][0]:
            desc = desc.replace(item, TRANSLATION_LIST[item][0]).strip()
        if TRANSLATION_LIST[item][1]:
            account = TRANSLATION_LIST[item][1].strip()
    return desc, account

def load_csv(_file, delimiter = ','):
    reader = csv.reader(_file, delimiter = delimiter)
    headers = reader.next()
    table = {}
    size = 0
    for h in headers:
        table[h.lower().replace(" ", "_")] = []
    for row in reader:
        size += 1
        for h, v in zip(headers, row):
            table[h.lower().replace(" ", "_")].append(v)
    return table, size
