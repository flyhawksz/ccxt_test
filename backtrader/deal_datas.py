# -*- coding: utf-8 -*-
# @Time    : 2019-11-10 19:46
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : deal_datas.py
# @Software: PyCharm
import pandas as pd
import os


def main():
    modpath = os.path.join(os.getcwd(), 'datas\stock_history')
    if not os.path.exists(modpath):
        os.makedirs(modpath)
    datapath = os.path.join(modpath, '600100.csv')

    df = pd.read_csv(datapath, header=0, encoding='gbk')
    print(df.columns)
    columns = df.columns.values.tolist()  # 获取列名列表，注意values，tolist的使用

    new_df = df.sort_values('日期', ascending=True)
    print(new_df)
    col_n = ['日期', '开盘价', '收盘价', '最高价', '最低价', '成交量']
    new_df1 = pd.DataFrame(new_df, columns=col_n)
    print(new_df1)
    new_df1.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    print(new_df1)


if __name__ == '__main__':
    main()