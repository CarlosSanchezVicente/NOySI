# IMPORTS
import io
import json
import logging
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

logger = logging.getLogger(__name__)

# Campos de Drive v3 que se piden al listar (solo metadatos, sin descargar).
LIST_FIELDS = "nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, md5Checksum, size)"


# DRIVE FUNCTIONS
def get_drive(cfg):
    """Autenticación de Google para cuenta de servicio.

    Los permisos (scopes) vienen de ``cfg.drive_scopes``: solo lectura salvo que
    ``ENABLE_EXTERNAL_WRITES`` esté activo (Fase 9).
    """
    info = json.loads(cfg.drive_service_account_json)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=list(cfg.drive_scopes)
    )
    return build('drive', 'v3', credentials=creds)


def download_file_bytes(service, file_id: str) -> bytes:
    """Descarga un archivo por ID y devuelve bytes."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    return fh.getvalue()


def upload_bytes_to_folder(service, folder_id, file_name, content_bytes):
    """Sube bytes a una carpeta de Drive. Requiere permiso de escritura (Fase 9)."""
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaIoBaseUpload(
        io.BytesIO(content_bytes),
        mimetype='application/octet-stream',
        resumable=True
    )
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def upload_df_to_drive_as_parquet(service, df, file_name, folder_id):
    """Sube un DataFrame a Drive en formato Parquet. Requiere permiso de escritura (Fase 9).

    Parameters
    ----------
    service : objeto construido con ``get_drive``.
    folder_id : ID de la carpeta de destino.
    """
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    return upload_bytes_to_folder(service, folder_id, file_name, parquet_buffer.getvalue())


# AUXILIARY FUNCTIONS
def list_folder(drive, folder_id: str):
    """Lista TODOS los archivos de una carpeta (con paginación): solo metadatos."""
    items = []
    page_token = None

    while True:
        results = drive.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields=LIST_FIELDS,
            pageSize=1000,
            pageToken=page_token,
        ).execute()
        items.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    logger.info("Carpeta %s: %d archivos", folder_id, len(items))
    return items


def extraer_experiment_id(file_name):
    """Devuelve el ``MED-<número>`` del nombre de archivo, o None si no lo tiene."""
    match = re.search(r'(MED-\d+)', file_name)
    if match:
        return match.group(1)
    return None


def es_tdms_time_relevante(title: str) -> bool:
    """True si es un .tdms de datos: contiene "time", no es índice ni archivo de "Respuestas"."""
    if not title:
        return False
    t = title.lower()
    return (
        t.endswith(".tdms") and
        "time" in t and
        not t.endswith(".tdms_index") and
        "respuesta" not in t
    )
