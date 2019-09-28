# -*- coding: utf-8 -*-
# @Time    : 2019-9-28 18:08
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : get_ticker_asynic.py
# @Software: PyCharm

# 引入库

import ccxt.async_support as ccxt
# import ccxt.async as ccxt
import asyncio
import time

now = lambda: time.time()
start = now()


async def getData(exchange, symbol):
    data = {}  # 用于存储ticker和depth信息
    # 获取ticker信息
    tickerInfo = await exchange.fetch_ticker(symbol)
    # 获取depth信息
    depth = {}
    # 获取深度信息
    exchange_depth = await exchange.fetch_order_book(symbol)
    # 获取asks,bids 最低5个，最高5个信息
    asks = exchange_depth.get('asks')[:5]
    bids = exchange_depth.get('bids')[:5]
    depth['asks'] = asks
    depth['bids'] = bids

    data['ticker'] = tickerInfo
    data['depth'] = depth

    return data


def main():
    # 实例化市场
    exchanges = [ccxt.binance(), ccxt.bitfinex2(), ccxt.okex(), ccxt.gdax()]
    # 交易对
    symbols = ['BTC/USDT', 'BTC/USD', 'BTC/USDT', 'BTC/USD']

    tasks = []
    for i in range(len(exchanges)):
        task = getData(exchanges[i], symbols[i])
        tasks.append(asyncio.ensure_future(task))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    main()
    print('Run Time: %s' % (now() - start))