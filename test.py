	
# -*- coding: utf-8 -*-
import pyupbit
import pandas as pd # pandas모듈 불러오기

access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"          # 본인 값으로 변경
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

# print(upbit.get_balances("KRW-BTC"))     # KRW-BTC 조회
# print(upbit.get_balance("KRW"))         # 보유 현금 조회
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

df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=2)
target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
print(target_price)

df = pyupbit.get_ohlcv("KRW-ETH", interval="day", count=2)
target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.2
print(target_price)

df = pyupbit.get_ohlcv("KRW-ADA", interval="day", count=2)
target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
print(target_price)

df = pyupbit.get_ohlcv("KRW-XRP", interval="day", count=2)
target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.1
print(target_price)
# print(pyupbit.get_tickers()) 

# get_start_time("KRW-ETH")