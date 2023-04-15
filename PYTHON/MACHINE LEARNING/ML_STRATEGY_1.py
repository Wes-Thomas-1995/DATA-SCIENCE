import conf
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM

import math
import os
import sys


import numpy as np


def get_raw_xy(data):
    data = data.drop(columns=['Date', 'Adj Close'])
    values=data.values
    
    return values[:, [0,1,2,3,4]], values[:, 3]




def train_test_split(X, Y, trs_len=0.80):
    lx=len(X)
    trs=int(lx*trs_len)
    train_x, train_y = X[:trs], Y[:trs]
    test_x, test_y = X[trs:], Y[trs:]
    return train_x, train_y, test_x, test_y


def get_vpo(values):
    shifted_y = list(values)
    








def get_lstm(batches, input_shape):
    
    model = Sequential()
    model.add(LSTM(60, input_shape=input_shape, stateful=True, batch_input_shape=(batches, input_shape[0], input_shape[1])))
    model.add(Dense(1))
    return model

confs={'default': dict(model=get_lstm)}


def train_model(name, train_x, train_y, epochs, batches, test_x, test_y):
    mparams=confs[name]
    model=mparams['model'](batches, (train_x.shape[1], train_y.shape[2]))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse', 'mape'])
    history=model.fit(train_x, train_y, verbose=2, epochs=epochs, batch_size=batches, validation_data=(test_x, test_y), shuffle=False)
    return model, name, mparams, history