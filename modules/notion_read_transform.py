# IMPORTS
import pandas as pd
import requests
from dotenv import dotenv_values
from datetime import datetime
import json
import notion_client
import duckdb
import statistics
from datetime import datetime
import streamlit as st 
import os

# IMPORT FUNCTIONS FROM MODULES
#from modules import notion_trans_s as transform_notion
from modules import duckdb as db
from modules import read_directory as dir

# SOURCES
# API Notion: https://www.notion.so/es-la/help/create-integrations-with-the-notion-api
#             https://www.youtube.com/watch?v=M1gu9MDucMA
#             https://developers.notion.com/reference/authentication
#             https://www.python-engineer.com/posts/notion-api-python/



# DEFINITIONS
#config = dotenv_values('./_wip_/.env')
#config = dotenv_values('.env')
#config = dotenv_values(os.path.join('..', '.env'))
#NOTION_TOKEN = config.get('NOTION_TOKEN')   # NOTION_TOKEN
#MATERIALES_DB_ID = config.get('MATERIALES_DB_ID')   # MATERIALES_DB_ID
#DISOLUCIONES_DB_ID = config.get('DISOLUCIONES_DB_ID')   # DISOLUCIONES_DB_ID
#SENSORES_DB_ID = config.get('SENSORES_DB_ID')   # SENSORES_DB_ID
#LED_DB_ID = config.get('LED_DB_ID')   # LED_DB_ID
#GASES_DB_ID = config.get('GASES_DB_ID')   # GASES_DB_ID
#MEDIDAS_DB_ID = config.get('MEDIDAS_DB_ID')   # MEDIDAS_DB_ID
#path_db = config.get('path_db')

# DEFINITIONS
#ID_list = [MATERIALES_DB_ID, DISOLUCIONES_DB_ID, SENSORES_DB_ID, LED_DB_ID, GASES_DB_ID, MEDIDAS_DB_ID]

#headers = {
#    'Authorization': 'Bearer ' + NOTION_TOKEN,
#    'Content-Type': 'application/json',
#    'Notion-Version': '2022-06-28'
#}

