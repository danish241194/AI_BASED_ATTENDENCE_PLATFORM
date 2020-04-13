'''
	1.Create a foler Project 
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