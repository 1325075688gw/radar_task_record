import numpy as np
import pickle
from sklearn.linear_model import LinearRegression

'''
    算法思想：
        设N=7
        对一个人，其前N帧不显示，从N+1帧开始显示
        从第N+1帧开始，计算其左侧N帧平均高度和其右侧N帧平均高度，取相差较小侧加上当前帧计算平均身高作为当前帧实际身高
        也就是说，对一个人，其前N帧不显示，且显示还有N帧延迟
'''

class Height():

    block_length=0.25
    # delta_height=[1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.2599404864574784, 1.1344320084145112,
    #               1.1988682786418468, 1.1119083755798245, 0.9852783189205492, 0.7072995609122058, 0.6282585815117643,
    #               0.3319765558510601, 0.08778045385836619, 0.008194747981847827, -0.25343017749817864,
    #               -0.37420679559517334, -0.4872027432969972, -0.6316345401074752, -0.701356690112346,
    #               -0.875, -1.05, -1.225, -1.4024673937450403, -1.5452798970619157]
    delta_height=[1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.28, 1.22, 1.24, 1.06, 0.81, 0.67, 0.55, 0.47, 0.18,
                  0.04, -0.22, -0.43, -0.52, -0.58, -0.86, -1, -1.14, -1.3, -1.46, -1.44]


    def __init__(self,height,distance):
        self.height=[self.add_delta(height,distance)]
        self.origin_height=[height]

        #kalman部分
        self.transitionMatrix = 1
        self.processNoiseCov = 0.01
        self.P = 0.01
        self.P_ = 0.01
        self.s = height
        self.s_ = 0

    def get_height(self):
        return self.height[-1]

    def get_current_height(self,M):
        if len(self.height)<M+1:
            return None

        return self.height[-M-1]

    def predict(self):
        self.s_=self.s
        self.P_=self.P+self.processNoiseCov

    def update(self,height):
        K=self.P_/(self.P_+self.processNoiseCov)
        self.s=self.s_+K*(height-self.s_)
        self.P=(1-K)*self.P_


    def add_height(self,height,distance):
        # self.predict()
        # self.update(height)
        self.origin_height.append(self.s)

        real_height=self.add_delta(height,distance)

        self.height.append(real_height)

        if len(self.height)>100:
            del self.height[0]

    # def add_real_height(self,height):
    #     self.origin_height.append(height)
    #     self.height.append(height)
    #
    #     if len(self.height)>100:
    #         del self.height[0]

    def add_delta(self,height,distance):
        if int(distance/self.block_length)>=len(self.delta_height):
            return height+self.delta_height[-1]
        return height+self.delta_height[int(distance/self.block_length)]