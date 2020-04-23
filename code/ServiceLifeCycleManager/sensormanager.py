import argparse
from flask import Flask,request,jsonify
import pickle
import requests
import threading 
import time
import os
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
import json
from json import dumps
import time

app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
KAFKA_IP = None
KAFKA_PORT = None

instituteToCamera = {}

instituteToImage = {}

instituteCamerasOnStream = {}

class Camera :
    def __init__(self, cameraID) :
        self.cameraID = cameraID

    def getCameraID(self) :
        return self.cameraID

def validateAddCameraInput(content) :
    returnValue = 'INVALID_INPUT'
    if 'institute_id' in content :
        if 'cameras' in content :
            for cameraInstance in content['cameras'] :
                if 'camera_id' in cameraInstance and 'room_id' in cameraInstance :
                    returnValue = 'success' 
            
    return returnValue 


def createKafkaTopic(topicName) :
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=["localhost:9092"])
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        topic_list = []
        topic_list.append(NewTopic(name=topicName, num_partitions=1, replication_factor=1))
    except:
        pass


@app.route('/institute/add_camera', methods=['GET', 'POST'])
def add_camera(): 
    print("+ REQUEST TO ADD INSTITUTE CAMERA")
    global instituteToCamera,instituteCamerasOnStream
    content = request.json

    errorCode = 'success'

    errorCode = validateAddCameraInput(content)

    if(errorCode != 'success') : 
        return {"Response" : "ERROR"}

    instituteID = str(content['institute_id'])

    for camera in content['cameras'] :

        cameraID = instituteID + "_" + str(camera['room_id']) + "_" + str(camera['camera_id'])
        keyToCamera = instituteID + "_" + str(camera['room_id'])
        if errorCode == 'success' :
            instituteToCamera[keyToCamera] = cameraID
            print("keyToCamera ",keyToCamera," unique key ",cameraID)
            # createKafkaTopic(keyToCamera) 
            instituteCamerasOnStream[keyToCamera] = False
        else :
            print("add_camera : " + errorCode + " for value " + str(camera['camera_id']))




    """
    content
    {
        "institute_id":1213,
        "cameras" :[
                    {
                    "camera_id":21323,
                    "room_id":213
                    },
                    {
                    "camera_id":1332,
                    "room_id",213,
                    }
            ]
    }
    """
    """
        Generate Unique ID For Every Camera Instance as instituteid concatenated with room_no
            as   iiit13:sh1
    """
    """
        output

        cameras_unique_ids = [id1,id2]
    """
    returnValue = {"Response" : "OK"}
    if errorCode != 'success' :
        returnValue = {"Response" : "ERROR"}
    
    return returnValue

def validateGetCameraInput(content) :
    returnValue = 'INVALID_INPUT'
    if "institute_id" in content and "room_id" in content :
        returnValue = 'success'

    return returnValue

@app.route('/institute/get_camera_instance', methods=['GET', 'POST'])
def get_camera_instance():
    global instituteToCamera
    content = request.json

    errorCode = 'success'

    errorCode = validateGetCameraInput(content)

    if errorCode != 'success' :
        returnValue =  errorCode
    else :
        key = str(content['institute_id']) + "_" + str(content["room_id"])
        print("get camera instance for key ",key)
        if key in instituteToCamera.keys():
            returnValue = instituteToCamera[key]
        else :
            returnValue = "Not initialized"

    return {"topic":returnValue}
    """
    input
    {
        "institute_id":"ins id"
        "room_id":"room id"
    }
    """
    """
        output

        {
            "topic":UNIQUE ID YOU GENERATED
        }

    """
    # return OUTPUT

# def data_fetching(topic):
    # consumer = KafkaConsumer(bootstrap_servers="KAFKA_IP + ":" + KAFKA_PORT")


    """
    definition for kafka producer
    """
    # while True:
    """
            if there is reuest for this topic then
            put latest image for this topic in the kafka topic(unique id) 
    """
def validateStartFetchingInput(content) :
    returnValue = 'INVALID_INPUT'
    if "institute_id" in content and "unique_id" in content :
        returnValue = 'success'

    return returnValue

def streamImages(producer, topicName) :
    global instituteToImage,instituteCamerasOnStream
    instituteCamerasOnStream[topicName] = True
    lastImageSent = "" 
    while True :
        # print("Fetching Image")
        if instituteCamerasOnStream[topicName] :
            if lastImageSent != instituteToImage[topicName] :
                print("PUSHING NEW IMAGE")
                lastImageSent = instituteToImage[topicName]
                data = {"image":lastImageSent}
                producer.send(topicName, value=data) 
        else :
            break

        time.sleep(5)
@app.route('/health')
def health():
    return {"res":"live"}
