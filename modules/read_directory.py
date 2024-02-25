# IMPORTS
import pandas as pd
import datetime
import os   # Import data from directory
from nptdms import TdmsFile   # Import tdms files



# AUXILIARY FUNCTIONS
def read_directory_tdms(directory):
    """Summary: function to read names of files in the directory

    Args:
        directory (string): path to read the files

    Returns:
        names (dataframe): dataframe with the names of files to extract, the path of the file and the creation date
    """  
    # Create an empty list to store the name and path of each file
    names = []
    
    # Obtain the list of the files in the directory
    files_tdms = [file for file in os.listdir(directory) if file.endswith(".tdms")]

    for file_tdms in files_tdms:
    # In each measurement, labview generates two files. To obtain the data, we need only the file without 'Respuesta' in the file name.
        
        if 'Respuestas' not in file_tdms:  
            # Extract dataframe name from the name_file
            name_dataframe = file_tdms.split()[0]   # Extract the name from the file
            name_dataframe = name_dataframe.replace("%", "")   # Remove % due to it's could cause problems
            # Constructs the complete path to the TDMS file
            complete_path = os.path.join(directory, file_tdms)

            # Extract the file creation date
            c_timestamp = os.path.getctime(directory)
 
            # convert creation timestamp into DateTime object
            c_datestamp = datetime.datetime.fromtimestamp(c_timestamp)

            # Append the data to the DataFrame
            names.append({'name_file': name_dataframe, 'path_file': complete_path, 'creation_date': c_datestamp})

    # Sort the dataframe by creation_date (the fist register will be the most recent experiment)
    names_df = pd.DataFrame(names)
    names_df = names_df.sort_values(by='creation_date', ascending=False)
    return names_df


def read_last_charge_date():
    """Summary: read the date on which the last data upload was performed

    Returns:
        date (string): date of last file upload
    """
    date_df = pd.read_csv('./data/most_recent_data_charge.csv')
    date = date_df['most_recent_data_charge'][0]
    return date


def update_last_charge_date(df):
    """Summary: upload the date in the 'most_recent_data_charge.csv' file

    Args:
        df (dataframe): dataframe with directory information and files in the directory
    """
    most_recent_data_charge = df['creation_date'][0]
    date_df = pd.DataFrame({'most_recent_data_charge': [most_recent_data_charge]})
    date_df.to_csv('./data/most_recent_data_charge.csv', index=False)


def extract_data_tdms_methane(tdms_file, name_file):
    # Create an empty dictionary
    data = {}

    # Extract the data from the tdms file and store it in data
    for group in tdms_file.groups():
        for channel in group.channels():
            data[channel.name] = channel[:].tolist()

    # Create the dataframe
    exec(f"{name_file} = pd.DataFrame(data)")

    # --Code to test and check the process--
    # Extract the column names of dataframe
    # exec(f'columns_name = {name_file}.columns.values')
    # Extract the shape of dataframe
    # exec(f'shape = {name_file}.shape')
    # Print the dataframe name, column names and dataframe shape
    # print(name_file,'| column names: ', columns_name, '| df shape: ', shape)



# MAIN FUNCTIONS
def read_tdms(directory):
    # Read the directory and extracts the file names, complete path for each file and the creation date of the file
    names_df = read_directory_tdms(directory)

    # Read the date of the last charge
    date = read_last_charge_date()

    # Filter the dataframe using the last charge
    names_filtered_df = names_df[names_df['creation_date'] > date]

    # Read the files generated since the last upload. Extract each row in each iteration of the loop
    for row in names_filtered_df.iterrows():
        # Read de data from tdms file
        tdms_file = TdmsFile.read(row['path'])
        # Transform the data in dataframe
        extract_data_tdms_methane(tdms_file, row['name'])


    #return data_df