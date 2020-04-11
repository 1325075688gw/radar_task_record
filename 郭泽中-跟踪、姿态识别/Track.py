import numpy as np
from Height import Height

class Track():

    def __init__(self,id,s,P,frame,height,N):
        self.s_ = []
        self.P_ = []
        self.id=id
        self.s=s
        self.P=P
        self.first_frame=frame
        self.points=[s]
        self.u=np.array([[0,0]])
        self.height=Height(height,N)