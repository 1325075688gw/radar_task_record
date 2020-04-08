import numpy as np  # 数据结构


def cluster_mean(points):
	return np.mean(points, axis=0)

def xyzheight(points):
	'''
		compute length, width, dz and height
	'''
	rmax = np.max(points, axis=0)
	rmin = np.min(points, axis=0)
	return [rmax[0]-rmin[0],rmax[1]-rmin[1],rmax[2]-rmin[2],rmax[2]]
