#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import re
from brand import BrandItem

#
class CoachItem(BrandItem):
    """
    Single item on coach.com
    """
    brand = 'coach'
    shop = u"Coach直営店"

    def __init__(self, url_shop, driver, item_id=None, my_price=None, usps=1390):
        """
        Construct an item in given url.
        """
        self.item_id = item_id
        self.my_price = my_price  # to calculate profit
        self.usps = usps  #

        BrandItem.__init__(self, 'coach', driver)

        # set url
        self.url_shop = url_shop

        # set name and style number
        pat = re.compile('coach.com/(.+)/(.+)\.html')
        match = re.search(pat, url_shop)
        if match:
            name = match.group(1)

            self.name = name
            self.style = match.group(2)

        else:
            print 'could not get name or style number ...'
            sys.exit(1)

        # get beautiful soup
        soup = self.get_soup(url_shop)

        # set in_stock
        # todo: not valid for items that have multiple colors
        tag = soup.find('button', id='add-to-cart')

        # the string could be "SOLD OUT" or "Sold Out"
        if tag.string.strip().lower() == 'sold out':
            self.in_stock = False
            return

        else:
            self.in_stock = True

            # set price
            tag_price = soup.find('span', {'class': 'price-sales'})  # normal

            if not tag_price or not tag_price.string:
                tag_price = soup.find('span', {'class': 'salesprice'})  # sales

            price_in_dollar = tag_price.string
            price_in_dollar = float(price_in_dollar.replace('$', ''))

            price_with_tax = price_in_dollar * 1.07
            self.price = int(price_with_tax * self.usd_jpn)

        # set dir_item
        self.dir_item = os.path.join(self.dir_site, self.name)

        # set details
        self.set_details(soup)

        # discount
        tag_msg = soup.find('li', {'class': 'product-message'})
        if tag_msg:
            msg = tag_msg.string
            match = re.search('(\d+)% OFF', msg)
            if match:
                discount_rate = match.group(1)
            #     price_in_dollar *= 1.0 - (float(discount_rate) / 100.0)
                print "[discount]", discount_rate + '%', 'not taken into account!!!'

        # get url for all colors.
        url_all_colors = []
        # print soup.find_all('a')
        for tag in soup.find_all('a'):
            # print tag.has_attr('data-pdpurl')
            if tag.has_attr('data-pdpurl'):
                url_all_colors.append(tag['data-pdpurl'])

        # set url for pictures
        self.pics = []

        for url_one_color in url_all_colors:
            soup_one_color = self.get_soup(url_one_color)
            self.set_pics(soup_one_color)

        if my_price:
            self.profit = int(float(my_price) * 0.946 - self.price - int(self.usps))

        print '[Coach item]', self.name

    def set_details(self, soup):

        self.size = []
        self.details = []

        details = list(soup.find('div', {'class': 'panel-body'}).ul.stripped_strings)
        n = len(details)
        for i in range(n):
            detail_tmp, is_size = self.inch_to_cm(details[i])
            if is_size:
                self.size.append(detail_tmp)
            else:
                self.details.append(detail_tmp.lower())

    def set_pics(self, soup):
        """ for coach (polymorphism) """
        color = soup.find('span', {'class': 'color-name'}).string[2:]
        color = re.sub(r'[/\s]', r'_', color)

        i = 0
        for tag in soup.find_all('img', {'class': 'primary-image'}):

            url_tmp = tag['src'].split('?')[0]
            color_tmp = color + '_' + str(i)

            # if it is a new url, add
            if url_tmp not in [pic[0] for pic in self.pics]:

                # append extension if necessary
                if not color_tmp.endswith('jpg'):
                    color_tmp += '.jpg'
                i += 1
                self.pics.append((url_tmp, color_tmp))

        # for pic in self.pics:
        #     print pic
        # sys.exit(0)

    @staticmethod
    def inch_to_cm(s):
        """ for coach """
        pat1 = '(\d*)\s?(\d)/(\d)"'  # 1/2", 1 1/2"
        pat2 = '(\d+)"'  # 7"

        is_size = False
        match = True
        while match:
            match = re.search(pat1, s)

            if match:
                is_size = True

                if match.group(1):
                    l = float(match.group(1))
                else:
                    l = 0.0

                num = float(match.group(2))
                den = float(match.group(3))

                l += num / den
                l_cm = round(l * 2.54, 1)
                s = re.sub(match.group(), str(l_cm) + 'cm', s)

        match = True
        while match:
            match = re.search(pat2, s)
            if match:
                is_size = True

                l = float(match.group(1))
                l_cm = round(l * 2.54, 1)
                s = re.sub(match.group(), str(l_cm) + 'cm', s)

        return s, is_size

## test case
# url_shop = "http://www.coach.com/coach-designer-accessories-dinosaur-turnlock-wristlet-30-in-glovetanned-leather/55040.html"
# url_shop = "http://www.coach.com/mammoth-necklace/55217.html"
# url_shop = "http://www.coach.com/coach-large-rexy-bag-charm/87459.html"
# url_shop = "http://www.coach.com/coach-designer-keychains-multi-mix-block-bag-charm/65127.html"
# url_shop = "http://www.coach.com/coach-mens-wallets-accordion-wallet-in-signature-canvas/74936.html"
# url_shop = "http://www.coach.com/coach-designer-purses-scout-hobo-in-pebble-leather/34312.html"
url_shop = "http://www.coach.com/coach-small-wristlet-in-wild-hearts-print-coated-canvas/57704.html"
item = CoachItem(url_shop, None)  # No selenium-web-driver
# #
print item.name
print item.in_stock
print item.price
print item.details
print item.size
print item.pics
print item.dir_item
