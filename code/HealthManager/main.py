import time
import json
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
def get(service_name):
	with open(str(service_name)) as f:
			  content= json.load(f)
	return content

def health_check():
		service_list=["BootstrapManager.json","HealthManager.json"]
		service_log={}
		for service_name in service_list:
		
			#For testing get
			res=get(service_name)
			#For real time use
			# res=requests.get('http://'+REGISTRY_IP+':'+int(REGISTRY_PORT)+'/get_service_location/service_name')
			
			#For testing
			content=res

			#For real time use
			# content=res.json()
			service_log[service_name]=content

		while (True):
			#Do it 10 for real time use
			time.sleep(1)
			for service_name in service_list:
				ip=service_log[service_name]["ip"]

				#for real time use
				#res = requests.get('http://'+ip+'9999/heartbeat')

				#for testing false cases
				res=False
				if res==False:
				# res = requests.get('http://'+REGISTRY_IP+':'+int(REGISTRY_PORT)+'/get_service_location/service_life_cycle')
					content =service_log[service_name] 
					service_lcm_ip,port = content["ip"],content["port"]
					# res = requests.get('http://'+service_lcm_ip+':'+port+'/run_service/'+service_name)
					# service_log[service_name]=res.json()



if __name__ == "__main__": 
	health_check()

