import pandas as pd
from math import floor
import datetime as dt 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt




def BUY_AND_SELL(data, signal_df):

    TRANSACTION_DF = pd.DataFrame(columns=['TICKER_COMMANDS', 'PORTFOLIO_COMMANDS', 'QUANTITY'])

    for i in range(len(data)):
            overall = signal_df[i]
            if overall.iat[len(overall)-1, 5] == 1 and overall.iat[len(overall) - 2, 5] == 0:
                COMMAND = 'BUY'
            elif overall.iat[len(overall)-1, 5] == 0 and overall.iat[len(overall) - 2, 5] == 1:
                COMMAND = 'SELL'
            else:
                COMMAND = 'HOLD'    
            
            if COMMAND == 'BUY' or COMMAND == 'SELL':
                TRANSACTION_DF = TRANSACTION_DF.append({'TICKER_COMMANDS'        : data[i],
                                                        'PORTFOLIO_COMMANDS'     : COMMAND,
                                                        'QUANTITY'               : 0,
                                                        'PRICE'                  : overall.iat[len(overall)-1, 3]}, ignore_index=True)  

    return TRANSACTION_DF



