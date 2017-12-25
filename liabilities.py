#!/usr/bin/env python

import sys
import subprocess
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

def commodity2float(commodity):
    return float(commodity.replace(",", "").split(" ")[0])

def get_amount(account):
    output = {}
    ACCOUNT_LIST = subprocess.check_output(['ledger', '-rVS', 'date', '--effective', '--register-format', '%(effective_date);%(amount)\n', 'register', account]).split("\n")
    for LINE in ACCOUNT_LIST:
        if len(LINE) > 0:
            DATE, VALUE = LINE.split(";")
            if DATE:
                INDEX = int(''.join(DATE.split("/")[:-1]))
                ADD = output[INDEX] if INDEX in output.keys() else 0.0
                output[INDEX] = commodity2float(VALUE)+ADD
    return output

accounts = {}
start_param_position = 0
export_csv = False

if sys.argv[1] == "csv":
    export_csv = True
    start_param_position += 1

for NUM in range(0, len(sys.argv)-start_param_position-1):
    accounts[NUM, 0] = sys.argv[NUM+start_param_position+1]
    accounts[NUM, 1] = get_amount(sys.argv[NUM+start_param_position+1])

num_of_accounts =  len(accounts)/2

output = "data"
for NUM in range(0, num_of_accounts):
    output += ";%s" % accounts[NUM, 0]

output += ";total" if num_of_accounts > 1 else ""

now = datetime.datetime.now()
for MONTH in range(0, 12):
    CURR_DATE = date.today() + relativedelta(months =+ MONTH)
    INDEX = int(CURR_DATE.strftime("%Y%m"))
    total = 0
    output += CURR_DATE.strftime("\n%Y-%m")
    for NUM in range(0, len(accounts)/2):
        VALUE = accounts[NUM, 1][INDEX] if INDEX in accounts[NUM, 1].keys() else 0.0
        total += VALUE
        output += ";%.2f" % VALUE
    output += ";%.2f" % total if num_of_accounts > 1 else ""

if export_csv:
    print output
else:
   num_of_accounts += 2 if num_of_accounts > 1 else 1
   for LINE in output.split("\n"):
       VALUES = LINE.split(";")
       if len(VALUES) > 1:
           print "%7s" % VALUES[0],
           for ITEM in range(1, num_of_accounts):
               print " %9s" % VALUES[ITEM],
           print ""
