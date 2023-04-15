
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from binance.client import Client
from binance.enums import *
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")







class RELOAD_SAVE_DATA_SQL():

    def __init__(self, TRADE_DF, DAILY_DF):
        self.TRADE_DF           = TRADE_DF
        self.DAILY_DF           = DAILY_DF

        self.RELOAD_SAVE_DATA_SQL()


    def RELOAD_SAVE_DATA_SQL(self):
        DATA_UPLOAD_TRADES  = self.TRADE_DF
        DATA_UPLOAD_BALANCE = self.DAILY_DF

        if len(DATA_UPLOAD_TRADES) > 0:

            engine = create_engine( 'postgresql://XXXXX')
            DATA_UPLOAD_TRADES.to_sql('ucts_trade_history_portfolio', engine, if_exists='append', index=False, chunksize=100000, method='multi')


        engine = create_engine( 'postgresql://XXXXX')
        DATA_UPLOAD_BALANCE.to_sql('ucts_portfolio_balance_history', engine, if_exists='append', index=False, chunksize=100000, method='multi')


        return 













class SAVING_SCRIPT():

    def __init__(self, client):
        self.client           = client

        self.TRADE_DF, self.DAILY_DF = self.SAVING_SCRIPT()


    def SAVING_SCRIPT(self):
        
        dt_string       = datetime.now().strftime("%Y-%m-%d")
        YEAR_STRING     = datetime.now().strftime("%Y") 
        MONTH_STRING    = datetime.now().strftime("%m")
        acc_balance     = self.client.futures_account_balance()

        for check_balance in acc_balance:
            if check_balance["asset"] == "USDT":
                usdt_balance = round(float(check_balance["balance"]),2)

        DAILY_DF    = pd.DataFrame(columns=['TRADE_DATE', 'USDT_VALUE'])
        DAILY_DF    = DAILY_DF.append({'TRADE_DATE'     : dt_string,   'USDT_VALUE'     : usdt_balance}, ignore_index=True)



        def FINISH_TRADE_VIEWS(df, dt_string):
            df          = pd.DataFrame(df)
            df['DATE']  = pd.to_datetime(df['time'], unit='ms')
            df['DATE']  = df['DATE'] + pd.DateOffset(hours=1)
            df['DATE']  = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d %H:%M:00')
            df          = df.sort_values(by='DATE')
            df          = df.reset_index()
            df          = df[(df['DATE'] >= dt_string)]
            df          = df.reset_index()
            del df['index']

            df['price']      = round(pd.to_numeric(df['price']),2)
            df['qty']        = round(pd.to_numeric(df['qty']),2)
            df['quoteQty']   = round(pd.to_numeric(df['quoteQty']),2)
            df['commission']   = round(pd.to_numeric(df['commission']),2)

            df1      = pd.pivot_table(df, index=['orderId' ,'DATE', 'symbol', 'side', 'commissionAsset'], aggfunc= {'price': 'mean', 'qty': 'sum', 'quoteQty': 'sum', 'commission':'sum'})
            df1      = df1.sort_values(by='DATE', ascending=True)
            df1      = df1.reset_index()
            
            df1      = df1.rename({'orderId'             :'ORDERID',
                                    'DATE'               :'TRADE_DATE', 
                                    'symbol'             :'SYMBOL',
                                    'side'               :'SIDE', 
                                    'price'              :'PRICE', 
                                    'qty'                :'QTY',
                                    'quoteQty'           :'USDT_VALUE',
                                    'commissionAsset'    :'COMMISSION ASSET',
                                    'commission'         :'COMMISSION'
                                                        }, axis=1)
            
            
            return df1

        df              = self.client.futures_account_trades()
        TRADE_DF        = FINISH_TRADE_VIEWS(df, dt_string)

        return  TRADE_DF, DAILY_DF







def FULL_RUN():

    api_key                 = 'XXXXX'
    api_secret              = 'XXXXX'
    client                  = Client(api_key, api_secret)

    DATA = SAVING_SCRIPT(client)
    RELOAD_SAVE_DATA_SQL(DATA.TRADE_DF, DATA.DAILY_DF)

    print(DATA.TRADE_DF)
    print(DATA.DAILY_DF)





if __name__ == '__main__':

    FULL_RUN()







