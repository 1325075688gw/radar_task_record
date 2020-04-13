import matplotlib.pyplot as plt
import numpy as np   
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle


import drawcube
POSTURES_DICT = {1:"站立", 2:"坐着", 3:"躺着", 4:"行走"}


def draw_circle(ax,center_point,r):
	'''Draw a circle on the plot
	
	Args:
		ax: a subplot of figure
		center_point: Center of circle
		r: radius of circle
	'''
	cir1 = Circle(xy = (center_point[0], center_point[1]), radius=r, alpha=0.5)
	ax.add_patch(cir1)

def show_for_cluster(cluster_show, fig):
	'''show for Cluster
	
	 
	'''
	colValue = ['gray', 'r', 'b', 'y', 'c', 'b', 'k', 'm','w']
	#ax=Axes3D(fig) 
	ax = fig.add_subplot(111)
	i = 0
	for cluster in cluster_show['cluster']:
		cluster_points = cluster['points']
		X = np.array(cluster_points)
		#print(X[:,0])
		label = 'Person' + str(cluster['cluster_id']+1) + ('身高为：%.2f'%cluster['height'])
		ax.scatter(X[:,0],X[:,1],c=colValue[(i+1)%len(colValue)],label=label + '\n' + "当前检测到{0}个点".format(len(cluster_points)), marker = '.')
		if i != -1:
			mean = np.mean(cluster_points, axis=0)
			draw_circle(ax,[cluster['center_point'][0],cluster['center_point'][1]],0.2)
		i = i + 1
	ax.scatter(0,0,c = 'g')
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	plt.xlim(-3,3)
	plt.ylim(0,6)
	#plt.title("people_count")
	plt.plot(label="")
	if i > 0:
		ax.legend(loc = 'upper left')


def show_track(locations, postures, frame_num):
	plt.xlim(-3, 3)
	plt.ylim(0, 7)
	plt.title('第' + str(frame_num) + '帧')
	plt.plot(0, 0, 'o', label='雷达', markersize=25)
	for person in locations:
		location = locations[person]
		posture = postures[person]
		plt.plot(location[0], location[1], 'o', label='人' + str(person), markersize=40)
		plt.text(location[0], location[1], POSTURES_DICT[posture])
	plt.legend(	markerscale=1.0 / 10)
