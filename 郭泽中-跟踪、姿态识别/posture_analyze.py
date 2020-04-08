import math

#根据身高比例和速度大小，判断人的姿态
def judge_posture(height_rate, velocity):
    posture_state = 0
    if height_rate > 0.55:
        if velocity > 0.3:
            posture_state = 4
        else:
            posture_state = 1
    elif height_rate > 0.35:
        posture_state = 2
    elif posture_state > 0.1:
        posture_state = 3
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
def get_postures(height_rates,velocity):
    posture_state=dict()
    for id in height_rates:
        posture_state[id]=judge_posture(height_rates[id],velocity[id])

    return posture_state