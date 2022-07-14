import json
import os
import traceback
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import glob


###################################   DEF   ##############################################

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
    standardizedXTest = pd.DataFrame(scaler.fit_transform( XTest ), columns = XTest.columns)

    return standardizedXTest
"""Normalization of the dataset"""


def getBestModel():
    file_path = 'smartBuildingResources/checkpointHum/*.h5'
    try:
        files = sorted(glob.iglob(file_path), key=os.path.getctime, reverse=True)
        if (len(files)>=1):
            return files[0]

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot retrieve the best model for the prediction")
"""Getting the best trained model"""


####################################  CODE   ############################################
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

if tf.test.gpu_device_name():
    print('GPU found')
else:
    print("No GPU found")

datasetPath = "smartBuildingResources/datasets/humidity.csv"
try:
    initialDataset= pd.read_csv(datasetPath, ",")
except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot retrieve the humidity dataset")
"""loading dataset"""


nSamples=50
"""configuration parameters"""


cols = ['year','month', 'day', 'hour', 'minute', 'recnt_Humidity', 'recnt_Temperature', 'Target_Humidity']
filteredDataset=initialDataset[cols]
"""filtring data removing year and seconds that are the same for all the entries of the dataset"""


normalizeTime(filteredDataset['month'], filteredDataset['day'],filteredDataset['hour'], filteredDataset['minute'])
"""normalize Time"""


colsX = ['year','monthSin', 'monthCos', 'daySin', 'dayCos', 'hourSin', 'hourCos','minuteSin', 'minuteCos', 'recnt_Humidity', 'recnt_Temperature']
colsY = ['Target_Humidity']
dataX= filteredDataset.loc[:,colsX]
dataY= filteredDataset.loc[:,colsY]
XTrain,XTest,YTrain,YTest = train_test_split(dataX,dataY,test_size=0.4,random_state=42)
"""split dataset in training data and test data"""


standardizedXTest = normalizeDataset()
test_x, test_y = createDataset(standardizedXTest, dataY, nSamples)
"""Normalization and creation of input/output dataframe"""


try:
    bestModel = tf.keras.models.load_model(getBestModel())

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot load the best model")
"""Loading of the best model"""


print("Starting Evaluation")
try:
    evaluationResults = bestModel.evaluate(test_x,test_y)
    print("test loss, test accuracy:", evaluationResults)

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot perform the evaluation of the network")
"""Evaluation"""


print("Starting Prediction")
try:
    result=np.mean(bestModel.predict(test_x))
    formattedResult="%.2f" % result
    print("Humidity Predicted -> " + formattedResult)

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot perform the prediction of hte network")
"""Prediction"""


try:
    with open("smartBuildingResources/results.json") as json_input:
        json_object = json.load(json_input)
    json_object["predictedHumidity"] = float(formattedResult)
    with open('smartBuildingResources/results.json', 'w') as json_output:
        json.dump(json_object, json_output, indent=4)

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Hum Prediction Error -> Cannot access the results file")
"""Writing on results.json the result of the prediction to be transferred"""


""" bestModel = tf.keras.models.load_model(getBestModel())
converter = tf.lite.TFLiteConverter.from_keras_model(bestModel)
tflite_model = converter.convert()

 #Save the model.
with open('checkpointHum/model.tflite', 'wb') as f:
  f.write(tflite_model)
testX1 = np.array(standardizedXTest) # convert to a numpy array
testX1 = np.expand_dims(testX1, 0) # change shape return a single value instead of a vectori
result=tflite_model.predict(testX1)
#TFLite Option """

