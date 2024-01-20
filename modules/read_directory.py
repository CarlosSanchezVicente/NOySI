# IMPORTS
import pandas as pd
import datetime
import os   # Import data from directory
from nptdms import TdmsFile   # Import tdms files


# AUXILIARY FUNCTIONS


# MAIN FUNCTIONS
def read_directory_tdms(path):
    """Summary: function to read names of files in the directory

    Args:
        path (string): 

    Returns:
        _type_: _description_
    """  
    # Create an empty list to store the name and path of each file
    names = []
    
    # Obtain the list of the files in the directory
    files_tdms = [file for file in os.listdir(path) if file.endswith(".tdms")]

    for file_tdms in files_tdms:
    # In each measurement, labview generates two files. To obtain the data, we need only the file without 'Respuesta' in the file name.
        
        if 'Respuestas' not in file_tdms:  
            # Extract dataframe name from the name_file
            name_dataframe = file_tdms.split()[0]   # Extract the name from the file
            name_dataframe = name_dataframe.replace("%", "")   # Remove % due to it's could cause problems
            # Constructs the complete path to the TDMS file
            complete_path = os.path.join(path, file_tdms)

            # Extract the file creation date
            c_timestamp = os.path.getctime(path)
 
            # convert creation timestamp into DateTime object
            c_datestamp = datetime.datetime.fromtimestamp(c_timestamp)

            # Append the data to the DataFrame
            names.append({'name': name_dataframe, 'path': complete_path, 'creation_date': c_datestamp})

            # Sort the dataframe by creation_date (the fist register will be the most recent experiment)
            

    return pd.DataFrame(names)

def read_tdms(df):

    tdms_file = TdmsFile.read(path)

    
