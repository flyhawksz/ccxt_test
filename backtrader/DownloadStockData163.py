# -*- coding: utf-8 -*-
# @Time    : 2019-11-9 10:50
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : DownloadStockData163.py
# @Software: PyCharm

import requests
import re
import os
# from Crawl import Crawler
from lxml import etree


class GetStockData163(object):
    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象
        # Crawler.__init__(self)
        self.list_url = "http://quote.eastmoney.com/stock_list.html"

    def getHTMLText(self, url):
        try:
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            return ""

    # # 获取股票代码列表
    def get_stock_code_list(self):
        stock_code_list = []
        # html = urllib.request.urlopen(url).read()

        html = self.getHTMLText(self.list_url)

        selector = etree.HTML(html)
        s = r'/html/body/div[9]/div[2]/div/ul[1]/li/a'
        for stock in selector.xpath(s):
            print(stock.text)
            reg = r'\((.*)\)'
            searchObj = re.search(reg, stock.text)
            if searchObj:
                print(searchObj.group(1))
                stock_code_list.append(searchObj.group(1))
        return stock_code_list


if __name__ == '__main__':
    operation = GetStockData163()
    stock_list = operation.get_stock_code_list()

    # print(stock_list)
