import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
from scipy.fftpack import diff
import yfinance as yf
import datetime as dt 
from dateutil.relativedelta import relativedelta
import ta as ta
from BACKTESTER import BACKTEST
from datetime import datetime
import matplotlib.pyplot as plt 



def STRATEGY(data, symbol_extra):
    df          = symbol_extra
    signal_df   = []
    

    
    
    
    def STOCH_SIGNAL_STRATEGY(data, df):
        
        def get_stoch_osc(high, low, close, k_lookback, d_lookback):
            lowest_low = low.rolling(k_lookback).min()
            highest_high = high.rolling(k_lookback).max()

            k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
            d_line = k_line.rolling(d_lookback).mean()
            return k_line, d_line

        df['%k'], df['%d']  = get_stoch_osc(df['high'], df['low'], df['open'], 14, 3)


        def implement_stoch_strategy(prices, k, d):    
            buy_price = []
            sell_price = []
            stoch_signal = []
            signal = 0

            for i in range(len(prices)):
                if k[i] < 30 and d[i] < 30 and k[i] < d[i]:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        stoch_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_signal.append(0)
                elif k[i] > 75 and d[i] > 75 and k[i] > d[i]:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        stoch_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    stoch_signal.append(0)
                    
            return buy_price, sell_price, stoch_signal
                    
        buy_price, sell_price, stoch_signal = implement_stoch_strategy(df['open'], df['%k'], df['%d'])

        position = []
        for i in range(len(stoch_signal)):
            if stoch_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['open'])):
            if stoch_signal[i] == 1:
                position[i] = 1
            elif stoch_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
                
        k               = df['%k']
        d               = df['%d']
        close_price     = df['open']
        stoch_signal    = pd.DataFrame(stoch_signal).rename(columns = {0:'stoch_signal'}).set_index(df.index)
        position        = pd.DataFrame(position).rename(columns = {0:'signal'}).set_index(df.index)
        frames          = [close_price, k, d, stoch_signal, position]
        strategy        = pd.concat(frames, join = 'inner', axis = 1)
        df              = df.iloc[::-1] 
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))


        df['diff']  = list_value
        df          = df.iloc[::-1]

        connect = [df, position]
        df = pd.concat(connect, join = 'inner', axis = 1)

        del df['%k']
        del df['%d']
        
        return df

    for i in range(len(data)):
        df_1 = STOCH_SIGNAL_STRATEGY(data[i], symbol_extra[i])
        signal_df.append(df_1)
    
    return signal_df



    

