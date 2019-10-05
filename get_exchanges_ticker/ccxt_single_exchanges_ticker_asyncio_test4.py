# -*- coding: utf-8 -*-
# @Time    : 2019-8-12 10:27
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ticker_test.py
# @Software: PyCharm

# import ccxt
import time
import csv
import datetime
import asyncio
import ccxt.async_support as ccxt  # noqa: E402


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


class GetMultiExchangeTicker:

    def __init__(self):
        self.TIMESTAMP = "%Y%m%d%H%M%S"
        self.good_currencies = ['BTC', 'ETH', 'LTC', 'USDT', 'USD']
        self.good_exchanges = ['bitfinex', 'binance'] #, # 'okex', 'poloniex', 'bittrex', 'bitstamp', 'gdax']
        self.fieldnames = ['timestamp', 'bid', 'ask', 'bidVolume', 'askVolume']
        self.candidate_exchange_symbol = {}
        self.test_symbol = self.make_pair(self.good_currencies)

    def make_pair(self, currencis):
        currencis_pair = []
        for i in range(len(currencis)):
            for currency in currencis:
                if currencis[i] == currency: continue
                currencis_pair.append(currencis[i] + '/' + currency)

        # display_list(currencis_pair)
        return currencis_pair

    async def get_ticker(self, exchange, symbol):
        exchange = getattr(ccxt, _exchange)()

        temp_price = Price()
        temp_price.exchange = exchange.name
        temp_price.currency_pair = symbol

        while True:
            print('--------------------------------------------------------------')
            print(exchange.iso8601(exchange.milliseconds()), 'fetching', symbol, 'ticker from', exchange.name)
            # this can be any call instead of fetch_ticker, really
            try:
                ticker = await exchange.fetch_ticker(symbol)
                print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)
                print(ticker)
            except ccxt.RequestTimeout as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                # will retry
            except ccxt.DDoSProtection as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeNotAvailable as e:
                print('[' + type(e).__name__ + ']')
                print(str(e.args)[0:200])
                # will retry
            except ccxt.ExchangeError as e:
                print('[' + type(e).__name__ + ']')
                print(str(e)[0:200])
                # break  # won't retry

            # temp_price.timestamp = ticker['timestamp']
            # temp_price.bid = ticker['bid']
            # temp_price.ask = ticker['ask']
            # temp_price.bidVolume = ticker['bidVolume']
            # temp_price.askVolume = ticker['askVolume']
            #
            # with open(exchange + '_' + symbol + '.csv', 'w') as csv_file:
            #     csv_writer = csv.DictWriter(csv_file, \
            #                                 fieldnames=fieldnames)
            #     csv_writer.writeheader()
            #
            # with open(exchange + '_' + symbol + '.csv', 'a') as csv_file:
            #     csv_writer = csv.DictWriter(csv_file, \
            #                                 fieldnames=fieldnames)
            #     info = {
            #         'timestamp': temp_price.timestamp,
            #         'bid': temp_price.bid,
            #         'ask': temp_price.ask,
            #         'bidVolume': temp_price.bidVolume,
            #         'askVolume': temp_price.askVolume
            #     }
            #     csv_writer.writerow(info)

        # await asyncio.sleep(60)
        await exchange.close()

    # async def save_ticker(temp_price, exchange, symbol, _ticker):
    #         temp_price.timestamp = _ticker['timestamp']
    #         temp_price.bid = _ticker['bid']
    #         temp_price.ask = _ticker['ask']
    #         temp_price.bidVolume = _ticker['bidVolume']
    #         temp_price.askVolume = _ticker['askVolume']
    #
    #         with open(exchange + '_' + symbol + '.csv', 'w') as csv_file:
    #             csv_writer = csv.DictWriter(csv_file, \
    #                                         fieldnames=fieldnames)
    #             csv_writer.writeheader()
    #
    #
    #         with open(exchange + '_' + symbol + '.csv', 'a') as csv_file:
    #             csv_writer = csv.DictWriter(csv_file, \
    #                                         fieldnames=fieldnames)
    #             info = {
    #                 'timestamp': temp_price.timestamp,
    #                 'bid': temp_price.bid,
    #                 'ask': temp_price.ask,
    #                 'bidVolume': temp_price.bidVolume,
    #                 'askVolume': temp_price.askVolume
    #             }
    #             csv_writer.writerow(info)

    async def async_ticker(self, _exchange):
        print('start get ticker in {}'.format(_exchange))
        exchange = getattr(ccxt, _exchange)()
        market = await exchange.fetch_markets()

        # 清除symbol ,当市场中没有该值对，跳过
        symbol = set()
        for i in market:
            # print(i)
            symbol.add(i['symbol'])

        # print('the symbols in {} is :{}'.format(_exchange.name, symbol))
        self.candidate_exchange_symbol[exchange.name] = symbol

        for pair in self.test_symbol:
            if pair in symbol:
                print(pair)
                try:
                    ticker = await exchange.fetch_ticker(pair)
                    print(exchange.iso8601(exchange.milliseconds()), 'fetched', pair, 'ticker from', exchange.name)
                    print(ticker)
                except ccxt.RequestTimeout as e:
                    print('[' + type(e).__name__ + ']')
                    print(str(e)[0:200])
                    # will retry
                except ccxt.DDoSProtection as e:
                    print('[' + type(e).__name__ + ']')
                    print(str(e.args)[0:200])
                    # will retry
                except ccxt.ExchangeNotAvailable as e:
                    print('[' + type(e).__name__ + ']')
                    print(str(e.args)[0:200])
                    # will retry
                except ccxt.ExchangeError as e:
                    print('[' + type(e).__name__ + ']')
                    print(str(e)[0:200])
                    # break  # won't retry

        await exchange.close()
        # return market

    async def multi_exchanges(self):
        tasks = [self.async_ticker(exchange) for exchange in self.good_exchanges]
        ticker = await asyncio.wait(tasks)

    def display_dic(self, obj):
        for i in obj.keys():
            print(i + ' - ', obj[i])

    def display_list(self, obj):
        for i in obj:
            print(i)

    def main(self):
        event_loop = asyncio.get_event_loop()
        try:
            # return_value = event_loop.run_until_complete(self.multi_exchanges())
            event_loop.run_until_complete(self.multi_exchanges())
            # print('result value: {!r}'.format(return_value))
        finally:
            event_loop.close()


if __name__ == '__main__':
    test = GetMultiExchangeTicker()
    test.main()
