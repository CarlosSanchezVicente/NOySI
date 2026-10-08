"""Lectura de los TDMS de ejemplo (data/example/). Se omiten si la carpeta no existe (está fuera de git)."""
from pathlib import Path

import pytest

from modules.drive_utils import es_tdms_time_relevante
from modules.extract_data import read_tdms_to_df

EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "data" / "example"
TDMS_FILES = sorted(p for p in EXAMPLE_DIR.glob("*.tdms") if es_tdms_time_relevante(p.name))

pytestmark = pytest.mark.skipif(not TDMS_FILES, reason="no hay TDMS de ejemplo en data/example/")


@pytest.mark.parametrize("path", TDMS_FILES, ids=lambda p: p.name)
def test_read_tdms_to_df(path):
    df = read_tdms_to_df(path.read_bytes())
    assert len(df) > 0
    assert df.shape[1] > 1
    names = [c.strip() for c in df.columns]
    assert any(n.startswith("Time") for n in names)
    assert any(n.startswith("R1") for n in names)
