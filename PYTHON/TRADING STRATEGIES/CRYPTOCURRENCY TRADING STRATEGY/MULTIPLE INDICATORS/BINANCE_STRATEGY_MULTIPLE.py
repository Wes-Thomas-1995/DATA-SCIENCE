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



def STRATEGY_MULTIPLE(data, symbol_extra, SIGNAL_CHOSEN):
    df = symbol_extra
    
    
    def looping(data, symbol_extra, SIGNAL_CHOSEN):
        signal_df = []
        
        for i in range(len(data)):
            if SIGNAL_CHOSEN == 'RSI':
                df = RSI_SIGNAL_STRATEGY(data[i], symbol_extra[i])
            elif SIGNAL_CHOSEN == 'STOCH':
                df = STOCH_SIGNAL_STRATEGY(data[i], symbol_extra[i])
            elif SIGNAL_CHOSEN == 'BB':
                df = BB_SIGNAL_STRATEGY(data[i], symbol_extra[i])    
            elif SIGNAL_CHOSEN == 'MACD':
                df = MACD_SIGNAL_STRATEGY(data[i], symbol_extra[i]) 
            elif SIGNAL_CHOSEN == 'ADX':
                df = ADX(data[i], symbol_extra[i])                                    
            elif SIGNAL_CHOSEN == 'MACD__STOCH':
                df = MACD__STOCH_STRATEGY_SIGNAL(data[i], symbol_extra[i]) 
            elif SIGNAL_CHOSEN == 'RSI_STOCH_MACD':
                df = RSI_STOCH_MACD(data[i], symbol_extra[i])               

            #for a in range(len(data)):
            #root = (r'/Users/westhomas/Desktop/CRYPTO/FILES')
            #signal_df[a].to_csv(root + '/' + data[a] + ' - output of strategy output.csv')
        
            signal_df.append(df)
        
        return signal_df
    
    
    def MACD_SIGNAL_STRATEGY(data, df):

        def get_macd(price, slow, fast, smooth):
            exp1 = price.ewm(span = fast, adjust = False).mean()
            exp2 = price.ewm(span = slow, adjust = False).mean()
            macd = pd.DataFrame(exp1 - exp2).rename(columns = {'open':'macd'})
            signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
            hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
            frames =  [macd, signal, hist]
            df = pd.concat(frames, join = 'inner', axis = 1)
            return df

        googl_macd = get_macd(df['open'], 26, 12, 9)
        googl_macd.tail()

        def implement_macd_strategy(prices, data):    
            buy_price = []
            sell_price = []
            macd_signal = []
            signal = 0

            for i in range(len(data)):
                if data['macd'][i] > data['signal'][i]:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        macd_signal.append(0)
                elif data['macd'][i] < data['signal'][i]:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        macd_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    macd_signal.append(0)
                    
            return buy_price, sell_price, macd_signal
                    
        buy_price, sell_price, macd_signal = implement_macd_strategy(df['open'], googl_macd)


        position = []
        for i in range(len(macd_signal)):
            if macd_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['open'])):
            if macd_signal[i]   == 1:
                position[i]     = 1
            elif macd_signal[i] == -1:
                position[i]     = 0
            else:
                position[i]     = position[i-1]
                
        macd            = googl_macd['macd']
        signal          = googl_macd['signal']
        close_price     = df['open']
        macd_signal     = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(df.index)
        position        = pd.DataFrame(position).rename(columns = {0:'macd_position'}).set_index(df.index)
        frames          = [close_price, macd, signal, macd_signal, position]
        strategy        = pd.concat(frames, join = 'inner', axis = 1)
        
        df              = df.iloc[::-1]
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))


        df['diff']  = list_value
        df          = df.iloc[::-1]
        df          = pd.concat([df, position], join ='inner', axis = 1)
        df = df.rename(columns={"macd_position":"signal"})
        
        return df



    def RSI_SIGNAL_STRATEGY(data, df):
        
        
        def get_rsi(close, lookback):
            ret = close.diff()
            up = []
            down = []
            for i in range(len(ret)):
                if ret[i] < 0:
                    up.append(0)
                    down.append(ret[i])
                else:
                    up.append(ret[i])
                    down.append(0)
            up_series = pd.Series(up)
            down_series = pd.Series(down).abs()
            up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
            down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
            rs = up_ewm/down_ewm
            rsi = 100 - (100 / (1 + rs))
            rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
            rsi_df = rsi_df.dropna()
            return rsi_df[3:]

        df['rsi_14'] = get_rsi(df['open'], 14)
        df = df.dropna()
        
        
        def implement_rsi_strategy(prices, rsi):    
            buy_price = []
            sell_price = []
            rsi_signal = []
            signal = 0

            for i in range(len(rsi)):
                if rsi[i-1] > 30 and rsi[i] < 30:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        rsi_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        rsi_signal.append(0)
                elif rsi[i-1] < 60 and rsi[i] > 60:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        rsi_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        rsi_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    rsi_signal.append(0)
                    
            return buy_price, sell_price, rsi_signal
                    

        buy_price, sell_price, rsi_signal = implement_rsi_strategy(df['open'], df['rsi_14'])
        
        position = []
        for i in range(len(rsi_signal)):
            if rsi_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['open'])):
            if rsi_signal[i] == 1:
                position[i] = 1
            elif rsi_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
                
        rsi             = df['rsi_14']
        close_price     = df['open']
        rsi_signal      = pd.DataFrame(rsi_signal).rename(columns = {0:'rsi_signal'}).set_index(df.index)
        position        = pd.DataFrame(position).rename(columns = {0:'rsi_position'}).set_index(df.index)
        df              = df.iloc[::-1]
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))


        df['diff']  = list_value
        df          = df.iloc[::-1]
        frames      = [df, position]
        df          = pd.concat(frames, join = 'inner', axis = 1)
        df          = df.rename(columns={"rsi_position":"signal"})
        del df['rsi_14'] 
        
        return df



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



    def BB_SIGNAL_STRATEGY(data, df):
        
        def sma(data, window):
            sma = data.rolling(window = window).mean()
            return sma

        df['sma_20'] = sma(df['open'], 20)
        df.tail()
        
        
        def bb(data, sma, window):
            std = data.rolling(window = window).std()
            upper_bb = sma + std * 2
            lower_bb = sma - std * 2
            return upper_bb, lower_bb

        df['upper_bb'], df['lower_bb'] = bb(df['open'], df['sma_20'], 20)
        df.tail()
        
        def implement_bb_strategy(data, lower_bb, upper_bb):
            buy_price = []
            sell_price = []
            bb_signal = []
            signal = 0
            
            for i in range(len(data)):
                if data[i-1] > lower_bb[i-1] and data[i] < lower_bb[i]:
                    if signal != 1:
                        buy_price.append(data[i])
                        sell_price.append(np.nan)
                        signal = 1
                        bb_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        bb_signal.append(0)
                elif data[i-1] < upper_bb[i-1] and data[i] > upper_bb[i]:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(data[i])
                        signal = -1
                        bb_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        bb_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    bb_signal.append(0)
                    
            return buy_price, sell_price, bb_signal

        buy_price, sell_price, bb_signal = implement_bb_strategy(df['open'], df['lower_bb'], df['upper_bb'])
        
        
        
        
        
        position = []
        for i in range(len(bb_signal)):
            if bb_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['open'])):
            if bb_signal[i] == 1:
                position[i] = 1
            elif bb_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
                
        upper_bb        = df['upper_bb']
        lower_bb        = df['lower_bb']
        close_price     = df['open']
        bb_signal       = pd.DataFrame(bb_signal).rename(columns = {0:'bb_signal'}).set_index(df.index)
        position        = pd.DataFrame(position).rename(columns = {0:'bb_position'}).set_index(df.index)
        df              = df.iloc[::-1]
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))

        df['diff']  = list_value
        df          = df.iloc[::-1]
        frames      = [df, position]
        df          = pd.concat(frames, join = 'inner', axis = 1)

        del df['sma_20']
        del df['upper_bb']
        del df['lower_bb']
        
        df = df.rename(columns={"bb_position":"signal"})

        
        
        
        
        return df



    def MACD__STOCH_STRATEGY_SIGNAL(data, df):
        
        
        
        
        def get_stoch_osc(high, low, close, k_lookback, d_lookback):
            lowest_low = low.rolling(k_lookback).min()
            highest_high = high.rolling(k_lookback).max()

            k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
            d_line = k_line.rolling(d_lookback).mean()
            return k_line, d_line


        def get_macd(price, slow, fast, smooth):
            exp1 = price.ewm(span=fast, adjust=False).mean()
            exp2 = price.ewm(span=slow, adjust=False).mean()
            macd = pd.DataFrame(exp1 - exp2).rename(columns={'open': 'macd'})
            signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(
                columns={'macd': 'signal'})
            hist = pd.DataFrame(macd['macd'] - signal['signal']
                                ).rename(columns={0: 'hist'})
            return macd, signal, hist



        def implement_stoch_macd_strategy(prices, k, d, macd, macd_signal):
            buy_price = []
            sell_price = []
            stoch_macd_signal = []
            signal = 0

            for i in range(len(prices)):
                if k[i] < 20 and d[i] < 20 and macd[i] < -2 and macd_signal[i] < -2:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        stoch_macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_macd_signal.append(0)

                elif k[i] > 80 and d[i] > 80 and macd[i] > 2 and macd_signal[i] > 2:
                    if signal != -1 and signal != 0:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        stoch_macd_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        stoch_macd_signal.append(0)

                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    stoch_macd_signal.append(0)

            return buy_price, sell_price, stoch_macd_signal



        def POSITION_LOGIC(stoch_macd_signal, df):
            position  = []
            
            if len(df) == 0:
                strategy = pd.DataFrame(columns=['open', '%k', '%d', 'macd', 'macd_signal', 'stoch_macd_signal', 'stoch_macd_position'])
                
                for u in range(0, 4):
                    strategy = strategy.append({'open': 0,
                                                '%k': 0,
                                                '%d': 0,
                                                'macd': 0,
                                                'macd_signal': 0,
                                                'stoch_macd_signal':0,
                                                'stoch_macd_position':0}, ignore_index=True)
                
            else:
            
                for x in range(len(stoch_macd_signal)):
                    if stoch_macd_signal[x] > 1:
                        position.append(0)
                    else:
                        position.append(1)
            
                for y in range(len(df['open'])):
                    if stoch_macd_signal[y] == 1:
                        position[y] = 1
                    elif stoch_macd_signal[y] == -1:
                        position[y] = 0
                    else:
                        position[y] = position[y-1]
            
                close_price = df['open']
                k_line = df['%k']
                d_line = df['%d']
                macd_line = df['macd']
                signal_line = df['macd_signal']
                stoch_macd_signal = pd.DataFrame(stoch_macd_signal).rename(
                    columns={0: 'stoch_macd_signal'}).set_index(df.index)
                position = pd.DataFrame(position).rename(
                    columns={0: 'stoch_macd_position'}).set_index(df.index)
                frames = [close_price, k_line, d_line, macd_line,
                        signal_line, stoch_macd_signal, position]
                
                strategy = pd.concat(frames, join='inner', axis=1)
            return strategy


        

        df['%k'], df['%d']                                                                = get_stoch_osc(df['high'], df['low'], df['open'], 14, 3)
        df['macd'], df['macd_signal'], df['macd_hist']                                    = get_macd(df['open'], 26, 12, 9)
        df                                                                                = df.dropna()
        buy_price, sell_price, stoch_macd_signal                                          = implement_stoch_macd_strategy(df['open'], df['%k'], df['%d'], df['macd'], df['macd_signal'])
        strategy                                                                          = POSITION_LOGIC(stoch_macd_signal, df)
        position_flag                                                                     = []

        
        strategy.reset_index(inplace=True)
        
        for i in range(len(strategy)):
            val = strategy.at[i, 'stoch_macd_position']
            position_flag.append(val)
        
        df                  = df.iloc[::-1]
        googl_ret           = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value          = [0]

        for o in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[o, 0]))

        df['diff']          = list_value
        df                  = df.iloc[::-1]
        del df['%k']
        del df['%d']
        del df['macd']
        del df['macd_signal']
        del df['macd_hist']
        
        df['signal'] = position_flag
        
        
        return df



    def ADX(data, df):
        def get_adx(high, low, close, lookback):
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            
            tr1 = pd.DataFrame(high - low)
            tr2 = pd.DataFrame(abs(high - close.shift(1)))
            tr3 = pd.DataFrame(abs(low - close.shift(1)))
            frames = [tr1, tr2, tr3]
            tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
            atr = tr.rolling(lookback).mean()
            
            plus_di = 100 * (plus_dm.ewm(alpha = 1/lookback).mean() / atr)
            minus_di = abs(100 * (minus_dm.ewm(alpha = 1/lookback).mean() / atr))
            dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
            adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
            adx_smooth = adx.ewm(alpha = 1/lookback).mean()
            return plus_di, minus_di, adx_smooth

        df['plus_di'] = pd.DataFrame(get_adx(df['high'], df['low'], df['open'], 14)[0]).rename(columns = {0:'plus_di'})
        df['minus_di'] = pd.DataFrame(get_adx(df['high'], df['low'], df['open'], 14)[1]).rename(columns = {0:'minus_di'})
        df['adx'] = pd.DataFrame(get_adx(df['high'], df['low'], df['open'], 14)[2]).rename(columns = {0:'adx'})
        df = df.dropna()
        df.tail()

        def implement_adx_strategy(prices, pdi, ndi, adx):
            buy_price = []
            sell_price = []
            adx_signal = []
            signal = 0
            
            for i in range(len(prices)):
                if adx[i-1] < 25 and adx[i] > 25 and pdi[i] > ndi[i]:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        adx_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        adx_signal.append(0)
                elif adx[i-1] < 25 and adx[i] > 25 and ndi[i] > pdi[i]:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        adx_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        adx_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    adx_signal.append(0)
                    
            return buy_price, sell_price, adx_signal

        buy_price, sell_price, adx_signal = implement_adx_strategy(df['open'], df['plus_di'], df['minus_di'], df['adx'])

        position = []
        for i in range(len(adx_signal)):
            if adx_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
                
        for i in range(len(df['open'])):
            if adx_signal[i] == 1:
                position[i] = 1
            elif adx_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
                
        close_price     = df['open']
        plus_di         = df['plus_di']
        minus_di        = df['minus_di']
        adx             = df['adx']
        adx_signal      = pd.DataFrame(adx_signal).rename(columns = {0:'adx_signal'}).set_index(df.index)
        position        = pd.DataFrame(position).rename(columns = {0:'adx_position'}).set_index(df.index)
        df              = df.iloc[::-1]
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))


        df['diff']      = list_value
        df              = df.iloc[::-1]
        frames          = [df, position]
        df              = pd.concat(frames, join = 'inner', axis = 1)
        df              = df.rename(columns={"adx_position":"signal"})
        
        del df['plus_di'] 
        del df['minus_di'] 
        del df['adx'] 



        return df

    
    
    
    def RSI_STOCH_MACD(data, df):
        df['%K'] = ta.momentum.stoch(df.high, df.low, df.close, window=14, smooth_window=3)     
        df['%D'] = df['%K'].rolling(3).mean()
        df['rsi'] = ta.momentum.rsi(df.close, window=14)
        df['macd']= ta.trend.macd_diff(df.close) 
        df.dropna(inplace=True)
        df2 = pd.DataFrame()
        for i in range(1,4): # this is 3 lags
            mask = (df['%K'].shift(i) < 25) & (df['%D'].shift(i) < 25)
            df2 = df2.append(mask, ignore_index=True)
    
    
        def gettriggers(df, lags, buy=True):
            df2 = pd.DataFrame()
            for i in range(1, lags+1):
                if buy:
                    mask= (df['%K'].shift(i) < 40) & (df['%D'].shift(i) < 40)
                else: 
                    mask= (df['%K'].shift(i) > 65) & (df['%D'].shift(i) > 65)
                df2 = df2.append(mask,ignore_index=True)
            return df2.sum(axis=0)
    
        df['Buytrigger'] = np.where(gettriggers(df, 4),1,0) # if we get a buy signal (sum is larger than 0) we get a 1, if 
        df['Selltrigger'] = np.where(gettriggers(df,4, False),1,0)
        df['Buy'] = np.where((df.Buytrigger) & (df["%K"].between(40,65)) & (df["%D"].between(40,65)) & (df.rsi>50) & (df.macd > 0),1,0)
        df['Sell'] = np.where((df.Selltrigger) & (df['%K'].between(40,65)) & (df['%D'].between(40,65)) & (df.rsi >50) & (df.macd > 0),1,0)
        
        Buying_dates, Selling_dates = [], []
        for i in range(len(df) - 1): 
            if df.Buy.iloc[i]: # checking if each row has a buy signal
                Buying_dates.append(df.iloc[i +1].name) # if condition is met, you buy at the next timepoint (next row)
                for num,j in enumerate(df.Sell[i:]): # checking from the buying date if the selling conditions are fulfilled.
                    if j: # j is the signal if its 1 or 0 
                        Selling_dates.append(df.iloc[i + num + 1].name) # i + num because num is the number of iterations.
                        break
        
        prev_cut = len(Buying_dates) - len(Selling_dates)
        
        if len(Buying_dates) - len(Selling_dates) == 1:
            Selling_dates.append(df.index[0])
        
        cutoff =len(Buying_dates) - len(Selling_dates)
        
        if cutoff:
            Buying_dates = Buying_dates[:-cutoff] # removing the buying dates if the selling conditions have not been fulfilled.
    
        frame = pd.DataFrame({'Buying_dates':Buying_dates, 'Selling_dates': Selling_dates})
        actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]
        
        overall = actuals
        overall = overall.reset_index()
        
        buy = []
        sell = []
        
        for w in range(len(overall)):
            val_1 = overall.at[w, 'Buying_dates']
            val_2 = overall.at[w, 'Selling_dates']

            buy.append(val_1)
            sell.append(val_2)
        
        signal = [] 
    
        for a in range(len(df)):
            numb = 0
    
            for b in range(len(buy)):
                if prev_cut == 1 and b == (len(buy)-1) and df.index[a] >= buy[b]:
                    numb = 1
                elif df.index[a] >= buy[b] and df.index[a] < sell[b]:
                    numb = 1

            signal.append(numb)
        
        df              = df.iloc[::-1] 
        googl_ret       = pd.DataFrame(np.diff(df['open'])).rename(columns = {0:'returns'})
        list_value      = [0]

        for i in range(len(googl_ret)):
            list_value.append(-1*(googl_ret.iat[i, 0]))


        df['diff']   = list_value
        df           = df.iloc[::-1]
        df['signal'] = signal
        
        del df['%K']
        del df['%D']
        del df['rsi']
        del df['macd']
        del df['Buytrigger']
        del df['Selltrigger']
        del df['Buy']
        del df['Sell']        
        
        
        return df
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



        

    if isinstance(data, str) is True:        
        if SIGNAL_CHOSEN == 'RSI':
            df = RSI_SIGNAL_STRATEGY(data, df)
        elif SIGNAL_CHOSEN == 'STOCH':
            df = STOCH_SIGNAL_STRATEGY(data, df)
        elif SIGNAL_CHOSEN == 'BB':
            df = BB_SIGNAL_STRATEGY(data, df)    
        elif SIGNAL_CHOSEN == 'MACD':
            df = MACD_SIGNAL_STRATEGY(data, df)  
        elif SIGNAL_CHOSEN == 'ADX':
            df = ADX(data, df)    
        elif SIGNAL_CHOSEN == 'MACD__STOCH':
            df = MACD__STOCH_STRATEGY_SIGNAL(data, df)  

        

    else:
        df  = looping(data, symbol_extra, SIGNAL_CHOSEN) 
    
    
    return df



    


