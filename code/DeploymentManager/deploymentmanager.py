import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
import paramiko

app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
        #     res = requests.post('http://'+deployment_manager_ip+':'+str(deployment_manager_port)+'/deployment/service/start', json=response)

@app.route('/deployment/service/start', methods=['GET', 'POST'])
def deploy_attendence():
	content = request.json
	req_content = content
	"""
	content = {"org":"institute","institute_id":institute_id,"attendence_minutes":attendence_minutes,"room_id":room_id,"course_no":course_no}

	"""
	print("+ REQUEST FOR ATTENDENCE BY ",req_content["org"]," ID ",req_content["institute_id"])
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
		ftp_client.put("code/institue_attendence_automatic.py",folder+"/institue_attendence_automatic.py")
		ftp_client.close()

		print("\t\t* COPIED ATTENDENCE CODE")

		arguments = "--container_id "+str(container_id)+" --institue_id "+req_content["institute_id"] +" --room_id "+req_content["room_id"] +" --course_no "+req_content["course_no"] +" --attendence_minutes "+req_content["attendence_minutes"]

		ssh_client.exec_command("python3 institue_attendence_automatic.py "+arguments)

		print("\t\t* EXECUTED CODE")

		ssh_client.close()
	else:
		print("\t- REQUEST FOR CORPORATE ATTENDENCE")

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
	
	app.run(debug=True,port=int(args["port"])) 