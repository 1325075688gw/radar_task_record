
def snrfilter(points, snr_limit):
	res = []
	for point in points:
		if point[3] >= snr_limit:
			res.append(point)
	return res     

def dopperfilter(points, low, high):
	res = []
	for point in points:
		if point[4] > high or point[4] < low:
			res.append(point)
	return res
	
def pointfilter_z(points, zmin, zmax):
	filterpoints = []
	for point in points:
		if point[2] > zmin and point[2] < zmax:
			filterpoints.append(point)
	return filterpoints

def pointfilter_y(points, ymin, ymax):
	filterpoints = []
	for point in points:
		if point[1] > ymin and point[1] < ymax:
			filterpoints .append(point)
	return filterpoints

def noisefilter(cluster_dict):
	try:
		cluster_dict.pop(-1)
	except:
		pass
	return cluster_dict
	
def countfilter(cluster_dict,num):
	res = {}
	tem_list = []
	for i in cluster_dict:
		if i == -1:
			res[-1] = cluster_dict[-1]
		else:
			if len(cluster_dict[i]) > num:
				tem_list.append(cluster_dict[i])
	for i in range(len(tem_list)):
		res[i] = tem_list[i]
	return res

