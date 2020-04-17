import argparse
from flask import Flask,request,jsonify
import pickle
import requests
import threading 
import time
import os
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
KAFKA_IP = None
KAFKA_PORT = None

institueToCameraPickle = "./institueToCamera.p"
institueToCamera = {}
newCamerasAdded = 0
cameraThreshould = 10

institueToImagePickle = './institueToImage.p'
institueToImage = {}
newImageAdded = 0
ImageThreshould = 10

instituteCamerasOnStream = {}

class Camera :
	def __init__(cameraID) :
		self.cameraID = cameraID

	def getCameraID() :
		return cameraID

def initialiseInstituteCamerasOnStream() :
	for camera in institueToCamera.keys() : 
		instituteCamerasOnStream[camera] = False

def loadPickleToDictionary(file, dictionary) :
	with open(file, 'rb') as fp:
    	dictionary = pickle.load(fp)

def inititalizeInstituteToCamera() :
	if(len(institueToCamera) == 0 ) :
		if(os.path.isfile(institueToCameraPickle)) :
			loadPickleToDictionary(institueToCameraPickle, institueToCamera)
			initialiseInstituteCamerasOnStream()

def dumpDictionaryToPickle(dictionary, file) :
	with open(file, 'wb') as fp:
    	pickle.dump(dictionary, fp, protocol=pickle.HIGHEST_PROTOCOL)

def validateAddCameraInput(content) :
	returnValue = 'INVALID_INPUT'
	if 'institue_id' in content :
		if 'cameras' in content['institue_id'] :
			if 'camera_id' in content['institue_id']['cameras'] and 'room_id' in content['institue_id']['cameras'] :
				returnValue = 'sucess' 
			
	return returnValue 

def ifExist( key, newCamera) :
	returnValue = 'success'
	if key in institueToCamera and institueToCamera[key] == newCamera :
		returnValue = 'DUPLICATE_ELEMENT' 

	return returnValue

def createKafkaTopic(topicName) :
	admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_IP + ":" + KAFKA_PORT)
	topic_list = []
	topic_list.append(NewTopic(name=topicName, num_partitions=1, replication_factor=1))
	admin_client.create_topics(new_topics=topic_list, validate_only=False)


