import argparse
from flask import Flask,request,jsonify
import json
import requests
import threading
import pprint 
import time
import datetime

app = Flask(__name__)

institute_attendance = {}
corporate_attendance = {}

'''
data structure format

institute_attendance = {
	"ins_id": {
		"course1": {
			"date1": {
				"roll_no1": 0/1,
				"roll_no2": 0/1
			},
			"date2": {
				"roll_no2": 0/1,
				"roll_no1": 0/1
			}
		}
	}
}
'''

'''
Example

institute_attendance = {
	"iiit": {
		"SMAI": {
			<datetime format>: {
				"2018201073": 1,
				"2018201070": 0
			},
			<datetime format>: {
				"2018201070": 1,
				"2018201073": 0
			}
		}
	}
}
'''

REGISTRY_IP = None
REGISTRY_PORT = None
@app.route('/institute/add_attendence', methods=['GET', 'POST'])
def add_attendence(x):
	content = request.json
	"""
	content
	{
		"institute_id":1213,
		"course":cs123,
		"attendance": {
			"roll_no2": 0/1,
			"roll_no3": 0/1,
			"roll_no1": 0/1
		}
		"date":"DD-MM-YYYY"
	}
	"""
	content_dict = json.loads(content)

	ins_id = content_dict["institute_id"]
	course = content_dict["course"]
	#converting date into python module "datetime" format before storing
	date = datetime.datetime.strptime(content_dict["date"], '%d-%m-%Y')
	student_attendance = content_dict["attendance"]

	if ins_id not in institute_attendance:
		institute_attendance[ins_id] = {}
	if course not in institute_attendance[ins_id]:
		institute_attendance[ins_id][course] = {}
	institute_attendance[ins_id][course][date] = student_attendance 

	return {"Response":"OK"}


@app.route('/institute/get_attendence', methods=['GET', 'POST'])
def get_attendence():
	content = request.json
	"""
	input

	content
	{

		"institute_id":1213,
		"query":{
					"courses":["cs123","cs247"] OR ["ALL"]
					"students":["roll_no_1", "roll_no_2"] OR ["ALL"]
					"start_date":"12-03-2020"
					"end_date":"22-04-2020"
					"condition":{
						"greater_than":"80" (or "less_than":"50")   (FOR INDIVIDUAL COURSES)
					}
					If condition is none condition will not be present as a key,
					otherwise it will either have greater_than or less_than (not both)
			}
	}
	"""

	"""
	output if no condition
	{
		"course_id_1":{
			"date_1":["roll_no_1","roll_no_2"],
			"date_2":["roll_no_1","roll_no_3"],
			.
			.
			.
		},
		"course_id_2":{
			"date_1":["roll_no_1","roll_no_2"],
			"date_2":["roll_no_1","roll_no_3"],
			.
			.
			.
		}
	}


	output if condition
	{
		"course_id_1":["roll_no_1","roll_no_2"]
		"course_id_2":["roll_no_1","roll_no_5"]
	}
	
	"""
	content_dict = json.loads(content)

	ins_id = content_dict["institute_id"]
	course_list = content_dict["query"]["courses"]
	student_list = content_dict["query"]["students"]
	#converting date into python module "datetime" format before storing
	st_date = datetime.datetime.strptime(content_dict["query"]["start_date"], '%d-%m-%Y')
	e_date = datetime.datetime.strptime(content_dict["query"]["end_date"], '%d-%m-%Y')

	condition = None
	if "condition" in content_dict["query"]:
		condition = content_dict["query"]["condition"]

	if course_list[0] == "ALL":
		course_list = list(institute_attendance[ins_id])

	output_dict = {}

	if ins_id not in institute_attendance:
		return json.dumps(output_dict)

	if condition == None:

		for course in course_list:
			if course in institute_attendance[ins_id]:
				output_dict[course] = {}
				start_date = st_date
				end_date = e_date

				while start_date <= end_date:
					if start_date in institute_attendance[ins_id][course]:
						present_student_list = []
						attendance_dict = institute_attendance[ins_id][course][start_date]
						for student, val in attendance_dict.items():
							if val == 1 and (student in student_list or student_list[0] == "ALL"):
								present_student_list.append(student)
						#converting datetime format into "dd-mm-yyyy" format
						output_dict[course][start_date.strftime('%d-%m-%Y')] = present_student_list
					start_date += datetime.timedelta(days=1)

	else:
		cond_str = list(condition)[0]
		cond_num = int(condition[cond_str])

		for course in course_list:
			if course in institute_attendance[ins_id]:
				output_dict[course] = []
				start_date = st_date
				end_date = e_date

				classes_attended_per_student = {}
				num_classes = 0
				while start_date <= end_date:
					if start_date in institute_attendance[ins_id][course]:
						num_classes += 1
						present_student_list = []
						attendance_dict = institute_attendance[ins_id][course][start_date]
						for student, val in attendance_dict.items():
							if val == 1 and (student in student_list or student_list[0] == "ALL"):
								if student not in classes_attended_per_student:
									classes_attended_per_student[student] = 0
								classes_attended_per_student[student] += 1
					start_date += datetime.timedelta(days=1)

				for student, classes_attended in classes_attended_per_student.items():
					if cond_str == "greater_than":
						if (classes_attended/num_classes)*100 > cond_num:
							output_dict[course].append(student)
					else:
						if (classes_attended/num_classes)*100 < cond_num:
							output_dict[course].append(student)


	return json.dumps(output_dict)


