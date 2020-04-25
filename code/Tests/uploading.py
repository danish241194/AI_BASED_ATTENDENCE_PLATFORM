from flask import Flask
import io
import base64
from PIL import Image
import io
import requests
import time
def upload_image(img):
	with open(img,"rb") as image:
		b64string = base64.b64encode(image.read())
		req = requests.post("http://172.17.0.1:5004/upload_image/uuuu_sh1_cam123",json={"image":b64string})
		print(req.json())
	return

list_=['s1.jpg','j1.png','a1.jpg']
i=0
while True:
	upload_image(list_[i%3])
	i+=1
	print("Uploading ",i)
	time.sleep(2)
	if(i>1000):
		i=0
