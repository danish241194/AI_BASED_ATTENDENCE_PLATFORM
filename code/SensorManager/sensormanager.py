import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
@app.route('/institue/add_camera', methods=['GET', 'POST'])
def add_camera():
    content = request.json
    """
    content
	{
		"institue_id":1213,
		"cameras" :[
					{"camera_id":21323,
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
    	Generate Unique ID For Every Camera Instance and store it in 
    	your data base as key=institue id concatenated with room no
    	and value is ur generated Unique camera id
    	"""
    """
		output

		cameras_unique_ids = [id1,id2]
    """
    return {"Response":"OK/ERROR"}


@app.route('/institue/get_camera_instance', methods=['GET', 'POST'])
def get_camera_instance():
    content = request.json
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
    return OUTPUT

def data_fetching(topic):
	"""
	definition for kafka producer
	"""
	while True:
		"""
			if there is reuest for this topic then
			put latest image for this topic in the kafka topic(unique id) 
		"""
@app.route('/institue/start_fetching', methods=['GET', 'POST'])
def start_fetching():
    content = request.json
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
    return OUTPUT

@app.route('/upload_image/<unique_id>', methods=['GET', 'POST'])
def upload_image(unique_id):
    content = request.json
    """
    content input
    {
	"image":"string"
    }
    """
    
    """
    	put the latest image in your data structure
    """
   
    return {"Response : OK/ERROR"}



@app.route('/corporate/add_camera', methods=['GET', 'POST'])
def add_camera_corporate():
    content = request.json
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
    return {"Response":"OK/ERROR"}

def data_fetching_corporate(type,corporate_id,unique_id):
	while True:
		"""
			if type == in:
				get latest data for unique id and put it in corporate_id_in topic
			else:
				in corporate_id_out topic
		"""
@app.route('/corporate/start_fetching', methods=['GET', 'POST'])
def start_fetching_corporate():
    content = request.json
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
    return OUTPUT

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