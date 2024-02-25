# IMPORTS
import pandas as pd
import statistics


# DEFINITIONS
ID_list = ['MATERIALES_DB', 'DISOLUCIONES_DB', 'SENSORES_DB', 'LED_DB', 'GASES_DB', 'MEDIDAS_DB']

# Materials table 
MATERIALES_DB_new_order =  ['id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 'Fabricante', 'Tipo', 'created_by', 
                            'last_edited_by', 'created_time', 'last_edited_time', 'Preparación', 'Otros compuestos', '% N', 
                            '% H', '% O', '% Compuesto Princ.', 'BET (m2/g)', 'Espesor', 'Tamaño', 'Proporción']

MATERIALES_DB_map  =   {'ID': 'ID',
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
                        '%N': 'n_percentage', 
                        '%H': 'h_percentage',
                        '%O': 'o_percentage',
                        '% Compuesto Princ.': 'main_comp_percentage', 
                        'BET_(m2/g)': 'bet_m2_g',
                        'Espesor':'thickness_nm', 
                        'Tamaño': 'size_material_nm', 
                        'Proporción': 'ratio'}

# Solutions table
DISOLUCIONES_DB_new_order = ['id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 'created_by', 'last_edited_by', 
                             'created_time', 'last_edited_time', 'Preparación', 'Concentración', 'Disolvente', 'Soluto', 
                             'Dopante', 'Sensor']

