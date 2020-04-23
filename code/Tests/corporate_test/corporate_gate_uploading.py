from flask import Flask
import io
import base64
from PIL import Image
import io
import requests
import time
import sys
def upload_image(img):
	with open(img,"rb") as image:
		

		b64string = base64.b64encode(image.read())
		req = requests.post("http://172.17.0.1:5004/corporate/upload_image_corporate/"+sys.argv[1],json={"image":b64string})
		print(req.json())
	return

list_=['s1.jpg','s1.jpg','s1.jpg','s1.jpg','s1.jpg','j1.png','j1.png','j1.png','j1.png','a1.jpg','a1.jpg','a1.jpg','a1.jpg','a1.jpg']
i=0
for frame in list_:
	upload_image(frame)
	time.sleep(2)

