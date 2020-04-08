import numpy as np

class Track():

    s_=[]
    P_=[]

    def __init__(self,id,s,P,frame):
        self.id=id
        self.s=s
        self.P=P
        self.points={frame:s}
        self.original_points={frame:s}
        self.point_num=1
        self.u=np.array([[0,0,0]])