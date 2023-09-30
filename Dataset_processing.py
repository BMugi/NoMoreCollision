from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
import Scenario_detect 

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


def calculate_degree (input_dataframe):
    """
    Calculate the degree of a car's movement based on yaw rates and time intervals.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame containing at least two columns:
            - 'YawRate' (float): Yaw rate (angular velocity) of the car in degrees per second.
            - 'dT' (float): Time interval in seconds between consecutive data points.
    
    Returns:
        pd.DataFrame: A copy of the input DataFrame with an additional 'Degree' column that represents
                      the cumulative degree angle of the car's movement.
    """
    
    df_copy = input_dataframe.copy()
        
    df_copy['Degree'] = 0.0
    
    for i in range(1, len(df_copy)):
        df_copy.at[i, 'Degree'] = df_copy.at[i-1, 'Degree'] + df_copy.at[i-1, 'YawRate'] * df_copy.at[i, 'dT']
    
    return df_copy


def calculate_car_velocity (input_dataframe):
    """
    Calculate the velocity of a car relative to the ground in both x and y directions.
    
    Args:
        input_dataframe (pd.DataFrame): A DataFrame with at least two columns:
            - 'VehicleSpeed' (float): The speed of the car in [m/s].
            - 'Degree' (float): The degree angle representing the car's orientation.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with two additional columns:
            - 'VehicleVelocity_X' (float): The velocity of the car in the x-direction relative to the ground in [m/s].
            - 'VehicleVelocity_Y' (float): The velocity of the car in the y-direction relative to the ground in [m/s]].
    """

    df_copy = input_dataframe.copy()
    
    df_copy['VehicleVelocity_X'] = df_copy['VehicleSpeed'] * np.cos(df_copy['Degree'])
    df_copy['VehicleVelocity_Y'] = df_copy['VehicleSpeed'] * np.sin(df_copy['Degree'])
    
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


def calculate_object_data(input_dataframe):
    """
    Calculate all neccessary data for all objects.

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
    
    def calculate_velocity(object_name, i):
        df_copy.at[i, f'{object_name}ObjectVelocity_X'] = df_copy.at[i, 'VehicleVelocity_X'] + df_copy.at[i, f'{object_name}ObjectSpeed_X']
        df_copy.at[i, f'{object_name}ObjectVelocity_Y'] = df_copy.at[i, 'VehicleVelocity_Y'] + df_copy.at[i, f'{object_name}ObjectSpeed_Y']

    def calculate_position(object_name, i):
        df_copy.at[i, f'{object_name}ObjectPosition_X'] = df_copy.at[i, 'VehiclePosition_X'] + df_copy.at[i, f'{object_name}ObjectDistance_X']
        df_copy.at[i, f'{object_name}ObjectPosition_Y'] = df_copy.at[i, 'VehiclePosition_Y'] + df_copy.at[i, f'{object_name}ObjectDistance_Y']

    def scenario_detect (object_name, index_num):
        scneario_id = Scenario_detect.scenario_ID(df_copy, index_num, object_name)
        df_copy.at[index_num,f'{object_name}Scenario_ID'] = int(scneario_id)
        
    with ThreadPoolExecutor() as executor:
        futures = []
        for object_name in object_list:
            for i in range(len(df_copy)):
                futures.append(executor.submit(calculate_velocity, object_name, i))
                futures.append(executor.submit(calculate_position, object_name, i))
            for i in range(9,len(df_copy)):
                futures.append(executor.submit(scenario_detect, object_name, i))


        

            

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    return df_copy



def data_for_visual(input_dataframe):
    """
    Remove unnecessary data columns from a DataFrame, leaving only data relative to the ground in correct order.

    Args:
        input_dataframe (pd.DataFrame): A DataFrame containing various columns of data.

    Returns:
        pd.DataFrame: A copy of the input DataFrame with unnecessary columns removed.
    """
    new_order = ['FirstObjectPosition_X','FirstObjectPosition_Y',
                 'SecondObjectPosition_X','SecondObjectPosition_Y',
                 'ThirdObjectPosition_X','ThirdObjectPosition_Y',
                 'FourthObjectPosition_X','FourthObjectPosition_Y',
                 'VehiclePosition_X','VehiclePosition_Y',
                 'FirstScenario_ID','SecondScenario_ID','ThirdScenario_ID','FourthScenario_ID']
    df = input_dataframe[new_order]

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

    radian_df = calculate_degree(dT_df)

    car_velocity_df = calculate_car_velocity(radian_df)

    car_position_df = calculate_car_position (car_velocity_df)

    object_data_df = calculate_object_data(car_position_df)

    object_data_df.to_csv("ProcessedData.csv", index=False)

    print ("Successfully processed data")

    final_df = data_for_visual(object_data_df)

    final_df.to_csv("Data_for_visualization.csv", index=False)

    return object_data_df

if __name__ == "__main__":
    final_dataset()
