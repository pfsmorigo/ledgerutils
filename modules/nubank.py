#!/usr/bin/env python

import csv
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import sys
sys.path.append("..")
from ledger import *

class Nubank(Ledger):
    """Docstring for Nubank. """

    _account_name = "Liabilities:Nubank"
    _pay_day = 15
    _best_day = 8
    _from_date = None

    def __init__(self, conf, output_file=None, from_date=None):
        """Init Nubank"""
        Ledger.__init__(self, conf, output_file)

        if conf:
            if 'account_name' in conf:
                self._account_name = conf['account_name']
            if 'pay_day' in conf:
                self._pay_day = int(conf['pay_day'])
            if 'best_day' in conf:
                self._best_day = int(conf['best_day'])

        self._from_date = from_date

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

            if date is not None and date < self._from_date:
                continue

            desc = line_split[2]
            value = float(line_split[3])
            eff_date = self.pay_date(date, self._pay_day, self._best_day)
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
                    eff_date = self.pay_date(eff_date, eff_date.tm_mday, 0)

            new_entry.add(Account(self._account_name))
            self._list_entry.append(new_entry)
        self.write_entry()

    def online(self, username, password):
        print "Running selenium..."
        chrome_options = Options()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://app.nubank.com.br/#/login")

        search_box = driver.find_element_by_id("username")
        search_box.send_keys(username)
        search_box = driver.find_element_by_id("input_001")
        search_box.send_keys(password)
        search_box.submit()

        time.sleep(5)

        rows = driver.find_elements_by_xpath("//tr[@class='dc-table-row info']")
        for row in rows:
            card_present = row.find_elements_by_class_name("card_present")
            title = row.find_element_by_class_name("title").text.encode("utf-8")
            desc = row.find_elements_by_class_name("description")
            amount = row.find_elements_by_class_name("amount")
            tags = row.find_element_by_class_name("tags").text.encode("utf-8")
            date = row.find_element_by_class_name("time").text.encode("utf-8")

            desc = desc[0].text.encode("utf-8") if len(desc) else ""
            amount = amount[0].text.encode("utf-8") if len(amount) else ""

            print "%s | %s | %s | %s | %s | %d | %d" % (title, desc, amount, tags, date, len(card_present))

            # output.append("%s;%s;%s" % (col[0].text, col[1].text, col[2].text))

        time.sleep(10)




