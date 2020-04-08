import numpy as np 

class Person():
	def __init__(self, points):
		self.id = -1
		self.points = points
		self.length = 0
		self.width = 0
		self.height = 0
		self.current_height = 0
		self.x = 0
		self.y = 0
		self.compute_height_count = 0
		self.compute_person_attributes()
		
	def compute_person_attributes(self):
		xyz_mean = np.mean(self.points, axis=0)
		xyz_max = np.max(self.points, axis=0)
		xyz_min = np.min(self.points, axis=0)
		self.x = xyz_mean[0]
		self.y = xyz_mean[1]
		self.length = xyz_max[0] - xyz_min[0]
		self.width = xyz_max[1] - xyz_min[1]
		self.current_height = xyz_max[2]
		
	def is_person(self):
		if(self.current_height < 0.3):
			return 0
		return 1

def transform_cluster_to_people(cluster_dict):
	person_list = []
	for i in cluster_dict:
		tem_person = Person(cluster_dict[i])
		if tem_person.is_person():
			person_list.append(tem_person)
	return person_list
