import sys
import matplotlib.pyplot as plt

sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\郭泽中-跟踪、姿态识别")
sys.path.append(r"C:\Users\Administrator\Documents\Tencent Files\3257266576\FileRecv\radar_task_record\龚伟-点云检测")


from Kalman import Multi_Kalman_Tracker
from cluster import Cluster
from points_filter import Points_Filter
import commo
import copy
import show


def cluster_points():
	global queue_for_show
	print("呵呵哈哈哈")
	person_dict = {} #key:id号，value:Person对象
	tracker=Multi_Kalman_Tracker(float('inf'),30,-3,3,7)
	p_filter = Points_Filter(z_min = 0, z_max = 2.5, del_dopper = 0)
	cl = Cluster(eps = 0.25,minpts = 5,type='2D',min_cluster_count = 20)
	while 1:
		# with commo.condition_for_count:
		# print("queue_for_count长度1：{0}".format(commo.queue_for_count.qsize()))
		# commo.condition_for_count.notify_all()
		# commo.condition_for_count.wait()
		frame_data = commo.queue_for_count.get()
		# print("queue_for_count长度2：{0}".format(commo.queue_for_count.qsize()))

		# continue

		p_filter.run_filter(frame_data)
		cl.do_clsuter(frame_data)
		clusters_center = cl.get_cluster_center_point_list()
		heights = cl.get_height_list()
		frame_num = frame_data["frame_num"]
		tracker.nextFrame(clusters_center, heights, frame_num)
		locations = tracker.get_each_person_location()
		postures = tracker.get_each_person_posture()
		commo.queue_for_show.put([frame_num, locations, postures])
		# print("queue_for_show长度2：{0}".format(commo.queue_for_show.qsize()))


def show_cluster_tracker():
	# fig = plt.figure(figsize=(7, 6))
	num = 0
	# ax = fig.add_subplot(111)
	plt.ion()
	while 1:
		# print("queue_for_show长度1：{0}".format(commo.queue_for_show.qsize()))
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
