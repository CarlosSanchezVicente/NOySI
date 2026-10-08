"""Tests de las funciones puras de modules/drive_utils.py (sin red)."""
import pytest

from modules.drive_utils import es_tdms_time_relevante, extraer_experiment_id


@pytest.mark.parametrize("name, expected", [
    ("C2_CO2_50%HR_LedL365A oct.-05-23 Time 0833.tdms", True),
    ("C2_CO2_50%HR_LedL365A Respuestas oct.-05-23 Time 0833.tdms", False),   # archivo de respuestas
    ("C3_CO2_50%HR_Led365A oct.-23-23 Time 0859.tdms_index", False),         # índice
    ("sin_hora.tdms", False),
    ("", False),
    (None, False),
])
def test_es_tdms_time_relevante(name, expected):
    assert es_tdms_time_relevante(name) is expected


@pytest.mark.parametrize("name, expected", [
    ("MED-228 oct Time 0833.tdms", "MED-228"),
    ("x_MED-12_y.tdms", "MED-12"),
    ("MED-123 prueba", "MED-123"),   # no se confunde con MED-12
    ("sin_med.tdms", None),
])
def test_extraer_experiment_id(name, expected):
    assert extraer_experiment_id(name) == expected
