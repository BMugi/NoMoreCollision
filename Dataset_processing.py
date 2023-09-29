
import multiprocessing
from multiprocessing import Pool
import pandas as pd
import numpy as np

object_list = ["First","Second","Third","Fourth"]


def dataset_unit_conversion(input_dataframe):
    """
    Convert data columns in a DataFrame to standard units: [m], [m/s].

    Args:
        input_dataframe (pd.DataFrame): A DataFrame with columns that containing 'speed' and 'distance'.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with selected columns converted to standard units.
    """

    df = input_dataframe.copy()

    for column in df.columns:
        if 'speed' in column.lower():
            df[column] = df[column] / 256
        elif 'distance' in column.lower():
            df[column] = df[column] / 128

    return df


def calculate_radian (input_dataframe):
    """
    Calculate the radian of a car's movement based on yaw rates and time intervals.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame containing at least two columns:
            - 'YawRate' (float): Yaw rate (angular velocity) of the car in radians per second.
            - 'dT' (float): Time interval in seconds between consecutive data points.
    
    Returns:
        pd.DataFrame: A copy of the input DataFrame with an additional 'Radian' column that represents
                      the cumulative radian angle of the car's movement.
    """
    
    df_copy = input_dataframe.copy()
        
    df_copy['Radian'] = 0.0
    
    for i in range(1, len(df_copy)):
        df_copy.at[i, 'Radian'] = df_copy.at[i-1, 'Radian'] + df_copy.at[i-1, 'YawRate'] * df_copy.at[i, 'dT']
    
    return df_copy


def calculate_car_velocity (input_dataframe):
    """
    Calculate the velocity of a car relative to the ground in both x and y directions.
    
    Args:
        input_dataframe (pd.DataFrame): A DataFrame with at least two columns:
            - 'VehicleSpeed' (float): The speed of the car in [m/s].
            - 'Radian' (float): The radian angle representing the car's orientation.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with two additional columns:
            - 'VehicleVelocity_X' (float): The velocity of the car in the x-direction relative to the ground in [m/s].
            - 'VehicleVelocity_Y' (float): The velocity of the car in the y-direction relative to the ground in [m/s]].
    """

    df_copy = input_dataframe.copy()
    
    df_copy['VehicleVelocity_X'] = df_copy['VehicleSpeed'] * np.cos(df_copy['Radian'])
    df_copy['VehicleVelocity_Y'] = df_copy['VehicleSpeed'] * np.sin(df_copy['Radian'])
    
    return df_copy


def calculate_deltaT(input_dataframe):
    """
    Calculate the time difference ('delta Timestamp') between consecutive Timestamps in a DataFrame.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame containing a 'Timestamp' column with datetime values in [s].

    Returns:
        pd.DataFrame: A copy of the input DataFrame with an additional 'dT' column representing the
                      time difference between consecutive timestamps in [s].
    """

    df_copy = input_dataframe.copy()

    df_copy['dT'] = df_copy['Timestamp'].diff()

    return df_copy


def calculate_car_position(input_dataframe):
    """
    Calculate the position of a car relative to the ground in both the x and y directions.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame with at least three columns:
            - 'VehicleVelocity_X' (float): The velocity of the car in the x-direction relative to the ground in [m/s].
            - 'VehicleVelocity_Y' (float): The velocity of the car in the y-direction relative to the ground in [m/s].
            - 'dT' (float): Time interval in seconds between consecutive data points.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with two additional columns:
            - 'VehiclePosition_X' (float): The position of the car in the x-direction relative to the ground in [m].
            - 'VehiclePosition_Y' (float): The position of the car in the y-direction relative to the ground in [m].
    """

    df_copy = input_dataframe.copy()
    
    df_copy['VehiclePosition_X'] = 0.0
    df_copy['VehiclePosition_Y'] = 0.0
    
    for i in range(1, len(df_copy)):
        df_copy.at[i, 'VehiclePosition_X'] = df_copy.at[i-1, 'VehiclePosition_X'] + df_copy.at[i-1, 'VehicleVelocity_X'] * df_copy.at[i, 'dT']
        df_copy.at[i, 'VehiclePosition_Y'] = df_copy.at[i-1, 'VehiclePosition_Y'] + df_copy.at[i-1, 'VehicleVelocity_Y'] * df_copy.at[i, 'dT']
    
    return df_copy


