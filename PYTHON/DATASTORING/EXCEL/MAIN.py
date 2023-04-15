
from CONTROLLER import TRADE_LOG

from binance.client import Client
from datetime import datetime
import warnings
import time

warnings.filterwarnings("ignore")





def FULL_RUN():

    api_key                 = 'XXXXXX'
    api_secret              = 'XXXXXX'
    client                  = Client(api_key, api_secret)

    ROOT_TRADES     = (r'/Users/westhomas/Desktop/OBJECT ORIENTATED')

    A = 0
    while A == 0:

        if datetime.now() >= (datetime.now().replace(minute=0, second=0, microsecond=1)) and datetime.now() <= (datetime.now().replace(minute=0, second=40, microsecond=0)):
            time.sleep(3480)
            COMPLETE = 'NO'

        elif COMPLETE =='NO':
            if datetime.now() >= (datetime.now().replace(hour=23, minute=59, second=0, microsecond=1)) and datetime.now() <= (datetime.now().replace(hour=23, minute=59, second=4, microsecond=1)):
                TRADE_LOG(client, ROOT_TRADES)
                COMPLETE = 'YES'

        else:
            time.sleep(3)





if __name__ == '__main__':

    FULL_RUN()

