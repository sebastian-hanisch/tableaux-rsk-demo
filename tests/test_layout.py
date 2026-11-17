"""Layout (DEMO-PLAYBOOK §2): fester Kopf, Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben, Kernfragen vor den Experimenten, Formeln im Expander.

Die Hervorhebung ist zustandslos (`aktives_preset` vergleicht jeden Regler aus SETTING_SPECS mit dem Preset). Die Tests stellen sicher, dass jeder Regler der Seitenleiste dort
steht, dass jeder Eintrag aus SETTING_SPECS auch gezeichnet wird, und dass die Änderung jedes Reglers die Markierung aufhebt (die Experiment-Regler stehen im Hauptbereich)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import trk_constants as C
import trk_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
REGLER_ARTEN = ("slider", "number_input", "select_slider", "selectbox", "radio", "toggle", "checkbox", "text_input")


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _typen(at) -> dict:
    """Button-Typ je Preset-Name (die Preset-Buttons der Seitenleiste)."""
    return {b.label: b.proto.type for b in at.sidebar.button if b.label in C.PRESETS}


def _regler(at, key):
    for art in REGLER_ARTEN:
        try:
            return getattr(at, art)(key=key)
        except KeyError:
            continue
    raise AssertionError(f"Regler {key} wird nicht gezeichnet")


def _anderer_wert(regler, spec):
    """Ein gültiger Wert, der vom aktuellen und von allen Preset-Werten dieses Reglers abweicht (sonst würde ein anderes Preset aktiv)."""
    verboten = {regler.value} | {preset[k] for preset in C.PRESETS.values() for k in preset if k == regler.key}
    if spec.caster is bool:
        return not regler.value
    if spec.options is not None:
        return next(o for o in spec.options if o not in verboten)
    if spec.caster is str:
        return "2 1 3" if regler.key == "e1_text" else "1 1 2 3 3 2"
    kandidaten = [regler.max, regler.min, (regler.min + regler.max) // 2]
    return next(int(w) for w in kandidaten if w not in verboten)


def test_presets_stehen_in_der_seitenleiste_und_nicht_im_hauptbereich():
    at = _app()
    assert [b.label for b in at.sidebar.button][: len(C.PRESETS)] == list(C.PRESETS)  # die ersten Buttons der Seitenleiste
    assert not [b for b in at.main.button if b.label in C.PRESETS]


def test_titel_steht_im_festen_kopf():
    at = _app()
    assert "st-key-kopf" in " ".join(h.proto.body for h in at.get("html"))  # das Stylesheet setzt an der Klasse des Containers an
    assert at.title[0].value


def test_kernfragen_stehen_vor_den_experimenten_und_formeln_im_expander():
    at = _app()
    markdown = [m.value for m in at.markdown]
    kern = next(i for i, m in enumerate(markdown) if m.startswith("## ❓ Kernfragen"))
    assert kern >= 0
    assert [s.value for s in at.subheader][:5] == [
        "🔬 Experiment 1: Einfügen Schritt für Schritt", "🔬 Experiment 2: Wie viele Folgen gehören zu welcher Form?", "🔬 Experiment 3: Die Form im ausgedachten Modell V (Verweilzeit D)",
        "🔬 Experiment 4: Zugfolgen gegen Folgen (die Falle der Zähleinheit)", "🔬 Experiment 5: Gleichstände – Wörter mit Zielgruppen"]
    assert any(s.value == "🚧 Wo die Annahmen enden" for s in at.subheader)
    assert next(e for e in at.expander if e.label == "📐 Mathematische Formulierung")
    assert next(e for e in at.expander if e.label.startswith("So funktioniert"))


def test_ausgedachtes_modell_wird_gleich_am_anfang_genannt():
    at = _app()
    assert any("ausgedachten Modell" in i.value and "nicht aus einer Messung" in i.value for i in at.info)


def test_beim_start_ist_genau_das_standard_preset_hervorgehoben():
    typen = _typen(_app())
    assert [name for name, typ in typen.items() if typ == "primary"] == [next(iter(C.PRESETS))]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_angeklicktes_preset_ist_hervorgehoben_und_bleibt_es_im_naechsten_lauf(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]
    at.run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]


def test_jeder_regler_der_seitenleiste_steht_in_setting_specs():
    at = _app()
    schluessel = {w.key for art in REGLER_ARTEN for w in getattr(at.sidebar, art) if w.key}
    fehlt = schluessel - set(P.SETTING_SPECS)
    assert not fehlt, f"Regler {sorted(fehlt)} fehlen in SETTING_SPECS: ihre Änderung hebt das aktive Preset nicht auf"


def test_jeder_eintrag_aus_setting_specs_wird_gezeichnet():
    at = _app()
    for key in P.SETTING_SPECS:
        _regler(at, key)


@pytest.mark.parametrize("state_key", [k for k in P.SETTING_SPECS if k != "seed_input"])
def test_jede_aenderung_eines_reglers_hebt_die_hervorhebung_auf(state_key):
    at = _app()
    regler = _regler(at, state_key)
    regler.set_value(_anderer_wert(regler, P.SETTING_SPECS[state_key])).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert "primary" not in _typen(at).values(), state_key
    # erneutes Anklicken markiert wieder
    name = next(iter(C.PRESETS))
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert _typen(at)[name] == "primary"


def test_der_zufalls_seed_gehoert_nicht_zum_szenario():
    at = _app()
    at.sidebar.number_input(key="seed_input").set_value(4242).run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [next(iter(C.PRESETS))]
