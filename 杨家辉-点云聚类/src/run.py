import sys
sys.path.append('./userinterface')

import matplotlib.pyplot as plt  
import json

import getpoints 
import pointfilter
import cluster_dbscan
import show
from people import Person
import people



def count_people(frame_data):
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
	return person_list
	#concrete_cluster = getpoints.get_concrete_cluster(cluster_dict)

def show_people(person_list,fig):
	show.show2d_new(person_list, fig)

def show_frame(frame_dict):
	person_list = count_people(frame_dict)
	show_people(person_list, fig)
	plt.pause(0.04)
	plt.clf()

if __name__ == "__main__":
	filename = './new_points_4_7_v3.json'
	fig = plt.figure(figsize=(10,10))
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		for i in temfile:
			person_list = count_people(temfile[i])
			show_people(person_list,fig)
			plt.pause(0.04)
			plt.clf()
