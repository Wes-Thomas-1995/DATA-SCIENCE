import pandas as pd
from math import floor
import datetime as dt 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
import yfinance as yf
from sqlalchemy import create_engine
import psycopg2
from datetime import datetime, timedelta, date





def RELOAD_LOAD_DATA_SQL(POD):


    engine              = create_engine('postgresql://XXXXX')
    POSITION_HISTORY    = pd.read_sql_table('test_portfolio_history', engine)
    yesterday           = pd.Timestamp(date.today() - timedelta(days=1))



    if len(POSITION_HISTORY) > 0:
        POSITION_HISTORY['ticker_commands'] = POSITION_HISTORY['ticker_commands'].replace( ' ', '', regex=True)
        if len(POD) > 0:
            for n in range(len(POSITION_HISTORY)):            
                if POSITION_HISTORY.at[n, 'updated'] == 'NO':
                    if POSITION_HISTORY.at[n, 'date'] < yesterday:

                        
                        TICKER              = POSITION_HISTORY.at[n, 'ticker_commands']
                        DATE                = POSITION_HISTORY.at[n, 'date']
                        PRICE               = str(POD[POD['Ticker'] == TICKER]['Purchase_Price'].values[0])
                        conn                = psycopg2.connect(host="localhost", port=5432, database="ENKI_STOCK_PORTFOLIO", user="postgres", password="Button0104")                    
                        conn.autocommit     = True
                        cursor              = conn.cursor()
                        
                        cursor.execute("""UPDATE test_portfolio_history SET PRICE = %s, UPDATED  = 'YES' WHERE ticker_commands = %s AND DATE = %s""", (PRICE, TICKER, DATE))
                        conn.commit()
                        conn.close()
                        
                    pass
                else:
                    pass

    engine              = create_engine('postgresql://XXXXX')
    POSITION_HISTORY    = pd.read_sql_table('test_portfolio_history', engine)

    if len(POSITION_HISTORY) > 0:
        POSITION_HISTORY['ticker_commands'] = POSITION_HISTORY['ticker_commands'].replace( ' ', '', regex=True)


    return POSITION_HISTORY









