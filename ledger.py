"""
Ledger module
"""
#!/usr/bin/env python

import csv
import time
import re
import os

TRANSLATION_LIST = {}
LEDGER_FILE = None


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

        num = self.desc.rsplit(None, 1)[-1]
        if num.isdigit():
            self.desc = "(#%s) %s" % (num, self.desc[:-len(num) - 1])

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

    def __init__(self, name=None, value=None, currency="BRL", eff_date=None):
        self.name = name
        self.value = value
        self.currency = currency
        self.eff_date = eff_date

    def __str__(self):
        if not self.name:
            return ""
        output = "\n    %s" % self.name
        if self.value:
            output = "%-34s %14.2f %s" % (output, self.value, self.currency)
        if self.eff_date:
            output += "  ; [=%s]" % time.strftime("%Y-%m-%d", self.eff_date)

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


def translate(desc, account="Unknown"):
    for item in TRANSLATION_LIST:
        if item not in desc:
            continue
        if TRANSLATION_LIST[item][0]:
            desc = desc.replace(item, TRANSLATION_LIST[item][0]).strip()
        if TRANSLATION_LIST[item][1]:
            account = TRANSLATION_LIST[item][1].strip()
    return desc, account


def pay_date(date, pay_day, best_day):
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


class Ledger(object):
    """Docstring for Ledger. """

    def __init__(self, legder_file):
        """TODO: Docstring for __init__.
        :returns: TODO

        """
        self._list_entry = []
        self._ledger_file = legder_file

    def write_entry(self):
        """TODO: Docstring for write_entry.

        :new_entry:
        :returns: None

        """
        for entry in self._list_entry:
            if self._ledger_file:
                insert_ledger_file(self._ledger_file, entry)
            else:
                print("\n%s" % entry)

    def list_entry(self):
        """List entry
        :returns: TODO

        """
        return self._list_entry


class Itau(Ledger):
    """Docstring for Itau. """

    def __init__(self, ledger_file):
        """Init Itau"""
        Ledger.__init__(self, ledger_file)

    def read_file(self, _file):
        """Read file

        :file: File to be read
        :returns: None

        """
        for line in _file:
            line_split = line.split(";")
            date = time.strptime(line_split[0], '%d/%m/%Y')
            desc = line_split[1].strip()
            value = float(line_split[2].strip().replace(",", "."))
            desc, account = translate(desc, "Expenses:Unknown")
            eff_date = None

            if desc[len(desc) - 3] == '/' and desc[len(desc) - 6] == '-':
                eff_date = date
                date = time.strptime(desc[len(desc) - 5:], '%d/%m')
                desc = desc[:-6]

            new_entry = Transaction(date, desc, eff_date)
            new_entry.add(Account("Assets:Checking", value))
            new_entry.add(Account(account))
            self._list_entry.append(new_entry)


class Nubank(Ledger):
    """Docstring for Nubank. """

    def __init__(self, ledger_file):
        """Init Nubank"""
        Ledger.__init__(self, ledger_file)

    def read_file(self, _file):
        """
        Read files
        """
        for line in _file:
            # ignore head line
            if line.startswith('date,'):
                continue

            line_split = line.split(",")
            date = time.strptime(line_split[0], '%Y-%m-%d')
            desc = line_split[2]
            value = float(line_split[3])
            eff_date = pay_date(date, 15, 8)
            desc, account = translate(desc, "Expenses:Unknown")
            total = 0

            if re.search(r'.* [0-9]+\/[0-9]+.*$', desc) is not None:
                part, total = map(int, desc.split()[-1].split('/'))
                desc = desc.rsplit(' ', 1)[0]

            if total is 0:
                new_entry = Transaction(date, desc, eff_date)
                new_entry.add(Account(account, value))
            else:
                if part is not 1:
                    continue
                new_entry = Transaction(date, desc)
                for _ in range(total):
                    new_entry.add(Account(account, value, eff_date=eff_date))
                    eff_date = pay_date(eff_date, eff_date.tm_mday, 0)

            new_entry.add(Account("Liabilities:Nubank"))
            self._list_entry.append(new_entry)


class QIF(Ledger):
    """
    Docstring for QIF.
    """
    def __init__(self, ledger_file):
        """Init QIF"""
        Ledger.__init__(self, ledger_file)

    def read_file(self, _file):
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

def insert_ledger_file(ledger_file, new_entry):
    input_file = open(ledger_file, 'r').readlines()
    write_file = open(ledger_file, 'w')
    pattern = re.compile('(\d+-\d+-\d+)')
    done = False

    for line in input_file:
        if not done and pattern.match(line):
            date_txt = line.split(' ', 1)[0].split('=', 1)[0]
            if time.strptime(date_txt, '%Y-%m-%d') > new_entry.date:
                write_file.write("%s\n\n" % new_entry)
                done = True
        write_file.write(line)

    if not done:
        write_file.write("\n%s\n" % new_entry)

    write_file.close()
