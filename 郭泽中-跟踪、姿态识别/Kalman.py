import numpy as np
from Track import Track
from hungary import hungary


#v5.0
class Multi_Kalman_Tracker():

    d=dict()    #存储当前帧中为轨迹分配的类
    tracks = []  # 所有轨迹
    deleted_tracks=[]   #在这一帧中被删除的轨迹id的集合

    frame=0 #当前帧号
    successive_times=0  #用于判断是否生成新轨迹
    plength=3

    #初始化
    def __init__(self,G,clusters,min_last_time,frame):
        self.G=G    #同一条轨迹在相邻两帧之间最大的移动距离
        self.measurementMatrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])    #H
        self.transitionMatrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  #状态转移矩阵
        self.processNoiseCov=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) * 0.03    #过程噪声矩阵
        self.B=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]])    #B
        self.clusters=clusters  #当前帧数据
        self.min_last_time=min_last_time
        self.frame=frame    #初始化帧号

        self.init_tracks()

    #根据第一帧中的数据，初始化跟踪轨迹列表
    def init_tracks(self):
        self.track_num=0    #track最大的id为track_num-1

        for i in range(len(self.clusters)):
            self.init_track(self.clusters[i])

    #初始化轨迹
    def init_track(self,s):
        track=Track(self.track_num,s,self.processNoiseCov,self.frame)
        self.track_num+=1
        self.tracks.append(track)

    #预测每一条轨迹在下一帧中的位置
    def predict(self):
        for track in self.tracks:
            track.s_=np.matmul(self.transitionMatrix,track.s)+np.matmul(self.B,track.u.mean(axis=0))
            track.P_=np.matmul(np.matmul(self.transitionMatrix,track.P),self.transitionMatrix.T)+self.processNoiseCov

    #使用匈牙利算法为轨迹分配点
    def association(self):
        #计算得到每条轨迹的预测位置与聚类得到的点的距离
        distance=np.array([])
        for i in range(len(self.tracks)):
            track=self.tracks[i]
            row = np.array([])
            for j in range(len(self.clusters)):
                row=np.append(row,[np.linalg.norm(self.clusters[j]-track.s_)],axis=0)
            if distance.size==0:
                distance=np.array([row])
            else:
                distance=np.append(distance,[row],axis=0)

        #使用匈牙利算法为每条轨迹分配一个点
        row_ind,col_ind=hungary(distance)

        for i in range(self.track_num):
            if col_ind[i]<len(self.clusters) and distance[i][col_ind[i]]<self.G:
                self.d[i]=col_ind[i]

    #更新
    def update(self):

        used_clusters=[]

        for i in range(self.track_num):
            track=self.tracks[i]
            frames = list(track.points.keys())

            #若当前轨迹没有被分配到点，则不对当前点进行更新
            try:
                cluster_id=self.d[i]
            except:
                track.s = track.s_
                track.P = track.P_
                track.u = np.append(track.u, [np.append(track.s[:2] - track.points[frames[-1]][:2], [0], axis=0)],
                                    axis=0)
                track.points[self.frame] = track.s
                track.point_num += 1
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
            track.u = np.append(track.u, [np.append(track.s[:2] - track.points[frames[-1]][:2], [0], axis=0)],
                                axis=0)

            track.points[self.frame] = track.s
            track.point_num+=1
            track.original_points[self.frame]=self.clusters[cluster_id]
        #track_update end

        #处理当前帧未被处理的点
        #若连续N帧都出现点比轨迹多的情况，则在第N+1帧生成一条新轨迹
        if_set_zero=True
        for j in range(len(self.clusters)):
            if j not in used_clusters:
                if self.successive_times>self.min_last_time:
                    self.init_track(self.clusters[j])
                    self.successive_times=0
                    break
                else:
                    self.successive_times+=1
                    if_set_zero=False

        if if_set_zero:
            self.successive_times=0

    #输入下一帧数据进行计算
    def nextFrame(self,clusters,frame):
        #将上一帧的数据清空
        self.d=dict()
        self.deleted_tracks=[]
        #帧号+1
        self.frame=frame
        self.clusters=clusters
        self.predict()
        self.association()
        self.update()

    '''
        func：
            获取当前帧每个人的位置
        return:
            position：字典类型，键值为人的id，对应的值为人的三维坐标（第三维度目前不用，为0)
    '''
    def get_each_person_position(self):
        position=dict()

        for track in self.tracks:
            position[track.id]=track.points[self.frame]

        return position

    '''
        func:
            获取当前帧对每个聚类的分配
        return:
            d:字典类型。键值为人的id，对应的值为类的下标(均为从0开始)
            deleted_tracks:列表。每个值对应一个在当前帧被删除掉的人的id
    '''
    def get_point_distribution(self):
        return self.d,self.deleted_tracks

    '''
        func:
            获取当前帧每个人的速度
        return:
            velocity:字典类型。键值为人的id，对应的值为其在当前帧的速度
    '''
    def get_each_person_velocity(self):
        velocity=dict()

        for track in self.tracks:
            velocity[track.id]=track.u[-1]

        return velocity