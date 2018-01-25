#!/usr/bin/env python

import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def alelo(number):
    chrome_options = Options()
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('https://www.meualelo.com.br/')

    search_box = driver.find_element_by_name('txtCartao1')
    search_box.send_keys(number)
    time.sleep(8)
    search_box.submit()

    driver.switch_to_frame(driver.find_element_by_id("conteudo"))
    driver.switch_to_frame(driver.find_element_by_id("saldoAlelo"))
    rows = driver.find_elements_by_class_name("rowTablenew")

    for row in rows:
        col = row.find_elements_by_tag_name("td")
        print "%s;%s;%s" % (col[0].text, col[1].text, col[2].text)

    driver.quit()

if len(sys.argv) < 2:
    print "Need arguments! %s <account> <attributes> ..." % sys.argv[0]
else:
    if sys.argv[1] == "alelo":
        if len(sys.argv) < 3:
            print "Need card number"
        else:
            alelo(sys.argv[2])
