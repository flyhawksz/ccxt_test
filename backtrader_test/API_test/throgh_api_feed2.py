#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqi
@contact: fly-hawk@126.com
@file: throgh_api_feed.py
@time: 2019/11/13 8:54 PM
@desc:
'''


from __future__ import (absolute_import, division, print_function,
                    unicode_literals)
from datetime import datetime, timedelta, timezone
import backtrader as bt
# from bittrex.bittrex import Bittrex # ,API_V2_0
import pandas as pd
# from bfxapi import Client
import time
import requests
import json
import pytz
from macd_strategy import CdmaCross


class TestStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(period=14)
        self.sma = bt.indicators.SMA(period=15)


def fetch(host, endpoint, params=""):
    """
    Send a GET request to the bitfinex api

    @return reponse
    """

    url = '{}/{}{}'.format(host, endpoint, params)
    resp = requests.get(url)
    print(resp)
    text = resp.text
    print(text)
    # if resp is not 200:
    #     raise Exception('GET {} failed with status {} - {}'
    #                     .format(url, resp, text))
    parsed = json.loads(text)
    print(parsed)
    return parsed


if __name__ == '__main__':
# """
# MTS	int	millisecond time stamp
# OPEN	float	First execution during the time frame
# CLOSE	float	Last execution during the time frame
# HIGH	float	Highest execution during the time frame
# LOW	float	Lowest execution during the timeframe
# VOLUME	float	Quantity of symbol traded within the timeframe
# """
    cerebro = bt.Cerebro()
    # data = bt.feeds.YahooFinanceData(
    #     dataname='AAPL',
    #     fromdate = datetime(2019,1,1),
    #     todate = datetime(2020,1,1),
    #     buffered= True
    # )
    tz = pytz.timezone('Asia/Shanghai')
    z_utc_8 = timezone(timedelta(hours=8))
    trade = 'BTC'
    currency = 'BTC'
    market = '{0}-{1}'.format(trade, currency)
    tick_interval = 'minute'
    # my_bittrex = Bittrex(None, None)  # or defaulting to v1.1 as Bittrex(None, None)

    # Client(self, API_KEY=None, API_SECRET=None, rest_host='https://api-pub.bitfinex.com/v2',
    #        ws_host='wss://api-pub.bitfinex.com/ws/2', create_event_emitter=None, logLevel='INFO', dead_man_switch=False,
    #        ws_capacity=25, *args, **kwargs)
    host = 'https://api-pub.bitfinex.com/v2'
    symbol = 'tBTCUSD'
    # start = int(round((time.time() // 60 * 60) * 1000))
    # end = start - (1000 * 60 * 60 * 1)  # * 24 * 1)  # 10 days ago
    now_timestamp = datetime.now().timestamp() * 1000
    to_date = int(now_timestamp)
    from_date = to_date - (1000 * 60 * 60 * 24 * 60)

    print(from_date, to_date)
    end = ''
    start = ''  # int(round((time.time() // 60 * 60) * 1000))  #  - (1000 * 60 * 60 * 24 * 10)
    section = 'hist',
    tf = '1D'
    limit = "100",
    sort = -1
    endpoint = 'candles/trade:{}:{}/hist?limit=5000&_bfx=1'.format(tf, symbol)
    params = "?start={}&end={}&limit={}&sort={}".format(start, end, limit, sort)
    # time_difference = (1000 * 60) * 5000
    # get now to the nearest min
    # now = int(round(time.time() * 1000))
    # url = '{}/{}{}'.format(host, endpoint, params)
    candles = fetch(host, endpoint, params)
    print("Candles:")
    print(candles)

    # [print(c) for c in candles]

    # t = my_bittrex.get_ticker(market)

    df = pd.DataFrame(candles)

    # df['T'] = pd.to_datetime(df['T'])
    # df.set_index(df['T'], inplace=True)

    df.columns = ['datetime', 'open', 'close', 'high', 'low', 'volume']
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms', utc=True)
    df = df.set_index('datetime')
    print(df)
    df = df.tz_convert('Asia/Shanghai')
    print(df)
    df = df.sort_values('datetime', ascending=True)
    # df = df.set_index('datetime')
    print(df)
    df['openinterest'] = 0

    data = bt.feeds.PandasData(dataname=df,
                               openinterest='openinterest',
                               timeframe=bt.TimeFrame.Days,
                               compression=1)
    cerebro.adddata(data)
    cerebro.addstrategy(CdmaCross)
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    # Set the commission
    cerebro.broker.setcommission(commission=0.001)
    cerebro.run()
    cerebro.plot(style='candle')