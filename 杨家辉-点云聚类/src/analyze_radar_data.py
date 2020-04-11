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
import copy
from queue import Queue
queue_for_show = Queue()

sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\杨家辉-点云聚类")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\郭泽中-跟踪、姿态识别")
import hungary
from Kalman import Multi_Kalman_Tracker
import posture_analyze

import receive_uart_data
import commo




print("家规")

def cluster_points():
	flag = 1
	person_dict = {} #key:id号，value:Person对象
	tracker=Multi_Kalman_Tracker(float('inf'),5,-3,3,7)
	print("jianghui")
	while 1:
		# print("a:{0}".format(receive_uart_data.a))
		print("你为什么不跑了")
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
		points = pointfilter.pointfilter_z(points, 0, 3)
		points = pointfilter.dopperfilter(points, 0, 0)
		#cluster
		# tag = cluster_dbscan.dbscan(points,0.25,5,1,'2D')
		if points == []:
			continue
		tag = cluster_dbscan.dbscan_official(points, 0.25, 5, '2D')
		cluster_dict = getpoints.tag2cluster(points, tag)
		#
		cluster_dict = pointfilter.noisefilter(cluster_dict)
		# cluster_dict = pointfilter.countfilter(cluster_dict,20) #过滤点数过小的类
		#Identify people
		end_time = time.time() * 1000
		print("聚类需要:{0}\n".format(end_time - start_time))
		#track_begin
		clusters_center = getpoints.get_cluster_center(cluster_dict)
		print("fdd")
		tracker.nextFrame(clusters_center, frame_num)
		print("ggsgdf")
		
		#根据跟踪结果更新人的信息
		person_dict = people.update_people_status(person_dict,cluster_dict,tracker)
		print("ffffffffffsssssssssss")
		print("person_dict:{0}".format(person_dict))
		# if len(person_dict) == 0:
		# 	continue
		person_list = []
		for i in person_dict:
			person = copy.deepcopy(person_dict[i])
			person_list.append(person)
			
		positions = tracker.get_each_person_position()
		temp = [frame_num, positions, person_list]
		#track_end
		commo.queue_for_show.put(temp)
		print("queue_for_show长度1：{0}".format(commo.queue_for_show.qsize()))
# return person_list
	#concrete_cluster = getpoints.get_concrete_cluster(cluster_dict)
def show_cluster_tracker():
	fig = plt.figure(figsize=(10, 10))
	num = 0
	while 1:
		print("queue_for_show长度2：{0}".format(commo.queue_for_show.qsize()))
		temp = commo.queue_for_show.get()
		print("temp{0}".format(temp))
		frame_num, positions, person_list = temp
		print("position：{0}".format(positions))
		print("person_list：{0}".format(person_list))
		print("queue_for_show长度3：{0}".format(commo.queue_for_show.qsize()))
		print("show_frame_num:{0}".format(frame_num))

		num += 1
		if num < 3:
			print("fffffffffffffffsssssssssssssssssssssss")
			continue
		else:
			num = 0
			print("gffffffffffffffgere")
			show.show2d_new(person_list, fig, frame_num)
			show.show_track(positions, fig, frame_num)
			print("fsfsdfsdfsdfd")
			plt.pause(0.0001)
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
