from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from pandas_datareader import data as pdr
from scipy.fftpack import diff
from math import floor, ceil
import yfinance as yf
import datetime as dt 
import pandas as pd
import numpy as np
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 




def TICKER_LIST(ticker):
    if ticker == 'SINGLE':
        data =input("Enter a stock ticker symbol: ")
    else:
        df_500      = (pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'))[0]
        data        = []

        for i in range(len(df_500)):
            tick = df_500.iloc[i,0]
            data.append(tick)
    

    return data


def RETRIEVE_DATA(symbol):
    symbol_dataframes   = []
    symbol_extra        = []
    tick_missing        = []
    tick_df_missing     = []
    missing             = []

    if isinstance(symbol, str) is True:
        symbol_extra = yf.Ticker(symbol).history(period="1y")
        symbol_extra = symbol_extra.rename({'Date':'date',
                                        'Open':'open', 
                                        'High':'high',
                                        'Low':'low', 
                                        'Close':'close',
                                        'Volume':'volume'
                                        }, axis=1)
        symbol_extra = symbol_extra.sort_index().astype(float)
        del symbol_extra['volume']
        del symbol_extra['Dividends']
        del symbol_extra['Stock Splits']
        
    else:

        for e in range(len(symbol)):
            symbol_dataframes.append(symbol[e] + "_dataframe")
            symbol_extra.append(symbol[e] + "_dataframe")

        for e in range(len(symbol)):
            symbol_extra[e] = None

        d           = {symbol[x]: yf.Ticker(symbol[x]).history(period="1y") for x in range(len(symbol))}
        missing     = list(yf.shared._ERRORS.keys())
            
        if len(missing)>0:
            for j in range(len(missing)):
                df_name = str(missing[j]) + "_dataframe"
                tick_df_missing.append(df_name)
                tick_missing.append(missing[j]) 
        
        for w in range(len(symbol)):
            if symbol[w] not in missing:
                symbol_extra[w] = pd.DataFrame(d[symbol[w]]) 
                del symbol_extra[w]['Dividends']
                del symbol_extra[w]['Stock Splits']  
            else:
                symbol_extra[w] = None
        
        for j in reversed(range(len(symbol))):
            if symbol[j] in tick_missing:
                del symbol_extra[j]

        symbol  = [ele for ele in symbol if ele not in missing]
    
        for k in range(len(symbol)):
                symbol_extra[k] = symbol_extra[k].rename({'Date':'date',
                                        'Open':'open', 
                                        'High':'high',
                                        'Low':'low', 
                                        'Close':'close',
                                        'Volume':'volume'
                                        }, axis=1)
                symbol_extra[k] = symbol_extra[k].sort_index().astype(float)
                del symbol_extra[k]['volume']
            
    return symbol, symbol_extra





