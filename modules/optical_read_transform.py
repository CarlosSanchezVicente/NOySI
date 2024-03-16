# Imports
import pandas as pd
import numpy as np
from io import StringIO
import matplotlib.pyplot as plt
import requests
from dotenv import dotenv_values
import datetime
import os   # Import data from directory
import duckdb



# AUXILIARY FUNCTIONS
# Used in auxiliary functions
def create_folder(name_dataframe, line):
    # Obtain current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Define and create the path to create new folder
    folder_path = os.path.join('../data/Bronze/optical_measurement/', current_date)

    # Check if the folder exists or not
    if not os.path.exists(folder_path):
        # Create new folder if it isn't exist
        os.makedirs(folder_path)
    
    # Include in the file name the line name
    name_dataframe = name_dataframe + '_' + line + '.txt'
    
    # Create the complete path with the name of dataframe
    bronze_path = os.path.join(folder_path, name_dataframe)
    
    return bronze_path


# Functions to read data
def read_txt(path):
    # Open '.tsv' file
    with open(path, 'r') as file:
        # Perform operations on the file
        content = file.read()
    return content


def write_txt(string, path):
    # Store this string in bronze folder
    with open(path, "w") as text_file:
        text_file.write(string)


def read_directory_txt(process_type, path):    
    # Create an empty list to store data
    names = []
    data_df = pd.DataFrame()
    
    # Obtain the list of the files in the directory
    files_txt = [file for file in os.listdir(path) if file.endswith(".txt")]
        
    for file_txt in files_txt:
        # Extract dataframe name from the name_file
        name_dataframe = file_txt.split('_')[0]   # Extract the name from the file
        name_dataframe = name_dataframe.replace("%", "")   # Remove % due to it's could cause problems
        # Constructs the complete path to the TDMS file
        complete_path_source = os.path.join(path, file_txt)
            
        # Extract the file creation date
        timestamp = os.path.getctime(complete_path_source)

        # convert creation timestamp into DateTime object
        datestamp = datetime.datetime.fromtimestamp(timestamp)
            
        # Append the name to the DataFrame name
        names.append({'name': name_dataframe, 'path': complete_path_source, 'creation_date': datestamp})
                    
    # Sort dataframe by creation_date
    names_pd = pd.DataFrame(names)
    names_pd = names_pd.sort_values(by='creation_date', ascending=True)
    
    return names_pd


def check_time(names):    
    # Extract the date of last intake
    date_df = pd.read_csv('../data/most_recent_data_charge.csv')
    last_update_date = date_df['most_recent_data_charge'][0]
    
    # Filter the names
    names_filtered = names[names['creation_date'] > last_update_date]
    
    return names_filtered


def transform_date(string, type_date):
    if type_date == 'start':
        string_date = datetime.datetime.strptime(string, '%a %b %d %H:%M:%S CET %Y')
        string_format = string_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    else:
        string_format = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    return string_format


def read_data_store_data(complete_path_source, name_dataframe, line):
    # Example path: 'G:/Otros ordenadores/PC Línea Metano/Espectros/MED-74_HDX016921__0__12-32-02-194.txt'
    
    # Read the data
    content = read_txt(complete_path_source)
    
    # Store this string in bronze folder
    bronze_path = create_folder(name_dataframe, line)
    
    # Write the data in txt (bronze)
    write_txt(content, bronze_path)
    
    return content 


