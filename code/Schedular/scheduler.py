import schedule 
import time 
import threading 
from random import randrange
import json
from flask import Flask,request,jsonify
import random
import json
import requests
import argparse
from datetime import datetime

app = Flask(__name__)

REGISTRY_IP = None
REGISTRY_PORT = None

deployment_manager_ip="172.17.0.1"
deployment_manager_port = 5003

class Scheduler:
    def __init__(self):   

    def pending_jobs(self):
        while True: 
            schedule.run_pending() 
            time.sleep(10)

    def send_request_to_deployment_manager(self,institute_id,attendence_minutes,room_id,course_no):
        response = {"org":"institute","institute_id":institute_id,"attendence_minutes":attendence_minutes,"room_id":room_id,"course_no":course_no}
        print("SENDING REQUEST TO DEP. MANAGER TO START ATTENDENCE")
        res = requests.post('http://'+deployment_manager_ip+':'+str(deployment_manager_port)+'/deployment/service/start_attendence', json=response)
    
    def run(self):
        t1 = threading.Thread(target=self.pending_jobs) 
        t1.start() 

    def run_service(self,service_detail):
        institute_id,attendence_minutes,room_id,course_no= service_detail[0],service_detail[1],service_detail[2],service_detail[3]
        #send request to deployment manager to start attendence
        self.send_request_to_deployment_manager(institute_id,attendence_minutes,room_id,course_no)
       

    def schedule(self,request_):
        institute_id = request_["institute_id"]
        day = request_["day"]
        start_time = request_["start_time"]
        attendence_minutes = request_["attendence_minutes"]
        room_id = request_["room_id"]
        course_no = request_["course_no"]

        '''
            "institue_id":"ins id"
            "room_id":"room id"
            "course_no":"cs1234"
            "day":"monday"
            "start_time":"13:00"
            "attendence_minutes":10
            ""
        '''
        schedule_instance_id=institute_id + course_no + room_id +str(randrange(10000))

        result = "OK"
        job_id = None        
        if(day=="monday"):
            job_id = schedule.every().monday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        elif(day=="tuesday"):
            job_id = schedule.every().tuesday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        elif(day=="wednesday"):
            job_id = schedule.every().wednesday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        elif(day=="thursday"):
            job_id = schedule.every().thursday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        elif(day=="friday"):
            job_id = schedule.every().friday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        elif(day=="saturday"):

            job_id = schedule.every().saturday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        else:
            job_id = schedule.every().sunday.at(start_time).do( self.run_service,((institute_id,attendence_minutes,room_id,course_no)))
        
        self.scheduling_ids[schedule_instance_id] = job_id
        return result,schedule_instance_id


  

@app.route('/health')
def schedule_health():
    return {"res":"live"}
    
@app.route('/schedule/startSchedule', methods=['GET', 'POST'])
def schedule_service():
    content = request.json
    '''
    "institue_id":"ins id"
    "room_id":"room id"
    "course_no":"cs1234"
    "day":"monday"
    "start_time":"13:00"
    "attendence_minutes":10
    ""
    '''
    
    result,schedule_instance_id = sch.schedule(content)

    return {"result":"OK","schedule_instance_id":schedule_instance_id}

sch = None
        
            
if __name__ == "__main__": 
    ap = argparse.ArgumentParser()
    ap.add_argument("-p","--port",required=True)
    # ap.add_argument("-i","--registry_ip",required=True)
    # ap.add_argument("-x","--registry_port",required=True)
    args = vars(ap.parse_args())          
    # REGISTRY_IP = args["registry_ip"]
    # REGISTRY_PORT = int(args["registry_port"])
    Myport = args["port"]
    sch = Scheduler()
    sch.run()
    

    app.run(debug=True,host = "0.0.0.0",port=int(args["port"])) 



