import os,time,requests
import shutil
import urllib, json
import subprocess
import threading
import paramiko


def runRegistry():
	subprocess.call("python3 Folder/Folder.py '-p 5000'", shell=True)

def getdummyData():
	with open("dummyfreelist.json") as f:
			  content= json.load(f)
	return content
def startBootstrap():
	# try:
	# 	os.mkdir("Folder")
	# except:
	# 	#Directory exists or some error
	# 	flag=False

	# shutil.copy("../Registry/registry.py","Folder/registry.py")
	# t1 = threading.Thread(target=runRegistry)
	# t1.start()
	# time.sleep(5)
	#use this for real use
	#res = requests.get('http://127.0.0.1:5000/get_free_list')
	#res=res.json()

	#For testing
	res=getdummyData()
	key=list(res["machines"].keys())
	machine1=res["machines"][key[0]]
	machine2=res["machines"][key[1]]
	ssh_client =paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print("enter")
	ssh_client.connect(hostname='127.0.0.1',username='n',password='')
	stdin,stdout,stderr=ssh_client.exec_command("ls")
	print(stdout.readlines())
	# subprocess.call(['Folder/Folder.py', '-p', '5000']) 
	# exec()
	# python3 "Folder/Folder.py"


'''
	1.Create a foler Project 

	course
	images
	encodings

	2.Copy the code of registry into Project FOLDER and run this registry code py passing port number 5000
	which is fix in our platform
	2.read the free list file which will be in the following format
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
					},
					.
					.
					.
					.

				]
	3. Read the top two  machines and using "paramiko" library copy codes of server life cycle and service life cycle
	   manager in those two machines and also copy machineagent.py code from current directory to these to machines
	   For service life cycle one copy also codes of query manager,sensor manager, scheduler

	4. using "paramiko" run serverlifecyle.py and machineagent.py in one machine
		and run servicelifecycle.py and machineagent.py in another machine
		and add the entry of these two services in registry

				as  data = {
					"servicename":scheduler
					"ip":ip,
					"port":port,
					"username":username,
					"password",password,
		    			}
		    res = requests.post('http://registryip:registryport/service_entry', json=data)

	5.for rest of services(scheduler,sensormanager,healthcheckmanager) call service life cycle manager api
		    res = requests.get('http://service_lcm_ip:port/run_service/<service>')

		    do remember call health check manager in the end

	

'''
if __name__ == "__main__": 
	startBootstrap()



	# mac1- reg.py dep.py app.py

	# mac2-
