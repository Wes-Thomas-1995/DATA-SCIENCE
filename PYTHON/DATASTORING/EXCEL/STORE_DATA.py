from datetime import datetime, timedelta, date
from binance.client import Client
from binance.enums import *
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")








class SAVING_SCRIPT():

    def __init__(self, ROOT, client):
        self.client           = client
        self.ROOT             = ROOT

        self.SAVING_SCRIPT()


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


        DAILY_DF.to_csv(self.ROOT + '/GRANULAR PERFORMANCE/' + YEAR_STRING  + '-' + MONTH_STRING + '/DAILY PROFITS/' + 'DAILY PROFITS - ' + dt_string + '.csv',index=False)
        TRADE_DF.to_csv(self.ROOT + '/GRANULAR PERFORMANCE/' + YEAR_STRING  + '-' + MONTH_STRING + '/DAILY TRADES/'  + 'DAILY TRADES - ' + dt_string + '.csv',index=False)
        
        print('\n\n---- TODAYS DATE            ---- ' + dt_string)
        print('\n---- DAILY FUTURES BALANCE  ---- CSV EXPORT IS COMPLETED')
        print('---- DAILY TRADE DATAFRAME  ---- CSV EXPORT IS COMPLETED')


        return  




class APPEND_TO_AGGREGATE():

    def __init__(self, ROOT, client):
        self.client           = client
        self.ROOT             = ROOT

        self.APPEND_TO_AGGREGATE()


    def APPEND_TO_AGGREGATE(self):
        
        dt_string           = datetime.now().strftime("%Y-%m-%d") 
        YEAR_STRING         = datetime.now().strftime("%Y") 
        MONTH_STRING        = datetime.now().strftime("%m")

        DF_DAILY_PROFIT     = pd.read_csv(self.ROOT + '/GRANULAR PERFORMANCE/' + YEAR_STRING  + '-' + MONTH_STRING + '/DAILY PROFITS/' + 'DAILY PROFITS - ' + dt_string + '.csv')
        DF_DAILY_TRADES     = pd.read_csv(self.ROOT + '/GRANULAR PERFORMANCE/' + YEAR_STRING  + '-' + MONTH_STRING + '/DAILY TRADES/'  + 'DAILY TRADES - ' + dt_string + '.csv')    
        DF_AGG_PROFIT       = pd.read_csv(self.ROOT + '/AGGREGATE PERFORMANCE/AGGREGATE_PROFITS.csv')
        DF_AGG_TRADES       = pd.read_csv(self.ROOT + '/AGGREGATE PERFORMANCE/AGGREGATE_TRADES.csv')
        DF_AGG_PROFIT       = DF_AGG_PROFIT.append({'TRADE_DATE' : DF_DAILY_PROFIT.at[0, 'TRADE_DATE'],  'USDT_VALUE' : DF_DAILY_PROFIT.at[0, 'USDT_VALUE']}, ignore_index=True)

        if len(DF_DAILY_TRADES) > 0:
            for i in range(len(DF_DAILY_TRADES)):
                DF_AGG_TRADES   = DF_AGG_TRADES.append({'ORDERID'            :DF_DAILY_TRADES.at[i, 'ORDERID'],
                                                        'TRADE_DATE'         :DF_DAILY_TRADES.at[i, 'TRADE_DATE'], 
                                                        'SYMBOL'             :DF_DAILY_TRADES.at[i, 'SYMBOL'],
                                                        'SIDE'               :DF_DAILY_TRADES.at[i, 'SIDE'], 
                                                        'PRICE'              :DF_DAILY_TRADES.at[i, 'PRICE'], 
                                                        'QTY'                :DF_DAILY_TRADES.at[i, 'QTY'],
                                                        'USDT_VALUE'         :DF_DAILY_TRADES.at[i, 'USDT_VALUE'],
                                                        'COMMISSION'         :DF_DAILY_TRADES.at[i, 'COMMISSION'],
                                                        'COMMISSION ASSET'   :DF_DAILY_TRADES.at[i, 'COMMISSION ASSET']
                                                        
                                                        }, ignore_index=True)


        VAL           = int(len(DF_AGG_TRADES)/2)
        APP_LS        = []
        APP_TRADE_NBR = []

        for i in range(VAL):
            if i == 0:
            
                if DF_AGG_TRADES.at[i, 'SIDE'] == 'BUY':
                    LS_LIST = 'LONG'
                    TRADE_NBR = i+1
                elif DF_AGG_TRADES.at[i, 'SIDE'] == 'SELL':
                    LS_LIST = 'SHORT'
                    TRADE_NBR = i+1
                else:
                    pass
            
            else:
                
                if DF_AGG_TRADES.at[(i*2), 'SIDE'] == 'BUY':
                    LS_LIST = 'LONG'
                    TRADE_NBR = i+1
                elif DF_AGG_TRADES.at[(i*2), 'SIDE'] == 'SELL':
                    LS_LIST = 'SHORT'
                    TRADE_NBR = i+1
                else:
                    pass
            
            APP_LS.append(LS_LIST)
            APP_LS.append(LS_LIST)
            APP_TRADE_NBR.append(TRADE_NBR)
            APP_TRADE_NBR.append(TRADE_NBR)

        DF_AGG_TRADES['LONG/SHORT'] = APP_LS
        DF_AGG_TRADES['TRADE_NBR']  =  APP_TRADE_NBR
        DF_AGG_PROFIT.to_csv(self.ROOT + '/AGGREGATE PERFORMANCE/AGGREGATE_PROFITS.csv',index=False)
        DF_AGG_TRADES.to_csv(self.ROOT + '/AGGREGATE PERFORMANCE/AGGREGATE_TRADES.csv',index=False)
        
        print('\n---- AGG FUTURES BALANCE    ---- CSV EXPORT IS COMPLETED')
        print('---- AGG TRADE DATAFRAME    ---- CSV EXPORT IS COMPLETED\n\n')
        
        return





