import sys
sys.path.append('./userinterface')

import matplotlib.pyplot as plt  
import json
import time
import threading
from queue import Queue


import getpoints 
import pointfilter
import cluster_dbscan
import show
from people import Person
import people

signal = True
frame_data_queue = Queue()
frame_people = Queue()
frame_people_qlock = threading.Lock()


def read_data():
	filename = './new_points_4_7_v3.json'
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		for i in temfile:
			frame_data_queue.put(temfile[i])
			
			
def analyze_radar_data():
	'''
	Args:
	frame_data:
			{"frame_num": 1, 
			 "time_stamp": 1585985633768, 
			 "point_num": 126, 
			 "point_list": [{"pid": 1, 
			                 "x": -3.3896964194420462, 
			                 "y": 1.9897085734888438, 
			                 "z": -3.489718823675718, 
			                 "dopper": 0.6546400174847804, 
			                 "snr": 0.04479999799728396},...]
			}
	'''
	global signal
	while signal:
		if not frame_data_queue.empty():
			frame_data = frame_data_queue.get()
		else:
			break
		frame_points = getpoints.get_frame_points(frame_data)
		points = []
		frame_num = 0
		for i in frame_points:
			frame_num = i
			points = frame_points[i]
		#point filter
		points = pointfilter.pointfilter_y(points, 0, 10)
		points = pointfilter.dopperfilter(points, 0, 0)
		#cluster
		tag = cluster_dbscan.dbscan(points,0.25,5,1,'2D')
		cluster_dict = getpoints.tag2cluster(points, tag)
		#
		cluster_dict = pointfilter.noisefilter(cluster_dict)
		cluster_dict = pointfilter.countfilter(cluster_dict,20) #过滤点数过小的类
		#Identify people
		person_list = people.transform_cluster_to_people(cluster_dict)
		if not frame_people.full():
			frame_people_qlock.acquire()
			frame_people.put(person_list)
			frame_people_qlock.release()
		else:
			sleep(0.5)
		#concrete_cluster = getpoints.get_concrete_cluster(cluster_dict)

def show_people(person_list,fig):
	show.show2d_new(person_list, fig)

def show_frame(frame_dict):
	person_list = count_people(frame_dict)
	show_people(person_list, fig)
	plt.pause(0.04)
	plt.clf()

if __name__ == "__main__":
	signal
	t1 = threading.Thread(target=analyze_radar_data)
	t2 = threading.Thread(target=read_data)
	t2.start()
	time.sleep(0.5)
	t1.start()
	fig = plt.figure(figsize=(10,10))
	while True:
		if not frame_people.empty():
			plt.clf()
			frame_people_qlock.acquire()
			person_list = frame_people.get()
			frame_people_qlock.release()
			show_people(person_list,fig)
			plt.pause(0.04)
		else:
			signal = False

'''
if __name__ == "__main__":
	filename = './new_points_4_7_v3.json'
	fig = plt.figure(figsize=(10,10))
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		for i in temfile:
			person_list = analyze_radar_data(temfile[i])
			show_people(person_list,fig)
			plt.pause(0.04)
			plt.clf()
'''
