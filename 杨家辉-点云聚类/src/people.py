import sys
import numpy as np 
import heapq

sys.path.append("../郭泽中-跟踪、姿态识别")
from height_kalman import HeightKalman
from posture_analyze import Posture
import Kalman

class Person():
	def __init__(self, points, id):
		self.id = id
		self.points = points
		self.length = 0
		self.width = 0
		self.height = 1.7
		self.current_height = 0
		self.x = 0
		self.y = 0
		self.z = 0
		self.compute_height_count = 0
		self.height_kal = HeightKalman()  #卡尔曼滤波计算身高
		self.posture = Posture(30)
		self.compute_person_attributes()
		
	def compute_person_attributes(self):
		xyz_mean = np.mean(self.points, axis=0)
		xyz_max = np.max(self.points, axis=0)
		xyz_min = np.min(self.points, axis=0)
		self.x = xyz_mean[0]
		self.y = xyz_mean[1]
		self.z = xyz_mean[2]
		self.length = xyz_max[0] - xyz_min[0]
		self.width = xyz_max[1] - xyz_min[1]
		self.cal_current_height()
		
		
	def is_person(self):
		if(self.current_height < 0.3):
			return 0
		return 1

	def cal_current_height(self):
		'''计算一帧当中人的身高（不是实际身高）

		'''
		k = int(len(self.points) * 0.1) + 1
		z_list = [self.points[i][2] for i in range(k)]
		print(sum(z_list))
		tem_height = 0
		sum_list = sum(z_list)
		for i in range(k):
			tem_height += z_list[i] * z_list[i] / sum_list
		self.current_height = tem_height
	
	def cal_actual_height(self):
		
		if self.compute_height_count >= 2000:
			return
		#使用kalman滤波迭代计算身高
		self.height_kal.cal_height(self.current_height) 
		self.height = self.height_kal.s
		self.compute_height_count += 1
		print("更新后的身高为：%f"%self.height)
	
	def update(self, points):
		self.points = points
		self.compute_person_attributes()
		print("当前高度：%f"%self.current_height)
		if self.current_height>0.5 and self.current_height<2.3:
			self.cal_actual_height()
		

def transform_cluster_to_people(cluster_dict):
	person_list = []
	for i in cluster_dict:
		tem_person = Person(cluster_dict[i])
		if tem_person.is_person():
			person_list.append(tem_person)
	return person_list

#根据跟踪结果，将点云和人对应起来，并根据点云信息更新人的状态
def update_people_status(person_dict, cluster_dict, tracker):
	for id in tracker.d:
		#将点云和人对应
		index = tracker.d[id]
		print("index{0}".format(index))
		print("dict:{0}".format(cluster_dict))
		if id not in person_dict.keys():
			person_dict[id] = Person(cluster_dict[index],id)
		else:
			person_dict[id].update(cluster_dict[index])
	#删除已经不存在的人
	for id in tracker.deleted_tracks:
		person_dict.pop(id)
	people_v_dict = tracker.get_each_person_velocity()
	if len(people_v_dict) > 0:
		print(people_v_dict)
		for id in people_v_dict:
			print(person_dict)
			print(id)
			height_rate = person_dict[id].current_height/person_dict[id].height
			person_dict[id].posture.get_posture(height_rate,people_v_dict[id])
			
	return person_dict
