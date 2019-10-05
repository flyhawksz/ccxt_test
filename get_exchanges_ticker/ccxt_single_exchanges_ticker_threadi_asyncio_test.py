# -*- coding: utf-8 -*-
# @Time    : 2019-8-12 10:27
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ticker_test.py
# @Software: PyCharm

import ccxt as accxt
import os
import time
import csv
import datetime
import asyncio
import ccxt.async_support as ccxt  # noqa: E402
import threading


class Price(object):
    exchange = ''
    currency_pair = ''
    timestamp = 0
    bid = 0
    ask = 0
    # bidVolume = 0
    # askVolume = 0

    def get_price_array(self):
        return [self.exchange, self.timestamp, self.currency_pair, self.bid, self.ask, self.bidVolume, self.askVolume]


class GetMultiExchangeTicker:

    def __init__(self):
        self.TIMESTAMP = "%Y%m%d%H%M%S"
        self.good_currencies = ['BTC', 'ETH', 'LTC', 'USDT', 'USD']
        self.good_exchanges = ['gdax', 'bitstamp'] # ['bitfinex', 'binance'] #, # 'okex', 'poloniex', 'bittrex', 'bitstamp', 'gdax']
        self.fieldnames = ['timestamp', 'bid', 'ask']
        self.candidate_exchange_symbol = {}
        self.test_symbol = self.make_pair(self.good_currencies)
        self.root = os.getcwd()
        # 数据文件夹，不存在，就创建
        self.data_path = os.path.join(self.root, 'data\\')
        self.sleep_time = 20

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

    def make_pair(self, currencis):
        currencis_pair = []
        for i in range(len(currencis)):
            for currency in currencis:
                if currencis[i] == currency:continue
                currencis_pair.append(currencis[i] + '/' + currency)

        # display_list(currencis_pair)
        return currencis_pair

    def save_ticker(self, exchange, symbol, _ticker):
        # 处理数据
        temp_price = Price()
        temp_price.timestamp = _ticker['timestamp']
        temp_price.bid = _ticker['bid']
        temp_price.ask = _ticker['ask']
        # temp_price.bidVolume = _ticker['bidVolume']
        # temp_price.askVolume = _ticker['askVolume']

        self.save_in_classify_dir(exchange, symbol, temp_price)
        self.save_in_one_dir(exchange, symbol, temp_price)

    def save_in_classify_dir(self, exchange, symbol, temp_price):
        print('start save ticker in classified dir : {} - {}'.format(exchange, symbol))

        # 按 symbol 分类存数据
        symbol_path = os.path.join(self.data_path, symbol.replace('/', ''))
        symbol_path_file_name = os.path.join(symbol_path, exchange + '.csv')

        if not os.path.exists(symbol_path):
            os.makedirs(symbol_path)

        if not os.path.exists(symbol_path_file_name):
            with open(symbol_path_file_name, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                csv_writer.writeheader()
                print('make header')

        with open(symbol_path_file_name, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            info = {
                'timestamp': temp_price.timestamp,
                'bid': temp_price.bid,
                'ask': temp_price.ask
            }
            csv_writer.writerow(info)

    def save_in_one_dir(self, exchange, symbol, temp_price):
        print('start save ticker in one dir : {} - {}'.format(exchange, symbol))
        filename = exchange + '_' + symbol + '.csv'
        path_file_name = os.path.join(self.data_path, filename.replace('/', ''))
        if not os.path.exists(path_file_name):
            with open(path_file_name, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                csv_writer.writeheader()
                print('make header')

        with open(path_file_name, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            info = {
                'timestamp': temp_price.timestamp,
                'bid': temp_price.bid,
                'ask': temp_price.ask
            }
            csv_writer.writerow(info)

    async def async_ticker(self, _exchange, symbol):

        print('threading {} start get ticker'.format(threading.get_ident()))
        exchange = getattr(ccxt, _exchange)()
        try:
            ticker = await exchange.fetch_ticker(symbol)
            print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)
            print(ticker)
            self.save_ticker(exchange.name, symbol, ticker)
            print(exchange.iso8601(exchange.milliseconds()), 'saved', symbol, 'ticker from', exchange.name)
        except Exception as e:
            print(e)

        # await asyncio.sleep(self.sleep_time)

        # await exchange.close()
        # return market

    def multi_exchanges(self, _exchange):
        print('-'*30)
        print('threading {} start work'.format(threading.get_ident()))
        # print('start get ticker in {}'.format(_exchange))
        exchange = getattr(accxt, _exchange)()
        market = exchange.fetch_markets()

        # 清除symbol ,当市场中没有该值对，跳过
        symbols = set()
        for i in market:
            # print(i)
            symbols.add(i['symbol'])

        print('the symbols in {} is :{}'.format(_exchange, symbols))
        # self.candidate_exchange_symbol[exchange.name] = symbols
        # print(self.candidate_exchange_symbol)

        target_symbols = []
        for symbol in self.test_symbol:
            if symbol in symbols:
                target_symbols.append(symbol)
        print('target_symbols is {}'.format(target_symbols))

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        tasks = [self.async_ticker(_exchange, _symbol) for _symbol in target_symbols]

        try:
            event_loop.run_until_complete(asyncio.wait(tasks))
        finally:
            event_loop.close()

    def main(self):
        # exchanges_thread = []
        for exchange in self.good_exchanges:
            thread = threading.Thread(target=self.multi_exchanges, args=(exchange, ))
            # exchanges_thread.append(thread)
            thread.start()


if __name__ == '__main__':
    test = GetMultiExchangeTicker()
    test.main()
