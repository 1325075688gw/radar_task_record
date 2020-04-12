import numpy as np

class Posture():

    def __init__(self):
        self.postures=[1]
        self.last_posture=1

    def add_posture(self,posture):
        self.postures.append(posture)


    def get_posture(self,M,rate):
        if len(self.postures)<M+1:
            return None

        if self.postures[-M-1]!=self.last_posture:
            counts=np.bincount(self.postures)
            most=np.argmax(counts)
            if counts[most]/M>rate and most==self.postures[-M-1]:
                self.last_posture=self.postures[-M-1]

        return self.last_posture


    # def get_each_person_posture(self,heights,velocities,distances):
    #     postures=dict()
    #
    #     for track_id in heights:
    #         postures[track_id]=self.get_posture(heights[track_id],velocities[track_id],distances[track_id])
    #
    #     return postures

    def cal_posture(self1,height,velocity):
        if velocity>0.033:
            return 4
        else:
            if height>1.3:
                return 1
            elif height>0.4:
                return 2
            else:
                return 3