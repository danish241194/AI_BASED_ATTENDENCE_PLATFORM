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
users_containers_load = [0]
new_machine = {}
new_machine["container_id"]=0
new_machine["ip"]="172.17.0.2"
new_machine["port"]="22"
new_machine["username"]="root"
new_machine["password"]="pppppp"

users_containers_details = [new_machine]

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
	print("\t- REQUEST FOR FREE LIST ")
	res = requests.get("http://"+REGISTRY_IP+":"+REGISTRY_PORT+"/get_free_list")
	print("\t- FREE LIST ",res.json())

	content = res.json()
	if(content["res"]=="OK"):
		new_machine = {}
		new_machine["container_id"]=len(users_containers_details)
		new_machine["ip"]=content["ip"]
		new_machine["port"]=content["port"]
		new_machine["username"]=content["username"]
		new_machine["password"]=content["password"]
		users_containers_load.append(1)
		users_containers_details.append(new_machine)
		print("\t- REQUESTING REGISTRY TO REMOVE ON ENTRY ")

		res = requests.get("http://"+REGISTRY_IP+":"+REGISTRY_PORT+"/remove_from_free_list")
		return new_machine

	print("\t- NO MACHINE AVAILABLE ",res.json())

	return {"container_id",-1}


if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	args = vars(ap.parse_args())       
	
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]
	app.run(debug=True,port=int(args["port"])) 
