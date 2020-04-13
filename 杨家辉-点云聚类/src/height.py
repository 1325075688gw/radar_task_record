import math

class Height():

	block_length=0.25
	# delta_height=[1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.2599404864574784, 1.1344320084145112,
	#               1.1988682786418468, 1.1119083755798245, 0.9852783189205492, 0.7072995609122058, 0.6282585815117643,
	#               0.3319765558510601, 0.08778045385836619, 0.008194747981847827, -0.25343017749817864,
	#               -0.37420679559517334, -0.4872027432969972, -0.6316345401074752, -0.701356690112346,
	#               -0.875, -1.05, -1.225, -1.4024673937450403, -1.5452798970619157]
	delta_height=[1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.28, 1.22, 1.24, 1.06, 0.81, 0.67, 0.55, 0.47, 0.18,
				  0.04, -0.22, -0.43, -0.52, -0.58, -0.86, -1, -1.14, -1.3, -1.46, -1.44]

	@staticmethod
	def get_people_height_list(cl):
		cluster_center_point_list = cl.get_cluster_center_point_list()
		cluster_height_list = cl.get_height_list()
		people_height_list = []
		for height, center_point in zip(cluster_height_list,cluster_center_point_list):
			x = center_point[0]
			y = center_point[1]
			distance = math.sqrt(x*x+y*y)
			people_height_list.append(Height.add_delta(height,distance))
		return people_height_list
			
	@staticmethod
	def add_delta(height,distance):
		if int(distance/Height.block_length)>=len(Height.delta_height):
			return height+Height.delta_height[-1]
		return height+Height.delta_height[int(distance/Height.block_length)]