def transform_optical_data(content, name_dataframe):
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    if 'Date: ' in lines[1]:
        start_date = lines[1].split('Date: ')[1]
    else:
        for index, line in enumerate(lines):
            if 'Date: ' in line:
                start_date = lines[index].split('Date: ')[index]

    # Transform the format date
    start_date_format = transform_date(start_date, 'start')

    # Eliminar las líneas que no contienen datos espectrales
    start_idx = lines.index(">>>>>Begin Spectral Data<<<<<")

    # Obtain the axis for each spectrum
    wavelength_data = lines[start_idx + 1]
    intensity_data = lines[start_idx + 2:]

    # Prepare wavelength_data
    wavelength_list = [value.strip() for value in ''.join(wavelength_data).split('\t') if value.strip()]

    # Create empty dataframe
    data_df = pd.DataFrame()

    # Prepare intensity_data and create a dataframe
    for line in intensity_data:   #[0:2]
        # Split the string with the data
        intensity_data = [value.strip() for value in ''.join(line).split('\t') if value.strip()]

        # Format the date of data
        date_format = transform_date(intensity_data[0], 'other')

        # Remove the date from the data
        intensity_data = intensity_data[1:]

        # Create a dataframe with columns
        df = pd.DataFrame({'wavelength': wavelength_list, 'intensity': intensity_data})

        # Create others columns
        df['start_date'] = date_format
        df['name'] = name_dataframe   #---------------Sustituir por variable
        df['spectrometer'] = (lines[3]).split('Spectrometer: ')[1]
        df['trigger_mode'] = (lines[4]).split('Trigger mode: ')[1]
        df['integration_time_s'] = (lines[5]).split('Integration Time (sec): ')[1]
        df['scans_to_avg'] = (lines[6]).split('Scans to average: ')[1]
        df['nonlinearity_corr'] = (lines[7]).split('Nonlinearity correction enabled: ')[1]
        df['boxcar_width'] = (lines[8]).split('Boxcar width: ')[1]
        df['x_axis_mode'] = (lines[10]).split('XAxis mode: ')[1]
        df['pixels_number'] = (lines[11]).split('Number of Pixels in Spectrum: ')[1]

        # Append to complete dataframe
        if data_df.empty:
            data_df = df.copy()
        else:
            data_df = pd.concat([data_df, df], ignore_index=True)
            
    return data_df


