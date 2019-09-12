#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqi
@contact: fly-hawk@126.com
@file: serialPlot.py
@time: 2019/9/10 11:36 PM
@desc:
'''

import time
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ == '__main__':
    # df = pd.read_csv(r'/Users/zhangqi/Desktop/test/test.csv')
    df1 = pd.read_csv(r't1.csv')
    df2 = pd.read_csv('t2.csv')

    df1['Date-Time'] = pd.to_datetime(df1['Date Time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M')
    df2['Date-Time'] = pd.to_datetime(df1['Date Time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M')

    print(df1.head(10))
    print('-'*60)
    print(df2.head(10))

    print('*'*60)

    # df['Date-Time'] = df['Date Time'].apply(lambda x:time.mktime(time.strptime(x,'%Y-%m-%d %H:%M:%S')))
    # print(df.head())
    df = pd.merge(df1, df2, on='Date-Time', how='inner')
    # df.set_index('Date-Time', inplace=True)
    # df.sort_index()
    df.sort_values('Date-Time', inplace=True)
    print(df.head(10))

    x = df['Date-Time']
    # print(x)
    y1 = df['Close_x']
    y2 = df['Close_y']
    # figure布局
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    #
    # 配置横坐标
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    # xfmt = mdates.DateFormatter('%Y-%m-%d %H')  ##正确显示时间序列
    # ax.xaxis.set_major_formatter(xfmt)

    # 设置x轴主刻度格式
    # alldays = mdates.DayLocator()  # 主刻度为每天
    # ax1.xaxis.set_major_locator(alldays)  # 设置主刻度
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
    # # 设置副刻度格式
    hoursLoc = mpl.dates.HourLocator(interval=1)  # 为6小时为1副刻度
    # ax1.xaxis.set_minor_locator(hoursLoc)
    # ax1.xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    minuteLoc = mpl.dates.MinuteLocator(interval=10)  # 为6小时为1副刻度
    ax1.xaxis.set_major_locator(hoursLoc)
    ax1.xaxis.set_minor_locator(minuteLoc)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # ax1.plot(x, y1)
    # ax1.plot(x, y2)

    ax1.plot(x, y1)
    # ax1.plot_date(x, y2)

    plt.ylabel(u'price', fontproperties='SimHei')
    plt.xlabel(u'time', fontproperties='SimHei')

    plt.gcf().autofmt_xdate()  # 自动旋转日期标记
    plt.grid(True)

    # ax1.tick_params(pad=2)

    plt.show()