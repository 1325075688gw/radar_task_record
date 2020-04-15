import numpy as np

class Posture():

    speed_line=0.1

    def __init__(self):
        self.postures=[1]
        self.velocities=[0]
        self.last_posture=1

    def add_posture(self,posture,velocity):
        self.postures.append(posture)
        self.velocities.append(velocity)

        if len(self.postures)>100:
            del self.postures[0]
            del self.velocities[0]

    def get_posture(self,M,rate):
        if len(self.postures)<M+1:
            return None

        if np.mean(self.velocities)>self.speed_line:
            return 4

        if self.postures[-M-1]!=self.last_posture:
            counts=np.bincount(self.postures[-M:])
            most=np.argmax(counts)
            if counts[most]/M>rate and most==self.postures[-M-1]:
                self.last_posture=self.postures[-M-1]

        return self.last_posture

    def cal_posture(self1,height,velocity):
        if velocity>0.024:
            return 4
        else:
            if height>1.2:
                return 1
            elif height>0.4:
                return 2
            else:
                return 3