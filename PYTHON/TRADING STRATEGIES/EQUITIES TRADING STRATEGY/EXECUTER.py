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




def PORTFOLIO_ANALYTICS(api, round_load=1):
    api_key                         = 'XXXXX'
    api_secret                      = 'XXXXX'
    base_url                        = 'https://paper-api.alpaca.markets'
    api                             = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    
    account             = api.get_account()
    buying_power        = account.buying_power
    cash                = account.cash

    equity              = float(account.equity)
    last_equity         = float(account.last_equity)
    DTD_Move            = equity - last_equity

    portfolio_value     = account.portfolio_value
    long_market_value   = account.long_market_value
    short_market_value  = account.short_market_value
    portfolio           = api.list_positions()

    Positions_open      = pd.DataFrame(columns=['Ticker', 'Quantity', 'Side'])
    POD                 = pd.DataFrame(columns=['Ticker', 'Quantity', 'Side', 'Purchase_Price', 'Current_Price'])

    print(' ')
    print('     - CASH                                              :   $' + str(cash))
    print('     - EQUITY                                            :   $' + str(equity))
    print('     - PORTFOLIO VALUE                                   :   $' + str(portfolio_value))
    print('        - VALUE OF LONG POSITIONS                        :   $' + str(long_market_value))
    print('        - VALUE OF SHORT POSITIONS                       :   $' + str(short_market_value))

    att_list = [cash, equity, portfolio_value, long_market_value, short_market_value]

    if len(portfolio) > 0:
        if round_load == 1:
            print(' ')
            print("     - POSITIONS IN THE CURRENT PORTFOLIO                :    {}".format(str(len(portfolio))))

            tick = portfolio[0].symbol
            quant = int(portfolio[0].qty)

            for position in portfolio:
                if float(position.qty) >= 10:
                    print("        - {} SHARES OF TICKER                            :    {}".format(position.qty, position.symbol))
                else:
                    print("        - {} SHARES OF TICKER                             :    {}".format(position.qty, position.symbol))

        for i in range(len(portfolio)):
            Positions_open = Positions_open.append({'Ticker'    : portfolio[i].symbol,
                                                    'Quantity'  : portfolio[i].qty,
                                                    'Side'      : portfolio[i].side}, ignore_index=True)

            POD = POD.append({'Ticker'              : portfolio[i].symbol,
                              'Quantity'            : portfolio[i].qty,
                              'Side'                : portfolio[i].side,
                              'Purchase_Price'      : portfolio[i].avg_entry_price,
                              'Current_Price'       : portfolio[i].current_price, }, ignore_index=True)

    else:
        print('        - POSITIONS IN THE CURRENT PORTFOLIO             :    0')

    return Positions_open, att_list, POD







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







def EXECUTION(TRANSACTION_DF, data):
    output = data


    api_key                         = 'XXXXX'
    api_secret                      = 'XXXXX'
    base_url                        = 'https://paper-api.alpaca.markets'
    api                             = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    Positions_open, att_list, POD   = PORTFOLIO_ANALYTICS(api, round_load=1)
    POSITION_HISTORY                = RELOAD_LOAD_DATA_SQL(POD)
    
    SELLING_DF                      = pd.DataFrame(columns=['TICKER_COMMANDS','PORTFOLIO_COMMANDS', 'PRICE', 'QUANTITY'])
    
    print(' ')
    print('     - TRANSACTIONS RESULTING FROM OUT STRATEGY')

    for w in range(len(TRANSACTION_DF)):
        if TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'] == 'SELL':
            if TRANSACTION_DF.at[w, 'TICKER_COMMANDS'] in Positions_open['Ticker'].values:
                
                row_numb = Positions_open[Positions_open['Ticker'] == TRANSACTION_DF.at[w, 'TICKER_COMMANDS']]
                row_num = row_numb.index.tolist()
            
                SELLING_DF.append({'TICKER_COMMANDS'        : TRANSACTION_DF.at[w, 'TICKER_COMMANDS'],
                                   'PORTFOLIO_COMMANDS'     : TRANSACTION_DF.at[w, 'PORTFOLIO_COMMANDS'],
                                   'PRICE'                  : TRANSACTION_DF.at[w, 'PRICE'],
                                   'QUANTITY'               : Positions_open.at[row_num[0],'Ticker']}, ignore_index=True)


    TRANSACTION_DF.drop(TRANSACTION_DF[TRANSACTION_DF['PORTFOLIO_COMMANDS'] == 'SELL'].index, inplace = True)
    TRANSACTION_DF = TRANSACTION_DF.reset_index()
    del TRANSACTION_DF['index']
    
  

    if len(SELLING_DF) > 0:
        TRANSACTION_DF.append(SELLING_DF)     

    if len(TRANSACTION_DF) > 0:
        for i in range(len(TRANSACTION_DF)):
            symbol_2 = TRANSACTION_DF.at[i, 'TICKER_COMMANDS']
            direction = TRANSACTION_DF.at[i, 'PORTFOLIO_COMMANDS']
            price = TRANSACTION_DF.at[i, 'PRICE']
            quantity = TRANSACTION_DF.at[i, 'QUANTITY']

            if quantity > 0:
                api.submit_order(symbol=symbol_2,
                qty=quantity,
                side=direction,
                type='market',
                time_in_force='gtc')
                
                
                print('        - ORDER PLACED -- ' + direction + '  --  ' + symbol_2 + ' -- ' + str(quantity))
            else:
                pass
    else:
        print('        - NO ORDERS TO BE PLACED')

    
    POSITION_HISTORY = ''
    return Positions_open, att_list, POD, TRANSACTION_DF, POSITION_HISTORY






