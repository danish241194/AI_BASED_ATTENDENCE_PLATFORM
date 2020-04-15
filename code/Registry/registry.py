import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
app = Flask(__name__)



@app.route('/store/<service>', methods=['GET', 'POST'])
def store(service):
	content = request.json

	registry_path = "/registry.pickle"

	data = pickle.loads(open(registry_path,"rb").read())

	try:
	    data[service] = content
	    # print(data)
	    f = open(registry_path,"wb")
	    f.write(pickle.dumps(data))
	    f.close()
	    return {"Response":"OK"}

	except:
	    return {"Response":"ERROR"}

	"""
	content
	{
		
		"data":{json}
	}
	"""


@app.route('/fetch/<service>')
def fetch(service):
    data = pickle.loads(open(registry_path,"rb").read())

    try:
    	return data[service]

    except:
    	return "ERROR"

free_list = list()
@app.route('/add_machine', methods=['GET', 'POST'])
def add_machine():
	content = request.json
	try:
		for machines in content[machines]:
			for machine in machines.values():
				free_list.append(machine)
		return {"Response":"OK"}
	except:
		return {"Response":"ERROR"}
	'''
		{
			machines:[
				machine_1:{
							"ip":ip,
							"port":port
							"username":username,
							"password":password
						},
				machine_2:{
							"ip":ip,
							"port":port,
							"username":username,
							"password":password
					}
				]
		}
	'''
	'''
	add this in free list
	'''
	'''
		return ack
	'''

    

servloc_dict = dict()
@app.route('/service_entry', methods=['GET', 'POST'])
def service_entry():
    content = request.json
    print("ok")

    servloc_dict[content["servicename"]] = { "ip":content["ip"] , "port":content["port"] , \
    "username":content["username"] , "password":content["password"] }
    '''
    	{
			"servicename":scheduler
			
			"ip":ip,
			"port":port,
			"username":username,
			"password",password,
    		

    	}
    '''
    '''
    	which service is running at which location
    '''
    '''
    	return ack
    '''

    return {"Response":"OK/ERROR"}
@app.route('/get_service_location/<service>')
def get_service_location(service):
	try:
		return servloc_dict[service]
	except:
		return "ERROR"
	'''
		OUTPUT
		{
			{
			"ip":ip,
			"port":port,
			"username":username,
			"password",password,
			}

			OF THAT SERVICE
		
		}
	'''
	return {"Response":"OK/ERROR"}


@app.route('/get_free_list')
def get_free_list():
    content = request.json

    if len(free_list) == 0:
    	return {"res":"NO_MACHINE_AVAILABLE"}
    else:
    	return {"res":"OK","free_list":free_list}
    
    '''
    	free_list = [{"ip":ip,"port":port"username":username,"password":password},
					{"ip":ip,"port":port"username":username,"password":password}
    				]
    '''

    # return {"res":"OK","free_list":free_list} or {"res":"NO_MACHINE_AVAILABLE"}


@app.route('/remove_from_free_list')
def remove_free_list():
    content = request.json

    if len(free_list) == 0:
    	return {"response":"NO_MACHINE_AVAILABLE"}
    else:
    	free_list.pop(0)
    	return {"Response":"OK"}
    
    '''
    	remove first machine from free_list
    '''

    



if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	args = vars(ap.parse_args())       
	
	app.run(debug=True,port=int(args["port"])) 