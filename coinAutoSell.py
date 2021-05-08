import time
import pyupbit
import datetime
import numpy as np

access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"

coins = ["BTC", "ETH", "ADA", "XRP"]

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

def get_buy_price(ticker):
    """산 가격 조회"""
    if ticker == "BTC":
        return 69183000
    elif ticker == "ETH":
        return 4279929
    elif ticker == "ADA":
        return 2075
    elif ticker == "XRP":
        return 2000

def get_earn_rate(ticker):
    """수익률 세팅"""
    if ticker == "BTC":
        return 1.03
    elif ticker == "ETH":
        return 1.03
    elif ticker == "ADA":
        return 1.05
    elif ticker == "XRP":
        return 1.05

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autosell start")
time.sleep(1)


# 자동매매 시작
while True:
    try:
        # globalK = funbBestK()

        time.sleep(5.0)
        # print("ddds")
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        
        if start_time + datetime.timedelta(seconds=10) < now < end_time - datetime.timedelta(seconds=10):
            for coin in coins:
                target_price = get_buy_price(coin) * get_earn_rate(coin)
                # e_target_price = get_buy_price("ETH") * get_earn_rate("ETH")
                # a_target_price = get_buy_price("ADA") * get_earn_rate("ADA")
                # x_target_price = get_buy_price("XRP") * get_earn_rate("XRP")

                current_price = get_current_price("KRW-" + coin)
                # print("cur",current_price,"tar",target_price)
                if target_price < current_price:
                    jan = get_balance(coin)
                    upbit.sell_market_order("KRW-" + coin, jan*0.9995)
                    print(coin+" 팔림")
                    coins.remove(coin)
                time.sleep(1)
                # print("for문")                
        else:
            time.sleep(100)
    except Exception as e:
        print(e)
        time.sleep(1)

# 백그라운드 실행: nohup python3 coinAutoSell.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 :print(pyupbit.get_tickers())     