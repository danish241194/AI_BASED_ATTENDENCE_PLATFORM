import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import paramiko
from pathlib import Path
import os
import pickle
from imutils import paths
import subprocess
from os import listdir
app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
        #     res = requests.post('http://'+deployment_manager_ip+':'+str(deployment_manager_port)+'/deployment/service/start', json=response)
@app.route('/health')
def health():
    return {"res":"live"}
@app.route('/deployment/service/start_attendence', methods=['GET', 'POST'])
def deploy_attendence():
	content = request.json
	req_content = content
	print(req_content)
	"""
	content = {"org":"institute","institute_id":institute_id,"attendence_minutes":attendence_minutes,"room_id":room_id,"course_no":course_no}
	"""
	print("+ REQUEST FOR ATTENDENCE BY ",req_content["org"]," ID ")
	if(req_content["org"]=="institute"):
		print(req_content["institute_id"])
	else:
		print(req_content["corporate_id"])

	print("-\t REQUESTED SERVER LCM FOR MACHINE ALLOCATION")
	print("http://"+SERVERLCM_IP+":"+SERVERLCM_PORT+"/serverlcm/allocate_user_machine")
	res = requests.get("http://"+SERVERLCM_IP+":"+SERVERLCM_PORT+"/serverlcm/allocate_user_machine")
	content = res.json()

	print("-\t MACHINE IN RESPONSE \n\t\t",content)

	container_id = content["container_id"]
	ip = content["ip"]
	port = content["port"]
	username = content["username"]
	password = content["password"]

	if req_content["org"]=="institute":
		
		print("\t- REQUEST FOR CLASS ATTENDENCE")

		folder = req_content["institute_id"]+"_"+ str(req_content["room_id"])+"_"+str(req_content["course_no"])
		ssh_client =paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh_client.connect(hostname=ip,username=username,password=password)

		print("\t\t* REMOVED ",folder)

		ssh_client.exec_command("rm -r "+folder)

		print("\t\t* CREATED ",folder)

		ssh_client.exec_command("mkdir "+folder)

		ftp_client=ssh_client.open_sftp()
		ftp_client.put("code/institute_attendence.py",folder+"/institute_attendence_automatic.py")
		ftp_client.close()

		print("\t\t* COPIED ATTENDENCE CODE")

		arguments = "--container_id "+str(container_id)+" --institute_id "+req_content["institute_id"] +" --room_id "+req_content["room_id"] +" --course_no "+req_content["course_no"] +" --attendence_minutes "+str(req_content["attendence_minutes"])
		print(arguments)
		ssh_client.exec_command("python3 "+folder+"/institute_attendence_automatic.py "+arguments)

		print("\t\t* EXECUTED CODE")

		ssh_client.close()
	else:
		print("\t- REQUEST FOR CORPORATE ATTENDENCE")

		folder = req_content["corporate_id"]+"_attendence"
		ssh_client =paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh_client.connect(hostname=ip,username=username,password=password)

		print("\t\t* REMOVED ",folder)

		ssh_client.exec_command("rm -r "+folder)

		print("\t\t* CREATED ",folder)

		ssh_client.exec_command("mkdir "+folder)

		ftp_client=ssh_client.open_sftp()
		ftp_client.put("code/corporate_attendence.py",folder+"/corporate_attendence.py")
		ftp_client.close()

		print("\t\t* COPIED ATTENDENCE CODE")
		arguments = "--container_id "+str(container_id)+" --corporate_id "+req_content["corporate_id"] +" --type_in_or_out IN"
		print(arguments)
		ssh_client.exec_command("python3 "+folder+"/corporate_attendence.py "+arguments)
		arguments = "--container_id "+str(container_id)+" --corporate_id "+req_content["corporate_id"] +" --type_in_or_out OUT"
		print(arguments)
		ssh_client.exec_command("python3 "+folder+"/corporate_attendence.py "+arguments)


		print("\t\t* EXECUTED CODE")

		ssh_client.close()

    		# get container_id,ip,port ,username,password from serverlife cycle

		"""	if org==institute:

    			ssh to container
    			mkdir with institue_id_room_no_course_no and delete if already present
    			request manager se list of all students jo is course mein hai

    			copy encodigns of institute and attendnce wala code and pass end time also and run and also container id
    			code khud server life cycle ko bolega band mein khtm horaha hun load ke liye
			else
				do same and not send end time as it wont be in content			
		"""
	return {"Response":"OK/ERROR"}
def transfer_files(folder_name,ssh_client,content_id):
	ftp_client=ssh_client.open_sftp()
	list_ = os.listdir("images/"+folder_name)
	ssh_client.exec_command("mkdir "+content_id+"/"+folder_name)
	for folder in list_:
		ssh_client.exec_command("mkdir "+content_id+"/"+folder_name+"/"+folder)

	imagePaths = list(paths.list_images("images/"+folder_name))
	for path_ in imagePaths: 
		
		ftp_client.put(path_,content_id+"/"+'/'.join(path_.split("/")[1:]))
	ftp_client.close()

