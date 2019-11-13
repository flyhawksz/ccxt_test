# !/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta
import backtrader as bt
from backtrader import cerebro
import time

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)


#Variable for our starting cash
startcash = 10000


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    hist_start_date = datetime.utcnow() - timedelta(minutes=1000)
    data_min = bt.feeds.CCXT(exchange='binance',
                             symbol="BTC/USDT",
                             name="btc_usd_min",
                             fromdate=hist_start_date,
                             todate=datetime.utcnow(),
                             timeframe=bt.TimeFrame.Minutes
                             )
    cerebro.adddata(data_min)
    cerebro.broker.setcash(startcash)
    cerebro.addstrategy(firstStrategy)
    cerebro.run()

    # Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    # Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))

    # Finally plot the end results
    cerebro.plot(style='candlestick')