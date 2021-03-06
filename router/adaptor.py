import os, psutil, time
'''
hardware_info()
time.sleep(1)
test = hardware_info()
print(test)
'''
def adaptor(remote_info, insNetworking, dispatcher, hardware_info):
	local_info = hardware_info.hardware_info()
	new_throttling = local_info["throttling"]
	remote_throttling = remote_info["throttling"]

	#Update local throttling 
	if local_info["free_cpu"] <= 30:
		if local_info["throttling"] > 50: 
			new_throttling = local_info["throttling"] - 20
		else: 
			new_throttling = local_info["throttling"] / 2
	
	elif local_info["free_cpu"] >= 50:
		if local_info["throttling"] < 50:
			new_throttling = local_info["throttling"] * 2
		elif local_info["throttling"] < 75: 
			new_throttling = local_info["throttling"] + 20
	#Update remote throttling 
	if remote_info["free_cpu"] <= 30:
		if remote_info["throttling"] > 50: 
			remote_throttling = remote_info["throttling"] - 20
		else: 
			remote_throttling = remote_info["throttling"] / 2
	
	elif remote_info["free_cpu"] >= 50:
		if remote_info["throttling"] < 50:
			remote_throttling = remote_info["throttling"] * 2
		elif remote_info["throttling"] < 75: 
			remote_throttling = remote_info["throttling"] + 20

	# Call worker thread function 
	dispatcher.setThrottling(new_throttling)
	hardware_info.throttle = new_throttling

	ret = {}
	ret["type"] = "thor"
	ret["throttling"] = remote_throttling
	num_jobs_in = 0
	if local_info["status"] == "Done" and remote_info["status"] == "Done":
		ret["type"] = "thor"
	elif local_info["status"] == "Done": 
		num_jobs_in = remote_info["num"] * local_info["throttling"]/(local_info["throttling"] + remote_info["throttling"])
	elif remote_info["status"] == "Done": 
		num_jobs_in = (-1) * remote_info["num"] * local_info["throttling"]/(local_info["throttling"] + remote_info["throttling"])
	else: 
		if local_info["num"] - remote_info["num"] > 20: 
			num_jobs_in = (-1) * (local_info["num"] - remote_info["num"]) / 2 
		elif remote_info["num"] - local_info["num"] > 20: 
			num_jobs_in = (remote_info["num"] - local_info["num"]) / 2 

	if num_jobs_in > 0: 
		ret["reqJobs"] = num_jobs_in
	else: 
		ret["reqJobs"] = 0
		num_jobs_in *= -1
		num_jobs = insNetworking.recved_jobs.qsize()
		to_send = []
		if num_jobs_in > num_jobs / 2:
			num_jobs_in = num_jobs / 2
		while num_jobs_in > 0:
			try:
				job = insNetworking.recved_jobs.get(timeout=3)
			except:
				print("timed out getting job")
				num_jobs_in = 0
				break
			else:
				to_send.append(job)
				num_jobs_in -= 1
		if len(to_send) > 0:
			insNetworking.send_jobs(to_send)
			print("sent {0} jobs".format(len(to_send)))		# Call transfer manager
	ret["my_cpu"] = local_info["my_cpu"]
	ret["free_cpu"] = local_info["free_cpu"]
	ret["my_throttle"] = local_info["throttling"]
	ret["qed"] = local_info["num"]
	ret["done"] = dispatcher.done_count

	insNetworking.send_comm(ret)

'''
	local_speed = local_info["num"] / local_info["time"] * (new_throttling / local_info["throttling"])
<<<<<<< HEAD:adaptor.py
	if local_speed == 0:
		return
	local_rem = local_info["num"] / local_speed 
	remote_speed = remote_info["num"] / remote_info["time"] * (remote_throttling / remote_info["throttling"])
	if remote_speed == 0:
		return
=======
	remote_speed = remote_info["num"] / remote_info["time"] * (remote_throttling / remote_info["throttling"])
	if local_speed == 0 or remote_speed == 0:
		return

	local_rem = local_info["num"] / local_speed 
>>>>>>> 86290a4b61034b83b5a61945b0afa9dc9e82315d:router/adaptor.py
	remote_rem = remote_info["num"] / remote_speed 
'''
