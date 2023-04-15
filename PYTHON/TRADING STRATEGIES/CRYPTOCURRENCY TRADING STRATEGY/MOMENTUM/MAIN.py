
from GOOGLE_SHEET import GOOGLE_SHEET_DATAFRAME
from CONTROLLER import LONG_TERM
from EMAIL_OUTPUT import EMAIL


from binance.client import Client
from datetime import datetime
import warnings
import time

warnings.filterwarnings("ignore")



def FULL_RUN():

    api_key                 = 'XXXXX'
    api_secret              = 'XXXXX'
    client                  = Client(api_key, api_secret)

    HOUR_CONDITIONS = {"COIN"              : 'ETHUSDT',  
                       "LEVERAGE"          : 8}

    DONE_LT = 'NO'
    while DONE_LT == 'NO':
        if datetime.now() >= (datetime.now().replace(minute=0, second=0, microsecond=0)) and datetime.now() <= (datetime.now().replace(minute=0, second=59, microsecond=0)):

            GOOGLE_SHEET_DATA = GOOGLE_SHEET_DATAFRAME(HOUR_CONDITIONS["COIN"])                    
            STATUS            = LONG_TERM(GOOGLE_SHEET_DATA.DF_LT, 
                                        HOUR_CONDITIONS["COIN"], 
                                        HOUR_CONDITIONS["LEVERAGE"],
                                        client, 
                                        DONE_LT)
            
            DONE_LT = STATUS.DONE_LT

        else:
            DONE_LT = 'YES'








def TEST_RUN():

    from BINANCE_OBJ import CLOSE_POSITION, OPEN_POSITIONS, SIZE_2, FINISH_TRADE_VIEWS, CREATE_ORDER, CREATE_TP_AND_SL

    api_key                 = 'XXXXX'
    api_secret              = 'XXXXX'
    client                  = Client(api_key, api_secret)

    HOUR_CONDITIONS = {"COIN"              : 'XRPUSDT',
                       "REFERENCE_DAYS"    : [0, 4, 5, 6],
                       "LEVERAGE"          : 20,
                       "TAKE_PROFIT"       : 0.5,
                       "STOP_LOSS"         : 2}




    GOOGLE_SHEET_DATA       = GOOGLE_SHEET_DATAFRAME(HOUR_CONDITIONS["COIN"])                    
    TRADE                   = FINISH_TRADE_VIEWS(client, HOUR_CONDITIONS["COIN"])

    PROFIT                  = TRADE.df.at[len(TRADE.df)-1, 'REALIZED PNL']
    START_AMOUNT            = TRADE.df.at[len(TRADE.df)-2, 'USDT_VALUE']/HOUR_CONDITIONS["LEVERAGE"]

    COMMISION               = TRADE.df.at[len(TRADE.df)-1, 'COMMISSION']
    TRADE_VALUE             = (START_AMOUNT + PROFIT - COMMISION)* (1-(0.0004 * HOUR_CONDITIONS["LEVERAGE"]))
    BALANCE_TO_TRADE        = TRADE_VALUE * HOUR_CONDITIONS["LEVERAGE"] 


    print(' ')
    print('GOOGLE SHEETS DATAFRAME : ')
    print(' ')
    print(GOOGLE_SHEET_DATA.DF_LT)
    print(' ')
    print('DIRECTION OF THE NEXT TRADE : ' + str(GOOGLE_SHEET_DATA.DF_LT.at[(len(GOOGLE_SHEET_DATA.DF_LT)-1),'POSITION']))
    print(' ')
    print('TRADE HISTORY DATAFRAME : ')
    print(' ')
    print(TRADE.df)
    print(' ')
    print('PREVIOUS TRADE PROFIT         : ' + str(round(PROFIT, 2)))
    print('PREVIOUS TRADE START AMOUNT   : ' + str(round(START_AMOUNT, 2)))
    print('PREVIOUS TRADE COMMISION      : ' + str(round(COMMISION, 2)))
    print(' ')
    print('TRADE AMOUNT FOR NEXT TRADE   : ' + str(round(TRADE_VALUE, 2)))
    print('TOTAL BALANCE FOR NEXT TRADE  : ' + str(round(BALANCE_TO_TRADE, 2)))
    print(' ')

    EMAIL(round(TRADE_VALUE,2), round(PROFIT,2))











if __name__ == '__main__':

    #FULL_RUN()
    TEST_RUN()