def transform_optical_data_inlist(content, name_dataframe):
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    if 'Date: ' in lines[1]:
        start_date = lines[1].split('Date: ')[1]
    else:
        for index, line in enumerate(lines):
            if 'Date: ' in line:
                start_date = lines[index].split('Date: ')[index]

    # Transform the format date
    start_date_format = transform_date(start_date, 'start')

    # Eliminar las líneas que no contienen datos espectrales
    start_idx = lines.index(">>>>>Begin Spectral Data<<<<<")

    # Obtain the axis for each spectrum
    wavelength_data = lines[start_idx + 1]
    intensity_data = lines[start_idx + 2:]

    # Prepare wavelength_data. This is common to all spectra
    wavelength_list = [value.strip() for value in ''.join(wavelength_data).split('\t') if value.strip()]
    # Transform each string to float
    wavelength_list = [float(x.replace(',', '.')) for x in wavelength_list]

    # Create empty dataframe
    data_df = pd.DataFrame()
    config_df = pd.DataFrame(index=[0])
    df_temp = pd.DataFrame()

    # DATAFRAME WITH CONFIGURATION
    # Add the configuration parameters to the dataframe. Transform some columns from string to float. After that, reduce the
    # reserved memory for this variable from 64 to 16 due to the numbers won't be bigger than 65504.0.

    # Biggest number calculation for 16 bits (IEEE 754): 1 sing bit, 5 exponenet bits (from -14 to +15), 10 franction bits
    # (2**0 + 2**-1 + 2**-2 + 2**-3 + 2**-4 + 2**-5 + 2**-6 + 2**-7 + 2**-8 + 2**-9 + 2**-10) * 2**15

    config_df['experiment_name'] = name_dataframe
    config_df['start_timestamp'] = start_date_format
    config_df['load_ts'] = str(datetime.datetime.now())
    config_df['spectrometer'] = (lines[3]).split('Spectrometer: ')[1]
    config_df['trigger_mode'] = np.float16( float((lines[4]).split('Trigger mode: ')[1]))
    config_df['integration_time_s'] = np.float16( float((lines[5]).split('Integration Time (sec): ')[1].replace(',', '.')))
    config_df['scans_to_avg'] = np.float16( float((lines[6]).split('Scans to average: ')[1]))
    config_df['nonlinearity_corr'] = [True if (( (lines[7]).split('Nonlinearity correction enabled: ')[1] ) == 'true') else False]
    config_df['boxcar_width'] = np.float16( float((lines[8]).split('Boxcar width: ')[1]))
    config_df['x_axis_mode'] = (lines[10]).split('XAxis mode: ')[1]
    config_df['pixels_number'] = np.int16( int((lines[11]).split('Number of Pixels in Spectrum: ')[1]))


    # DATAFRAME WITH DATA
    # Prepare intensity_data and create a dataframe
    for idx, line in enumerate(intensity_data):   #[0:2]
        # Split the string with the data
        strip_line = [value.strip() for value in ''.join(line).split('\t') if value.strip()]

        # Format the date of data
        date_format = str(transform_date(strip_line[0], 'other'))

        # Remove the date from the data
        intensity_data = strip_line[1:]
        # Transform each string to float
        intensity_data = [float(x) for x in intensity_data]

        # Create a dataframe with columns. Wavelength_list only stores the first time.
        if idx == 0:
            df_dat = pd.DataFrame({'wavelength': [wavelength_list], 'intensity': [intensity_data]})
            #df_dat['current_time'] = time
        else:
            # Store the intensity only
            df_dat = pd.DataFrame({'intensity': [intensity_data]})
            #df_dat['current_time'] = time

        # Create others columns in temporal dataframe to add after loop
        df_temp = pd.DataFrame({'name': name_dataframe, 'current_timestamp': date_format}, index=[0])

        # Append to complete dataframe and create others columns in temporal dataframe to add after loop
        if data_df.empty:
            data_df = df_dat.copy()
            df_temp2 = df_temp.copy()
        else:
            data_df = pd.concat([data_df, df_dat], axis=1)
            df_temp2 = pd.concat([df_temp2, df_temp], ignore_index=True)

    # Transpose the dataframe with the data
    data_df_transpose = data_df.transpose()

    # Add the index as new column
    data_df_transpose.reset_index(inplace=True)

    # Add another row to temporal dataframe
    new_row = df_temp2.iloc[0].copy()  # Copiar la primera fila
    df_temp3 = pd.concat([new_row.to_frame().T, df_temp2], ignore_index=True)

    # Fix the temporal and data dataframe
    data_df_result = pd.concat([df_temp3, data_df_transpose], axis=1)
    
    return config_df, data_df_result


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
def read_transform_optical():
    path = 'G:/Otros ordenadores/PC Línea Metano/Espectros/'
    process_type = 'total'
    line = 'MethaneLine'

    # Obtain the files in the directory
    names_files = read_directory_txt('total', path)
        
    # In the case that the user select a date to filter the name files to charge in db. 
    # If the process_type == 'total' the dataframe doesn't change
    if process_type == 'time':
        names_files = check_time(names_files)
        
    # Create empty dataframe
    config_complete_df = pd.DataFrame()
    data_complete_df = pd.DataFrame()
        
    # Extract the data from each file
    for index, row in names_files.iterrows():
        # Obtain the complete path and name for each experiment
        complete_path_source = row['path']
        name_dataframe = row['name']
        print('Path: ', complete_path_source, ' | Dataframe name: ', name_dataframe)
        
        # Extract data from tdms and store the data in bronze folder
        new_data = read_data_store_data(complete_path_source, name_dataframe, line)
        
        # Create the dataframe with the data
        df_config, df_data = transform_optical_data_inlist(new_data, name_dataframe)
        
        # Append the data to general dataframe
        if data_complete_df.empty:
            config_complete_df = df_config.copy()
            data_complete_df = df_data.copy()
        else:
            config_complete_df = pd.concat([config_complete_df, df_config], ignore_index=True)
            data_complete_df = pd.concat([data_complete_df, df_data], ignore_index=True)

    # Change the number columns and finals transformations
    # Add the index to the dataframe
    data_complete_df['index_col'] = data_complete_df.index
    # Change the column names
    data_complete_df.rename(columns={'index_col': 'ID', 
                                    'name': 'experiment_name', 
                                    'index': 'axis', 
                                    0: 'spectra'}, inplace=True)
    # Change the column sort
    data_complete_df = data_complete_df[['ID', 'experiment_name', 'current_timestamp', 'axis', 'spectra']]

    # STORE THE DATA IN DB
    # Connect with database
    con = duckdb.connect("./data/Silver/LabSilver.db")

    # Build the query
    #table_name = ID_dict['MethaneLine']['db_name']   # Construct table name 
    query_write = """
        INSERT INTO {table_name} ({columns})
        VALUES {values};
    """

    # Write the configuration optical process
    #write_df_to_db(con, config_complete_df, 'optical_parameters', query_write)
    # Write the spectra
    write_df_to_db(con, data_complete_df, 'optical_spectra', query_write)