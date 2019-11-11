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
        self.bear_percentage = [0.00, 0.10, 0.20, 0.30]

        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        self.sar = bt.ind.PSAR(self.data, period=self.p.psar_period, af=self.p.af, afmax=self.p.afmax)

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        self.order = None

        # self.K = bt.indicators.StochasticFast(self.data)
        # self.kdj = bt.indicators.StochasticFull(self.data)

        self.EMA12 = bt.indicators.EMA(self.data, period=self.p.macd1)
        self.EMA26 = bt.indicators.EMA(self.data, period=self.p.macd2)

        self.dif = self.EMA12 - self.EMA26
        self.dea = bt.indicators.EMA(self.dif, period=self.p.macdsig)
        self.my_macd = self.dif - self.dea

        self.macd_cross = bt.indicators.CrossOver(self.dif, self.dea)

        # self.dif_cross_zero = bt.indicators.CrossOver(self.dif, 0)
        self.dif_cross_up = bt.indicators.CrossUp(self.dif, 0)
        self.dif_cross_down = bt.indicators.CrossDown(self.dif, 0)
        # self.dea_cross_zero = bt.indicators.CrossOver(self.dea, 0)
        self.dea_cross_up = bt.indicators.CrossUp(self.dea, 0)
        self.dea_cross_down = bt.indicators.CrossDown(self.dea, 0)

        self.buy_level = 0
        self.buy_small_adjust_step = 0.01
        self.buy_small_adjust = 0
        self.buy_position = 0
        self.buy_position_percentage = 0

        self.sell_level = 0
        self.sell_small_adjust_step = 0.01
        self.sell_small_adjust = 0
        self.sell_position = 0
        self.sell_position_percentage = 0

        self.val_start = 0
        self.roi = 0

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def next(self):
        buy_flag = None
        operate_volume = 0

        if self.order:
            return  # pending order execution

        if self.data.close == 0:
            return  # 数据错误

        # self.log('dif cross zero:{},{} dea cross zero: {},{}'.format(
        #     self.dif_cross_up, self.dif_cross_down, self.dea_cross_up, self.dea_cross_down))

        if self.macd_cross[0] > 0:
            buy_flag = 0
            self.buy_small_adjust = 0
            self.log('出现金叉')
        elif self.dif_cross_up[0] > 0:
            buy_flag = 0
            self.buy_small_adjust = 0
            self.log('DIF上穿零轴')
        elif self.dea_cross_up[0] > 0:
            buy_flag = 0
            self.buy_small_adjust = 0
            self.log('DEA上穿零轴')
        # macd 为正，多头。如正得越来越多，以buy_percentage 为基础，不断增加头寸。但不超过本档上限
        #                 如果正得越来越少，已不buy_percentage 为基础，逐渐头寸。但不超过本档下限
        elif self.my_macd[0] > 0:
            # 用SAR指标来辨别MACD反复交叉
            if self.my_macd[0] >= self.my_macd[-1]:  # 持续增,
                if self.sar < self.data.low:  # 保持多头，且未变向，可以增持
                    self.buy_small_adjust = self.buy_small_adjust + self.buy_small_adjust_step
                    buy_flag = 0
                    self.log('macd为正递增')
                elif self.sar > self.data.high:  # 翻转，MACD增加无效，不处理
                    pass
            elif self.my_macd[0] < self.my_macd[-1]:  # 红柱递减
                if self.sar > self.data.low:  # 反转
                    self.buy_small_adjust = self.buy_small_adjust - self.buy_small_adjust_step
                    buy_flag = 3  # 牛市减持
                    self.log('madc为正递减，减持')
                elif self.sar < self.data.low:
                    # 仍是多头，未反转，不处理
                    pass

        # if self.macd_cross[0] < 0:
        #     if self.EMA12 >= self.EMA26:
        #         #  当仍多头时，死叉无效
        #         self.log('出现无效死叉')
        #         pass
        #     else:
        #         # 当跨档时，微调清零
        #         self.sell_small_adjust = 0
        #         buy_flag = 1
        #         self.log('出现死叉')
        # elif self.dif_cross_down[0] > 0:
        #     if self.EMA12 >= self.EMA26:
        #         self.log('DIF无效下穿零轴')
        #         pass
        #     else:
        #         self.sell_small_adjust = 0
        #         buy_flag = 1
        #         self.log('DIF下穿零轴')
        # elif self.dea_cross_down[0] > 0:
        #     if self.EMA12 >= self.EMA26:
        #         self.log('DEA无效下穿零轴')
        #         pass
        #     else:
        #         self.sell_small_adjust = 0
        #         buy_flag = 1
        #         self.log('DEA下穿零轴')

        if self.macd_cross[0] < 0:
            # 当跨档时，微调清零
            self.sell_small_adjust = 0
            buy_flag = 1
            self.log('出现死叉')
        elif self.dif_cross_down[0] > 0:
            self.sell_small_adjust = 0
            buy_flag = 1
            self.log('DIF下穿零轴')
        elif self.dea_cross_down[0] > 0:
            self.sell_small_adjust = 0
            buy_flag = 1
            self.log('DEA下穿零轴')
        # macd 为负，空头。如负得越来越多，已sell_percentage 为基础，不断减少头寸。
        elif self.my_macd[0] < 0:
            if self.my_macd[0] > self.my_macd[-1]:
                if self.sar < self.data.low:
                    buy_flag = 2  # 熊市增持
                    self.sell_small_adjust = self.sell_small_adjust + self.sell_small_adjust_step
                    self.log('madc为负缩小，可增持少量')
                else:
                    #  仍是空头，未反转，不处理
                    pass
            elif self.my_macd[0] < self.my_macd[-1]:
                if self.sar > self.data.high:
                    buy_flag = 1
                    self.sell_small_adjust = self.sell_small_adjust - self.sell_small_adjust_step
                    self.log('madc为负扩大，持续卖')
                else:
                    pass

        # update postion percentage
        self.update_position()

        operate_volume = self.get_operate_volume(buy_flag)

        if buy_flag == 0 or buy_flag == 2:
            self.buy(exectype=bt.Order.Market, size=operate_volume)  # default if not given
            self.log('Buy {:.2f}%  Sell {:.2f}%  已持仓位：{:.2f}'.format(
                self.buy_position_percentage * 100, self.sell_position_percentage * 100,
                self.position.size * self.data.close[0]
            ))
            self.log('BUY CREATE, exectype Market, price {}， size {}'.format(
                self.data.close[0], operate_volume))
        elif buy_flag == 1 or buy_flag == 3:
            self.sell(exectype=bt.Order.Market, size=operate_volume)  # default if not given
            self.log('Buy {:.2f}%  Sell {:.2f}%  已持仓位：{:.2f}'.format(
                self.buy_position_percentage * 100, self.sell_position_percentage * 100,
                 self.position.size * self.data.close[0]
            ))
            self.log('SELL CREATE, exectype Market, price{}, size {}'.format(
                self.data.close[0], operate_volume))

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

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))

    def update_position(self):
        _value = self.broker.get_value()
        if self.buy_level <= 2:
            if self.get_upper_percent() + self.buy_small_adjust > self.bull_percentage[self.buy_level + 1]:
                self.buy_position_percentage = self.bull_percentage[self.buy_level + 1]
            elif self.get_upper_percent() + self.buy_small_adjust < 0:
                self.buy_position_percentage = 0
            else:
                self.buy_position_percentage = self.get_upper_percent() + self.buy_small_adjust
        else:  # 不可能
            self.buy_position_percentage = self.bull_percentage[2]
        self.buy_position = _value * self.buy_position_percentage

        if self.sell_level >= 0:
            if self.get_lower_percent() + self.sell_small_adjust < 0:
                self.sell_position_percentage = 0
            elif self.get_lower_percent() + self.sell_small_adjust > self.bear_percentage[self.sell_level + 1]:
                self.sell_position_percentage = self.bear_percentage[self.sell_level+1]
            else:
                self.sell_position_percentage = self.get_lower_percent() + self.sell_small_adjust
        else:
            self.sell_position_percentage = self.bear_percentage[0]
        self.sell_position = _value * self.sell_position_percentage

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
        self.buy_level = _per
        _invest_per = self.bull_percentage[_per]

        return _invest_per

    # 计算应持仓位（头寸）
    def get_lower_percent(self):
        # 投资占头寸的下限
        _invest_per = 0
        _per = 0
        # 牛
        if self.dea > self.dif > 0:
            _per = 2
        elif self.dea > 0 > self.dif:
            _per = 1
        elif self.dea < 0:
            _per = 0
            # if self.dea > self.dif:
            #     _invest_per = self.bear_percentage[3]
        self.sell_level = _per
        _invest_per = self.bear_percentage[_per]

        return _invest_per

    # 具体生成买卖数量
    # operateion:0,1,2,3, 买，卖，熊市增持，牛市减持
    def get_operate_volume(self, operation):
        operate_volume = 0
        _value = self.broker.get_value()
        _cash = self.broker.get_cash()
        _volume = self.position.size
        _price = self.position.price
        _close = self.data.close
        _percentage = 0
        # buy
        if operation == 0:
            _percentage = self.buy_position_percentage
            # self.log('Buy percentage is {}%'.format(_percentage * 100))
        # sell
        elif operation == 1:
            _percentage = self.sell_position_percentage
            # self.log('Sell percentage is {}%'.format(_percentage*100))
        # bear buy
        elif operation == 2:
            _percentage = self.sell_position_percentage
            # self.log('Buy percentage is {}%'.format(_percentage * 100))
        # bull sell
        elif operation == 3:
            _percentage = self.buy_position_percentage
            # self.log('Buy percentage is {}%'.format(_percentage*100))

        if operation == 0 or operation == 2:
            # 现金仍有头寸
            if _cash > 0:
                # 可买金额
                available_cash = _value * _percentage - _volume * _close
                if available_cash > 0:
                    if available_cash > _cash:
                        available_cash = _cash
                    operate_volume = math.floor(available_cash / _close)
        elif operation == 1 or operation == 3:
            if _volume > 0:
                should_sell_cash = _volume * _close - _value * _percentage
                if should_sell_cash > 0:
                    operate_volume = math.floor(should_sell_cash / _close)
                if operate_volume > _volume:
                    operate_volume = _volume

        return operate_volume


