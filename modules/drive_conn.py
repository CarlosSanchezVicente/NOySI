# IMPORTS
import io
import os
import time
import pandas as pd
from datetime import datetime, timezone
import json
import tempfile
from typing import List, Tuple, Optional
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from utils_drive import (
    get_drive, list_folder, download_file_bytes, upload_bytes_to_folder
)


# Usa el scope mínimo necesario. Para lectura y escritura, mejor drive.file o drive.
# - readonly: solo lectura
# - drive.file: leer y escribir archivos creados/abiertos por la app
# - drive: acceso completo al Drive al que tenga permisos
READ_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
WRITE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FULL_SCOPE = "https://www.googleapis.com/auth/drive"

# Elige el alcance que necesitas:
SCOPES = [FULL_SCOPE]  # o [READ_SCOPE] si solo vas a leer


@st.cache_resource(show_spinner=False)

def get_drive() -> GoogleDrive:
    """Autenticación con Cuenta de Servicio. Lee JSON desde st.secrets."""
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = {
        "client_json": json.loads(st.secrets["drive"]["service_account_json"]),
        "scope": SCOPES,
    }
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

def list_folder(drive: GoogleDrive, folder_id: str):
    """Retorna la lista de items (diccionarios v2) dentro de la carpeta."""
    q = f"'{folder_id}' in parents and trashed=false"
    # Puedes añadir orderBy si quieres: {"q": q, "orderBy": "createdDate desc"}
    return drive.ListFile({"q": q}).GetList()

def list_folder_simple(drive: GoogleDrive, folder_id: str) -> List[Tuple[str, str, str]]:
    """Lista simplificada: (title, id, mimeType)."""
    items = list_folder(drive, folder_id)
    return [(f.get("title"), f.get("id"), f.get("mimeType")) for f in items]

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

def create_folder(drive: GoogleDrive, name: str, parent_folder_id: Optional[str] = None) -> str:
    """Crea una carpeta y devuelve su ID (Drive v2)."""
    meta = {"title": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_folder_id:
        meta["parents"] = [{"id": parent_folder_id}]
    folder = drive.CreateFile(meta)
    folder.Upload()
    return folder["id"]

def move_file_to_folder(drive: GoogleDrive, file_id: str, new_parent_id: str):
    """Mueve un archivo a otra carpeta."""
    f = drive.CreateFile({"id": file_id})
    f.FetchMetadata(fields="parents")
    f["parents"] = [{"id": new_parent_id}]
    f.Upload()




BRONZE_MANIFEST_NAME = "manifest_ingesta.csv"

def ensure_manifest(drive, bronze_folder_id):
    """Devuelve (df_manifest, manifest_file_id). Crea uno vacío si no existe."""
    items = list_folder(drive, bronze_folder_id)
    manifest = next((x for x in items if x.get("title") == BRONZE_MANIFEST_NAME), None)

    if manifest is None:
        # Crear manifest vacío
        cols = ["file_id", "source_folder", "raw_title", "createdDate", "md5Checksum",
                "bronze_file_id", "bronze_title", "processed_at_utc"]
        df = pd.DataFrame(columns=cols)
        data = df.to_csv(index=False).encode("utf-8")
        mf_id = upload_bytes_to_folder(
            drive, data, BRONZE_MANIFEST_NAME, bronze_folder_id, mime_type="text/csv"
        )
        return df, mf_id
    else:
        b = download_file_bytes(drive, manifest["id"])
        df = pd.read_csv(io.BytesIO(b))
        return df, manifest["id"]

def save_manifest(drive, bronze_folder_id, manifest_file_id, df_manifest):
    """Sobrescribe el manifest en Drive."""
    data = df_manifest.to_csv(index=False).encode("utf-8")
    # Subir como nuevo y (opcional) borrar el anterior, o simplemente crear/actualizar
    # Con PyDrive2, lo más directo es crear un nuevo archivo y (opcional) borrar el viejo.
    new_id = upload_bytes_to_folder(
        drive, data, BRONZE_MANIFEST_NAME, bronze_folder_id, mime_type="text/csv"
    )
    # (Opcional) borrar el anterior:
    # f = drive.CreateFile({"id": manifest_file_id})
    # f.Delete()
    return new_id

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

def process_one_file(drive, file_meta, bronze_folder_id):
    """
    Descarga un archivo, lo limpia y lo sube como Parquet a bronze.
    Devuelve (bronze_file_id, bronze_title).
    """
    file_id = file_meta["id"]
    title = file_meta.get("title")  # v2
    mime = file_meta.get("mimeType")
    created = file_meta.get("createdDate")
    md5 = file_meta.get("md5Checksum")

    raw_bytes = download_file_bytes(drive, file_id)

    # Detectar y cargar (adapta a tus formatos reales)
    # Asumimos CSV como ejemplo:
    df_raw = pd.read_csv(io.BytesIO(raw_bytes))  # usa sep=";" si aplica
    df_clean = clean_and_extract(df_raw)

    # Serializar a Parquet (bytes)
    parquet_bytes = io.BytesIO()
    df_clean.to_parquet(parquet_bytes, index=False)  # requiere pyarrow o fastparquet instalado
    parquet_bytes.seek(0)

    # Nombre parquet de salida
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bronze_title = f"{title}_clean_{ts}.parquet"

    bronze_file_id = upload_bytes_to_folder(
        drive, parquet_bytes.getvalue(), bronze_title, bronze_folder_id,
        mime_type="application/octet-stream"
    )
    return bronze_file_id, bronze_title, created, md5, title

def run_ingestion():
    st.header("Ingesta a Bronze")
    drive = get_drive()

    src_metano = st.secrets["folders"]["metano"]
    src_permeacion = st.secrets["folders"]["permeacion"]
    bronze_id = st.secrets["folders"]["bronze"]

    df_manifest, manifest_id = ensure_manifest(drive, bronze_id)
    ya_procesados = set(df_manifest["file_id"].astype(str)) if not df_manifest.empty else set()

    st.write("Leyendo listados de carpetas de origen…")
    items_met = list_folder(drive, src_metano)
    items_perm = list_folder(drive, src_permeacion)

    pendientes = []
    for x in items_met:
        if x["id"] not in ya_procesados:
            x["__source"] = "LineaMetano"
            pendientes.append(x)
    for x in items_perm:
        if x["id"] not in ya_procesados:
            x["__source"] = "LineaPermeacion"
            pendientes.append(x)

    st.info(f"Archivos pendientes: {len(pendientes)}")

    if st.button("Realizar ingesta"):
        rows = []
        progress = st.progress(0)
        for i, meta in enumerate(pendientes, start=1):
            try:
                bronze_id_out, bronze_title, created, md5, raw_title = process_one_file(
                    drive, meta, bronze_id
                )
                rows.append({
                    "file_id": meta["id"],
                    "source_folder": meta["__source"],
                    "raw_title": raw_title,
                    "createdDate": created,
                    "md5Checksum": md5,
                    "bronze_file_id": bronze_id_out,
                    "bronze_title": bronze_title,
                    "processed_at_utc": datetime.now(timezone.utc).isoformat(),
                })
                st.success(f"Procesado: {raw_title} → {bronze_title}")
            except Exception as e:
                st.error(f"Error con {meta.get('title')}: {e}")
            finally:
                progress.progress(i / max(1, len(pendientes)))

        if rows:
            df_new = pd.DataFrame(rows)
            df_manifest = pd.concat([df_manifest, df_new], ignore_index=True)
            manifest_id = save_manifest(drive, bronze_id, manifest_id, df_manifest)
            st.success("Manifest actualizado.")
        else:
            st.info("No había nada que procesar.")
