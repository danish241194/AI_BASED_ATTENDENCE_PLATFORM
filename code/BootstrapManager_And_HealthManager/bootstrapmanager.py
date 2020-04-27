import os,time,requests
import shutil
import urllib, json
import subprocess
import threading
import paramiko
import time
from texttable import Texttable
service_ip_mapping={}
service_port_mapping={}

service_ip_mapping['Application Manager'] = '172.17.0.1'
service_ip_mapping['Server LCM'] = '172.17.0.2'
service_ip_mapping['Service LCM'] = '172.17.0.2'
service_ip_mapping['Deployment Manager'] = '172.17.0.1'
service_ip_mapping['Query Manager'] = '172.17.0.3'
service_ip_mapping['Sensor Manager'] = '172.17.0.1'
service_ip_mapping['Scheduler'] = '172.17.0.1'
service_ip_mapping['Registry'] = '172.17.0.1'
service_ip_mapping['Registry-Backup'] = '172.17.0.1'



service_port_mapping['Application Manager'] = 5000
service_port_mapping['Server LCM'] = 3001
service_port_mapping['Service LCM'] = 5993
service_port_mapping['Deployment Manager'] = 5003
service_port_mapping['Query Manager'] = 9874
service_port_mapping['Sensor Manager'] = 5004
service_port_mapping['Scheduler'] = 8899
service_port_mapping['Registry'] = 5533
service_port_mapping['Registry-Backup'] = 5544

health_status = {}
def mycopy(ftp_client,source,target):
		
		for item in os.listdir(source):
				if os.path.isfile(os.path.join(source, item)):
						ftp_client.put(os.path.join(source, item),target+"/"+str(item))
				else:
						mycopy(ftp_client,os.path.join(source, item),target+"/"+str(item))


def create_structure(ssh_client,source,target):
	
		for item in os.listdir(source):
				if os.path.isfile(os.path.join(source, item))==False:
						stdin,stdout,stderr=ssh_client.exec_command("mkdir "+target+"/"+str(item))
						create_structure(ssh_client,os.path.join(source, item),target+"/"+str(item))

def copyit(ssh_client,ftp_client,source,destination):
	create_structure(ssh_client,source,destination)
	mycopy(ftp_client,source,destination)


def getdummyData():
	with open("freelist.json") as f:
			  content= json.load(f)
	return content


def Update(freelist,machine1,machine2):

		del freelist['machines'][machine1]
		del freelist['machines'][machine2]
		with open('newfreelist.json', 'w') as data_file:
							data = json.dump(freelist, data_file)

		return data   

def thread_run(ssh_client1, filename):
	stdin,stdout,stderr=ssh_client1.exec_command("python3.6 "+filename)
	print(filename,stderr.readlines())

def send_details_to_registry(service_name,ip,port):
	req = requests.post("http://172.17.0.1:5533/service_entry",json={"servicename":service_name,"ip":ip,"port":port})

def setup_machine_1(machine):

	ssh_client1 =paramiko.SSHClient()
	ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client1.connect(hostname=machine["ip"],username=machine["username"],password=machine["password"])
	stdin,stdout,stderr=ssh_client1.exec_command("mkdir images")
	stdin,stdout,stderr=ssh_client1.exec_command("mkdir encodings")


	ftp_client1=ssh_client1.open_sftp()
	copyit(ssh_client1,ftp_client1,"../ApplicationManager",".")
	copyit(ssh_client1,ftp_client1,"../DeploymentManager",".")
	copyit(ssh_client1,ftp_client1,"../SensorManager",".")
	copyit(ssh_client1,ftp_client1,"../Schedular",".")
	copyit(ssh_client1,ftp_client1,"../Registry",".")


	# thread = threading.Thread(target=thread_run, args=(ssh_client1, "run_registry.py",))
	# thread.start()
	# time.sleep(5)
	thread = threading.Thread(target=thread_run, args=(ssh_client1, "app.py",))
	thread.start()
	print("APP RUNNING")


	thread = threading.Thread(target=thread_run, args=(ssh_client1, "run_scheduler.py",))
	thread.start()


	thread = threading.Thread(target=thread_run, args=(ssh_client1, "run_sensor_manager.py",))
	thread.start()

	send_details_to_registry("Application Manager",machine["ip"],5000)
	send_details_to_registry("Deployment Manager",machine["ip"],5003)
	send_details_to_registry("Sensor Manager",machine["ip"],5004)
	send_details_to_registry("Scheduler",machine["ip"],8899)

	ftp_client1.close()
	# ssh_client1.close()


