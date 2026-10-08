"""Configuración única del proyecto.

Toda ruta, secreto o nombre de tabla se lee aquí y se pasa a las funciones
como parámetro. Importar este módulo no lee secretos ni abre conexiones:
solo ``load_config()`` lo hace, y solo cuando se la llama.

Orden de búsqueda de cada valor: variable de entorno -> ``st.secrets``.
Cambiar de entorno (local -> cloud) es solo cambiar esa configuración.
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent

# Logo de la app. El nombre es el que rastrea git (img/NoySI.png); en Linux importan las mayúsculas.
LOGO_PATH = ROOT / "img" / "NoySI.png"

# Permisos de Drive: solo lectura salvo que se activen las escrituras externas (Fase 9).
DRIVE_READ_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
DRIVE_WRITE_SCOPE = "https://www.googleapis.com/auth/drive"

# Propiedad de Notion que el script lee y escribe. `Carga bbdd` es una fórmula de solo lectura
# que muestra este valor con colores: no se puede escribir.
NOTION_STATUS_PROPERTY = "Status"
NOTION_STATUS_TYPE = "select"          # tipo de la propiedad en la API (confirmado por el usuario 2026-10-08: selector)
NOTION_STATE_PENDING = "Pendiente"                # aún no cargado (también si está vacío)
NOTION_STATE_DONE = "Procesado"                    # cargado correctamente
NOTION_STATE_INGEST_ERROR = "Error ingesta"        # problema con el archivo (falta TDMS, corrupto, sustituido…)
NOTION_STATE_METADATA_ERROR = "Error metadatos"    # faltan datos o son incoherentes en Notion
NOTION_STATE_PARTIAL = "Ensayo incompleto"         # cargado pero incompleto (PARTIAL: último ciclo a medias…)
NOTION_STATE_ERROR = "Error"                       # fallo inesperado del script
# Regla: cualquier valor distinto de Procesado significa "hay que revisar" y su registro de Notion
# se vuelve a leer en la siguiente ingesta (además de los vacíos); si vuelve a fallar, se anota de nuevo.
# Excepción prevista (N-41, aún no implementada): los registros con Resultado = "Erróneo (revisado)"
# dejan de leerse y de cargarse. Un "Ensayo incompleto" aún sin revisar solo se recarga si cambia el
# md5 del archivo (lo decide ingestion_log, Fase 3).
NOTION_STATES_TO_READ = (
    NOTION_STATE_PENDING,
    NOTION_STATE_INGEST_ERROR,
    NOTION_STATE_METADATA_ERROR,
    NOTION_STATE_PARTIAL,
    NOTION_STATE_ERROR,
)

# (sección de st.secrets, clave) de cada valor. La variable de entorno se llama SECCION_CLAVE en mayúsculas.
_NOTION_DB_KEYS = {
    "MATERIALES_DB": "MATERIALES_DB_ID",
    "DISOLUCIONES_DB": "DISOLUCIONES_DB_ID",
    "SENSORES_DB": "SENSORES_DB_ID",
    "LED_DB": "LED_DB_ID",
    "GASES_DB": "GASES_DB_ID",
    "MEDIDAS_DB": "MEDIDAS_DB_ID",
}


@dataclass(frozen=True)
class Config:
    env: str                              # 'dev' | 'prod'
    notion_token: str
    notion_db_ids: dict                   # {'MATERIALES_DB': id, ...}
    drive_service_account_json: str
    drive_scopes: tuple
    drive_folders: dict                   # {'metano_line': id, ...}
    database_url: str                     # vacío en dev salvo NOYSI_DEV_DATABASE_URL
    silver_db: Path
    gold_db: Path
    enable_external_writes: bool
    logo_path: Path


def _read_streamlit_secrets():
    """Devuelve ``st.secrets`` o un dict vacío si Streamlit o el archivo no existen."""
    try:
        import streamlit as st
        return st.secrets.to_dict()
    except (ImportError, FileNotFoundError, KeyError, AttributeError):
        logger.debug("st.secrets no disponible; solo se usan variables de entorno")
        return {}


def _get(secrets, section, key, default=""):
    """Variable de entorno ``SECTION_KEY`` o ``secrets[section][key]``."""
    env_value = os.environ.get(f"{section}_{key}".upper())
    if env_value is not None:
        return env_value
    return secrets.get(section, {}).get(key, default)


def load_config(secrets=None):
    """Construye la configuración.

    Parameters
    ----------
    secrets : dict, optional
        Secretos ya cargados (útil en tests). Si es None se lee ``st.secrets``.
    """
    if secrets is None:
        secrets = _read_streamlit_secrets()

    env = os.environ.get("NOYSI_ENV", "dev").lower()
    if env not in ("dev", "prod"):
        raise ValueError(f"NOYSI_ENV debe ser 'dev' o 'prod', no {env!r}")

    writes = os.environ.get("ENABLE_EXTERNAL_WRITES", "false").lower() == "true"

    # En dev NUNCA se usa `database.database_url` de st.secrets (puede ser la BBDD de producción):
    # solo NOYSI_DEV_DATABASE_URL. Si no está definida queda vacía y no se escribe en PostgreSQL.
    if env == "prod":
        database_url = _get(secrets, "database", "database_url")
    else:
        database_url = os.environ.get("NOYSI_DEV_DATABASE_URL", "")

    # Decisión 2026-10-08: las BBDD actuales sirven también para desarrollo (se sustituirán por una
    # carga completa nueva en PostgreSQL), así que dev y prod comparten las rutas de los SQLite.
    silver, gold = ROOT / "data/Silver/LabSilver.db", ROOT / "data/Gold/LabGold.db"

    return Config(
        env=env,
        notion_token=_get(secrets, "tokens", "NOTION_TOKEN"),
        notion_db_ids={name: _get(secrets, "tokens", key) for name, key in _NOTION_DB_KEYS.items()},
        drive_service_account_json=_get(secrets, "drive", "service_account_json"),
        drive_scopes=(DRIVE_WRITE_SCOPE,) if writes else (DRIVE_READ_SCOPE,),
        drive_folders=dict(secrets.get("folders", {})),
        database_url=database_url,
        silver_db=Path(os.environ.get("NOYSI_SILVER_DB", silver)),
        gold_db=Path(os.environ.get("NOYSI_GOLD_DB", gold)),
        enable_external_writes=writes,
        logo_path=LOGO_PATH,
    )
