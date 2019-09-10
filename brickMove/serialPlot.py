#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqi
@contact: fly-hawk@126.com
@file: serialPlot.py
@time: 2019/9/10 11:36 PM
@desc:
'''


import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.read_csv(r'/Users/zhangqi/Desktop/test/test.csv')
    plt.plot(df['Date Time'],df['Close'])

    plt.ylabel(u'风速',fontproperties='SimHei')
    plt.xlabel(u'时间',fontproperties='SimHei')

    plt.grid(True)
    plt.show()