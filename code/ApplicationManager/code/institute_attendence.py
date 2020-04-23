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


def detect_students(attendence,course_enrolled_list,data,frame):
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
		if(name in course_enrolled_list):
			attendence[name]=1
	return


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
# ap.add_argument("-o","--org",required=True)
ap.add_argument("-d","--institute_id",required=True)
ap.add_argument("-r","--room_id",required=True)
ap.add_argument("-x","--course_no",required=True)
ap.add_argument("-a","--attendence_minutes",required=True)
args = vars(ap.parse_args())

# ask for encodings and all roll_numbers
print("REQUEST TO D.P.MANAGER FOR ENCODINGS FOR ",args["institute_id"])
res = requests.get("http://"+DEPLOYMENT_IP+":"+DEPLOYMENT_PORT+"/deployment/service/send_me_encodings/"+args["institute_id"])
content = res.json()
old_encodings = content["encodings"]
new_encodings = []
for enc in old_encodings:
	new_encodings.append(np.array(enc))

data = {"res":"old","encodings":new_encodings,"names":content["names"]}



# ask for course_enrolled_students

res = requests.get("http://"+DEPLOYMENT_IP+":"+DEPLOYMENT_PORT+"/deployment/service/send_me_course_enrols/"+args["institute_id"]+"/"+args["course_no"])
course_enrolled_students = (res.json())["enrols"] #list

attendence = {}
for name in course_enrolled_students:
	attendence[name]=0




#ask for kafkatopic

res = requests.post("http://"+SENSOR_MANAGER_IP+":"+SENSOR_MANAGER_PORT+"/institute/get_camera_instance",json={"institute_id":args["institute_id"],"room_id":args["room_id"]})
kafka_topic = res.json()["topic"]
print("kafka_topic ",kafka_topic)
# kafka_topic="input_to_camera"


#call start fetching
res = requests.post("http://"+SENSOR_MANAGER_IP+":"+SENSOR_MANAGER_PORT+"/institute/start_fetching",json={"institute_id":args["institute_id"],"unique_id":kafka_topic})

consumer  = KafkaConsumer(
	kafka_topic,bootstrap_servers=['localhost:9092'],
	auto_offset_reset="earliest",
	enable_auto_commit=True,
	group_id="my-group")


secs = 0
for message in consumer:
	# print("message ",message,"value ",message.value)
	consumer.commit()
	print("+GOT NEW FRAME")
	secs = secs+10
	image_string =  json.loads(message.value)["image"]
	image_string = str.encode(image_string)
	f = io.BytesIO(base64.b64decode(image_string))
	pilimage = Image.open(f)
	
	frame = numpy.array(pilimage) 
	print(len(data["encodings"]))
	
	detect_students(attendence,course_enrolled_students,data,frame)
	
	if int(secs/60)>=int(args["attendence_minutes"]):
		break

#stop fetching data
res = requests.post("http://"+SENSOR_MANAGER_IP+":"+SENSOR_MANAGER_PORT+"/institute/stop_fetching",json={"institute_id":args["institute_id"],"unique_id":kafka_topic})


print("ATTENDENCE ",attendence)

# send dictionary of all present students to query manager
query_manager_data = {
		"institute_id": args["institute_id"],
		"course": args["course_no"],
		"attendance": attendence,
		"date":str(datetime.today().strftime('%d-%m-%Y'))
	}

res = requests.get("http://"+SERVERLCM_IP+":"+SERVERLCM_PORT+"/serverlcm/de_allocate_user_machine/"+args["container_id"])

req = requests.post("http://172.17.0.3:"+QUERY_MANAGER_PORT+"/institute/add_attendance",json=query_manager_data)
