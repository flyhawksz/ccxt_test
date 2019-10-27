from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd

# Import the backtrader platform
import backtrader as bt


class MySignal(bt.Indicator):
    lines = ('signal',)
    params = (('period', 30),)

    def __init__(self):
        self.lines.signal = self.data - bt.indicators.SMA(period=self.p.period)

# ————————————————
# 版权声明：本文为CSDN博主「钱塘小甲子」的原创文章，遵循
# CC
# 4.0
# BY - SA
# 版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https: // blog.csdn.net / qtlyx / article / details / 70945174

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    cerebro.add_signal(bt.SIGNAL_LONGSHORT, MySignal, subplot=False)
    # 这句话很有用，画图看效果
    # cerebro.signal_accumulate(True)


    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(modpath):
        os.makedirs(modpath)
    datapath = os.path.join(modpath, 'dfqc.csv')

    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    dataframe['openinterest'] = 0
    data = bt.feeds.PandasData(dataname=dataframe,
                               fromdate=datetime.datetime(2015, 1, 1),
                               todate=datetime.datetime(2016, 12, 31)
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

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
