# -*- coding: utf-8 -*-
# @Time    : 2019-11-20 17:15
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : backtrader_json_test.py
# @Software: PyCharm


import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import requests
import json
import time
import math
from datetime import datetime
import pandas as pd

import talib

price = 0
prof = 1


def trade_log(self, op):
    global PRICE
    global profit
    global prof
    dt = self.datas[0].datetime.date(0)
    if op == 'buy':
        PRICE = self.dataclose[0]
        print(
            '%s, BUY  Покупка, Price: %.2f' %
            (dt.isoformat(), PRICE)
        )
    if op == 'sell':
        PRICE2 = self.dataclose[0]
        profit = PRICE2 / PRICE - 0.004
        prof = prof * profit
        print('%s, SELL Продажа, Price: %.2f, Cost: %.2f,  Profit: %.3f, Prof: %.3f' %
              (dt.isoformat(), PRICE2, PRICE, profit, prof))


def get_polonix():
    time_depth = 500
    start_day = 500
    st_time = time.time() - start_day * 24 * 60 * 60
    end_time = st_time + time_depth * 60 * 60 * 24
    pair = 'USDT_BTC'

    # resource=requests.get("https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=%s&period=1800" % (pair,st_time,end_time))
    resource = requests.get(
        "https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=%s&period=14400" % (
        pair, st_time, end_time))
    # resource=requests.get("https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=%s&period=300" % (pair,st_time,end_time))
    # resource=requests.get("https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=%s&period=86400" % (pair,st_time,end_time))
    # resource=requests.get("https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=%s&period=21600" % (pair,st_time,end_time))

    data = []
    chart_data = {}
    chart_data = json.loads(resource.text)
    for elems in chart_data:
        data.append(elems)

    df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['openinterest'] = 0
    df['date'] = pd.to_datetime(df['date'], unit='s')
    # df = df[(df['date'] > '2018-1-1') & (df['date'] <= '2018-2-1')]
    # df = df[(df['date'] > '2017-9-1') & (df['date'] <= '2018-1-1')]
    df = df[(df['date'] >= '2018-4-1')]
    df = df.set_index('date')
    # print(df)
    return df


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (('BBandsperiod', 20),)

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.redline = None
        self.blueline = None

        # Add a BBand indicator
        self.bband = bt.indicators.BBands(self.datas[0], period=self.params.BBandsperiod)

        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])

        self.t_macd = bt.talib.MACD(self.datas[0], fastperiod=12, slowperiod=26, signalperiod=9, plotname='MACD')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if self.dataclose < self.bband.lines.bot and not self.position:
            self.redline = True

        if self.dataclose > self.bband.lines.top and self.position:
            self.blueline = True

        # if self.dataclose > self.bband.lines.mid and not self.position and self.redline:

        if (
                self.dataclose > self.bband.lines.mid
                and self.t_macd.macd[0] > 0
                and self.t_macd.macdsignal[0] > 0
                and not self.position and self.redline
        ):
            # BUY, BUY, BUY!!! (with all possible default parameters)
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()

            trade_log(self, 'buy')

            # if self.dataclose > self.bband.lines.top and not self.position:

        if (
                self.dataclose > self.bband.lines.top
                and self.t_macd.macd[0] > 0
                and self.t_macd.macdsignal[0] > 0
                and not self.position
        ):
            # BUY, BUY, BUY!!! (with all possible default parameters)
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()
            trade_log(self, 'buy')
        if self.dataclose < self.bband.lines.mid and self.position and self.blueline:
            # SELL, SELL, SELL!!! (with all possible default parameters)
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.blueline = False
            self.redline = False
            # Keep track of the created order to avoid a 2nd order
            self.order = self.sell()
            trade_log(self, 'sell')


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # atapath = os.path.join(modpath, 'TSLA-USD.csv')

    # Create a Data Feed
    # data = bt.feeds.GenericCSVData(
    # dataname=datapath,
    # Do not pass values before this date
    # fromdate=datetime.datetime(2008, 4, 4),
    # Do not pass values before this date
    # todate=datetime.datetime(2016, 12, 2),

    # nullvalue=0.0,

    # dtformat=('%m/%d/%Y'),

    # datetime=0,
    # high=2,
    # low=3,
    # open=1,
    # close=4,
    # volume=5,
    # openinterest=-1)

    df = get_polonix()
    data = bt.feeds.PandasData(dataname=df)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=5)

    # Set the commission
    cerebro.broker.setcommission(commission=0.002)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot(style='candlestick')

###############################################################
# if ((self.talibb.macd[0] > self.talibb.macdsignal[0]) and (self.talibb.macd[-1] <= self.talibb.macdsignal[-1])) :