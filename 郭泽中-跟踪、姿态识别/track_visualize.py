from matplotlib import pyplot as plt

def show_track(positions,fig):
    ax=fig.add_subplot(122)
    for person in positions:
        position=positions[person]
        ax.plot(position[0],position[1],'o',markersize=40,label=str(person))
        ax.set_title('当前帧有:'+str(len(positions.keys()))+'个人')
        ax.legend(markerscale=1.0/10)

fig=plt.figure()
plt.ion()
positions={1:[1,1],2:[2,2],3:[3,3]}
while True:
    plt.cla()
    show_track(positions,fig)
    plt.pause(0.033)