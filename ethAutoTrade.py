import time
import pyupbit
import datetime
import numpy as np

access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"
globalK = 0.1

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


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-ETH",count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_bestK():
    ror2 = 0.0
    bestK = 0.0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        if ror2 < ror:
            ror2 = ror
            bestK = k
    if ror2 < 1.01:
        bestK = 0             
    return round(bestK,1)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
globalK = get_bestK()
time.sleep(1)

print("bestk:", globalK)

# 자동매매 시작
while True:
    try:
        time.sleep(2)
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=1000):
            target_price = get_target_price("KRW-ETH", globalK)
            current_price = get_current_price("KRW-ETH")
            if target_price < current_price:   
                krw = get_balance("KRW")
                limit = 4500000
                eth_m = upbit.get_amount("ETH")
                if eth_m is None:
                    eth_m = 0
                krw = limit - eth_m
                if krw > 5000 and krw < limit and globalK > 0:
                    upbit.buy_market_order("KRW-ETH", krw*0.9995)
            eth_m = upbit.get_amount("ETH")  
            if eth_m > 4400000:
                time.sleep(100)                       
        else:
            eth = get_balance("ETH")
            if eth > 0.0017:
                upbit.sell_market_order("KRW-ETH", eth*0.9995)
            globalK = get_bestK()
            time.sleep(1)    
    except Exception as e:
        print(e)
        time.sleep(1)

# 백그라운드 실행: nohup python3 ethAutoTrade.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 :print(pyupbit.get_tickers())     