@app.route('/deployment/service/train_users', methods=['GET', 'POST'])
def train_users():
	content = request.json
	"""
	content = {"org":"institute","id":"id","zip_location":"zip_location"} dont incluce .zip also only filename
	get machine
	copy training code to machine
	copy theis zip file there
	"""

	'''

		unzip zip_location and remove it

	'''
	my_file = Path("encodings/"+content["id"]+".pickle")
	if not my_file.exists():
		print("+ ENCODING NOT EXISTING")
		data = {"res":"new"}
		f = open("encodings/"+content["id"]+".pickle","wb")
		f.write(pickle.dumps(data))
		f.close()
		print("+CREATED NEW PATH FOR ENCODINGS")
	folder = content["id"]+"_train"
	print("+ REQUEST FROM REQUEST MANAGER TO TRAIN NEW USERS OF ",content["org"]," -ID- ",content["id"])
	print("\t- REQUESTED SERVER LCM FOR MACHINE ALLOCATION")
	res = requests.get("http://"+SERVERLCM_IP+":"+SERVERLCM_PORT+"/serverlcm/allocate_user_machine")
	server_content = res.json()
	
	container_id = server_content["container_id"]

	print("\t- ID OF CONTAINER ASSIGNED : ",container_id)
	ip = server_content["ip"]
	port = server_content["port"]
	username = server_content["username"]
	password = server_content["password"]


	ssh_client =paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client.connect(hostname=ip,username=username,password=password)

	print("\t- REMOVED ",folder)

	ssh_client.exec_command("rm -r "+folder)

	print("\t- CREATED ",folder)
	print("\t- ","mkdir "+folder)
	ssh_client.exec_command("mkdir "+folder)

	ftp_client=ssh_client.open_sftp()
	ftp_client.put("code/train_new_users.py",folder+"/train_new_users.py")
	
	ftp_client.close()
	transfer_files(content["zip_location"],ssh_client, folder)	
	print("\t- COPIED ATTENDENCE CODE")

	
	arguments = "--dataset "+folder+"/"+content["zip_location"]+" --container_id "+str(container_id)+" --org "+content["org"]+" --id "+content["id"] 
	print(arguments)
	ssh_client.exec_command("python3.6 "+folder+"/train_new_users.py "+arguments)

	print("\t- EXECUTED CODE")
	os.system("rm -r images/"+content["zip_location"])
	ssh_client.close()
	return {"res":"ok"}

@app.route('/deployment/service/send_me_encodings/<id>')
def send_me_encodings(id):
	print("+ REQUEST FROM RUN TIME SERVER TO SEND ENCODINGS FOR ID ",id)
	data = pickle.loads(open("encodings/"+str(id)+".pickle","rb").read())
	return data
@app.route('/deployment/service/take_new_encodings/<id>', methods=['GET', 'POST'])
def take_new_encodings(id):
	print("+ REQUEST FROM RUN TIME SERVER TO STORE NEW ENCODINGS FOR ID ",id)
	content = request.json
	f = open("encodings/"+str(id)+".pickle","wb")
	f.write(pickle.dumps(content))
	f.close()
	return {"res":"ok"}


@app.route('/deployment/service/send_me_course_enrols/<ins_id>/<course_no>')
def send_me_course_enrols(ins_id,course_no):
	#path is static/data/institutes/ins_id/course/courseid.pickle
	data = pickle.loads(open("static/data/institutes/"+ins_id+"/courses/"+course_no+".pickle","rb").read())
	packet = {"enrols":data["students"]}
	# packet = {"enrols":["salman","johncena","danish"]}
	
	return packet

@app.route('/deployment/service/remove_users', methods=['GET', 'POST'])
def remove_user():
	'''
		input
		{
			{
		"institute_id":"iiit123",
		"roll_number":["204820101","212"]

		}
	'''
	print("+ REQUEST TO REMOVE USER")
	content = request.json
	data = pickle.loads(open("encodings/"+content["institute_id"]+".pickle","rb").read())
	encodings = data["encodings"]
	names = data["names"]
	new_encodings=[]
	new_names = []
	for i in range(len(encodings)):
		name = names[i]
		if name in content["roll_numbers"]:
			continue
		new_encodings.append(encodings[i])
		new_names.append(names[i])
	data = {"res":"old","encodings":new_encodings,"names":new_names}
	print("+ Total New Encodings : ",len(new_encodings))
	print("+ Dumping New Encodings")
	f = open("encodings/"+content["institute_id"]+".pickle","wb")
	f.write(pickle.dumps(data))
	f.close()
	return {"res":"ok"}

if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	ap.add_argument("-s","--serverlcm_ip",required=True)
	ap.add_argument("-r","--serverlcm_port",required=True)
	args = vars(ap.parse_args())       
	
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]

	SERVERLCM_IP = args["serverlcm_ip"]
	SERVERLCM_PORT = args["serverlcm_port"]
	
	app.run(debug=True,host = "0.0.0.0",port=int(args["port"])) 
