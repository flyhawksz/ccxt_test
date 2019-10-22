import backtrader as bt
from datetime import datetime, timedelta
import time
import traceback
import ccxt


class TestStrategy(bt.Strategy):

    def start(self):
        self.counter = 0

        print('START')

    def next(self):
        try:
            self.counter += 1
            print(self.data0.open[0], self.data1.open[0])
            print("lalalal")
        except:
            traceback.print_exc()
            pass
        # sio.emit('logs', 'fries', namespace='/test', broadcast=True)


# io.on('connect', namespace='/test')
# ARBY = TestStrategy


def d(sid, environ):
    print('connect + thats sid', sid)


# @sio.on('arbitrage', namespace='/test')
def check_oppor(sid, DATA):
    # sio.emit('logs', 'STARTING BOT...', namespace='/test', broadcast=True)
    print(DATA['API_KEY'], DATA['API_SECRET'], DATA['EXCHANGES'])
    global addD, datas
    global broker, makers, takers, withdrawls, configs, exchanges, keys, secrets
    exchanges = DATA['EXCHANGES']
    keys = DATA['API_KEY']
    secrets = DATA['API_SECRET']
    exchanges = [item for items in exchanges for item in items.split(",")]
    keys = [item for items in keys for item in items.split(",")]
    secrets = [item for items in secrets for item in items.split(",")]

    for key, secret in zip(keys, secrets):
        config = {
            'apiKey': key,
            'secret': secret,
            'nonce': lambda: str(int(time.time() * 1000))
        }
        configs.append(config)

    datas = []
    cerebro = bt.Cerebro()

    hist_start_date = datetime.utcnow() - timedelta(minutes=3)

    indicators = []
    print(len(configs))
    d = exchanges

    for index, c in zip(range(len(configs)), configs):
        try:
            print(index, "this is the index")
            Obj = getattr(ccxt, exchanges[index])
            Obj = Obj(c)

            indicators.append(Obj)

            data = bt.feeds.CCXT(exchange=exchanges[index], config=c,
                                 symbol='ETH/BTC',
                                 timeframe=bt.TimeFrame.Minutes,
                                 fromdate=hist_start_date, compression=1, ohlcv_limit=999, retries=100)

            data1 = bt.feeds.CCXT(exchange=exchanges[index], config=c,
                                  symbol='BCH/BTC',
                                  timeframe=bt.TimeFrame.Minutes,
                                  fromdate=hist_start_date, compression=1, ohlcv_limit=999, retries=100)

            data2 = bt.feeds.CCXT(exchange=exchanges[index], config=c,
                                  symbol='LTC/BTC',
                                  timeframe=bt.TimeFrame.Minutes,
                                  fromdate=hist_start_date, compression=1, ohlcv_limit=999, retries=100)

            datas.append([data, data1, data2])
            print(datas)
        except:
            traceback.print_exc()
            pass
    print(datas)
    allDatas = [elem for sublist in datas for elem in sublist]
    print(allDatas)
    for i in indicators:
        fees = i.describe()['fees']
        maker = fees['trading']['maker']
        taker = fees['trading']['taker']
        makers.append(maker)
        takers.append(taker)

        withdrawal = fees['funding']['withdraw']
        withdrawls.append(withdrawal)
        print(withdrawal)

    broker = bt.brokers.CCXTBroker(exchange='kucoin',
                                   currency='BTC', config=configs[1])

    addD = cerebro.adddata
    print(allDatas)
    for ind, d in enumerate(allDatas, start=0):
        try:
            addD(d, name="data" + str(ind))
            print(ind)
        except:
            traceback.print_exc()
            pass

    print(allDatas)

    cerebro.addstrategy(TestStrategy)
    cerebro.run()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    hist_start_date = datetime.utcnow() - timedelta(minutes=10)
    data_min = bt.feeds.CCXT(exchange='bitmex', symbol="BTC/USD", name="btc_usd_min", fromdate=hist_start_date,
                             timeframe=bt.TimeFrame.Minutes)
    cerebro.adddata(data_min)
    cerebro.addstrategy(TestStrategy)
    cerebro.run()
# ————————————————
# 版权声明：本文为CSDN博主「点火三周」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/u013613428/article/details/83304472