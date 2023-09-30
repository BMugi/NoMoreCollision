import matplotlib.pyplot as plt
import matplotlib.animation as animation
import Dataset_processing
import numpy as np
import matplotlib.lines as mlines
from matplotlib.patches import Patch

quiver = None

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    line5.set_data([], [])
    return line1, line2, line3, line4, line5

def rotate_coordinates(x, y):
    return -np.array(y), np.array(x)


def animate(i):
    global quiver # global

    # Remove the old arrows if they exist
    if quiver is not None:
        quiver.remove()

    # legend infos
    scenario_info = f'Scenario: {first_scene[i]} | {second_scene[i]} | {third_scene[i]} | {fourth_scene[i]}'
    red_label = f'Target object'
    green_label = 'Non-target objects\n'

    red_patch = mlines.Line2D([], [], color='red', marker='o', markersize=10, label=red_label, linestyle='None')
    green_patch = mlines.Line2D([], [], color='green', marker='o', markersize=10, label=green_label, linestyle='None')
    scenario_patch = Patch(color='none', label=scenario_info)

    legend = ax.legend(handles=[red_patch, green_patch, scenario_patch], loc='upper right', frameon=True)

    for idx, line, scene in zip(range(1, 5), [line1, line2, line3, line4], [first_scene, second_scene, third_scene, fourth_scene]):
        color = 'ro' if scene[i] != 0 else 'go'
        line.set_color(color[0])  # Set color to red if target

    line1.set_data(object_1_x[i], object_1_y[i])
    line2.set_data(object_2_x[i], object_2_y[i])
    line3.set_data(object_3_x[i], object_3_y[i])
    line4.set_data(object_4_x[i], object_4_y[i])
    line5.set_data(car_x[i], car_y[i])

    ax.arrow(car_x[i], car_y[i], car_vx[i], car_vy[i], color='k', head_width=0.2)

    quiver = ax.quiver(
        [car_x[i]],
        [car_y[i]],
        [car_vx[i]],
        [car_vy[i]],
        color=['k']
    )

    return line1, line2, line3, line4, line5, quiver

# read the data
df = Dataset_processing.final_dataset()

print("Here")

# assignments
object_1_x = df['FirstObjectPosition_X'].tolist()
object_1_y = df['FirstObjectPosition_Y'].tolist()
object_2_x = df['SecondObjectPosition_X'].tolist()
object_2_y = df['SecondObjectPosition_Y'].tolist()
object_3_x = df['ThirdObjectPosition_X'].tolist()
object_3_y = df['ThirdObjectPosition_Y'].tolist()
object_4_x = df['FourthObjectPosition_X'].tolist()
object_4_y = df['FourthObjectPosition_Y'].tolist()
car_x = df['VehiclePosition_X'].tolist()
car_y = df['VehiclePosition_Y'].tolist()
car_vx = df['VehicleVelocity_X'].tolist()
car_vy = df['VehicleVelocity_Y'].tolist()
first_scene = df['FirstScenario_ID'].tolist()
second_scene = df['SecondScenario_ID'].tolist()
third_scene = df['ThirdScenario_ID'].tolist()
fourth_scene = df['FourthScenario_ID'].tolist()


# plot
fig, ax = plt.subplots()

# Setting labels and title
ax.set_title('Environment of the ego vehicle and four objects from the global reference')
ax.set_xlabel('Vehicle X axis (m)')
ax.set_ylabel('Vehicle Y Axis (m)')

# Setting limits for the axes
ax.set_ylim([min(min(object_1_y), min(object_2_y), min(object_3_y), min(object_4_y), min(car_y)), 
             max(max(object_1_y), max(object_2_y), max(object_3_y), max(object_4_y), max(car_y))])
ax.set_xlim([min(min(object_1_x), min(object_2_x), min(object_3_x), min(object_4_x), min(car_x)), 
             max(max(object_1_x), max(object_2_x), max(object_3_x), max(object_4_x), max(car_x))])

# Setting axis lines
ax.axhline(0, color='grey', linewidth=0.5, alpha=0.5)  # Horizontal axis (alpha sets transparency)
ax.axvline(0, color='grey', linewidth=0.5, alpha=0.5)  # Vertical axis

# Setting grid lines
ax.grid(True, linestyle='--', color='grey', linewidth=0.5, alpha=0.5)

line1, = ax.plot([], [], 'go')  # red dot for object 1
line2, = ax.plot([], [], 'go')  # blue dot for object 2
line3, = ax.plot([], [], 'go')  # green dot for object 3
line4, = ax.plot([], [], 'go')  # yellow dot for object 4
line5, = ax.plot([], [], 'ko')  # black dot for car

ani = animation.FuncAnimation(fig, animate, frames=len(object_1_x), init_func=init, blit=True, interval=100)

plt.show()
