import json
from commo import frame_data_queue

def read_data():
	filename = r'./new_points_2_6.json'
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		#print(temfile)
		for i in temfile:
			#print(temfile[i])
			frame_data_queue.put(temfile[i])
