
from STRATEGY import STRATEGY, STRATEGY__COMPARISON
from DATA import TICKER_LIST, RETRIEVE_DATA
from RISK_MANAGER import RISK_MANAGEMENT
from OUTPUT import OUTPUT_PROCESSES
from BUY_SELL import BUY_AND_SELL
from BACKTESTER import BACKTEST
from EXECUTER import EXECUTION


from datetime import datetime, timedelta, date
from datetime import time as dtime
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")


BACKTEST_RUN                                                                = 'NO'
STRATEGY_ANALYSIS                                                           = 'NO'

invest_amount                                                               = 100
BACKTEST_OPTIONS                                                            = ['SNC', 'SC']
SIGNAL_OPTIONS                                                              = ['RSI', 'STOCH', 'BB', 'MACD', 'ADX', 'MACD__STOCH']
TICKER_RANGE                                                                = ['SINGLE', 'MULTIPLE'] 

BACKTEST_CHOSEN                                                             = BACKTEST_OPTIONS[0]
SIGNAL_CHOSEN                                                               = SIGNAL_OPTIONS[3]
RANGE_CHOSEN                                                                = TICKER_RANGE[1]


def FULL_SCRIPT_RUN_THROUGH(RANGE_CHOSEN, SIGNAL_CHOSEN, BACKTEST_CHOSEN, BACKTEST_RUN, STRATEGY_ANALYSIS, SIGNAL_OPTIONS):

    data                                                                        = TICKER_LIST(RANGE_CHOSEN)
    data, symbol_extra                                                          = RETRIEVE_DATA(data)

    signal_df                                                                   = STRATEGY(data, symbol_extra, SIGNAL_CHOSEN)
    output, performance_df                                                      = BACKTEST(data, signal_df, invest_amount, BACKTEST_CHOSEN, BACKTEST_RUN)
    strategy_perf_df                                                            = STRATEGY__COMPARISON(data, symbol_extra, SIGNAL_OPTIONS, invest_amount, STRATEGY_ANALYSIS, BACKTEST_CHOSEN)

    PORTFOLIO_COMMANDS, TICKER_COMMANDS, PRICE, QUANTITY, TRANSACTION_DF        = BUY_AND_SELL(data, signal_df, invest_amount)
    output                                                                      = RISK_MANAGEMENT(data)
    Positions_open, att_list, POD, TRANSACTION_DF, POSITION_HISTORY             = EXECUTION(TRANSACTION_DF, data)
    TRANSACTION_OPT                                                             = OUTPUT_PROCESSES(TRANSACTION_DF, data)



    print(' ')
    print(POSITION_HISTORY)  


    return


def FULL_LOOPING_PROCESS():
    ALLOW               = 0
    ALLOW_SA            = 0
    DATE_REFRESH        = ''    
    
    while ALLOW         == 0:  
        DATE_NOW        = date.today().strftime("%Y-%m-%d")
        TIME_NOW        = datetime.now().time()
        
        if DATE_REFRESH == DATE_NOW:
            pass
        else:
            if date.today().strftime("%A") == 'Saturday':
                time.sleep(36000) 
                            
            elif date.today().strftime("%A") == 'Sunday':
                time.sleep(36000)
                
            else:
                if datetime.now().time() >= dtime(10) and datetime.now().time() <= dtime(12):
                    FULL_SCRIPT_RUN_THROUGH(RANGE_CHOSEN, SIGNAL_CHOSEN, BACKTEST_CHOSEN, BACKTEST_RUN, STRATEGY_ANALYSIS, SIGNAL_OPTIONS)   
                    time.sleep(7200)
                    DATE_REFRESH = DATE_NOW

    return



FULL_LOOPING_PROCESS()
#FULL_SCRIPT_RUN_THROUGH(RANGE_CHOSEN, SIGNAL_CHOSEN, BACKTEST_CHOSEN, BACKTEST_RUN, STRATEGY_ANALYSIS, SIGNAL_OPTIONS)


