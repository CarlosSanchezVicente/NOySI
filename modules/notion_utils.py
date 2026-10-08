# IMPORTS
import json
import logging
import re
import statistics
from datetime import datetime

import notion_client
import pandas as pd
import requests

import config as cfg_module

logger = logging.getLogger(__name__)


# SOURCES
# API Notion: https://www.notion.so/es-la/help/create-integrations-with-the-notion-api
#             https://www.youtube.com/watch?v=M1gu9MDucMA
#             https://developers.notion.com/reference/authentication
#             https://www.python-engineer.com/posts/notion-api-python/


# DEFINITIONS
# Mapeos de columnas Notion -> BBDD (constantes: no se modifican en ningún sitio).
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


# CONNECTION HELPERS (la configuración se recibe como parámetro; nada se lee al importar)
def build_headers(cfg):
    """Cabeceras HTTP para la API de Notion (para las funciones que usan ``requests``)."""
    return {
        'Authorization': 'Bearer ' + cfg.notion_token,
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }


def build_id_list(cfg):
    """Diccionario {nombre de BBDD de Notion: ID} tomado de la configuración."""
    return dict(cfg.notion_db_ids)


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
        raise NotImplementedError("process_type='time' no está implementado")
    else:
        raise ValueError(f"process_type incorrecto: {process_type!r} (use 'number', 'total' o 'time')")
    
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

def get_pages_by_status(NOTION_TOKEN, DATABASE_ID, path=None):
    """Lee de Notion las páginas pendientes de cargar (solo lectura).

    Devuelve las páginas cuya propiedad ``Status`` está vacía o tiene un valor distinto
    de ``Procesado`` (estados en ``config.NOTION_STATES_TO_READ``): los fallidos se reintentan.
    Maneja la paginación (más de 100 registros).

    Parameters
    ----------
    NOTION_TOKEN : str
        Token de la integración.
    DATABASE_ID : str
        ID de la BBDD de Notion.
    path : str, optional
        Si se indica, guarda la lista de páginas en ese JSON (copia local en Bronze).

    Returns
    -------
    dict
        ``{'results': [páginas]}``, la estructura que espera ``extract_data_from_json``.
    """
    notion = notion_client.Client(auth=NOTION_TOKEN)

    prop = cfg_module.NOTION_STATUS_PROPERTY
    kind = cfg_module.NOTION_STATUS_TYPE
    query_filter = {
        "or": [{"property": prop, kind: {"is_empty": True}}]
        + [{"property": prop, kind: {"equals": state}} for state in cfg_module.NOTION_STATES_TO_READ]
    }

    results = []
    has_more = True
    next_cursor = None
    while has_more:
        kwargs = {"database_id": DATABASE_ID, "filter": query_filter}
        if next_cursor:
            kwargs["start_cursor"] = next_cursor
        response = notion.databases.query(**kwargs)
        results.extend(response["results"])
        has_more = response["has_more"]
        next_cursor = response["next_cursor"]

    if path:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    logger.info("Notion: %d páginas por cargar", len(results))
    return {"results": results}

def extract_data_from_json(pages):
    """Summary: function to extract the data from the one database

    Args:
        pages (json): json database data

    Returns:
        (dataframe): dataframe with the data
    """
    resultados = []
    type_list = []

    # Acepta {'results': [...]} (respuesta de la API) o directamente la lista de páginas
    page_list = pages['results'] if isinstance(pages, dict) else pages

    for result in page_list:
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