DISOLUCIONES_DB_map =  {'ID': 'ID',
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

# Sensors table
SENSORES_DB_new_order = ['id', 'Título', 'Etiquetas', 'parent', 'url', 'Realizado', 'Tipo', 'created_by', 'last_edited_by', 
                         'created_time', 'last_edited_time', 'Preparación', 'Método dep.', 'Membrana 1', 'Membrana 2', 
                         'Membrana 3', 'Membrana 1', 'Disol. empleadas', 'Parámetros dep.']

SENSORES_DB_map =  {'ID': 'ID', 
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
                    'Preparación': 'preparation_date',
                    'Método dep.': 'deposition_method', 
                    'Membrana 1': 'susbtrate_1', 
                    'Membrana 2': 'susbtrate_2', 
                    'Membrana 3': 'susbtrate_3', 
                    'Membrana 4': 'susbtrate_4', 
                    'Disol. empleadas': 'solutions_used', 
                    'Parámetros dep.': 'deposition_parameters'}

# Leds table 
LED_DB_new_order = ['id', 'Título', 'Etiquetas', 'parent', 'url', 'created_by', 'last_edited_by', 'created_time', 
                    'last_edited_time', 'Preparación', 'V/A utilizado', 'V/A utilizado', 'Voltaje', 'Corriente', 
                    'Long. onda', 'Potencia Óptica', 'Comentarios']

LED_DB_maps =  {'ID': 'ID',
                'id': 'id_led',
                'Título': 'name_led',
                'Etiquetas': 'label',
                'parent': 'parent',
                'url': 'url',
                'created_by': 'record_created_by',
                'last_edited_by': 'record_last_edited_by',
                'created_time': 'record_created_time',
                'last_edited_time': 'record_last_edited_time',
                'V/A utilizado': 'voltage_V_used',
                'V/A utilizado': 'current_mA_used',
                'Voltaje': 'voltage_range',
                'Corriente': 'current_range',
                'Long. onda': 'wavelength_nm',
                'Potencia Óptica': 'optical_power_mW',
                'Comentarios': 'comments'}

# Gases table
GASES_DB_new_order = ['id', 'Título', 'Etiquetas', 'parent', 'url', 'created_by', 'last_edited_by', 'created_time', 
                      'last_edited_time', 'Max. Concetración']

GASES_DB_maps = {'ID': 'ID', 
                 'id': 'id_gas',
	             'Título': 'name_gas',
	             'Etiquetas': 'label',
	             'parent': 'parent',
	             'url': 'url',
	             'created_by': 'record_created_by',
	             'last_edited_by': 'record_last_edited_by',
                 'created_time': 'record_created_time',
	             'last_edited_time': 'record_last_edited_time',
	             'Max. Concetración': 'max_concentration'}

# Medidas table
MEDIDAS_DB_new_order = ['id', 'Título', 'Gas', 'parent', 'url', 'Realizado', 'created_by', 'last_edited_by', 'created_time', 
                        'last_edited_time', 'Concentraciones', 'Humedad', 'Equipo medida', 'Resultado', 'Línea', 'Sensor', 
                        'Led', 'Gases']

MEDIDAS_DB_maps =  {'ID': 'ID',
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
                    'Concentraciones': 'concetrations_ppb',
                    'Humedad': 'humidity_percentage',
                    'Equipo medida': 'measurement_equipment',
                    'Resultado': 'result_measurement',
                    'Línea': 'gases_line_used',
                    'Sensor': 'id_sensor',
                    'Led': 'id_led',
                    'Gases': 'id_gases'}


# AUXILIARY FUNCTIONS
def transform_rages(str):
    """Summary: function to transform the string with number o range in a integer.

    Args:
        str (string): string with number or range.

    Returns:
        (integer): number or range number mean.
    """
    # If the string includes '-' means that there is a range. If it doesn't include '-', there is a number.
    if '-' in str:
        str2 = str.split(' - ')
        return statistics.mean(int(str2[0]), int(str2[1]))   # Return the mean of both numbers
    else:
        return int(str)


def remove_symbol(str):
    """Summary: function to remove the unit or diferent symbols.

    Args:
        str (string): string with unit or symbols.

    Returns:
        (integer): number without symbols or unit.
    """
    str2 = str.split(' ')
    if len(str2)>2:
        return int(str2[1])
    else:
        return int(str2[0])
    
def obtain_votage_current(str, type):   # Data structure: 5.57 V / 36 mA
    str2 = str.plit(' / ')
    if type == 'voltage':
        str3 = str2[0].plit(' ')
        return float(str3[0])
    elif type == 'current':
        str3 = str2[1].plit(' ')
        return float(str3[0])
    

def sort_gases_names(str):
    pass
    


# MAIN FUNCTIONS
def transform_notion_table(ID, df):
    # Obtain the name of table to transform
    name_db = ID.split('_')
    df['Date']= pd.to_datetime(df['Date'])

    # Create column ID
    df.reset_index(inplace=True).rename(columns={df.index.name:'ID'})   # Create ID column
    # Create variable name of new order and map 
    new_order = ID + '_new_order'
    maps = ID + '_maps'
    # Change the column names such as the database
    exec(f'df = df[{new_order}]')
    exec(f'df.rename(columns={maps})')

    # Transform columns common in all tables
    df['created_time']= pd.to_datetime(df['created_time'])
    df['last_edited_time']= pd.to_datetime(df['last_edited_time'])

    # Transform the table in each case
    if name_db[0] == 'MATERIALES':
        df['preparation_date'] = pd.to_datetime(df['preparation_date'])   # Transform string to datetime
        df['n_percentage'] = df['n_percentage', 'h_percentage'].astype(float)   # Transform int to float
        df['main_comp_percentage'] = df['main_comp_percentage'].apply(lambda row: transform_rages(row))   # Transform range to int
        df['thickness_nm'] = df['thickness_nm'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols
        df['size_material_nm'] = df['size_material_nm'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols

    elif name_db[0] == 'DISOLUCIONES':
        df['preparation_date'] = pd.to_datetime(df['preparation_date'])   # Transform string to datetime

    elif name_db[0] == 'SENSORES':
        df['preparation_date'] = pd.to_datetime(df['preparation_date'])   # Transform string to datetime   

    elif name_db[0] == 'LED_DB':
        df['voltage_V_used'] = df['voltage_V_used'].apply(lambda row: obtain_votage_current(row, 'voltage'))   # Obtain voltage value
        df['current_mA_used'] = df['current_mA_used'].apply(lambda row: obtain_votage_current(row, 'current'))   # Obtain current value
        df['wavelength_nm'] = df['wavelength_nm'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols
        df['optical_power_mW'] = df['optical_power_mW'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols

    elif name_db[0] == 'GASES':
        df['max_concentration'] = df['max_concentration'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols

    elif name_db[0] == 'MEDIDAS':
        df['humidity_percentage'] = df['humidity_percentage'].apply(lambda row: remove_symbol(row))   # Remove the units and symbols
