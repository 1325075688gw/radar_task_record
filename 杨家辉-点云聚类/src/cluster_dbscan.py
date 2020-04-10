import json
import random
import numpy as np  # 数据结构
import sklearn.cluster as skc
import math
import matplotlib.pyplot as plt  # 可视化绘图
from mpl_toolkits.mplot3d import Axes3D
#import test

#下一步修改方案，按照扇面进行搜索范围判定

def dict_z(p1,p2):
    return abs(p1[2]-p2[2])

def dict_xy(p1,p2):
	'''
	计算三维点p1,p2的平面距离
	'''
	return math.sqrt((np.power((p1[0]-p2[0]),2) + np.power((p1[1]-p2[1]),2)))

def dict_xyz(p1,p2):
	return math.sqrt((np.power((p1[0]-p2[0]),2) + np.power((p1[1]-p2[1]),2)+ np.power((p1[2]-p2[2]),2)))

def judge_arrange(p1,p2,eps,high,type):
	res = 1
	if type == '3D':
		return dict_xyz(p1,p2) < eps
	if type == '2D':
		res = dict_xy(p1,p2) <= eps
	if type == 'cylinder':
		res = res and dict_z(p1, p2) <= high
	return res

def getneighbor(data, p, eps, high, type):
	neighbor = []
	for i in range(len(data)):
		dict_bool = judge_arrange(data[i], data[p],eps, high ,type)
		if dict_bool:
			neighbor.append(i)
	return neighbor

def expand(data, res, neighbor, k, unvisited, eps, minpts, high, type):
	for i in neighbor:
		if res[i] == -1:
			res[i] = k
		if i in unvisited:
			unvisited.remove(i)
			ineighbor = getneighbor(data, i, eps, high, type)
			if len(ineighbor) >= minpts:
				expand(data, res, ineighbor, k, unvisited, eps, minpts, high,type)

def dbscan(data,eps,minpts,high,type='2D'):
	''''''
	num = len(data)
	unvisited = [i for i in range(num)]
	res = [-1 for i in range(num)] #输出点的类号[]，-1为噪声点
	k = -1
	while len(unvisited) > 0:
		p = unvisited[0]
		#p = random.choice(unvisited)
		unvisited.remove(p)
		neighbor = getneighbor(data, p, eps, high, type); #获得p领域内的点
		if len(neighbor) >= minpts:
			k = k + 1
			expand(data, res ,neighbor, k, unvisited, eps, minpts, high, type)
	return np.array(res)


def dbscan_official(data,eps,minpts,type='2D'):
	X = np.array(data)
	if type == '2D':
		X = X[:,:2]
	elif type == '3D':
		X = X[:,:3]
	db = skc.DBSCAN(eps=0.25, min_samples=5).fit(X)
	return db.labels_
	
'''	
if __name__ == '__main__':	
	allpoints = test.data2points2(r'data2020.04.01/two_pp/3/two_pp_sit/point_cloud_list.json')
	for points in allpoints:
		print(mydbscan(points,0.3,3,0.3))
'''
