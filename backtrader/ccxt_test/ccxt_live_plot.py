# -*- coding: utf-8 -*-
# @Time    : 2019-11-14 15:08
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_live_plot.py
# @Software: PyCharm

#!/usr/local/bin/python3

import asyncio

import os
import sys

import datetime
import time

import ccxt.async_support as ccxt  # noqa: E402

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


style.use('fivethirtyeight')

import matplotlib.dates as mdate
from matplotlib.ticker import FormatStrFormatter

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root)

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
#fig, ax1 = plt.subplots()

fig.subplots_adjust(left = 0.1, bottom = 0.1)
#fig.tight_layout()

def animate(i):
    btcusd = (asyncio.get_event_loop().run_until_complete(ccxt.bittrex().fetch_ticker('BTC/USDT')))
    print(btcusd)
    print(btcusd['bid'])
    print(btcusd['ask'])

#    try:
#        startdate
#    except NameError:
#        startdate = mdate.epoch2num(btcusd['timestamp'] / 1000)

    xaxis = mdate.epoch2num(btcusd['timestamp'] / 1000)
    yaxis = btcusd['bid']
#    x = datetime.datetime.fromtimestamp(btcusd['timestamp'].astype(str))
    ######ax1.clear()
    #ax1.set_xticklabels(xs)
    #ax1.axis([0, 20, 0, 20])
    ##ax1.plot_date(x, btcusd['bid'])
    #####ax1.plot_date(x = xaxis, y = yaxis, lw=1, linestyle = 'solid') #fmt = '.r-') #, linestyle='solid', marker='None') #, fmt='-', linewidth=2)
    ax1.plot_date(xaxis, yaxis, ls='-', marker='.')

    ##ax1.yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
    plt.axes().tick_params(labelsize=6)
    plt.axes().yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ### ETH/BTC plt.axes().yaxis.set_major_formatter(FormatStrFormatter('%.8f'))
    plt.axes().xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.axes().xaxis_date()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='center')

    #ax1.plot(btcusd['bid'])
    plt.xlim(mdate.epoch2num((btcusd['timestamp'] / 1000) - 300), mdate.epoch2num((btcusd['timestamp'] / 1000) + 300))
    ##plt.xlim(startdate, datetime.date.today())
    # ETC/BTC plt.ylim(btcusd['bid'] - 0.0000001, btcusd['bid'] + 0.0000001)
    plt.ylim(btcusd['bid'] - 50, btcusd['bid'] + 50)
    ##ax1.plot()
#    plt.xscale('linear')
#    plt.yscale('linear')
    #plt.grid(True)

    #plt.set_data(x[:num], y[:num])
    #plt.axes.axis([-20, 20, -20, 20])

##    ax1.axhline(y = btcusd['bid'], color = 'r', linestyle = '-', linewidth = 0.1)

# plt.grid(False)
#ax1.autoscale_view(True,True,True)
fig.autofmt_xdate()
ani = animation.FuncAnimation(fig, animate, interval=30000)
plt.show()