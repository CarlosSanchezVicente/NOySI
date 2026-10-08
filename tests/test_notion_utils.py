"""Tests de modules/notion_utils.py con una respuesta de Notion SINTÉTICA (sin red ni secretos)."""
import json
from pathlib import Path

import pandas as pd
import pytest

from modules import notion_utils as nu

FIXTURE = Path(__file__).parent / "fixtures" / "notion_medidas.json"


@pytest.fixture(scope="module")
def pages():
    return json.loads(FIXTURE.read_text(encoding="utf8"))


# extract_data_from_json
def test_extract_data_from_json_filas_y_columnas_base(pages):
    df = nu.extract_data_from_json(pages)
    assert len(df) == 2
    for col in ("id", "created_time", "last_edited_time", "created_by", "last_edited_by", "parent", "url"):
        assert col in df.columns
    assert df.loc[0, "parent"] == "00000000-0000-0000-0000-0000000000d1"


def test_extract_data_from_json_acepta_lista(pages):
    assert len(nu.extract_data_from_json(pages["results"])) == 2


def test_extract_data_from_json_tipos_de_propiedad(pages):
    df = nu.extract_data_from_json(pages)
    a, b = df.iloc[0], df.iloc[1]
    assert a["Título"] == "Medida sintética A" and pd.isna(b["Título"])   # title
    assert a["Comentario"] == "Texto de prueba" and pd.isna(b["Comentario"])   # rich_text
    assert a["Proporción"] == 2.5   # number
    assert a["Humedad"] == "50%" and pd.isna(b["Humedad"])   # select
    assert a["Etiquetas"] == "CO2, NH3" and b["Etiquetas"] == "CH4"   # multi_select
    assert a["Realizado"] == "2024-01-15" and pd.isna(b["Realizado"])   # date
    assert (a["ID_conn"], b["ID_conn"]) == ("MED-1", "MED-123")   # unique_id


def test_extract_data_from_json_relation(pages):
    df = nu.extract_data_from_json(pages)
    assert df.loc[0, "Sensor"] == "00000000-0000-0000-0000-0000000000s1"
    assert df.loc[1, "Sensor"] == "00000000-0000-0000-0000-0000000000s2, 00000000-0000-0000-0000-0000000000s3"
    assert df.loc[1, "Led"] == "00000000-0000-0000-0000-0000000000e1"
    assert df.loc[0, "Led"] == ""   # relación vacía -> cadena vacía (comportamiento actual)


def test_extract_data_from_json_numero_vacio_es_cero_hoy(pages):
    """Comportamiento ACTUAL (ERR-H3): un número vacío se guarda como 0. Debería ser NULL (Fase 4)."""
    df = nu.extract_data_from_json(pages)
    assert df.loc[0, "BET (m2/g)"] == 0
    assert df.loc[1, "BET (m2/g)"] == 120


def test_extract_data_from_json_vacio():
    assert nu.extract_data_from_json({"results": []}).empty


# parse_notion_purity
@pytest.mark.parametrize("value, expected", [
    ("85,5", 85.5),
    ("85.5", 85.5),
    ("77,0-82,6", 79.8),
    ("77.0-82.6", 79.8),
    (None, 0.0),
    ("", 0.0),
    ("abc", 0.0),
])
def test_parse_notion_purity(value, expected):
    assert nu.parse_notion_purity(value) == pytest.approx(expected)


# transform_rages
@pytest.mark.parametrize("value, expected", [
    ("5 - 10", 7.5),
    ("12", 12.0),
    (None, 0),
])
def test_transform_rages(value, expected):
    assert nu.transform_rages(value) == pytest.approx(expected)


# remove_symbol_nm
@pytest.mark.parametrize("value, expected", [
    ("100 nm", 100),
    ("≤ 50 nm", 50),
    ("2 um", 2000),
    ("30", 30),
    (None, 0),
])
def test_remove_symbol_nm(value, expected):
    assert nu.remove_symbol_nm(value) == expected


# remove_symbol_humidity
@pytest.mark.parametrize("value, expected", [("50%", 50), ("50 %", 50), ("0%", 0), (None, 0)])
def test_remove_symbol_humidity(value, expected):
    assert nu.remove_symbol_humidity(value) == expected


# remove_symbol_bottle
@pytest.mark.parametrize("value, expected", [
    ("500 ppb", 500.0),
    ("10 PPB", 10.0),
    ("2 ppm", 2000.0),
    ("1.5 PPM", 1500.0),
    (None, None),
    ("5 ppt", None),   # unidad no reconocida: hoy devuelve None
])
def test_remove_symbol_bottle(value, expected):
    assert nu.remove_symbol_bottle(value) == expected


def test_sort_gases_names():
    assert nu.sort_gases_names("NH3, CO2") == "CO2, NH3"
    assert nu.sort_gases_names("CO2") == "CO2"