@app.route('/corporate/add_attendence', methods=['GET', 'POST'])
def add_attendence_corporate():
	content = request.json
	"""
	content
	{
		"corporate_id":1213,
		"type":"IN/OUT",
		"ids":[emp_no_1,emp_no_2,...] 
		"date":DD-MM-YY"
		"time":

	}

	"""
	return {"Response":"OK/ERROR"}


@app.route('/corporate/get_attendence', methods=['GET', 'POST'])
def get_attendence_corporate():
	content = request.json
	"""
	input content
	{
		"corporate_id":1213,
		"ids":[emp_no_1,emp_no_2] OR ["ALL"]
		"query":{
			"start_date":"12-03-2020"
			"end_date":"22-04-2020"
			"effective_time":"YES" or None
			"condition":null{
				"greater_than":"80"   FOR INDIVIDUAL COURSES

			}
		}
	}

	"""

	"""
	OUTPUT
	case 1: if effective time is None
				subcase 1: if condition is None:
						OUTPUT = {
									"date_1":[emp_no_1,emp_no_2],
									"date_2":[emp_no_1,emp_no_2],
									.
									.

							}
				subcase 2: if condition is Not None
						OUTPUT = {
								ids:[emp_1,emp_2]   these are the emps whose attendence between start and end date is according to condition
							}
	case 2: if effective time is not None
			in this case condition will always be present
				
						OUTPUT = {
								ids:[emp_1,emp_2]   these are the emps whose average effective time between start and end date  is according to condition
							}
	"""
	return OUTPUT


def data_dumping_service():
	while True:
		time.sleep(60) #wait for 1 minute then upload data in registry
		data = {"institute":institute_data,"corporate":"corporate_data"}
		res = requests.post('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/store/query_manager', json=data)


if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	ap.add_argument("-i","--registry_ip",required=True)
	ap.add_argument("-x","--registry_port",required=True)
	args = vars(ap.parse_args())       
	
	"""
	REGISTRY_IP = args["registry_ip"]
	REGISTRY_PORT = args["registry_port"]

	res = requests.get('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/fetch/query_manager')
	data = res.json()
	//inititalize you data
	t1 = threading.Thread(target=data_dumping_service) 
	t1.start()
	"""
	app.run(debug=True,port=int(args["port"])) 