import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import pickle
app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
@app.route('/run_service/<service>', methods=['GET', 'POST'])
def run_service(service):

    '''
		    res = requests.get('http://'+REGISTRY_IP+':'+int(REGISTRY_PORT)+'/get_service_location/server_life_cycle')
		    content = res.json()
		    ip = content["ip"]
		    port = content["port"]

		    res = requests.get('http://'+ip+':'+int(port)+'/assign_machine_for_platform_sevice')
		    content = res.json()
			
				content = {
					"ip":ip,
					"port":port,
					"username":username,
					"password",password,
		    			}

		   using "paramiko" copy the service(given) code which will be in the current direct to the remote
		   machine whose details are in content and also copy machine agent code and run both service file as
		   well as machineagent file

		   add the entry of these two services in registry

				as  data = {get_free_list():
					"servicename":scheduler
					"ip":ip,
					"port":port,
					"username":username,
					"password",password,
		    			}
		    res = requests.post('http://registryip:registryport/service_entry', json=data)
		
    '''
    return {"Response":data}


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
	
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]
	"""
	res = requests.get('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/fetch/query_manager')
	data = res.json()
	//inititalize you data
	t1 = threading.Thread(target=data_dumping_service) 
	t1.start()
	"""
	# app.run(debug=True,port=int(args["port"])) 

	data = {
			"servicename":"scheduler",

			"ip":"127.9.9.9",
			"port":"9000",
			"username":"username",
			"password":"password"
			}
	print("ok1")
	res = requests.get("http://"+REGISTRY_IP+":"+REGISTRY_PORT+"/service_entry", json=data)
	print(res)
	print("ok2")
	data = {}
	res = requests.get("http://"+REGISTRY_IP+":"+REGISTRY_PORT+"/get_service_location/"+"scheduler", json=data)
	print(res)