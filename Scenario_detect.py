import Dataset_processing
import math
import coordinate_gen
import pandas

def is_object_angle_nearside(dist_long, dist_lat):
    if dist_lat == 0:
        if dist_long < 0:
            angle_deg = 90
    else:
        # Calculate the angle in radians
        angle_rad = math.atan(dist_long / dist_lat)
        # Convert the angle from radians to degrees
        angle_deg = math.degrees(angle_rad)
        print(angle_deg)
    # Check if the angle is smaller than 45 degrees
    return angle_deg < 45

def radian_per_second_to_degree_per_second(rad_per_sec):
    degrees_per_sec = rad_per_sec * (180 / math.pi)
    return degrees_per_sec


def is_car_turning(yaw_degree):
    """
    Checks last 10 yaw rates,
    :param yaw_rate: Pass column of yaw rate in dataset
    :return:
    """
    turning = False
    sum_deg = sum(yaw_degree)
    if sum_deg >= 1:
        turning = True
    return turning, sum_deg


def is_object_closing(dist_o_lat, dist_o_long):
    dist_o_c = []
    dist_decreasing = False

    # Calculate distances and append to dist_o_c
    for dist_o_lat_i, dist_o_long_i in zip(dist_o_lat, dist_o_long):
        dist_o_c.append(math.sqrt(dist_o_lat_i ** 2 + dist_o_long_i ** 2))

    # Check if distances are decreasing
    for i in range(len(dist_o_c) - 1):
        if dist_o_c[i] < dist_o_c[i + 1]:
            dist_decreasing = True

    return dist_decreasing

def estimate_next_position(x, y, vx, vy):
    """
    one value of x, y, vx, vy
    this function needs to be extended to realize linear motion model
    :return: next_x, next_y
    """
    time_interval = 0.1
    next_x = x + vx * time_interval
    next_y = y + vy * time_interval
    return next_x, next_y

def direction_of_obj(x, y, speed_lat, speed_long):
    """
    determine direction of the object moving in degrees
    """
    # Calculate the angle in radians using atan2
    angle_rad = math.atan2(y, x)

    # Convert the angle from radians to degrees
    angle_deg = math.degrees(angle_rad)

    # Ensure the angle is within the range [0, 360) degrees
    if angle_deg < 0:
        angle_deg += 360.0

    return angle_deg

def is_this_CPNCO(dataset, i):
    """
    Determines if this scenario is child running before car
    need to have last 10 dataset
    :return:
    """
    # TODO handle first 10 data
    object_name = "First"
    ObjectDistance_X = dataset[f'{object_name}ObjectDistance_X'].iloc[i-9:i].tolist()
    print(ObjectDistance_X)
    ObjectDistance_Y = dataset[f'{object_name}ObjectDistance_Y'].iloc[i-9:i].tolist()

    Yaw_degree = dataset['Degree'].iloc[i-9:i].tolist()
    print(Yaw_degree)
    if is_object_angle_nearside(ObjectDistance_Y[-1], ObjectDistance_X[-1]):
        turning, sum_of_deg = is_car_turning(Yaw_degree)
        print(turning, sum_of_deg)
        print("it's nearside ")
    return True


def dummy():
    #dataset = Dataset_processing.final_dataset()
    #print(dataset.at[423, 'VehiclePosition_X'])
    distances = coordinate_gen.converted_dataset()
    print(distances)
#dummy()

"""class Scenarion_detection:
    def __init__(self, dataset):
        self.dataset = dataset
        
    def recursive_scenario_checking(self):
        # Define some method logic here
        pass

    def method2(self):
        # Define another method logic here
        pass"""

def Main():
    #dataset_to_ground = Dataset_processing.final_dataset()
    #dataset_original = coordinate_gen.converted_dataset()
    # Need to run this on 4 objects simultaneously with threads
    dataset = Dataset_processing.final_dataset()
    #print (dataset_or)
    if is_this_CPNCO(dataset, 23):
        print("This is CNPCO")
    print("Program run")

Main()