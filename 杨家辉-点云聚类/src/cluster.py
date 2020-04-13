import numpy as np  # 数据结构
import sklearn.cluster as skc

class Cluster():
	def __init__(self,eps,minpts,type,min_cluster_count):
		self.eps = eps
		self.minpts = minpts
		self.type = type
		self.min_cluster_count = min_cluster_count
		self.frame_cluster_dict = {}
		'''
		frame_cluster_dict
		{
			'frame_num':
			'cluster':[
						{'cluster_id'
						...
						},
						...
					  ]
		}
		'''
	def dbscan_official(self, data):
		if data == []:
			return []
		X = np.array(data)
		if self.type == '2D':
			X = X[:,:2]
		elif self.type == '3D':
			X = X[:,:3]
		db = skc.DBSCAN(eps=self.eps, min_samples=self.minpts).fit(X)
		return db.labels_
	
	def frame_data_to_cluster_points(self,frame_data):
		points = []
		for data in frame_data['point_list']:
			point = [data['x'],data['y'],data['z'],data['dopper'],data['snr']]
			points.append(point)
		return points
	
	def cluster_filter_by_noise(self, tem_dict):
		#去掉噪声
		try:
			tem_dict.pop(-1)
		except:
			pass
	
	def cluster_filter_by_count(self, tem_dict):
		#去除点数较少的类
		del_list = []
		for i in tem_dict:
			if len(tem_dict[i]) < self.min_cluster_count:
				del_list.append(i)
		for key in del_list:
			tem_dict.pop(key)
	
	def compute_cluster_height(self, points):
		k = int(len(points) * 0.1) + 1 #计算前10%点
		z_list = [points[i][2] for i in range(k)]
		return round(np.mean(z_list),3)
	
	def compute_cluster_attr(self, tem_dict):
		cluster_list = []
		k = 0
		for i in tem_dict:
			cluster_dict = {}
			center_point = np.mean(tem_dict[i], axis=0)
			varlist = np.var(tem_dict[i], axis=0)
			cluster_dict['cluster_id'] = k
			cluster_dict['points_num'] = len(tem_dict[i])
			cluster_dict['center_point'] = [center_point[0],center_point[1],center_point[2]]
			cluster_dict['var_x'] = varlist[0]
			cluster_dict['var_y'] = varlist[1]
			cluster_dict['var_z'] = varlist[2]
			cluster_dict['height'] = self.compute_cluster_height(tem_dict[i])
			cluster_dict['points'] = tem_dict[i]
			cluster_list.append(cluster_dict)
			k += 1
		return cluster_list
			
	def points_to_cluster_by_tag(self, points, tag):
		tem_dict = {}
		#按照类别将点分类
		key_list = []
		for i in tag:
			if i not in key_list:
				key_list.append(i)
		#key_list = sorted(key_list)
		for i in key_list:
			tem_dict[i] = []
		for t, point in zip(tag, points):
			tem_dict[t].append(point)
			
		#过滤
		self.cluster_filter_by_noise(tem_dict)
		self.cluster_filter_by_count(tem_dict)
		#tem_dict = sorted(tem_dict.items(), key = lambda x : x[0]) #按key排序
		cluster_list = self.compute_cluster_attr(tem_dict)
		return cluster_list
	
	def get_cluster_center_point_list(self):
		cluster_center_point_list = []
		for cluster in self.frame_cluster_dict['cluster']:
			center_point = [cluster['center_point'][0],cluster['center_point'][1]]
			cluster_center_point_list.append(center_point)
		return cluster_center_point_list
	
	def get_height_list(self):
		cluster_height_list = []
		for cluster in self.frame_cluster_dict['cluster']:
			height = cluster['height']
			cluster_height_list.append(height)
		return cluster_height_list
	
	def do_clsuter(self, frame_data):
		self.frame_cluster_dict['frame_num'] = frame_data['frame_num']
		points = self.frame_data_to_cluster_points(frame_data)
		tag = self.dbscan_official(points)
		self.frame_cluster_dict['cluster'] = self.points_to_cluster_by_tag(points, tag)
		#print(self.frame_cluster_dict)