if __name__ == '__main__':
    # 获取数据来源方式：0 yahoo online; 1 local data file
    data_method = 0
    # 数据文件来源，用自带的数据（0），还是用中国股市数据（1）
    data_source = 1
    data_path = os.path.join(os.getcwd(), 'datas')
    data_file_name = '600177.csv'
    data_file_path = ''
    yahoo_stock_code = 'AZO'

    # Create a cerebro entity
    cerebro = bt.Cerebro()


    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    if data_source == 1:
        data_path = os.path.join(data_path, 'stock_history')
        # if not os.path.exists(modpath):
        #     os.makedirs(modpath)

        data_file_path = os.path.join(data_path, data_file_name)

        df = pd.read_csv(data_file_path, header=0, encoding='gbk', parse_dates=True)
        # print(df.columns)
        # columns = df.columns.values.tolist()  # 获取列名列表，注意values，tolist的使用
        # new_df = df.sort_values('日期', ascending=True)
        # print(new_df)
        col_n = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量']
        data_df = pd.DataFrame(df, columns=col_n)
        data_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        data_df = data_df.sort_values('date', ascending=True)
        data_df['date'] = pd.to_datetime(data_df['date'])
        data_df = data_df.set_index('date')
    else:
        data_file_path = os.path.join(data_path, data_file_name)
        data_df = pd.read_csv(data_file_path, index_col=0, parse_dates=True)

    if data_method == 1:
        print(data_df)
        data_df['openinterest'] = 0
        data = bt.feeds.PandasData(dataname=data_df,
                                   fromdate=datetime.datetime(2017, 10, 1),
                                   todate=datetime.datetime(2019, 10, 31)
                                   )
    elif data_method == 0:
        data = bt.feeds.YahooFinanceData(
            dataname=yahoo_stock_code,
            fromdate=datetime.datetime(2018, 1, 10),
            todate=datetime.datetime(2019, 10, 31),
            buffered=True
        )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Add a strategy
    # cerebro.addstrategy(SmaCross)
    cerebro.addstrategy(CdmaCross)

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
