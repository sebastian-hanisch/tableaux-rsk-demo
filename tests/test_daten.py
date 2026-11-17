"""Die vorgerechneten Dateien in data/ stimmen mit einer Neu-Rechnung überein (die Skripte in tools/ haben dafür `--check`).

Ganzzahlen (Formen, Zugfolgen) sind exakt; die Modell-V-Tabelle (Zufall) wird als Band verglichen. Die langen Läufe haben die Marke `slow`."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _werkzeug(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _datei(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


@pytest.mark.slow
def test_formen_tabelle_stimmt_mit_neu_rechnung_bis_n9():
    assert _werkzeug("trk_make_formen").rechnen() == _datei("trk_formen.json")


@pytest.mark.slow
def test_zugfolgen_tabelle_stimmt_mit_neu_rechnung():
    assert _werkzeug("trk_make_zuege").rechnen() == _datei("trk_zuege.json")


@pytest.mark.slow
def test_modellv_ein_vollstaendiger_lauf_stimmt_mit_der_tabelle_im_band():
    """D = 4, Zufalls-Seed 101, alle 20 000 Folgen: Mittel auf 0,02, Anteil der häufigsten Form auf 0,01."""
    import trk_evaluation as ev

    st = ev.modellv_statistik(10, 4, 20000, 101)
    zeile = next(z for z in _datei("trk_modellv.json")["zeilen"] if z["d"] == 4)["seeds"]["101"]
    assert abs(st["mittel_erste_zeile"] - zeile["mittel_erste_zeile"]) < 0.02 and abs(st["mittel_zeilenzahl"] - zeile["mittel_zeilenzahl"]) < 0.02
    assert list(st["top"]) == zeile["top"] and abs(st["top_anteil"] - zeile["top_anteil"]) < 0.01 and st["formen_gesehen"] == zeile["formen"]


def test_modellv_stromzuordnung_wie_in_der_tabelle():
    """Der Strom je D ist Zufalls-Seed + Index von D: dieselbe Folge in der App und im Werkzeug."""
    import trk_scenario as S

    assert S.D_WERTE.index(4) == 3
    assert S.folgen_modell(10, 4, 1, 101)[0] == S.folge_modell_v(10, 4, S.strom(101, 3))
    assert S.folgen_modell(10, 4, 5, 101)[:3] == S.folgen_modell(10, 4, 3, 101)
