import json
import os
import glob
import datetime
import runpy
import traceback
from paho.mqtt.client import Client


###################################   DEF   ##############################################

def trainHum():       
    files = glob.iglob('checkpointHum/*')
    for f in files:
        os.remove(f)
    try:
        runpy.run_path("buildTrainHum.py")
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Impossible to start the building and the training of the network, please contact the admin")


def trainTemp():       
    files = glob.iglob('checkpointTemp/*')
    for f in files:
        os.remove(f)
    try:
        runpy.run_path("buildTrainTemp.py")

    except Exception as e:
        print(traceback.format_exc())
        print(e)    
        print("Main Error -> Impossible to start the building and the training of the network, please contact the admin")


def predictHum():  
    try:
        runpy.run_path("evaluatePredictHum.py")

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Impossible to start the evaluation and the prediction of the network, please contact the admin")


def predictTemp():  
    try:
        runpy.run_path("evaluatePredictTemp.py")

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Impossible to start the evaluation and the prediction of the network, please contact the admin")


def getResults():
    try:
        with open("results.json") as json_file:
            json_object=json.load(json_file)
            result=json.dumps(json_object)
            return result

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Cannot access the results of the prediction")


def sendResults(results):
    broker = "broker.hivemq.com"
    port=1883
    topic= "data/tensor/"+str(userFloor)+"/"+str(userApartment)
    client= Client(client_id="EdgeDeviceSlave#"+str(clientId))

    try:
        output=client.connect(broker, port)
        print(output)
        print(results)
        pub=client.publish(topic, results)
        print(pub)

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Cannot connect to the network")


def setTrainingExecution():
    try:
        with open("smartBuildingResources/tfconfig.json") as json_input:
            json_object = json.load(json_input)
        json_object["trainingExecution"] = False
        with open('smartBuildingResources/tfconfig.json', 'w') as json_output:
            json.dump(json_object, json_output, indent=4)

    except Exception as e:
            print(traceback.format_exc())
            print(e)
            print("Main Error -> Cannot modify the configuration file")


def main():
    now = datetime.datetime.now()
    if ((now.day == 1 and now.hour == 0 and 0<=now.minute<=1) or trainingExecution == True):
        trainHum()
        trainTemp()
        setTrainingExecution()
    predictHum()
    predictTemp()
    result=getResults()
    sendResults(result)
    


####################################  MAIN   ############################################
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

try:
    with open("smartBuildingResources/tfconfig.json") as json_file:
        json_object = json.load(json_file)
    trainingExecution=json_object["trainingExecution"]
    with open("smartBuildingResources/mqttconfig.json") as json_file:
        json_object = json.load(json_file)
    userApartment=json_object["userApartment"]
    userFloor=json_object["userFloor"]
    clientId=json_object["clientId"]

except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("Main Error -> Cannot access the configuration file")


if __name__ == "__main__":
    main()