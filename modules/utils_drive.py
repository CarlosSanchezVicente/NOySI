# IMPORTS
import io
import os
import tempfile
import json
from typing import Optional
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


# VARIABLES
# Usa el scope mínimo necesario. Para lectura y escritura, mejor drive.file o drive.
# - readonly: solo lectura
# - drive.file: leer y escribir archivos creados/abiertos por la app
# - drive: acceso completo al Drive al que tenga permisos
READ_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
WRITE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FULL_SCOPE = "https://www.googleapis.com/auth/drive"

# Elige el alcance que necesitas:
SCOPES = [FULL_SCOPE]  # o [READ_SCOPE] si solo vas a leer


# FUNCIONES DRIVE
def get_drive():
    """Autenticación oficial de Google para Cuenta de Servicio."""
    
    # 1. Cargamos el JSON desde los secretos
    info = json.loads(st.secrets["drive"]["service_account_json"])
    
    # 2. Definimos los permisos (Scopes)
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
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