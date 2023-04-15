from ta import add_all_ta_features
from ta.utils import dropna

from datetime import datetime  
import pytz  
from time import strftime
from datetime import time
import pandas as pd
import warnings
import os.path
import os

warnings.filterwarnings("ignore")




class GOOGLE_SHEET_DATAFRAME():

    def __init__(self, ticker):
        self.ticker = ticker
        self.DF_GS_BASIC = self.TRIAL_GOOGLE_SHEET()
        self.DF_ST, self.DF_LT, self.DF_GS, = self.DATAFRAME_PROCESSING()


    def TRIAL_GOOGLE_SHEET(self):
        SHEET_ID   = 'XXXXX'
        SHEET_NAME = 'XXXXX'
        url        = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

        try:
            DF_GS_BASIC = pd.read_csv(url)
        except:
            try:
                DF_GS_BASIC = pd.read_csv(url)
            except:
                DF_GS_BASIC = pd.DataFrame(columns=['TIME_ACTION','INTERVAL','TICKER','POSITION','COMMENT','PRICE','TIME_RELATIVE','ZAP_TIME'])
            
        
        return DF_GS_BASIC


    def DATAFRAME_PROCESSING(self):

        df = self.DF_GS_BASIC

        dt1     = datetime.strptime((str((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))), "%Y-%m-%d %H:%M:%S")
        dt2     = datetime.strptime((str((datetime.now(pytz.utc)).strftime("%Y-%m-%d %H:%M:%S"))), "%Y-%m-%d %H:%M:%S")
        delta   = int(((dt1 - dt2).total_seconds())/3600)

        if len(df)>0:

            COMMENT_LIST           = []
            df['COMMENT']          = df['COMMENT'].str.upper()
            df['POSITION']         = df['POSITION'].str.upper()
            df['TIME_ACTION']      = pd.to_datetime(df['TIME_ACTION'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['TIME_RELATIVE']    = pd.to_datetime(df['TIME_RELATIVE'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['ZAP_TIME']         = pd.to_datetime(df['ZAP_TIME'], format='%Y-%m-%d %H:%M:%S') + pd.DateOffset(hours=delta)
            df['DAY OF WEEK']      = df['TIME_ACTION'].dt.day_name()
            df['DAY NUMBER']       = df['TIME_ACTION'].dt.day_of_week
            df['TIME']             = df['TIME_ACTION'].dt.time
            df                     = df[['TIME_ACTION', 'INTERVAL', 'TICKER', 'POSITION', 'COMMENT', 'PRICE', 'TIME_RELATIVE', 'ZAP_TIME', 'DAY OF WEEK', 'DAY NUMBER', 'TIME']]
            
            for i in range(len(df)):   

                    if df.at[i, 'COMMENT'] == "EXIT LONG PROFIT":
                        COMMENT = "LONG - EXIT TP"

                    elif df.at[i, 'COMMENT'] == "EXIT SHORT PROFIT":
                        COMMENT = "SHORT - EXIT TP"

                    elif df.at[i, 'COMMENT'] == "ENTER SHORT":
                        COMMENT = "SHORT - ENTRY"

                    elif df.at[i, 'COMMENT'] == "ENTER LONG":
                        COMMENT = "LONG - ENTRY"

                    elif df.at[i, 'COMMENT'] == "EXIT LONG LOSS":
                        COMMENT = "LONG - EXIT SL"

                    elif df.at[i, 'COMMENT'] == "CLOSE ENTRY(B) ORDER ENTER SHORT":
                        COMMENT = "SHORT - EXIT"

                    elif df.at[i, 'COMMENT'] == "CLOSE ENTRY(S) ORDER ENTER LONG":
                        COMMENT = "LONG - EXIT"

                    elif df.at[i, 'COMMENT'] == "EXIT SHORT LOSS":
                        COMMENT = "SHORT - EXIT SL"
                        
                    else:
                        COMMENT = "------"            

                    COMMENT_LIST.append(COMMENT)
                    
            df['COMMENT']               = COMMENT_LIST
            DF_ST                       = (df[df['INTERVAL'] == 15]).reset_index().iloc[:, 1:]
            DF_LT                       = (df[df['INTERVAL'] == 60]).reset_index().iloc[:, 1:]

        else:
            DF_LT = df
            DF_ST = df

        return DF_ST, DF_LT, df