@app.route('/institute/start_fetching', methods=['GET', 'POST'])
def start_fetching():
    global instituteToImage
    content = request.json

    errorCode = validateStartFetchingInput(content)

    if errorCode == 'success' :
        topicName = content["unique_id"]
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"],value_serializer=lambda x:dumps(x).encode('utf-8'))
        thread = threading.Thread(target=streamImages, args=(producer, topicName,))
        thread.start()

    else :
        print("start_fetching : " + errorCode)
    """ 
    input
    {
        "institute_id":"ins_id"
        "unique_id":"unique_id"
    }
    """
    """
        create a thread which puts data in kakfa topic(unique id)
    """
    """
        output

        {
            "Response Ok":"OK"
        }

    """
    returnValue = {"Response" : "ERROR"}
    if errorCode == 'success' :
        returnValue = {"Response" : "OK"}
   
    return returnValue

def validateUploadImageInput(content) :
    returnValue = 'INVALID_INPUT'
    if 'image' in content :
        returnValue = 'success'

    return returnValue

@app.route('/upload_image/<unique_id>', methods=['GET', 'POST'])
def upload_image(unique_id):
    global instituteToImage
    # print("REQUEST TO UPLOAD IMAGE FOR CAMERA ",unique_id)
    content = request.json

    errorCode = 'success'
    errorCode = validateUploadImageInput(content)

    if(errorCode == 'success'):
        instituteToImage[unique_id] = content['image']
    else :
        print("upload_image : " + errorCode)


    """
    content input
    {
    "image":"string"
    }
    """
    
    """
        put the latest image in your data structure
    """
    returnValue = {"Response" : "ERROR"}
    if errorCode == 'success' :
        returnValue = {"Response" : "OK"}
    # print(returnValue)
    return returnValue



@app.route('/institute/stop_fetching', methods=['GET', 'POST'])
def stop_fetching() :
    print("REQUEST TO STOP FETCHING ")
    global instituteCamerasOnStream
    """
    input
    {
        "institute_id":"ins_id"
        "unique_id":"unique_id"
    }
    """
    content = request.json

    instituteCamerasOnStream[content["unique_id"]] = False
    
    return {"res":"ok"}



corporates_registered_with_topics={}
corporate_images_for_topic={}
def streamImagesForCorporate(producer,topicName):
    global corporate_images_for_topic
    prev_image = ""
    while True:
        if prev_image == corporate_images_for_topic[topicName]:
            print("NO NEW IMAGE ",topicName)
        else:
            print("new iamge")
            prev_image = corporate_images_for_topic[topicName]
            data = {"image":prev_image}
            producer.send(topicName, value=data)
        time.sleep(4)

@app.route('/corporate/upload_image_corporate/<kafkaTopic>', methods=['GET', 'POST'])
def upload_image_corporate(kafkaTopic):
    global corporate_images_for_topic,corporates_registered_with_topics
    content = request.json
    print(kafkaTopic)
    if kafkaTopic in corporates_registered_with_topics:
        print("UPLOADED")
        corporate_images_for_topic[kafkaTopic] = content["image"]
    return {"res":"ok"}

@app.route('/corporate/add_camera', methods=['GET', 'POST'])
def add_camera_corporate():
    global corporates_registered_with_topics
    content = request.json
    corporate_id = content["corporate_id"]
    camera_id = content["cameras"][0]["camera_id"]
    type_ = content["cameras"][0]["type"]

    kafkaTopic = corporate_id+"_"+type_
    print("KAFKA TOPIC ",kafkaTopic)
    if kafkaTopic not in corporates_registered_with_topics.keys():
        corporates_registered_with_topics[kafkaTopic]=True
        corporate_images_for_topic[kafkaTopic]=""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"],value_serializer=lambda x:dumps(x).encode('utf-8'))
        thread = threading.Thread(target=streamImagesForCorporate, args=(producer, kafkaTopic,))
        thread.start()

    print("HERE ")
    return {"camera_UID":kafkaTopic}

    """
    content
    {
        "corporate_id":1213,
        "cameras" :[
                    {
                    "camera_id":21323,
                    "type":"in"
                    }
            ]
    }
    """
    """
        Generate Unique ID For Every Camera Instance and store it in 
        your data base as key=corporate_id concatenated with camera_id
        and value is ur generated Unique camera id and also store whether it
        is in type or out type
    """
    """
        output

        cameras_unique_ids = [id1,id2]
    """

def data_dumping_service():
    while True:
        time.sleep(60) #wait for 1 minute then upload data in registry
        data = {"institute":institute_data,"corporate":"corporate_data"}
        res = requests.post('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/store/query_manager', json=data)


if __name__ == "__main__": 
    ap = argparse.ArgumentParser()
    ap.add_argument("-p","--port",required=True)
    # ap.add_argument("-i","--registry_ip",required=True)
    # ap.add_argument("-x","--registry_port",required=True)
    # ap.add_argument("-k", "--kafka_ip", required=True)
    # ap.add_argument("f", "--kafka_port", required=True)
    args = vars(ap.parse_args())       
    
    """
    REGISTRY_IP = args["registry_ip"]
    REGISTRY_PORT = args["registry_port"]

    res = requests.get('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/fetch/query_manager')
    data = res.json()
    //inititalize you data
    t1 = threading.Thread(target=data_dumping_service) 
    t1.start()
    """
    app.run(debug=True,host = "0.0.0.0",port=int(args["port"])) 

    