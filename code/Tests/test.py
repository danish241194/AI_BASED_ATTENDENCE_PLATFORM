from flask import Flask
import io
import base64
from PIL import Image
import io
app = Flask(__name__)
from PIL import Image
@app.route("/hello")
def remove_ip_from_freelist():
	with open("abc.png", "rb") as image:
		b64string = base64.b64encode(image.read())
		f = io.BytesIO(base64.b64decode(b64string))
		pilimage = Image.open(f)
		pilimage.save("hoo.png")
		return b64string


if __name__ == "__main__":        # on running python app.py
	app.run(debug=True,port=6060) 
