import pandas as pd
from math import floor
import datetime as dt 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import yfinance as yf
from sqlalchemy import create_engine














def RELOAD_SAVE_DATA_SQL(ACTION_ITEMS):
    DATA_UPLOAD = ACTION_ITEMS

    if len(DATA_UPLOAD) > 0:

        DATA_UPLOAD = DATA_UPLOAD.rename({'TICKER_COMMANDS'     : 'ticker_commands',
                                          'PORTFOLIO_COMMANDS'  : 'portfolio_commands',
                                          'PRICE'               : 'price',
                                          'QUANTITY'            : 'quantity',
                                          'INDUSTRY'            : 'industry',
                                          'SECTOR'              : 'sector',
                                          'NAME'                : 'name',
                                          'DATE'                : 'date' 
                                          }, axis=1)

        engine = create_engine(
            'postgresql://XXXXX')
        DATA_UPLOAD.to_sql('test_portfolio_history', engine, if_exists='append',
                           index=False, chunksize=100000, method='multi')

        print(' ')
        happy = print('     - SQL TABLE ON POSITION HISTORY IS UPDATED          :   COMPLETED')
    else:
        print(' ')
        happy = print('     - NO NEED TO UPDATE THE SQL TABLE                   :   COMPLETED')

    return happy

  

def TEST_INDUSTRY(TRANSACTION_DF):

    TRANSACTION_OPT = pd.DataFrame(columns=['TICKER_COMMANDS', 'PORTFOLIO_COMMANDS', 'PRICE', 'QUANTITY', 'INDUSTRY', 'SECTOR', 'NAME'])

    DATE_TODAY = datetime.today().strftime('%Y-%m-%d')


    if len(TRANSACTION_DF) > 0:
        for i in range(len(TRANSACTION_DF)):
            ticker              = TRANSACTION_DF.at[i, 'TICKER_COMMANDS']
            PORTFOLIO_COM       = TRANSACTION_DF.at[i, 'PORTFOLIO_COMMANDS']
            PRICE               = TRANSACTION_DF.at[i, 'PRICE']
            QUANTITY            = TRANSACTION_DF.at[i, 'QUANTITY']
            
            stockInfo           = yf.Ticker(ticker).info
            industry            = stockInfo['industry']
            sector              = stockInfo['sector']
            name                = stockInfo['shortName']

            TRANSACTION_OPT = TRANSACTION_OPT.append({'TICKER_COMMANDS': ticker,
                                                      'PORTFOLIO_COMMANDS': PORTFOLIO_COM,
                                                      'PRICE': PRICE,
                                                      'QUANTITY': QUANTITY,
                                                      'INDUSTRY': industry,
                                                      'SECTOR': sector,
                                                      'NAME': name,
                                                      'DATE': DATE_TODAY}, ignore_index=True)


    return TRANSACTION_OPT



def OUTPUT_PROCESSES(TRANSACTION_DF, data):
    TRANSACTION_OPT                                                             = TEST_INDUSTRY(TRANSACTION_DF)    
    OUTPUT                                                                      = RELOAD_SAVE_DATA_SQL(TRANSACTION_OPT)
    return TRANSACTION_OPT