def calculate_object_position(input_dataframe):
    """
    Calculate the position of objects relative to the ground based on their distances from a vehicle.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame with columns representing:
            - 'VehiclePosition_X' (float): The x-coordinate of the vehicle's position relative to the ground in [m].
            - 'VehiclePosition_Y' (float): The y-coordinate of the vehicle's position relative to the ground in [m].
            - 'ObjectNumber' (string): An identifier for the objects (e.g., 'First').
            - 'ObjectDistance_X' (float): The distance of objects from the vehicle in the x-direction in [m].
            - 'ObjectDistance_Y' (float): The distance of objects from the vehicle in the y-direction in [m].

    Returns:
        pd.DataFrame: A copy of the input DataFrame with additional columns for each object:
            - '{ObjectNumber}ObjectPosition_X' (float): The x-coordinate of the object's position relative to the ground in [m].
            - '{ObjectNumber}ObjectPosition_Y' (float): The y-coordinate of the object's position relative to the ground in [m].
    """

    df_copy = input_dataframe.copy()

    for object_number in object_list:
        for i in range(len(df_copy)):
            df_copy.at[i, f'{object_number}ObjectPosition_X'] = df_copy.at[i, 'VehiclePosition_X'] + df_copy.at[i, f'{object_number}ObjectDistance_X']
            df_copy.at[i, f'{object_number}ObjectPosition_Y'] = df_copy.at[i, 'VehiclePosition_Y'] + df_copy.at[i, f'{object_number}ObjectDistance_Y']
        
    return df_copy


def calculate_object_velocity(input_dataframe):
    """
    Calculate the velocity of objects relative to the ground in both the x and y directions.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame with columns representing:
            - 'VehicleVelocity_X' (float): The x-component of the vehicle's velocity relative to the ground in [m/s].
            - 'VehicleVelocity_Y' (float): The y-component of the vehicle's velocity relative to the ground in [m/s].
            - 'ObjectNumber' (string): An identifier for the objects (e.g., 'First').
            - '{ObjectNumber}ObjectSpeed_X' (float): The speed of objects in the x-direction relative to the ground in [m/s].
            - '{ObjectNumber}ObjectSpeed_Y' (float): The speed of objects in the y-direction relative to the ground in [m/s].

    Returns:
        pd.DataFrame: A copy of the input DataFrame with additional columns for each object:
            - '{ObjectNumber}ObjectVelocity_X' (float): The x-component of the object's velocity relative to the ground in [m/s].
            - '{ObjectNumber}ObjectVelocity_Y' (float): The y-component of the object's velocity relative to the ground in [m/s].
    """

    df_copy = input_dataframe.copy()
    
    for object_number in object_list:
        for i in range(len(df_copy)):
            df_copy.at[i, f'{object_number}ObjectVelocity_X'] = df_copy.at[i, 'VehicleVelocity_X'] + df_copy.at[i, f'{object_number}ObjectSpeed_X']
            df_copy.at[i, f'{object_number}ObjectVelocity_Y'] = df_copy.at[i, 'VehicleVelocity_Y'] + df_copy.at[i, f'{object_number}ObjectSpeed_Y']
        
    return df_copy


def remove_not_needed_data(input_dataframe):
    """
    Remove unnecessary data columns from a DataFrame, leaving only data relative to the ground.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame containing various columns of data.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with unnecessary columns removed.
    """

    df = input_dataframe.drop(columns=['VehicleSpeed','YawRate','Radian'])
    for object_number in object_list:
        df = df.drop(columns=[f'{object_number}ObjectDistance_X', 
                              f'{object_number}ObjectDistance_Y',
                              f'{object_number}ObjectSpeed_X',
                              f'{object_number}ObjectSpeed_Y'])
    return df

# function reads data from excel sheet to DataFrame and do all neccessary data processing and return data which is only relative to the ground
def final_dataset():
    """
    Read data from an Excel sheet into a DataFrame and perform necessary data processing.

    Args:
        None

    Returns:
        pd.DataFrame: A processed DataFrame containing relevant data related to the ground.
    """

    df = pd.read_excel("DevelopmentData.xlsx")

    converted_df = dataset_unit_conversion(df)

    dT_df = calculate_deltaT(converted_df)

    radian_df = calculate_radian(dT_df)

    car_velocity_df = calculate_car_velocity(radian_df)

    car_position_df = calculate_car_position (car_velocity_df)

    object_position_df = calculate_object_position(car_position_df)

    object_velocity_df = calculate_object_velocity(object_position_df)

    final_df = remove_not_needed_data(object_velocity_df)

    return final_df 

df = final_dataset()
df.to_excel("ProcessedData.xlsx", index=False)
    