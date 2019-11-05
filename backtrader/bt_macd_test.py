from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd
# Import the backtrader platform
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds


# Create a subclass of Strategy to define the indicators and logic
class CdmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # self.K = bt.indicators.StochasticFast(self.data)
        self.kdj = bt.indicators.StochasticFull(self.data)

        self.dif = bt.indicators.EMA(self.data, period=self.p.macd1) -bt.indicators.EMA(self.data, period=self.p.macd2)
        self.dea = bt.indicators.EMA(self.dif, period=self.p.macdsig)
        self.my_macd = (self.dif - self.dea) * 2

        self.total_funds = 0
        self.used_funds = 0
        self.available_funds = 0
        # self.position = 0

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        if self.order:
            return  # pending order execution

        self.log('fund value:{}'.format(self.broker.get_fundvalue()))
        self.log('CASH:{}'.format(self.broker.get_cash()))
        self.log('value:{}'.format(self.broker.get_value()))
        # self.log('fundvalue:{}'.format(self.broker.get_fundvalue()))
        self.log('postion:{}'.format(self.position.size))

        if self.macd.macd[0] > 0:
            self.log('macd:{}'.format(self.macd.macd[0]))
            self.log('dif:{}'.format(self.dif[0]))

        if self.macd.signal[0] > 0:
            self.log('signal:{}'.format(self.macd.signal[0]))
            self.log('dea:{}'.format(self.dea[0]))

        # 如果macd.dif >0
        if self.dif[0] > 0:
            # 1、dif上穿过零轴
            if self.dif[-1] < 0:
                # BUY, BUY, BUY!!! (with all possible default parameters)

                # Keep track of the created order to avoid a 2nd order
                self.buy(exectype=bt.Order.Market)  # default if not given

                self.log('BUY CREATE, exectype Market, price %.2f' %
                         self.data.close[0])

                # 如果 dea > 0
                if self.dea[0] > 0:
                    # （1）dea上穿过零轴
                    if self.dea[-1] < 0:
                        # BUY, BUY, BUY!!! (with all possible default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

                    # dea正常在零轴上方
                    else:
                        pass

            # 在零轴下方
            else:
                # 死叉
                if self.dif[-1] > 0:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    self.sell(exectype=bt.Order.Market)  # default if not given

                    self.log('SELL CREATE, exectype Market, price %.2f' %
                             self.data.close[0])
                    # self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    # Keep track of the created order to avoid a 2nd order
                    # self.order = self.sell()



                # dif 过零轴

                # dea 过零轴

                # （2）下穿
                if self.dif[-1] > 0:
                    pass
                else:
                    pass
                # dea 过零轴
                if self.dea[-1] > 0:
                    pass
                else:
                    pass
                # 2、dif下穿过零轴
                # 2、发生金叉
            # 如果 dea < 0
            if self.dea[0] < 0:
                if self.dif[-1] < 0:
                    pass
                else:
                    pass


        else:
            # 如果 dea > 0
            if self.dea[0] > 0:
                pass
            # 如果 dea < 0
            if self.dea[0] < 0:
                pass

            # 如果macd.dif <0, dea <0

        # self.log('dif:{}'.format(self.dif[0]))
        # self.log('dea:{}'.format(self.dea[0]))
        # if self.macd.
        # if not self.position:  # not in the market
        #     if self.mcross[0] > 0.0 and self.smadir < 0.0:
        #         self.order = self.buy()
        #         # pdist = self.atr[0] * self.p.atrdist
        #         # self.pstop = self.data.close[0] - pdist
        #
        # else:  # in the market
        #     pclose = self.data.close[0]
        #     pstop = self.pstop
        #
        #     if pclose < pstop:
        #         self.close()  # stop met - get out
        #     else:
        #         pdist = self.atr[0] * self.p.atrdist
        #         # Update only if greater than
        #         self.pstop = max(pstop, pclose - pdist)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
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

            # self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def notify_cashvalue(self, cash, value):
        self.log('Cash %s Value %s' % (cash, value))

    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.log('BUY SIZE %s' % size)
        self.buy(size=size)

    # def stop(self):
    #     # calculate the actual returns
    #     self.roi = (self.broker.get_value() / self.val_start) - 1.0
    #     print('ROI:        {:.2f}%'.format(100.0 * self.roi))

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # cerebro.addstrategy(SmaCross)
    cerebro.addstrategy(CdmaCross)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere

    modpath = os.path.join(os.getcwd(), 'datas')
    if not os.path.exists(modpath):
        os.makedirs(modpath)
    datapath = os.path.join(modpath, '601857-2007-2019.csv')

    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    dataframe['openinterest'] = 0
    data = bt.feeds.PandasData(dataname=dataframe,
                               fromdate=datetime.datetime(2018, 1, 1),
                               todate=datetime.datetime(2019, 10, 31)
                               )
    # ————————————————
    # 版权声明：本文为CSDN博主「钱塘小甲子」的原创文章，遵循
    # CC
    # 4.0
    # BY - SA
    # 版权协议，转载请附上原文出处链接及本声明。
    # 原文链接：https: // blog.csdn.net / qtlyx / article / details / 70945174

    # Create a Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath,
    #     # Do not pass values before this date
    #     fromdate=datetime.datetime(2014, 2, 1),
    #     # Do not pass values before this date
    #     todate=datetime.datetime(2014, 12, 31),
    #     # Do not pass values after this date
    #     reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
