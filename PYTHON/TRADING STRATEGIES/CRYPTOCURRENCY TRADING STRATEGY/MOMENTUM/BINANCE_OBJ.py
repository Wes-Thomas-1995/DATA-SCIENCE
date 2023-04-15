from ta import add_all_ta_features
from ta.utils import dropna


from datetime import datetime
from datetime import time
import pandas as pd
import warnings
import os.path
import os

warnings.filterwarnings("ignore")




class OPEN_POSITIONS():

    def __init__(self, client, COIN):
        self.client                                                     = client
        self.COIN                                                       = COIN
        self.POS_DF, self.ENTRY_PRICE, self.DIRECTION_EXIST, self.QTY,  = self.OPEN_POSITIONS()


    def OPEN_POSITIONS(self):

        QTY, DIRECTION_EXIST, ENTRY_PRICE     = 0, 'NA', 0
        POS_DF                                = pd.DataFrame(self.client.futures_account()['positions'])
        POS_DF                                = POS_DF[POS_DF['symbol'] == self.COIN]
        POS_DF['entryPrice']                  = POS_DF['entryPrice'].astype(float)
        POS_DF                                = POS_DF[POS_DF['entryPrice'] > 0]
        
        if len(POS_DF) > 0:
            POS_DF               = POS_DF[POS_DF['symbol'] == self.COIN].reset_index()
            ENTRY_PRICE          = POS_DF.at[0, 'entryPrice']
            DIRECTION_EXIST      = float(POS_DF.at[0, 'positionAmt'])
            QTY                  = abs(float(POS_DF.at[0, 'positionAmt']))

            if DIRECTION_EXIST < 0:
                DIRECTION_EXIST = 'SELL'
            else:
                DIRECTION_EXIST = 'BUY'
        
        return POS_DF, ENTRY_PRICE, DIRECTION_EXIST, QTY


 

class CLOSE_POSITION():

    def __init__(self, client, TICKER, QTY, DIRECTION_EXIST):
        self.client             = client
        self.TICKER             = TICKER
        self.QTY                = QTY
        self.DIRECTION_EXIST    = DIRECTION_EXIST
        self.CLOSE_POSITION()


    def CLOSE_POSITION(self):
        
        if self.DIRECTION_EXIST == 'SELL':
            DIRECTION = 'BUY'
        else:
            DIRECTION = 'SELL'
            
        self.client.futures_create_order(symbol=self.TICKER, side=DIRECTION, type='MARKET', quantity=self.QTY)
        
        return




class CREATE_ORDER():

    def __init__(self, client, TICKER, QTY, DIRECTION, LEVERAGE):
        self.client             = client
        self.TICKER             = TICKER
        self.QTY                = QTY
        self.DIRECTION          = DIRECTION
        self.LEVERAGE           = LEVERAGE
        self.CREATE_ORDER()


    def CREATE_ORDER(self):
        
        if self.DIRECTION == 'SHORT':
            SIDE      = 'SELL'
        else:
            SIDE      = 'BUY'

        self.client.futures_change_leverage(symbol=self.TICKER, leverage=self.LEVERAGE)
        self.client.futures_create_order(symbol=self.TICKER, side=SIDE, type='MARKET', quantity=self.QTY)
        
        return




