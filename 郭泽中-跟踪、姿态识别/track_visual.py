from matplotlib import pyplot as plt
from posture_analyze import get_posture

def visual(fig,data):
    ax=fig.add_subplot(122)
    ax.xlim(-3,3)
    ax.ylim(0,7)

    for person in data:
        position=data[person][0]
        height=data[person][2]
        velocity=data[person][1]
        gesture=get_posture(height,velocity)

        ax.plot(position[0],position[1],label='人'+str(person),markersize=40)
        ax.text(position[0],position[1],str(gesture))

    ax.legend(markerscale=1.0/20)