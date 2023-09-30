import Dataset_processing
import math


threshold_angle = 45
last_measurements = 9
TURNING_DEGREE = 1
THRESHOLD_DISTANCE_NEAR = 20
THRESHOLD_AHEAD_X = 20
THRESHOLD_AHEAD_Y = 10

def is_object_angle_nearside(dist_long, dist_lat):
    angle_deg = 0
    if dist_lat == 0:
        if dist_long < 0:
            angle_deg = 90
    else:
        # Calculate the angle in radians
        angle_rad = math.atan(dist_long / dist_lat)

        # Convert the angle from radians to degrees
        angle_deg = math.degrees(angle_rad)
        # print(angle_deg)
    # Check if the angle is smaller than 45 degrees
    return abs(angle_deg) < threshold_angle

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
    if sum_deg >= TURNING_DEGREE:
        turning = True
    return turning, sum_deg


def is_object_closing_and_near(dist_o_lat, dist_o_long):
    dist_o_c = []
    dist_decreasing = False
    dist_near = False
    # Calculate distances and append to dist_o_c
    for dist_o_lat_i, dist_o_long_i in zip(dist_o_lat, dist_o_long):
        dist_o_c.append(math.sqrt(dist_o_lat_i ** 2 + dist_o_long_i ** 2))

    # Check if distances are decreasing
    for i in range(len(dist_o_c) - 1):
        if dist_o_c[i] < dist_o_c[i + 1]:
            dist_decreasing = True

    if dist_o_c[-1] <= THRESHOLD_DISTANCE_NEAR and dist_decreasing:
        return True
    else:
        return False


def is_object_ahead(Obj_pos_x, Obj_pos_y, Veh_pos_x, Veh_pos_y):
    thr_ahead_x_min = Veh_pos_x
    thr_ahead_x_max = Veh_pos_x + THRESHOLD_AHEAD_X

    if thr_ahead_x_min <= Obj_pos_x <= thr_ahead_x_max:
        thr_ahead_y_min = Veh_pos_y - THRESHOLD_AHEAD_Y / 2
        thr_ahead_y_max = Veh_pos_y + THRESHOLD_AHEAD_Y / 2
        if thr_ahead_y_min <= Obj_pos_y <= thr_ahead_y_max:
            return True
    return False

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


def is_this_CPNCO(ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
    """
    Scenario 1
    Determines if this scenario is child running before car
    need to have last_measurements dataset
    Checks if obj is closing and near, is object nearside, is car turning
    :return:
    """
    # TODO handle first 10 data

    if is_object_closing_and_near(ObjectDistance_Y, ObjectDistance_X):
        # print("object is closing and under" + str(THRESHOLD_DISTANCE_NEAR) + " m")
        if is_object_angle_nearside(ObjectDistance_Y[-1], ObjectDistance_X[-1]):
          #  print("it's nearside ")
            turning, sum_of_deg = is_car_turning(Yaw_degree)
           # print("Turning, sum of degree" + str(turning), str(sum_of_deg))
            if turning:
                # it's not CPNCO
                return False
            else:
                # it's CPNCO
                return True
    return False

def is_this_CPTA(ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
    """
    Scenario 2
    Determines if this scenario is car is in cross-section, adult is walking in same direction
    need to have last_measurements dataset
    Checks if obj is closing and near, is object nearside, is car turning, is adult walking in same dir
    :return:
    """
    # TODO handle first 10 data

    if is_object_closing_and_near(ObjectDistance_Y, ObjectDistance_X):
        # print("object is closing and under" + str(THRESHOLD_DISTANCE_NEAR) + " m")
        if is_object_angle_nearside(ObjectDistance_Y[-1], ObjectDistance_X[-1]):
           # print("it's nearside ")
            turning, sum_of_deg = is_car_turning(Yaw_degree)
           # print("Turning, sum of degree" + str(turning), str(sum_of_deg))
            if turning:
                #print("Vehicle is turning")
                # TODO: add one more condition for human was walking in same dir
                return True
    return False

def is_this_CPLA(dataset, i, object_name, ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
    """
    Scenario 3
    Determines if this scenario is pedestrian walking ahead of the car
    need to have last_measurements dataset
    Checks if obj is closing and near, is object ahead, is not car turning
    :return:
    """
    # TODO handle first 10 data

    Obj_pos_x = dataset[f'{object_name}ObjectPosition_X'].iloc[i]
    Obj_pos_y = dataset[f'{object_name}ObjectPosition_Y'].iloc[i]
    Veh_pos_x = dataset['VehiclePosition_X'].iloc[i]
    Veh_pos_y = dataset['VehiclePosition_Y'].iloc[i]

    if is_object_closing_and_near(ObjectDistance_Y, ObjectDistance_X):
        #print("object is closing and under" + str(THRESHOLD_DISTANCE_NEAR) + " m")
        if is_object_ahead(Obj_pos_x, Obj_pos_y, Veh_pos_x, Veh_pos_y):
            #print("Object is ahead!")
            if not is_object_angle_nearside(ObjectDistance_Y[-1], ObjectDistance_X[-1]):
                #print("it's not nearside ")
                turning, sum_of_deg = is_car_turning(Yaw_degree)
                #print("Turning, sum of degree" + str(turning), str(sum_of_deg))
                if not turning:
                    #print("Vehicle is not turning")
                    # TODO: add one more condition for human was walking in same dir
                    return True
    return False


def scenario_ID(dataset, i, object_name):
    """
    Scenario detection function
    :param dataset:
    :param i:
    :param object_name:
    :return:  Scenario ID
    """
    ObjectDistance_X = dataset[f'{object_name}ObjectDistance_X'].iloc[i - last_measurements:i].tolist()
    ObjectDistance_Y = dataset[f'{object_name}ObjectDistance_Y'].iloc[i - last_measurements:i].tolist()

    Yaw_degree = dataset['Degree'].iloc[i - last_measurements:i].tolist()

    scenario = 0
    if is_this_CPNCO(ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
        scenario = 1
    if is_this_CPLA(dataset, i, object_name, ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
        scenario = 3
    if is_this_CPTA(ObjectDistance_X, ObjectDistance_Y, Yaw_degree):
        scenario = 2

    return scenario

