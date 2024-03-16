# IMPORTS
# Typical imports
import numpy as np
import pandas as pd
import datetime
# File import
from nptdms import TdmsFile   # Import tdms files
import requests   # Make http GET and POST requests
import os   # Import data from directory
# plot
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
# Others
from io import StringIO   # Handle different types of I/O
from dotenv import dotenv_values   # Load environment variables from a .env file in an application
import re
import duckdb
# Processing
import scipy #import signal
from scipy.optimize import curve_fit
import statsmodels.api as sm
from scipy.interpolate import interp1d



# AUXILIARY FUNCTIONS
def extract_data():
    # create a connection to a file called 'file.db'
    con = duckdb.connect("./data/Silver/LabSilver.db")
    # Query to extract data from database
    query_full = """
    SELECT
        ID,
        file_title,
        load_ts,
        time_s,
        sensor1_ohm,
        sensor2_ohm,
        sensor3_ohm,
        sensor4_ohm,
        bottle1_ppb,
        bottle2_ppb,
        bottle3_ppb,
        date_timestamp
    FROM data_methane_line;
    """
    data_df = con.execute(query_full).df()
    return data_df


def get_nonzero_column(df):
    temp_df = df.filter(like='bottle')
    nonzero_counts = temp_df.sum()  # Contar valores no cero por columna
    if nonzero_counts.sum() == 0:
        nonzero_column = 'no_process'
    else:
        nonzero_column = nonzero_counts[nonzero_counts != 0].idxmax()
    return nonzero_column


def sensor_processing(df, bottle_name):
    pos = []
    datetime = []
    prev_value = 0

    for index, row in df.iterrows():
        # Primer valor
        if index == df.index[0]:
            pos.append([index, None])
        
        # Inicia adsorción
        elif prev_value < row[bottle_name]:
            pos[-1][1] = index-1
            pos.append([index, None])
        
        # Fin adsorción
        elif prev_value > row[bottle_name]:
            pos[-1][1] = index-1
            pos.append([index, None])
        
        # Store prev_value
        prev_value = row[bottle_name]

    # Last value
    pos[-1][1] = df.index[len(df)-1]

    # Crear los DataFrames position_df_cero y position_df_mayor_cero
    pos_df = pd.DataFrame(pos, columns=['init_pos', 'final_pos'])
    pos_df['bottle_cycle_ppb'] = df.loc[pos_df['init_pos'], bottle_name].values.astype(int)
    return pos_df


def add_date_to_pos(pos_df):
    datetime_list = []

    for index, row in pos_df.iterrows():
        # Obtain the position value
        pos_temp = row['final_pos']

        # Store the datetime for last element of each semicycle
        timestamp_value = df.loc[pos_temp]['date_timestamp']

        # Store the value in the list
        datetime_list.append(timestamp_value)

    # Transform the list to panda serie
    timestamps_series = pd.Series(datetime_list)

    # Add the serie to dataframe
    pos_df['final_date_timestamp'] = timestamps_series
    
    return pos_df


def desplaced_column(df, pos_df):
    df_copy = df.copy()
    # Iterar sobre las filas de pos_df y actualizar df_drift
    for index, row in pos_df.iterrows():
        # Only for adsortion semicycles
        if row['bottle_cycle_ppb'] != 0:
            # Create new fragment data
            fragment_list = [row['bottle_cycle_ppb']]*20
        
            # Overwrite the fragment
            final_pos = row['final_pos']
            final_pos_20 = final_pos + 19
            
            # Check if the final_pos_20 is smaller than dataframe length. If it's bigger, the fragment_list won't overwrite
            if df_copy.index[len(df_copy)-1] > final_pos_20:
                # Overwrite the data
                df_copy.loc[final_pos:final_pos_20, 'bottle_ppb_desplaced'] = fragment_list
    return df_copy


# Función para escribir en la base de datos
def write_df_to_db(con, df, table_name, query_write):
    # Formatear las fechas en el DataFrame
    #df = format_dates_in_df(df)
    
    # Obtener los nombres de las columnas del DataFrame
    columns = ','.join(df.columns)
    
    # Iterar sobre cada fila del DataFrame e insertarla en la base de datos
    for index, row in df.iterrows():
        # Extraer los valores de una fila
        values = tuple(row)
        # Construir la consulta de escritura
        query = query_write.format(table_name=table_name, columns=columns, values=values)
        print(query)
        con.execute(query)



