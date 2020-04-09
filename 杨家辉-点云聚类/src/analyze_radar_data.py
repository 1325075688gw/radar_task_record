import sys
sys.path.append('./userinterface')

import matplotlib.pyplot as plt  
import json

import getpoints 
import pointfilter
import cluster_dbscan
import time
import numpy as np
import sklearn.cluster as skc
# import show
from userinterface import show
from people import Person
import people
from queue import Queue
queue_for_show = Queue()

sys.path.append(r"F:\radar_soft\radar_task_record\龚伟_点云检测")
sys.path.append(r"F:\radar_soft\radar_task_record\郭泽中_跟踪、姿态识别")
import Kalman
import receive_uart_data
import commo

def cluster_points():
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
	# frame_data = receive_uart_data.queue_for_count.get()
	flag = 1
	tracker = Kalman.Multi_Kalman_Tracker(float('inf'), 5)
	while 1:
		# print("a:{0}".format(receive_uart_data.a))
		print("queue_for_count长度：{0}".format(commo.queue_for_count.qsize()))
		frame_data = commo.queue_for_count.get()
		print("queue_for_count长度2：{0}".format(commo.queue_for_count.qsize()))
		start_time = time.time() * 1000
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
		# tag = cluster_dbscan.dbscan(points,0.25,5,1,'2D')
		if points == []:
			continue
		tag = cluster_dbscan.dbscan_official(points, 0.25, 5, '2D')
		cluster_dict = getpoints.tag2cluster(points, tag)
		#
		# cluster_dict = pointfilter.noisefilter(cluster_dict)
		# cluster_dict = pointfilter.countfilter(cluster_dict,20) #过滤点数过小的类
		#Identify people
		end_time = time.time() * 1000
		print("聚类需要:{0}\n".format(end_time - start_time))
		person_list = people.transform_cluster_to_people(cluster_dict)
		#track_begin
		clusters = []
		for p in person_list:
			cluster_center = [p.x,p.y,p.z]
			clusters.append(cluster_center)
		tracker.nextFrame(clusters, frame_num)
		positions = tracker.get_each_person_position()
		temp = [positions, person_list]
		#track_end
		commo.queue_for_show.put(temp)
		print("queue_for_show长度1：{0}".format(commo.queue_for_show.qsize()))
# return person_list
	#concrete_cluster = getpoints.get_concrete_cluster(cluster_dict)
def show_cluster_tracker():
	fig = plt.figure(figsize=(10, 10))
	while 1:
		print("queue_for_show长度2：{0}".format(commo.queue_for_show.qsize()))
		temp = commo.queue_for_show.get()
		print("temp{0}".format(temp))
		position, person_list = temp
		print("position：{0}".format(position))
		print("person_list：{0}".format(person_list))

		print("queue_for_show长度3：{0}".format(commo.queue_for_show.qsize()))
		show.show2d_new(person_list,fig)
		show.show_track(position, fig)
		plt.pause(0.001)
		plt.clf()
#
# if __name__ == "__main__":
# 	filename = './new_points_4_7_v3.json'
# 	fig = plt.figure(figsize=(10,10))
# 	with open(filename, 'r', encoding='utf-8') as f:
# 		temfile = json.load(f)
# 		for i in temfile:
# 			person_list = count_people(temfile[i])
# 			show_people(person_list,fig)
# 			plt.pause(0.04)
# 			plt.clf()
