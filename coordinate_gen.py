import pandas as pd

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

# Function to extract coordinates for a specific object
def extract_object_coordinates(df, object_number):
    x_column = f'{object_number}ObjectDistance_X'
    y_column = f'{object_number}ObjectDistance_Y'
    x_coordinates = df[x_column].tolist()
    y_coordinates = df[y_column].tolist()
    return x_coordinates, y_coordinates



def object_data_proc():
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_excel("DevelopmentData.xlsx")


    converted_df = dataset_unit_conversion(df)

    # Extract coordinates for each object
    object1_x, object1_y = extract_object_coordinates(converted_df, "First")
    object2_x, object2_y = extract_object_coordinates(converted_df, "Second")
    object3_x, object3_y = extract_object_coordinates(converted_df, "Third")
    object4_x, object4_y = extract_object_coordinates(converted_df, "Fourth")

    return object1_x, object1_y,object2_x, object2_y,object3_x, object3_y,object4_x, object4_y