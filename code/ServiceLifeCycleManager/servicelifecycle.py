import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import pickle
import paramiko
import os
app = Flask(_name_)

service_files = {}
service_files["scheduler"]=["run_scheduler.py","scheduler.py"]
service_files["query_manager"]=["run_query_manager.py","querymanager.py"]
service_files["sensor_manager"]=["run_sensor_manager.py","sensormanager.py"]

REGISTRY_IP = None
REGISTRY_PORT = None

def thread_run(ssh_client1, filename):
	stdin,stdout,stderr=ssh_client1.exec_command("python3.6 "+filename)
	print(filename,stderr.readlines())
@app.route('/health')
def health():
    return {"res":"live"}
@app.route('/run_service/<service>')
def run_service(service):
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

	# stdin,stdout,stderr=ssh_client1.exec_command("python3 Environment/run_service_lcm.py")
	ftp_client1.close()
	return machine


if _name_ == "_main_": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	args = vars(ap.parse_args())       
	
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]
	app.run(debug=True,host = "0.0.0.0",port=int(args["port"]))