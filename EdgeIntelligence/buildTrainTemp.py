import json
import os
import traceback
#from matplotlib import pyplot as plt for statistics
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import BatchNormalization


###################################   DEF   ##############################################
""" def visualize_loss(history, title):
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    epochs = range(len(loss))
    plt.figure()
    plt.plot(epochs, loss, "b", label="Training loss")
    plt.plot(epochs, val_loss, "r", label="Validation loss")
    plt.title(title)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.yticks(np.arange(0, 5, 0.0050))
    plt.show() 
    STATISTICS"""


def createDataset(X, y, n_samples):
    X_res, y_res = [], []
    for i in range(len(X) - n_samples):
        v = X.iloc[i:(i + n_samples)].values
        X_res.append(v)
        y_res.append(y.iloc[i + n_samples])

    return np.array(X_res), np.array(y_res)
"""reshaping method"""


def normalizeTime(month, day, hour, minute):
    scaledMonth= 2*np.pi*(month/12.0)
    scaledDay= 2*np.pi*(day/31.0)
    scaledHour= 2*np.pi*(hour/23.0)
    scaledMinute= 2*np.pi*(minute/59.0)
    
    filteredDataset['monthSin'] = np.sin(scaledMonth)
    filteredDataset['monthCos'] = np.cos(scaledMonth)
    filteredDataset['daySin'] = np.sin(scaledDay)
    filteredDataset['dayCos'] = np.cos(scaledDay)
    filteredDataset['hourSin'] = np.sin(scaledHour)
    filteredDataset['hourCos'] = np.cos(scaledHour)
    filteredDataset['minuteSin'] = np.sin(scaledMinute)
    filteredDataset['minuteCos'] = np.cos(scaledMinute)
"""adding cyclic features beahaviour for handling the time"""


def normalizeDataset():
    scaler = StandardScaler()
    standardizedXTrain = pd.DataFrame(scaler.fit_transform( XTrain ), columns = XTrain.columns)

    return standardizedXTrain
"""normalizing dataset"""


####################################  CODE   ############################################
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

if tf.test.gpu_device_name():
    print('GPU found')
else:
    print("No GPU found")


datasetPath = "smartBuildingResources/datasets/temperature.csv"
try:
    initialDataset= pd.read_csv(datasetPath, ",")

except Exception as e:
    print(traceback.format_exc())
    print(e)
    print("Temp Training Error -> Cannot access the temperature dataset")
"""loading dataset"""


try:
    with open("smartBuildingResources/tfconfig.json") as json_file:
        json_object = json.load(json_file)
    epochs=json_object["epochs"]
    neuronsLayer1=json_object["neuronsLayer1"]
    neuronsLayer2=json_object["neuronsLayer2"]
    nSamples=50
    print("Number of epochs -> "+ str(epochs))
    print("Number of neurons for the first layer -> " + str(neuronsLayer1))
    print("Number of neurons for the second layer -> " + str(neuronsLayer2))

except Exception as e:
    print(traceback.format_exc())
    print(e)
    print("Temp Training Error -> Cannot access the configuration file")
"""configuration parameters"""


cols = ['year', 'month', 'day', 'hour', 'minute', 'recnt_Humidity', 'recnt_Temperature', 'Target_Temperature']
filteredDataset=initialDataset[cols]
"""filtring data removing year and seconds that are the same for all the entries of the dataset"""


model=None
"""definition of the model"""


normalizeTime(filteredDataset["month"],filteredDataset["day"],filteredDataset["hour"],filteredDataset["minute"])
"""adding cyclic features beahaviour for handling the time"""


colsX = ['year','monthSin', 'monthCos', 'daySin', 'dayCos', 'hourSin', 'hourCos','minuteSin', 'minuteCos', 'recnt_Humidity', 'recnt_Temperature']
colsY = ['Target_Temperature']
dataX= filteredDataset.loc[:,colsX]
dataY= filteredDataset.loc[:,colsY]
XTrain,XTest,YTrain,YTest = train_test_split(dataX,dataY,test_size=0.4,random_state=42)
"""split dataset in training data and test data"""


standardizedXTrain = normalizeDataset() 
"""Standardize the training dataset"""


train_x, train_y = createDataset(standardizedXTrain, dataY, nSamples)
"""reshape the input/output dataframe for training"""


print('Building model...')
regularizer=tf.keras.regularizers.L2(l2=0.2)
# train a 2-layer LSTM with one output layer
try:
    model = Sequential(name='Sequential_input')
    model.add(LSTM(int(neuronsLayer1), implementation=2, kernel_initializer='glorot_uniform', kernel_regularizer=regularizer, return_sequences=True, dropout=0.4, recurrent_dropout=0.4, name='LSTM_layer1')) # layer1
    model.add(BatchNormalization(name='BatchNorm_layer1'))
    model.add(LSTM(int(neuronsLayer2), implementation=2, kernel_initializer='glorot_uniform', kernel_regularizer=regularizer, return_sequences=False, dropout=0.2, recurrent_dropout=0.2, name='LSTM_layer2')) # layer2
    model.add(BatchNormalization(name='BatchNorm_layer2'))
    model.add(Dense(1, activation='linear', kernel_initializer='glorot_uniform', name='Dense_output')) #output layer

    opt = tf.keras.optimizers.SGD(learning_rate=0.3)
    model.compile(loss='mean_squared_logarithmic_error', optimizer=opt, metrics=['msle'])

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Temp Training Error -> Cannot build the network")
"""Building"""


try:
    early_stopping = EarlyStopping(monitor='val_loss', patience=15)
    model_checkpoint = ModelCheckpoint('checkpointTemp/'+'model_temp_{epoch:02d}-{val_loss:.2f}.h5', monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=False, mode='auto')
    lr_reducer = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, verbose=0, mode='auto', min_delta=0.0001, cooldown=0, min_lr=0)

    print('Training model...')
    history=model.fit(train_x, train_y, validation_split=0.2, verbose=2, callbacks=[early_stopping, model_checkpoint, lr_reducer],batch_size=128, epochs=int(epochs), shuffle=True)
    model.summary()
    # visualize_loss(history, "best configuration") for statistics

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Temp Training Error -> Cannot train the network")
"""Training"""

