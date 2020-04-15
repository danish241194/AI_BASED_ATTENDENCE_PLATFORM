import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time
app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None
        #     res = requests.post('http://'+deployment_manager_ip+':'+str(deployment_manager_port)+'/deployment/service/start', json=response)

@app.route('/deployment/service/start', methods=['GET', 'POST'])
def add_camera():
    content = request.json
    """
    content = {"org":"institute","institute_id":institute_id,"attendence_minutes":attendence_minutes,"room_id":room_id,"course_no":course_no}

    """
    """
    		get container_id,ip,port ,username,password from serverlife cycle
    		if org==institute:

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
	args = vars(ap.parse_args())       
	
	"""
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]

	"""
	app.run(debug=True,port=int(args["port"])) 