import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import pickle
from pathlib import Path


import os
app = Flask(__name__)



@app.route('/store/<service>', methods=['GET', 'POST'])
def store(service):
	print("+ REQUEST TO DUMP FROM ",service)
	content = request.json

	registry_path = "registry_data/registry.pickle"
	print("-\tREQUEST TO DUMP FROM ",service)

	my_file = Path("registry_data")
	if not my_file.is_dir():
		os.system("mkdir registry_data")
		f = open(registry_path,"wb")
		data = {"nothingadasd":"nothingxxsdsd"}
		f.write(pickle.dumps(data))

		f.close()


	data = pickle.loads(open(registry_path,"rb").read())

	try:
	    data[service] = content
	    # print(data)
	    f = open(registry_path,"wb")
	    f.write(pickle.dumps(data))
	    f.close()

	    print("- RETURNING RESPONSE OK TO ",service)

	    return {"Response":"OK"}

	except:
		print("- RETURNING RESPONSE ERROR TO ",service)
		return {"Response":"ERROR"}

	"""
	content
	{
		
		"data":{json}
	}
	"""


@app.route('/fetch/<service>')
def fetch(service):
	print("+ REQUEST TO FETCH FROM ",service)
	registry_path = "registry_data/registry.pickle"

	data = pickle.loads(open(registry_path,"rb").read())

	try:
		print("+ RETURNING DATA TO ",service)
		return data[service]

	except:
		return "ERROR"

free_list = list()
@app.route('/add_machine', methods=['GET', 'POST'])
def add_machine():
	print("+ REQUEST TO ADD MACHINE FROM PLATOFRM ADMIN MANAGER")
	content = (request.json)["machines"]
	try:
		for key in content.keys():
			free_list.append(content[key])
			print("-\t ",key," : ",content[key])
			print("+ RETURNING RESPONSE OK TO PLATFORM ADMIN MANAGER")

		return {"Response":"OK"}
	except:
		print("+ RETURNING RESPONSE OK TO PLATFORM ADMIN MANAGER")
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
	print("+ REQUEST TO ENTER ADDRESS OF ",content["servicename"])

	servloc_dict[content["servicename"]] = { "ip":content["ip"] , "port":content["port"] ,"username":content["username"] , "password":content["password"] }
	print("\t- ",content["servicename"])

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
	print("+ RETURNING RESPONSE OK")

	return {"Response":"OK/ERROR"}

@app.route('/get_service_location/<service>')
def get_service_location(service):
	print("+ REQUEST TO GET ADDRESS OF SERVICE ",service)

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
	try:
		print("+ RETURNING ADDRESS",servloc_dict[service])
		return servloc_dict[service]
	except:
		return {"res":"ERROR"}

@app.route('/get_free_list')
def get_free_list():
	print("+ REQUEST FOR FREE LIST")

	if len(free_list) == 0:
		print("\t- NO MACHINE AVAILABLE")
		return {"res":"NO_MACHINE_AVAILABLE"}
	else:
		print("\t- RETURNING FREE LIST : ",free_list)
		return {"res":"OK","free_list":free_list}
    
	'''
    	free_list = [{"ip":ip,"port":port"username":username,"password":password},
					{"ip":ip,"port":port"username":username,"password":password}
    				]
	'''

    # return {"res":"OK","free_list":free_list} or {"res":"NO_MACHINE_AVAILABLE"}


@app.route('/remove_from_free_list')
def remove_free_list():
	print("+ REQUEST TO REMOVE FIRST MACHINE FROM FREE LIST")
	if len(free_list) == 0:
		return {"response":"NO_MACHINE_AVAILABLE"}
	else:
		print("\t- REMOVING ......")
		free_list.pop(0)
		print("+RETURNING OK")
		return {"Response":"OK"}
    
	'''
    	remove first machine from free_list
	'''
@app.route('/display_free_list_and_server_loc')
def display_free_list_and_server_loc():
	print("+ REQUEST TO DISPLAY DATA")
	print("\n##############################################################################################")
	print("[+] FREE LIST")
	print(free_list)
	print("\n[+] SERVER LOCATION")
	print(servloc_dict)    
	print("\n##############################################################################################")

	'''
    	remove first machine from free_list
	'''
	return {"ok":"ok"}

    



if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	args = vars(ap.parse_args())       
	
	app.run(debug=True,port=int(args["port"])) 