#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqi
@contact: fly-hawk@126.com
@file: throgh_api_feed.py
@time: 2019/11/13 8:54 PM
@desc:
'''


from __future__ import (absolute_import, division, print_function,
                    unicode_literals)
from datetime import datetime, timedelta
import backtrader as bt
from bittrex.bittrex import Bittrex # ,API_V2_0
import pandas as pd


class TestStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(period=14)
        self.sma = bt.indicators.SMA(period=15)


if __name__ == '__main__':

    cerebro = bt.Cerebro()
    # data = bt.feeds.YahooFinanceData(
    #     dataname='AAPL',
    #     fromdate = datetime(2019,1,1),
    #     todate = datetime(2020,1,1),
    #     buffered= True
    # )
    trade = 'BTC'
    currency = 'DOGE'
    market = '{0}-{1}'.format(trade, currency)
    tick_interval = 'day'
    my_bittrex = Bittrex(None, None)  # or defaulting to v1.1 as Bittrex(None, None)

    t = my_bittrex.get_ticker(market)

    df = pd.DataFrame(t['result'])
    df['T'] = pd.to_datetime(df['T'])
    df.set_index(df['T'], inplace=True)

    df.columns = ['BV', 'close', 'high', 'low', 'open', 'datetime', 'volume']

    df['openinterest'] = 0

    data = bt.feeds.PandasData(dataname=df, datetime=-1, open=-1, high=-1, low=-1, close=-1, volume=-1,
                               openinterest='openinterest', timeframe=bt.TimeFrame.Days, compression=1)
    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    cerebro.run()
    cerebro.plot()