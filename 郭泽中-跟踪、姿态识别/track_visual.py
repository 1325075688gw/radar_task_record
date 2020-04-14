from matplotlib import pyplot as plt
import numpy as np
import math

def visual(ax,locations,gestures,frame):
    angle = np.arange(math.pi / 3, math.pi *2/ 3, 0.1)

    x = np.cos(angle)*7
    y = np.sin(angle)*7

    x=np.insert(x,0,0)
    y=np.insert(y,0,0)
    x=np.insert(x,len(x),0)
    y=np.insert(y,len(y),0)

    ax.plot(x, y)

    ax.set_xlim(-3,3)
    ax.set_ylim(0,7)

    ax.set_title('第'+str(frame)+'帧')
    ax.plot(0,0,'o',label='雷达',markersize=40)

    for person in locations:
        location=locations[person]
        gesture=gestures[person]

        ax.plot(location[0],location[1],'o',label='人'+str(person),markersize=40)
        ax.text(location[0],location[1],str(gesture))

    ax.legend(markerscale=1.0/10)