# IMPORTS
import pandas as pd
import datetime
import os   # Import data from directory
from nptdms import TdmsFile   # Import tdms files



# MAIN FUNCTIONS
def read_directory_tdms(path):
    """Summary: function to read names of files in the directory

    Args:
        directory (string): path to read the files

    Returns:
        names (dataframe): dataframe with the names of files to extract, the path of the file and the creation date
    """  
    # Create an empty list to store the name and path of each file
    names = []
    data_df = pd.DataFrame()
    
    # Obtain the list of the files in the directory
    files_tdms = [file for file in os.listdir(path) if file.endswith(".tdms")]
        
    for file_tdms in files_tdms:
    # In each measurement, labview generates two files. To obtain the data, we need only the file without 'Respuesta' in the file name.
        
        if 'Respuestas' not in file_tdms:  
            # Extract dataframe name from the name_file
            name_dataframe = file_tdms.split()[0]   # Extract the name from the file
            name_dataframe = name_dataframe.replace("%", "")   # Remove % due to it's could cause problems
            # Constructs the complete path to the TDMS file
            complete_path_source = os.path.join(path, file_tdms)
            
            # Extract the file creation date
            timestamp = os.path.getctime(complete_path_source)

            # convert creation timestamp into DateTime object
            datestamp = datetime.datetime.fromtimestamp(timestamp)
            
            # Append the name to the DataFrame name
            names.append({'name': name_dataframe, 'path': complete_path_source, 'creation_date': datestamp})
                    
    # Sort dataframe by creation_date
    names_df = pd.DataFrame(names)
    names_df = names_df.sort_values(by='creation_date', ascending=True)
    
    return names_df


def check_time(names):    
    # Extract the date of last intake
    date_df = pd.read_csv('./data/most_recent_data_charge.csv')
    last_update_date = date_df['most_recent_data_charge'][0]
    
    # Filter the names
    names_filtered = names[names['creation_date'] > last_update_date]
    
    return names_filtered


def read_last_charge_date():
    """Summary: read the date on which the last data upload was performed

    Returns:
        date (string): date of last file upload
    """
    date_df = pd.read_csv('./data/most_recent_data_charge.csv')
    date = date_df['most_recent_data_charge'][0]
    date_2 = date.split(' ')[0]
    return date_2


def update_last_charge_date(df):
    """Summary: upload the date in the 'most_recent_data_charge.csv' file

    Args:
        df (dataframe): dataframe with directory information and files in the directory
    """
    most_recent_data_charge = df['creation_date'][0]
    date_df = pd.DataFrame({'most_recent_data_charge': [most_recent_data_charge]})
    date_df.to_csv('./data/most_recent_data_charge.csv', index=False)
