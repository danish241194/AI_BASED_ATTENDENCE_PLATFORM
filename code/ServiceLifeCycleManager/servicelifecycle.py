import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import pickle
import paramiko
import os
app = Flask(__name__)

service_files = {}
service_files["Scheduler"]=["run_scheduler.py","scheduler.py"]
service_files["Query Manager"]=["run_query_manager.py","querymanager.py"]
service_files["Sensor Manager"]=["run_sensor_manager.py","sensormanager.py"]

REGISTRY_IP = None
REGISTRY_PORT = None


service_port_mapping={}
service_port_mapping['Application Manager'] = 5000
service_port_mapping['Server LCM'] = 3001
service_port_mapping['Service LCM'] = 5993
service_port_mapping['Deployment Manager'] = 5003
service_port_mapping['Query Manager'] = 9874
service_port_mapping['Sensor Manager'] = 5004
service_port_mapping['Scheduler'] = 8899

def thread_run(ssh_client1, filename):
	stdin,stdout,stderr=ssh_client1.exec_command("python3.6 "+filename)
	print(filename,stderr.readlines())

@app.route('/health')
def health():
    return {"res":"live"}


def send_details_to_registry(service_name,ip,port):
	req = requests.post("http://172.17.0.1:5533/service_entry",json={"servicename":service_name,"ip":ip,"port":port})

@app.route('/run_service/<service>')
def run_service(service):
	machine = None
	if service ==  "Scheduler":
		machine = {"ip":"172.17.0.1","username":"machine1","password":"password"}
	else:
		res = requests.get('http://172.17.0.2:3001/allocate_service_machine')
		machine = res.json()
	print("machine ",machine)
	ssh_client1 =paramiko.SSHClient()
	ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client1.connect(hostname=machine["ip"],username=machine["username"],password=machine["password"])

	ftp_client1=ssh_client1.open_sftp()

	ftp_client1.put(service_files[service][0],service_files[service][0])
	ftp_client1.put(service_files[service][1],service_files[service][1])

	thread = threading.Thread(target=thread_run, args=(ssh_client1,service_files[service][0] ,))
	thread.start()

	send_details_to_registry(service,machine["ip"],service_port_mapping[service])
	# stdin,stdout,stderr=ssh_client1.exec_command("python3 Environment/run_service_lcm.py")
	ftp_client1.close()
	return machine


if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	args = vars(ap.parse_args())       
	
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]
	app.run(debug=True,host = "0.0.0.0",port=int(args["port"])) 