class CREATE_TP_AND_SL():

    def __init__(self, client, TICKER, ENTRY_PRICE, DIRECTION, TAKE_PROFIT, STOP_LOSS, tick_size, TAKE_PROFIT_INC_LT, STOP_LOSS_INC_LT):
        self.client               = client
        self.TICKER               = TICKER
        self.ENTRY_PRICE          = ENTRY_PRICE
        self.DIRECTION            = DIRECTION
        self.TAKE_PROFIT          = TAKE_PROFIT
        self.STOP_LOSS            = STOP_LOSS
        self.tick_size            = tick_size
        self.TAKE_PROFIT_INC_LT   = TAKE_PROFIT_INC_LT
        self.STOP_LOSS_INC_LT     = STOP_LOSS_INC_LT

        self.CREATE_TP_AND_SL()


    def CREATE_TP_AND_SL(self):

        if self.DIRECTION == 'BUY':
            SIDE                = 'SELL'
            TAKE_PROFIT_PRICE   = self.ENTRY_PRICE * (1 + (self.TAKE_PROFIT/100))
            STOP_LIMIT_PRICE    = self.ENTRY_PRICE * (1 - (self.STOP_LOSS/100))   

        else:
            SIDE = 'BUY'
            TAKE_PROFIT_PRICE   = self.ENTRY_PRICE * (1 - (self.TAKE_PROFIT/100))
            STOP_LIMIT_PRICE    = self.ENTRY_PRICE * (1 + (self.STOP_LOSS/100))        

        TAKE_PROFIT_PRICE = "{:0.0{}f}".format((TAKE_PROFIT_PRICE), self.tick_size)
        STOP_LIMIT_PRICE = "{:0.0{}f}".format((STOP_LIMIT_PRICE), self.tick_size)

        print('TAKE PROFIT PRICE : ' + TAKE_PROFIT_PRICE)
        print('STOP LOSS PRICE   : ' + STOP_LIMIT_PRICE)

        if  self.STOP_LOSS_INC_LT== 'YES':
            try:
                try:
                    self.client.futures_create_order(symbol=self.TICKER, side=SIDE, type='STOP_MARKET', timeInForce= 'GTE_GTC', stopPrice=STOP_LIMIT_PRICE, closePosition='true') 
                except:
                    time.sleep(1)
                    self.client.futures_create_order(symbol=self.TICKER, side=SIDE, type='STOP_MARKET', timeInForce= 'GTE_GTC', stopPrice=STOP_LIMIT_PRICE, closePosition='true') 
            except:
                pass
            
        if  self.TAKE_PROFIT_INC_LT== 'YES':
            try:
                try:
                    self.client.futures_create_order(symbol=self.TICKER, side=SIDE, type='TAKE_PROFIT_MARKET', timeInForce= 'GTE_GTC', stopPrice=TAKE_PROFIT_PRICE, closePosition='true')   
                except:
                    time.sleep(1)
                    self.client.futures_create_order(symbol=self.TICKER, side=SIDE, type='TAKE_PROFIT_MARKET', timeInForce= 'GTE_GTC', stopPrice=TAKE_PROFIT_PRICE, closePosition='true')   
            except:
                pass



        return




class SIZE_2():

    def __init__(self, client, COIN):
        self.client                    = client
        self.COIN                      = COIN
        self.STEP_SIZE, self.TICK_SIZE = self.SIZE_2()


    def SIZE_2(self):
        
        info = self.client.futures_exchange_info() 
        info = info['symbols']
        for x in range(len(info)):
            if info[x]['symbol'] == self.COIN:
                
                return info[x]['quantityPrecision'], info[x]['pricePrecision']
        return None




class FINISH_TRADE_VIEWS():

    def __init__(self, client, COIN):
        self.client                    = client
        self.COIN                      = COIN
        self.df                        = self.FINISH_TRADE_VIEWS()


    def FINISH_TRADE_VIEWS(self):
        
        df                 = self.client.futures_account_trades()
        dt_string          = datetime.now().strftime("%Y-%m-%d") 
        df                 = pd.DataFrame(df)
        df['DATE']         = pd.to_datetime(df['time'], unit='ms')
        df['DATE']         = df['DATE'] + pd.DateOffset(hours=1)
        df['DATE']         = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d %H:%M')
        df                 = df.sort_values(by='DATE')
        df                 = df.reset_index()
        df                 = df[(df['symbol'] == self.COIN)]
        df                 = df.reset_index()
        del df['index']

        df['price']        = round(pd.to_numeric(df['price']),10)
        df['qty']          = round(pd.to_numeric(df['qty']),10)
        df['quoteQty']     = round(pd.to_numeric(df['quoteQty']),10)
        df['commission']   = round(pd.to_numeric(df['commission']),10)
        df['realizedPnl']  = round(pd.to_numeric(df['realizedPnl']),10)

        df1      = pd.pivot_table(df, index=['orderId' ,'DATE', 'symbol', 'side', 'commissionAsset'], aggfunc= {'price': 'mean', 'qty': 'sum', 'quoteQty': 'sum', 'commission':'sum', 'realizedPnl':'sum'})
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
                                'commission'         :'COMMISSION',
                                'realizedPnl'        :'REALIZED PNL'
                                                    }, axis=1)
        
        return df1

