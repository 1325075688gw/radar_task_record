
class HeightKalman():

    def __init__(self):
        self.transitionMatrix = 1
        self.processNoiseCov = 0.03
        self.P = 0.03
        self.P_ = 0.03
        self.s = 0
        self.s_ = 0

    def predict(self):
        self.s_=self.s
        self.P_=self.P+self.processNoiseCov

    def update(self,height):
        K=self.P_/(self.P_+self.processNoiseCov)
        self.s=self.s_+K*(height-self.s_)
        self.P=(1-K)*self.P_
        print("更新后的P:%f"%self.P)

    def cal_height(self,height):
        if self.s==0:
            self.s=height
        else:
            self.predict()
            self.update(height)

        return self.s
