import numpy as np
from Height import Height
from posture import Posture

class Track():

    def __init__(self,id,s,P,frame,height):
        self.s_ = []
        self.P_ = []
        self.id=id
        self.s=s
        self.P=P
        self.first_frame=frame
        self.points=[s]
        self.u=np.array([[0,0]])
        self.height=Height(height,np.linalg.norm(self.s))
        self.posture=Posture()

    def add_frame(self,position,speed,height):
        self.add_position(position)
        self.add_speed(speed)
        self.add_height(height,np.linalg.norm(position))
        self.add_posture(self.height.get_height(),np.linalg.norm(speed),np.linalg.norm(position))

    def add_real_frame(self,position,speed,height):
        self.add_position(position)
        self.add_speed(speed)
        self.add_real_height(height)
        self.add_posture(self.height.get_height(), np.linalg.norm(speed), np.linalg.norm(position))

    def add_position(self,position):
        self.points.append(position)

    def add_speed(self,speed):
        self.u=np.append(self.u,[speed],axis=0)

    def add_height(self,height,distance):
        self.height.add_height(height,distance)

    def add_real_height(self,height):
        self.height.add_real_height(height)

    def add_posture(self,height,velocity,distance):
        posture=self.posture.cal_posture(height,velocity)
        self.posture.add_posture(posture)

    def get_posture(self,M,rate):
        return self.posture.get_posture(M,rate)

    def get_location(self,M):
        if len(self.points)<M+1:
            return None
        return self.points[-M-1]