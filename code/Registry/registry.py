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


@app.route('/fetch/<service>')
def fetch(service):
    '''
    return data what ever was latest stored by the service
    '''

    return data

@app.route('/add_machine', methods=['GET', 'POST'])
def add_machine():
    content = request.json
    '''
    	{
			machines:[
				machine_1:{
							"ip":ip,
							"port":port
							"username":username,
							"password":password
						},
				machine_2:{
							"ip":ip,
							"port":port,
							"username":username,
							"password":password
					}
				]
    	}
    '''
    '''
    add this in free list
    '''
    '''
    	return ack
    '''

    return {"Response":"OK/ERROR"}


 @app.route('/service_entry', methods=['GET', 'POST'])
def service_entry():
    content = request.json
    '''
    	
    '''
    '''
    	which service is running at which location
    '''
    '''
    	return ack
    '''

    return {"Response":"OK/ERROR"}
 @app.route('/get_service_location/<service>')
def get_service_location(service):
    '''
    	OUTPUT
    	{
    		{
			"ip":ip,
			"port":port,
			"username":username,
			"password",password

    		}

    		OF THAT SERVICE
		
    	}
    '''
    return {"Response":"OK/ERROR"}


@app.route('/get_free_list')
def get_free_list():
    content = request.json
    
    '''
    	free_list = [{"ip":ip,"port":port"username":username,"password":password},
					{"ip":ip,"port":port"username":username,"password":password}
    				]
    '''

    return {"res":"OK","free_list":free_list} or {"res":"NO_MACHINE_AVAILABLE"}


@app.route('/remove_from_free_list')
def get_free_list():
    content = request.json
    
    '''
    	remove first machine from free_list
    '''

    return {"response":"OK"}



if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	args = vars(ap.parse_args())       
	
	app.run(debug=True,port=int(args["port"])) 