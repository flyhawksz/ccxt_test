# -*- coding: utf-8 -*-
# @Time    : 2019-10-27 15:41
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : backtrader_ccxt_test1.py
# @Software: PyCharm
# !/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2017 Ed Bartosh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

import backtrader as bt


class TestStrategy(bt.Strategy):
    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status))

    def next(self):
        print('*' * 5, 'NEXT:', bt.num2date(self.data0.datetime[0]), self.data0._name, self.data0.open[0],
              bt.TimeFrame.getname(self.data0._timeframe), len(self.data0))


def runstrategy(argv):
    # Create a cerebro
    cerebro = bt.Cerebro()

    data = bt.feeds.CCXT(exchange='okex', symbol='BTC/USDT', timeframe=bt.TimeFrame.Ticks, compression=1)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes)
    # cerebro.adddata(data)

    # Add the strategy
    cerebro.addstrategy(TestStrategy)

    # Run the strategy
    cerebro.run()


if __name__ == '__main__':
    sys.exit(runstrategy(sys.argv))