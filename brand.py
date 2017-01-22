#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import commands
import os
import sys
import re
import urllib
import urllib2
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select

from yahoo_finance import Currency
import wget
import time
import simplejson as json
import pyperclip

# configuration
dir_base = '/test'

#
class BrandItem():
    usd_jpn = float(Currency('USDJPY').get_bid())

    # constructor
    def __init__(self, site, driver=None):

        BrandItem.driver = driver

        self.site = site
        self.dir_site = os.path.join(dir_base, site)

        self.price = None
        self.details = []
        self.colors = []
        self.size = []
        self.pics = []
        self.style = None

    def save_data(self):
        """Save data in summary.json"""

        summary_file = os.path.join(self.dir_item, "summary.json")
        with open(summary_file, "w") as file:
            # del driver  # remove driver b/c it cannot be saved ...
            json.dump(self.__dict__, file, indent=2)

            # show object attributes
            print json.dumps(self.__dict__, indent=2)

        print 'Summary file created ...', self.dir_item



    @staticmethod
    def get_soup(url):
        # get html resource
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        values = {'name': 'Michael Foord',
            'location': 'Northampton',
            'language': 'Python'}
        headers = {'User-Agent': user_agent}

        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req)
            html = response.read()

        except urllib2.HTTPError as e:
            print e, url
            response = urllib2.urlopen(url)
            html = response.read()

        return BeautifulSoup(html, 'html.parser')
