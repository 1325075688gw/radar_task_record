import sys
sys.path.append("./src")
sys.path.append("./ui")
import threading
from queue import Queue
import copy
import matplotlib.pyplot as plt
import numpy as np

from cluster import Cluster
from points_filter import Points_Filter
from commo import frame_data_queue
from read_file_data import read_data
import show
from height import Height

cluster_show_queue = Queue()


def test_point_filter():
	p_filter = Points_Filter(z_min = 0, z_max = 2.5, del_dopper = 0)
	cl = Cluster(eps = 0.25,minpts = 5,type='2D',min_cluster_count = 20)
	all_height = []
	while 1:
		frame_data = frame_data_queue.get()
		p_filter.run_filter(frame_data)
		cl.do_clsuter(frame_data)
		frame_cluster_dict = copy.deepcopy(cl.frame_cluster_dict)
		

		people_height_list = Height.get_people_height_list(cl)
		'''
		if people_height_list != []:
			height_dict = {}
			height_dict[cl.get_height_list()[0]] = people_height_list[0]
			print(height_dict)
			all_height.append(height_dict)
			'''
		#print(np.mean(all_height))
		#print(np.var(all_height))
		cluster_show_queue.put(frame_cluster_dict)
		#print(cl.get_cluster_center_point_list())
		#print(cl.get_height_list())


if __name__ == "__main__":
	t1 = threading.Thread(target=read_data)
	t2 = threading.Thread(target=test_point_filter)
	t1.start()
	t2.start()
	fig = plt.figure(figsize=(10,10))
	while 1:
		plt.clf()
		cluster_show = cluster_show_queue.get()
		show.show_for_cluster(cluster_show,fig)
		plt.title("第%d帧"%cluster_show['frame_num'])
		plt.pause(0.04)

