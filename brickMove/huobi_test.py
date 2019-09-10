#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqi
@contact: fly-hawk@126.com
@file: huobi_test.py
@time: 2019/9/10 10:40 PM
@desc:
'''

# import websocket
from websocket import create_connection
from pyquery import PyQuery
from colorama import init, Fore

import requests
import socket
import gzip
import json

alert = {
    'hsr': {'hb': {'enable': True, 'profit': 2}, 'zb': {'enable': True, 'profit': 2}},
    'eth': {'hb': {'enable': True, 'profit': 2}, 'zb': {'enable': True, 'profit': 2}},
    }

otc = {'usdt': {'sell': 0.0, 'buy': 0.0}, 'qc': {'sell': 0.0, 'buy': 0.0}}
markets = dict()

def run_client():
    ws = websocket.create_connection("wss://www.hbg.com/-/s/pro/ws")
    ws.send(json.dumps({'sub': 'market.overview'}))
    while True:
        data = ws.recv()
        result = gzip.decompress(data)
        obj = json.loads(result)
        if 'ping' in obj:
            ws.send(json.dumps({'pong': obj['ping']}))
            refresh()
            output()
        elif 'ch' in obj:
            for data in obj['data']:
                if data['symbol'].endswith('usdt'):
                    key = data['symbol'].replace('usdt', '')
                    if not key in markets:
                        markets[key] = dict()
                    markets[key]['hb'] = {'last': data['close']}

def run_forever():
    while True:
        try:
            run_client()
        except Exception as e:
            print(type(e), e.args)
        except KeyboardInterrupt:
            break

def refresh():
    try:
        url = "http://api.zb.cn/data/v1/allTicker"
        r = requests.get(url)
        obj = r.json()
        for key in obj:
            if key.endswith('qc'):
                currency = key.replace('qc', '')
                if currency == 'bcc':
                    currency = 'bch'
                if currency in markets:
                    markets[currency]['zb'] = {'last': float(obj[key]['last']), 'sell': float(obj[key]['sell']), 'buy': float(obj[key]['buy'])}
    except Exception as e:
        print(type(e), e.args)

def output():
    get_hb_price(1)
    get_hb_price(2)
    get_zb_price(1)
    get_zb_price(2)

    beep = ''
    print('┌───────┬─────────────────────────────────────┬───────┬─────────────────────────────────────┐')
    print('│  USDT │  SELL: {0:.2f}    BUY: {1:.2f}            │   QC  │  SELL: {2:.3f}    BUY: {3:.3f}          │'.format(\
        otc['usdt']['sell'], otc['usdt']['buy'], otc['qc']['sell'], otc['qc']['buy']))
    print('├───────┼─────────────────────────────────────┴───────┴───────────────┬─────────────────────┤')
    for key in markets:
        if 'zb' in markets[key]:
            hb = markets[key]['hb']['last']
            zb = markets[key]['zb']['last']
            profit_hb = 100 / hb / otc['usdt']['sell'] * zb * otc['qc']['buy'] - 100
            profit_zb = 100 / otc['qc']['sell'] / zb * hb * otc['usdt']['buy'] - 100
            if key in alert:
                if (alert[key]['hb']['enable'] and profit_hb > alert[key]['hb']['profit']) or (alert[key]['zb']['enable'] and profit_zb > alert[key]['zb']['profit']):
                    beep = '\a'
                color = Fore.YELLOW
            else:
                color = Fore.RESET
            if profit_hb > 1:
                dir = '>>'
            elif profit_zb > 1:
                dir = '<<'
            else:
                dir = '  '
            str = "│{0}  {1:^4} \033[0m│{0}  {2:>6.2f}  {3:>8}  {4:>8}  {5:}  {6:>6.2f}  {7:>8}  {8:>8} \033[0m│{0}  {9:>8}  {10:>8} \033[0m│".format(\
                color, key.upper(), profit_hb, format_price(hb * otc['usdt']['sell']), format_price(zb * otc['qc']['buy']), dir, \
                profit_zb, format_price(hb * otc['usdt']['buy']), format_price(zb * otc['qc']['sell']), format_price(hb), format_price(zb))
            print(str)
    print('└───────┴─────────────────────────────────────────────────────────────┴─────────────────────┘' + beep)

def get_hb_price(trade=1):
    if trade == 1:
        tradeType = 'buy'
    else:
        tradeType = 'sell'
    try:
        url = "https://otc-api.hbg.com/v1/data/trade-market?country=37&currency=1&payMethod=0&currPage=1&coinId=2&tradeType={0}&blockType=general&online=1".format(tradeType)
        r = requests.get(url)
        obj = r.json()
        for data in obj['data']:
            if data['minTradeLimit'] <= 20000 and data['maxTradeLimit'] >= 5000:
                otc['usdt'][tradeType] = data['price']
                break
    except Exception as e:
        print(type(e), e.args)

def get_zb_price(trade=1):
    if trade == 1:
        tradeType = 'buy'
    else:
        tradeType = 'sell'
    try:
        url = "https://vip.zb.cn/otc/trade/qc_cny?type={0}".format(trade)
        s = requests.session()
        s.headers['Accept-Language'] = 'zh-Hans-CN, zh-Hans; q=0.5'
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
        r = s.get(url)
        if len(r.text):
            d = PyQuery(r.text)
            tr = d('table.c2c-table')('tr:gt(0) td.price')
            for td in tr:
                price = float(td.text[:-5])
                l = td.find('span').text.split('-')
                if float(l[0]) <= 20000 and float(l[1]) >= 5000:
                    otc['qc'][tradeType] = price
                    break
    except Exception as e:
        print(type(e), e.args)

def format_price(price):
    price = str(price)[:8]
    return float(price)

def main():
    init()
    socket.setdefaulttimeout(10)
    run_forever()

if __name__ == '__main__':
    main()