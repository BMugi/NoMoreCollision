
import multiprocessing
from multiprocessing import Pool
import pandas as pd
import numpy as np
delta_timestamp = 0.1
# This function converts dataset into m/s or m unit
def dataset_unit_conversion(input_dataframe):
    # Load the Excel file into a DataFrame
    df = input_dataframe.copy()

    # Iterate through columns and divide based on column name
    for column in df.columns:
        if 'speed' in column.lower():
            df[column] = df[column] / 256
        elif 'distance' in column.lower():
            df[column] = df[column] / 128

    return df

def calculate_radian (input_dataframe):
    if 'YawRate' not in df.columns or 'Timestamp' not in df.columns:
        raise ValueError("DataFrame must have 'YawRate' and 'Timestamp' columns.")
    
    df_copy = input_dataframe.copy()
        
    # Initialize the 'Radian' column with zeros
    df_copy['Radian'] = 0.0
    
    # Calculate radians using the provided formula
    for i in range(1, len(df_copy)):
        df_copy.at[i, 'Radian'] = df_copy.at[i-1, 'Radian'] + df_copy.at[i-1, 'YawRate'] * df_copy.at[i, 'dT']
    
    return df_copy

def calculate_car_velocity (input_dataframe):
    df_copy = input_dataframe.copy()
    
    # Calculate 'velocity_x' and 'velocity_y' using trigonometric functions
    df_copy['VehicleVelocity_X'] = df_copy['VehicleSpeed'] * np.cos(df_copy['Radian'])
    df_copy['VehicleVelocity_Y'] = df_copy['VehicleSpeed'] * np.sin(df_copy['Radian'])
    
    return df_copy


def calculate_deltaT(input_dataframe):
    df_copy = input_dataframe.copy()

    df_copy['dT'] = df_copy['Timestamp'].diff()

    return df_copy



# Define a function to calculate the position of the car relative to ground
def calculate_car_position(input_dataframe):

    df_copy = input_dataframe.copy()
    
    df_copy['VehiclePosition_X'] = 0.0
    df_copy['VehiclePosition_Y'] = 0.0
    
    for i in range(1, len(df_copy)):
        df_copy.at[i, 'VehiclePosition_X'] = df_copy.at[i-1, 'VehiclePosition_X'] + df_copy.at[i-1, 'VehicleVelocity_X'] * df_copy.at[i, 'dT']
        df_copy.at[i, 'VehiclePosition_Y'] = df_copy.at[i-1, 'VehiclePosition_Y'] + df_copy.at[i-1, 'VehicleVelocity_Y'] * df_copy.at[i, 'dT']
    
    return df_copy


# Define a function to calculate the position of objects relative to ground
def calculate_object_position(input_dataframe, object_number):

    df_copy = input_dataframe.copy()
    
    for i in range(len(df_copy)):
        df_copy.at[i, f'{object_number}ObjectPosition_X'] = df_copy.at[i, 'VehiclePosition_X'] + df_copy.at[i, f'{object_number}ObjectDistance_X']
        df_copy.at[i, f'{object_number}ObjectPosition_Y'] = df_copy.at[i, 'VehiclePosition_Y'] + df_copy.at[i, f'{object_number}ObjectDistance_Y']
    
    return df_copy
    # Initialize a list to store Pgo
    #Pgo = []

    # Loop through the rows of the DataFrame
    #for _, row in data.iloc[1:].iterrows():
    #    Pco = (row['Object_Position_X'], row['Object_Position_Y'])  # Object position relative to the car
    #    Pgc_t = Pgc[_]  # Car's position relative to the ground at timestamp t
    #    Pgo_t = (Pgc_t[0] + Pco[0], Pgc_t[1] + Pco[1])  # Object position relative to the ground at timestamp t
    #    Pgo.append(Pgo_t)  # Append the calculated Pgo to the list

    #return Pgo


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


if __name__ == "__main__":
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_excel("DevelopmentData.xlsx")


    df = dataset_unit_conversion(df)

    df = calculate_deltaT(df)

    df = calculate_radian(df)

    df = calculate_car_velocity(df)

    df = calculate_car_position (df)

    df = calculate_object_position(df,"First")
    df = calculate_object_position(df,"Second")
    df = calculate_object_position(df,"Third")
    df = calculate_object_position(df,"Fourth")

    

    print (df)

    