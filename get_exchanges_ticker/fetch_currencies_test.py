# -*- coding: utf-8 -*-
# @Time    : 2019-9-30 21:07
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : fetch_currencies_test.py
# @Software: PyCharm

import ccxt

good_exchanges = ['bitfinex', 'binance', 'okex', 'poloniex', 'bittrex', 'bitstamp', 'gdax']

def main():
    # # exchange = ccxt.gdax({
    # exchange = ccxt.bitfinex({
    #     'enableRateLimit': True,  # this option enables the built-in rate limiter
    # })
    # markets = exchange.fetch_markets()
    # for i in markets:
    #     print(i)
    for _exchange in good_exchanges:
        symbol = set()
        exchange = getattr(ccxt, _exchange)()
        markets = exchange.fetch_markets()
        for i in markets:
            print(i)
            symbol.add(i['symbol'])

        print(symbol)


if __name__ == '__main__':
    main()
