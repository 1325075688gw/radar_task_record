import json
from commo import frame_data_queue

def read_data():
	filename = r'./data/one_person_upanddown_v1.json'
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		#print(temfile)
		for i in temfile:
			#print(temfile[i])
			frame_data_queue.put(temfile[i])