# MAIN FUNCTIONS
def electrical_data_transform(df, sensor_name):
    # Extract data from silver database
    data_df = extract_data()
    exp_name_list = data_df['file_title'].unique()

    # Create empty dataframes
    pos_complete_df = pd.DataFrame()
    data_complete_df = pd.DataFrame()
    response_complete_df = pd.DataFrame()

    for exp_name in exp_name_list:
        df = data_df.loc[(data_df['file_title'] == exp_name)]

        # Obtain the column of bottle concentration
        bottle_name = get_nonzero_column(df)
        sensor_names = ['sensor1_ohm', 'sensor2_ohm', 'sensor3_ohm', 'sensor4_ohm']
        
        # In the case that the experiment was made with some gas
        if bottle_name != 'no_process':
            # Obtain the initial and final position per each cycle
            pos_df = sensor_processing(df, bottle_name)
            # Add date to pos_df
            pos_df = add_date_to_pos(pos_df)
            # Add the name file
            pos_df = pos_df.assign(file_title=exp_name)    

            # Create a column with displaced values
            df['bottle_ppb_desplaced'] = df[bottle_name]
            df = desplaced_column(df, pos_df)

            # Calculate data without drift 
            for sensor_name in sensor_names:
                # Change sensor name
                dict_name = {'sensor1_ohm': 's1', 'sensor2_ohm': 's2', 'sensor3_ohm': 's3', 'sensor4_ohm': 's4'}
                short_name = dict_name[sensor_name]

                # Obtain the medium value of the signal
                medium_value = df[sensor_name].mean()

                # Create new column NaN
                drift_curve = f"{short_name}_drift_curve"
                df[drift_curve] = np.nan
                df.loc[df['bottle_ppb_desplaced'] == 0, drift_curve] = df[sensor_name]

                # Spline interpolation (order 2)
                drift_curve_corr = f"{short_name}_drift_curve_corr"
                df[drift_curve_corr] = df[drift_curve].interpolate(method='spline', order=1)  

                # Filter to drift correction
                alpha = 0.1 # depends on fs and desired cutoff frequency
                signal_filtered = scipy.signal.lfilter([alpha], [1, -(1-alpha)], df[drift_curve_corr])

                # Calculate the difference
                signal_without_drift_2 = df[sensor_name] - signal_filtered

                # Add the medium value to each column item
                value_medium = df[sensor_name].mean()
                signal_without_drift_2 = signal_without_drift_2.add(value_medium)

                # Store the data in the dataframe
                without_drift_name = f"{short_name}_without_drift"
                df[without_drift_name] = signal_without_drift_2

            # Append the dictionary
            if pos_complete_df.empty:
                pos_complete_df = pos_df.copy()
                data_complete_df = df.copy()
            else:
                pos_complete_df = pd.concat([pos_complete_df, pos_df], ignore_index=True) 
                data_complete_df = pd.concat([data_complete_df, df], ignore_index=True)

    # Modify de dataframe
    pos_complete_df['ID'] = pos_complete_df.reset_index().index
    reorder_columns = ['ID', 'file_title', 'init_pos', 'final_pos', 'bottle_cycle_ppb', 'final_date_timestamp']
    pos_complete_df = pos_complete_df.reindex(columns=reorder_columns)
    data_complete_df['date_timestamp'] = data_complete_df['date_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_complete_df['load_ts'] = data_complete_df['load_ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_complete_df = data_complete_df.fillna(value=0)

    # WRITE DATA TO GOLD DATAFRAME
    # Connect with database
    conn = duckdb.connect("C:/Users/carlo/NOySI/data/Gold/LabGold.db")

    # Build the query
    table_name = 'data_methane_processed'   # Construct table name 
    query_write = """
        INSERT INTO {table_name} ({columns})
        VALUES {values};
    """
            
    # Write the data
    write_df_to_db(conn, data_complete_df, table_name, query_write)
    