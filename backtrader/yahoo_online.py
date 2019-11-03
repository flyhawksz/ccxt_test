# -*- coding: utf-8 -*-
# @Time    : 2019-11-2 11:15
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : yahoo_online.py
# @Software: PyCharm

from __future__ import (absolute_import, division, print_function,
                    unicode_literals)
from datetime import datetime, timedelta
import backtrader as bt


class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(period=14)
        self.sma = bt.indicators.SMA(period=15)

    def next(self):
        self.log('rsi:{}'.format(self.rsi[0]))
        self.log('sma:{}'.format(self.sma[0]))


if __name__ == '__main__':

    cerebro = bt.Cerebro()
    data = bt.feeds.YahooFinanceData(
         dataname='AAPL',
         fromdate = datetime(2019,1,1),
         todate = datetime(2019,2,1),
         buffered= True
         )


    cerebro.adddata(data)
    cerebro.addstrategy(TestStrategy)
    cerebro.run()
    cerebro.plot()