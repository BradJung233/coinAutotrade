import time
import pyupbit
import datetime
import numpy as np
import math
import schedule
from fbprophet import Prophet

access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"
globalKBTC = 0.0
globalKETH = 0.0
globalKADA = 0.0
globalKXRP = 0.0
globalKXLM = 0.0
globalKDOT = 0.0
globalKEOS = 0.0
globalKWAVES = 0.0
globalKBCH = 0.0
globalKLTC = 0.0
globalKFLOW = 0.0
globalKXTZ = 0.0
globalKLINK = 0.0

limitBTC = 1000000
limitETH = 1000000
limitADA = 1000000
limitXRP = 1000000
limitXLM = 1000000
limitDOT = 1000000
limitEOS = 1000000
limitWAVES = 1000000
limitBCH = 1000000
limitLTC = 1000000
limitFLOW = 1000000
limitXTZ = 1000000
limitLINK = 1000000

offsetBTC = 10000
offsetETH = 5000
offsetADA = 10
offsetXRP = 10
offsetXLM = 3
offsetDOT = 30
offsetEOS = 30
offsetWAVES = 30
offsetBCH = 1500
offsetLTC = 300
offsetFLOW = 30
offsetXTZ = 15
offsetLINK = 50

close_price_BTC = 0
close_price_ETH = 0
close_price_ADA = 0
close_price_XRP = 0
close_price_XLM = 0
close_price_DOT = 0
close_price_EOS = 0
close_price_WAVES = 0
close_price_BCH = 0
close_price_LTC = 0
close_price_FLOW = 0
close_price_XTZ = 0
close_price_LINK = 0




# coins = ["BTC", "ETH", "ADA", "XLM", "EOS", "XRP", "DOT" ,"WAVES","BCH","LTC","FLOW", "XTZ","LINK"]
coins = ["BTC","ADA","EOS","WAVES","BCH","LTC","FLOW", "XTZ","LINK"]


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0            
def get_buy_price(ticker):
    """매수가 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0  

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_ror(k=0.5, ticker="KRW-BTC"):
    df = pyupbit.get_ohlcv(ticker,count=5)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_bestK(ticker):
    ror2 = 0.0
    bestK = 0.0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k,ticker)
        if ror2 < ror:
            ror2 = ror
            bestK = k
    if ror2 < 1.02:
        bestK = 0            
    return round(bestK,1)

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    _now = datetime.datetime.now()
    _start_time = get_start_time("KRW-BTC")
    _end_time = _start_time + datetime.timedelta(days=1)    
    date_diff = _end_time - _now
    date_diff_hour = round(date_diff.seconds/3600)
    
    global predicted_close_price
 
    # print(ticker, date_diff_hour)
    # df = pyupbit.get_ohlcv(ticker, count=1000, period=1)
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1000)

    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    print("date_diff_hour",date_diff_hour)
    future = model.make_future_dataframe(periods=24, freq='H')
    # future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    print(forecast)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    # print("closedf:",closeDf)
    predicted_close_price = closeValue

def predict_price_loop():
    global predicted_close_price
    for coin in coins:
        # if globals()['globalK{}'.format(coin)] == 0:
        #     continue        
        predict_price("KRW-" + coin)
        time.sleep(1.5)    
        globals()['close_price_{}'.format(coin)] = predicted_close_price
        print("predict:",coin, predicted_close_price)
    print("----------------------")
    time.sleep(2)        

def get_bestK_loop():
    for coin in coins:
        globals()['globalK{}'.format(coin)] = get_bestK("KRW-" + coin)
        time.sleep(1)
        print("loop",coin, globals()['globalK{}'.format(coin)])

# schedule.every(20).seconds.do(lambda: predict_price_loop())

# 로그인
upbit = pyupbit.Upbit(access, secret)
# print("autotrade start")
predict_price("KRW-THETA")

# print(get_buy_price("ENJ"))
# time.sleep(3)

# get_bestK_loop()

# 자동매매 시작
# while True:
#     try:
#         # globalK = funbBestK()

#         now = datetime.datetime.now()
#         start_time = get_start_time("KRW-BTC")
#         end_time = start_time + datetime.timedelta(days=1)
#         schedule.run_pending()
#         if start_time + datetime.timedelta(seconds=30) < now < end_time:
#             time.sleep(0.5)               
#         else:
#             time.sleep(1)
#     except Exception as e:
#         print(e)
#         time.sleep(1)

# 백그라운드 실행: nohup python3 coinAutoTradeAi.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 :print(pyupbit.get_tickers())     