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
users_containers_load = []

service_nodes = []
servie_noes_load=[]


@app.route('/health')
def health():
    return {"res":"live"}

users_containers_details = []


@app.route('/give_load_details_ai_machines')
def give_load_details():

	return {"machines":users_containers_details,"load":users_containers_load}

@app.route('/show_machines')
def show_machines():
	print("AI MACHINES")
	print(users_containers_details)
	print("SERVICE MACHINES")
	print(service_nodes)
	return {"ai_machines":users_containers_details,"service_machines":service_nodes}


@app.route('/allocate_service_machine')
def allocate_service_machine():
	global service_nodes,load
	content = request.json
	if(len(service_nodes)==0):
		return {"res":"no new machine"}
	for i in range(len(service_nodes)):
		if servie_noes_load[i]<1:
			servie_noes_load[i]+=1
			return service_nodes[i]
	return {"res":"no machine"}


@app.route('/add_new_machines', methods=['GET', 'POST'])
def add_new_ai_machines():
	global users_containers_load,users_containers_details,service_nodes

	'''
	{
		machine_1:{
			"ip"
			"port"
			"username"
			"password"
		},
		machine_2:{
				.
				.
				.
				.
		}
	}
	'''
	content_machines = request.json
	content_machines = content_machines["machines"]
	for key in content_machines.keys():

		content = content_machines[key]
		if content["type"]=="AI":
			new_machine = {}
			new_machine["container_id"]=len(users_containers_details)
			new_machine["ip"]=content["ip"]
			new_machine["port"]=content["port"]
			new_machine["username"]=content["username"]
			new_machine["password"]=content["password"]
			users_containers_load.append(0)
			users_containers_details.append(new_machine)
		else:
			new_machine = {}
			new_machine["ip"]=content["ip"]
			new_machine["port"]=content["port"]
			new_machine["username"]=content["username"]
			new_machine["password"]=content["password"]
			service_nodes.append(new_machine)
			servie_noes_load.append(0)
			
	return {"res":"ok"}



@app.route('/serverlcm/de_allocate_user_machine/<container_id>')
def de_allocate_user_machine(container_id):
	print("REQUEST TO DEALLOCATE")
	index = int(container_id)
	users_containers_load[index]-=1
	return {"res":"ok"}
@app.route('/serverlcm/display_loads')
def display_loads():
	for i in range(len(users_containers_load)):
		print("Container ",i," : ",users_containers_load[i])
	return {"res":"ok"}

@app.route('/serverlcm/allocate_user_machine', methods=['GET', 'POST'])
def allocate_user_machine():
	print("\n\n+ REQUEST TO ALLOCATE MACHINE REQUEST")

	content = request.json
	for i in range(len(users_containers_details)):
		if(users_containers_load[i]<3):
			users_containers_load[i]+=1;
			print("\t- MACHOME FROM ALREADY EXISTING CONTAINER ")
			print("\t\t* ",users_containers_details[i])

			return users_containers_details[i];
	return {"res":"no_machine"}

if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	args = vars(ap.parse_args())       
	
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]
	
	app.run(debug=True,host = "0.0.0.0",port=int(args["port"])) 
