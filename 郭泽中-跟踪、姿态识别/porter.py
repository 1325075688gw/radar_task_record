from Kalman import Multi_Kalman_Tracker
import numpy as np



'''
test
'''
x=[1,2,3]
y=[1,2,3]
z=[1,2,3]

clusters=np.array([x,y,z]).T
tracker=Multi_Kalman_Tracker(float('inf'),clusters,5,1)
print(tracker.get_each_person_position())

x=[2,3,4,5]
y=[2,3,4,5]
z=[2,3,4,5]
clusters = np.array([x, y, z]).T

for i in range(10):
    tracker.nextFrame(clusters+i,2+i)
    print(tracker.get_each_person_position())
    print(tracker.get_point_distribution())