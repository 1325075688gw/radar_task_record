import sys
import matplotlib.pyplot as plt

sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\郭泽中-跟踪、姿态识别")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\龚伟-点云检测")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\杨家辉-点云聚类\src")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\杨家辉-点云聚类\ui")

from Kalman import Multi_Kalman_Tracker
from cluster import Cluster
from points_filter import Points_Filter
from height import Height
import commo
import show


def cluster_points():
	tracker=Multi_Kalman_Tracker(float('inf'),30,-3,3,7)
	p_filter = Points_Filter(z_min = 0, z_max = 2.5, del_dopper = 0)
	cl = Cluster(eps = 0.25,minpts = 5,type='2D',min_cluster_count = 20)
	while 1:
		frame_data = commo.queue_for_count.get()
		p_filter.run_filter(frame_data)
		cl.do_clsuter(frame_data)
		clusters_center = cl.get_cluster_center_point_list()
		people_height_list = Height.get_people_height_list(cl)
		# heights = cl.get_height_list()
		frame_num = frame_data["frame_num"]
		tracker.nextFrame(clusters_center, people_height_list, frame_num)
		locations = tracker.get_each_person_location()
		postures = tracker.get_each_person_posture()
		commo.queue_for_show.put([frame_num, locations, postures])
def show_cluster_tracker():
	num = 0
	plt.ion()
	while 1:
		frame_num, positions, postures = commo.queue_for_show.get()
		print("frame_num:{0}".format(frame_num))
		num += 1
		if num < 4:
			continue
		else:
			num = 0
			# show.show2d_new(person_list, fig, frame_num)
			show.show_track(positions, postures, frame_num)
			plt.pause(0.00001)
			# plt.cla()
			plt.clf()
