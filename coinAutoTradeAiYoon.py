import time
import pyupbit
import datetime
import numpy as np
import math
import schedule
from fbprophet import Prophet

access = "oXNV9A36Dglx1IPXFsc38829tSV51WkKM17ghsV6"
secret = "KaUQe2rrVexFP85U34Ro9xUGzdCxJSH2DmHXS1g4"
globalK_BTC = 0.0
globalK_ETH = 0.0
globalK_ADA = 0.0
globalK_XRP = 0.0
globalK_XLM = 0.0
globalK_DOT = 0.0
globalK_EOS = 0.0
globalK_WAVES = 0.0
globalK_BCH = 0.0
globalK_LTC = 0.0
globalK_FLOW = 0.0
globalK_XTZ = 0.0
globalK_LINK = 0.0

limit_BTC = 1000000
limit_ETH = 1000000
limit_ADA = 1000000
limit_XRP = 1000000
limit_XLM = 1000000
limit_DOT = 1000000
limit_EOS = 1000000
limit_WAVES = 1000000
limit_BCH = 1000000
limit_LTC = 1000000
limit_FLOW = 1000000
limit_XTZ = 1000000
limit_LINK = 1000000


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


# offset_BTC = 10000
# offset_ETH = 5000
# offset_ADA = 10
# offset_XRP = 10
# offset_XLM = 3
# offset_DOT = 30
# offset_EOS = 30
# offset_WAVES = 30
# offset_BCH = 1500
# offset_LTC = 300
# offset_FLOW = 30
# offset_XTZ = 15
# offset_LINK = 50


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
    if date_diff_hour < 1:
        predicted_close_price = 0
        return    
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=date_diff_hour, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue

def predict_price_loop():
    global predicted_close_price
    for coin in coins:
        if globals()['globalK_{}'.format(coin)] == 0:
            continue        
        predict_price("KRW-" + coin)
        time.sleep(1.5)    
        globals()['close_price_{}'.format(coin)] = predicted_close_price
        print("predict:",coin, predicted_close_price)
    print("----------------------")
    time.sleep(2)        

def get_bestK_loop():
    for coin in coins:
        get_bestK("KRW-"+coin)
        time.sleep(1)
    

for coin in coins:
    globals()['globalK_{}'.format(coin)] = get_bestK("KRW-"+coin)
    time.sleep(1)
    if globals()['globalK_{}'.format(coin)] == 0:
        continue
    predict_price("KRW-" + coin)
    time.sleep(1)
    globals()['close_price_{}'.format(coin)] = predicted_close_price
    print(coin,'close_price:', globals()['close_price_{}'.format(coin)] )
    print(coin, globals()['globalK_{}'.format(coin)])
    print(coin,"target_price:", get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)]))
    time.sleep(1) # 속도가 느리면 다음 코인 값을 못 갖고와 에러남. 그래서 sleep

schedule.every(10).minutes.do(lambda: predict_price_loop())
schedule.every().day.at("09:01").do(lambda: get_bestK_loop())
schedule.every().day.at("09:02").do(lambda: predict_price_loop())

# schedule.every(20).seconds.do(lambda: predict_price_loop())

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


time.sleep(3)

# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()
        if start_time + datetime.timedelta(seconds=30) < now < end_time:
            for coin in coins:
                current_price = get_current_price("KRW-"+coin)
                # print(coin, "k:",globals()['globalK_{}'.format(coin)])
                # print(coin,"curren:",current_price, "target:", get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)]), "predict:", globals()['close_price_{}'.format(coin)])
                if globals()['close_price_{}'.format(coin)] == 0:
                    continue
                if globals()['globalK_{}'.format(coin)] == 0 and current_price *1.05 > globals()['close_price_{}'.format(coin)]:
                    time.sleep(1)        
                    continue 
                target_price = get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)])

                # print(globals()['globalK_{}'.format(coin)])
                print(coin,"curren:",current_price, "predict:", globals()['close_price_{}'.format(coin)])
                # print(coin, target_price)
                # if ((target_price <= current_price < target_price + globals()['offset_{}'.format(coin)]) and target_price * 1.01 < globals()['close_price_{}'.format(coin)])or current_price *1.05 < globals()['close_price_{}'.format(coin)]:
                if  current_price * 1.05 < globals()['close_price_{}'.format(coin)]:
                    krw = get_balance("KRW")
                    limit = globals()['limit_{}'.format(coin)]
                    coin_m = upbit.get_amount(coin)

                    if krw is None or krw < 5000:
                        continue
                    if limit is None:
                        print(coin,"continue")
                        continue                        
                    if coin_m is None:
                        coin_m = 0
                    buyamt = limit - coin_m    
                    if buyamt > 5000 and buyamt <= limit:
                        if buyamt > krw:
                            buyamt = krw
                        print("-------buy",coin, krw, "---------")
                        upbit.buy_market_order("KRW-" + coin, buyamt*0.9995) 
                if current_price *0.975 > globals()['close_price_{}'.format(coin)]:
                    coinjan = get_balance(coin)
                    print("-------sell",coin, current_price, "---------")
                    upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                    print("-------sell",coin, current_price, "---------")

                coin_m = upbit.get_amount(coin)  
                if coin_m is None:
                    coin_m = 0                
                limit = globals()['limit_{}'.format(coin)]
                if coin_m > limit * 0.95:
                    time.sleep(2)         
                time.sleep(0.5)  
            print("------------------------------------------------------")
        else:
            for coin in coins:
                coinjan = get_balance(coin)
                if coinjan > 0.00008:
                    upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                    # globals()['globalK_{}'.format(coin)] = get_bestK("KRW-" + coin)
            time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

# 백그라운드 실행: nohup python3 coinAutoTradeAi.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 :print(pyupbit.get_tickers())     