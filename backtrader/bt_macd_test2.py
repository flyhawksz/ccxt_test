from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd
# Import the backtrader platform
import backtrader as bt
import math


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
        ("psar_period", 2),
        ("af", 0.02),
        ("afmax", 0.2)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.bull_percentage = [0.25, 0.50, 0.75, 1.00]
        self.bear_percentage = [0.00, 0.15, 0.35, 0.50]
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.sar = bt.ind.PSAR(self.data, period=self.p.psar_period, af=self.p.af, afmax=self.p.afmax)

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # self.K = bt.indicators.StochasticFast(self.data)
        # self.kdj = bt.indicators.StochasticFull(self.data)

        self.dif = bt.indicators.EMA(self.data, period=self.p.macd1) - bt.indicators.EMA(self.data, period=self.p.macd2)
        self.dea = bt.indicators.EMA(self.dif, period=self.p.macdsig)
        self.my_macd = self.dif - self.dea

        self.macd_cross = bt.indicators.CrossOver(self.dif, self.dea)

        # self.dif_cross_zero = bt.indicators.CrossOver(self.dif, 0)
        self.dif_cross_up = bt.indicators.CrossUp(self.dif, 0)
        self.dif_cross_down = bt.indicators.CrossDown(self.dif, 0)
        # self.dea_cross_zero = bt.indicators.CrossOver(self.dea, 0)
        self.dea_cross_up = bt.indicators.CrossUp(self.dea, 0)
        self.dea_cross_down = bt.indicators.CrossDown(self.dea, 0)

        self.small_adjust = 0
        self.buy_position = 0
        self.buy_position_percentage = 0
        self.sell_position = 0
        self.sell_position_percentage = 0

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        buy_flag = None
        # update postion percentage
        self.update_position()

        if self.order:
            return  # pending order execution

        # self.log('dif cross zero:{},{} dea cross zero: {},{}'.format(
        #     self.dif_cross_up, self.dif_cross_down, self.dea_cross_up, self.dea_cross_down))

        if self.macd_cross[0] > 0:
            buy_flag = 1
            self.small_adjust = 0
            self.log('出现金叉，可用头寸：{}，已持仓位：{}'.format(
                self.buy_position, self.position.size * self.data.close[0]))
        elif self.dif_cross_up[0] > 0:
            buy_flag = 1
            self.small_adjust = 0
            self.log('DIF上穿零轴，可用头寸：{}，已持仓位：{}'.format(
                self.buy_position, self.position.size * self.data.close[0]))
        elif self.dea_cross_up[0] > 0:
            buy_flag = 1
            self.small_adjust = 0
            self.log('DEA上穿零轴，可用头寸：{}，已持仓位：{}'.format(
                self.buy_position, self.position.size * self.data.close[0]))
        # macd 为正，多头。如正得越来越多，以buy_percentage 为基础，不断增加头寸。但不超过本档上限
        #                 如果正得越来越少，已不buy_percentage 为基础，逐渐头寸。但不超过本档下限
        elif self.my_macd > 0:
            if self.my_macd[0] >= self.my_macd[-1]:  # 持续增
                self.small_adjust = self.small_adjust + 0.02
                if self.get_buy_volume() > self.data.close[0]:
                    buy_flag = 1
                    self.log('macd为正递增，可用头寸：{}，已持仓位：{}'.format(
                        self.buy_position, self.position.size * self.data.close[0]))
            elif self.my_macd[0] < self.my_macd[-1]:
                self.small_adjust = self.small_adjust - 0.02
                if self.get_sell_volume() > self.data.close[0]:
                    buy_flag = 0
                    self.log('madc为正递减，可用头寸：{}，已持仓位：{}'.format(
                        self.sell_position, self.position.size * self.data.close[0]))

        if self.macd_cross[0] < 0:
            # 当跨档时，微调清零
            self.small_adjust = 0
            buy_flag = 0
            self.log('出现死叉，可用头寸：{}，已持仓位：{}'.format(
                self.sell_position, self.position.size * self.data.close[0]))
        elif self.dif_cross_down[0] > 0:
            self.small_adjust = 0
            buy_flag = 0
            self.log('DIF下穿零轴，可用头寸：{}，已持仓位：{}'.format(
                self.sell_position, self.position.size * self.data.close[0]))
        elif self.dea_cross_down[0] > 0:
            self.small_adjust = 0
            buy_flag = 0
            self.log('DEA下穿零轴，可用头寸：{}，已持仓位：{}'.format(
                self.sell_position, self.position.size * self.data.close[0]))
        # macd 为负，空头。如负得越来越多，已sell_percentage 为基础，不断减少头寸。
        elif self.my_macd[0] < 0:
            # if self.my_macd[0] > self.my_macd[-1]:
            #     if self.get_buy_volume() > self.data.close[0]:
            #         buy_flag = 1
            #         self.small_adjust = self.small_adjust + 0.02
            #         self.buy(exectype=bt.Order.Market, size=self.get_buy_vol())  # default if not given
            #         self.log('macd持续增，可用头寸：{}，已持仓位：{}'.format(self.sell_position,
            #                                            self.position.size * self.data.close[0]))
            if self.my_macd[0] < self.my_macd[-1]:
                if self.get_sell_volume() > self.data.close[0]:
                    buy_flag = 0
                    self.small_adjust = self.small_adjust + 0.02
                    self.log('madc为负递减，持续卖，可用头寸：{}，已持仓位：{}'.format(
                        self.sell_position, self.position.size * self.data.close[0]))

        if buy_flag:
            self.buy(exectype=bt.Order.Market, size=self.get_buy_vol())  # default if not given
            self.log('BUY CREATE, exectype Market, price {}， size {}'.format(
                self.data.close[0], self.get_buy_volume()))
        else:
            self.sell(exectype=bt.Order.Market, size=self.get_sell_volume())  # default if not given
            self.log('SELL CREATE, exectype Market, price{}, size {}'.format(
                self.data.close[0], self.get_sell_volume()))

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
        # self.available_funds = self.get_position()
        self.log('Cash %.2f Value %.2f Position %.2f Size %s Price %.2f'
                 % (cash, value, self.position.size * self.position.price,
                    self.position.size, self.position.price))

    # def nextstart(self):
    #     # Buy all the available cash
    #     size = int(self.broker.get_cash() / self.data)
    #     self.log('BUY SIZE %s' % size)
    #     self.buy(size=size)

    # def stop(self):
    #     # calculate the actual returns
    #     self.roi = (self.broker.get_value() / self.val_start) - 1.0
    #     print('ROI:        {:.2f}%'.format(100.0 * self.roi))

    def update_position(self):
        _value = self.broker.get_value()
        self.sell_position_percentage = self.get_lower_percent()
        self.sell_position = _value* self.sell_position_percentage
        self.buy_position_percentage = self.get_upper_percent()
        self.buy_position = _value* self.buy_position_percentage

    # 计算应持仓位（头寸）
    def get_upper_percent(self):
        # 投资占头寸的上限
        _invest_per = 0
        _per = 0
        # 牛
        if 0 > self.dif > self.dea:
            _per = 0
        elif self.dif > 0 > self.dea:
            _per = 1
        elif self.dea >= 0:
            _per = 2
            # if self.dif > self.dea:
            #     _invest_per = self.bull_percentage['多多']

        _invest_per = self.bull_percentage[_per]

        return _invest_per

    # 计算应持仓位（头寸）
    def get_lower_percent(self):
        # 投资占头寸的上限
        _invest_per = 0
        _per = 0
        # 牛
        if self.dea > self.dif > 0:
            _per = 0
        elif self.dea > 0 > self.dif:
            _per = 1
        elif self.dea < 0:
            _per = 2
            # if self.dea > self.dif:
            #     _invest_per = self.bear_percentage[3]

        _invest_per = self.bear_percentage[_per]

        return _invest_per

    # 做多时，可买的头寸，数量
    def get_buy_volume(self):
        buy_volume = 0
        buy_position = 0
        _value = self.broker.get_value()
        _cash = self.broker.get_cash()
        _volume = self.position.size
        _price = self.position.price
        _close = self.data.close[0]
        _percentage = self.buy_position_percentage

        # 现金仍有头寸
        if _cash > 0:
            # 可买金额
            available_cash = _value * _percentage - _volume * _close

            if available_cash > 0:
                if available_cash > _cash:
                    available_cash = _cash

                buy_volume = math.floor(available_cash/_close)

        return buy_volume

    # 做空时，要卖的头寸，数量
    def get_sell_volume(self):
        sell_volume = 0
        _value = self.broker.get_value()
        _cash = self.broker.get_cash()
        _volume = self.position.size
        _price = self.position.price
        _close = self.data.close[0]
        _percentage = self.sell_position_percentage

        if _volume > 0:
            should_sell_cash = _volume * _close - _value * _percentage
            if should_sell_cash > 0:
                sell_volume = math.floor(should_sell_cash/_close)

            if sell_volume > _volume:
                sell_volume = _volume

        return sell_volume


class maxRiskSizer(bt.Sizer):
    params = (('risk', 20),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be entered as a float. e.g. 0.5')

    def _getsizing(self, comminfo, cash, data, isbuy):

        position = self.broker.getposition(data)

        if not position:
            size = math.floor((cash * self.p.risk) / data.close[0])
        else:
            size = position.size

        return size


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

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.FixedSize, stake=10)

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
