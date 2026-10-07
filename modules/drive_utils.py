# IMPORTS
import io
import os
import tempfile
import json
import re
from typing import Optional
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload, MediaFileUpload


# VARIABLES
READ_SCOPE = "https://www.googleapis.com/auth/drive.readonly"    # Solo lectura (desarrollo)
SCOPES = [READ_SCOPE]  # el alcance de escritura solo se activa en la Fase 9


# DRIVE FUNCTIONS
def get_drive():
    """Autenticación oficial de Google para Cuenta de Servicio."""
    
    # 1. Cargamos el JSON desde los secretos
    info = json.loads(st.secrets["drive"]["service_account_json"])
    
    # 2. Definimos los permisos (Scopes): solo lectura
    SCOPES = [READ_SCOPE]
    
    # 3. Creamos las credenciales
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    
    # 4. Construimos el servicio de Drive (v3 es la versión actual)
    service = build('drive', 'v3', credentials=creds)
    
    return service


def download_file_bytes(service, file_id: str) -> bytes:
    """Descarga un archivo por ID y devuelve bytes."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return fh.getvalue()


def upload_bytes_to_folder(service, folder_id, file_name, content_bytes):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(
        io.BytesIO(content_bytes), 
        mimetype='application/octet-stream', 
        resumable=True
    )
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


# AUXILIARY FUNCTIONS
@st.cache_resource(show_spinner=False)
def list_folder(_drive, folder_id: str):
    """Lista TODOS los archivos de una carpeta manejando la paginación."""
    items = []
    page_token = None
    
    while True:
        query = f"'{folder_id}' in parents and trashed = false"
        
        # Llamamos a la API incluyendo el pageToken
        results = _drive.files().list(
            q=query,
            fields="nextPageToken, files(id, name)",
            pageSize=1000,  # Aumentamos el tamaño de página (máx 1000)
            pageToken=page_token
        ).execute()
        
        # Añadimos los archivos encontrados a nuestra lista global
        items.extend(results.get('files', []))
        
        # Verificamos si hay más páginas
        page_token = results.get('nextPageToken')
        
        # Si no hay más tokens, salimos del bucle
        if not page_token:
            break
            
    return items


def list_metano():
    drive = get_drive()
    metano_id = st.secrets["folders"]["metano"]

    items = list_folder(drive, metano_id)

    st.write(f"Archivos en metano_line: {len(items)}")
    for f in items:
        st.write({
            "title": f.get("title"),
            "id": f.get("id"),
            "mimeType": f.get("mimeType"),
            "createdDate": f.get("createdDate"),
            "modifiedDate": f.get("modifiedDate"),
        })


def extraer_experiment_id(file_name):
    # Busca la palabra MED seguida de un guion y varios números
    match = re.search(r'(MED-\d+)', file_name)
    if match:
        return match.group(1) # Devuelve "MED-228"
    return None


def es_tdms_time_relevante(title: str) -> bool:
    if not title:
        return False
    t = title.lower()

    # 1. Debe ser .tdms
    # 2. Debe contener "time"
    # 3. NO debe ser un archivo de índice
    # 4. NO debe contener la palabra "respuesta" (aunque generalmente es Respuestas, respuesta siempre funcionará porque utiliza la raiz de la palabra independientemente del plural o letras en minúscula/mayúscula)
    return (
        t.endswith(".tdms") and 
        "time" in t and 
        not t.endswith(".tdms_index") and
        "respuesta" not in t
    )


def upload_df_to_drive_as_parquet(service, df, file_name, folder_id):
    """
    Sube un DataFrame a Google Drive en formato Parquet.
    service: El objeto construido con googleapiclient.discovery.build
    folder_id: El ID de la carpeta de destino (ej. la carpeta con la fecha)
    """
    # 1. Convertir el DataFrame a un archivo Parquet en memoria (BytesIO)
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0) # Volver al inicio del archivo virtual

    # 2. Configurar los metadatos del archivo en Drive
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # 3. Preparar el medio de subida
    media = MediaIoBaseUpload(parquet_buffer, 
                              mimetype='application/octet-stream', 
                              resumable=True)

    # 4. Ejecutar la subida
    file = service.files().create(body=file_metadata, 
                                  media_body=media, 
                                  fields='id').execute()
    
    return file.get('id')


# FUNCIÓN TEST DRIVE
def test_drive():
    # Con esta función solo probamos la conexión y listamos archivos TDMS relevantes
    drive = get_drive()
    metano_id = st.secrets["folders"]["metano_line"]

    items = list_folder(drive, metano_id)

    tdms_relevantes = [
        f for f in items
        if es_tdms_time_relevante(f.get("name", ""))
    ]

    st.write(f"TDMS relevantes: {len(tdms_relevantes)}")
    for f in tdms_relevantes:
        st.write(f["name"])