import matplotlib.pyplot as plt
import numpy as np   
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle
import time
import sys
sys.path.append(r"F:\radar_soft\radar_task_record\龚伟_点云检测")
import commo


import drawcube
# from ..analyze_radar_data import queue_for_show

def draw_circle(ax,center_point,r):
	'''Draw a circle on the plot
	
	Args:
		ax: a subplot of figure
		center_point: Center of circle
		r: radius of circle
	'''
	cir1 = Circle(xy = (center_point[0], center_point[1]), radius=r, alpha=0.5)
	ax.add_patch(cir1)

def show2d_new(person_list, fig, frame_num):
	print("ffffffffffffffffffffff")
	colValue = ['gray', 'r', 'b', 'y', 'c', 'b', 'k', 'm', 'w']
	# ax=Axes3D(fig)
	ax = fig.add_subplot(121)
	i = 0
	for person in person_list:
		cluster_points = person.points
		X = np.array(cluster_points)
		# print(X[:,0])
		label = 'Person' + str(i + 1)
		ax.scatter(X[:, 0], X[:, 1], c=colValue[(i + 1) % len(colValue)],
				   label=label + '\n' + "当前检测到{0}个点".format(len(cluster_points)), marker='.')
		if i != -1:
			mean = np.mean(cluster_points, axis=0)
			draw_circle(ax, [mean[0], mean[1]], 0.2)
		i = i + 1
	ax.scatter(0, 0, c='g')
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	plt.xlim(-3, 3)
	plt.ylim(0, 6)
	plt.plot(label="")
	ax.set_title('当前是第:' + str(frame_num) + '帧')
	ax.legend(loc='upper left')

def show2d(cluster_concrete_dict, fig):
	'''show 2d 
	
	 
	'''
	colValue = ['gray', 'r', 'b', 'y', 'c', 'b', 'k', 'm','w']
	#ax=Axes3D(fig) 
	ax = fig.add_subplot(212)
	for i in cluster_concrete_dict:
		cluster_points = cluster_concrete_dict[i]['points']
		X = np.array(cluster_points)
		#print(X[:,0])
		if i == -1:
			label = 'noise'
		else:
			label = 'Person' + str(i+1)
		ax.scatter(X[:,0],X[:,1],c=colValue[(i+1)%len(colValue)],label=label + '\n' + "当前检测到{0}个点".format(len(cluster_points)), marker = '.')
		if i != -1:
			mean = np.mean(cluster_points, axis=0)
			draw_circle(ax,[mean[0],mean[1]],0.2)
	ax.scatter(0,0,c = 'g')
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	plt.xlim(-3,3)
	plt.ylim(0,6)
	plt.plot(label="")
	ax.legend(loc = 'upper left')


def show_track(positions, fig, frame_num):
	print("方法")
	ax=fig.add_subplot(122)
	plt.xlim(-3, 3)
	plt.ylim(0, 6)
	ax.set_title('当前帧有:'+str(len(positions.keys()))+'个人' + ' == 当前是第:' + str(frame_num) + '帧')
	ax.legend(markerscale=1.0/10)
	for person in positions:
		position=positions[person]
		ax.plot(position[0],position[1],'o',markersize=40,label=str(person))
def show3d(cluster_concrete_dict, fig):
	'''
	显示图像,比show_cluster多了标签
	'''
	colValue = ['gray', 'r', 'b', 'y', 'c', 'b', 'k', 'm','w']
	#ax=Axes3D(fig) 
	ax = fig.add_subplot(211, projection='3d')
	for i in cluster_concrete_dict:
		cluster_i = cluster_concrete_dict[i]
		X = np.array(cluster_i['points'])
		if i == -1:
			label = 'noise'
		else:
			label = 'Person' + str(i+1)
			#加上方差、中心点、长宽高
			label = label + '\n中心点:' + str(cluster_i['center_point'])
			label = label + '\n' + ("方差x:%.3f，y:%.3f，z:%.3f"
			%(cluster_i['var_x'],cluster_i['var_y'],cluster_i['var_z']))
			label = label + '\n' + ("身高：%.1f,长：%.2f,宽:%.2f"
			%(cluster_i['height'],cluster_i['length'],cluster_i['width']))
		ax.scatter(X[:,0],X[:,1],X[:,2],c=colValue[(i+1)%len(colValue)],label=label, marker = '.')
		#计算dx,dy,dz来画立方体
		drawcube.plot_linear_cube(cluster_i['center_point'][0]-cluster_i['length']/2,
		cluster_i['center_point'][1]-cluster_i['width']/2,0,
		cluster_i['length'],cluster_i['width'],cluster_i['height'],ax,color = 'y')
	
	ax.scatter(0,0,1.8,c = 'g')
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.set_zlabel('z')
	#plt.xlim(-0.5,1.75)
	#plt.ylim(-0.5,1.75)
	#plt.zlim(-3,3)
	#plt.title('three_pp_stand')
	ax.legend(loc = 'upper left', fontsize=8)
	

