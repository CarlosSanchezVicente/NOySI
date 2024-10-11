# IMPORTS LIBRARIES
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import hmac
import os
import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# IMPORT FUNCTIONS FROM MODULES
from modules import notion_read_transform as notion
from modules import electrical_read_transform as elecr
from modules import electrical_processing as elecp
from modules import optical_read_transform as op


# DEFINITION
# General
main_page = "main.py"
#config = dotenv_values('.env')

# Electrical measurement
#path_electrical_methane_line = config['path_electrical_methane_line']
#path_optical_methane_line = config['path_optical_methane_line']
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


# AUTHENTICATION
def add_logo():
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="margin: 0;">NoySI</h1>
            <div style="display: flex; gap: 10px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6d/Logotipo_del_CSIC.svg" width="100" alt="Logo_csic">
                <img src="https://www.itefi.csic.es/sites/default/files/logos/LOGO-ITEFI-color.svg" width="100" alt="Logo_itefi">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('##')   # Add blanck space between two streamlit components
    #st.logo('./img/csic_logo.png', size="small")

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct. The compare_digest function is used as a security layer against timing 
        attacks, so that the comparison between passwords always has the same duration."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        st.session_state['authentication_status'] = True
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

def authenticate_google_drive():
    gauth = GoogleAuth()

    # Configuración de credenciales usando st.secrets
    gauth.settings['client_config_backend'] = 'settings'
    gauth.settings['client_config'] = st.secrets["drive"]

    # Iniciar autenticación mediante el servidor web local
    gauth.LocalWebserverAuth()  # Autenticar con Google

    # Crear una instancia de Google Drive
    drive = GoogleDrive(gauth)
    
    # Probar si la conexión es exitosa listando los archivos en la raíz de Google Drive
    try:
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        if file_list:
            st.success("Conexión con Google Drive realizada correctamente.")
            st.write("Archivos en tu Google Drive:")
            for file in file_list:
                st.write(f" - {file['title']}")
        else:
            st.info("La conexión es exitosa, pero no se encontraron archivos en Google Drive.")
    except Exception as e:
        st.error("Error al conectar con Google Drive.")
        st.error(e)

def obtain_page_names():
    # Ruta a la carpeta 'pages'
    pages_folder = os.path.join(os.getcwd(), 'pages')

    # Obtener los nombres de los archivos
    page_names = os.listdir(pages_folder)
    #page_names.insert(0, main_page)
        
    return page_names


# MAIN FUNCTION
def main():
    # STREAMLIT CODE
    # Config streamlit page
    st.set_page_config(
        page_title='Home',
        page_icon='🏠')
    add_logo()
    st.logo('./img/NoySI.png', size="medium")

    # Inicializate 'authentication_status' variable
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False  # O False si prefieres que inicie en no autenticado
    
    # User authentication
    if not check_password():
        st.stop()

    st.text('Carga_correcta_4')
    dict_drive = dict(st.secrets["drive"])
    st.text(type(dict_drive))
    st.text(dict_drive.keys())

    # Drive authentication
    authenticate_google_drive()

    # Add another elements
    st.sidebar.success('Select a page')
    st.warning('Check that all measurements have been completed before proceeding. \n \
            If they are not finished it could cause problems in data ingestion.', icon="⚠️")


    # EXRACT DATA FROM ROW AND CLEAN IT: ROW -> BRONZE -> SILVER -> GOLD
    # With this function Obtain data from notion, store the jsons and files in the bronze level, clean the data and store it in the 
    # silver level. In the end, the calculation will be store in gold database.
        

    # GENERAL CONFIGURATION
    # Ingestion type: process_type = 'total' (total pages) / 'time' (pages from specific date)/ 'number' (specific pages number). 
    if st.button('Click to add the unprocessed data', type='primary'):
        # NOTION
        #notion.obtain_data_notion(config, headers, 'last_upload', '2024-01-01')   

        # ELECTRICAL MEASUREMENT
        #electrical_data_silver = elecr.obtain_data_electrical_m('time', ID_dict_elec, 'MethaneLine', path_electrical_methane_line)
        # Source data: source = 'database' / 'calculated_data'
        #elecp.electrical_data_transform('time', 'calculated_data', electrical_data_silver)

        # OPTICAL MEASUREMENT
        #op.read_transform_optical('time', 'MethaneLine', path_optical_methane_line)
        pass
        


# MAIN EXECUTION
if __name__ == '__main__':
    result = main()