ID_dict = {'MATERIALES_DB':{'db_name': 'materials',
    
                            'DB_new_order':  ['index','id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 
                                              'Fabricante', 'Tipo', 'created_by', 'last_edited_by', 'created_time', 
                                              'last_edited_time', 'load_ts', 'Preparación', 'Otros compuestos', '% N', 
                                              '% H', '% O', '% Compuesto Princ.', 'BET (m2/g)', 'Espesor', 
                                              'Tamaño', 'Proporción'],
                            
                            'DB_map':  {'index': 'ID',
                                        'id': 'id_material',
                                        'Título': 'name_material',
                                        'Etiquetas': 'label',
                                        'parent': 'parent',
                                        'url':'url',
                                        'Realizado': 'realized_by',
                                        'Fabricante': 'manufacturer',
                                        'Tipo': 'material_type',
                                        'created_by': 'record_created_by',
                                        'last_edited_by': 'record_last_edited_by',
                                        'created_time': 'record_created_time',
                                        'last_edited_time': 'record_last_edited_time',
                                        'Preparación': 'preparation_date',
                                        'Otros compuestos':'others_compounds',
                                        '% N': 'n_percentage', 
                                        '% H': 'h_percentage',
                                        '% O': 'o_percentage',
                                        '% Compuesto Princ.': 'main_comp_percentage', 
                                        'BET (m2/g)': 'bet_m2_g',
                                        'Espesor':'thickness_nm', 
                                        'Tamaño': 'size_material_nm', 
                                        'Proporción': 'ratio'}
                           }, 
           'DISOLUCIONES_DB':{'db_name': 'solutions', 
                              
                              'DB_new_order':  ['index','id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 
                                                'created_by', 'last_edited_by', 'created_time', 'last_edited_time', 
                                                'load_ts', 'Preparación', 'Concentración', 'Disolvente', 'Soluto', 
                                                'Dopante', 'Sensor'],
                              
                              'DB_map':{'index': 'ID',
                                        'id': 'id_solution',
                                        'Título': 'name_solution',
                                        'Etiquetas': 'label',
                                        'parent': 'parent',
                                        'url': 'url',
                                        'Realizado': 'realized_by',
                                        'created_by': 'record_created_by', 
                                        'last_edited_by': 'record_last_edited_by',
                                        'created_time': 'record_created_time',
                                        'last_edited_time': 'record_last_edited_time',
                                        'Preparación': 'preparation_date',
                                        'Concentración': 'ratio_materials',
                                        'Disolvente': 'id_solvent',
                                        'Soluto': 'id_solute', 
                                        'Dopante':'id_dopant',
                                        'Sensor': 'id_sensor'}
                              
                             },
           'SENSORES_DB': {'db_name': 'sensors',
                           
                           'DB_new_order': ['index','id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 'Tipo', 
                                            'created_by', 'last_edited_by', 'created_time', 'last_edited_time', 'load_ts', 
                                            'Método dep.', 'Membrana 1', 'Membrana 2', 'Membrana 3', 'Membrana 4', 
                                            'Disol. empleadas', 'Parámetros dep.'],
                           
                           'DB_map':   {'index': 'ID', 
                                        'id': 'id_sensor',
                                        'Título': 'name_sensor',
                                        'Etiquetas': 'label', 
                                        'parent': 'parent',
                                        'url': 'url',
                                        'Realizado': 'realized_by',
                                        'Tipo': 'sensor_type', 
                                        'created_by': 'record_created_by', 
                                        'last_edited_by': 'record_last_edited_by', 
                                        'created_time': 'record_created_time', 
                                        'last_edited_time': 'record_last_edited_time', 
                                        'Método dep.': 'deposition_method', 
                                        'Membrana 1': 'susbtrate_1', 
                                        'Membrana 2': 'susbtrate_2', 
                                        'Membrana 3': 'susbtrate_3', 
                                        'Membrana 4': 'susbtrate_4', 
                                        'Disol. empleadas': 'solutions_used', 
                                        'Parámetros dep.': 'deposition_parameters'}
                          
                          }, 
           'LED_DB': {'db_name':'leds',
                      
                      'DB_new_order':  ['index','id', 'Led', 'parent', 'url', 'created_by', 'last_edited_by', 
                                        'created_time', 'load_ts', 'last_edited_time', 'Volt. utilizado (V)', 
                                        'Corr. utilizada (mA)', 'Voltaje tip.', 'Corriente tip.', 'Long. onda (nm)', 
                                        'Potencia Óptica (mW)', 'Comentarios'],
                      
                      'DB_map':{'index': 'ID',
                                'id': 'id_led',
                                'Led': 'name_led',
                                'parent': 'parent',
                                'url': 'url',
                                'created_by': 'record_created_by',
                                'last_edited_by': 'record_last_edited_by',
                                'created_time': 'record_created_time',
                                'last_edited_time': 'record_last_edited_time',
                                'Volt. utilizado (V)': 'voltage_V_used',
                                'Corr. utilizada (mA)': 'current_mA_used',
                                'Voltaje tip.': 'voltage_range',
                                'Corriente tip.': 'current_range',
                                'Long. onda (nm)': 'wavelength_nm',
                                'Potencia Óptica (mW)': 'optical_power_mW',
                                'Comentarios': 'comments'}
                     }, 
           'GASES_DB':{'db_name': 'gases',
                      
                       'DB_new_order': ['index','id', 'Título', 'Etiquetas', 'parent', 'url', 'created_by', 
                                        'last_edited_by', 'created_time', 'last_edited_time', 'load_ts', 
                                        'Max. Concentración'],
                       
                       'DB_map':{'index': 'ID', 
                                 'id': 'id_gas',
                                 'Título': 'name_gas',
                                 'Etiquetas': 'label',
                                 'parent': 'parent',
                                 'url': 'url',
                                 'created_by': 'record_created_by',
                                 'last_edited_by': 'record_last_edited_by',
                                 'created_time': 'record_created_time',
                                 'last_edited_time': 'record_last_edited_time',
                                 'Max. Concentración': 'max_concentration_ppb'}
                      }, 
           'MEDIDAS_DB': {'db_name': 'measurements',
                          
                          'DB_new_order':  ['index', 'ID_conn', 'id', 'Título', 'Gas', 'parent', 'url', 'Realizado', 
                                            'created_by', 'last_edited_by', 'created_time', 'last_edited_time', 'load_ts', 
                                            'Proyecto', 'Concentraciones', 'Humedad', 'Equipo medida', 'Resultado', 
                                            'Línea', 'Sensor', 'Led', 'Gases'],
                          
                          'DB_map':{'index': 'ID',
                                    'ID_conn': 'conn_measurement',
                                    'id': 'id_measurement',
                                    'Título': 'name_measurement',
                                    'Gas': 'label',
                                    'parent': 'parent',
                                    'url': 'url',
                                    'Realizado': 'realized_by',
                                    'created_by': 'record_created_by',
                                    'last_edited_by': 'record_last_edited_by',
                                    'created_time': 'record_created_time',
                                    'last_edited_time': 'record_last_edited_time',
                                    'Proyecto': 'project',
                                    'Concentraciones': 'concetrations_ppb',
                                    'Humedad': 'humidity_percentage',
                                    'Equipo medida': 'measurement_equipment',
                                    'Resultado': 'result_measurement',
                                    'Línea': 'gases_line_used',
                                    'Sensor': 'id_sensor',
                                    'Led': 'id_led',
                                    'Gases': 'id_gases'}
                         }
          }



