#!/usr/bin/env python

import datetime
import json
import sys
import time
import urllib2
import pprint

date = int(time.mktime(time.strptime(sys.argv[1], "%Y-%m-%d")))
url = "https://www.mercadobitcoin.net/api/BTC/trades/%d/%d/" % (date, date+90000)

# print url
response = urllib2.urlopen(url)
data = json.loads(response.read())

if len(data) > 0:
    out_date = datetime.datetime.fromtimestamp(data[0]["date"]).strftime("%Y-%m-%d")
    out_price = float(data[0]["price"])
    print "P %s BTC %6.0f BRL" % (out_date, out_price)
