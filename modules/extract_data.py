# IMPORTS
import io
import os
import re
import time
import pandas as pd
from datetime import datetime, timezone
import json
import tempfile
from typing import List, Tuple, Optional
from nptdms import TdmsFile
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


# IMPORT FUNCTIONS FROM MODULES
from modules.drive_utils import (
    get_drive, download_file_bytes, upload_bytes_to_folder, es_tdms_time_relevante
)
from modules.notion_utils import obtain_data_notion


# FUNCIONAMIENTO DRIVE CONN + INGESTA
"""
run_ingestion()
│
├── list_folder()             ← SOLO lista metadatos
│
├── es_tdms_time_relevante()  ← FILTRA
│
├── process_one_tdms_file()   ← AQUÍ se leen los archivos
│       ├── download_file_bytes()
│       ├── read_tdms_to_df()  ✅ AQUÍ se hace la lectura TDMS REAL
│       ├── clean_and_extract()
│       └── upload_bytes_to_folder()
│
└── actualización del manifest
"""

# VARIABLES



# AUXILIARY FUNCTIONS - LEVEL 2 
def clean_and_extract(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    TU lógica de limpieza:
    - parsing de columnas
    - filtrado NaN
    - recorte de ventanas
    - normalización de unidades, etc.
    """
    # Ejemplo trivial: quitar columnas vacías y duplicados
    df = df_raw.dropna(how="all").drop_duplicates()
    return df


def process_one_tdms_file(drive, file_meta, bronze_folder_id):
    file_id = file_meta["id"]
    title = file_meta["title"]
    created = file_meta.get("createdDate")
    md5 = file_meta.get("md5Checksum")

    raw_bytes = download_file_bytes(drive, file_id)

    df_raw = read_tdms_to_df(raw_bytes)
    df_clean = clean_and_extract(df_raw)

    buf = io.BytesIO()
    df_clean.to_parquet(buf, index=False)
    buf.seek(0)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bronze_title = f"{title}_clean_{ts}.parquet"

    bronze_file_id = upload_bytes_to_folder(
        drive,
        buf.getvalue(),
        bronze_title,
        bronze_folder_id,
        mime_type="application/octet-stream"
    )

    return {
        "file_id": file_id,
        "raw_title": title,
        "createdDate": created,
        "md5Checksum": md5,
        "bronze_file_id": bronze_file_id,
        "bronze_title": bronze_title,
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
    }






# MAIN FUNCTION
import io
from nptdms import TdmsFile
import pandas as pd
# Importas tus funciones de conexión a Postgres y Notion
# from database import engine, update_notion_status

def run_data_pipeline():
    drive = get_drive()
    # IDs de carpetas desde tus secretos
    folder_bronce_id = st.secrets["folders"]["bronce_parquet"]
    folder_procesados_id = st.secrets["folders"]["procesados_tdms"]
    
    # 1. CARGA MASIVA DE NOTION (Para eficiencia)
    # Supongamos que esta función devuelve un DF con 'experiment_id' como índice
    df_notion_all = obtain_data_notion(process_type, date, pages_number=100) 

    items = list_folder(drive, st.secrets["folders"]["metano_line"])
    tdms_relevantes = [f for f in items if es_tdms_time_relevante(f.get("name", ""))]

    for f in tdms_relevantes:
        try:
            file_id = f["id"]
            file_name = f["name"]
            experiment_id = extraer_experiment_id(file_name) # Tu función regex

            # --- PASO 1: DESCARGA Y LECTURA (RAM) ---
            df_raw = descargar_y_leer_tdms(drive, file_id) # La función que hablamos antes

            # --- PASO 2: OBTENER METADATOS ESPECÍFICOS ---
            # Filtramos los datos de Notion para este experimento
            df_metadatos = df_notion_all[df_notion_all['experiment_id'] == experiment_id]

            if df_metadatos.empty:
                st.warning(f"⚠️ Saltando {experiment_id}: No existe en Notion.")
                continue

            # --- PASO 3: GUARDAR BACKUPS EN DRIVE (CAPA BRONCE) ---
            # Guardamos el sensor en Parquet
            guardar_dataframe_en_drive(drive, df_raw, f"{experiment_id}_sensor.parquet", folder_bronce_id)
            # Guardamos el snapshot de Notion en Parquet
            guardar_dataframe_en_drive(drive, df_metadatos, f"{experiment_id}_notion.parquet", folder_bronce_id)

            # --- PASO 4: CARGA A POSTGRESQL (PLATA) ---
            # Unimos metadatos y sensor en un solo DF para la tabla Silver
            df_plata = df_raw.copy()
            for col in df_metadatos.columns:
                df_plata[col] = df_metadatos[col].iloc[0]

            df_plata.to_sql('lecturas_sensores', engine, schema='silver', if_exists='append', index=False)

            # --- PASO 5: LIMPIEZA FINAL ---
            mover_archivo_a_procesados(drive, file_id, folder_procesados_id)
            
            st.success(f"✅ Procesado e integrados backups para {experiment_id}")

        except Exception as e:
            st.error(f"❌ Error procesando {f['name']}: {str(e)}")