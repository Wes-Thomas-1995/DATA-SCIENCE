

import warnings
warnings.filterwarnings("ignore")

import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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


TICKER_CSV                  = 'KO'
root                        = (r'/Users/westhomas/Desktop/')
df                          = pd.read_csv(root + TICKER_CSV + ".csv")


full_length = len(df)

start_date = '2022-01-01'
end_date = '2022-10-28'

mask = (df['Date'] > start_date) & (df['Date'] <= end_date)
print(df.loc[mask])

print(len(df.loc[mask]))





epoch                       = 100
train_test_relative         = 0.95
data_avail                  = math.ceil(train_test_relative * len(df))
data_remain                 = (len(df)-data_avail)
data_full                   = data_remain + 60


training_set                = df.iloc[:data_avail, 1:2].values
test_set                    = df.iloc[data_avail:, 1:2].values


# Feature Scaling
sc                          = MinMaxScaler(feature_range = (0, 1))
training_set_scaled         = sc.fit_transform(training_set)

# Creating a data structure with 60 time-steps and 1 output
X_train                     = []
y_train                     = []

for i in range(60, data_avail):
    X_train.append(training_set_scaled[i-60:i, 0])
    y_train.append(training_set_scaled[i, 0])

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
dataset_train               = df.iloc[:data_avail, 1:2]
dataset_test                = df.iloc[data_avail:, 1:2]
dataset_total               = pd.concat((dataset_train, dataset_test), axis = 0)
inputs                      = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
inputs                      = inputs.reshape(-1,1)
inputs                      = sc.transform(inputs)
X_test                      = []
Y_test                      = []

for i in range(60, data_full):
    X_test.append(inputs[i-60:i, 0])
    
X_test                      = np.array(X_test)
X_test                      = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

print(X_test.shape)


predicted_stock_price       = model.predict(X_test)
predicted_stock_price       = sc.inverse_transform(predicted_stock_price)




df_prediction               = pd.DataFrame(columns=['DATE', 'ACTUAL', 'PREDICTED'])
df_prediction['DATE']       = df.loc[data_avail:, 'Date']
df_prediction['ACTUAL']     = df.loc[data_avail:, 'Close']

df_prediction.reset_index(inplace = True)
del df_prediction['index']

df_prediction               = df_prediction.drop(61)
df_prediction               = df_prediction.drop(60)
predicted_stock_price_del   = np.delete(predicted_stock_price, [0,1],0)

df_prediction['PREDICTED']  = predicted_stock_price_del
df_prediction['ACT_RET']    = df_prediction['ACTUAL'].pct_change()
df_prediction['PRD_RET']    = df_prediction['PREDICTED'].pct_change()
correlation                 = df_prediction['ACT_RET'].corr(df_prediction['PRD_RET'])





print(' ')
print('Correlation is: ', correlation)
print(' ')

position = [0]

for i in range(1,len(df_prediction)):
    if df_prediction.iloc[i, 4] >0:
        position.append(1)
    elif df_prediction.iloc[i, 4] <0:
        position.append(-1)

df_prediction['POSITION'] = position

print(' ')
print(df_prediction)
print(' ')


df_prediction.to_csv(root + '/' + 'TRIAL_ML_STRATEGY - ' + TICKER_CSV + '.csv') 
df_date = df.loc[data_avail+1:(len(df)-2), 'Date']
df_act = dataset_test.iloc[1:-1 , 0]
df_res = predicted_stock_price_del


# Visualising the results
plt.plot(df_date,df_act, color = 'red', label = 'Real '+TICKER_CSV+' Stock Price')
plt.plot(df_date,df_res, color = 'blue', label = 'Predicted '+TICKER_CSV+' Stock Price')
plt.xticks(np.arange(0,data_remain,50))
plt.title(''+TICKER_CSV+' Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel(''+TICKER_CSV+' Stock Price')
plt.legend()
plt.show()

