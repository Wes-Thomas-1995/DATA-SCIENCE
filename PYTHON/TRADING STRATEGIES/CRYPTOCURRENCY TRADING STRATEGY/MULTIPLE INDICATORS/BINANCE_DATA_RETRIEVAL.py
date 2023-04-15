

from binance.client import Client
from binance.enums import *
import pandas as pd
import warnings

warnings.filterwarnings("ignore")





def PORTFOLIO_ANALYTICS_TRIAL(data, client, df, history_reference):

    info = client.get_account()
    bala = info['balances']

    CURRENT_ASSETS_DF      = pd.DataFrame(columns=['Ticker', 'Quantity', 'USDT Value'])

    for b in bala:
        if float(b['free']) > 0:
            TICKER  = b['asset']
            VALUE   = float(b['free'])
            
            if TICKER != 'USDT':
                symbol_use = str(TICKER + "USDT")
                asset_price = client.get_symbol_ticker(symbol=symbol_use)
                COMMON_VALUE = VALUE * float(asset_price['price'])
            else:
                COMMON_VALUE = VALUE
            
            
            CURRENT_ASSETS_DF = CURRENT_ASSETS_DF.append({'Ticker'    : TICKER,
                                                          'Quantity'  : VALUE,
                                                          'USDT Value': COMMON_VALUE}, ignore_index=True)    
    
    
    
    for i in range(len(data)):
        TRADE_HISTORY_DF                                       = df[df['symbol'] == data[i]]
        TRADE_HISTORY_DF                                       = TRADE_HISTORY_DF.reset_index()
        del TRADE_HISTORY_DF['index']

        orders                                                 = client.get_open_orders(symbol=data[i])
        FLAG                                                   = TRADE_HISTORY_DF.at[len(TRADE_HISTORY_DF)-1, 'isBuyer']
        
        if FLAG == True and len(orders) > 0:
            QTY_RECENT                                          = float(TRADE_HISTORY_DF.at[len(TRADE_HISTORY_DF)-1, 'qty'])

            if history_reference[i] in CURRENT_ASSETS_DF['Ticker'].unique():
                CURRENT_ASSETS_DF_SPEC                          = CURRENT_ASSETS_DF[CURRENT_ASSETS_DF['Ticker'] == history_reference[i]]
                CURRENT_ASSETS_DF_SPEC                          = CURRENT_ASSETS_DF_SPEC.reset_index()
                del CURRENT_ASSETS_DF_SPEC['index']  


                QTY_OWNED                                       = float(CURRENT_ASSETS_DF_SPEC.at[0, 'Quantity'])
                PRICE_OWNED                                     = float(CURRENT_ASSETS_DF_SPEC.at[0, 'USDT Value'])/float(CURRENT_ASSETS_DF_SPEC.at[0, 'Quantity'])
                USDT_VALUE                                      = PRICE_OWNED * QTY_RECENT

                row_numb                                        = CURRENT_ASSETS_DF[CURRENT_ASSETS_DF['Ticker'] == history_reference[i]]
                row_num                                         = row_numb.index.tolist()
                CURRENT_ASSETS_DF.at[row_num[0],'Quantity']     = QTY_RECENT
                CURRENT_ASSETS_DF.at[row_num[0],'USDT Value']   = USDT_VALUE

            else:
                PRICE_STATS                                     = client.get_symbol_ticker(symbol=data[i])
                PRICE_CURRENT                                   = float(PRICE_STATS["price"])
                USDT_VALUE                                      = QTY_RECENT * PRICE_CURRENT
                CURRENT_ASSETS_DF                               = CURRENT_ASSETS_DF.append({'Ticker':history_reference[i],
                                                                                            'Quantity':QTY_RECENT,
                                                                                            'USDT Value':USDT_VALUE}, ignore_index=True)            

                
    return CURRENT_ASSETS_DF


def TRADE_HISTORY(data, client):

    df = pd.DataFrame()

    for ticker in data:
        data = client.get_my_trades(symbol=ticker)
        da = pd.DataFrame(data)
        df = pd.concat([df, da], axis=0, ignore_index=True, sort=False)
    
    
    df.set_index("id", inplace=True)

    df['DATE']  = pd.to_datetime(df['time'], unit='ms')
    df['DATE']  = df['DATE'] + pd.DateOffset(hours=1)
    df['DATE']  = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df          = df.sort_values(by='DATE')
    df          = df.reset_index()
    df          = df[(df['DATE'] >= '2022-11-20')]
    df          = df.reset_index()
    del df['index']

    df['price']      = pd.to_numeric(df['price'])
    df['qty']        = pd.to_numeric(df['qty'])
    df['quoteQty']   = pd.to_numeric(df['quoteQty'])
    df = pd.pivot_table(df, index=['orderId' ,'DATE', 'symbol', 'isBuyer'], aggfunc= {'price': 'mean', 'qty': 'sum', 'quoteQty': 'sum'})
    df   = df.reset_index()


    return df


def TICK_SIZE(data, client):
    
    step_size_list          = []
    tick_size_list          = []
    history_reference       = []

    def get_tick_and_step_size(symbol):
            tick_size = None
            step_size = None
            symbol_info = client.get_symbol_info(symbol)
            for filt in symbol_info['filters']:
                if filt['filterType'] == 'PRICE_FILTER':
                    tick_size = float(filt['tickSize'])
                elif filt['filterType'] == 'LOT_SIZE':
                    step_size = float(filt['stepSize'])
            return tick_size, step_size


    for i in range(len(data)):
        tick_size, step_size = get_tick_and_step_size(data[i])
        tick_size_list.append(tick_size)
        step_size_list.append(step_size)

        s = data[i]
        n = s.replace('USDT', '')
        history_reference.append(n)




    return tick_size_list, step_size_list, history_reference
        
        
def LIMIT_DATAFRAME(data, client):
    LIMIT_DF      = pd.DataFrame(columns=['Ticker', 'limit_flag'])

    for i in range(len(data)):
        orders              = client.get_open_orders(symbol=data[i])
        
        if len(orders) > 0:
            LF = 'Y'
        else:
            LF = 'N'

        LIMIT_DF = LIMIT_DF.append({'Ticker'    : data[i],
                                    'limit_flag': LF}, ignore_index=True) 

    return LIMIT_DF

