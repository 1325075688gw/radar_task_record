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
    # delta_height=[1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028,
    #               1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028,
    #               1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3140541414412028,
    #               1.3140541414412028, 1.3140541414412028, 1.3140541414412028, 1.3288594926377155, 1.3134312804075299, 1.2219216453875605,
    #               1.2143259488724887, 1.2145383426959306, 1.3130789078759186, 1.1048957942758475, 1.0872530129696312, 1.0636310246037115,
    #               0.9336202974427237, 0.8856223908055612, 0.7907446665797653, 0.8281747719175835, 0.8921147417711005, 0.6231591950247712,
    #               0.5686247957657931, 0.24488477291970856, 0.31081176492600227, 0.6683509198365475, 0.30118874846519805, 0.20038753290780997,
    #               0.20823179854074825, 0.17770912725863663, 0.27437255532115, -0.13800364858106073, -0.16936670470881676,
    #               -0.14191211218850475, -0.3139048637254789, -0.35464433277773777, -0.6855953006070292, -0.47922275692136784,
    #               -0.527188393163923, -0.48966066462114766, -0.637606118126333, -0.5105364668906307, -0.61, -0.71, -0.81, -0.91, -1.01, -1.11, -1.21, -1.31,
    #               -1.41, -1.51, -1.61, -1.7660115429222136, -1.3406171820308672, -1.3465835784515052, -1.417989730047414]
    delta_height=[[], [], [], [], [], [], [], [], 1.2599404864574784, 1.1344320084145112, 1.1988682786418468, 1.1119083755798245, 0.9852783189205492, 0.7072995609122058, 0.6282585815117643, 0.3319765558510601, 0.08778045385836619, 0.008194747981847827, -0.25343017749817864, -0.37420679559517334, -0.4872027432969972, -0.6316345401074752, -0.701356690112346, [], [], [], -1.4024673937450403, -1.5452798970619157]


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
        # N=self.N
        #
        # if len(self.height)<2*N+1:
        #     return None
        #
        # l_half=np.mean(self.height[-2*N-1:-N-1])
        # r_half=np.mean(self.height[-N:])
        #
        # if abs(self.height[-N-1]-l_half)<abs(self.height[-N-1]-r_half):
        #     return np.mean(self.height[-2*N-1:-N])
        # else:
        #     return np.mean(self.height[-N-1:])
        return self.height[-1]

    def predict(self):
        self.s_=self.s
        self.P_=self.P+self.processNoiseCov

    def update(self,height):
        K=self.P_/(self.P_+self.processNoiseCov)
        self.s=self.s_+K*(height-self.s_)
        self.P=(1-K)*self.P_


    def add_height(self,height,distance):

        self.origin_height.append(height)

        # self.predict()
        # self.update(height)

        # self.s=self.height_cal.predict([[distance,self.s]])[0]
        real_height=self.add_delta(height,distance)
        if real_height<2.5:
            self.s=self.add_delta(height,distance)

        self.height.append(self.s)

    def add_real_height(self,height):
        self.origin_height.append(height)
        self.height.append(height)

    def add_delta(self,height,distance):
        if int(distance/self.block_length)>=len(self.delta_height):
            return height+self.delta_height[-1]
        return height+self.delta_height[int(distance/self.block_length)]