def setup_machine_2(machine):

	ssh_client1 =paramiko.SSHClient()
	ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client1.connect(hostname=machine["ip"],username=machine["username"],password=machine["password"])



	ftp_client1=ssh_client1.open_sftp()
	copyit(ssh_client1,ftp_client1,"../ServerLifeCycle",".")
	copyit(ssh_client1,ftp_client1,"../ServiceLifeCycleManager",".")
	copyit(ssh_client1,ftp_client1,"../QueryManager",".")
	copyit(ssh_client1,ftp_client1,"../Schedular",".")
	copyit(ssh_client1,ftp_client1,"../SensorManager",".")

	thread = threading.Thread(target=thread_run, args=(ssh_client1, "run_server_lcm.py",))
	thread.start()

	thread = threading.Thread(target=thread_run, args=(ssh_client1, "run_servicelife_cycle.py",))
	thread.start()

	send_details_to_registry("Server LCM",machine["ip"],3001)
	send_details_to_registry("Service LCM",machine["ip"],5993)

	# ssh_client1.close()


def startBootstrap():

	freelist=getdummyData()
	machine_list=list(freelist["machines"].keys())
	machine1=freelist["machines"][machine_list[0]]
	machine2=freelist["machines"][machine_list[1]]

	setup_machine_1(machine1)

	freelist=Update(freelist,machine_list[0],machine_list[1])
	setup_machine_2(machine2)
	return freelist

def draw_details():
	os.system("clear")

	print("\n\t\t Health Status")

	TABLE_ = [['SERVICE Name', 'IP','PORT','STATUS']]
	for key in health_status.keys():
		if(health_status[key][0]=="Registry-Backup"):
			health_status[key][1] = '172.17.0.4'
		TABLE_.append(health_status[key])
	t = Texttable()
	t.add_rows(TABLE_)
	print(t.draw())
	try:
		res = requests.get('http://172.17.0.2:3001/give_load_details_ai_machines')
		content = res.json()

		load = content["load"]
		machines = content["machines"]

		details=[['Machine Name','Username', 'IP','SSH-PORT','STATUS','LOAD']]
		for i in range(len(load)):
			list_=["AI NODE "+str(i)]
			list_.append(machines[i]["username"])

			list_.append(machines[i]["ip"])
			list_.append(machines[i]["port"])
			if(load[i]==0):
				list_.append("IDLE")	
			else:
				list_.append("RUNNING")	

			list_.append(str(load[i])+"/3")
			details.append(list_)	


		print("\n\t\t AI NODES")
		t = Texttable()
		t.add_rows(details)
		print(t.draw())
	except:
		details=[['Machine Name', 'IP','SSH-PORT','STATUS','LOAD']]

		print("\n\t\t AI NODES")
		t = Texttable()
		t.add_rows(details)
		print(t.draw())

def thread_start_new(name):
	time.sleep(3)
	res = requests.get("http://172.17.0.2:5993/run_service/"+name)
	service_ip_mapping[name] = (res.json())["ip"]


def health_individual(name,ip,port):
	global health_status

	try:
		res = requests.get('http://'+ip+":"+str(port)+'/health')

		health_status[name]=[name,ip,port,"RUNNING"]
	except:
		health_status[name]=[name,ip,port,"DOWN"]
		thread = threading.Thread(target=thread_start_new, args=(name,))
		thread.start()


def health_manager():
	global health_status


	services = ['Scheduler','Application Manager','Query Manager','Server LCM','Deployment Manager','Sensor Manager','Service LCM','Registry','Registry-Backup']
	while True:	
		time.sleep(5)
		for service in services:
			health_individual(service,service_ip_mapping[service],service_port_mapping[service])
		draw_details()



if __name__ == "__main__": 

	free_list = startBootstrap()

	other_servies = ["Query Manager"]

	try:
		with open("newfreelist.json") as f:
			content= json.load(f)
		
			requests.post("http://172.17.0.2:3001/add_new_machines",json=content)
	except:
		print("WATING FOR SERVER LIF CYCLE TO BE ACTIVE")
		time.sleep(5)
		with open("newfreelist.json") as f:
			content= json.load(f)
		requests.post("http://172.17.0.2:3001/add_new_machines",json=content)
	
	print("WATING FOR SERVICE LIFE CYCLE TO BE ACTIVE")

	time.sleep(5)
	for service in other_servies:
		requests.get("http://172.17.0.2:5993/run_service/"+service)


	health_manager()