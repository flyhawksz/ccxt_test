# -*- coding: utf-8 -*-
# @Time    : 2019-5-20 11:55
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_test.py
# @Software: PyCharm

import ccxt
import pandas as pd
from datetime import datetime
import numpy as np


def create_exchange(exchange_name):
    exchange = getattr(ccxt, exchange_name)()
    # exchange.proxies = {
    #     'http': 'socks5://127.0.0.1:1080',
    #     'https': 'socks5h://127.0.0.1:1080'
    # }
    # if isMac():
    #     exchange.proxies = {
    #         'http': 'http://127.0.0.1:1080',
    #         'https': 'https://127.0.0.1:1080'
    #     }
    exchange.load_markets()
    return exchange


def get_symbol(exchange_name):
    exchange = create_exchange(exchange_name)
    return exchange.symbols

if __name__ == '__main__':
    pass