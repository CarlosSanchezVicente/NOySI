# IMPORTS LIBRARIES
# Typical imports
import numpy as np
import pandas as pd
import datetime
# File import
from nptdms import TdmsFile   # Import tdms files
#import requests   # Make http GET and POST requests
import os   # Import data from directory
# Others
#from io import StringIO   # Handle different types of I/O
from dotenv import dotenv_values   # Load environment variables from a .env file in an application
#import re
import duckdb
#import warnings
import streamlit as st
# Processing
#import scipy 
#import signal

# IMPORT FUNCTIONS FROM MODULES
from modules import read_directory as dir
from modules import duckdb as db


# AUXILIARY FUNCTIONS
def create_folder(name_dataframe, line):
    # Obtain current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Define and create the path to create new folder
    folder_path = os.path.join('./data/Bronze/electrical_measurement/', current_date)

    # Check if the folder exists or not
    if not os.path.exists(folder_path):
        # Create new folder if it isn't exist
        os.makedirs(folder_path)
    
    # Include in the file name the line name
    name_dataframe = name_dataframe + '_' + line
    
    # Create the complete path with the name of dataframe
    bronze_path = os.path.join(folder_path, name_dataframe)
    
    return bronze_path


def read_data_store_data(complete_path_source, name_dataframe, line):
    # Read tdms data
    tdms_file = TdmsFile.read(complete_path_source)
    
    # Read the data from 
    new_data = {}
    for group in tdms_file.groups():
        for channel in group.channels():
            new_data[channel.name] = channel[:].tolist()
    
    # Transform the dictionary to dataframe
    print('Nombre: ', name_dataframe)
    new_df = pd.DataFrame(new_data)
    
    # Store this dataframe in bronze folder
    bronze_path = create_folder(name_dataframe, line)
    new_df.to_csv(bronze_path, index=False)
    
    return new_df


def transform_df(df, ID_dict, file_name, line):
    #print('Previous column names:', df.columns, '\n')
    # Remove space blanc before or after each column name
    df.rename(columns=lambda x: x.strip(), inplace=True)
        
    # Create column ID
    df.reset_index(inplace=True)
    
    # Create file_title column with the file name
    df['file_title'] = file_name
        
    # Create load_ts column with ingestion date
    df['load_ts'] = str(datetime.datetime.now()) 
        
    # Create variable name of new order and map
    maps = ID_dict[line]['DB_map']
    new_order = ID_dict[line]['DB_new_order']
        
    # Change the column names such as the database
    df.rename(columns=maps, inplace=True)
    df = df[new_order]
    
    # The date_timestamp column includes dates in string format, but in a format: "00:37:17.00,20-Jul-2023". And in the 
    # database I am required to be in this format: YYYYY-MM-DD HH:MM:SS[.US][±HH:MM| ZONE]. But when saving the datetime 
    #data in the database I get an error, so I transform it into a string and duckdb manages to parse it.
    df_v2 = df.copy()
    df_v2['date_timestamp'] = pd.to_datetime(df_v2['date_timestamp'], format="%H:%M:%S.%f,%d-%b-%Y")   # String to datetime
    #df['date_time'] = df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S%z')   # Change the format datetime
    df_v2['date_timestamp'] = df_v2['date_timestamp'].astype(str)   # Datetime to string
    
    return df_v2


def transform_bottle_columns(df, ID_dict, line):
    # Obtain the columns name in which it is included '\[Botella '
    bottle_columns = df.columns[df.columns.str.contains('\[Botella ')].tolist()
    
    # Create an empty dictionary
    bottle_dict = {}

    # Iterar sobre la lista de columnas de botellas
    for column in bottle_columns:
        # Extract the number from '[Botella 1-Nada] [ppbv]'. First extract: '[Botella 1' and after that extract the number.
        bottle_number = column.split('-')[0].split()[-1]   
        # Generar el nombre de la clave
        key = f'bottle{bottle_number}_ppb'
        # Añadir la entrada al diccionario
        bottle_dict[column] = key
    
    # Includes the new key-value pairs in the dictionary
    ID_dict[line]['DB_map'].update(bottle_dict)
    
    return ID_dict


# MAIN FUNCTION
def obtain_data_electrical_m(process_type, ID_dict, line, path):
    #process_type = 'total'
    #line = 'MethaneLine'

    # Create empty dataframe
    columns = ID_dict[line]['DB_new_order']
    data_df = pd.DataFrame(columns=columns)
    
    # Obtain the files in the directory
    names_files = dir.read_directory_tdms(path)
    
    # In the case that the user select a date to filter the name files to charge in db. 
    # If the process_type == 'total' the dataframe doesn't change
    if process_type == 'time':
        names_files = dir.check_time(names_files)
    
    #names_files_v2 = names_files.iloc[0:1]
    
    # Extract the data from each file
    for index, row in names_files.iterrows():
        # Obtain the complete path and name for each experiment
        complete_path_source = row['path']
        name_dataframe = row['name']
        print('Path: ', complete_path_source, ' | Dataframe name: ', name_dataframe)

        # Extract data from tdms and store the data in bronze folder
        new_data = read_data_store_data(complete_path_source, name_dataframe, line)

        # Transform first the bottles column names due to this names would be different in each experiment
        ID_dict_trans = transform_bottle_columns(new_data, ID_dict, line)

        # Transform the dataframe, includes other colums, sort columns and rename columns (the rest of the columns)
        new_data_trans = transform_df(new_data, ID_dict_trans, name_dataframe, line)

        # Append dictionary to dataframe. In the case that the dataframe is empty, the data is assinged directly to 
        # the dataframe
        if data_df.empty:
            data_df = new_data_trans.copy()
        else:
            data_df = pd.concat([data_df, new_data_trans], ignore_index=True)

    # Print in streamlit the experiment added to database
    unique_values = data_df['file_title'].unique().tolist()
    st.markdown('#### New electrical experiment:')
    st.write(pd.DataFrame({'Experiments processed': unique_values}))

    # STORE THE DATA IN SILVER DB
    # Connect with database
    con = duckdb.connect("./data/Silver/LabSilver.db")
    table_name = ID_dict['MethaneLine']['db_name']   # Construct table name

    if process_type == 'time':
        # Change the ID column if process_type is different to 'total'. In the case of process_type='time', ID is different to index and
        # the first value of this column will be the last value stored in the database. 
        # Build the query
        query_ID = "SELECT MAX(ID) AS max_id FROM " + table_name + ";"

        # Read the las value of database
        last_ID_df = con.execute(query_ID).df()
        last_ID_value = last_ID_df.iloc[0,0] + 1

        # Create a new column ID using the last value of database
        data_df['ID'] = range(last_ID_value, len(data_df) + last_ID_value)

    # Build the query
    print(table_name)
    query_write = """
        INSERT INTO {table_name} ({columns})
        VALUES {values};
    """

    # Write the data
    db.write_df_to_db(con, data_df, table_name, query_write)

    # Return dataframe to process
    return data_df