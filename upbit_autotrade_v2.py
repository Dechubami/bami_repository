#!/usr/bin/env python
# coding: utf-8

# In[80]:


import time
import pyupbit
import datetime
import requests

access = "XX1QRq7SGojjymRfxfvxAbo5WP2T6gcuLdb7QMKz"
secret = "RC4Jx01wP7xUNu8uVkrWbxueObIbuvnkCtrqEfM1"
myToken = "xoxb-2433042185894-2425281849719-68K5htN5JjC1ChmlINGNCvPw"

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
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

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

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

def get_balance_avg(ticker):
    """평균가 조회"""
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

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("자동매매 시작합니다.")
# 시작 메세지 슬랙 전송
post_message(myToken,"#bitcoin", "자동매매 시작합니다.")

target = pyupbit.get_tickers()   

#KRW 코인만 가져오기
target_name_krw = []
for i in target:
     if i [:3] == 'KRW':
              target_name_krw.append(i);
                     
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
       
        #5개 코인 한정 로직 수행 - 밀크, 샌드박스, 비트코인캐쉬, 플라이댑, 이더리움
        #target = ['KRW-MLK', 'KRW-SAND', 'KRW-BCHA', 'KRW-PLA', 'KRW-ETH']
        #price = ['MLK','SAND','BCHA','PLA','ETH']
        #target = dict(zip(target, price))
        
        #KRW 코인에서 돌파전략사용하여 코인 구매
        for target_name in target_name_krw:
            #코인 이름 표기
            #print (target_name, target_name[:3], target_name[4:])
            if start_time < now < end_time - datetime.timedelta(seconds=10):
                #목표 코인 가격
                target_price = get_target_price(target_name, 0.3)
                ma15 = get_ma15(target_name)
                #현재 코인 가격
                current_price = get_current_price(target_name)
                #현재 보유한 코인 가격(blance)
                coin_price = get_balance(target_name[4:])
                #구매한 코인에 평균 가격(avg)
                coin_price_avg = get_balance_avg(target_name[4:])
                if target_price < current_price and ma15 < current_price and coin_price_avg < 1:
                    krw = get_balance("KRW")
                    #print("매수하였습니다. 코인 이름: "+str(target_name)+" 현재 가격: "+str(current_price)+" 구매 가격: "+str(coin_price_avg)+" 목표 가격: "+str(target_price))
                    if krw > 30000 :
                        buy_result = upbit.buy_market_order(target_name, krw*0.2000)
                        post_message(myToken,"#bitcoin", "매수하였습니다. 코인 이름: "+str(target_name)+" 현재 가격: "+str(current_price)+" 구매 가격: "+str(coin_price_avg)+" 목표 가격: "+str(target_price))
                        post_message(myToken,"#bitcoin", str(buy_result))
                        #print("매수하였습니다. 코인 이름: "+str(target_name)+" 현재 가격: "+str(current_price)+" 구매 가격: "+str(coin_price_avg)+" 목표 가격: "+str(target_price))
                elif coin_price_avg > 0 and current_price > coin_price_avg+coin_price_avg*0.05 :
                    sell_result = upbit.sell_market_order(target_name, btc)
                    post_message(myToken,"#bitcoin", "5% 상승으로 매도하였습니다. 코인 이름: "+str(target_name)+" 구매 가격: "+str(coin_price_avg)+" 판매 가격: "+str(current_price))
                    #print("5% 상승으로 매도하였습니다. 현재 코인값:"+str(current_price)+"구매 코인값:"+str(coin_price)+"구매 코인값:"+str(krw)+"코인 이름: "+str(target_name)+" 판매 가격: "+str(current_price))
                elif coin_price_avg > 0 and current_price < coin_price_avg-coin_price_avg*0.02 :
                    sell_result = upbit.sell_market_order(target_name, btc)
                    post_message(myToken,"#bitcoin", "2% 하락으로 매도하였습니다. 코인 이름: "+str(target_name)+" 구매 가격: "+str(coin_price_avg)+" 판매 가격: "+str(current_price))
                    #print("2% 하락으로 매도하였습니다. 코인 이름: "+str(target_name)+" 구매 가격: "+str(coin_price_avg)+" 판매 가격: "+str(current_price))
            else:
                btc = get_balance(target_name[4:])
                if btc > 0:
                    sell_result = upbit.sell_market_order(target_name, btc)
                    post_message(myToken,"#bitcoin", "장이 종료되어 일괄 매도하였습니다. 코인 이름: "+str(target_name)+" 구매 가격: "+str(coin_price_avg)+" 판매 가격: "+str(current_price))
            time.sleep(1) 
    except Exception as e:
        print(e)
        post_message(myToken,"#bitcoin", e)
        time.sleep(1)

