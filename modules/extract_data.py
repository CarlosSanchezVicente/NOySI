# IMPORTS
import io
import os
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
from modules.utils_drive import (
    get_drive, download_file_bytes, upload_bytes_to_folder
)

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
# Usa el scope mínimo necesario. Para lectura y escritura, mejor drive.file o drive.
# - readonly: solo lectura
# - drive.file: leer y escribir archivos creados/abiertos por la app
# - drive: acceso completo al Drive al que tenga permisos
READ_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
WRITE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FULL_SCOPE = "https://www.googleapis.com/auth/drive"

# Elige el alcance que necesitas:
BRONZE_MANIFEST_NAME = "manifest_ingesta.csv"


# FUNCIONES MANIFEST
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

def es_tdms_time_relevante(title: str) -> bool:
    if not title:
        return False
    t = title.lower()
    return t.endswith(".tdms") and "time" in t and not t.endswith(".tdms_index")

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


# FUNCIÓN PRINCIPAL
"""
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
"""
            
@st.cache_resource(show_spinner=False)

def list_folder(drive: GoogleDrive, folder_id: str):
    q = f"'{folder_id}' in parents and trashed=false"
    return drive.ListFile({"q": q}).GetList()

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

def run_ingestion():
    drive = get_drive()
    metano_id = st.secrets["folders"]["metano"]

    items = list_folder(drive, metano_id)

    tdms_relevantes = [
        f for f in items
        if es_tdms_time_relevante(f.get("title", ""))
    ]

    st.write(f"TDMS relevantes: {len(tdms_relevantes)}")
    for f in tdms_relevantes:
        st.write(f["title"])

