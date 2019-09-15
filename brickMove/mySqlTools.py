# -*- coding: utf-8 -*-
# @Time    : 2019-9-12 22:51
# @Author  : flyhawk
# @Email   : flyhawksz@163.com
# @File    : mySqlTools.py
# @Software: PyCharm

import logging  # log相关功能，不能总是用print那么low
from Mysql_connect_pool_tools import MyPymysqlPool


class MySqlTools:

    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象
        self.connargs = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456"}
        # 配置log信息存储的位置
        logging.basicConfig(filename='./debug.log', filemode="w", level=logging.DEBUG)
        # # 3秒内没有打开web页面，就放弃等待，防止死等，不管哪种语言，都要防范网络阻塞造成程序响应迟滞，CPU经常因此被冤枉
        # socket.setdefaulttimeout(3)
        self.mysql = None

    def write_one_dict_into_mysql(self, table_name, dict_data):
        fields = ','.join(dict_data.keys())
        values = ','.join(dict_data.values())
        try:
            logging.info("insert into " + table_name + " (ip) values (%s);")
            self.mysql.insert(
                "insert into {table} ({key}) values ({val});".format(table=table_name, key=fields, val=values))
            # self.mysql.end()

        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)

    def write_one_into_mysql(self, table_name, fields_tuple, value_tuple):
        fields = ','.join(fields_tuple)
        values = ','.join(value_tuple)
        try:
            logging.info("insert into " + table_name + " (ip) values (%s);")
            self.mysql.insert(
                "insert into {table} ({key}) values ({val});".format(table=table_name, key=fields, val=values))
            # self.mysql.end()

        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)

    # 如果多字段，value_list 形如 （（f1,f2,f3）, (f1,f2,f3)）
    def write_list_into_mysql(self, table_name, fields, value_list):
        try:
            logging.info("insert into " + table_name + " (%s) values (%s);")
            self.mysql.insertMany("insert into " + table_name + "  (" + fields + ") values (%s);", value_list)
            self.mysql.end()

        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)

    # 生成MySQL数据库连接池
    def create_mysql(self, connargs):
        logging.info("create_mysql")
        self.mysql = MyPymysqlPool(connargs)
