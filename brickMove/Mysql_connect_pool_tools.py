#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pymysql
import os
import configparser
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import re
import threading
import time


class Config(object):
    """
    # Config().get_content("user_information")

    配置文件里面的参数
    [notdbMysql]
    host = 192.168.1.101
    port = 3306
    user = root
    password = python123
    """

    def __init__(self, config_filename="myProjectConfig.cnf"):
        file_path = os.path.join(os.path.dirname(__file__), config_filename)
        self.cf = configparser.ConfigParser()
        self.cf.read(file_path)

    def get_sections(self):
        return self.cf.sections()

    def get_options(self, section):
        return self.cf.options(section)

    def get_content(self, section):
        result = {}
        for option in self.get_options(section):
            value = self.cf.get(section, option)
            result[option] = int(value) if value.isdigit() else value
        return result


class BasePymysqlPool(object):
    def __init__(self, connargs):
        self.db_host = connargs['host']   #'host'
        self.db_port = int(connargs['port'])
        self.user = connargs['user']
        self.password = str(connargs['passwd'])
        self.db = connargs['db']
        self.conn = None
        self.cursor = None


class MyPymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self, connargs):
        # self.conf = Config().get_content(conf_name)
        BasePymysqlPool.__init__(self, connargs)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if MyPymysqlPool.__pool is None:
            __pool = PooledDB(creator=pymysql,
                              mincached=1,
                              maxcached=20,
                              host=self.db_host,
                              port=self.db_port,
                              user=self.user,
                              passwd=self.password,
                              db=self.db,
                              use_unicode=False,
                              charset="utf8",
                              cursorclass=DictCursor)
        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            if num == 'all':
                result = self._cursor.fetchall()
            elif isinstance(num, int):
                result = self._cursor.fetchmany(num)
            else:
                result = self._cursor.fetchmany(10)
        else:
            result = False
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()

    def hasThisTable(self, table_name):
        '''
        判断是否存在此表
        :param table_name:表名
        :return: True  or  False
        '''
        sql = "show tables;"
        tables = self.getAll(sql)
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        if table_name in table_list:
            return 1  # 存在返回1
        else:
            return 0

    # ---------------------
    # 作者：不论如何未来很美好
    # 来源：CSDN
    # 原文：https: // blog.csdn.net / qq_36523839 / article / details / 80639297
    # 版权声明：本文为博主原创文章，转载请附上博文链接！

    def hasThisId(self, table_name, ID):
        '''
        判断在此表中是否已经有此主键
        :param table_name: 表名
        :param dateID: 主键值
        :return: True  or  False
        '''
        sql = "select dates from " + table_name + ";"
        ids = self.getAll(sql)
        for i in ids:
            if i[0] == ID:
                return True
        else:
            return False


# ---------------------
# 作者：RunffyCSDN
# 来源：CSDN
# 原文：https: // blog.csdn.net / RunffyCSDN / article / details / 81486880
# 版权声明：本文为博主原创文章，转载请附上博文链接！

