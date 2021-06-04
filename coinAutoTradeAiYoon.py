import time
import pyupbit
import datetime
import numpy as np
import math
import schedule
from fbprophet import Prophet
import pandas as pd

access = "oXNV9A36Dglx1IPXFsc38829tSV51WkKM17ghsV6"
secret = "KaUQe2rrVexFP85U34Ro9xUGzdCxJSH2DmHXS1g4"


limit_BTC = 400000
limit_ETH = 400000
limit_ADA = 400000
limit_XRP = 300000
limit_XLM = 400000
limit_DOT = 300000
limit_EOS = 400000
limit_WAVES = 400000
limit_BCH = 400000
limit_LTC = 400000
limit_FLOW = 400000
limit_XTZ = 400000
limit_LINK = 400000
limit_ENJ = 300000
limit_NEO = 300000






# coins = ["BTC", "ETH", "ADA", "XLM", "EOS", "XRP", "DOT" ,"WAVES","BCH","LTC","FLOW", "XTZ","LINK","ENJ","NEO"]
coins = ["BTC", "ETH", "EOS", "BCH", "LTC", "LINK", "ENJ", "NEO", "DOT", "XRP"]
# coins = ["BTC","ADA","EOS","WAVES","BCH","LTC","FLOW", "XTZ","LINK"]

"""------------------------------------------이하 공통 부분---------------------------------------------------------------"""
"""v1.071"""
# 1.04 매도1조건에 예측가가 매수가보다 낮을 경우에만 팔도록 조건 추가
# 1.05 매수가 업비트에서 들고 오도록 수정
# 1.06 RSI 지수 추가 ;; RSI지수가 30보다 작으면(과매도), 70보다 크면(과매수)
# 1.07 RSI 가 50밑이라도 2번 연속 지수 상승했다면 매수가능
# 1.071 예상가보다 현재가가 낮아도 목표가 돌파했다면 매수가능
"""변수 생성"""
for coin in coins:
    globals()['globalK_{}'.format(coin)] = 0.0
    globals()['close_price_{}'.format(coin)] = 0
    # globals()['bef_close_price_{}'.format(coin)] = 0
    globals()['current_price_{}'.format(coin)] = 0
    # globals()['bef_current_price_{}'.format(coin)] = 0
    globals()['buy_price_{}'.format(coin)] = 0
    globals()['sell_price_{}'.format(coin)] = 0
    globals()['rsi_b3_{}'.format(coin)] = 0
    globals()['rsi_b2_{}'.format(coin)] = 0
    globals()['rsi_b1_{}'.format(coin)] = 0
    globals()['rsi_{}'.format(coin)] = 0
    # globals()['limit_{}'.format(coin)] = 1000000

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
    global predicted_close_price
    # df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1000, period=1)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
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
        globals()['bef_current_price_{}'.format(coin)] = globals()['current_price_{}'.format(coin)] 
        print("predict:",coin, predicted_close_price)
    print("----------------------")
    time.sleep(2)        

def get_bestK_loop():
    for coin in coins:
        globals()['globalK_{}'.format(coin)] = get_bestK("KRW-"+coin)
        time.sleep(1)

def rsi(ohlc: pd.DataFrame, period: int = 14): 
    delta = ohlc["close"].diff() 
    ups, downs = delta.copy(), delta.copy() 
    ups[ups < 0] = 0 
    downs[downs > 0] = 0 
    AU = ups.ewm(com = period-1, min_periods = period).mean() 
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean() 
    RS = AU/AD 
    return pd.Series(100 - (100/(1 + RS)), name = "RSI")

rsi_continue_chk = False
sell_continue_chk = False

""" RSI 지표 가져오기 """    
def get_rsi(ticker):
    data = pyupbit.get_ohlcv(ticker, interval="minute5")
    now_rsi = rsi(data, 14).iloc[-1]
    coin = ticker.replace("KRW-","")
    globals()['rsi_b3_{}'.format(coin)] = globals()['rsi_b2_{}'.format(coin)]
    globals()['rsi_b2_{}'.format(coin)] = globals()['rsi_b1_{}'.format(coin)]
    globals()['rsi_b1_{}'.format(coin)] = globals()['rsi_{}'.format(coin)]
    globals()['rsi_{}'.format(coin)] = now_rsi
    print(coin, "B3_RSI:", globals()['rsi_b3_{}'.format(coin)])
    print(coin, "B2_RSI:", globals()['rsi_b2_{}'.format(coin)])
    print(coin, "B1_RSI:", globals()['rsi_b1_{}'.format(coin)])
    print(coin, "RSI:", now_rsi)
    globals()['rsi_{}'.format(coin)] = now_rsi
    time.sleep(1)

def get_rsi_loop():
    for coin in coins:
        get_rsi("KRW-"+coin)
        time.sleep(1)

def sell_price_loop():
    for coin in coins:
        globals()['sell_price_{}'.format(coin)] = 0

