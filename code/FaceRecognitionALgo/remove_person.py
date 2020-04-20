import argparse
import pickle


ap = argparse.ArgumentParser()
ap.add_argument("-e","--encodings",required=True)#olds path
ap.add_argument("-f","--file_path",required=True)#cnn
args = vars(ap.parse_args())

encodings_path = args["encodings"]
names_file_path = args["file_path"]

print("+ Fetching names to be removed")
with open(names_file_path) as f:
    content = f.readlines()
names_to_be_removed = [x.strip() for x in content]
print("+ Names Fetching")

data = pickle.loads(open(encodings_path,"rb").read())

encodings = data["encodings"]
names = data["names"]

print("+ Removing Names")
new_encodings=[]
new_names = []
for i in range(len(encodings)):
	name = names[i]
	if name in names_to_be_removed:
		continue
	new_encodings.append(encodings[i])
	new_names.append(names[i])

data = {"encodings":new_encodings,"names":new_names}
print("+ Total New Encodings : ",len(new_encodings))
print("+ Dumping New Encodings")
f = open(encodings_path,"wb")
f.write(pickle.dumps(data))
f.close()