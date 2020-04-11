from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-i","--dataset",required=True)
ap.add_argument("-e","--encodings",required=True)
ap.add_argument("-d","--detection_method",type=str,default="hog")#cnn
args = vars(ap.parse_args())

dataset_path = args["dataset"]
encodings_path = args["encodings"]
detection_method = args["detection_method"]

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
		knownEncodings.append(encodings)

data = {"encodings":knownEncodings,"names":knownNames}
print("+ Dumping encodings")
f = open(encodings_path,"wb")
f.write(pickle.dumps(data))
f.close()