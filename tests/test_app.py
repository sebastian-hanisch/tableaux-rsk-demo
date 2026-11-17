"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


# --- Eingaben, Auswahlfelder und Adresszeile (zusätzlich zum Rauchtest oben) ---------------------------------------------------------------------

def test_ungueltige_folgen_geben_eine_meldung_und_keinen_fehler():
    for text in ("", "1 2 2", "a b c", "1 " * 13, "7"):
        at = _fresh_app()
        at.text_input(key="e1_text").set_value(text).run(timeout=TIMEOUT)
        assert not at.exception, (text, [str(e) for e in at.exception])
        if text in ("", "1 2 2", "a b c", "1 " * 13):
            assert any("Angezeigt wird solange die Handfolge" in w.value for w in at.warning), text
    at = _fresh_app()
    at.text_input(key="e1_text").set_value("30 10 20").run(timeout=TIMEOUT)
    assert any("auf Ränge umgerechnet" in i.value for i in at.info)


def test_jede_auswahl_der_auswahlfelder_laeuft_ohne_fehler():
    for key, art in (("e1_orient", "radio"), ("e2_hl", "radio"), ("e3_d", "select_slider"), ("e5_inhalt", "selectbox"), ("e5_fassung", "radio")):
        optionen = list(getattr(_fresh_app(), art)(key=key).options)
        for wert in optionen:
            at = _fresh_app()
            getattr(at, art)(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_wort_mit_falschem_inhalt_gibt_eine_meldung():
    at = _fresh_app()
    at.text_input(key="e5_text").set_value("1 2 3").run(timeout=TIMEOUT)
    assert not at.exception and any("passt nicht zum Inhalt" in w.value for w in at.warning)


def test_zurueckrechnen_umschalter_zeigt_das_ergebnis():
    at = _fresh_app()
    at.toggle(key="e1_zurueck").set_value(True).run(timeout=TIMEOUT)
    assert not at.exception and any("das ist die eingegebene Folge" in s.value for s in at.success)


def test_zufallsfolge_knopf_setzt_eine_folge_der_gewaehlten_laenge():
    at = _fresh_app()
    at.slider(key="e1_n").set_value(9).run(timeout=TIMEOUT)
    [b for b in at.button if b.label == "🎲 Zufallsfolge würfeln"][0].click().run(timeout=TIMEOUT)
    assert not at.exception
    zahlen = sorted(int(x) for x in at.text_input(key="e1_text").value.split())
    assert zahlen == list(range(1, 10))


def test_permalink_uebernimmt_werte_und_begrenzt_sie():
    at = AppTest.from_file(APP_PATH)
    at.query_params["folge"] = "3 4 1 2"
    at.query_params["fn"] = "99"
    at.query_params["orient"] = "gibt es nicht"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.text_input(key="e1_text").value == "3 4 1 2" and at.slider(key="e2_n").value == 30
    assert at.radio(key="e1_orient").value.startswith("Stapel fallend")


def test_schritt_regler_wird_bei_kuerzerer_folge_begrenzt():
    at = _fresh_app()
    at.text_input(key="e1_text").set_value("2 1 3").run(timeout=TIMEOUT)
    assert not at.exception and at.slider(key="e1_schritt").value == 3 and at.slider(key="e1_schritt").max == 3
    at.text_input(key="e1_text").set_value("1").run(timeout=TIMEOUT)
    assert not at.exception
