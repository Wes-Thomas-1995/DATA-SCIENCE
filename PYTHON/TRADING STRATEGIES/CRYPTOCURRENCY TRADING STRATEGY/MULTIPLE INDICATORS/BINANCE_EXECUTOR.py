from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *
from math import floor
import pandas as pd
import time





def EXECUTION(TRANSACTION_DF, data, step_size_list, data_2, client, TRADE_HISTORY_DF, CURRENT_ASSETS_DF, tick_size_list):
    
    BUYING_DF                       = pd.DataFrame(columns=['TICKER_COMMANDS','PORTFOLIO_COMMANDS', 'QUANTITY', 'PRICE'])
    SELLING_DF                      = pd.DataFrame(columns=['TICKER_COMMANDS','PORTFOLIO_COMMANDS', 'QUANTITY', 'PRICE'])
    
    for w in range(len(TRANSACTION_DF)):  
         
        index_item      = data.index(TRANSACTION_DF.at[w, 'TICKER_COMMANDS'])
        tick_asset      = data_2[index_item]
        row_numb        = CURRENT_ASSETS_DF[CURRENT_ASSETS_DF['Ticker'] == tick_asset]
        row_num         = row_numb.index.tolist()         
        price_1         = TRANSACTION_DF.at[w, 'PRICE']
        
        value = 1/float(step_size_list[index_item])
        
        
        if TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'] == 'SELL':
            if len(row_numb)!=0 and CURRENT_ASSETS_DF.at[row_num[0],'USDT Value'] >= 5:  
                orders      = client.get_open_orders(symbol=TRANSACTION_DF.at[w, 'TICKER_COMMANDS'])
                total       = len(orders)

                if total > 0:
                    if total > 1:
                        for k in range(len(total)):
                            order_id = orders[k]['orderId']
                            result = client.cancel_order(symbol=TRANSACTION_DF.at[w, 'TICKER_COMMANDS'], orderId=order_id)
                    else:
                        result = client.cancel_order(symbol=TRANSACTION_DF.at[w, 'TICKER_COMMANDS'], orderId=orders[0]['orderId'])
                
                qty             = round_step_size(client.get_asset_balance(asset=tick_asset)['free'], step_size_list[index_item])                                   
                SELLING_DF      = SELLING_DF.append({'TICKER_COMMANDS'        : TRANSACTION_DF.at[w, 'TICKER_COMMANDS'],
                                                     'PORTFOLIO_COMMANDS'     : TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'],
                                                     'QUANTITY'               : qty,
                                                     'PRICE'                  : price_1}, ignore_index=True)
    
    
        if TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'] == 'BUY':
            
            if len(row_numb)==0 or CURRENT_ASSETS_DF.at[row_num[0],'USDT Value'] <= 5:
                TRADES_TICKER   = TRADE_HISTORY_DF[TRADE_HISTORY_DF['symbol'] == TRANSACTION_DF.at[w, 'TICKER_COMMANDS']]
                TRADES_TICKER   = TRADES_TICKER.reset_index()
                del TRADES_TICKER['index']
                
                QUANTITY        = round_step_size((float(TRADES_TICKER.at[(len(TRADES_TICKER))-1, 'quoteQty'])/price_1), step_size_list[index_item])
                BUYING_DF       = BUYING_DF.append({'TICKER_COMMANDS'        : TRANSACTION_DF.at[w, 'TICKER_COMMANDS'],
                                                    'PORTFOLIO_COMMANDS'     : TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'],
                                                    'QUANTITY'               : QUANTITY,
                                                    'PRICE'                  : price_1}, ignore_index=True)                



    TRANSACTION_DF = pd.DataFrame(columns=['TICKER_COMMANDS','PORTFOLIO_COMMANDS', 'QUANTITY', 'PRICE'])
    
    if len(BUYING_DF) > 0:
        TRANSACTION_DF = TRANSACTION_DF.append(BUYING_DF)  

    if len(SELLING_DF) > 0:
        TRANSACTION_DF = TRANSACTION_DF.append(SELLING_DF)           
    
    TRANSACTION_DF = TRANSACTION_DF.reset_index()
    del TRANSACTION_DF['index']
    
    if len(TRANSACTION_DF) > 0:
        for i in range(len(TRANSACTION_DF)):
            
            index_item      = data.index(TRANSACTION_DF.at[i, 'TICKER_COMMANDS'])
            symbol_2        = TRANSACTION_DF.at[i, 'TICKER_COMMANDS']
            direction       = TRANSACTION_DF.at[i, 'PORTFOLIO_COMMANDS']
            quantity        = float(TRANSACTION_DF.at[i, 'QUANTITY'])
            price_2         = float(TRANSACTION_DF.at[i, 'PRICE'])
            price_STOP      = round_step_size((price_2*0.985), tick_size_list[index_item])
            
            print('        - NEXT ORDER  -- ' + direction + '  --  ' + symbol_2 + ' -- ' + str(quantity) + ' -- ' + str(round((quantity * price_2) ,2)))
                
            if (quantity * price_2) > 15:
                if quantity > 0:  
                    try:
                        order = client.create_order(
                                    symbol=symbol_2,
                                    side=direction,
                                    type='MARKET',
                                    quantity=quantity)
                        print('        - ORDER PLACED -- ' + direction + '  --  ' + symbol_2 + ' -- ' + str(quantity) + ' -- ' + str(price_2))
                    except:
                        print('        - ERROR PLACING ORDER -- ' + direction + '  --  ' + symbol_2 + ' -- ' + str(quantity) + ' -- ' + str(price_2) + ' -- ' + str(round((quantity * price_2) ,2)))
            else:
                pass
    else:
        print('        - NO ORDERS TO BE PLACED')    
    
    return TRANSACTION_DF, CURRENT_ASSETS_DF, TRADE_HISTORY_DF







