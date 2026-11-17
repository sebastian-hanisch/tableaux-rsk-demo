"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und je Schnellstart-Szenario die erwartete Verdikt-Zeile (DEMO-PLAYBOOK §11a Punkt 7).

Die Erwartungen sind von Hand gesetzt (siehe test_verdicts.py und test_handbeispiel.py), nicht aus dem Lauf übernommen."""

import pytest

import trk_constants as C
import trk_evaluation as ev
import trk_presets as P
import trk_scenario as S


def _wert(name, key):
    return C.PRESETS[name].get(key, P.SETTING_SPECS[key].default)


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_valid_for_their_widgets():
    for name, preset in C.PRESETS.items():
        for key, wert in preset.items():
            spec = P.SETTING_SPECS[key]
            assert P.begrenze(spec, wert if spec.caster is not bool else str(wert)) == wert, (name, key)


def test_setting_specs_cover_every_preset_key_and_the_seed():
    assert set(P.PRESET_KEYS.values()) | {"seed_input"} == set(P.SETTING_SPECS)


def test_default_preset_equals_the_default_settings():
    erstes = next(iter(C.PRESETS))
    for key, spec in P.SETTING_SPECS.items():
        if key != "seed_input":
            assert _wert(erstes, key) == spec.default, key


def test_no_two_presets_are_the_same_scenario():
    szenarien = [tuple(_wert(n, k) for k in P.PRESET_KEYS) for n in C.PRESETS]
    assert len(set(szenarien)) == len(szenarien)


def test_default_text_matches_the_default_step_and_content():
    folge = S.folge_einlesen(C.DEFAULT_TEXT, C.E1_MAX_LAENGE)[0]
    assert len(folge) == P.SETTING_SPECS["e1_schritt"].default == 6
    inhalt = tuple(int(x) for x in C.DEFAULT_INHALT.strip("()").split(","))
    assert S.wort_einlesen(C.DEFAULT_WORT, inhalt)[0] is not None


def test_permalink_begrenzt_und_weist_ungueltiges_ab():
    s = P.SETTING_SPECS
    assert P.begrenze(s["e2_n"], "99") == 30 and P.begrenze(s["e2_n"], "-3") == 2 and P.begrenze(s["e2_n"], "x") is None
    assert P.begrenze(s["e1_orient"], "irgendwas") is None and P.begrenze(s["e3_d"], "16") == "16" and P.begrenze(s["e3_d"], "3") is None
    assert P.begrenze(s["e1_zurueck"], "true") is True and P.begrenze(s["e1_zurueck"], "false") is False
    assert P.begrenze(s["e1_text"], "x" * 500) == "x" * 80


# --- je Szenario die erwartete Verdikt-Zeile -------------------------------------------------------------------------------------------------------

def _folge(name):
    return S.folge_einlesen(_wert(name, "e1_text"), C.E1_MAX_LAENGE)[0]


def test_preset_handfolge():
    name = "Handfolge n = 6 (1,3,6,2,5,4)"
    art, text = ev.verdict_einfuegen(ev.analysiere_folge(_folge(name)))
    assert art == "success" and "Form (3,2,1), f = 16" in text and "256 von 720" in text and _wert(name, "e1_schritt") == 6


def test_preset_alle_folgen_n4():
    name = "Alle Folgen n = 4"
    n = _wert(name, "e2_n")
    assert n == 4
    from trk_enum import aufzaehlen
    art, text = ev.verdict_formen(ev.formen_zusammenfassung(n), aufzaehlen(n))
    assert "5 Formen" in text and "(3,1) und (2,1,1) mit je 9 von 24 Folgen" in text and "Catalan(4) = 14 Folgen" in text and "nur 7" in text


def test_preset_ein_stapel_gegen_zwei():
    name = "Ein Stapel gegen zwei: (3,4,1,2)"
    folge = _folge(name)
    assert folge == (3, 4, 1, 2) and _wert(name, "e1_schritt") == 4
    a = ev.analysiere_folge(folge)
    assert not a.ein_stapel and a.stapelzahl == 2 and a.form == (2, 2)
    assert "Ein einziger Stapel sortiert die Folge nicht" in ev.verdict_einfuegen(a)[1] and "Mindestzahl **fallender** Stapel ([3, 1] [4, 2])" in ev.verdict_einfuegen(a)[1]


def test_preset_formverteilung_n10():
    name = "Formverteilung n = 10"
    art, text = ev.verdict_formen(ev.formen_zusammenfassung(_wert(name, "e2_n")))
    assert "42 Formen" in text and "(4,3,2,1) mit 589\xa0824 von 3\xa0628\xa0800 Folgen (16,3 %)" in text and "zusammen: 49,2 %" in text


def test_preset_verweilzeit_d4_liegt_im_band():
    name = "Verweilzeit D = 4"
    d = dict(zip(C.D_LABELS, S.D_WERTE))[_wert(name, "e3_d")]
    assert d == 4 and _wert(name, "e3_n") == 10
    stat = ev.modellv_statistik(10, d, 2000, 101)
    assert abs(stat["mittel_erste_zeile"] - 6.05) < 0.15 and abs(stat["mittel_zeilenzahl"] - 3.02) < 0.15
    art, text = ev.verdict_modellv_live(stat, 10, d, 101)
    assert "D = 4, n = 10, 2000 Folgen" in text and "exakt 4,3350" in text


def test_preset_zugfolgen_zwei_stapel_n4():
    name = "Zugfolgen: zwei Stapel, n = 4"
    t, n = _wert(name, "e4_t"), _wert(name, "e4_n")
    art, text = ev.verdict_zuege(ev.zug_tabelle(t, 8), t, n)
    assert art == "warning" and "462 Zugfolgen" in text and "24 verschiedene Folgen" in text and "19,25" in text


def test_preset_zielgruppen_222():
    name = "Zielgruppen (2,2,2)"
    inhalt = tuple(int(x) for x in _wert(name, "e5_inhalt").strip("()").split(","))
    wort, fehler = S.wort_einlesen(_wert(name, "e5_text"), inhalt)
    assert fehler is None and inhalt == (2, 2, 2)
    art, text = ev.verdict_woerter(ev.analysiere_wort(inhalt, wort, True))
    assert art == "success" and "Alle 90 Wörter" in text and "74 von 90" in text and "Form (3,2,1): 32 = 16 · 2" in text


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_kein_preset_meldet_einen_fehler(name):
    """Kein Szenario darf ein Fehler-Verdikt auslösen (Umkehrung, Gegenproben, Aufzählung)."""
    folge = _folge(name)
    assert ev.verdict_einfuegen(ev.analysiere_folge(folge))[0] == "success"
    assert ev.verdict_einfuegen(ev.analysiere_folge(folge, fallend=False))[0] == "success"
    assert ev.verdict_formen(ev.formen_zusammenfassung(_wert(name, "e2_n")))[0] == "info"
