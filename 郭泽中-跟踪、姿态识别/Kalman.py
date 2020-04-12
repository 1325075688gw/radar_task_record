import numpy as np
from Track import Track
from hungary import hungary
import math

#v5.0
class Multi_Kalman_Tracker():

    M=30
    rate=0.5

    #初始化
    def __init__(self,G,min_last_time,xmin,xmax,ymax):
        self.measurementMatrix=np.array([[1, 0,], [0, 1]])    #H
        self.transitionMatrix=np.array([[1, 0], [0, 1]])  #状态转移矩阵
        self.processNoiseCov=np.array([[1, 0], [0, 1]]) * 0.03    #过程噪声矩阵
        self.B=np.array([[1, 0], [0, 1]])    #B
        self.d = dict()  # 存储当前帧中为轨迹分配的类
        self.tracks = dict()  # 所有轨迹
        self.deleted_tracks = []  # 在这一帧中被删除的轨迹id的集合
        self.clusters = []  # 当前帧中的点
        self.not_detected_times=dict()

        self.frame = 0  # 当前帧号
        self.successive_times = 0  # 用于判断是否生成新轨迹
        self.plength = 2

        self.heights=[]    #当前帧中的每个人的身高
        self.min_last_time=min_last_time
        self.G=G    #同一条轨迹在相邻两帧之间最大的移动距离
        self.xmin=xmin  #空间最小横向坐标
        self.xmax=xmax  #空间最大横向坐标
        self.ymax=ymax  #空间的最大纵向长度

        self.init_tracks()

    #根据第一帧中的数据，初始化跟踪轨迹列表
    def init_tracks(self):
        self.track_num=0    #track最大的id为track_num-1

        for i in range(len(self.clusters)):
            self.init_track(self.clusters[i],self.heights[i])

    #初始化轨迹
    def init_track(self,s,height):
        track=Track(self.track_num,s,self.processNoiseCov,self.frame,height)
        self.tracks[self.track_num]=track
        self.not_detected_times[self.track_num]=0
        self.track_num+=1

    #预测每一条轨迹在下一帧中的位置
    def predict(self):
        for track_id in self.tracks:
            track=self.tracks[track_id]
            track.s_=np.matmul(self.transitionMatrix,track.s)+np.matmul(self.B,track.u.mean(axis=0))
            track.P_=np.matmul(np.matmul(self.transitionMatrix,track.P),self.transitionMatrix.T)+self.processNoiseCov

    #计算每条轨迹与当前帧中每个点之间的距离
    def cal_distance(self):
        # 计算得到每条轨迹的预测位置与聚类得到的点的距离
        distance = np.array([])
        for track_id in self.tracks:
            track = self.tracks[track_id]
            row = np.array([])
            for j in range(len(self.clusters)):
                row = np.append(row, [np.linalg.norm(self.clusters[j] - track.s_)], axis=0)
            if distance.size == 0:
                distance = np.array([row])
            else:
                distance = np.append(distance, [row], axis=0)

        return distance

    #使用匈牙利算法为轨迹分配点
    def association(self):

        if len(self.clusters)==0:
            return

        distance=self.cal_distance()

        #使用匈牙利算法为每条轨迹分配一个点
        row_ind,col_ind=hungary(distance)
        track_ids=list(self.tracks.keys())

        for i in range(self.track_num):
            if col_ind[i]<len(self.clusters) and distance[i][col_ind[i]]<self.G:
                self.d[track_ids[i]]=col_ind[i]

    #判断轨迹是否位于边缘
    def is_at_edge(self,s):
        #判断是否位于给定空间边缘
        if s[0]<self.xmin+0.2 or s[0]>self.xmax-0.2 or s[1]>self.ymax-0.2:
            return True
        #判断是否位于雷达探测范围边缘
        if s[1]<0.2:
            return True
        if s[0]!=0:
            if s[1]/math.sqrt(3)-0.2<abs(s[0]):
                return True

        return False

    #更新未被分配到点的轨迹
    def update_unassigned_track(self,track_id):
        track=self.tracks[track_id]

        track.add_real_frame(track.s,[0,0],track.height.s)

    #处理未被分配到点的轨迹
    def deal_unassigned_track(self):
        to_be_deleted=[]
        for track_id in self.tracks:
            track=self.tracks[track_id]
            #若轨迹未被分配到点
            if track_id not in self.d:
                #若上一帧中轨迹位于边缘
                if self.is_at_edge(track.s):
                    self.not_detected_times[track_id]+=1
                    if self.not_detected_times[track_id]>self.min_last_time:
                        to_be_deleted.append(track_id)
                    else:
                        self.update_unassigned_track(track_id)
                else:
                    self.update_unassigned_track(track_id)
                    self.not_detected_times[track_id]=max(0,self.not_detected_times[track_id]-1)

        for track_id in to_be_deleted:
            self.delete_track(track_id)

    #删除指定轨迹
    def delete_track(self,track_id):
        del self.tracks[track_id]
        self.track_num-=1
        if track_id in self.not_detected_times:
            del self.not_detected_times[track_id]
        self.deleted_tracks.append(track_id)

    #更新
    def update_assigned_tracks(self):

        self.deal_unassigned_track()

        used_clusters=[]

        for track_id in self.tracks:
            track=self.tracks[track_id]

            #若当前轨迹没有被分配到点，则不对当前点进行更新
            try:
                cluster_id=self.d[track_id]
            except:
                continue

            #将该点标记为已被分配
            used_clusters.append(cluster_id)

            K=np.matmul(track.P_,np.linalg.inv(track.P_+self.processNoiseCov))
            track.s=track.s_+np.matmul(K,self.clusters[cluster_id]-track.s_)
            track.P=np.matmul(np.mat(np.identity(self.plength))-K,track.P_)

            #解决numpy中矩阵与向量相乘导致向量本来应该是x，变成[x]
            if len(track.s)==1:
                track.s=np.array(track.s)[0]

            # 为当前点计算速度(只考虑xy方向的)
            track.add_frame(track.s,track.s-track.points[-1],self.heights[cluster_id])

        #track_update end

        #处理当前帧未被处理的点
        #若连续N帧都出现点比轨迹多的情况，则在第N+1帧生成一条新轨迹
        if_set_zero=True
        for j in range(len(self.clusters)):
            if j not in used_clusters:
                if self.successive_times>self.min_last_time:
                    self.init_track(self.clusters[j],self.heights[j])
                    self.successive_times=0
                    break
                else:
                    self.successive_times+=1
                    if_set_zero=False

        if if_set_zero:
            self.successive_times=max(self.successive_times-1,0)

    #输入下一帧数据进行计算
    def nextFrame(self,clusters,heights,frame):
        #将上一帧的数据清空
        self.d=dict()
        self.deleted_tracks=[]
        #帧号+1
        self.frame=frame
        self.clusters=clusters
        self.heights=heights
        #判断当前是否有轨迹存在
        if self.track_num==0:
            self.init_tracks()
        else:
            self.predict()
            self.association()
            self.update_assigned_tracks()

    #获得每个人的身高
    def get_each_person_height(self):
        height=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            height[track_id]=track.height.get_height()

        return height

    #获得每个人的速度
    def get_each_person_velocity(self):
        velocity=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            velocity[track_id]=np.linalg.norm(track.u[-1])

        return velocity

    #获得每个人到雷达板的距离
    def get_each_person_distance(self):
        distances=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            distances[track_id]=np.linalg.norm(track.points[-1])

        return distances

    #获得每个人的位置
    def get_each_person_location(self):
        locations=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            location=track.get_location(self.M)
            if location is not None:
                locations[track_id]=location

        return locations

    #获得每个人的姿态
    def get_each_person_posture(self):
        postures=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            posture=track.get_posture(self.M,self.rate)
            if posture is not None:
                postures[track_id]=posture

        return postures


    #获得每个人的原始身高
    def get_each_person_raw_height(self):
        raw_height=dict()

        for track_id in self.tracks:
            track=self.tracks[track_id]
            raw_height[track_id]=track.height.origin_height[-1]

        return raw_height