for coin in coins:
    globals()['globalK_{}'.format(coin)] = get_bestK("KRW-"+coin)
    time.sleep(1)
    if globals()['globalK_{}'.format(coin)] == 0:
        continue
    predict_price("KRW-" + coin)
    time.sleep(1)
    globals()['close_price_{}'.format(coin)] = predicted_close_price
    # globals()['bef_close_price_{}'.format(coin)] = predicted_close_price
    # globals()['bef_current_price_{}'.format(coin)] = globals()['current_price_{}'.format(coin)] 
    print(coin,'close_price:', globals()['close_price_{}'.format(coin)] )
    print(coin, globals()['globalK_{}'.format(coin)])
    print(coin,"target_price:", get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)]))
    # get_rsi(coin) # RSI 지표 구하기
    get_rsi("KRW-"+coin)
    # print(coin,rsi)
    time.sleep(1) # 속도가 느리면 다음 코인 값을 못 갖고와 에러남. 그래서 sleep

schedule.every(10).minutes.do(lambda: predict_price_loop())
schedule.every(5).minutes.do(lambda: get_rsi_loop())
schedule.every().day.at("09:02").do(lambda: get_bestK_loop())
schedule.every(60).minutes.do(lambda: sell_price_loop()) # sell_price 1시간마다 초기화 안 쓸거면 주석

# schedule.every(60).minutes.do(lambda: get_bestK_loop())
# schedule.every().day.at("09:03").do(lambda: predict_price_loop())

# schedule.every(20).seconds.do(lambda: predict_price_loop())

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# ------sell_price 입력하는 곳---------------
# 프로그램이 돌아가는 중 종료했을 경우에만 입력하면 됨
# sell_price: 장중에 매도한 코인을 다시 사지 않기 위한 기준. 0보다 크면 상관없다.


# sell_price_LINK = 36980
# sell_price_ENJ = 36980
# ------------------------------------------------
time.sleep(3)

# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()
        if start_time + datetime.timedelta(seconds=60) < now < end_time:
            for coin in coins:
                
                globals()['current_price_{}'.format(coin)]  = get_current_price("KRW-"+coin)
                # print(coin, "k:",globals()['globalK_{}'.format(coin)])
                # print(coin,"curren:",current_price, "target:", get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)]), "predict:", globals()['close_price_{}'.format(coin)])

                if globals()['close_price_{}'.format(coin)] == 0:
                    time.sleep(0.5)  
                    continue

                ma5 = get_ma5("KRW-"+coin)
                if ma5 is None:
                    print(coin, "ma5 None")
                    time.sleep(0.2)  
                    continue                
                target_price = get_target_price("KRW-"+coin, globals()['globalK_{}'.format(coin)])
                coinjan = get_balance(coin)
                # print(coin, "coinjan:",coinjan)
                if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:                
                    globals()['buy_price_{}'.format(coin)] = get_buy_price(coin)
                else:
                    globals()['buy_price_{}'.format(coin)] = 0     
                # time.sleep(0.1)
                # print(coin, globals()['limit_{}'.format(coin)])
                print(coin,"curren:",globals()['current_price_{}'.format(coin)] , "ma5:", ma5 , "predict:", globals()['close_price_{}'.format(coin)], "RSI:",globals()['rsi_{}'.format(coin)])
                if globals()['buy_price_{}'.format(coin)] > 0:
                    print("buy_price",coin, globals()['buy_price_{}'.format(coin)])
                if globals()['sell_price_{}'.format(coin)] > 0:
                    print("sell_price",coin, globals()['sell_price_{}'.format(coin)])     
                    time.sleep(0.5)
                    continue   
                if globals()['globalK_{}'.format(coin)] == 0 and globals()['current_price_{}'.format(coin)]  *1.05 > globals()['close_price_{}'.format(coin)]:
                    time.sleep(0.5)        
                    continue                             
                # print(coin, target_price)
                # if ((target_price <= current_price < target_price + globals()['offset_{}'.format(coin)]) and target_price * 1.01 < globals()['close_price_{}'.format(coin)])or current_price *1.05 < globals()['close_price_{}'.format(coin)]:
                if  ((globals()['current_price_{}'.format(coin)]  * 1.05 < globals()['close_price_{}'.format(coin)] or target_price < globals()['current_price_{}'.format(coin)])
                     and globals()['current_price_{}'.format(coin)]  > ma5):
                    krw = get_balance("KRW")
                    limit = globals()['limit_{}'.format(coin)]
                    coin_m = upbit.get_amount(coin)

                    # """이전 현재가보다 현재가가 낮으면 패스"""
                    # if globals()['bef_current_price_{}'.format(coin)] > globals()['current_price_{}'.format(coin)] :
                    #     print(coin, "bef_current_price", globals()['bef_current_price_{}'.format(coin)], "current_price",globals()['current_price_{}'.format(coin)] )
                    #     time.sleep(0.5)  
                    #     continue

                    # """이전 예상가보다 현재 예상가가 낮으면 패스"""
                    # if globals()['bef_close_price_{}'.format(coin)] > globals()['close_price_{}'.format(coin)]:
                    #     print(coin, "bef_predict",globals()['bef_close_price_{}'.format(coin)] ,"predict:", globals()['close_price_{}'.format(coin)])
                    #     time.sleep(0.5)  
                    #     continue
                    
                    if 30 < globals()['rsi_{}'.format(coin)] < 50:
                        rsi_continue_chk = False

                    if (globals()['rsi_{}'.format(coin)] > 30 and globals()['rsi_b3_{}'.format(coin)] < 30 and  globals()['rsi_{}'.format(coin)] > globals()['rsi_b1_{}'.format(coin)] 
                        > globals()['rsi_b2_{}'.format(coin)] > globals()['rsi_b3_{}'.format(coin)]):
                        rsi_continue_chk = True      

                    if globals()['rsi_b1_{}'.format(coin)] == 0 or globals()['rsi_b2_{}'.format(coin)] == 0 or globals()['rsi_b3_{}'.format(coin)] == 0:
                        rsi_continue_chk = False

                    if globals()['rsi_{}'.format(coin)] < globals()['rsi_b1_{}'.format(coin)] < globals()['rsi_b2_{}'.format(coin)] < globals()['rsi_b3_{}'.format(coin)]:
                        rsi_continue_chk = False

                    if globals()['rsi_{}'.format(coin)] > 70:
                        rsi_continue_chk = False

                    if rsi_continue_chk == False:
                        time.sleep(0.5)
                        continue

                    if krw is None or krw < 5000:
                        time.sleep(0.5)  
                        continue
                    if limit is None:
                        print(coin,"continue")
                        time.sleep(0.5)  
                        continue                        
                    if coin_m is None:
                        coin_m = 0
                    buyamt = limit - coin_m    
                    if buyamt > 5000 and buyamt <= limit:
                        if buyamt > krw:
                            buyamt = krw
                        print("-------buy",coin, krw, "---------")
                        upbit.buy_market_order("KRW-" + coin, buyamt*0.9995) 
                        # globals()['buy_price_{}'.format(coin)] = globals()['current_price_{}'.format(coin)]
                        print("buy_price",coin, globals()['buy_price_{}'.format(coin)])
                """매도0조건 RSI지수가 50보다 크면 패스"""        
                if 50 < globals()['rsi_{}'.format(coin)] <70:
                    sell_continue_chk = False

                """현재가가 목표가보다 크면 패스"""  
                if target_price <  globals()['current_price_{}'.format(coin)]:
                    sell_continue_chk = False               

                """매도3조건 RSI지수가 70 이상이면 매도"""
                if globals()['rsi_{}'.format(coin)] >75:  
                    sell_continue_chk = True

                if sell_continue_chk == False:
                    time.sleep(0.5)
                    continue

                """매도1조건"""        
                # if (globals()['sell_price_{}'.format(coin)]  == 0 and globals()['current_price_{}'.format(coin)]  *0.99 > globals()['close_price_{}'.format(coin)] and
                #     globals()['buy_price_{}'.format(coin)] < globals()['current_price_{}'.format(coin)]):
                #     # coinjan = get_balance(coin)
                #     if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:
                #         print("-------sell",coin, globals()['current_price_{}'.format(coin)] , "---------")
                #         upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                #         globals()['sell_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)] 
                #         # print("-------sell",coin, globals()['current_price_{}'.format(coin)] , "---------")
                #         print("_____buy_price",coin, globals()['buy_price_{}'.format(coin)])
                """매도2조건"""           
                if globals()['sell_price_{}'.format(coin)]  == 0  and globals()['buy_price_{}'.format(coin)] > 0 and globals()['buy_price_{}'.format(coin)] * 0.95 > globals()['current_price_{}'.format(coin)] :
                    # coinjan = get_balance(coin)
                    if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:
                        # print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                        globals()['sell_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)] 
                        print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        print("_______buy_price2",coin, globals()['buy_price_{}'.format(coin)])

                """매도3조건"""           
                if sell_continue_chk == True:
                    if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:
                        # print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                        globals()['sell_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)] 
                        print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        print("_______buy_price2",coin, globals()['buy_price_{}'.format(coin)])


                coin_m = upbit.get_amount(coin)  
                if coin_m is None:
                    coin_m = 0                
                limit = globals()['limit_{}'.format(coin)]
                if coin_m > limit * 0.95:
                    time.sleep(1)         
                time.sleep(0.5)  
            print("------------------------------------------------------")
        else:
            for coin in coins:
                coinjan = get_balance(coin)
                if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:                
                    upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                    # globals()['globalK_{}'.format(coin)] = get_bestK("KRW-" + coin)
            time.sleep(0.5)
    except Exception as e:
        print(e)
        time.sleep(1)

# 백그라운드 실행: nohup python3 coinAutoTradeAi.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 :print(pyupbit.get_tickers())     