# -*- coding: utf-8 -*-
# @Time    : 2019-9-28 18:17
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ticker_async_mango.py
# @Software: PyCharm

import asyncio
import ccxt.async_support as ccxt
import time
import pymongo


# 获取ticker和depth信息
async def get_exchange_tickerDepth(exchange, symbol):  # 其中exchange为实例化后的市场
    # print('start get_ticker')
    while True:
        print('%s is run %s' % (exchange.id, time.ctime()))

        # 获取ticher信息
        tickerInfo = await exchange.fetch_ticker(symbol)
        ticker = tickerInfo.get('info')

        if type(ticker) == type({}):
            ticker['timestamp'] = tickerInfo.get('timestamp')
            ticker['high'] = tickerInfo.get('high')
            ticker['low'] = tickerInfo.get('low')
            ticker['last'] = tickerInfo.get('last')
        else:
            ticker = tickerInfo
        # print(ticker)

        # 获取深度信息
        depth = {}
        exchange_depth = await exchange.fetch_order_book(symbol)
        # 获取asks,bids 最低5个，最高5个信息
        asks = exchange_depth.get('asks')[:5]
        bids = exchange_depth.get('bids')[:5]
        depth['asks'] = asks
        depth['bids'] = bids
        # print('depth:{}'.format(depth))
        data = {
            'exchange': exchange.id,
            'countries': exchange.countries,
            'symbol': symbol,
            'ticker': ticker,
            'depth': depth
        }

        # 保存数据
        save_exchangeDate(exchange.id, data)
        print('********* %s is finished, time %s *********' % (exchange.id, time.ctime()))

        # 等待时间
        await asyncio.sleep(2)


# 存库
def save_exchangeDate(exchangeName, data):
    # 链接MongoDB
    connect = pymongo.MongoClient(host='localhost', port=27017)
    # 创建数据库
    exchangeData = connect['exchangeDataAsyncio']
    # 创建表
    exchangeInformation = exchangeData[exchangeName]
    # print(table_name)
    # 数据去重后保存
    count = exchangeInformation.count()
    if not count > 0:
        exchangeInformation.insert_one(data)
    else:
        for item in exchangeInformation.find().skip(count - 1):
            lastdata = item
        if lastdata['ticker']['timestamp'] != data['ticker']['timestamp']:
            exchangeInformation.insert_one(data)


def main():
    exchanges = [ccxt.binance(), ccxt.bitfinex2(), ccxt.okex(),
                 ccxt.gdax()]
    symbols = ['BTC/USDT', 'BTC/USD', 'BTC/USDT', 'BTC/USD']
    tasks = []
    for i in range(len(exchanges)):
        task = get_exchange_tickerDepth(exchanges[i], symbols[i])
        tasks.append(asyncio.ensure_future(task))

    loop = asyncio.get_event_loop()

    try:
        # print(asyncio.Task.all_tasks(loop))
        loop.run_forever()

    except Exception as e:
        print(e)
        loop.stop()
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()