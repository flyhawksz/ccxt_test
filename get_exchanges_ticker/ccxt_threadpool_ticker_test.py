# -*- coding: utf-8 -*-
# @Time    : 2019-10-5 21:12
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : ccxt_thread_ticker_test.py
# @Software: PyCharm

import ccxt
import os
import time
import csv
# from signal import *
import pandas as pd
import numpy as np
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import threading
import logging  # 引入logging模块
import os.path
# import time


# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = os.path.dirname(os.getcwd()) + '/Logs/'
if not os.path.exists(log_path): os.mkdir(log_path)
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)
# 日志


class Price(object):
    exchange = ''
    currency_pair = ''
    base_currency = ''
    target_currency = ''
    timestamp = 0
    ask = 0  # 卖价，要价
    bid = 0  # 买价
    # askVolume = 0
    # bidVolume = 0

    def get_price_array(self):
        return [self.exchange, self.timestamp, self.currency_pair, self.bid, self.ask]
        # , self.bidVolume, self.askVolume]


class GetMultiExchangeTicker:

    def __init__(self):
        # self.TIMESTAMP = "%Y%m%d%H%M%S"
        self.good_currencies = ['USD', 'BTC', 'ETH', 'LTC', 'USDT']
        # self.good_exchanges = ['gdax', 'bitstamp', 'bitfinex', 'binance', 'okex']
        self.good_exchanges = ['gdax', 'bitstamp', 'bitfinex']  # , 'binance', 'okex']
        self.fieldnames = ['timestamp', 'bid', 'ask']
        self.DataFrame_fieldnames = ['exchange', 'timestamp', 'symbol', 'bid', 'ask']

        self.candidate_exchange_symbol = {}
        self.target_exchange_symbol = {}  # 以市场为key，symbol为内容
        self.target_symbol_exchange = {}  # 以symbol为kwy， exchange为内容，为矩阵中不同市场间，相同symbol可以兑换
        self.test_symbol = self.make_pair(self.good_currencies)
        self.valid_symbol = set()  # 验证的symbol
        self.valid_exchange_currency = {}  # 以市场为key，currency为内容, 为填充矩阵用

        # 数据文件夹，不存在，就创建
        self.data_path = os.path.join(os.getcwd(), 'data\\')
        self.interval = 2  # 查询symbol间隔，防止被市场屏蔽
        self.sleep_time = 10
        self.count = 0   #  收集数据量，用于退出死循环
        self.max_records = 200  # 用于退出死循环
        self.data_queue = Queue(maxsize=len(self.good_exchanges))  # 用于线程间传递数据
        self.stop_flag = False

        self.matrix_dim = int(str(len(self.good_exchanges) - 1) + str(len(self.good_currencies)))  # 矩阵shape
        self.matrix = self.create_blank_directed_matrix(self.matrix_dim)  # 矩阵，先初始化
        self.vertices = self.create_vertices(self.matrix_dim)  # 所有顶点
        print(self.vertices)
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

    # 根据不同市场 但货币相同，填充矩阵数据，交换价格为 1
    def fill_matrix_by_exchange_same_currency(self):
        for exchange_header, currencies_header in self.valid_exchange_currency.items():
            for exchange_tail, currencies_tail in self.valid_exchange_currency.items():
                for currency_header in currencies_header:
                    for currency_tail in currencies_tail:
                        if exchange_header != exchange_tail and currency_header == currency_tail\
                                and currency_header != 'USD':
                            index_exchange_header = self.good_exchanges.index(exchange_header)
                            index_exchange_tail = self.good_exchanges.index(exchange_tail)
                            index_currency = self.good_currencies.index(currency_header)
                            index_header = int(str(index_exchange_header) + str(index_currency))
                            index_tail = int(str(index_exchange_tail) + str(index_currency))
                            self.matrix[index_header][index_tail] = 1
                            self.matrix[index_tail][index_header] = 1

    # 填充 市场-货币，为填充 矩阵 准备， 返回字典
    def fill_valid_exchange_currency(self):
        print('target_exchange symbol:{}'.format(self.target_exchange_symbol))
        for exchange in self.target_exchange_symbol:
            for symbol in self.target_exchange_symbol[exchange]:
                currencyA, currencyB = symbol.split('/')
                if exchange not in self.valid_exchange_currency.keys():
                    self.valid_exchange_currency[exchange] = {currencyA, currencyB}
                else:
                    if currencyA not in self.valid_exchange_currency[exchange]:
                        self.valid_exchange_currency[exchange].add(currencyA)
                    if currencyB not in self.valid_exchange_currency[exchange]:
                        self.valid_exchange_currency[exchange].add(currencyB)
        print(self.valid_exchange_currency)

    # 填充可以用的 货币对-市场， 返回字典
    def fill_target_symbol_exchange(self):
        print('target_exchange symbol:{}'.format(self.target_exchange_symbol))
        for exchange in self.target_exchange_symbol:
            for symbol in self.target_exchange_symbol[exchange]:
                if symbol not in self.target_symbol_exchange.keys():
                    self.target_symbol_exchange[symbol] = {exchange}
                else:
                    if exchange not in self.target_symbol_exchange[symbol]:
                        self.target_symbol_exchange[symbol].add(exchange)

        print(self.target_symbol_exchange)

    # 生成 顶点 列表，用于 矩阵填充，矩阵边的 key
    # 将三维矩阵降维，exchange 下标，currency的下标组成两位数，未用的序号，用 v + 数字  填充
    def create_vertices(self, dim):
        vertices = list(range(0, dim))
        print(vertices)

        for i in range(len(self.good_exchanges)):
            for j in range(10):
                if i >= len(self.good_exchanges)-1 and j >= len(self.good_currencies):
                    break

                if j >= len(self.good_currencies):
                    exchange = 'v' + str(i)
                    currency = str(j)
                else:
                    exchange = self.good_exchanges[i]
                    currency = self.good_currencies[j]

                index = i * 10 + j
                vertices[index] = exchange + '.' + currency

        return vertices

    # 初始化矩阵
    def create_blank_directed_matrix(self, dim):
        matrix = np.zeros((dim, dim))
        inf = float('inf')
        for i in range(dim):
            for j in range(dim):
                if i != j:
                    matrix[i][j] = inf

        return matrix

    # 在初始化矩阵基础上，根据 ticker 填充矩阵。
    # 货币对拆分为两个顶点， 基础货币/目标货币，当卖出基础货币，取得目标货币，只能按 bid(买价），
    # 当要买基础货币，卖出目标货币，就要按 ask（要价）的倒数，从而实现货币对双向交换
    def fill_matrix_by_ticker(self, temp_price: Price):
        # print('***************fill_matrix************')
        exchange_index = self.good_exchanges.index(temp_price.exchange.lower())
        base_currency_index = self.good_currencies.index(temp_price.base_currency.upper())
        target_currency_index = self.good_currencies.index(temp_price.target_currency.upper())
        ask_price = temp_price.ask
        bid_price = temp_price.bid

        base_index = int(str(exchange_index) + str(base_currency_index))
        target_index = int(str(exchange_index) + str(target_currency_index))
        # print('{},{},{},{}'.format(temp_price.exchange.lower(), temp_price.currency_pair, \
        #                                  temp_price.ask, temp_price.bid))
        # print('{},{},{}'.format(base_index, target_index, base_target_price))
        self.matrix[base_index][target_index] = bid_price
        # print('{},{},{}'.format(target_index, base_index, target_base_price))
        self.matrix[target_index][base_index] = 1/ask_price

        # print(self.matrix)

    # 根据想监控的 货币，生成 货币对
    def make_pair(self, currencis):
        currencis_pair = []
        for i in range(len(currencis)):
            for currency in currencis:
                if currencis[i] == currency: continue
                currencis_pair.append(currencis[i] + '/' + currency)

        # display_list(currencis_pair)
        return currencis_pair

    # ticker持久化
    def save_ticker(self, exchange, symbol, _ticker):
        # 处理数据
        temp_price = Price()
        temp_price.exchange = exchange
        temp_price.currency_pair = symbol
        temp_price.base_currency, temp_price.target_currency = symbol.split('/')
        temp_price.timestamp = _ticker['timestamp']
        temp_price.ask = _ticker['ask']
        temp_price.bid = _ticker['bid']
        # temp_price.bidVolume = _ticker['bidVolume']
        # temp_price.askVolume = _ticker['askVolume']

        self.fill_matrix_by_ticker(temp_price)
        # self.save_in_exchange(exchange, symbol, temp_price)
        self.save_in_classify_dir(exchange, symbol, temp_price)
        self.save_in_one_dir(exchange, symbol, temp_price)

        return temp_price

    # 按市场进行分类，存 ticker
    def save_in_exchange(self, exchange, symbol, temp_price):
        print('\n*********save_in_exchange**************\n')
        filename = exchange + '.csv'
        path_file_name = os.path.join(self.data_path, filename)
        if not os.path.exists(path_file_name):
            with open(path_file_name, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.DataFrame_fieldnames)
                csv_writer.writeheader()
                # print('make header')

        with open(path_file_name, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.DataFrame_fieldnames)
            info = {
                'exchange': exchange,
                'timestamp': temp_price.timestamp,
                'symbol': symbol,
                'bid': temp_price.bid,
                'ask': temp_price.ask
            }
            csv_writer.writerow(info)

    # 按 货币对 进行分类，存 ticker
    def save_in_classify_dir(self, exchange, symbol, temp_price):
        # print('start save ticker in classified dir : {} - {}'.format(exchange, symbol))

        # 按 symbol 分类存数据
        symbol_path = os.path.join(self.data_path, symbol.replace('/', ''))
        symbol_path_file_name = os.path.join(symbol_path, exchange + '.csv')

        if not os.path.exists(symbol_path):
            os.makedirs(symbol_path)

        if not os.path.exists(symbol_path_file_name):
            with open(symbol_path_file_name, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                csv_writer.writeheader()
                # print('make header')

        with open(symbol_path_file_name, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            info = {
                'timestamp': temp_price.timestamp,
                'bid': temp_price.bid,
                'ask': temp_price.ask
            }
            csv_writer.writerow(info)

    # 按 市场、货币对 进行分类，存 ticker 在同一个文件夹中
    def save_in_one_dir(self, exchange, symbol, temp_price):
        # print('start save ticker in one dir : {} - {}'.format(exchange, symbol))
        filename = exchange + '_' + symbol + '.csv'
        path_file_name = os.path.join(self.data_path, filename.replace('/', ''))
        if not os.path.exists(path_file_name):
            with open(path_file_name, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                csv_writer.writeheader()
                # print('make header')

        with open(path_file_name, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            info = {
                'timestamp': temp_price.timestamp,
                'bid': temp_price.bid,
                'ask': temp_price.ask
            }
            csv_writer.writerow(info)

    # 取得 某市场 某货币对 的 ticker
    def get_ticker(self, exchange, symbol):
        # print('-'*30)
        # print('threading {} start get ticker'.format(threading.get_ident()))
        try:
            ticker = exchange.fetch_ticker(symbol)
            self.count += 1
            # print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)
            # print(ticker)
            # 按时间顺序保存ticker, 留待以后进行分析使用
            temp_price = self.save_ticker(exchange.name, symbol, ticker)
            # print('threading {} {} saved {} ticker from {}'.format(threading.get_ident(), \
            #             exchange.iso8601(exchange.milliseconds()), symbol, exchange.name))
        # 出错，终止
        except Exception as e:
            print(e)
            self.stop_flag = True
            return []
        return temp_price

    # 取得每个市场的 货币对
    def get_market_symbols(self, exchange):
        target_symbols = []
        symbols = set()  # 从市场中取得所有symbol
        market = exchange.fetch_markets()
        # print('market:', market)
        for i in market:
            symbols.add(i['symbol'])
        # print('the symbols in {} is :{}'.format(exchange.name, target_symbols))
        self.candidate_exchange_symbol[exchange.name] = symbols

        for symbol in self.test_symbol:
            if symbol in symbols:
                if symbol not in self.valid_symbol:
                    self.valid_symbol.add(symbol)
                target_symbols.append(symbol)
        # print('target_symbols is {}'.format(target_symbols))
        return target_symbols

    # 多线程任务，按每个市场，市场中的每个 货币对 取得 ticker
    def multi_exchanges(self, _exchange):
        target_symbols = []  # market 中要取的symbol

        print('\nthreading {} start work\n'.format(threading.get_ident()))
        # print('start get ticker in {}'.format(_exchange))
        exchange = getattr(ccxt, _exchange)()

        # print('self.target_exchange_symbol : ', self.target_exchange_symbol)
        # symbol 数据只取一次，放入持久层，如存在，就不再取数
        if _exchange in self.target_exchange_symbol.keys():
            # print('已经存在symbols, 直接取数')
            target_symbols = self.target_exchange_symbol[_exchange]
        else:
            # print('不存在symbols, 从市场中取数')
            target_symbols = self.get_market_symbols(exchange)
            self.target_exchange_symbol[_exchange] = target_symbols

        symbol_price = []
        for _symbol in target_symbols:
            # 取得货币对 ticker 信息，用 PRICE 对象传递
            price = self.get_ticker(exchange, _symbol)
            symbol_price.append(price.get_price_array())
            # 间隔 ，防止被屏蔽
            time.sleep(self.interval)
        single_exchange_data = pd.DataFrame(symbol_price, columns=self.DataFrame_fieldnames)
        # print('single_exchange_data: ', single_exchange_data)
        # 往queue中添加exchange 数据
        self.data_queue.put(single_exchange_data)
        if self.data_queue.full():
            # print('已满，开始计算，并将queue清空')
            # 如果已满，开始计算，并将queue清空
            self.deal_data()

    # 如果两市场同种symbol价格差异超过0.5 %，则提示
    def deal_data(self):
        data = pd.DataFrame()
        while not self.data_queue.empty():
            tdata = self.data_queue.get()
            data = data.append(tdata)

        # 开始按symbol 将exchange 两两组合进行计算，如果两市场同种symbol价格差异超过0.5%，则提示
        for symbol in self.valid_symbol:
            # print('-'*30)
            # print('开始取数据，货币对为：', symbol)
            symbol_data = data[data.symbol==symbol]
            # print(symbol_data)
            for indexA, rowA in symbol_data.iterrows():
                for indexB, rowB in symbol_data.iterrows():
                    exchangeA = rowA['exchange']
                    exchangeB = rowB['exchange']
                    askA = rowA['ask']
                    askB = rowB['ask']
                    bidA = rowA['bid']
                    bidB = rowB['bid']
                    # print(exchangeA, exchangeB, askA, bidB)
                    if exchangeA != exchangeB:
                        rate = askA/bidB-1
                        # print(symbol, exchangeA + '-' + exchangeB, askA/bidB-1)
                        logger.info('{},{},{}'.format(symbol, exchangeA + '-' + exchangeB, askA/bidB-1))
                        if abs(rate) > 0.005:
                            logger.warning('!!!!!!!!!!!!!! rate more than 0.5% !!!!!!!!!!!!!!!!!')
                            logger.warning('the ticker is: {},{},{},{}'.format(symbol, exchangeA, askA, bidA))
                            logger.warning('the ticker is: {},{},{},{}'.format(symbol, exchangeB, askB, bidB))
                            # print('!!!!!!!!!!!!!! rate more than 0.5% !!!!!!!!!!!!!!!!!')
                            # print('the ticker is: {},{},{},{}'.format(symbol, exchangeA, askA, bidA))
                            # print('the ticker is: {},{},{},{}'.format(symbol, exchangeB, askB, bidB))

            # for i in combinations(symbol_data, 2):
            #     print(i)

    def main(self):
        all_task = []
        with ThreadPoolExecutor(len(self.good_exchanges)) as executor:
            while not self.stop_flag:
                now = time.time()
                for exchange in self.good_exchanges:
                    all_task.append(executor.submit(self.multi_exchanges, exchange))
                # time.sleep(self.sleep_time)
                print('\n----------total collected ticker {}-----------------\n'.format(self.count))
                if self.count > self.max_records:
                    break
                # all_task = [executor.submit(get_html, (url)) for url in urls]
                wait(all_task, timeout=40, return_when=ALL_COMPLETED)

                # 在全部访问完以后，对所有市场的所有symbol进行遍历，填充target_symbol_exchange.
                print('-------------------------fill_valid_exchange_currency-------------------------')
                if len(self.target_symbol_exchange) == 0:
                    self.fill_target_symbol_exchange()
                if len(self.valid_exchange_currency) == 0:
                    self.fill_valid_exchange_currency()

                # 根据不同市场 但货币相同，填充矩阵数据，交换价格为 1
                self.fill_matrix_by_exchange_same_currency()

                # 根据 每个 市场-货币对 的 ticker 更新matrix，更新完后，在此打印一次
                print(self.matrix)
                np.savetxt('matrix.txt', self.matrix, delimiter=',', fmt='%10.8f')
                np.savetxt('vertices.txt', self.vertices, delimiter=',', fmt='%s')

                print('spend time {}'.format(time.time() - now))
                print('...............................sleep.......................................')
                time.sleep(self.sleep_time)

            #  matrix 全部清零
            self.matrix = np.zeros((self.matrix_dim, self.matrix_dim))

        print('finished collect data')


if __name__ == '__main__':
    test = GetMultiExchangeTicker()
    test.main()