#!/usr/bin/env python

import sys
import csv
import time
import re
import datetime
import glob
import os.path

translation_list = {}
ledger_file = None

class Transaction:
    def __init__(self, date, desc, eff_date = None):
        self.date = date
        self.desc = desc
        self.eff_date = eff_date
        self.accounts = [Account() for i in range(20)]
        self.total = 0

        while '  ' in self.desc:
            self.desc = self.desc.replace('  ', ' ').strip()

        num = self.desc.rsplit(None, 1)[-1]
        if num.isdigit():
            self.desc = "(#%s) %s" % (num, self.desc[:-len(num)-1])

        if self.eff_date and self.date.tm_year == 1900:
            date_str = "-%s" % time.strftime("%m-%d", self.date)
            year = self.eff_date.tm_year
            if int(self.eff_date.tm_yday) < int(self.date.tm_yday):
                year -= 1
            self.date = time.strptime(str(year)+date_str, '%Y-%m-%d')

    def add(self, account):
        self.accounts[self.total] = account
        self.total += 1

    def __str__(self):
        output = "%s" % time.strftime("%Y-%m-%d", self.date)
        if self.eff_date and self.date != self.eff_date:
            output += "=%s" % time.strftime("%Y-%m-%d", self.eff_date)
        output +=" %s" % self.desc

        for i in range(0, 20):
            output += "%s" % self.accounts[i]

        return output

class Account:
    def __init__(self, name = None, value = None, currency = "BRL", eff_date = None):
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
    if not os.path.isfile("import.csv"):
        return
    f = open("import.csv", 'rt')
    try:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            translation_list[row[0]] = [ row[1], row[2] ]
    finally:
        f.close()

def translate(desc, account = "Unknown"):
    for item in translation_list:
        if item not in desc:
            continue
        if translation_list[item][0]:
            desc = desc.replace(item, translation_list[item][0]).strip()
        if translation_list[item][1]:
            account = translation_list[item][1].strip()
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

def itau(f):
    for line in f:
        line_split = line.split(";")
        date = time.strptime(line_split[0], '%d/%m/%Y')
        desc = line_split[1].strip()
        value = float(line_split[2].strip().replace(",", "."))
        desc, account = translate(desc, "Expenses:Unknown")
        eff_date = None

        if desc[len(desc)-3] is '/' and desc[len(desc)-6] is '-':
            eff_date = date
            date = time.strptime(desc[len(desc)-5:], '%d/%m')
            desc = desc[:-6]

        new_entry = Transaction(date, desc, eff_date)
        new_entry.add(Account("Assets:Checking", value))
        new_entry.add(Account(account))
        write_entry(new_entry)


def nubank(f):
    for line in f:
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
            for i in range(total):
                new_entry.add(Account(account, value, eff_date = eff_date))
                eff_date = pay_date(eff_date, eff_date.tm_mday, 0)

        new_entry.add(Account("Liabilities:Nubank"))
        write_entry(new_entry)


def qif(f):
    for line in f:
        if line[0] is 'N':
            account1 = line[1:].strip()

        if line[0] is 'D':
            date = time.strptime(line[1:].strip(), '%Y/%m/%d')

        if line[0] is 'M':
            desc = line[1:].strip()

        if line[0] is 'S':
            account2 = line[1:].strip()

        if line[0] is '$' and desc != "Opening Balances":
            value = float(line[1:])
            new_entry = Transaction(date, desc)
            new_entry.add(Account(account1, value))
            new_entry.add(Account(account2))
            write_entry(new_entry)


def conectcar(f):
    for line in f:
        line_split = line.split(";")
        date = line_split[0]
        car = line_split[1]
        desc = line_split[2]
        income = "%s BRL" % line_split[3].strip().replace(",", ".")
        outcome = "%s BRL" % line_split[4].strip().replace(",", ".")

        description, account = translate(desc)
        value = "%.2f BRL" % (float(outcome.strip())*(-1))
        print_entry(date, description, value, "Expeses:House", outcome)


def insert_ledger_file(ledger_file, new_entry):
    input_file = open(ledger_file, 'r').readlines()
    write_file = open(ledger_file,'w')
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

def write_entry(new_entry):
    if ledger_file:
        insert_ledger_file(ledger_file, new_entry)
    else:
        print "\n%s" % new_entry

if len(sys.argv) < 3:
    print "Need arguments! %s <account> <input_file> <ledger_file>" % sys.argv[0]
else:
    load_list_csv()
    account = sys.argv[1]

    if len(sys.argv) > 3:
        ledger_file = sys.argv[3] if os.path.isfile(sys.argv[3]) else None

    with open(sys.argv[2], 'r') as f:
        eval(account + "(f)")
        f.close()
