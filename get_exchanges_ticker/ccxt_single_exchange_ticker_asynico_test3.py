# -*- coding: utf-8 -*-
# @Time    : 2019-5-23 15:33
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : async_tickers_from_many_exchanges.py
# @Software: PyCharm

# -*- coding: utf-8 -*-

import asyncio
import ccxt
import ccxt.async_support as ccxta  # noqa: E402
import time
import os
import sys
import pprint

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')


def make_pair(currencis):
    currencis_pair = []
    for i in range(len(currencis)):
        for currency in currencis:
            if currencis[i] == currency: continue
            currencis_pair.append(currencis[i] + '/' + currency)

    # display_list(currencis_pair)
    return currencis_pair


async def async_client(exchange):
    client = getattr(ccxta, exchange)()
    market = client.fetch_markets()

    # 清除symbol ,当市场中没有该值对，跳过
    symbol = set()
    # exchange = getattr(ccxt, _exchange)()
    # markets = exchange.fetch_markets()
    # print(markets)
    for i in market:
        # print(i)
        _symbol = i['symbol']
        print(_symbol)
        symbol.add(_symbol)
    print(symbol)
    tasks = [async_ticker(exchange, _symbol) for _symbol in symbol]
    tickers = await asyncio.gather(*tasks, return_exceptions=True)
    print(tickers)
    await client.close()
    # return tickers


async def multi_tickers(exchanges):
    input_coroutines = [async_client(exchange) for exchange in exchanges]
    tickers = await asyncio.gather(*input_coroutines, return_exceptions=True)
    return tickers


if __name__ == '__main__':

    # Consider review request rate limit in the methods you call
    exchanges = ['gdax', 'coinex'] #["coinex", "bittrex", "bitfinex", "poloniex", "hitbtc"]
    good_currencies = ['BTC', 'ETH', 'LTC', 'USDT']

    tic = time.time()
    a = asyncio.get_event_loop().run_until_complete(multi_tickers(exchanges))

    print("async call spend:", time.time() - tic)

    time.sleep(1)

    # tic = time.time()
    # a = [sync_client(exchange) for exchange in exchanges]
    # print("sync call spend:", time.time() - tic)