import math
import matplotlib.pyplot as plt

def make_map(motor_data, map_filename="map.png"):
    '''
    Takes in array of left and right wheel distances traveled per time step
    [[0,1],[2,3],...]
    plots path taken by rover
    saves figure under timestamp 
    gui opens and displays image
    returns nothing
    '''
    wheel_separation = 0.251075
    #seperate left and right wheel data
    left_wheel = [LR[0] for LR in motor_data]
    right_wheel = [LR[1] for LR in motor_data]

    #initialize x,y, and pose
    #theta here is inital heading angle in radians
    #0 = east, pi/2 = north, etc.
    x,y,theta = 0,0,math.pi/2 
    positions = [(x,y)]

    #pose is relative to previous pose, so update pose
    #make arrays using second order midpoint method

    for i in range(0, len(left_wheel)):
        #get distance traveled by center
        d_center = (left_wheel[i] + right_wheel[i]) / 2.0
        #get change in pose
        d_theta = (right_wheel[i] - left_wheel[i]) / wheel_separation
        
        #create new posistion point
        x += d_center * math.cos(theta + d_theta / 2)
        y += d_center * math.sin(theta + d_theta / 2)
        theta += d_theta

        positions.append((x, y))

    # Plot path
    xs, ys = zip(*positions)
    plt.plot(xs, ys, marker='o')
    plt.axis('equal')
    plt.title("Path drawn from motor data")
    plt.xlabel("X position (m)")
    plt.ylabel("Y position (m)")
    #plt.show() #only for testing, plt.save intented 
    plt.savefig(map_filename, dpi=150, bbox_inches="tight")
    return 0

#testing section
if __name__ == "__main__":
    import random
    #random motor data
    motor_data = []
    for _ in range(20):
        left = random.uniform(0.0, 0.2)
        right = random.uniform(0.0, 0.2)
        motor_data.append((left, right))

    make_map(motor_data)
