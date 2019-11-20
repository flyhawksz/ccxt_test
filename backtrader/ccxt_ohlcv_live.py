# -*- coding: utf-8 -*-
# @Time    : 2019-11-14 13:32
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_ohlcv_live.py
# @Software: PyCharm

""" Chart of ohlcv and more for multi cryptos
    - get exchange api data using ccxt (past and live)
    - chart closing price percentage, volume + ohlcv
    - store data in  dfpairs = { pair = dataframe( o h l c v * microstimestamp ), ... }
    Todo:
    - free memory
    - volume
    - split charts
"""
import sys
import datetime
from time import sleep

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
# from matplotlib.finance import candlestick2_ohlc
from mpl_finance import candlestick2_ohlc

import ccxt
# import theo.utils as ut


class ccxt_ohlcv_live():
    def __init__(self, ex, pairs):
        self.ex = ex
        self.pairs = pairs
        self.timeframe = '1m'
        self.tickerperiod = 5
        self.itemdisplay = 50
        self.dateformat = '%d %H:%M'  # '%Y-%m-%d %H:%M:%S'
        self.dfpairs = {}  # dict{ pair * df }

    def run(self, i):
        """ i : animation ticker """
        init = True if i == 0 else False
        self.fetch_ticker(init)
        self.call_fetch_ohlcv(init)
        self.graph()
        return

    def getdataframe(self, rowname):
        """ extract data from dfpairs dataframe into rowname dataframe """
        # mix columns from pairs dfs
        dfrow = None
        for pair in self.pairs:
            current = self.dfpairs[pair][rowname]
            dfpair = pd.DataFrame(current.values, index=current.index, columns=[rowname])
            # print('-------------dfpair-------------')
            # print(dfpair)
            if dfrow is None:
                dfrow = dfpair
                # print('*************dfrow1******************')
                # print(dfrow)
            else:
                dfrow = pd.merge(dfrow, dfpair, right_index=True, left_index=True)
                dfrow = pd.merge(dfrow, dfpair, on='mts')
                # print('*************dfrow2******************')
                # print(dfrow)
        # rename index
        dfrow.columns = self.pairs
        print('*************dfrow3******************')
        print(dfrow)
        return dfrow

    def dfindexdate(self, df):
        df.index = map(lambda x: datetime.datetime.fromtimestamp(int(x / 1000)).strftime(self.dateformat), df.index)

    def graph(self):

        for oneaxe in fig.axes:
            oneaxe.clear()
            oneaxe.legend(prop={'size': 6})

        # close
        df = self.getdataframe('close')
        print(df)
        print('-' * 25)
        print(df.values[0])
        df = 100 * ((df / df.values[0]) - 1)
        self.dfindexdate(df)
        df.plot(ax=ax0)

        # dt = self.tick
        # dt = 100 * ((dt / dt.values[0]) - 1)
        # dt.plot(ax=ax1)
        #
        # # volume
        # dfv = self.getdataframe('volume').pct_change()
        # self.dfindexdate(dfv)
        # dfv.plot(ax=ax2, width=.9, kind='bar', alpha=.8)

        # ohlc btc
        for i, pair in enumerate(self.pairs):
            quotes = self.dfpairs[pair]
            candlestick2_ohlc(axs[i], quotes['open'], quotes['high'], quotes['low'], quotes['close'], width=0.6)
            axs[i].set_title(pair, fontsize=8)

    def call_fetch_ohlcv(self, init):
        """ call_fetch_ohlcv : fetch_ohlcv (ccxt) on first run, then fetch_ohlcv_last (custom) """
        responses = {}
        for pair in self.pairs:
            sleep(2)
            pairup = self.symbolup(pair)
            if init:
                responses[pair] = self.ex.fetch_ohlcv(symbol=pairup, timeframe=self.timeframe, since=None)
            else:
                responses[pair] = self.fetch_ohlcv_last(symbol=pairup, timeframe=self.timeframe)
        self.ohlcv2dataframe(init, responses)

    def fetch_ticker(self, init):
        """ fetch ticker into dataframe"""
        pairsup = map(lambda x: self.symbolup(x), self.pairs)
        tickers = self.ex.fetch_tickers(pairsup)
        datesum, r = 0, {}
        for symbol, ticker in tickers.items():
            pairlow = self.symbollow(symbol)
            r[pairlow] = ticker['last']
            datesum = datesum + ticker['timestamp']
        datemean = int(datesum / len(self.pairs))
        oneserie = [datemean]
        for pair in self.pairs:
            oneserie.append(r[pair])

        # store in dataframe
        if init:
            mcolumns = self.pairs[:]  # copy var !
            mcolumns.insert(0, 'mtimestamp')
            self.tick = pd.DataFrame([oneserie], columns=mcolumns).set_index('mtimestamp')
        else:
            mts = oneserie.pop(0)
            self.tick.loc[mts] = oneserie

    def ohlcv2dataframe(self, init, responses):
        columns = ['mts', 'open', 'high', 'low', 'close', 'volume']
        for pair in self.pairs:
            if init:
                # reverse and slice
                self.dfpairs[pair] = pd.DataFrame(responses[pair], columns=columns).set_index('mts')[::-1]
                self.dfpairs[pair] = self.dfpairs[pair].iloc[-self.itemdisplay:]
            else:
                mts = responses[pair][0].pop(0)
                self.dfpairs[pair].loc[mts] = responses[pair][0]

    def fetch_ohlcv_last(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        """ method from bitfinex modified to get live ohlc (Last)"""
        ex = self.ex
        market = ex.market(symbol)
        request = {
            'symbol': market['id'],
            'timeframe': ex.timeframes[timeframe],
        }
        if limit:
            request['limit'] = limit
        if since:
            request['start'] = since
        request = ex.extend(request, params)
        response = ex.publicGetCandlesTradeTimeframeSymbolLast(request)
        """ same as hist but add list """
        return ex.parse_ohlcvs([response], market, timeframe, since, limit)

    def symbollow(self,symbol):
        if symbol[:4] == 'DASH':
            return (symbol[:4] + symbol[5:]).lower()
        return (symbol[:3] + symbol[4:]).lower()

    def symbolup(self,symbol):
        if symbol[:4] == 'dash':
            return (symbol[:4] + '/' + symbol[4:]).upper()
        return (symbol[:3] + '/' + symbol[3:]).upper()


if __name__ == '__main__':
    exchange = 'bitfinex'
    ex = getattr(ccxt, exchange)()
    # ex = ccxt.bitfinex()
    pairs = ['btcusd'] # , 'bchusd', 'ethusd'] # , 'ltcusd', 'xrpusd']  # ,'eosusd','iotusd'
    cc = ccxt_ohlcv_live(ex, pairs)

    """
    Display 2 columns, right for percentage close + volume left is for pairs OHLCV
    """
    c, r = (2, len(pairs))
    fig = plt.figure(0)
    #                      ((canvasY,canvasX),(posY,posY), span)
    ax0 = plt.subplot2grid((r, c), (0, 0), rowspan=2)
    # ax1 = plt.subplot2grid((r, c), (2, 0), rowspan=2)
    # ax2 = plt.subplot2grid((r, c), (4, 0), rowspan=1)
    axs = []
    for i, pair in enumerate(pairs):
        axs.append(plt.subplot2grid((r, c), (i, 1)))
    ani = animation.FuncAnimation(fig, cc.run, interval=10000)
    # ani.save("test.mp4")
    plt.show()