def STRATEGY__COMPARISON(data, symbol_extra, SIGNAL_OPTIONS, investment_amount, STRATEGY_ANALYSIS, BACKTEST_CHOSEN):
    
    strategy_perf_df = pd.DataFrame(columns=['STRATEGY_CHOSEN', 'RETURN_TOTAL', 'RETURN_PER_TOTAL', 'MIN_TOTAL', 'MIN_PER_TOTAL', 'MAX_TOTAL', 'MAX_PER_TOTAL'])
    invest_amount = investment_amount
    
    if STRATEGY_ANALYSIS == 'YES':
    
        for i in range(len(SIGNAL_OPTIONS)):
            SIGNAL_CHOSEN                                               = SIGNAL_OPTIONS[i]
            signal_df                                                   = STRATEGY_MULTIPLE(data, symbol_extra, SIGNAL_CHOSEN)
            output, performance_df                                      = BACKTEST(data, signal_df, invest_amount, BACKTEST_CHOSEN, 'YES')

            #root = (r'/Users/westhomas/Desktop/CRYPTO/FILES')
            #performance_df.to_csv(root + '/' + str(SIGNAL_OPTIONS[i]) + ' - BACKTEST OUTPUT.csv')


            RETURN = performance_df["total_return"].mean()
            RETURN_TOTAL = RETURN - investment_amount
            RETURN_PER_TOTAL = (RETURN_TOTAL/investment_amount)*100

            MIN = performance_df["total_return"].min()
            MIN_TOTAL = MIN - investment_amount
            MIN_PER_TOTAL = (MIN_TOTAL/investment_amount)*100

            MAX = performance_df["total_return"].max()
            MAX_TOTAL = MAX - investment_amount
            MAX_PER_TOTAL = (MAX_TOTAL/investment_amount)*100  
        
            strategy_perf_df          = strategy_perf_df.append({'STRATEGY_CHOSEN'       : SIGNAL_CHOSEN,
                                                                'RETURN_TOTAL'           : RETURN_TOTAL,
                                                                'RETURN_PER_TOTAL'       : RETURN_PER_TOTAL,
                                                                'MIN_TOTAL'              : MIN_TOTAL,
                                                                'MIN_PER_TOTAL'          : MIN_PER_TOTAL,
                                                                'MAX_TOTAL'              : MAX_TOTAL,
                                                                'MAX_PER_TOTAL'          : MAX_PER_TOTAL}, ignore_index=True)
        
        print(strategy_perf_df)

    #root = (r'/Users/westhomas/Desktop/CRYPTO/FILES')
    CURRENT_DT = datetime.now()
    DT_STRING = CURRENT_DT.strftime("%Y-%m-%d %H:%M:%S")
    #strategy_perf_df.to_csv(root + '/STRATEGIC PERFORMANCE - ' + DT_STRING + '.csv')

    return strategy_perf_df




