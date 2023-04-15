


import warnings
warnings.filterwarnings("ignore")

import time
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping

TICK_LIST_123 = ['MSFT', 'KO', 'ET', 'DVN', 'GOOG'] 

for w in range(len(TICK_LIST_123)):
    TICKER_CSV                  = TICK_LIST_123[w]
    root                        = (r'/Users/westhomas/Desktop/')
    df                          = pd.read_csv(root + TICKER_CSV + ".csv")
    
    full_length                 = len(df)
    output_view_prediction      = 63
    ALT                         = df.iloc[-252:,:]
    OUTPUT_PREDICTION           = len(ALT)/4




    START_PDF                   = time.time()    
    BACKTEST_DF                 = df.iloc[-252:, :]
    predictions                 = []

    for i in range(4):

        train_end               = -252 + 0 + (i * 63)
        test_start              = -252 + 0 + (i * 63)
        test_end                = -252 + 63 + (i * 63)


        if test_end == 0:

            training_set            = df.iloc[:train_end, 1:2].values
            test_set                = df.iloc[test_start:, 1:2].values 
            dataset_train           = df.iloc[:train_end, 1:2]
            dataset_test            = df.iloc[test_start:, 1:2]

        else:

            training_set            = df.iloc[:train_end, 1:2].values
            test_set                = df.iloc[test_start:test_end, 1:2].values
            dataset_train           = df.iloc[:train_end, 1:2]
            dataset_test            = df.iloc[test_start:test_end, 1:2]


    

        epoch                       = 100
        train_test_relative         = 0.95
        data_avail                  = len(training_set)
        data_remain                 = len(test_set)
        data_full                   = data_remain + 60


        # Feature Scaling
        sc                          = MinMaxScaler(feature_range = (0, 1))
        training_set_scaled         = sc.fit_transform(training_set)

    
        # Creating a data structure with 60 time-steps and 1 output
        X_train                     = []
        y_train                     = []

        for p in range(60, data_avail):
            X_train.append(training_set_scaled[p-60:p, 0])
            y_train.append(training_set_scaled[p, 0])

    
        X_train, y_train            = np.array(X_train), np.array(y_train)
        X_train                     = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    

        

        

        model = Sequential()

        #Adding the first LSTM layer and some Dropout regularisation
        model.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
        model.add(Dropout(0.2))

        # Adding a second LSTM layer and some Dropout regularisation
        model.add(LSTM(units = 50, return_sequences = True))
        model.add(Dropout(0.2))

        # Adding a third LSTM layer and some Dropout regularisation
        model.add(LSTM(units = 50, return_sequences = True))
        model.add(Dropout(0.2))

        # Adding a fourth LSTM layer and some Dropout regularisation
        model.add(LSTM(units = 50))
        model.add(Dropout(0.2))

        # Adding the output layer
        model.add(Dense(units = 1))

        # Compiling the RNN
        model.compile(optimizer = 'adam', loss = 'mean_squared_error')

        # Fitting the RNN to the Training set
        model.fit(X_train, y_train, epochs = epoch, batch_size = 32)

    

    

        # Getting the predicted stock price of 2017
        dataset_total               = pd.concat((dataset_train, dataset_test), axis = 0)
        inputs                      = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
        inputs                      = inputs.reshape(-1,1)
        inputs                      = sc.transform(inputs)
        X_test                      = []
        Y_test                      = []
    

        for o in range(60, data_full):
            X_test.append(inputs[o-60:o, 0])

        X_test                      = np.array(X_test)
        X_test                      = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    

        predicted_stock_price       = model.predict(X_test)
        predicted_stock_price       = sc.inverse_transform(predicted_stock_price)


        for x in range(len(predicted_stock_price)):
            predictions.append(predicted_stock_price.item(x))





    END_PDF    = time.time()
    TIME_PDF   = round((END_PDF - START_PDF)/60,2)
    print(' ')
    print('   - TIME TAKEN TO COMPLETE THE MACHINE LEARNING MODULE  :   ' + str(TIME_PDF) + ' MINS')

    del predictions[1]
    del predictions[0]

    BACKTEST_DF.reset_index(inplace = True)
    del BACKTEST_DF['index']

    BACKTEST_DF                 = BACKTEST_DF.drop(251)
    BACKTEST_DF                 = BACKTEST_DF.drop(250)
    BACKTEST_DF['PREDICTED']    = predictions
    BACKTEST_DF['CLOSE_RET']    = BACKTEST_DF['Close'].pct_change()
    BACKTEST_DF['PRED_RET']     = BACKTEST_DF['PREDICTED'].pct_change()
    correlation                 = BACKTEST_DF['CLOSE_RET'].corr(BACKTEST_DF['PRED_RET'])

    print(' ')
    print('Correlation is: ', correlation)
    print(' ')

    
    googl_ret       = pd.DataFrame(np.diff(BACKTEST_DF['Close'])).rename(columns = {0:'returns'}) 
    list_value      = [0]
    position        = [0]

    for i in range(len(googl_ret)):
        list_value.append(googl_ret.iat[i, 0])


    for i in range(1,len(BACKTEST_DF)):

        if BACKTEST_DF.iloc[i, 9] >0:
            position.append(1)

        elif BACKTEST_DF.iloc[i, 9] <0:
            position.append(-1)

    
    BACKTEST_DF['diff']         = list_value
    BACKTEST_DF['POSITION']     = position
    BACKTEST_DF                 = BACKTEST_DF.rename(columns={"POSITION":"signal"})
    FORECAST_DF                 = BACKTEST_DF.copy()
    df_date                     = FORECAST_DF.loc[:, 'Date']
    df_act                      = FORECAST_DF.loc[:, 'Close']
    df_res                      = FORECAST_DF.loc[:, 'PREDICTED']

    col_list_1 = ['Open', 'High', 'Low', 'Adj Close', 'Volume', 'CLOSE_RET', 'PRED_RET', 'diff', 'signal']
    col_list_2 = ['Adj Close', 'Volume', 'CLOSE_RET', 'PRED_RET', 'PREDICTED']

    for u in range(len(col_list_1)):
        del FORECAST_DF[col_list_1[u]]
        
    for z in range(len(col_list_2)):
        del BACKTEST_DF[col_list_2[z]]


    
    FORECAST_DF.to_csv(root + '/' + 'FORECAST_ML_STRATEGY - ' + TICKER_CSV + '.csv')
    BACKTEST_DF.to_csv(root + '/' + 'BACKTEST_ML_STRATEGY - ' + TICKER_CSV + '.csv')





    # Visualising the results
    plt.plot(df_date,df_act, color = 'red', label = 'Real '+TICKER_CSV+' Stock Price')
    plt.plot(df_date,df_res, color = 'blue', label = 'Predicted '+TICKER_CSV+' Stock Price')
    plt.xticks(np.arange(0,data_remain,50))
    plt.title(''+TICKER_CSV+' Stock Price Prediction')
    plt.xlabel('Time')
    plt.ylabel(''+TICKER_CSV+' Stock Price')
    plt.legend()
    plt.savefig(root + '/' + TICKER_CSV + ' ML FORECAST.png')
    plt.close()


