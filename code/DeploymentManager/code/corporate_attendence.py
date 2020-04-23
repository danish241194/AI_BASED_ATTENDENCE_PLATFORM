from imutils import paths
import face_recognition
import argparse
import pickle
import os
import requests
import json
import cv2
import io
import base64
from PIL import Image
import io
from kafka import KafkaConsumer
import numpy
import numpy as np
from datetime import datetime

def get_new_encodings(corporate_id):
	print("REQUEST TO D.P.MANAGER FOR ENCODINGS FOR ",corporate_id)
	res = requests.get("http://"+DEPLOYMENT_IP+":"+DEPLOYMENT_PORT+"/deployment/service/send_me_encodings/"+corporate_id)
	content = res.json()
	old_encodings = content["encodings"]
	new_encodings = []
	for enc in old_encodings:
		new_encodings.append(np.array(enc))

	data = {"res":"old","encodings":new_encodings,"names":content["names"]}
	return data

def detect_employees(attendence,data,frame):
	print("+ Finding matches")
	image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
	boxes = face_recognition.face_locations(image,model="hog")
	encodings = face_recognition.face_encodings(image,boxes)
	for encoding  in encodings:
		name = "Unknown"
		matches = face_recognition.compare_faces(data["encodings"],encoding)
		if  True in matches:
			matchedIdxs = [j for (j,b) in enumerate(matches) if b]
			counts = {}
			for j in matchedIdxs:
				name = data["names"][j]
				counts[name] = counts.get(name,0)+1
			name = max(counts,key=counts.get)
		if(name != "Unknown"):
			attendence[name]=1
	return

def send_attendence_to_QM(attendence,type_,corporate_id):
	entry_exit_list = list(attendence.keys())
	data_for_QM = {"corporate_id":corporate_id,"type":type_,"ids":entry_exit_list}
	date_current = str(datetime.today().strftime('%d-%m-%Y'))
	time = str(datetime.today().strftime('%H:%M:%S'))
	data_for_QM["date"] = date_current
	data_for_QM["time"] = time
	print(data_for_QM)
	req = requests.post("http://172.17.0.3:"+QUERY_MANAGER_PORT+"/corporate/add_attendance",json=data_for_QM)

	"""
	content
	{
		"corporate_id":1213,
		"type":"IN/OUT",
		"ids":[emp_no_1,emp_no_2,...],
		"date":"DD-MM-YY",
		"time":"hh:mm:ss"
	}
	"""
DEPLOYMENT_IP = "172.17.0.1"
DEPLOYMENT_PORT = "5003"
SERVERLCM_IP = "172.17.0.2"
SERVERLCM_PORT = "3001"
SENSOR_MANAGER_IP = "172.17.0.1"
SENSOR_MANAGER_PORT = "5004"
QUERY_MANAGER_IP = "172.17.0.3"
QUERY_MANAGER_PORT = "9874"


ap = argparse.ArgumentParser()
ap.add_argument("-c","--container_id",required=True)
ap.add_argument("-d","--corporate_id",required=True)
ap.add_argument("-a","--type_in_or_out",required=True)
args = vars(ap.parse_args())

SEND_ATTENDENCE_TIMEOUT = 3

PREV_ENCODING_DATE = str(datetime.today().strftime('%d-%m-%Y'))


data = get_new_encodings(args["corporate_id"])



kafka_Topic = args["corporate_id"]+"_"+args["type_in_or_out"]

consumer  = KafkaConsumer(
	kafka_Topic,bootstrap_servers=['localhost:9092'],
	auto_offset_reset="earliest",
	enable_auto_commit=True,
	group_id="my-group")



secs = 0
attendence = {}
for  message in consumer:
	consumer.commit()
	secs = secs+1

	print("+GOT NEW FRAME")
	
	image_string =  json.loads(message.value)["image"]
	image_string = str.encode(image_string)
	f = io.BytesIO(base64.b64decode(image_string))
	pilimage = Image.open(f)
	frame = numpy.array(pilimage) 
	
	detect_employees(attendence,data,frame)
	
	if(secs==1001):
		secs=1

	if(secs%SEND_ATTENDENCE_TIMEOUT==0):
		print("SENDINGS ATTENDENCE TO QM")
		send_attendence_to_QM(attendence,args["type_in_or_out"],args["corporate_id"])
		attendence = {}

	current_date = str(datetime.today().strftime('%d-%m-%Y'))
	if(PREV_ENCODING_DATE!=current_date):
		print("ASKING FOR NEW ENCODINGS")
		PREV_ENCODING_DATE = current_date
		data = get_new_encodings(args["corporate_id"])

