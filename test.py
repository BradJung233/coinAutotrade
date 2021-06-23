	
# -*- coding: utf-8 -*-
import pyupbit
import pandas as pd # pandas모듈 불러오기
import math


access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"          # 본인 값으로 변경
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

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

# print(upbit.get_balances("KRW-BTC"))     # KRW-BTC 조회
# print(get_balance("KRW"))         # 보유 현금 조회
# print(upbit.get_amount("ETH"))     # 코인 매수 금액 조회
# print(upbit.get_amount("BTC"))     # 코인 매수 금액 조회

# print(upbit.get_order("KRW-BTC",state='done',kind='normal', contain_req=False))
# print(pyupbit.get_tickers())  

# df = pyupbit.get_ohlcv("KRW-BTC", count=7)
# print(pd.DataFrame(df))

# print(upbit.get_balances("KRW-ADA"))     # KRW-BTC 조회

# 목표 매수가 조회
# df = pyupbit.get_ohlcv("KRW-ETH", interval="day", count=2)
# target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
# print(target_price)

# print(pyupbit.get_ohlcv("KRW-ADA", interval="day", count=1))

# df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=2)
# target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.0
# print(target_price)

# df = pyupbit.get_ohlcv("KRW-ETH", interval="day", count=2)
# target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
# print(target_price)

# df = pyupbit.get_ohlcv("KRW-XLM", interval="day", count=2)
# target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
# print(target_price)


# df = pyupbit.get_ohlcv("KRW-XRP", interval="day", count=2)
# target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.0
# print(target_price)
# print(pyupbit.get_tickers()) 
# print(math.floor(target_price))

"""이동 평균선 조회"""
# df = pyupbit.get_ohlcv("KRW-ADA", interval="day", count=5)
# ma5 = df['close'].rolling(5).mean().iloc[-1]

# print(ma5)

# def get_start_time(ticker):
#     """시작 시간 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
#     start_time = df.index[0]
#     return start_time

# print(get_start_time("KRW-BTC"))
# get_start_time("KRW-ETH")

def get_opening_price(ticker):
    """시작가 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['opening_price'] is not None:
                return float(b['opening_price'])
            else:
                return 0
        print(b)
    return 0  

print(get_opening_price("KRW-BTC"))    
pyupbit.get