# AUXILIARY FUNCTIONS - EXTRACT DATA
def get_pages_100(headers, DATABASE_ID, pages_number, process_type, path):
    """Summary: function to obtain 100 pages of the databases or from last update ('process_type' indicates the behavior). This function 
        use the 'request' library to connecto to the API.

    Args:
        headers (dictionary): variable to store the connection header to Notion.
        DATABASE_ID (string): variable with the ID of the database from which the data is downloaded.
        pages_number (integer): number of pages to download from Notion.
        process_type (string): variable to know if the data ingestion is total or just an update since a specific date.
        path (string): path to store the json

    Returns:
        data (json): database data.
    """
    # url to the database
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    if process_type == 'number' or process_type == 'total':
        # Obtain the last 100 pages from Notion
        payload = {"page_size": pages_number}
        response = requests.post(url, json=payload, headers=headers)
    elif process_type == 'time':
        pass
    else:
        return print('Error: You have entered an incorrect value for the data entry type')
    
    # Store the json in the bronze file in google drive
    data = response.json()
    with open (path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data


def get_pages_more_100(headers, DATABASE_ID, path, pages_number=None):
    """Summary: function to obtain the number of pages specified of the databases. This function use the 'request' library to connecto to 
        the API.

    Args:
        headers (dictionary): variable to store the connection header to Notion.
        DATABASE_ID (string): variable with the ID of the database from which the data is downloaded.
        path (string): path to store the json
        pages_number (string, optional): path to store the json. Defaults to None.
    """
    # url to the database
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    # Check the number of pages
    get_all = pages_number is None
    page_size = 100 if get_all else pages_number

    # Post operation
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data["results"]

    # Redo the post request until all desired pages are extracted.
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])   # With extend method it's possible to add new element to result.

    # Store the json in the bronze file in google drive
    with open (path, 'w', encoding='utf8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    return results


def get_pages_select_date(NOTION_TOKEN, DATABASE_ID, path, date):
    """Summary: function to get the Notion database pages after a specified date. This function use the "notion_client" library to connect 
        with the API.

    Args:
        NOTION_TOKEN (string): token to connect to the Notion API.
        DATABASE_ID (string): ID of the database from which the pages are to be extracted.
        path (string): path to store the json.
        date (string): date from which the information will be extracted from the database. The format of date would be: YYYY-MM-DD
    Returns:
        data (json): database data.
    """
   # Create a client to connect with Notion API
    notion = notion_client.Client(auth=NOTION_TOKEN)

    # Filter to obtain the data using a timestamp
    filter = {  # error pertains to this filter
        "filter": {
            "and": [
                {
                    "timestamp": "created_time",
                    "created_time": {
                        "after": f"{date}T00:00:00"
                    }
                }
            ]
        }
    }

    # Query to obtain the data from the Notion using a filter by date
    response = notion.databases.query(
            DATABASE_ID,
            **filter
        )
    
    # Store the json in the bronze file in google drive
    data = response
    #data = response.json()
    #with open (path, 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)
    
    return data


def extract_data_from_json(pages):
    """Summary: function to extract the data from the one database

    Args:
        pages (json): json database data

    Returns:
        (dataframe): dataframe with the data
    """
    resultados = []
    type_list = []

    for result in pages['results']:
        properties = result.get('properties', {})
        result_dict = {'id': result['id'], 
                       'created_time': result['created_time'], 
                       'last_edited_time': result['last_edited_time'],
                       'created_by': result['created_by']['id'],
                       'last_edited_by': result['last_edited_by']['id'],
                       'parent': result['parent']['database_id'],
                       'url': result['url']} 

        # Add the element inside properties
        for key, value in properties.items():
            # Extract the type of each field to perform a different action depending on it.
            type = properties[key]['type']
            if type not in type_list:
                type_list.append(type)

            # If the type of field is a 'number'
            if type == 'number':
                # Obtain the value of the key 'number'
                number = properties[key]['number']

                # If the field is empty, store in the dataframe zero, otherwise store the number.
                if number == None:
                    result_dict[key] = 0
                else:
                    result_dict[key] = properties[key]['number']

            # If the type of field is a 'rich_text'.
            elif type == 'rich_text':
                # Obtain the different elements that are found within the list, because the value of this type of key is 
                # a list with a dictionary inside de list.
                rich_text_list = properties[key].get('rich_text', [])

                # Extract 'content' from 'text' if it exists. With this loop it's possible to move through the list.
                content = rich_text_list[0]['text']['content'] if rich_text_list else None #'NS'
                result_dict[key] = content

            # If the type of field is a 'select'.
            elif type == 'select':
                # Obtain the value of the key 'select'.
                select = properties[key]['select']

                # If select isn't value, store in the dataframe 'NS', otherwise store the information.
                
                if select == None:
                    result_dict[key] = None #'NS'
                else:
                    result_dict[key] = properties[key]['select']['name']
                

            # If the type of field is a 'date'.
            elif type == 'date':
                # Obtain the value of the key 'date'.
                date = properties[key]['date']

                # If select isn't value, store in the dataframe 'NS', otherwise store the information.
                
                if date == None:
                    result_dict[key] = None #'NS'
                else:
                    result_dict[key] = properties[key]['date']['start']
                

            # If the type of field is a 'title'.
            elif type == 'title':
                # Obtain the different elements that are found within the list, because the value of this type of key is 
                # a list with a dictionary inside de list.
                title_list = properties[key].get('title', [])

                # Extract 'content' from 'text' if it exists. With this loop it's possible to move through the list.
                content = title_list[0]['text']['content'] if title_list else None #'NS'
                result_dict[key] = content
  
            # If the type of field is a 'multi-select'.
            elif type == 'multi_select':
                # Obtain the different elements that are found within the list, because the value of this type of key is 
                # a list with a dictionary inside de list.
                multi_select_list = properties[key].get('multi_select', [])
                
                # Extract 'content' from 'text' if it exists. With this loop it's possible to move through the list.
                if len(multi_select_list)==1:
                    content_str = multi_select_list[0]['name'] if multi_select_list else None #'NS'
                else:
                    contents = []
                    for pos in range(0, len(multi_select_list)):
                        content = multi_select_list[pos]['name'] if multi_select_list else None #'NS'
                        contents.append(content)
                    content_str = ', '.join(contents)

                result_dict[key] = content_str
                
            # If the type of field is a 'relation'.
            elif type == 'relation':
                # Obtain the different elements that are found within the list, because the value of this type of key is a list
                # with a dictionary inside de list.
                relation_list = properties[key].get('relation', [])

                # Extract 'content' from 'text' if it exists. With this loop it's possible to move through the list.
                if len(relation_list)==1:
                    content_str = relation_list[0]['id'] if relation_list else None #'NS'
                else:
                    contents = []
                    for pos in range(0, len(relation_list)):
                        content = relation_list[pos]['id'] if relation_list else None
                        contents.append(content)
                    content_str = ', '.join(contents)

                result_dict[key] = content_str
                
            elif type == 'unique_id':
                # Obtain the unique ID for each measurement. This is the ID to connect with the optical and electrical
                # measurements
                ID_conn_list = properties[key].get('unique_id', [])
                #print(ID_conn_list)
                result_dict[key] = ID_conn_list['prefix'] + '-' + str(ID_conn_list['number'])

        resultados.append(result_dict)
        
    return pd.DataFrame(resultados)


# AUXILIARY FUNCTIONS - TRANSFORM DATA
def transform_rages(string):
    """Summary: function to transform the string with number o range in a integer.

    Args:
        str (string): string with number or range.

    Returns:
        (integer): number or range number mean.
    """
    # If the string includes '-' means that there is a range. If it doesn't include '-', there is a number.
    if string is None:
        return 0  # Return None if the value is None
    elif '-' in string:
        str2 = string.split(' - ')
        return statistics.mean([float(str2[0]), float(str2[1])])   # Return the mean of both numbers
    else:
        return float(string)


def remove_symbol_nm(string):
    """Summary: function to remove the unit or diferent symbols.

    Args:
        str (string): string with unit or symbols.

    Returns:
        (integer): number without symbols or unit.
    """
    if string is None:
        return 0  # Return None if the value is None
    else:
        # Remove the simbol '≤' if it's included
        if '≤' in string:
            str2 = string.split('≤')[1].strip()   # In this case: '≤ 50 nm' -> Remove '≤': ['',' 50 nm'] -> extract [1]: ' 50 nm' -> Remove ' ': '50 nm'
        else:
            str2 = string
        
        # Remove the unit and transform to nm if it's necessary
        str3 = str2.split(' ')
        if len(str3) == 1:
            return int(str3[0])
        else:
            if 'nm' in str3[1]:
                return int(str3[0])
            elif 'um' in str3[1]:
                return int(str3[0])*1000


def remove_symbol_humidity(string):
    """Summary: function to remove the unit or diferent symbols.

    Args:
        str (string): string with unit or symbols.

    Returns:
        (integer): number without symbols or unit.
    """
    if string is None:
        return 0  # Return None if the value is None
    else:
        str2 = string.split('%')
        return int(str2[0])


def remove_symbol_bottle(string):
    """Summary: function to remove the unit or diferent symbols.

    Args:
        str (string): string with unit or symbols.

    Returns:
        (integer): number without symbols or unit.
    """
    if string is None:
        return None  # Return None if the value is None
    else:
        if ('ppb' in string) or ('PPB' in string):
            str2 = string.lower().split('ppb')
            return float(str2[0])
        elif ('ppm' in string) or ('PPM' in string):
            str2 = string.lower().split('ppm')
            return float(str2[0])*1000


def sort_gases_names(string):
    if ',' in string:
        words = string.split(', ')
        words.sort()
        return ', '.join(words)
    else:
        return string


def replace_nan_nat_none(df):
    columns_name = df.columns
    # Check all columns
    for name in columns_name:
        # Check if the column includes NaN, NaT or None
        if df[name].isna().any():
            
            # Check if the column is object type. If the column isn't object transform the column to object. After that
            # with object column, it's possible to change NaN, NaT or None to 'unk' = unknown
            if df[name].dtype != 'object':
                df[name] = df[name].astype('object')
                
            # Replaces the NaN, NaT or None values by unknown
            df[name].fillna('unk', inplace=True)
    
    return df




# MAIN FUNCTIONS
def obtain_data_notion(process_type, date, pages_number=100):   #config
    """Summary: function to obtain the pages of the databases or from last update('process_type' indicates the behavior). 

    Args:
        process_type (string): it indicates the behavior of the ingestion. 
            - 'process_type'=number -> download all pages indicated in pages_number. 
            - 'process_type'=last_upload -> read the date of the last upload in the csv file.
            - 'process_type'=time -> download all pages from last update. 
        date (string, optional): date from which the information will be extracted from the database. The format of date would be: 
            YYYY-MM-DD. Defaults to 100. Defaults to None.
        pages_number (integer, optional): number of pages to download. Defaults to 100.

    Returns:
        pages (json): data from Notion
    """
    # Definition
    #NOTION_TOKEN = config.get('NOTION_TOKEN')   # NOTION_TOKEN
    headers = {
        'Authorization': 'Bearer ' + NOTION_TOKEN,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    #path_db = config.get('path_db')
    ID_list = ['MATERIALES_DB', 'DISOLUCIONES_DB', 'SENSORES_DB', 'LED_DB', 'GASES_DB', 'MEDIDAS_DB']
    st.markdown('#### New Notion records:')

    # Obtain and store data from each notion table
    for db_name in ID_list:
        print(db_name)
        
        # Create the name to store the data
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{db_name}_{current_date}"

        # Create database ID
        id_name = f'{db_name}_ID'
        DATABASE_ID = config[id_name]
        #exec(f'DATABASE_ID = config["{id_name}"]')

        # Obtain and store the data from Notion database
        # Create the path
        path = f"./data/Bronze/{file_name}.json"

        # If the user want to obtain a specific numbers of pages
        if process_type == 'number' or process_type == 'total':
            if pages_number == 100:
                pages = get_pages_100(headers, DATABASE_ID, 100, process_type, path)
            else:
                pages = get_pages_more_100(headers, DATABASE_ID, path, pages_number=None)
        # If the user want to obtain the pages from last update
        elif process_type == 'last_upload':
            date = dir.read_last_charge_date()
            pages = get_pages_select_date(NOTION_TOKEN, DATABASE_ID, path, date)
        # If the user want to obtain the pages from specific date
        elif process_type == 'date':
            pages = get_pages_select_date(NOTION_TOKEN, DATABASE_ID, path, date)
        else:
            print('Error: You have entered an incorrect value for the data entry type. \nYou have to introduce: "number" or "total"')
            #return 

        # Obtain a dataframe from json
        df = extract_data_from_json(pages)
        
        # It may be the case that some databases do not have any new records. In this case the code execution is not continued in order to avoid errors.
        if not df.empty:
            # COLUMN TRANSFORMATIONS COMMON TO ALL DATAFRAMES 
            # Remove space blanc before or after each column name
            df.rename(columns=lambda x: x.strip(), inplace=True)

            # Create column ID
            df.reset_index(inplace=True)
            
            # Create load_ts column with ingestion date
            df['load_ts'] = str(datetime.now())
            
            # Create variable name of new order and map 
            new_order = ID_dict[db_name]['DB_new_order']
            maps = ID_dict[db_name]['DB_map']
            
            # Change the column names such as the database
            df = df[new_order]
            df.rename(columns=maps, inplace=True)

            
            # TRANSFORMATION OF COLUMNS SPECIFIC TO EACH DATAFRAME
            if db_name == 'MATERIALES_DB':
                # Transform range to int
                df['main_comp_percentage'] = df['main_comp_percentage'].apply(lambda row: transform_rages(row))
                # Remove the units and symbols
                df['thickness_nm'] = df['thickness_nm'].apply(lambda row: remove_symbol_nm(row))
                # Remove the units and symbols
                df['size_material_nm'] = df['size_material_nm'].apply(lambda row: remove_symbol_nm(row))
                # Data charged to database
                st.markdown('##### Materiales stored to the database:')
                name_values = df['name_material'].tolist()
                st.write(pd.DataFrame({'Nombre de los materiales': name_values}))

            elif db_name == 'DISOLUCIONES_DB':
                # Data charged to database
                st.markdown('##### Solutions  stored to the database:')
                name_values = df['name_solution'].tolist()
                st.write(pd.DataFrame({'Nombre de las disoluciones': name_values}))

            elif db_name == 'SENSORES_DB':
                # Data charged to database
                st.markdown('##### Sensors  stored to the database:')
                name_values = df['name_sensor'].tolist()
                st.write(pd.DataFrame({'Nombre de los sensores': name_values})) 

            elif db_name == 'LED_DB':
                # Data charged to database
                st.markdown('##### Leds  stored to the database:')
                name_values = df['name_led'].tolist()
                st.write(pd.DataFrame({'Nombre de los leds': name_values}))

            elif db_name == 'GASES_DB':
                # Remove the units and symbols
                df['max_concentration_ppb'] = df['max_concentration_ppb'].apply(lambda row: remove_symbol_bottle(row))
                # Data charged to database
                st.markdown('##### Gases  stored to the database:')
                name_values = df['name_gas'].tolist()
                st.write(pd.DataFrame({'Nombre de los gases': name_values}))

            elif db_name == 'MEDIDAS_DB':
                # Remove the units and symbols
                df['humidity_percentage'] = df['humidity_percentage'].apply(lambda row: remove_symbol_humidity(row))
                # Add date to file name
                df['label'] = df['label'].apply(lambda row: sort_gases_names(row))
                # Data charged to database
                st.markdown('##### Measurements stored to the database:')
                name_values = df['conn_measurement'].tolist()
                st.write(pd.DataFrame({'Nombre de las medidas': name_values}))

                
            # Transform NaT, None, NaN to Unkown
            df = replace_nan_nat_none(df)
            
            # STORE THE DATA IN SILVER DB
            # Connect with database
            con = duckdb.connect(path_db)
            table_name = ID_dict[db_name]['db_name'] + '_hist'   # Construct table name

            if process_type == 'time':
                # Change the ID column if process_type is different to 'total'. In the case of process_type='time', ID is different to index and
                # the first value of this column will be the last value stored in the database. 
                # Build the query
                query_ID = "SELECT MAX(ID) AS max_id FROM " + table_name + ";"

                # Read the las value of database
                last_ID_df = con.execute(query_ID).df()
                last_ID_value = last_ID_df.iloc[0,0] + 1

                # Update the ID column
                df['ID'] = range(last_ID_value, len(df) + last_ID_value)
            
            # Build the query
            query_write = """
                INSERT INTO {table_name} ({columns})
                VALUES {values};
            """
            
            # Write the data
            db.write_df_to_db(con, df, table_name, query_write)

            # Return the experiment added
            #if db_name == 'MEDIDAS_DB':
            #    return name_values
    