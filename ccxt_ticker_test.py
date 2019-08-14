# -*- coding: utf-8 -*-
# @Time    : 2019-8-12 10:27
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ticker_test.py
# @Software: PyCharm

import ccxt
import pandas as pd


def make_pair(currencis):
    currencis_pair = []
    for i in range(len(currencis)):
        for currency in currencis:
            if currencis[i] == currency: continue

        currencis_pair.append(currencis[i] + '/' + currency)

    display_list(currencis_pair)
    return currencis_pair


def display_dic(obj):
    for i in obj.keys():
        print(i + ' - ', obj[i])


def display_list(obj):
    for i in obj:
        print(i)

good_coin = ['BTC', 'ETH', 'LTC', 'USD']
good_exchange_name = ['bitfinex', 'bithumb', 'coinbase', 'coinex']


print(ccxt.exchanges)

bitfinex = ccxt.bitfinex()
print(bitfinex)
market = bitfinex.load_markets()
display_dic(market)
# print(market)
symbols = bitfinex.symbols
display_list(symbols)
# print(symbols)
#
btc_ticker = bitfinex.fetch_ticker('BTC/USDT')
display_dic(btc_ticker)
print(btc_ticker)
#
# # tickers = bitfinex.fetch_tickers()
#
# kline_data = bitfinex.fetch_ohlcv('BTC/USDT', timeframe='60m')
# print(kline_data)


