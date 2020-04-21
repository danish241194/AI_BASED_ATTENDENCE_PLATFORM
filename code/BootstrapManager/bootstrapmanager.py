import os,time,requests
import shutil
import urllib, json
import subprocess
import threading
import paramiko


def copy(ssh_client,ftp_client,source, target):
		# print(source,target)
		for item in os.listdir(source):
				if os.path.isfile(os.path.join(source, item)):
						# print("Enter")
						# print("File=>",item)
						
						ftp_client.put(os.path.join(source, item),str(target)+"/"+str(item))
						# print("Exit")
				else:
						# print("folder=>",item)
						stdin,stdout,stderr=ssh_client.exec_command("mkdir "+str(target)+"/"+str(item))
						copy(ssh_client,ftp_client,os.path.join(source, item), str(target)+"/"+str(item))


def runRegistry():
	subprocess.call("python3 Folder/Folder.py '-p 5982'", shell=True)

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
def startBootstrap():

	freelist=getdummyData()
	machine_list=list(freelist["machines"].keys())
	machine1=freelist["machines"][machine_list[0]]
	machine2=freelist["machines"][machine_list[1]]
	ssh_client1 =paramiko.SSHClient()
	ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client2 =paramiko.SSHClient()
	ssh_client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client1.connect(hostname=machine1["ip"],username=machine1["username"],password=machine1["password"])
	ssh_client2.connect(hostname=machine2["ip"],username=machine2["username"],password=machine2["password"])

	stdin,stdout,stderr=ssh_client1.exec_command("mkdir Project")
	stdin,stdout,stderr=ssh_client1.exec_command("mkdir Course")
	stdin,stdout,stderr=ssh_client1.exec_command("mkdir Images")
	stdin,stdout,stderr=ssh_client1.exec_command("mkdir Encodings")
	stdin,stdout,stderr=ssh_client2.exec_command("mkdir Project")


	ftp_client1=ssh_client1.open_sftp()
	copy(ssh_client1,ftp_client1,'../ApplicationManager','Project')
	copy(ssh_client1,ftp_client1,'../DeploymentManager','Project')
	copy(ssh_client1,ftp_client1,'../Registry','Project')
	


	ftp_client2=ssh_client2.open_sftp()
	# copy(ssh_client2,ftp_client,'../ServiceLifeCycleManager','Project')
	copy(ssh_client2,ftp_client2,'../ServerLifeCycle','Project')
	# # stdin,stdout,stderr=ssh_client1.exec_command("cp  deploymentmanager.py")
	# print("enter")

	## ==> RUNNING MACHINE ONE
	print("Running Registry in Machine=",machine1["username"])
	stdin,stdout,stderr=ssh_client1.exec_command("python3 Project/registry.py -p 5982")

	print("Running Deployment Manager in Machine=",machine1["username"])
	stdin,stdout,stderr=ssh_client1.exec_command("python3 Project/run_deployment_manager.py")
	# print(stderr.readlines())

	print("Running Application Manager in Machine=",machine1["username"])
	stdin,stdout,stderr=ssh_client1.exec_command("python3 Project/app.py")
	# print(stderr.readlines())

	## ==> RUNNING MACHINE TWO
	print("Running Server Life Cycle Manager in Machine=",machine2["username"])
	stdin,stdout,stderr=ssh_client2.exec_command("python3 Project/run_server_lcm.py")

	print("Free list sent to ServiceLifeCycleManager")
	freelist=Update(freelist,machine_list[0],machine_list[1])
	ftp_client2.put("newfreelist.json","Project/freelist.json")
	# print(stderr.readlines())
	ftp_client1.close()
	ftp_client2.close()


	# stdin,stdout,stderr=ssh_client1.exec_command("ls")
	# print(stdout.readlines())
	# # print("hhshs")
	# # res = requests.get('http://127.0.0.1:5982/get_free_list')
	# # print(res.json())
	# # stdin,stdout,stderr=ssh_client1.exec_command("python3 deploymentmanager.py")
	# stdin,stdout,stderr=ssh_client1.exec_command("python3 -m pip install --user flask")
	# stdin,stdout,stderr=ssh_client1.exec_command("python3 -m pip install --user flask_cors")
	# stdin,stdout,stderr=ssh_client1.exec_command("python3 app.py")
	# print(stderr.readlines())
	# subprocess.call(['Folder/Folder.py', '-p', '5982']) 
	# exec()
	# python3 "Folder/Folder.py"


'''
	1.Create a foler Project 

	course
	images
	encodings

	2.Copy the code of registry into Project FOLDER and run this registry code py passing port number 5982
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
