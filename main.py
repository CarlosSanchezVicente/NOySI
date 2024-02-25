# IMPORTS LIBRARIES
import pandas as pd

# IMPORT FUNCTIONS FROM MODULES
from modules import notion_read_data_b as rn
from modules import read_directory as rd
from modules import electrical_measurement as elecm


# DEFINITION
ID_list = ['MATERIALES_DB', 'DISOLUCIONES_DB', 'SENSORES_DB', 'LED_DB', 'GASES_DB', 'MEDIDAS_DB']


# MAIN FUNCTION
def main():
    # EXRACT DATA FROM ROW AND CLEAN IT: ROW -> BRONZE -> SILVER
    # With this function Obtain data from notion, store the json in the bronze level, clean the data and store it in the silver level
    # Ingestion type: process_type = 'total' (total pages) / 'time' (pages from specific date)/ 'number' (specific pages number). 
    # Defaults to: date='2024-01-01', pages_number=100
    rn.obtain_data_notion('total', ID_list)


# MAIN EXECUTION
if __name__ == '__main__':
    result = main()
    print(result)