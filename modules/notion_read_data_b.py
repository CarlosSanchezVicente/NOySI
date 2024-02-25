# IMPORTS
import pandas as pd
import requests
from dotenv import dotenv_values
from datetime import datetime
import json
import notion_client

# IMPORT FUNCTIONS FROM MODULES
from modules import notion_trans_s as transform_notion

# SOURCES
# API Notion: https://www.notion.so/es-la/help/create-integrations-with-the-notion-api
#             https://www.youtube.com/watch?v=M1gu9MDucMA
#             https://developers.notion.com/reference/authentication
#             https://www.python-engineer.com/posts/notion-api-python/



# DEFINITIONS
config = dotenv_values('.env')
NOTION_TOKEN = config.get('NOTION_TOKEN')   # NOTION_TOKEN
MATERIALES_DB_ID = config['MATERIALES_DB_ID']   # MATERIALES_DB_ID
DISOLUCIONES_DB_ID = config['DISOLUCIONES_DB_ID']   # DISOLUCIONES_DB_ID
SENSORES_DB_ID = config['SENSORES_DB_ID']   # SENSORES_DB_ID
LED_DB_ID = config['LED_DB_ID']   # LED_DB_ID
GASES_DB_ID = config['GASES_DB_ID']   # GASES_DB_ID
MEDIDAS_DB_ID = config['MEDIDAS_DB_ID']   # MEDIDAS_DB_ID
ID_list = [MATERIALES_DB_ID, DISOLUCIONES_DB_ID, SENSORES_DB_ID, LED_DB_ID, GASES_DB_ID, MEDIDAS_DB_ID]

headers = {
    'Authorization': 'Bearer ' + NOTION_TOKEN,
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}



# AUXILIARY FUNCTIONS
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
    data = response.json()
    with open (path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
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
                content = multi_select_list[0]['name'] if multi_select_list else None #'NS'
                result_dict[key] = content
                
            # If the type of field is a 'relation'.
            elif type == 'relation':
                # Obtain the different elements that are found within the list, because the value of this type of key is a list
                # with a dictionary inside de list.
                relation_list = properties[key].get('relation', [])

                # Extract 'content' from 'text' if it exists. With this loop it's possible to move through the list.
                content = relation_list[0]['id'] if relation_list else None #'NS'
                result_dict[key] = content

        resultados.append(result_dict)
    
    return pd.DataFrame(resultados)



# MAIN FUNCTIONS
def obtain_data_notion(process_type, ID_list, date='2024-01-01', pages_number=100):
    """Summary: function to obtain the pages of the databases or from last update('process_type' indicates the behavior). 

    Args:
        process_type (string): it indicates the behavior of the ingestion. 
            - 'process_type'=number -> download all pages indicated in pages_number. 
            - 'process_type'=time -> download all pages from last update. 
        date (string, optional): date from which the information will be extracted from the database. The format of date would be: 
            YYYY-MM-DD. Defaults to 100. Defaults to None.
        pages_number (integer, optional): number of pages to download. Defaults to 100.

    Returns:
        pages (json): data from Notion
    """
    for db_name in ID_list:
        # Create the name to store the data
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{db_name}_{current_date}"
        
        # Obtain and store the data from Notion database
        # Create the path
        path = f"G:\Mi unidad\Bronze\{file_name}.json"

        # Create database ID
        id_name = f'{db_name}_ID'
        exec(f'DATABASE_ID = config["{id_name}"]')

        # If the user want to obtain a specific numbers of pages
        if process_type == 'number' or process_type == 'total':
            if pages_number == 100:
                pages = get_pages_100(headers, DATABASE_ID, 100, process_type, path)
            else:
                pages = get_pages_more_100(headers, DATABASE_ID, path, pages_number=None)
        # If the user want to obtain the pages from specific date
        elif process_type == 'time':
            get_pages_select_date(NOTION_TOKEN, DATABASE_ID, path, date)
        else:
            return print('Error: You have entered an incorrect value for the data entry type. \nYou have to introduce: "number" or "total"')

        # Obtain a dataframe from json
        df = extract_data_from_json(pages)
        print(df)
        # transform_notion_table()
    