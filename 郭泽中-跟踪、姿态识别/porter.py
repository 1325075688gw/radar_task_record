from Kalman import Multi_Kalman_Tracker
import numpy as np
import json,time
from track_visual import visual
from matplotlib import pyplot as plt

plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False

'''
test
'''
filepath= 'one_people_updown_v1.json'
file=open(filepath)
data=json.load(file)

tracker=Multi_Kalman_Tracker(0.5,50,50,20,0.5,-3,3,8)


fig=plt.figure(figsize=(8,8))
ax=fig.add_subplot(111)
plt.ion()

all_heights=[]

for frame in data:
    point_list=data[frame]
    point_list=np.array(point_list)

    if len(point_list)!=0:
        clusters=point_list[:,:2]
        heights=point_list[:,-1]

    else:
        clusters=[]
        heights=[]

    tracker.nextFrame(clusters,heights,int(frame))

    postures=tracker.get_each_person_posture()
    locations=tracker.get_each_person_location()
    distances=tracker.get_each_person_distance()
    heights=tracker.get_each_person_height()
    raw_heights=tracker.get_each_person_raw_height()

    for id in heights:
        all_heights.append(heights[id])

    visual(ax,locations,postures,frame)

    plt.pause(0.0000001)
    plt.cla()

print(np.mean(all_heights),np.std(all_heights))