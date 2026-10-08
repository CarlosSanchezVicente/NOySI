"""Tests de config.py: sin secretos reales (se pasan dicts de prueba) y sin red."""
import pytest

import config

FAKE_SECRETS = {
    "tokens": {"NOTION_TOKEN": "tok", "MEDIDAS_DB_ID": "med-id"},
    "drive": {"service_account_json": "{}"},
    "folders": {"metano_line": "folder-id"},
    "database": {"database_url": "postgresql://prod.invalid/prod"},
}


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch):
    for var in ("NOYSI_ENV", "ENABLE_EXTERNAL_WRITES", "NOYSI_DEV_DATABASE_URL",
                "NOYSI_SILVER_DB", "NOYSI_GOLD_DB", "TOKENS_NOTION_TOKEN"):
        monkeypatch.delenv(var, raising=False)


def test_valores_por_defecto_seguros():
    cfg = config.load_config({})
    assert cfg.env == "dev"
    assert cfg.enable_external_writes is False
    assert cfg.drive_scopes == (config.DRIVE_READ_SCOPE,)
    assert cfg.database_url == ""
    assert cfg.silver_db.name == "LabSilver.db" and cfg.gold_db.name == "LabGold.db"


def test_dev_ignora_database_url_de_secrets():
    assert config.load_config(FAKE_SECRETS).database_url == ""


def test_dev_usa_url_de_desarrollo(monkeypatch):
    monkeypatch.setenv("NOYSI_DEV_DATABASE_URL", "postgresql://localhost/dev")
    assert config.load_config(FAKE_SECRETS).database_url == "postgresql://localhost/dev"


def test_prod_usa_secrets_y_bbdd_de_produccion(monkeypatch):
    monkeypatch.setenv("NOYSI_ENV", "prod")
    cfg = config.load_config(FAKE_SECRETS)
    assert cfg.database_url == "postgresql://prod.invalid/prod"
    assert cfg.silver_db.name == "LabSilver.db" and cfg.gold_db.name == "LabGold.db"


def test_entorno_invalido(monkeypatch):
    monkeypatch.setenv("NOYSI_ENV", "staging")
    with pytest.raises(ValueError):
        config.load_config({})


def test_escrituras_solo_si_se_activan_por_entorno(monkeypatch):
    monkeypatch.setenv("ENABLE_EXTERNAL_WRITES", "true")
    cfg = config.load_config({})
    assert cfg.enable_external_writes is True
    assert cfg.drive_scopes == (config.DRIVE_WRITE_SCOPE,)


def test_variable_de_entorno_tiene_prioridad(monkeypatch):
    monkeypatch.setenv("TOKENS_NOTION_TOKEN", "desde-entorno")
    assert config.load_config(FAKE_SECRETS).notion_token == "desde-entorno"


def test_ids_de_notion_y_carpetas():
    cfg = config.load_config(FAKE_SECRETS)
    assert cfg.notion_db_ids["MEDIDAS_DB"] == "med-id"
    assert cfg.notion_db_ids["GASES_DB"] == ""   # no definido
    assert cfg.drive_folders["metano_line"] == "folder-id"
