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
import csv
import time
import pandas as pd


class GetStockData163(object):
    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象
        # Crawler.__init__(self)
        self.list_url = "http://quote.eastmoney.com/stock_list.html"
        self.data_path = os.path.join(os.getcwd(), 'datas')

        self.fields = 'date', 'TCLOSE', 'HIGH', 'LOW', 'TOPEN', 'LCLOSE', 'CHG', 'PCHG',\
                      'TURNOVER', 'OTURNOVER', 'VATURNOVER', 'TCAP', 'MCAP'


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
            # print(stock.text)
            reg = r'\((.*)\)'
            searchObj = re.search(reg, stock.text)
            if searchObj:
                print(searchObj.group(1))
                stock_code_list.append(searchObj.group(1))
        return stock_code_list


class DownloadHistoryStock(object):

    def __init__(self, code):
        self.code = code
        self.data_path = os.path.join(os.getcwd(), 'datas')
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        # self.start_url = "http://quotes.money.163.com/trade/lsjysj_" + self.code + ".html"
        # print(self.start_url)
        # self.headers = {
        #     "User-Agent": ":Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        # }

    # def parse_url(self):
    #
    #     response = requests.get(self.start_url)
    #     print(response.status_code)
    #     if response.status_code == 200:
    #         return etree.HTML(response.content)
    #     return False
    #
    # def get_date(self, response):
    #     # 得到开始和结束的日期
    #     start_date = ''.join(response.xpath('//input[@name="date_start_type"]/@value')[0].split('-'))
    #     end_date = ''.join(response.xpath('//input[@name="date_end_type"]/@value')[0].split('-'))
    #     return start_date,end_date

    def download(self, start_date, end_date):
        download_url = "http://quotes.money.163.com/service/chddata.html?code=0" + \
                       self.code+"&start="+start_date+"&end="+end_date\
                       + "&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"
        data = requests.get(download_url)
        filename = self.code + '.csv'
        path_file_name = os.path.join(self.data_path, filename.replace('/', ''))
        f = open(path_file_name, 'wb')

        for chunk in data.iter_content(chunk_size=10000):
            if chunk:
                f.write(chunk)
        print('股票---', self.code, '历史数据正在下载')

    def run(self):
        try:
            # html = self.parse_url()
            # start_date,end_date = self.get_date(html)
            self.download('20150101', '20191108')
        except Exception as e:
            print(e)


def download_stock_history(code, start_date, end_date):
    download_url = "http://quotes.money.163.com/service/chddata.html?code=0" + \
                   code+"&start="+start_date+"&end="+end_date\
                   + "&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"
    data = requests.get(download_url)
    filename = code + '.csv'
    path_file_name = os.path.join(data_path, filename.replace('/', ''))
    f = open(path_file_name, 'wb')

    for chunk in data.iter_content(chunk_size=10000):
        if chunk:
            f.write(chunk)
    print('股票---', code, '历史数据正在下载')


def write_list_txtfile(list, filename):
    # print(proxies)
    for t_list in list:
        # with as 语法的使用，可以省去close文件的过程
        with open(filename, 'a+', encoding="UTF-8") as f:
            f.write(t_list + ',')
    print("Finish Writing!!!")


if __name__ == '__main__':
    data_path = os.path.join(os.getcwd(), 'datas')
    stock_list_filepath = os.path.join(os.getcwd(), 'datas\\') + 'stock_code.csv'
    stock_list = []
    if not os.path.exists(stock_list_filepath):
        operation = GetStockData163()
        stock_list = operation.get_stock_code_list()
        write_list_txtfile(stock_list, stock_list_filepath)
        # test = pd.DataFrame(columns=['Code'], data=stock_list)
        # test = pd.DataFrame(data=stock_list)
        # # print(test)
        # test.to_csv(stock_list_filepath, encoding='utf-8')
    else:
        # # 将txt中所有信息读到list中，
        # with open(stock_list_filepath, 'r') as f:
        #     stock_list = f.readlines()  # 读取全部内容
        stock_list = csv.reader(stock_list_filepath)
        print(stock_list)

    for Code in stock_list:
        Code.strip("\n")
        print(Code)
        if Code.startswith('5') or Code.startswith('20'):
            pass
        else:
            time.sleep(1)
            download_stock_history(Code, '20150101', '20191108')


        # name = ['日期','股票代码','名称','收盘价','最高价','最低价','开盘价','前收盘','涨跌额','涨跌幅','换手率','成交量','成交金额','总市值','MCAP']
