# IMPORTS
import os
import tempfile
import json
from typing import Optional
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


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
def get_drive() -> GoogleDrive:
    """Autenticación con Cuenta de Servicio. Lee JSON desde st.secrets."""

    # 1. Cargamos el JSON de los secretos
    service_account_info = json.loads(st.secrets["drive"]["service_account_json"])

    # 2. Configuración de forma manual
    settings = {
        "client_config_backend": "settings",
        "service_config": {
            "client_json_dict": service_account_info,
            "scope": SCOPES  # <--- Añadimos el scope aquí
        }
    }

    # 3. PASAR LAS SETTINGS AQUÍ para evitar que busque el archivo settings.yaml
    gauth = GoogleAuth(settings=settings)

    # 4. Autenticamos
    gauth.service_account_auth()
    
    return GoogleDrive(gauth)

def download_file_bytes(drive: GoogleDrive, file_id: str) -> bytes:
    """Descarga un archivo por ID y devuelve bytes."""
    f = drive.CreateFile({"id": file_id})
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
    try:
        f.GetContentFile(tmp_path)
        with open(tmp_path, "rb") as fh:
            return fh.read()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

def upload_bytes_to_folder(
    drive: GoogleDrive,
    data: bytes,
    filename: str,
    folder_id: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> str:
    """Sube bytes a una carpeta de Drive. Devuelve el file_id."""
    meta = {"title": filename}
    if folder_id:
        meta["parents"] = [{"id": folder_id}]
    if mime_type:
        meta["mimeType"] = mime_type

    f = drive.CreateFile(meta)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(data)
    try:
        f.SetContentFile(tmp_path)
        f.Upload()
        return f["id"]
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass