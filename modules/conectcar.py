#!/usr/bin/env python

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

class ConectCar(Ledger):
    """Docstring for ConectCar. """

    _account_name = "Assets:ConectCar"
    _from_date = None

    def __init__(self, conf, output_file=None, from_date=None):
        """Init ConectCar"""
        Ledger.__init__(self, conf, output_file)

        if conf and 'account_name' in conf:
            self._account_name = conf['account_name'].encode('utf-8')

        self._from_date = from_date

    def online(self, username, password):
        print "Running selenium..."
        chrome_options = Options()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://cliente.conectcar.com/Autenticacao/Autenticar?ReturnUrl=%2fExtrato")

        search_box = driver.find_element_by_id("UserName")
        search_box.send_keys(username)
        search_box = driver.find_element_by_id("Password")
        search_box.send_keys(password)
        search_box.submit()

        driver.get("https://cliente.conectcar.com/Extrato/ConsultaExtratoCompleto")

        rows = driver.find_elements_by_xpath("//tr[@data-grupodia]")
        for row in rows:
            date_raw = row.get_attribute("data-grupodia").encode("utf-8")
            date = time.strptime(date_raw, '%d/%m/%Y')

            if date is not None and date < self._from_date:
                continue

            col = row.find_elements_by_tag_name("td")

            car_plate = col[2].text.encode("utf-8")
            desc_raw = col[3].text.encode("utf-8").replace("|", "->").split("\n")
            credit = float(col[5].text.replace(",",".")) if len(col[5].text) > 0 else 0.0
            debit = float(col[6].text.replace(",",".")) if len(col[6].text) > 0 else 0.0
            desc = ""
            account = "Expenses:Auto:"

            if desc_raw[0].startswith("Passagem em"):
                desc += "%s (%s, %s)" % (desc_raw[1].title(), car_plate, desc_raw[0].replace("Passagem em ", ""))
                account += "Toll"
            elif desc_raw[0].startswith("Estacionamento em"):
                desc += "%s (%s, %s)" % (desc_raw[1].title(), car_plate, desc_raw[0].replace("Estacionamento em ", ""))
                account += "Parking"
            elif desc_raw[0].startswith("Mensalidade") or desc_raw[0].startswith("Recarga"):
                desc += "%s (%s)" % (desc_raw[1], car_plate)
                account += "Taxes"
            else:
                desc += raw_desc.replace("\n", " - ")
                account += "Unknown"

            # Remove date from desc if it's the same date
            desc = desc.replace("%s " % date_raw, "")

            new_entry = Transaction(date, desc, None)
            if credit:
                new_entry.add(Account(self._account_name, credit))
                new_entry.add(Account(account))
            else:
                new_entry.add(Account(account, debit))
                new_entry.add(Account(self._account_name))

            self._list_entry.append(new_entry)
        self.write_entry()
