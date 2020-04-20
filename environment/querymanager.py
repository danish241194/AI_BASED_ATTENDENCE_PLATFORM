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

'''
data structure format for institute_attendance

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
@app.route('/institute/add_attendance', methods=['GET', 'POST'])
def add_attendance():
	global institute_attendance
	content = request.json
	"""
	content
	{
		"institute_id": 1213,
		"course": "cs123",
		"attendance": {
			"roll_no2": 0/1,
			"roll_no3": 0/1,
			"roll_no1": 0/1
		}
		"date":"DD-MM-YYYY"
	}
	"""
	content_dict = content

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
@app.route('/institute/show')
def show():
	global institute_attendance
	print(institute_attendance)
	return {"Response":"OK"}

@app.route('/institute/get_attendance', methods=['GET', 'POST'])
def get_attendance():
	global institute_attendance
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
					"condition":{                 (FOR INDIVIDUAL COURSES)
						"greater_than": 80
						(or "less_than": 50)
						(or null)
					}
					Condition will either be null or greater_than or less_than
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
	content_dict = content

	ins_id = content_dict["institute_id"]
	course_list = content_dict["query"]["courses"]
	student_list = content_dict["query"]["students"]
	#converting date into python module "datetime" format before storing
	st_date = datetime.datetime.strptime(content_dict["query"]["start_date"], '%d-%m-%Y')
	e_date = datetime.datetime.strptime(content_dict["query"]["end_date"], '%d-%m-%Y')

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
		cond_num = condition[cond_str]

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
						if int((classes_attended/num_classes)*100) > cond_num:
							output_dict[course].append(student)
					


	return output_dict


'''
data structure format for corporate_attendance

corporate_attendance = {
	"corporate_id": {
		"date1": {
			"emp_no_1": {
				"duration": "seconds" (duration for which he is in the office that day)
				"last_in": "hh:mm:ss" or None (time at which he last went in the office)
			}
		}
	}
}
'''

corporate_attendance = {}

@app.route('/corporate/add_attendance', methods=['GET', 'POST'])
def add_attendance_corporate():
	content = request.json
	"""
	content
	{
		"corporate_id":1213,
		"type":"IN/OUT",
		"ids":[emp_no_1,emp_no_2,...],
		"date":"DD-MM-YY",
		"time":"hh:mm:ss"
	}
	"""
	content_dict = json.loads(content)

	corporate_id = content_dict["corporate_id"]
	timestamp_type = content_dict["type"]
	empid_list = content_dict["ids"]
	date = content_dict["date"]
	time = content_dict["time"]

	timestamp = datetime.datetime.strptime(date + " " + time, '%d-%m-%Y %H:%M:%S')
	date = datetime.datetime.strptime(date, '%d-%m-%Y')

	if corporate_id not in corporate_attendance:
		corporate_attendance[corporate_id] = {}

	if date not in corporate_attendance[corporate_id]:
		corporate_attendance[corporate_id][date] = {}

	for emp in empid_list:
		if emp not in corporate_attendance[corporate_id][date]:
			corporate_attendance[corporate_id][date][emp] = {}
			corporate_attendance[corporate_id][date][emp]["duration"] = 0 #intially duration would be zero
			corporate_attendance[corporate_id][date][emp]["last_in"] = timestamp

		if timestamp_type == "IN":
			corporate_attendance[corporate_id][date][emp]["last_in"] = timestamp
		else:
			last_in_time = corporate_attendance[corporate_id][date][emp]["last_in"]
			out_time = timestamp

			duration_to_be_added = (out_time - last_in_time).seconds

			corporate_attendance[corporate_id][date][emp]["duration"] += duration_to_be_added			

	return {"Response":"OK"}




@app.route('/corporate/get_attendance', methods=['GET', 'POST'])
def get_attendance_corporate():
	content = request.json
	"""
	input content
	{
		"corporate_id":1213,
		"ids":[emp_no_1,emp_no_2] OR ["ALL"]
		"query":{

			"start_date":"12-03-2020",
			"end_date":"22-04-2020",
			"effective_time": "hh:mm:ss" or null (denoting the duration that an employee needs to be in the office),
			"condition":{
				"greater_than": 80
				(or null)
			}
		}
	}

	"""

	"""
	OUTPUT

	Case 1: if condition is None:
		OUTPUT = {
			"date_1": [emp_no_1,emp_no_2],
			"date_2": [emp_no_1,emp_no_2],
			.
			.
		}
+
+	Case 2: if condition is Not None
		OUTPUT = {
			"ids": [emp_1,emp_2]   these are the emps whose attendence between start and end date is according to condition
		}
	
	"""

	content_dict = json.loads(content)

	corporate_id = content_dict["corporate_id"]
	empid_list = content_dict["ids"]
	start_date = datetime.datetime.strptime(content_dict["query"]["start_date"], '%d-%m-%Y')
	end_date = datetime.datetime.strptime(content_dict["query"]["end_date"], '%d-%m-%Y')
	duration_string = content_dict["query"]["effective_time"]
	condition = content_dict["query"]["condition"]

	if duration_string == None:
		effective_time = 0
	else:
		#converting effective_time_string to seconds
		effective_time = int(duration_string[:2])*3600 + int(duration_string[3:5])*60 + int(duration_string[6:])


	'''
	data structure format for corporate_attendance

	corporate_attendance = {
		"corporate_id": {
			"date1": {
				"emp_no_1": {
					"duration": "seconds" (duration for which he is in the office that day)
					"last_in": "hh:mm:ss" or None (time at which he last went in the office)
				}
			}
		}
	}
	'''

	output_dict = {}

	if condition is None:
		while start_date <= end_date:
			if start_date in corporate_attendance[corporate_id]:
				present_emp_list = []
				for emp in corporate_attendance[corporate_id][start_date]:
					if (empid_list[0] == "ALL" or emp in empid_list) and corporate_attendance[corporate_id][start_date][emp]["duration"] > effective_time:
						present_emp_list.append(emp)

				output_dict[start_date.strftime('%d-%m-%Y')] = present_emp_list

			start_date += datetime.timedelta(days=1)

	else:
		output_dict["ids"] = []
		parameter = condition[list(condition)[0]]
		
		days_present_per_employee = {}
		num_working_days = 0

		while start_date <= end_date:
			
			if start_date in corporate_attendance[corporate_id]:
				num_working_days += 1
				for emp in corporate_attendance[corporate_id][start_date]:
					if (empid_list[0] == "ALL" or emp in empid_list) and corporate_attendance[corporate_id][start_date][emp]["duration"] > effective_time:
						if emp not in days_present_per_employee:
							days_present_per_employee[emp] = 0
						days_present_per_employee[emp] += 1

			start_date += datetime.timedelta(days=1)

		for emp in days_present_per_employee:
			if (days_present_per_employee[emp]/num_working_days)*100 > parameter:
				output_dict["ids"].append(emp)

	return json.dumps(output_dict)


def data_dumping_service():
	while True:
		time.sleep(60) #wait for 1 minute then upload data in registry
		data = {"institute":institute_data,"corporate":"corporate_data"}
		res = requests.post('http://'+REGISTRY_IP+':'+str(REGISTRY_PORT)+'/store/query_manager', json=data)


if __name__ == "__main__": 
	ap = argparse.ArgumentParser()
	ap.add_argument("-p","--port",required=True)
	# ap.add_argument("-i","--registry_ip",required=True)
	# ap.add_argument("-x","--registry_port",required=True)
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