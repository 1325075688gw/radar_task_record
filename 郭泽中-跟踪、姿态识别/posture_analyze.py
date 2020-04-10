
class Posture():

    def __init__(self,min_last_time):
        self.min_last_time=min_last_time
        self.current_posture=1  #当前姿态
        self.last_time=0    #当前姿态持续时间


    #根据身高比例和速度大小，判断人的姿态
    def judge_posture(self,height_rate, velocity):
        posture_state=self.current_posture

        if velocity>0.033:
            posture_state=4
        else:
            if height_rate>0.55:
                posture_state=1
            elif height_rate>0.35:
                posture_state=2
            else:
                posture_state=3

        return posture_state


    '''
        func:
            输入每个人的身高比例和速度，得到每个人对应的姿态
        args:
            height_rates:字典类型。键值为人的id，对应的值为每个人的身高比例
            velocity:字典类型。键值为人的id，对应的值为每个人的速度大小
        return:
            posture_state:字典类型。键值为每个人的id，对应的值为每个人的姿态代码
    '''
    def get_posture(self,height_rate,velocity):
        posture=self.judge_posture(height_rate,velocity)

        if posture==self.current_posture:
            self.last_time=0
        else:
            self.last_time+=1
            if self.last_time>self.min_last_time:
                self.current_posture=posture
                self.last_time=0

        return self.current_posture