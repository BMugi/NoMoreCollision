
import pandas as pd
import multiprocessing
from multiprocessing import Pool
import numpy as np

# Define a function to calculate the position of the car relative to ground
def calculate_car_position(data):
    delta_timestamp = 0.5  # Constant delta timestamp of 0.5 seconds

    # Initialize lists to store Pgc and Vgc
    Pgc = [(0, 0)]  # Initial position (0, 0)
    Vgc = []

    # Loop through the rows of the DataFrame
    for _, row in data.iloc[1:].iterrows():
        car_velocity = (row['Car_Velocity_X'], row['Car_Velocity_Y'])

        # Calculate new position based on the previous position, velocity, and constant delta timestamp
        previous_position = Pgc[-1]  # Get the last recorded position
        new_position = (
            previous_position[0] + car_velocity[0] * delta_timestamp,
            previous_position[1] + car_velocity[1] * delta_timestamp,
        )
        Pgc.append(new_position)  # Append the new position

        Vgc.append(car_velocity)  # Append the car's velocity

    # Remove the initial (0, 0) position from Pgc
    Pgc = Pgc[1:]

    return Pgc, Vgc


# Define a function to calculate the position of objects relative to ground
def calculate_object_position(data, Pgc):
    # Initialize a list to store Pgo
    Pgo = []

    # Loop through the rows of the DataFrame
    for _, row in data.iloc[1:].iterrows():
        Pco = (row['Object_Position_X'], row['Object_Position_Y'])  # Object position relative to the car
        Pgc_t = Pgc[_]  # Car's position relative to the ground at timestamp t
        Pgo_t = (Pgc_t[0] + Pco[0], Pgc_t[1] + Pco[1])  # Object position relative to the ground at timestamp t
        Pgo.append(Pgo_t)  # Append the calculated Pgo to the list

    return Pgo


# Define a function to calculate the velocity of objects relative to ground
def calculate_object_velocity(data, Vgc):
    # Initialize a list to store Vgo
    Vgo = []

    # Loop through the rows of the DataFrame
    for _, row in data.iloc[1:].iterrows():
        Vco = (row['Object_Velocity_X'], row['Object_Velocity_Y'])  # Object velocity relative to the car
        Vgc_t = Vgc[_]  # Car's velocity relative to the ground at timestamp t
        Vgo_t = (Vco[0] + Vgc_t[0], Vco[1] + Vgc_t[1])  # Object velocity relative to the ground at timestamp t
        Vgo.append(Vgo_t)  # Append the calculated Vgo to the list

    return Vgo



def calculate_car(df):
    object_id = df['ID']

    if object_id.startswith("car"):
    # Calculate car position relative to ground
    Pgc, Vgc = calculate_car_position(df)
    return Pgc, Vgc

def process_object_data(data, car_positions):
    object_id = data['ID']

    # Check if it's an object based on the "ID" column
    if object_id.startswith("object"):
        Pgo = calculate_object_position(data, car_positions)
        Vgo = calculate_object_velocity(data, car_positions)
        return object_id, Pgo, Vgo
    else:
        return None  # Not an object

if __name__ == "__main__":
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv("your_dataset.csv")

    # Calculate car position relative to ground
    car_positions, car_velocities = calculate_car(df)

    # Filter out object data
    object_df = df[df['ID'].str.startswith("object")]

    # Create a list of dataframes for each object
    object_dataframes = [group for _, group in object_df.groupby('ID')]

    # Initialize a Pool for multiprocessing
    num_processes = multiprocessing.cpu_count()  # Number of CPU cores
    pool = Pool(processes=num_processes)

    # Use parallel processing to calculate positions and velocities for each object
    results = pool.starmap(process_object_data, [(data, car_positions) for data in object_dataframes])
    pool.close()
    pool.join()

    # Now, 'results' is a list of tuples, where each tuple contains (object_id, Pgo, Vgo)

    # Process and use the results as needed
    for result in results:
        if result is not None:
            object_id, positions, velocities = result
            # Process positions and velocities for objects
