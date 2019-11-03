# !/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta

import backtrader as bt
import ccxt


class TestStrategy(bt.Strategy):
    params = (
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or bt.num2date(self.data.datetime[0])
            print('%s, %s' % (dt, txt))

    def start(self):
        self.counter = 0
        print('START')

    def prenext(self):
        self.counter += 1
        print('prenext len %d - counter %d' % (len(self), self.counter))
        self.log("data#0: " + str(self.datas[0].datetime[0]))
        self.log("data#1: " + str(self.datas[1].datetime[0]))

    def __init__(self):
        self.macd = bt.indicators.MACDHisto(self.datas[0])
        self.macd2 = bt.indicators.MACDHisto(self.datas[1])

    def next(self):
        self.counter += 1
        price_txt = "Counter: " + str(self.counter) + " Open/Close/High/Low/Volume: " + str(
            self.data0.open[0]) + " - " + str(self.data0.close[0]) + " - " + str(self.data0.high[0]) + " - " + str(
            self.data0.low[0]) + " - " + str(self.data0.volume[0]) + " Len: " + str(len(
            self.data0))  # + " Time Frame:" + bt.TimeFrame.getname(self.data0._timeframe) + " Len: "+ str(len(self.data0))
        self.log(price_txt)
        macd_txt = "MACD: {:.2f}, Histo: {:.2f}".format(self.macd.macd[0], self.macd.histo[0])
        self.log("MACD#1: " + macd_txt)
        macd2_txt = "MACD: {:.2f}, Histo: {:.2f}".format(self.macd2.macd[0], self.macd2.histo[0])
        self.log("MACD#2: " + macd2_txt)


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    exchange = sys.argv[1] if len(sys.argv) > 1 else 'bitstamp'
    # exchange = sys.argv[1] if len(sys.argv) > 1 else 'gateio'
    symbol = sys.argv[2] if len(sys.argv) > 2 else 'ETH/USD'

    hist_start_date = datetime.utcnow() - timedelta(minutes=10)
    print('UTC NOW: ', datetime.utcnow())
    print('hist_start_data: ', hist_start_date)
    print('Using symbol: ', symbol)

    # Create data feeds
    data_1m = bt.feeds.CCXT(exchange=exchange, symbol=symbol, name="1m",
                            timeframe=bt.TimeFrame.Minutes,  # fromdate=hist_start_date,
                            compression=1)
    cerebro.adddata(data_1m)

    cerebro.replaydata(data_1m, timeframe=bt.TimeFrame.Minutes, name="1m", compression=5)

    cerebro.addstrategy(TestStrategy)
    cerebro.run()