import time
import pyupbit
import datetime
import numpy as np
import schedule
import pandas as pd

access = "NBfy02ssHZPdySYKdZIHHNRyv0Ke2Tk8qzvlxV0z"
secret = "3ChZhxpxYMcgLpAMZK7x7DpeL8PSFLQap6XDdu80"


# limit_BTC = 1000000
# limit_ETH = 1000000
# limit_ADA = 1000000
# limit_XRP = 1000000
# limit_XLM = 1000000
# limit_DOT = 1000000
# limit_EOS = 1000000
# limit_WAVES = 1000000
# limit_BCH = 1000000
# limit_LTC = 1000000
# limit_FLOW = 1000000
# limit_XTZ = 1000000
# limit_LINK = 1000000

# coins = ["BTC", "ETH", "ADA", "XLM", "EOS", "XRP", "DOT" ,"WAVES","BCH","LTC","FLOW", "XTZ","LINK"]
coins = ["BTC","ADA","EOS","WAVES","BCH","LTC","FLOW","LINK","THETA","ENJ","VET","TFUEL","ETC","XTZ","ONG","BTG","BCHA","BSV","DOGE"]

"""------------------------------------------이하 공통 부분---------------------------------------------------------------"""
"""v1.088"""
# 1.81 매도8조건에 매수가가 10프로 상승하면 팔도록 조건 추가
# 1.84 매도7조건 2번연속 -> 3번연속으로 수정
# 1.85 매도10조건 추가
# 1.87 매수조건 수정, 매도조건 11,12 추가
# 1.88 K값 무시

"""변수 생성"""
for coin in coins:
    globals()['globalK_{}'.format(coin)] = 0.0
    globals()['close_price_{}'.format(coin)] = 0
    # globals()['bef_close_price_{}'.format(coin)] = 0
    globals()['past_b30_price_{}'.format(coin)] = 0
    globals()['past_b20_price_{}'.format(coin)] = 0
    globals()['past_b10_price_{}'.format(coin)] = 0
    globals()['past_b3_price_{}'.format(coin)] = 0
    globals()['past_b2_price_{}'.format(coin)] = 0
    globals()['past_b1_price_{}'.format(coin)] = 0
    globals()['past_b0_price_{}'.format(coin)] = 0
    globals()['past_price_{}'.format(coin)] = 0
    globals()['current_price_{}'.format(coin)] = 0
    globals()['opening_price_{}'.format(coin)] = 0
    # globals()['bef_current_price_{}'.format(coin)] = 0
    globals()['buy_price_{}'.format(coin)] = 0
    globals()['sell_price_{}'.format(coin)] = 0
    globals()['rsi_b5_{}'.format(coin)] = 0
    globals()['rsi_b4_{}'.format(coin)] = 0
    globals()['rsi_b3_{}'.format(coin)] = 0
    globals()['rsi_b2_{}'.format(coin)] = 0
    globals()['rsi_b1_{}'.format(coin)] = 0
    globals()['rsi_{}'.format(coin)] = 0
    globals()['sell_time_{}'.format(coin)]= None
    globals()['limit_{}'.format(coin)] = 500000

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

     

def get_opening_loop():
    for coin in coins:
        globals()['opening_price_{}'.format(coin)] = globals()['current_price_{}'.format(coin)]
        time.sleep(0.1)

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
trade_message =""

""" RSI 지표 가져오기 """    
def get_rsi(ticker):
    data = pyupbit.get_ohlcv(ticker, interval="minute5")
    now_rsi = rsi(data, 14).iloc[-1]
    coin = ticker.replace("KRW-","")
    globals()['rsi_b5_{}'.format(coin)] = globals()['rsi_b4_{}'.format(coin)]
    globals()['rsi_b4_{}'.format(coin)] = globals()['rsi_b3_{}'.format(coin)]
    globals()['rsi_b3_{}'.format(coin)] = globals()['rsi_b2_{}'.format(coin)]
    globals()['rsi_b2_{}'.format(coin)] = globals()['rsi_b1_{}'.format(coin)]
    globals()['rsi_b1_{}'.format(coin)] = globals()['rsi_{}'.format(coin)]
    globals()['rsi_{}'.format(coin)] = now_rsi
    print(coin, "B5_RSI:", globals()['rsi_b5_{}'.format(coin)])
    print(coin, "B4_RSI:", globals()['rsi_b4_{}'.format(coin)])
    print(coin, "B3_RSI:", globals()['rsi_b3_{}'.format(coin)])
    print(coin, "B2_RSI:", globals()['rsi_b2_{}'.format(coin)])
    print(coin, "B1_RSI:", globals()['rsi_b1_{}'.format(coin)])
    print(coin, "RSI:", now_rsi)
    print("--------")
    globals()['rsi_{}'.format(coin)] = now_rsi
    time.sleep(1)

def get_rsi_loop():
    for coin in coins:
        # if globals()['globalK_{}'.format(coin)] == 0:
        #     time.sleep(0.1)
        #     continue        
        get_rsi("KRW-"+coin)
        time.sleep(1)

