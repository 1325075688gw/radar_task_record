import cluster_sta
import json
import numpy as np

def get_cluster_center(cluster_dict):
	center_point_list = []
	i = 0
	if len(cluster_dict) == 0:
		return center_point_list
	while i <= max(cluster_dict):
		center_point = np.mean(cluster_dict[i], axis=0)
		center_point_list.append([center_point[0],center_point[1],center_point[2]])
		i += 1
	return center_point_list

def get_frame_points(frame_data):
	points = []
	point_list = frame_data['point_list']
	for data in point_list:
		point = [data['x'], data['y'], data['z'],data['snr'],data['dopper']]
		points.append(point)
	frame_points = {}
	frame_points[frame_data['frame_num']] = points
	return frame_data['frame_num'], points

def get_json_points(filename):
	'''Read json data and return data in correct format.
	
	Args:
	filename: The name of json file. For example:
		{"frame_num_1": 
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
		...
		}
	
	Returns:
		A list of data points of multi_frame. For example:
		
		list_example = [
						[[1,1,1,0.5],[1,1,2,0.7],[1,2,3,1.3],...],
						...
					   ]
		
		Each frame_list in list_example represents a frame of points. 
		Each point_list in frame_list represents coordinates of the point
		(such as (1,1,1))and snr of the point (such as 0.5).
	'''
	allpoints = []
	with open(filename, 'r', encoding='utf-8') as f:
		temfile = json.load(f)
		for i in temfile:
			points = []
			point_list = temfile[i]['point_list']
			for data in point_list:
				point = [data['x'], data['y'], data['z'],data['snr'],data['dopper']]
				points.append(point)
			allpoints.append(points)
	return allpoints

def get_simple_cluster(points, tags):
	'''Sort points by tags.
	
	Args:
	points: A frame of points. For example:
	
		[[1,1,1,0.5],[1,1,2,0.7],[1,2,3,1.3],...]
	
	tags: The tags of the points.
	
		[0,0,1,...]
	
	Returns:
		A dict of points which have been sorted by tags. For example:
		
		{'0':[[1,1,1,0.5],[1,1,2,0.7]],
		 '1':[1,2,3,1.3],
		 ...
		}
		
	'''
	cluster_dict = {}
	for t in tags:
		cluster_dict[t] = []
	for t, point in zip(tags, points):
		cluster_dict[t].append(point)
	return cluster_dict

def get_concrete_cluster(cluster_dict):
	'''compute the attributes of cluster.
		
	Returns:
		A dict of points which have been sorted by tags and the details 
		of the cluser. For example:
		
		{'0':{
			'points': [[1,1,1,0.5],[1,1,2,0.7]],
			'center_point': [1,1,1.5],
			'var_x': 0,
			'var_y': 0,
			'var_z': 0.3535,
			'height': 2.8,
			'length': 0,
			'width': 0
			 },
		 '1':[1,2,3,1.3],
		 ...
		}
	'''
	cluster_concrete_dict = {}
	for i in cluster_dict:
		attr_dict = {}
		mean = cluster_sta.cluster_mean(cluster_dict[i])
		vardict = np.var(cluster_dict[i], axis=0)
		xyz_height = cluster_sta.xyzheight(cluster_dict[i])
		attr_dict['points'] = cluster_dict[i]
		attr_dict['center_point'] = [mean[0],mean[1],mean[2]]
		attr_dict['var_x'] = vardict[0]
		attr_dict['var_y'] = vardict[1]
		attr_dict['var_z'] = vardict[2]
		attr_dict['height'] = xyz_height[3]
		attr_dict['length'] = xyz_height[0]
		attr_dict['width'] = xyz_height[1]
		cluster_concrete_dict[i] = attr_dict
	return cluster_concrete_dict
	
def tag_to_cluster(points, tag):
	'''
	根据points和tag将每一帧的点按聚类类别分类，输出格式为{'0':[[point1][point2]],'1':[[][]]}
	'''
	output = {}
	for t in tag:
		output[t] = []
	for t, point in zip(tag, points):
		output[t].append(point)
	return output
	
