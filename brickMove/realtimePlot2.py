# -*- coding: utf-8 -*-
# @Time    : 2019-9-11 23:14
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : realtimePlot2.py
# @Software: PyCharm

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#设置样式
plt.style.use('fivethirtyeight')
x_vals = []
y_vals = []
#定义函数读取csv文件内容
def animate(i):
    data = pd.read_csv('data.csv')
    x = data['x_value']
    y1 = data['total_1']
    y2 = data['total_2']

    plt.cla()
    #绘制线图
    plt.plot(x, y1, label='Channel 1')
    plt.plot(x, y2, label='Channel 2')
    plt.legend(loc='upper left')
    plt.tight_layout()
#调用FuncAnimation实时调用函数每秒执行1次
ani = FuncAnimation(plt.gcf(), animate, \
     interval=1000)

plt.tight_layout()
plt.show()