# AUXILIARY FUNCTIONS - UPLOAD DATA IN NOTION
def update_pages_status(cfg, page_ids, state, dry_run=True):
    """Cambia la propiedad ``Status`` de las páginas a ``state``.

    Escribe en Notion, así que solo actúa si ``cfg.enable_external_writes`` es True
    y ``dry_run`` es False (Fase 9). Si no, solo informa en el log.
    Se moverá a ``sinks/notion_writer.py`` (N-23).
    """
    if dry_run or not cfg.enable_external_writes:
        logger.info("dry_run: pondría Status='%s' en %d páginas de Notion", state, len(page_ids))
        return
    notion = notion_client.Client(auth=cfg.notion_token)
    for p_id in page_ids:
        notion.pages.update(
            page_id=p_id,
            properties={cfg_module.NOTION_STATUS_PROPERTY: {cfg_module.NOTION_STATUS_TYPE: {"name": state}}}
        )
    logger.info("Actualizados %d estados en Notion a '%s'", len(page_ids), state)


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

def transform_notion_df(df, db_name):
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
    df = df[new_order].rename(columns=maps)

    # TRANSFORMATION OF COLUMNS SPECIFIC TO EACH DATAFRAME
    if db_name == 'MATERIALES_DB':
        # Transform range to int
        df['main_comp_percentage'] = df['main_comp_percentage'].apply(lambda row: transform_rages(row))
        # Remove the units and symbols
        df['thickness_nm'] = df['thickness_nm'].apply(lambda row: remove_symbol_nm(row))
        # Remove the units and symbols
        df['size_material_nm'] = df['size_material_nm'].apply(lambda row: remove_symbol_nm(row))

    elif db_name == 'GASES_DB':
        # Remove the units and symbols
        df['max_concentration_ppb'] = df['max_concentration_ppb'].apply(lambda row: remove_symbol_bottle(row))

    elif db_name == 'MEDIDAS_DB':
        # Remove the units and symbols
        df['humidity_percentage'] = df['humidity_percentage'].apply(lambda row: remove_symbol_humidity(row))
        # Sort the gas names
        df['label'] = df['label'].apply(lambda row: sort_gases_names(row))

    logger.info("%s: %d registros transformados", db_name, len(df))

    # Transform NaT, None, NaN to Unkown
    df = replace_nan_nat_none(df)

    return df


# PARSEAR LAS , POR . DEBIDO A QUE NOTION ESTÁ EN ESPAÑOL
def parse_notion_purity(value):
    # 1. Si el valor es nulo, devolvemos 0 o None
    if not value: return 0.0
    
    # 2. Convertimos a string y cambiamos comas por puntos por si acaso
    clean_val = str(value).replace(',', '.')
    
    # 3. Si detecta un rango (ej. "77.0-82.6")
    if '-' in clean_val:
        # Extraemos todos los números (floats) encontrados en la cadena
        numbers = [float(n) for n in re.findall(r"\d+\.\d+|\d+", clean_val)]
        return sum(numbers) / len(numbers) if numbers else 0.0
    
    # 4. Si es un número único
    try:
        return float(clean_val)
    except ValueError:
        return 0.0


# MAIN FUNCTION
def obtain_data_notion(cfg, dry_run=True):
    """Lee de Notion los registros pendientes de las 6 BBDD y los transforma.

    De momento solo en ``dry_run``: lee Notion (solo lectura) y transforma, pero no
    guarda en Bronze/Silver ni cambia ``Status``. La carga real se hace en la Fase 3.

    Parameters
    ----------
    cfg : config.Config
    dry_run : bool
        Debe ser True hasta la Fase 3.

    Returns
    -------
    dict
        ``{'records': {BBDD: nº de registros}, 'measurements': [MED-n, ...]}``
    """
    if not dry_run:
        raise NotImplementedError("La carga real de Notion se implementa en la Fase 3; usar dry_run=True.")

    records = {}
    new_measurements = []

    for db_name, database_id in build_id_list(cfg).items():
        pages = get_pages_by_status(cfg.notion_token, database_id)
        df_raw = extract_data_from_json(pages)

        if df_raw.empty:
            logger.info("Sin novedades en %s", db_name)
            records[db_name] = 0
            continue

        df = transform_notion_df(df_raw.copy(), db_name)
        records[db_name] = len(df)

        if db_name == 'MEDIDAS_DB':
            new_measurements = df['conn_measurement'].tolist()

    return {"records": records, "measurements": new_measurements}
