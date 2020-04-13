import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading 
import time

@app.route('/store/<service>', methods=['GET', 'POST'])
def store(service):
    content = request.json
    """
    content
	{
		
		"data":{json}
	}
    """

    return {"Response":"OK/ERROR"}


@app.route('/fetch/<service>', methods=['GET', 'POST'])
def fetch(service):
    content = request.json
    """
    content
	{
		
		"data":{json}
	}
    """

    return {"Response":"OK/ERROR"}
if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	args = vars(ap.parse_args())       
	
	app.run(debug=True,port=int(args["port"])) 