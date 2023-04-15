from binance.helpers import round_step_size
from binance.client import Client
from binance.enums import *


from BINANCE_OBJ import CLOSE_POSITION, OPEN_POSITIONS, SIZE_2, FINISH_TRADE_VIEWS, CREATE_ORDER, CREATE_TP_AND_SL

from datetime import datetime, timedelta, date
from pytimedinput import timedInput
import pandas as pd
import numpy as np
import warnings
import time
import os
import sys

warnings.filterwarnings("ignore")








class LONG_TERM():

    def __init__(self, DF_LT, COIN, LEVERAGE,  TAKE_PROFIT, STOP_LOSS ,REFERENCE_DAYS, client, DONE_LT):
        self.client            = client
        self.COIN              = COIN
        self.LEVERAGE          = LEVERAGE
        self.TAKE_PROFIT       = TAKE_PROFIT
        self.STOP_LOSS         = STOP_LOSS
        self.REFERENCE_DAYS    = REFERENCE_DAYS
        self.DF_LT             = DF_LT
        self.DONE_LT           = DONE_LT

        self.DONE_LT           = self.LONG_TERM_STRATEGY()


    def LONG_TERM_STRATEGY(self):
        
        self.DF_LT = self.DF_LT[self.DF_LT['TIME_RELATIVE'] == (datetime.now().replace(second=0, microsecond=0))].reset_index()
        
        if len(self.DF_LT) > 0:
            if self.DF_LT.at[len(self.DF_LT)-1, 'DAY NUMBER'] in self.REFERENCE_DAYS:
                for i in range(len(self.DF_LT)):
                    if self.DF_LT.at[i, 'COMMENT'] == "LONG - EXIT" or self.DF_LT.at[i, 'COMMENT'] == "SHORT - EXIT":
                        self.DF_LT = self.DF_LT.drop(i)

                self.DF_LT = self.DF_LT.reset_index()        

                if self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] != "LONG - EXIT TP" or self.DF_LT.at[len(self.DF_LT)-1, 'COMMENT'] != "SHORT - EXIT TP":

                    print('\n-- LONG TERM STRATEGY --')
                    OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)

                    if len(OPEN_POS.POS_DF) != 0:
                        CLOSE_POSITION(self.client, self.COIN, OPEN_POS.QTY, OPEN_POS.DIRECTION_EXIST)
                        time.sleep(3)

                    STEP_INFO               = SIZE_2(self.client, self.COIN)
                    TRADE                   = FINISH_TRADE_VIEWS(self.client, self.COIN)

                    PROFIT                  = TRADE.df.at[len(TRADE.df)-1, 'REALIZED PNL']
                    START_AMOUNT            = TRADE.df.at[len(TRADE.df)-2, 'USDT_VALUE']/self.LEVERAGE

                    COMMISION               = TRADE.df.at[len(TRADE.df)-1, 'COMMISSION']
                    TRADE_VALUE             = (START_AMOUNT + PROFIT - COMMISION)* (1-(0.0004 * self.LEVERAGE))
                    BALANCE_TO_TRADE        = TRADE_VALUE * self.LEVERAGE 
                    PRICE                   = float(self.client.futures_symbol_ticker(symbol=self.COIN)['price'])
                    QTY                     = "{:0.0{}f}".format((BALANCE_TO_TRADE/PRICE), STEP_INFO.STEP_SIZE)
                    DIRECTION               = self.DF_LT.at[len(self.DF_LT)-1, 'POSITION']
                    
                    if DIRECTION != 'FLAT':
                        CREATE_ORDER(self.client, self.COIN, QTY, DIRECTION, self.LEVERAGE)
                        time.sleep(2)      
                        OPEN_POS = OPEN_POSITIONS(self.client, self.COIN)

                        print('TRADE_VALUE       : ' + str(round(TRADE_VALUE,2))) 
                        print('ENTRY_PRICE       : ' + str(OPEN_POS.ENTRY_PRICE)) 
                        CREATE_TP_AND_SL(self.client, self.COIN, OPEN_POS.ENTRY_PRICE, OPEN_POS.DIRECTION_EXIST, self.TAKE_PROFIT,  self.STOP_LOSS, STEP_INFO.TICK_SIZE, 'YES', 'YES')

                        self.DONE_LT = 'YES'

        return self.DONE_LT