@app.route('/institue/add_camera', methods=['GET', 'POST'])
def add_camera():
    content = request.json

    errorCode = 'success'

    errorCode = validateAddCameraInput(content)

    if(errorCode != 'success') : #add code to update log file
    	print("add_camera : " + errorCode)
    	return 

    institueID = content['institue_id']

    inititalizeInstituteToCamera()

    for camera in content['cameras'] :
    	cameraID = institueID + "_" + content['cameras']['room_id'] + "_" content['cameras']['camera_id'] 
    	keyToCamera = institueID + "_" + content['cameras']['room_id']
    	camera = Camera(cameraID) 
    	errorCode = ifExist(keyToCamera, camera)
    	if errorCode == 'success' :
    		institueToCamera[keyToCamera] = cameraID 
    		createKafkaTopic(keyToCamera) 
    		instituteCamerasOnStream[keyToCamera] = False
    		newCamerasAdded += 1 
    		if(newCamerasAdded == cameraThreshould) :
    			dumpDictionaryToPickle(institueToCamera, institueToCameraPickle)
    			newCamerasAdded = 0 
    	else :
    		print("add_camera : " + errorCode + " for value " + content['cameras']['camera_id'])




    """
    content
	{
		"institue_id":1213,
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
    	Generate Unique ID For Every Camera Instance as institueid concatenated with room_no
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
	if "institue_id" in content and "room_id" in content :
		returnValue = 'success'

	return returnValue

@app.route('/institue/get_camera_instance', methods=['GET', 'POST'])
def get_camera_instance():
    content = request.json

    errorCode = 'success'

    errorCode = validateGetCameraInput(content)

    if errorCode != 'success' :
    	print("get_camera_instance : " + errorCode)
    	returnValue =  errorCode
    else :
	    inititalizeInstituteToCamera()
	    key = content['institue_id'] + "_" + content["room_id"]

	    if key in institueToCamera :
			returnValue = institueToCamera[key].getCameraID()
		else :
			returnValue = "Not initialized"

	return returnValue
    """
    input
    {
    	"institue_id":"ins id"
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
	if "institue_id" in content and "unique_id" in content :
		returnValue = 'success'

	return returnValue

def streamImages(producer, topicName) :
	instituteCamerasOnStream[topicName] = True
	lastImageSent = "" 
	while True :
		if instituteCamerasOnStream[topicName] :
			if lastImageSent != institueToImage[topicName] :
				lastImageSent = institueToImage[topicName]
				producer.send(topicName, lastImageSent) 
		else :
			break

		sleep(5)

@app.route('/institue/start_fetching', methods=['GET', 'POST'])
def start_fetching():
    content = request.json

    errorCode = validateStartFetchingInput(content)

    if errorCode == 'success' :
    	topicName = content["unique_id"]
    	producer = KafkaProducer(bootstrap_servers=KAFKA_IP + ":" + KAFKA_PORT)
    	thread = threading.Thread(target=streamImages, args=(producer, topicName,))
    	thread.start()

    else :
    	print("start_fetching : " + errorCode)
    """ 
    input
    {
    	"institue_id":"ins_id"
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
    returnValue = {"Response : ERROR"}
    if errorCode == 'success' :
    	returnValue = {"Response : OK"}
   
    return returnValue

def validateUploadImageInput(content) :
	returnValue = 'INVALID_INPUT'
	if 'image' in content :
		returnValue = 'success'

	return returnValue

@app.route('/upload_image/<unique_id>', methods=['GET', 'POST'])
def upload_image(unique_id):
    content = request.json

    errorCode = 'success'
    errorCode = validateUploadImageInput(content)

    if(errorCode == 'success'):
    	institueToImage[unique_id] = content['image']
    	newImageAdded += 1
    	if newImageAdded == ImageThreshould :
    		dumpDictionaryToPickle(institueToImage, institueToImagePickle)
    		newImageAdded = 0
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
    returnValue = {"Response : ERROR"}
    if errorCode == 'success' :
    	returnValue = {"Response : OK"}
   
    return returnValue

def validateStopFecthingInput(content) :
	returnValue = 'INVALID_INPUT'
	if "institue_id" in content and "unique_id" in content :
		errorCode = 'success'

	return returnValue

@app.route('/institue/stop_fetching', methods=['GET', 'POST'])
def stop_fetching() :
	"""
	input
    {
    	"institue_id":"ins_id"
    	"unique_id":"unique_id"
    }
    """
    content = request.json
    errorCode = validateStopFecthingInput(content)

    if errorCode == 'success' :
    	instituteCamerasOnStream[topicName] = False
    else :
    	print("stop_fetching : " + errorCode)

corporateToCameraPickle = "./corporateToCamera.p"
corporateToCamera = {}
newCorporateCamerasAdded = 0
corporateCameraThreshould = 10

corporateToImagePickle = './corporateToImage.p'
corporateToImage = {}
newCorporateImageAdded = 0
corporateImageThreshould = 10

corporateCamerasOnStream = {}

def validateAddCameraCorporateInput(content) :
	returnValue = 'INVALID_INPUT'

	if "corporate_id" in content and "cameras" in content :
		if "camera_id" in content["cameras"][0] and "type" in content["cameras"][0] :
			if "camera_id" in content["cameras"][1] and "type" in content["cameras"][1] :
				returnValue = 'success'

	return returnValue

def inititalizeCorporateToCamera() :
	if(len(corporateToCamera) == 0 ) :
		if(os.path.isfile(corporateToCameraPickle)) :
			loadPickleToDictionary(corporateToCameraPickle, corporateToCamera)
			initialiseCorporateCamerasOnStream()

def initialiseCorporateCamerasOnStream() :
	for camera in corporateToCamera.keys() : 
		corporateCamerasOnStream[camera] = False

@app.route('/corporate/add_camera', methods=['GET', 'POST'])
def add_camera_corporate():
    content = request.json

    errorCode = validateAddCameraCorporateInput(content)

    if errorCode == 'success' :
    	inititalizeCorporateToCamera()

    	keyIN = content["corporate_id"] + "_in"
    	keyOUT = content["corporate_id"] + "_out"
    	inValue = ""
    	outValue = ""

    	if content["cameras"][0]["type"] == "in" :
    		inValue = content["cameras"][0]["camera_id"]
    	else :
    		inValue = content["cameras"][1]["camera_id"]

    	if content["cameras"][0]["type"] == "out" :
    		outValue = content["cameras"][0]["camera_id"]
    	else :
    		outValue = content["cameras"][1]["camera_id"]

    	corporateToCamera[keyIN] = Camera(inValue)
    	corporateToCamera[keyOUT] = Camera(outValue)

    	createKafkaTopic(keyIN)
    	createKafkaTopic(keyOUT)

    	corporateCamerasOnStream[keyIN] = False
    	corporateCamerasOnStream[keyOUT] = False

    	newCorporateCamerasAdded += 2 
    	if newCorporateCamerasAdded == corporateCameraThreshould :
    		dumpDictionaryToPickle(corporateToCamera, corporateToCameraPickle)
    		newCorporateCamerasAdded = 0
    else :
    	print("add_camera_corporate : " + errorCode)

    """
    content
	{
		"corporate_id":1213,
		"cameras" :[
					{
					"camera_id":21323,
					"type":"in"
					},
					{
					"camera_id":1332,
					"type":"out",
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
    returnValue = {"Response" : "OK"}
    if errorCode != 'success' :
    	returnValue = {"Response" : "ERROR"}
    
    return returnValue

# def data_fetching_corporate(type,corporate_id,unique_id):
	# while True:
		"""
			if type == in:
				get latest data for unique id and put it in corporate_id_in topic
			else:
				in corporate_id_out topic
		"""

def validateStartFetchingCorporateInput(content) :
	returnValue = 'INVALID_INPUT'
	if "corporate_id" in content and "unique_id" in content :
		returnValue = 'success'

	return returnValue

def streamCorporateImages(producer, topicName) :
	corporateCamerasOnStream[topicName] = True 
	lastImageSent = "" 
	while True :
		if corporateCamerasOnStream[topicName] :
			if lastImageSent != corporateToImage[topicName] :
				lastImageSent = corporateToImage[topicName]
				producer.send(topicName, lastImageSent) 
		else :
			break

		sleep(5)

@app.route('/corporate/start_fetching', methods=['GET', 'POST'])
def start_fetching_corporate():
    content = request.json

    errorCode = validateStartFetchingCorporateInput(content)

    if errorCode == 'success' :
    	topicName = content["unique_id"]
    	producer = KafkaProducer(bootstrap_servers=KAFKA_IP + ":" + KAFKA_PORT)
    	thread = threading.Thread(target=streamCorporateImages, args=(producer, topicName,))
    	thread.start()

    else :
    	print("start_fetching : " + errorCode)
    """
    input
    {
    	"corporate_id":"ins_id"
    	"unique_id":"unique_id"
    }
    """
    """
    	create a thread which puts data in kakfa topic(corporate_id_in or corporate_id_out)
    """
    """
	    output

	    {
			"Response Ok":"OK"
	    }

    """
    returnValue = {"Response : ERROR"}
    if errorCode == 'success' :
    	returnValue = {"Response : OK"}
   
    return returnValue

def validateUploadCorporateImageInput(content) :
	returnValue = 'INVALID_INPUT'
	if "image" in content : 
		returnValue = 'success'

	return returnValue

@app.route('/upload_corporate_image/<unique_id>', methods=['GET', 'POST'])
def upload_corporate_image(unique_id):
    content = request.json

    errorCode = 'success'
    errorCode = validateUploadCorporateImageInput(content)

    if(errorCode == 'success'):
    	corporateToImage[unique_id] = content['image']
    	newCorporateImageAdded += 1
    	if newCorporateImageAdded == corporateImageThreshould :
    		dumpDictionaryToPickle(corporateToImage, corporateToImagePickle)
    		newCorporateImageAdded = 0
    else :
    	print("upload_corporate_image : " + errorCode)


    """
    content input
    {
	"image":"string"
    }
    """
    
    """
    	put the latest image in your data structure
    """
    returnValue = {"Response : ERROR"}
    if errorCode == 'success' :
    	returnValue = {"Response : OK"}
   
    return returnValue

def validateGetCorporateCameraInput(content) :
	returnValue = 'INVALID_INPUT'
	if "corporate_id" in content and "type" in content :
		returnValue = 'success'

	return returnValue

@app.route('/institue/get_corporate_camera_instance', methods=['GET', 'POST'])
def get_corporate_camera_instance():
    content = request.json

    errorCode = 'success'

    errorCode = validateGetCorporateCameraInput(content)

    if errorCode != 'success' :
    	print("get_corporate_camera_instance : " + errorCode)
    	returnValue =  errorCode
    else :
	    inititalizeInstituteToCamera()
	    key = content['corporate_id'] + "_" + content["type"]

	    if key in corporateToCamera :
			returnValue = institueToCamera[key].getCameraID()
		else :
			returnValue = "Not initialized"

	return returnValue
    """
    input
    {
    	"corporate_id":"ins id"
    	"type":"room id"
    }
    """
    """
	    output

	    {
			"topic":UNIQUE ID YOU GENERATED
	    }

    """
    # return OUTPUT

def validateStopCorporateFetchingInput(content) :
	returnValue = 'INVALID_INPUT'
	if "corporate_id" in content and "unique_id" in content :
		returnValue = 'success' 

	return returnValue

@app.route('/institue/stop_corporate_fetching', methods=['GET', 'POST'])
def stop_corporate_fetching() :
	"""
    input
    {
    	"corporate_id":"ins_id"
    	"unique_id":"unique_id"
    }
    """
    content = request.json
    errorCode = validateStopCorporateFecthingInput(content)

    if errorCode == 'success' :
    	corporateCamerasOnStream[topicName] = False
    else :
    	print("stop_corporate_fetching : " + errorCode)

def data_dumping_service():
	while True:
		time.sleep(60) #wait for 1 minute then upload data in registry
		data = {"institue":institue_data,"corporate":"corporate_data"}
		res = requests.post('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/store/query_manager', json=data)


if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	ap.add_argument("-k", "--kafka_ip", required=True)
	ap.add_argument("f", "--kafka_port", required=True)
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
	app.run(debug=True,port=int(args["port"])) 