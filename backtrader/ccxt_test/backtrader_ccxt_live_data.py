# -*- coding: utf-8 -*-
# @Time    : 2019-11-14 23:18
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : resample_test.py
# @Software: PyCharm

import sys
import backtrader as bt
import pytz
import datetime
import time


class TestStrategy(bt.Strategy):
    def utc_to_local(self, utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
        local_tz = pytz.timezone('Asia/Shanghai')
        local_format = "%Y-%m-%d %H:%M:%S"
        utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
        utc_dt = datetime.strptime(utc_time_str, utc_format)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        time_str = local_dt.strftime(local_format)
        return datetime.fromtimestamp(int(time.mktime(time.strptime(time_str, local_format))))

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status))

    def next(self):
        msg = '***** NEXT: {} '.format(bt.num2date(self.data.datetime[0], pytz.timezone('Asia/Shanghai')))
        for d in self.datas:
            msg += '{} {} {} '.format(d._name, len(d), d.close[0])
        print(msg)


def run(argv):
    cerebro = bt.Cerebro()
    # data = bt.feeds.CCXT(exchange='bitstamp', symbol='BTC/USD', timeframe=bt.TimeFrame.Ticks, compression=1,
    #                      ohlcv_limit=10)
    data = bt.feeds.CCXT(exchange='bitstamp', symbol='BTC/USD', timeframe=bt.TimeFrame.Minutes, compression=1)
    cerebro.adddata(data, name='1t')
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=2, name='2M')
    cerebro.addstrategy(TestStrategy)
    cerebro.run()


if __name__ == '__main__':
    run(sys.argv)

    # good_exchanges = ['poloniex', 'bittrex', 'bitstamp']