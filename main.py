# IMPORTS LIBRARIES
import streamlit as st
from dotenv import dotenv_values 

# IMPORT FUNCTIONS FROM MODULES
#from modules import notion_read_transform as notion
#from modules import electrical_read_transform as elecr
#from modules import electrical_processing as elecp
#from modules import optical_read_transform as op


# DEFINITION
# General
#config = dotenv_values('.env')
# Notion

# Electrical measurement
#path_methane_line = config['path_methane_line']
ID_dict_elec = {'MethaneLine':{'db_name': 'data_methane_line',

                          'DB_new_order':['ID','file_title', 'load_ts', 'time_s', 'sensor1_ohm', 'sensor2_ohm', 
                                          'sensor3_ohm', 'sensor4_ohm', 'bottle1_ppb', 'bottle2_ppb', 'bottle3_ppb',
                                          'date_timestamp', 'temperature_C', 'sensor1_heat_mV', 'sensor2_heat_mV', 
                                          'sensor3_heat_mV', 'sensor4_heat_mV', 'sensor1_heat_mA', 'sensor2_heat_mA',
                                          'sensor3_heat_mA', 'sensor4_heat_mA', 'sensor1_heat_C', 'sensor2_heat_C',
                                          'sensor3_heat_C', 'sensor4_heat_C', 'c1_flow_ml_min', 'c2_flow_ml_min', 
                                          'c3_flow_ml_min', 'c4_flow_ml_min', 'c5_flow_ml_min', 'c6_flow_ml_min',
                                          'polarization_voltage_V', 'humidity_percentage', 'comments'],
                          
                          
                          'DB_map':{'index': 'ID',
                                    'Time [s]': 'time_s',
                                    'R1 [ohm]': 'sensor1_ohm',
                                    'R2 [ohm]': 'sensor2_ohm',
                                    'R3 [ohm]': 'sensor3_ohm',
                                    'R4 [ohm]': 'sensor4_ohm',
                                    #'[Botella 1-Nada] [ppbv]': 'bottle1_ppb',
                                    #'[Botella 2-CO2] [ppbv]': 'bottle2_ppb',
                                    #'[Botella 3-Nada] [ppbv]': 'bottle3_ppb',
                                    'Time Stamp': 'date_timestamp',
                                    'Temperature [ºC]': 'temperature_C',
                                    'V Heating R1 [mV]': 'sensor1_heat_mV',
                                    'V Heating R2 [mV]': 'sensor2_heat_mV',
                                    'V Heating R3 [mV]': 'sensor3_heat_mV',
                                    'V Heating R4 [mV]': 'sensor4_heat_mV',
                                    'I Heating R1 [mA]': 'sensor1_heat_mA',
                                    'I Heating R2 [mA]': 'sensor2_heat_mA',
                                    'I Heating R3 [mA]': 'sensor3_heat_mA',
                                    'I Heating R4 [mA]': 'sensor4_heat_mA',
                                    'T Heating R1 [ºC]': 'sensor1_heat_C',
                                    'T Heating R2 [ºC]': 'sensor2_heat_C',
                                    'T Heating R3 [ºC]': 'sensor3_heat_C',
                                    'T Heating R4 [ºC]': 'sensor4_heat_C',
                                    'C1 Flow [ml/min]': 'c1_flow_ml_min',
                                    'C2 Flow [ml/min]': 'c2_flow_ml_min',
                                    'C3 Flow [ml/min]': 'c3_flow_ml_min',
                                    'C4 Flow [ml/min]': 'c4_flow_ml_min',
                                    'C5 Flow [ml/min]': 'c5_flow_ml_min',
                                    'Nada': 'c6_flow_ml_min',
                                    'Voltaje Polarización [V]': 'polarization_voltage_V',
                                    'HR': 'humidity_percentage',
                                    'Untitled': 'comments'}
                        }
          }


# MAIN FUNCTION
def main():
    # EXRACT DATA FROM ROW AND CLEAN IT: ROW -> BRONZE -> SILVER
    
    # NOTION: With this function Obtain data from notion, store the json in the bronze level, clean the data and store it in the 
    # silver level
    # Ingestion type: process_type = 'total' (total pages) / 'time' (pages from specific date)/ 'number' (specific pages number). 
    # Defaults to: date='2024-01-01', pages_number=100
    #notion.obtain_data_notion('total')

    # ELECTRICAL MEASUREMENT
    #elecr.obtain_data_electrical_m('total', ID_dict_elec, 'MethaneLine', path_methane_line)
    #elecp.electrical_data_transform(df, sensor_name)

    # OPTICAL MEASUREMENT
    #op.read_transform_optical()

    # STREAMLIT CODE
    st.set_page_config(
        page_title='Home',
        page_icon='🏠'
    )

    st.title("Main Page - NOySI Lab")
    st.sidebar.success('Select a page')



# MAIN EXECUTION
if __name__ == '__main__':

    result = main()
    print(result)