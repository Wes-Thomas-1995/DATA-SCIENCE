
from datetime import datetime, timedelta, date
from binance.client import Client
from binance.enums import *
import datetime, time
import pandas as pd
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

def TICKER_LIST(ticker):
    if ticker == 'SINGLE':
        data =input("Enter a CRYPTOCURRENCY symbol: ")
        value = [1]
        data_2 = ''
    else:
        data = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT', 'SOLUSDT', 'AVAXUSDT', 'LTCUSDT']
        data_2 = ['BTC', 'ETH', 'BNB', 'XRP', 'DOGE', 'ADA', 'SOL', 'AVAX', 'LTC']
        value = [100000,10000,1000,1,1,10,100,100,1000]

    return data, value, data_2


def RETRIEVE_DATA(data, howLong, inter, client):
    

    untilThisDate = datetime.datetime.now()
    sinceThisDate = untilThisDate - datetime.timedelta(days = howLong)


    symbol_extra        = []

    if isinstance(data, str) is True:
    
        if inter == '15M':
            candle = client.get_historical_klines(data, Client.KLINE_INTERVAL_15MINUTE, str(sinceThisDate), str(untilThisDate))
        elif inter == '1M':
            candle = client.get_historical_klines(data, Client.KLINE_INTERVAL_1MINUTE, str(sinceThisDate), str(untilThisDate))       
        elif inter == '30M':
            candle = client.get_historical_klines(data, Client.KLINE_INTERVAL_15MINUTE, str(sinceThisDate), str(untilThisDate))
        elif inter == '5M':
            candle = client.get_historical_klines(data, Client.KLINE_INTERVAL_5MINUTE, str(sinceThisDate), str(untilThisDate))
        elif inter == '1D':
            candle = client.get_historical_klines(data, Client.KLINE_INTERVAL_1DAY, str(sinceThisDate), str(untilThisDate))        

        df              = pd.DataFrame(candle, columns=['Date', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
        df.Date         = pd.to_datetime(df.Date, unit='ms')
        df.set_index('Date', inplace=True)

        df['open']     = df['open'].astype(float)
        df['high']     = df['high'].astype(float)
        df['low']      = df['low'].astype(float)
        df['close']    = df['close'].astype(float)
        symbol_extra    = df.drop(['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore', 'volume'], axis=1)
        symbol_extra.index = symbol_extra.index + pd.DateOffset(hours=1)

    else:
        
        if inter == '15M':
            d  = {data[x]: client.get_historical_klines(data[x], Client.KLINE_INTERVAL_15MINUTE, str(sinceThisDate), str(untilThisDate))  for x in range(len(data))}
        elif inter == '5M': 
            d  = {data[x]: client.get_historical_klines(data[x], Client.KLINE_INTERVAL_5MINUTE, str(sinceThisDate), str(untilThisDate))  for x in range(len(data))}
        elif inter == '1M': 
            d  = {data[x]: client.get_historical_klines(data[x], Client.KLINE_INTERVAL_1MINUTE, str(sinceThisDate), str(untilThisDate))  for x in range(len(data))}
        elif inter == '30M':
            d  = {data[x]: client.get_historical_klines(data[x], Client.KLINE_INTERVAL_30MINUTE, str(sinceThisDate), str(untilThisDate))  for x in range(len(data))}
        elif inter == '1D':
            d  = {data[x]: client.get_historical_klines(data[x], Client.KLINE_INTERVAL_1DAY, str(sinceThisDate), str(untilThisDate))  for x in range(len(data))}

        for e in range(len(data)):
            symbol_extra.append(data[e] + "_dataframe")

        for e in range(len(data)):
            symbol_extra[e] = None

        for w in range(len(data)):
            temp_df             = pd.DataFrame(d[data[w]], columns=['Date', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])
            temp_df.Date        = pd.to_datetime(temp_df.Date, unit='ms')
            temp_df.set_index('Date', inplace=True)
            temp_df             = temp_df.drop(['closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol','takerBuyQuoteVol', 'ignore', 'volume'], axis=1)
            
            temp_df['open']     = temp_df['open'].astype(float)
            temp_df['high']     = temp_df['high'].astype(float)
            temp_df['low']      = temp_df['low'].astype(float)
            temp_df['close']    = temp_df['close'].astype(float)
            
            
            symbol_extra[w] = temp_df
            symbol_extra[w].index = symbol_extra[w].index + pd.DateOffset(hours=1)            
            
            
            
            
            
    return data, symbol_extra



