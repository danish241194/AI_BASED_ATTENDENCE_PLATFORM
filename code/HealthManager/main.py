'''
	do this for every service name
		res = requests.get('http://'+REGISTRY_IP+':'+int(REGISTRY_PORT)+'/get_service_location/service_name')
		content = res.json()
		The content information will be as
			content = {
				"ip":ip,
				"port":port,
				"username":username,
				"password":password
			}
	now you know every services ip address 
	After every 10 secs call
				res = requests.get('http://'+ip+'9999/heartbeat')
				9999 is fix for heart beats
				if res.ok
					//do nothing
				else
					res = requests.get('http://'+REGISTRY_IP+':'+int(REGISTRY_PORT)+'/get_service_location/service_life_cycle')
					content = res.json()
					service_lcm_ip,port = content["ip"],content["ip"]
					res = requests.get('http://service_lcm_ip:port/run_service/<service>')


'''