def sell_price_loop():
    for coin in coins:
        # if globals()['globalK_{}'.format(coin)] == 0:
        #     time.sleep(0.1)
        #     continue              
        coin_selltime = globals()['sell_time_{}'.format(coin)] 
        if coin_selltime is None:
            globals()['sell_price_{}'.format(coin)] = 0
            continue
        now = datetime.datetime.now()
        if coin_selltime + datetime.timedelta(hours=6) <  now:
            globals()['sell_price_{}'.format(coin)] = 0
            print(coin, "sell_price init")        
    print("sell_price init")        

def past_price_loop():
    for coin in coins:
        # if globals()['globalK_{}'.format(coin)] == 0:
        #     time.sleep(0.1)
        #     continue              
        # now = datetime.datetime.now()
        globals()['past_b30_price_{}'.format(coin)] = globals()['past_b20_price_{}'.format(coin)] 
        globals()['past_b20_price_{}'.format(coin)] = globals()['past_b10_price_{}'.format(coin)] 
        globals()['past_b10_price_{}'.format(coin)] =globals()['past_price_{}'.format(coin)] 
        globals()['past_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)]
        print(coin, "past_b30_price:", globals()['past_b30_price_{}'.format(coin)])
        print(coin, "past_b20_price:", globals()['past_b20_price_{}'.format(coin)])
        print(coin, "past_b10_price:", globals()['past_b10_price_{}'.format(coin)])
        print(coin, "past_price:", globals()['past_price_{}'.format(coin)])

    print("past_price setting")    

def past_price_loop2():
    for coin in coins:
        # if globals()['globalK_{}'.format(coin)] == 0:
        #     time.sleep(0.1)
        #     continue              
        # now = datetime.datetime.now()
        globals()['past_b3_price_{}'.format(coin)] = globals()['past_b2_price_{}'.format(coin)] 
        globals()['past_b2_price_{}'.format(coin)] = globals()['past_b1_price_{}'.format(coin)] 
        globals()['past_b1_price_{}'.format(coin)] =globals()['past_b0_price_{}'.format(coin)] 
        globals()['past_b0_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)]
        print(coin, "past_b3_price:", globals()['past_b3_price_{}'.format(coin)])
        print(coin, "past_b2_price:", globals()['past_b2_price_{}'.format(coin)])
        print(coin, "past_b1_price:", globals()['past_b1_price_{}'.format(coin)])
        print(coin, "past_b0_price:", globals()['past_b0_price_{}'.format(coin)])

    print("past_price setting") 

for coin in coins:
    get_rsi("KRW-"+coin)
    globals()['sell_time_{}'.format(coin)] = datetime.datetime.now()
    # print(coin,rsi)
    time.sleep(0.2) # 속도가 느리면 다음 코인 값을 못 갖고와 에러남. 그래서 sleep
get_opening_loop()
# schedule.every(10).minutes.do(lambda: predict_price_loop())
schedule.every(1).minutes.do(lambda: get_rsi_loop())
schedule.every().day.at("09:00").do(lambda: get_opening_loop())

# schedule.every(60).minutes.do(lambda: get_bestK_loop())
# schedule.every().day.at("09:03").do(lambda: predict_price_loop())

# schedule.every(20).seconds.do(lambda: predict_price_loop())

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade2 start")
# ------sell_price 입력하는 곳---------------
# 프로그램이 돌아가는 중 종료했을 경우에만 입력하면 됨
# sell_price: 장중에 매도한 코인을 다시 사지 않기 위한 기준. 0보다 크면 상관없다.


# sell_price_LINK = 36980
# sell_price_ENJ = 36980
# ------------------------------------------------
time.sleep(3)

start_time = get_start_time("KRW-BTC")
# print("start_time",start_time)
# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=3)
        schedule.run_pending()
        if start_time + datetime.timedelta(seconds=10) < now < end_time:
            for coin in coins:
                 
                globals()['current_price_{}'.format(coin)]  = get_current_price("KRW-"+coin)
                coinjan = get_balance(coin)
                # print(coin, "coinjan:",coinjan)
                if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:                
                    globals()['buy_price_{}'.format(coin)] = get_buy_price(coin)
                else:
                    globals()['buy_price_{}'.format(coin)] = 0     

                print(coin,"curren:",round(globals()['current_price_{}'.format(coin)],3) ,"RSI:",round(globals()['rsi_{}'.format(coin)],2))
                if globals()['buy_price_{}'.format(coin)] > 0:
                    print("buy_price",coin, globals()['buy_price_{}'.format(coin)])
                if globals()['sell_price_{}'.format(coin)] > 0:
                    print("sell_price",coin, globals()['sell_price_{}'.format(coin)])     
                    time.sleep(0.5)
                    continue   

                krw = get_balance("KRW")
                limit = globals()['limit_{}'.format(coin)]
                coin_m = upbit.get_amount(coin)

                rsi_continue_chk = False


                """매수1조건: rsi가 65이상이고 시작가 보다 2프로이상 상승"""
                if (globals()['rsi_{}'.format(coin)] > 65 
                    and globals()['current_price_{}'.format(coin)] > globals()['opening_price_{}'.format(coin)] * 1.02 ):
                    trade_message = "buyby_1"                         
                    rsi_continue_chk = True  
                    if globals()['opening_price_{}'.format(coin)] == 0:
                        rsi_continue_chk = False 

                if now > start_time + datetime.timedelta(hours=1, minutes=30):
                    rsi_continue_chk = False

                if krw is None or krw < 5000:
                    rsi_continue_chk = False

                if limit is None:
                    rsi_continue_chk = False                      
                if coin_m is None:
                    coin_m = 0
                buyamt = limit - coin_m    
                if buyamt > 5000 and buyamt <= limit and rsi_continue_chk == True:
                    if buyamt > krw:
                        buyamt = krw
                    print("-------buy",coin, krw, "---------")
                    upbit.buy_market_order("KRW-" + coin, buyamt*0.9995) 
                    # globals()['buy_price_{}'.format(coin)] = globals()['current_price_{}'.format(coin)]
                    print("buy_price",coin, globals()['buy_price_{}'.format(coin)])
                    print(coin, trade_message)
                    continue

                """매도1조건"""           
                if globals()['sell_price_{}'.format(coin)]  == 0  and globals()['buy_price_{}'.format(coin)] > 0 and globals()['buy_price_{}'.format(coin)] * 0.97 > globals()['current_price_{}'.format(coin)] :
                    # coinjan = get_balance(coin)
                    if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:
                        # print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                        globals()['sell_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)] 
                        globals()['sell_time_{}'.format(coin)] =  datetime.datetime.now() 
                        print("-------sellby_1",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        print("_______buy_price2",coin, globals()['buy_price_{}'.format(coin)])

                sell_continue_chk = False



                """매도9조건 매수가 대비 3프로 이하이고 RSI 60 아래면 매도"""
                if (coinjan * globals()['current_price_{}'.format(coin)]  > 5000 and globals()['buy_price_{}'.format(coin)]*1.03 > globals()['current_price_{}'.format(coin)]
                    and globals()['rsi_{}'.format(coin)] <60):
                    sell_continue_chk = True
                    trade_message = "sellby_9"       

                if now < start_time + datetime.timedelta(hours=1):
                    sell_continue_chk = False

                """매도8조건 매수가 대비 10프로 상승하면 매도"""
                if coinjan * globals()['current_price_{}'.format(coin)]  > 5000 and globals()['buy_price_{}'.format(coin)]*1.1 < globals()['current_price_{}'.format(coin)]:  
                    trade_message = "sellby_8"                         
                    sell_continue_chk = True
                    
                """매도10조건 매수가 대비 3~5프로이고 RSI 70 아래면 매도"""
                if (coinjan * globals()['current_price_{}'.format(coin)]  > 5000 and globals()['buy_price_{}'.format(coin)]*1.03 < globals()['current_price_{}'.format(coin)]
                    < globals()['buy_price_{}'.format(coin)]*1.05 and globals()['rsi_{}'.format(coin)] <70):
                    sell_continue_chk = True
                    trade_message = "sellby_10"  

                """매도11조건 매수가 대비 5~10 프로이고 RSI 75 아래면 매도"""
                if (coinjan * globals()['current_price_{}'.format(coin)]  > 5000 and globals()['buy_price_{}'.format(coin)]*1.05 < globals()['current_price_{}'.format(coin)]
                    < globals()['buy_price_{}'.format(coin)]*1.1 and globals()['rsi_{}'.format(coin)] <75):
                    sell_continue_chk = True
                    trade_message = "sellby_11"  

                if globals()['rsi_{}'.format(coin)] == 0:
                    sell_continue_chk = False

                if sell_continue_chk == False:
                    time.sleep(0.5)
                    continue

                """매도"""           
                if sell_continue_chk == True:
                    if coinjan * globals()['current_price_{}'.format(coin)]  > 5000:
                        # print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        upbit.sell_market_order("KRW-" + coin, coinjan*0.9995)
                        globals()['sell_price_{}'.format(coin)] =  globals()['current_price_{}'.format(coin)] 
                        globals()['sell_time_{}'.format(coin)] =  datetime.datetime.now() 
                        print("-------sell2",coin, globals()['current_price_{}'.format(coin)] , "---------")
                        print("_______buy_price2",coin, globals()['buy_price_{}'.format(coin)])
                        print(coin,trade_message)

                coin_m = upbit.get_amount(coin)  
                if coin_m is None:
                    coin_m = 0                
                limit = globals()['limit_{}'.format(coin)]
                if coin_m > limit * 0.95:
                    time.sleep(1)         
                time.sleep(0.5)  
            print("------------------------------------------------------")
    except Exception as e:
        print(e)
        time.sleep(1)

# 백그라운드 실행: nohup python3 -u shortTrade1.py > output.log &
# 실행되고 있는지 확인: ps ax | grep .py
# 프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID     
# 코인종류 조회 : print(pyupbit.get_tickers())     
# 로그확인 : tail -f nohup.out