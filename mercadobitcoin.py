#!/usr/bin/env python
"""
Module mercado bitcoin
"""

import datetime
import json
import sys
import time
import urllib2

DATE = int(time.mktime(time.strptime(sys.argv[1], "%Y-%m-%d")))
URL = "https://www.mercadobitcoin.net/api/BTC/trades/%d/%d/" % (DATE,
                                                                DATE + 90000)

# print url
RESPONSE = urllib2.urlopen(URL)
DATA = json.loads(RESPONSE.read())

if len(DATA) > 0:
    OUT_DATE = datetime.datetime.fromtimestamp(
        DATA[0]["date"]).strftime("%Y-%m-%d")
    OUT_PRICE = float(DATA[0]["price"])
    print "P %s BTC %6.0f BRL" % (OUT_DATE, OUT_PRICE)
