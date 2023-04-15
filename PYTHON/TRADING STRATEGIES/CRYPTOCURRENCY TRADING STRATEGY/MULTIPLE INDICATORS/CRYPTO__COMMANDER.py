
from BINANCE_DATA_RETRIEVAL import PORTFOLIO_ANALYTICS_TRIAL, TRADE_HISTORY, TICK_SIZE, LIMIT_DATAFRAME
from BINANCE_STRATEGY_MULTIPLE import STRATEGY_MULTIPLE, STRATEGY__COMPARISON
from BINANCE_DATA import RETRIEVE_DATA, TICKER_LIST
from BINANCE_BUY_SELL import BUY_AND_SELL
from BINANCE_EXECUTOR import EXECUTION
from BINANCE_STRATEGY import STRATEGY
from BACKTESTER import BACKTEST

from datetime import datetime, timedelta, date
from binance.helpers import round_step_size
from datetime import time as dtime
from binance.client import Client
from binance.enums import *
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")




ROOT            = (r'/Users/westhomas/Desktop/CRYPTO TRADER')
temp            = open(ROOT + '/' + 'API_FILE.txt','r').read().splitlines()
DATA            = open(ROOT + '/' + 'TICKER_FILE.txt','r').read().splitlines()
API_SECRET_KEY  = temp[0]
API_KEY         = temp[1]



def BACKTESTING_STRATEGY(API_KEY, API_SECRET_KEY, data, howLong):
    client                                                                      = Client(API_KEY, API_SECRET_KEY)
    BACKTEST_RUN                                                                = 'YES'
    STRATEGY_ANALYSIS                                                           = 'NO'

    BACKTEST_OPTIONS                                                            = ['SNC', 'SC']
    SIGNAL_OPTIONS                                                              = ['RSI', 'STOCH', 'BB', 'MACD', 'ADX', 'MACD__STOCH', 'RSI_STOCH_MACD']
    TICKER_RANGE                                                                = ['SINGLE', 'MULTIPLE'] 

    BACKTEST_CHOSEN                                                             = BACKTEST_OPTIONS[1]
    SIGNAL_CHOSEN                                                               = SIGNAL_OPTIONS[1]
    RANGE_CHOSEN                                                                = TICKER_RANGE[0]

    data, symbol_extra                                                          = RETRIEVE_DATA(data, howLong, '5M', client) 
    signal_df                                                                   = STRATEGY_MULTIPLE(data, symbol_extra, SIGNAL_CHOSEN)  

    print('\n     - TECHNIAL STRATEGY    :  ' + str(SIGNAL_CHOSEN))
    print('     - NBR OF DAYS TESTED   :  ' + str(howLong))
    print(' ')
    
    output, performance_df                                                      = BACKTEST(data, signal_df, 100, BACKTEST_CHOSEN, BACKTEST_RUN)
    strategy_perf_df                                                            = STRATEGY__COMPARISON(data, symbol_extra, SIGNAL_OPTIONS, 100, STRATEGY_ANALYSIS, BACKTEST_CHOSEN)        

    return


def TRADING_STRATEGY(TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference, client, data):
    START_OVERALL                                                               = time.time()
    
    data, symbol_extra                                                          = RETRIEVE_DATA(data, 1, '5M', client) 
    signal_df                                                                   = STRATEGY(data, symbol_extra)  
    TRANSACTION_DF                                                              = BUY_AND_SELL(data, signal_df)
    TRANSACTION_DF_OPT, CURRENT_ASSETS_DF, TRADE_HISTORY_DF                     = EXECUTION(TRANSACTION_DF, data, step_size_list, history_reference, client, TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list)
    
    END_OVERALL                                                                 = time.time()
    TIME_TAKEN                                                                  = round((END_OVERALL-START_OVERALL)/60,2)

    time.sleep(15)
    return TRANSACTION_DF_OPT, TIME_TAKEN


def TRADE_INFORMATION_RETRIEVAL(client, data):

    TRADE_HISTORY_DF                                    = TRADE_HISTORY(data, client)
    tick_size_list, step_size_list, history_reference   = TICK_SIZE(data, client)
    CURRENT_ASSETS_DF                                   = PORTFOLIO_ANALYTICS_TRIAL(data, client, TRADE_HISTORY_DF, history_reference)
    
    return CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference


def PLACING_LIMIT_ORDER(data, df, client, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference, TIME_TAKEN):
    
    
    def LIMIT_ORDER(symbol_2, quantity, PRICE_LOW_LIMIT):

        try:
            order = client.create_order(
                symbol = symbol_2, 
                side = SIDE_SELL, 
                type = ORDER_TYPE_STOP_LOSS_LIMIT, 
                timeInForce = TIME_IN_FORCE_GTC, 
                quantity = quantity, 
                price = str(PRICE_LOW_LIMIT), 
                stopPrice = str(PRICE_LOW_LIMIT))  
            print('        - LIMIT ORDER PLACED -- ' + data[i])
        except:
            print('        - ERROR PLACING LIMIT ORDER -- ' + data[i])
        
        return

    
    LIMIT_PERCENT_STAT                                       = 0.985
    
    for i in range(len(data)):
        TRADE_HISTORY_DF                                       = df[df['symbol'] == data[i]]
        TRADE_HISTORY_DF                                       = TRADE_HISTORY_DF.reset_index()
        FLAG                                                   = TRADE_HISTORY_DF.at[len(TRADE_HISTORY_DF)-1, 'isBuyer']
        
        QTY_RECENT                                          = float(TRADE_HISTORY_DF.at[len(TRADE_HISTORY_DF)-1, 'qty'])
        PRICE_RECENT                                        = float(TRADE_HISTORY_DF.at[len(TRADE_HISTORY_DF)-1, 'price'])

        CURRENT_ASSETS_DF_SPEC                              = CURRENT_ASSETS_DF[CURRENT_ASSETS_DF['Ticker'] == history_reference[i]]
        CURRENT_ASSETS_DF_SPEC                              = CURRENT_ASSETS_DF_SPEC.reset_index()
        del CURRENT_ASSETS_DF_SPEC['index']

        tick_size               = tick_size_list[i]
        step_size               = step_size_list[i]

        if len(CURRENT_ASSETS_DF_SPEC) >0:
            QTY_OWNED               = float(CURRENT_ASSETS_DF_SPEC.at[0, 'Quantity'])
            QTY_OWNED               = round_step_size(QTY_OWNED, step_size)
            PRICE_LIMIT             = round_step_size((PRICE_RECENT*LIMIT_PERCENT_STAT), tick_size)
            
            if FLAG == True:
                orders              = client.get_open_orders(symbol=data[i])
                total               = len(orders)

                if total == 0:
                    LIMIT_ORDER(data[i], QTY_OWNED, PRICE_LIMIT)
                    

    print(' ')
    print('        - TIME TAKEN TO COMPLETE THIS PROCESS           : ' + str(TIME_TAKEN) + 'MINS')
    print(' ')

    return


def PRIMARY_SCRIPT(API_KEY, API_SECRET_KEY, data, TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference):
    
    client                                                                                  = Client(API_KEY, API_SECRET_KEY)
    TRANSACTION_DF_OPT, TIME_TAKEN                                                          = TRADING_STRATEGY(TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference, client, data)
    CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference  = TRADE_INFORMATION_RETRIEVAL(client, data)
    PLACING_LIMIT_ORDER(data, TRADE_HISTORY_DF, client, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference, TIME_TAKEN)


    



    return


def SECONDARY_SCRIPT(API_KEY, API_SECRET_KEY, data):
    
    client                                                                                  = Client(API_KEY, API_SECRET_KEY)    
    CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference  = TRADE_INFORMATION_RETRIEVAL(client, data)

    return CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference


def LOOPING_SCRIPT(API_KEY, API_SECRET_KEY, data):
    CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference      = SECONDARY_SCRIPT(API_KEY, API_SECRET_KEY, data)
    trade_time_list                                                                             = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
    info_time_list                                                                              = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58]

    print(' ')
    print(CURRENT_ASSETS_DF)
    print(' ')
    print(TRADE_HISTORY_DF)
    print(' ')
 
    ALLOW                                                   = 0
    while ALLOW                                             == 0:
        current_dt                                          = datetime.now()
        dt_string                                           = current_dt.strftime("%Y-%m-%d %H:%M:%S")      
        
        for t in range(len(trade_time_list)):
            if current_dt > (datetime.now().replace(minute=(trade_time_list[t]), second=1, microsecond=0)) and current_dt <= (datetime.now().replace(minute=(trade_time_list[t]), second=5, microsecond=0)):
                print('\nDATE NOW     :  ' + dt_string)
                PRIMARY_SCRIPT(API_KEY, API_SECRET_KEY, data, TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list, step_size_list, history_reference)
                time.sleep(3)
    
            elif current_dt > (datetime.now().replace(minute=(info_time_list[t]), second=1, microsecond=0)) and current_dt <= (datetime.now().replace(minute=(info_time_list[t]), second=5, microsecond=0)):
                CURRENT_ASSETS_DF, TRADE_HISTORY_DF, tick_size_list, step_size_list, history_reference      = SECONDARY_SCRIPT(API_KEY, API_SECRET_KEY, data)
                time.sleep(3)

        time.sleep(3)

    return



LOOPING_SCRIPT(API_KEY, API_SECRET_KEY, DATA)

#BACKTESTING_STRATEGY(API_KEY, API_SECRET_KEY, DATA, 30)
