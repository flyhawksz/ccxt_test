from ccxtbt import CCXTStore
import backtrader as bt
from datetime import datetime, timedelta
import time


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', True),
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),  # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def start(self):
        self.counter = 0
        print('START')

    def __init__(self):

        self.macd1m = bt.indicators.MACD(self.datas[0])
        self.macd5m = bt.indicators.MACD(self.datas[1])

    def prenext(self):
        self.counter += 1
        print('prenext len %d - counter %d' % (len(self), self.counter))

    def next(self):

        # Get cash and balance
        # New broker method that will let you get the cash and balance for
        # any wallet. It also means we can disable the getcash() and getvalue()
        # rest calls before and after next which slows things down.

        # NOTE: If you try to get the wallet balance from a wallet you have
        # never funded, a KeyError will be raised! Change LTC below as approriate
        if self.live_data:
            cash, value = self.broker.get_wallet_balance('USDT')
        else:
            # Avoid checking the balance during a backfill. Otherwise, it will
            # Slow things down.
            cash = 'NA'

        # for data in self.datas:

        print('{} - {} \t| Cash {} | O: {} H: {} L: {} C: {} V:{:.5f} \tMACD(1):{} \tMACD(5):{}'.format(
            self.datas[0].datetime.datetime(),
            self.datas[0]._name, cash, self.datas[0].open[0], self.datas[0].high[0], self.datas[0].low[0],
            self.datas[0].close[0], self.datas[0].volume[0],
            self.macd1m[0], self.macd5m[0]))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = 'Data Status: {}'.format(data._getstatusname(status))
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False


if __name__ == '__main__':
    # apikey = 'x'
    # secret = 'x'

    cerebro = bt.Cerebro(quicknotify=True)

    # Add the strategy
    cerebro.addstrategy(TestStrategy)

    # Create our store
    # config = {'apiKey': apikey,
    #           'secret': secret,
    #           'enableRateLimit': True
    #           }

    # IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
    # for get cash or value if You have never held any LTC coins in your account.
    # So switch LTC to a coin you have funded previously if you get errors

    # store = CCXTStore(exchange='binance', currency='USDT', config=config, retries=5, debug=False)

    # Get the broker and pass any kwargs if needed.
    # ----------------------------------------------
    # Broker mappings have been added since some exchanges expect different values
    # to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
    # required if the broker uses the same values as the defaults in CCXTBroker.
    broker_mapping = {
        'order_types': {
            bt.Order.Market: 'market',
            bt.Order.Limit: 'limit',
            bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
            bt.Order.StopLimit: 'stop limit'
        },
        'mappings': {
            'closed_order': {
                'key': 'status',
                'value': 'closed'
            },
            'canceled_order': {
                'key': 'result',
                'value': 1}
        }
    }

    # broker = store.getbroker(broker_mapping=broker_mapping)
    # broker = store.getbroker()
    # cerebro.setbroker(broker)

    # Get our data
    # Drop newest will prevent us from loading partial data from incomplete candles
    hist_start_date = datetime.utcnow() - timedelta(minutes=150)
    # data = store.getdata(dataname='ETH/USDT',
    #                      name="ETHUSDT",
    #                      timeframe=bt.TimeFrame.Minutes,
    #                      fromdate=hist_start_date,
    #                      # todate=datetime.utcnow(),
    #                      compression=1,
    #                      # ohlcv_limit=50,
    #                      drop_newest=True)  # , historical=True)
    # data2 = store.getdata(dataname='ETH/USDT',
    #                         name="ETHUSDT",
    #                         timeframe=bt.TimeFrame.Minutes,
    #                         fromdate=hist_start_date,
    #                         #todate=datetime.utcnow(),
    #                         compression=5,
    #                         #ohlcv_limit=50,
    #                         drop_newest=True) #, historical=True)
    data = bt.feeds.CCXT(exchange='okex', symbol='BTC/USDT', timeframe=bt.TimeFrame.Ticks, compression=1)
    # Add the feed
    # cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=1, name="1MIN")
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name="5MIN")

    # Run the strategy
    cerebro.run()