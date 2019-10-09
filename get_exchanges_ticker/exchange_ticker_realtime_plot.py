# -*- coding: utf-8 -*-
# @Time    : 2019-9-11 23:14
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : realtimePlot2.py
# @Software: PyCharm

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class ExchangeTickerRealtimePlot:
    def __init__(self):
        self.root = os.getcwd()
        # 数据文件夹，不存在，就创建
        self.data_path = os.path.join(self.root, 'data\\')

        # 读取所有文件，按exchange, symbol拆分
        # symbol 放入一个列表，如果已存在，则将exchange放入该值中，这样可以统计每一symbol有哪些exchange
        # 如果不存在，则增加新的symbol， 加入exchange
        self.classify_dir_list = self.classify_dir()
        self.fieldnames = ['timestamp', 'bid', 'ask']

    # 数据文件预处理，按symbol进行分类，形成列表，每个子图都读一次同symbol的文件。
    def classify_dir(self):
        classify_dir = []
        list = os.listdir(self.data_path)  # 列出文件夹下所有的目录与文件
        for i in range(0, len(list)):
            path = os.path.join(self.data_path, list[i])
            if os.path.isdir(path):
                classify_dir.append(path)
            # if os.path.isfile(filepath):
            #     exchange, symbol = list[i].split('_')
            #     if symbol not in symbols:
            #         symbol[]
        return classify_dir

    def read_data_plot(self, path):
        exchange = os.path.basename(path)
        data = []
        list = os.listdir(path)  # 列出文件夹下所有的目录与文件
        for i in range(len(list)):
            file_path = os.path.join(path, list[i])
            if exchange == 'BTCUSD' and os.path.isfile(file_path):
                data = pd.read_csv(file_path)
                data['Date-Time'] = pd.to_datetime(data['timestamp'], \
                                    unit='ms').dt.strftime('%Y-%m-%d %H:%M')

                print(data)
                plt.plot(data['Date-Time'], data['bid'], data['ask'])
        plt.show()



                # 调用FuncAnimation实时调用函数每秒执行1次
                # ani = FuncAnimation(plt.gcf(), self.animate, \
                #                     interval=1000)
                #
                # plt.tight_layout()
                # plt.show()
                # self.animate(data, list[i])

            # df = pd.merge(df1, df2, on='Date-Time', how='inner')
            #
            # df.sort_values('Date-Time', inplace=True)
            # print(df.head(10))

    def animate(self, data, exchange):
        print('start plot of {}'.format(exchange))
        # data = pd.read_csv('data.csv')
        x = data['Date-Time']
        y1 = data['bid']
        y2 = data['ask']

        plt.cla()
        # 绘制线图
        plt.plot(x, y1, label=exchange + 'bid')
        plt.plot(x, y2, label=exchange + 'ask')
        plt.legend(loc='upper left')
        plt.tight_layout()

    def main(self):
        for path in self.classify_dir_list:
            self.read_data_plot(path)

# 第二步，按symbol读取文件
# 循环遍历symbol ，分别组合symbol和exchange，取得文件数据


# 第三步，绘制图形

if __name__ == '__main__':
    # path = 'F:\PycharmProjects\ccxt_test2\get_exchanges_ticker\data\BTCUSD'
    plot = ExchangeTickerRealtimePlot()
    plot.main()