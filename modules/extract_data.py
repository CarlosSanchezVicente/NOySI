"""Coordinador de la ingesta: Drive (TDMS) -> Bronze -> Silver.

Versión mínima. De momento solo funciona en ``dry_run``: lista los TDMS de Drive y
dice qué haría, sin descargar ni escribir nada. La ingesta real (Parquet en Bronze,
``bronze.ingestion_log``, Silver) se construye en la Fase 3.
"""
import io
import logging

import pandas as pd
from nptdms import TdmsFile

from modules.drive_utils import (
    list_folder, es_tdms_time_relevante, extraer_experiment_id
)

logger = logging.getLogger(__name__)

# Clave (en config.drive_folders) de la carpeta de TDMS de la línea de botellas (antes "metano").
# N-39 la sustituirá por un mapeo de nombres con alias.
DEFAULT_FOLDER_KEY = "metano_line"


# AUXILIARY FUNCTIONS
def make_engine(cfg):
    """Crea la conexión SQLAlchemy a PostgreSQL con ``cfg.database_url``.

    Falla si la URL está vacía (en ``dev`` lo está salvo que se defina
    ``NOYSI_DEV_DATABASE_URL``), para no escribir nunca en una BBDD sin querer.
    """
    if not cfg.database_url:
        raise ValueError(
            "database_url vacío: en dev defina NOYSI_DEV_DATABASE_URL; "
            "no se crea ninguna conexión a PostgreSQL."
        )
    from sqlalchemy import create_engine   # import perezoso: solo si se necesita
    return create_engine(cfg.database_url)


def read_tdms_to_df(raw_bytes: bytes) -> pd.DataFrame:
    """Lee un TDMS (en bytes) y devuelve un DataFrame con una columna por canal.

    Parameters
    ----------
    raw_bytes : bytes
        Contenido del archivo ``.tdms``.
    """
    tdms_file = TdmsFile.read(io.BytesIO(raw_bytes))
    data = {}
    for group in tdms_file.groups():
        for channel in group.channels():
            data[channel.name] = pd.Series(channel[:])
    return pd.DataFrame(data)


# MAIN FUNCTION
def run_data_pipeline(cfg, drive, engine=None, dry_run=True, folder_key=DEFAULT_FOLDER_KEY):
    """Revisa la carpeta de TDMS de Drive y dice qué ingeriría.

    Parameters
    ----------
    cfg : config.Config
    drive : cliente de Drive (``drive_utils.get_drive``), solo lectura.
    engine : conexión a PostgreSQL; no se usa en ``dry_run``.
    dry_run : si es True (por defecto) solo informa, sin descargar ni escribir.
    folder_key : clave de la carpeta en ``cfg.drive_folders``.

    Returns
    -------
    dict
        Resumen: archivos relevantes, su MED y la acción prevista.
    """
    if not dry_run:
        raise NotImplementedError(
            "La ingesta real (Bronze/Silver) se implementa en la Fase 3; usar dry_run=True."
        )

    folder_id = cfg.drive_folders.get(folder_key)
    if not folder_id:
        raise KeyError(f"Falta la carpeta '{folder_key}' en la configuración (folders.{folder_key})")

    items = list_folder(drive, folder_id)
    relevant = [f for f in items if es_tdms_time_relevante(f.get("name", ""))]

    files = []
    for f in relevant:
        med = extraer_experiment_id(f["name"])
        files.append({
            "name": f["name"],
            "med": med,
            "size_bytes": f.get("size"),
            "modified": f.get("modifiedTime"),
            "action": "descargaría y leería" if med else "omitido: el nombre no contiene MED-<n>",
        })
        logger.info("dry_run: %s (%s)", f["name"], med)

    return {
        "dry_run": True,
        "files_in_folder": len(items),
        "tdms_relevant": len(relevant),
        "files": files,
    }
