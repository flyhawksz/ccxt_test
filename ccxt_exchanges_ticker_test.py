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


def get_ticker(obj_exchange, currencies_pair):
    _tickers = []
    _exchange = getattr(ccxt, obj_exchange)()
    if _exchange:
        market = _exchange.load_markets()
        # display_dic(market)
        # print(market)
        symbols = _exchange.symbols
        # display_list(symbols)
        # print(symbols)
        for pair in currencies_pair:
            if pair in symbols:
                _tickers.append(_exchange.fetch_ticker(pair))
                # display_dic(ticker)
                # print(ticker)
        return _tickers


def display_dic(obj):
    for i in obj.keys():
        print(i + ' - ', obj[i])


def display_list(obj):
    for i in obj:
        print(i)


good_currencies = ['BTC', 'ETH', 'LTC', 'USDT']
good_exchanges = ['bitfinex', 'binance', 'okex']

display_list(ccxt.exchanges)

if __name__ == '__main__':
    test_currencies_pair = make_pair(good_currencies)
    for exchange in good_exchanges:
        print('------------------------' + exchange + '--------------------------')
        tickers = get_ticker(exchange, test_currencies_pair)
        display_list(tickers)



