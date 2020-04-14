import numpy as np

class Posture():

    def __init__(self):
        self.postures=[1]
        self.last_posture=1

    def add_posture(self,posture):
        self.postures.append(posture)

        if len(self.postures)>100:
            del self.postures[0]

    def get_posture(self,M,rate):
        if len(self.postures)<M+1:
            return None

        if self.postures[-M-1]!=self.last_posture:
            counts=np.bincount(self.postures[-M:])
            most=np.argmax(counts)
            if counts[most]/M>rate and most==self.postures[-M-1]:
                self.last_posture=self.postures[-M-1]

        return self.last_posture

    def cal_posture(self1,height,velocity):
        if velocity>0.033:
            return 4
        else:
            if height>1.2:
                return 1
            elif height>0.4:
                return 2
            else:
                return 3