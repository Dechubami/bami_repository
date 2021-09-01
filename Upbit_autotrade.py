#!/usr/bin/env python
# coding: utf-8

# In[81]:


import time
import pyupbit
import datetime
import requests

access = "XX1QRq7SGojjymRfxfvxAbo5WP2T6gcuLdb7QMKz"
secret = "RC4Jx01wP7xUNu8uVkrWbxueObIbuvnkCtrqEfM1"
myToken = "xoxb-2433042185894-2425281849719-20MCXqVZKrqlNgC5lIakP2hM"

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

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#bitcoin", "autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        
        #밀크, 샌드박스, 비트코인캐쉬, 플라이댑, 이더리움
        target = ['KRW-MLK', 'KRW-SAND', 'KRW-BCHA', 'KRW-PLA', 'KRW-ETH']
        price = ['MLK','SAND','BCHA','PLA','ETH']
        target = dict(zip(target, price))
        
        for target_name in target:
            if start_time < now < end_time - datetime.timedelta(seconds=10):
                target_price = get_target_price(target_name, 0.3)
                ma15 = get_ma15(target_name)
                current_price = get_current_price(target_name)
                if target_price < current_price and ma15 < current_price:
                    krw = get_balance("KRW")
                    coin_price = get_balance(target[target_name])
                    print('1'+target_name, target_price, current_price, coin_price)
                    if krw > 5000 and 0 == coin_price:
                        buy_result = upbit.buy_market_order(target_name, krw*0.1995)
                        post_message(myToken,"#bitcoin", "Target buy : "target_name +str(buy_result))
            else:
                btc = get_balance(target[target_name])
                if btc > 0.00008:
                    sell_result = upbit.sell_market_order(target_name, btc*0.9995)
                    post_message(myToken,"#bitcoin", "Target buy : "target_name +str(sell_result))
            time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#bitcoin", e)
        time.sleep(1)


# In[82]:


jupyter nbconvert -to script Upbit_autotrade.ipynb

