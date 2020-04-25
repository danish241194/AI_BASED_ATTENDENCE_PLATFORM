from imutils import paths
import face_recognition
import argparse
import pickle
import os
import requests
import json


def get_ip_port(service):
    res = requests.get("http://172.17.0.1:5533/get_service_location/"+service)
    return (res.json())["ip"]+":"+str((res.json())["port"])

DEPLOYMENT_IP = "172.17.0.1"
DEPLOYMENT_PORT = "5003"
SERVERLCM_IP = "172.17.0.2"
SERVERLCM_PORT = "3001"
ap = argparse.ArgumentParser()
ap.add_argument("-i","--dataset",required=True)
ap.add_argument("-c","--container_id",required=True)
ap.add_argument("-o","--org",required=True)
ap.add_argument("-d","--id",required=True)
args = vars(ap.parse_args())

dataset_path = args["dataset"]
detection_method = "hog"

imagePaths = list(paths.list_images(dataset_path))

knownEncodings = []
knownNames = []

print("+ Findings encodings")

for(i,imagePath) in enumerate(imagePaths):
	print("\t- Processing image {}/{}".format(i+1,len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]
	image = face_recognition.load_image_file(imagePath)
	boxes = face_recognition.face_locations(image,model=detection_method)
	encodings = face_recognition.face_encodings(image,boxes)
	for encoding in encodings :
		knownNames.append(name)
		knownEncodings.append(encoding.tolist())

res = requests.get("http://"+DEPLOYMENT_IP+":"+DEPLOYMENT_PORT+"/deployment/service/send_me_encodings/"+args["id"])

data = res.json()
if(data["res"]=="new"):
	data = {"res":"old","encodings":knownEncodings,"names":knownNames}
else:
	data["encodings"].extend(knownEncodings)
	data["names"].extend(knownNames)
print("new encodings keys" ,data.keys())

res = requests.post("http://"+DEPLOYMENT_IP+":"+DEPLOYMENT_PORT+"/deployment/service/take_new_encodings/"+args["id"],json=data)
res = requests.get("http://"+get_ip_port("Server LCM")+"/serverlcm/de_allocate_user_machine/"+args["container_id"])
