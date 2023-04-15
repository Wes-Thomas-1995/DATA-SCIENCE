#!/usr/local/bin/python3
from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *


from BINANCE_OBJ import CLOSE_POSITION, OPEN_POSITIONS, SIZE_2, FINISH_TRADE_VIEWS, CREATE_ORDER, CREATE_TP_AND_SL, GET_BALANCE

from datetime import datetime, timedelta, date
import pandas as pd
import warnings
import time
import os
import sys

warnings.filterwarnings("ignore")








class LONG_TERM():

    def __init__(self, DF_LT, COIN, LEVERAGE, client, DONE_LT):
        self.client            = client
        self.COIN              = COIN
        self.LEVERAGE          = LEVERAGE
        self.DF_LT             = DF_LT
        self.DONE_LT           = DONE_LT

        self.DONE_LT           = self.LONG_TERM_STRATEGY()


    def LONG_TERM_STRATEGY(self):
        
        self.DF_LT = self.DF_LT[self.DF_LT['TIME_ACTION'] >= ((datetime.now() - timedelta(minutes=59)).replace(second=0, microsecond=0))].reset_index()

        if len(self.DF_LT) > 0:
            if self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] == "CLOSE SHORT" or self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] == "CLOSE LONG":
                    
                    OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)

                    if len(OPEN_POS.POS_DF) != 0:
                        CLOSE_POSITION(self.client, self.COIN, OPEN_POS.QTY, OPEN_POS.DIRECTION_EXIST)
                        time.sleep(3)

                        print('\n-- ELLIPSE LONG TERM STRATEGY --')
                        print('-- CLOSE POSITION --')

                        self.DONE_LT = 'YES'

            else:
                    self.DF_LT      = self.DF_LT[self.DF_LT['TIME_RELATIVE'] >= ((datetime.now()).replace(second=0, microsecond=0))].reset_index()
                    OPEN_POS        = OPEN_POSITIONS(self.client, self.COIN)

                    if len(OPEN_POS.POS_DF) != 0:
                        CLOSE_POSITION(self.client, self.COIN, OPEN_POS.QTY, OPEN_POS.DIRECTION_EXIST)
                        time.sleep(3)

                    STEP_INFO               = SIZE_2(self.client, self.COIN)
                    CURRENT                 = GET_BALANCE(self.client)
                    TRADE_VALUE             = (CURRENT.BALANCE)* (1-(0.00045 * self.LEVERAGE))
                    BALANCE_TO_TRADE        = TRADE_VALUE * self.LEVERAGE 
                    PRICE                   = float(self.client.futures_symbol_ticker(symbol=self.COIN)['price'])
                    QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_INFO.STEP_SIZE)
                    DIRECTION               = self.DF_LT.at[len(self.DF_LT)-1, 'POSITION']
                    
                    CREATE_ORDER(self.client, self.COIN, QTY, DIRECTION, self.LEVERAGE)
                    time.sleep(2)      
                    OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)

                    print('\n-- ELLIPSE LONG TERM STRATEGY --')
                    print('TRADE_VALUE       : ' + str(round(TRADE_VALUE,2))) 
                    print('ENTRY_PRICE       : ' + str(OPEN_POS.ENTRY_PRICE)) 

                    self.DONE_LT = 'YES'

        return self.DONE_LT









