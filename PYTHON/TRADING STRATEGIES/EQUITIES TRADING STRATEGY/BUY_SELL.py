import pandas as pd
from math import floor
import datetime as dt 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt




def BUY_AND_SELL(data, signal_df, invest_amount):

    PORTFOLIO_COMMANDS = []
    TICKER_COMMANDS = []
    PRICE = []
    QUANTITY = []

    if isinstance(data, str) is False:
        for i in range(len(data)):
            overall = signal_df[i]
            if overall.iat[len(overall)-1, 5] == 1 and overall.iat[len(overall) - 2, 5] == 0:
                COMMAND = 'BUY'
            elif overall.iat[len(overall)-1, 5] == 0 and overall.iat[len(overall) - 2, 5] == 1:
                COMMAND = 'SELL'
            else:
                COMMAND = 'HOLD'    
            
            if COMMAND == 'BUY' or COMMAND == 'SELL':
                PORTFOLIO_COMMANDS.append(COMMAND)
                TICKER_COMMANDS.append(data[i])   
                PRICE.append(overall.iat[len(overall)-1, 3])
                QUANTITY.append(round(invest_amount/overall.iat[len(overall)-1, 3], 2))
            
    else:
        overall = signal_df
        if overall.iat[len(overall)-1, 5] == 1 and overall.iat[len(overall) - 2, 5] == 0:
            COMMAND = 'BUY'
        elif overall.iat[len(overall)-1, 5] == 0 and overall.iat[len(overall) - 2, 5] == 1:
            COMMAND = 'SELL'
        else:
            COMMAND = 'HOLD'    
            
        if COMMAND == 'BUY' or COMMAND == 'SELL':
            PORTFOLIO_COMMANDS.append(COMMAND)
            TICKER_COMMANDS.append(data) 
            PRICE.append(overall.iat[len(overall)-1, 3])
            QUANTITY.append(round(invest_amount/overall.iat[len(overall)-1, 3], 2))
    
    TRANSACTION_DF = pd.DataFrame(columns=['TICKER_COMMANDS', 'PORTFOLIO_COMMANDS', 'PRICE', 'QUANTITY'])
    
    TRANSACTION_DF['TICKER_COMMANDS']       = TICKER_COMMANDS
    TRANSACTION_DF['PORTFOLIO_COMMANDS']    = PORTFOLIO_COMMANDS
    TRANSACTION_DF['PRICE']                 = PRICE
    TRANSACTION_DF['QUANTITY']              = QUANTITY    

    return PORTFOLIO_COMMANDS, TICKER_COMMANDS, PRICE, QUANTITY, TRANSACTION_DF



