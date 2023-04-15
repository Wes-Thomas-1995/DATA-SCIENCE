import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from nsepy import get_history
from datetime import datetime
import pandas as pd
import numpy as np
import time

np.set_printoptions(suppress=True)

# Fetching the data
startDate               = datetime(2019, 1,1)
endDate                 = datetime(2020, 10, 5)
StockData               = get_history(symbol='INFY', start=startDate, end=endDate)
StockData['TradeDate']  = StockData.index
FullData                = StockData[['Close']].values


sc                      = MinMaxScaler()
DataScaler              = sc.fit(FullData)
X                       = DataScaler.transform(FullData)


 
# Printing last 10 values of the scaled data which we have created above for the last model
# Here I am changing the shape of the data to one dimensional array because
# for Multi step data preparation we need to X input in this fashion
X               = X.reshape(X.shape[0],)

# Multi step data preparation
X_samples       = list()
y_samples       = list()
 
NumerOfRows     = len(X)
TimeSteps       = 10      # next few day's Price Prediction is based on last how many past day's prices
FutureTimeSteps = 5       # How many days in future you want to predict the prices

for i in range(TimeSteps , NumerOfRows-FutureTimeSteps , 1):
    x_sample = X[i-TimeSteps:i]
    y_sample = X[i:i+FutureTimeSteps]
    X_samples.append(x_sample)
    y_samples.append(y_sample)
 
# Reshape the Input as a 3D (samples, Time Steps, Features)
# We do not reshape y as a 3D data  as it is supposed to be a single column only
X_data          = np.array(X_samples)
X_data          = X_data.reshape(X_data.shape[0],X_data.shape[1], 1)
y_data          = np.array(y_samples)
TestingRecords  = 5

# Splitting the data into train and test
X_train         = X_data[:-TestingRecords]
X_test          = X_data[-TestingRecords:]
y_train         = y_data[:-TestingRecords]
y_test          = y_data[-TestingRecords:]

# Defining Input shapes for LSTM
TimeSteps       = X_train.shape[1]
TotalFeatures   = X_train.shape[2]



regressor = Sequential()
regressor.add(LSTM(units = 10, activation = 'relu', input_shape = (TimeSteps, TotalFeatures), return_sequences=True))
regressor.add(LSTM(units = 5, activation = 'relu', input_shape = (TimeSteps, TotalFeatures), return_sequences=True))
regressor.add(LSTM(units = 5, activation = 'relu', return_sequences=False ))
regressor.add(Dense(units = FutureTimeSteps))
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

StartTime   = time.time()
regressor.fit(X_train, y_train, batch_size = 5, epochs = 100, verbose=0)
EndTime     = time.time()

print("Total Time Taken: ", round((EndTime-StartTime)/60), 'Minutes')




 
# Making predictions on test data
predicted_Price = regressor.predict(X_test)
predicted_Price = DataScaler.inverse_transform(predicted_Price)
print('#### Predicted Prices ####')
print(predicted_Price)

# Getting the original price values for testing data
orig=y_test
orig=DataScaler.inverse_transform(y_test)
print('\n#### Original Prices ####')
print(orig)



# Making predictions on test data
Last10DaysPrices    = np.array([1376.2, 1371.75,1387.15,1370.5 ,1344.95, 1312.05, 1316.65, 1339.45, 1339.7 ,1340.85])
Last10DaysPrices    = Last10DaysPrices.reshape(-1, 1)
X_test              = DataScaler.transform(Last10DaysPrices)

NumberofSamples     = 1
TimeSteps           = X_test.shape[0]
print(TimeSteps)

NumberofFeatures    = X_test.shape[1]
X_test              = X_test.reshape(NumberofSamples,TimeSteps,NumberofFeatures)
Next5DaysPrice      = regressor.predict(X_test, verbose=0)
Next5DaysPrice      = DataScaler.inverse_transform(Next5DaysPrice)

print(Next5DaysPrice)


