import face_recognition
import argparse
import pickle
from imutils import paths
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-e","--encodings",required=True)
ap.add_argument("-i","--images",required=True)
ap.add_argument("-d","--detection_method",type=str,default="hog")
args = vars(ap.parse_args())

encodings_path = args["encodings"]
detection_method = args["detection_method"]
images_path = args["images"]


data = pickle.loads(open(encodings_path,"rb").read())

imagePaths = list(paths.list_images(images_path))

names={}
print("+ Finding matches")
for(i,imagePath) in enumerate(imagePaths):
	print("\t- Processing image {}/{}".format(i+1,len(imagePaths)))
	image = face_recognition.load_image_file(imagePath)
	boxes = face_recognition.face_locations(image,model=detection_method)
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
		names[name]="P"

print("+ Processing Done")
print("+ Results")
for name in names.keys():
	print("\t- ",name)