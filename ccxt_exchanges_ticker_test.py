# -*- coding: utf-8 -*-
# @Time    : 2019-8-12 10:27
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ticker_test.py
# @Software: PyCharm

import ccxt
import pandas as pd
import time
import datetime


class Price(object):
    exchange = ''
    currency_pair = ''
    timestamp = 0
    bid = 0
    ask = 0
    bidVolume = 0
    askVolume = 0

    def get_price_array(self):
        return [self.exchange, self.timestamp, self.currency_pair, self.bid, self.ask, self.bidVolume, self.askVolume]


def make_pair(currencis):
    currencis_pair = []
    for i in range(len(currencis)):
        for currency in currencis:
            if currencis[i] == currency: continue
            currencis_pair.append(currencis[i] + '/' + currency)

    # display_list(currencis_pair)
    return currencis_pair


def get_ticker(price_matrix, obj_exchange, currencies_pair):
    _tickers = []
    _exchange = getattr(ccxt, obj_exchange)()
    if _exchange:
        temp_price = Price()

        market = _exchange.load_markets()
        # display_dic(market)
        # print(market)
        symbols = _exchange.symbols
        # display_list(symbols)
        # print(symbols)
        for pair in currencies_pair:
            temp_price.exchange = _exchange.name
            temp_price.currency_pair = pair

            if pair in symbols:
                _ticker = _exchange.fetch_ticker(pair)
                temp_price.timestamp = _ticker['timestamp']
                temp_price.bid = _ticker['bid']
                temp_price.ask = _ticker['ask']
                temp_price.bidVolume = _ticker['bidVolume']
                temp_price.askVolume = _ticker['askVolume']
                # _tickers.append(_ticker)
                # display_dic(ticker)
                # print(ticker)
            price_matrix.append(temp_price.get_price_array())

        return price_matrix


def display_dic(obj):
    for i in obj.keys():
        print(i + ' - ', obj[i])


def display_list(obj):
    for i in obj:
        print(i)


good_currencies = ['BTC', 'ETH', 'LTC', 'USDT']
good_exchanges = ['bitfinex', 'binance', 'okex', 'poloniex', 'bittrex', 'bitstamp', 'gdax']


# display_list(ccxt.exchanges)

if __name__ == '__main__':
    price_matrix = []
    data = []
    test_currencies_pair = make_pair(good_currencies)
    for i in range(len(good_exchanges)):
        print('------------------------' + good_exchanges[i] + '--------------------------')
        data.append(get_ticker(price_matrix, good_exchanges[i], test_currencies_pair))
        # print(data[i])
    df = pd.Dataframe(data)
    # print(data)
    writer = pd.ExcelWriter('output_%s.xlsx' % datetime.date.today())
    df.to_excel(writer, 'all')
    writer.save()
    writer.close()




