#!/usr/bin/env python
# coding=utf-8

import sys
import csv
import time
import re
import os
import ledger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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

    def online(self, _number):
        print "Running selenium..."
        chrome_options = Options()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://www.meualelo.com.br/")

        search_box = driver.find_element_by_name("txtCartao1")
        search_box.send_keys(_number)
        raw_input("Press Enter after you enter the catcha...")
        search_box.submit()

        driver.switch_to_frame(driver.find_element_by_id("conteudo"))
        driver.switch_to_frame(driver.find_element_by_id("saldoAlelo"))
        rows = driver.find_elements_by_class_name("rowTablenew")

        output = []
        for row in rows:
            col = row.find_elements_by_tag_name("td")
            output.append("%s;%s;%s" % (col[0].text, col[1].text, col[2].text))

        self.read_file(output)
        driver.quit()