if __name__ == '__main__':
#     mysql = MyPymysqlPool("notdbMysql")
#
#     sqlAll = "select * from myTest.aa;"
#     result = mysql.getAll(sqlAll)
#     print(result)
#
#     sqlAll = "select * from myTest.aa;"
#     result = mysql.getMany(sqlAll, 2)
#     print(result)
#
#     result = mysql.getOne(sqlAll)
#     print(result)
#
#     # mysql.insert("insert into myTest.aa set a=%s", (1))
#
#     # 释放资源
#     mysql.dispose()


    exitFlag = 0


    def get_conn48():
        conn = None
        try:
            conn = pymysql.connect(
                host="192.168.1.3",
                port=3308,
                user="root",
                passwd="mysqlpass",
                charset="utf8",
            )
        except Exception as err:
            print(err)
        return conn


    def get_data48(sql):
        conn = get_conn48()
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        return data


    class myThread(threading.Thread):
        def __init__(self, threadID, counter, member_id):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = "Thread-" + str(threadID)
            self.counter = counter
            self.member_id = member_id

        def run(self):
            print("开始线程：" + self.name)
            print_time(self.name, self.counter, self.member_id)
            print("退出线程：" + self.name)


    def print_time(threadName, counter, member_id):
        while counter:
            if exitFlag:
                threadName.exit()

            print("%s: %s" % (threadName, time.ctime(time.time())))
            conn = get_conn48()
            cursor = conn.cursor()

            try:
                # 执行sql语句
                sql = ''' update goeses.tb_member_balance set modify_time = modify_time + 1 where member_id=%s  ''' % (
                    member_id)
                print(sql)
                cursor.execute(sql)
                conn.commit()
            except:
                # 如果发生错误则回滚
                conn.rollback()
            # 关闭数据库连接
            conn.close()
            counter -= 1


    # 创建新线程
    thread1 = myThread(1, 500000, 1000000001)
    thread2 = myThread(2, 500000, 1000000002)
    thread3 = myThread(3, 500000, 1000000003)
    thread4 = myThread(4, 500000, 1000000004)
    thread5 = myThread(5, 500000, 1000000005)
    thread6 = myThread(6, 500000, 1000000006)
    thread7 = myThread(7, 500000, 1000000007)
    thread8 = myThread(8, 500000, 1000000008)
    thread9 = myThread(9, 500000, 1000000009)
    thread10 = myThread(10, 500000, 1000000010)
    thread11 = myThread(11, 500000, 1000000011)
    thread12 = myThread(12, 500000, 1000000012)
    thread13 = myThread(13, 500000, 1000000013)
    thread14 = myThread(14, 500000, 1000000014)
    thread15 = myThread(15, 500000, 1000000015)
    thread16 = myThread(16, 500000, 1000000016)
    thread17 = myThread(17, 500000, 1000000017)
    thread18 = myThread(18, 500000, 1000000018)
    thread19 = myThread(19, 500000, 1000000019)
    thread20 = myThread(20, 500000, 1000000020)
    thread21 = myThread(21, 500000, 1000000021)
    thread22 = myThread(22, 500000, 1000000022)
    thread23 = myThread(23, 500000, 1000000023)
    thread24 = myThread(24, 500000, 1000000024)
    thread25 = myThread(25, 500000, 1000000025)
    thread26 = myThread(26, 500000, 1000000026)
    thread27 = myThread(27, 500000, 1000000027)
    thread28 = myThread(28, 500000, 1000000028)
    thread29 = myThread(29, 500000, 1000000029)
    thread30 = myThread(30, 500000, 1000000030)
    thread31 = myThread(31, 500000, 1000000031)
    thread32 = myThread(32, 500000, 1000000032)
    thread33 = myThread(33, 500000, 1000000033)
    thread34 = myThread(34, 500000, 1000000034)
    thread35 = myThread(35, 500000, 1000000035)
    thread36 = myThread(36, 500000, 1000000036)
    thread37 = myThread(37, 500000, 1000000037)
    thread38 = myThread(38, 500000, 1000000038)
    thread39 = myThread(39, 500000, 1000000039)
    thread40 = myThread(40, 500000, 1000000040)
    thread41 = myThread(41, 500000, 1000000041)
    thread42 = myThread(42, 500000, 1000000042)
    thread43 = myThread(43, 500000, 1000000043)
    thread44 = myThread(44, 500000, 1000000044)
    thread45 = myThread(45, 500000, 1000000045)
    thread46 = myThread(46, 500000, 1000000046)
    thread47 = myThread(47, 500000, 1000000047)
    thread48 = myThread(48, 500000, 1000000048)
    thread49 = myThread(49, 500000, 1000000049)
    thread50 = myThread(50, 500000, 1000000050)

    # 开启新线程
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()
    thread9.start()
    thread10.start()
    thread11.start()
    thread12.start()
    thread13.start()
    thread14.start()
    thread15.start()
    thread16.start()
    thread17.start()
    thread18.start()
    thread19.start()
    thread20.start()
    thread21.start()
    thread22.start()
    thread23.start()
    thread24.start()
    thread25.start()
    thread26.start()
    thread27.start()
    thread28.start()
    thread29.start()
    thread30.start()
    thread31.start()
    thread32.start()
    thread33.start()
    thread34.start()
    thread35.start()
    thread36.start()
    thread37.start()
    thread38.start()
    thread39.start()
    thread40.start()
    thread41.start()
    thread42.start()
    thread43.start()
    thread44.start()
    thread45.start()
    thread46.start()
    thread47.start()
    thread48.start()
    thread49.start()
    thread50.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()
    thread11.join()
    thread12.join()
    thread13.join()
    thread14.join()
    thread15.join()
    thread16.join()
    thread17.join()
    thread18.join()
    thread19.join()
    thread20.join()
    thread21.join()
    thread22.join()
    thread23.join()
    thread24.join()
    thread25.join()
    thread26.join()
    thread27.join()
    thread28.join()
    thread29.join()
    thread30.join()
    thread31.join()
    thread32.join()
    thread33.join()
    thread34.join()
    thread35.join()
    thread36.join()
    thread37.join()
    thread38.join()
    thread39.join()
    thread40.join()
    thread41.join()
    thread42.join()
    thread43.join()
    thread44.join()
    thread45.join()
    thread46.join()
    thread47.join()
    thread48.join()
    thread49.join()
    thread50.join()

    print("退出主线程")