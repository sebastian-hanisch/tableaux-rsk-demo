"""Claims-Tests: jede Zahl der Befunde B1 bis B12 der README mit ihren Voraussetzungen (DEMO-PLAYBOOK §4, §11a; die Tabelle „Zahl → Test“ der README nennt je Befund die Funktion).

Zähleinheiten: Folgen (n! Anordnungen der Ränge), Tableaux, Zugfolgen (vollständige Zugreihen), Wörter (Folgen mit gleichen Buchstaben).
Plattform (Lehre 2026-11-15): alle Zählungen sind Ganzzahlen oder Brüche und deshalb exakt; Zufallsproben (Modell V, Zufallsfolgen) als Band. Zufall nur aus SplitMix64 (`trk_rng`).
Zeiten stehen nur in der README (eine Messung, Windows), in keinem Test."""

import json
import math
from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path

import pytest

import trk_enum as E
import trk_evaluation as ev
import trk_haken as H
import trk_rsk as R
import trk_scenario as S
import trk_woerter as W
import trk_zuege as Z
from trk_rng import SplitMix64

ROOT = Path(__file__).resolve().parent.parent


def _rund(x, nd=1):
    return round(float(x) * 100, nd)


# --- B1: Bijektion und Umkehrung ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n", range(1, 9))
def test_b1_bijektion_und_umkehrung_n_bis_8(n):
    """n! verschiedene Paare (P, Q), Rückwärts-Einfügen liefert jede Folge zurück, Folgen je Form = f² (alle Formen)."""
    auf = E.aufzaehlen(n)
    assert auf["paare"] == math.factorial(n) and auf["umkehrung_ok"]
    assert auf["formen"] == {lam: H.f_haken(lam) ** 2 for lam in H.partitionen(n)}
    assert len(auf["formen"]) == [1, 2, 3, 5, 7, 11, 15, 22][n - 1]


@pytest.mark.slow
def test_b1_n9_nur_formenzaehlung():
    tab = E.eingefroren()[9]
    assert tab["formen"] == {lam: H.f_haken(lam) ** 2 for lam in H.partitionen(9)} and len(tab["formen"]) == 30
    assert sum(tab["formen"].values()) == 362880 == math.factorial(9)


# --- B2: Ablesen --------------------------------------------------------------------------------------------------------------------------------

def test_b2_erste_zeile_ist_lis_und_zeilenzahl_ist_lds_fuer_alle_folgen_bis_n7():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            lam = R.form(R.einfuegen(p)[0])
            assert lam[0] == R.lis_laenge(p) and len(lam) == R.lds_laenge(p)


def test_b2_2000_zufallsfolgen_n_12_bis_30_zufalls_seed_101():
    rng = SplitMix64(101)
    for _ in range(2000):
        n = 12 + rng.below(19)
        p = S.folge_modell_u(n, rng)
        P, Q = R.einfuegen(p)
        lam = R.form(P)
        assert lam[0] == R.lis_laenge(p) and len(lam) == R.lds_laenge(p)
        assert R.zurueckrechnen(P, Q) == p


# --- B3: Σ f² = n! und Σ f = Involutionen -------------------------------------------------------------------------------------------------------

def test_b3_summen_bis_n14():
    invol = [1, 2, 4, 10, 26, 76, 232, 764, 2620, 9496, 35696, 140152, 568504, 2390480]
    for n in range(1, 15):
        assert sum(z[2] for z in H.formverteilung(n)) == math.factorial(n)
        assert sum(z[1] for z in H.formverteilung(n)) == invol[n - 1] == H.involutionen(n)
    assert [len(H.formverteilung(n)) for n in range(1, 11)] == [1, 2, 3, 5, 7, 11, 15, 22, 30, 42]
    assert len(H.formverteilung(30)) == 5604


# --- B4: Handfolge -----------------------------------------------------------------------------------------------------------------------------

def test_b4_handfolge():
    p = (1, 3, 6, 2, 5, 4)
    P, Q = R.einfuegen(p)
    assert P == [[1, 2, 4], [3, 5], [6]] and Q == [[1, 2, 3], [4, 5], [6]]
    assert H.f_haken((3, 2, 1)) == 16 and 16 ** 2 == 256 and math.factorial(6) == 720
    assert R.stapel_bilden(p) == [[1], [3, 2], [6, 5, 4]] and R.stapelzahl_verlauf(p) == [1, 2, 3, 3, 3, 3]
    assert not R.ein_stapel_sortiert(p)
    assert dict(Counter(R.form(R.einfuegen(q)[0]) for q in permutations(range(1, 7))))[(3, 2, 1)] == 256
    je_form = {lam: H.f_haken(lam) ** 2 for lam in H.partitionen(6)}
    assert je_form == {(6,): 1, (5, 1): 25, (4, 2): 81, (4, 1, 1): 100, (3, 3): 25, (3, 2, 1): 256, (3, 1, 1, 1): 100, (2, 2, 2): 25, (2, 2, 1, 1): 81, (2, 1, 1, 1, 1): 25, (1,) * 6: 1}


# --- B5: Q liest den Verlauf -------------------------------------------------------------------------------------------------------------------

def _q_verlauf_abweichungen(n):
    abw = 0
    for p in permutations(range(1, n + 1)):
        P, Q, schritte = R.einfuegen_protokoll(p)
        verlauf = R.stapelzahl_verlauf(p)
        for i in range(1, n + 1):
            lam_q = R.form_nach_schritt(Q, i)
            if lam_q != R.form(schritte[i - 1].p_danach) or lam_q[0] != verlauf[i - 1] or len(lam_q) != R.lds_laenge(p[:i]):
                abw += 1
    return abw


def test_b5_q_verlauf_n_bis_7_ohne_abweichung():
    assert sum(_q_verlauf_abweichungen(n) for n in range(1, 8)) == 0


@pytest.mark.slow
def test_b5_q_verlauf_n8_ohne_abweichung():
    assert _q_verlauf_abweichungen(8) == 0


# --- B6: Formverteilung (Modell U, exakt) -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n,formen,top,f,folgen,anteil,top5", [
    (4, 5, ((3, 1), (2, 1, 1)), 3, 9, 37.5, 100.0),
    (6, 11, ((3, 2, 1),), 16, 256, 35.6, 85.8),
    (8, 22, ((4, 2, 1, 1),), 90, 8100, 20.1, 64.7),
    (10, 42, ((4, 3, 2, 1),), 768, 589824, 16.3, 49.2),
    (12, 77, ((5, 3, 2, 1, 1),), 7700, 59290000, 12.4, 39.5),   # 189 430 098 / 479 001 600 = 0,39547: die erste Rechnung nannte 39,6 (aus 0,3955 gerundet)
])
def test_b6_formverteilung(n, formen, top, f, folgen, anteil, top5):
    z = ev.formen_zusammenfassung(n)
    assert (z.formen, z.haeufigste, z.f_haeufigste, z.folgen_haeufigste) == (formen, top, f, folgen)
    assert _rund(z.anteil_haeufigste) == anteil and _rund(z.anteil_top5) == top5 and z.fakultaet == math.factorial(n)


def test_b6_exakte_brueche_und_gleichstaende():
    assert ev.formen_zusammenfassung(10).anteil_haeufigste == Fraction(256, 1575)
    assert ev.formen_zusammenfassung(4).anteil_haeufigste == Fraction(3, 8)
    assert ev.formen_zusammenfassung(3).haeufigste == ((2, 1),) and ev.formen_zusammenfassung(3).folgen_haeufigste == 4
    gleichstand = {n for n in range(2, 13) if len(ev.formen_zusammenfassung(n).haeufigste) > 1}
    assert gleichstand == {2, 4, 7, 9, 11}
    for n in gleichstand:
        top = ev.formen_zusammenfassung(n).haeufigste
        assert len(top) == 2 and R.konjugiert(top[0]) == top[1]
    assert ev.formen_zusammenfassung(7).folgen_haeufigste == 1225 and ev.formen_zusammenfassung(9).folgen_haeufigste == 46656 and ev.formen_zusammenfassung(11).folgen_haeufigste == 5336100
    selbst = {n for n in range(2, 13) if len(ev.formen_zusammenfassung(n).haeufigste) == 1}
    assert selbst == {3, 5, 6, 8, 10, 12} and all(R.konjugiert(ev.formen_zusammenfassung(n).haeufigste[0]) == ev.formen_zusammenfassung(n).haeufigste[0] for n in (6, 10))


def test_b6_erwartungswert_der_ersten_zeile_exakt():
    assert H.erwartete_erste_zeile(4) == Fraction(29, 12) and H.erwartete_erste_zeile(5) == Fraction(67, 24)
    assert [sum(z[0][0] * z[2] for z in H.formverteilung(n)) for n in (4, 5, 6)] == [58, 335, 2261]
    assert round(float(H.erwartete_erste_zeile(10)), 4) == 4.3350 == round(float(H.erwartete_zeilenzahl(10)), 4)


# --- B7: Catalan zweimal, andere Menge ----------------------------------------------------------------------------------------------------------

def test_b7_catalan_ueber_hoechstens_2_zeilen_und_spalten_n_bis_14():
    for n in range(1, 15):
        assert H.folgen_mit_hoechstens_zeilen(n, 2) == H.folgen_mit_hoechstens_spalten(n, 2) == H.catalan(n)
    assert [H.catalan(n) for n in (4, 6, 9, 14)] == [14, 132, 4862, 2674440]


def test_b7_ueberlappung_n_bis_9_zahlenmuster():
    tab = E.eingefroren()
    gemeinsam = [tab[n]["stapel_lis2"] for n in range(1, 10)]
    assert gemeinsam == [1, 2, 4, 7, 11, 16, 22, 29, 37] == [math.comb(n, 2) + 1 for n in range(1, 10)]          # Zahlenmuster, kein Beweis
    assert [tab[n]["stapel_lds2"] for n in range(1, 10)] == [1, 2, 4, 8, 16, 32, 64, 128, 256] == [2 ** (n - 1) for n in range(1, 10)]
    assert [tab[n]["lis2_lds2"] for n in range(1, 10)] == [1, 2, 4, 4, 0, 0, 0, 0, 0]
    assert all(tab[n]["stapel"] == tab[n]["lis2"] == tab[n]["lds2"] == H.catalan(n) for n in range(1, 10))
    n6 = tab[6]
    assert (n6["stapel_lis2"], n6["stapel"] - n6["stapel_lis2"], n6["lis2"] - n6["stapel_lis2"]) == (16, 116, 116) and _rund(Fraction(16, 132)) == 12.1
    assert n6["stapel"] + n6["lis2"] - n6["stapel_lis2"] == 248 and tab[9]["stapel_lis2"] == 37


def test_b7_handbeispiel_n4():
    perms = list(permutations(range(1, 5)))
    stapel = {p for p in perms if R.ein_stapel_sortiert(p)}
    lis2 = {p for p in perms if R.lis_laenge(p) <= 2}
    assert len(stapel) == len(lis2) == 14 and len(stapel & lis2) == 7
    assert R.ein_stapel_sortiert((1, 2, 3, 4)) and R.lis_laenge((1, 2, 3, 4)) == 4
    assert not R.ein_stapel_sortiert((3, 4, 1, 2)) and R.lis_laenge((3, 4, 1, 2)) == 2


# --- B8: Zugfolgen gegen Folgen --------------------------------------------------------------------------------------------------------------

def test_b8_zugfolgen_tabelle():
    soll = {(1, 4): (14, 14), (1, 8): (1430, 1430), (2, 2): (5, 2), (2, 3): (42, 6), (2, 4): (462, 24), (2, 5): (6006, 120), (2, 6): (87516, 720),
            (3, 4): (24024, 24)}
    for (t, n), (zugfolgen, ausgaben) in soll.items():
        erg = Z.zugfolgen_zaehlen(t, n)
        assert (erg.zugfolgen, erg.ausgaben) == (zugfolgen, ausgaben) and zugfolgen == H.hakenzahl_rechteck(t + 1, n), (t, n)
    for (t, n), (zugfolgen, ausgaben) in {(2, 7): (1385670, 5018), (3, 5): (1662804, 120)}.items():      # vorgerechnet; die Neu-Rechnung steht in tests/test_daten.py (langsam)
        fest = ev.zuege_eingefroren()[(t, n)]
        assert (fest["zugfolgen"], fest["ausgaben"]) == (zugfolgen, ausgaben) == (H.hakenzahl_rechteck(t + 1, n), ausgaben)
    assert [H.hakenzahl_rechteck(4, n) for n in (6, 7)] == [140229804, 13672405890]


def test_b8_zugfolgen_je_folge():
    z = ev.zug_tabelle(2, 8)
    assert [round(float(r["je_ausgabe"]), 2) for r in z[:7]] == [1.0, 2.5, 7.0, 19.25, 50.05, 121.55, 276.14]
    assert [round(float(r["je_ausgabe"]), 1) for r in ev.zug_tabelle(3, 8)[3:5]] == [1001.0, 13856.7]
    assert all(r["je_ausgabe"] == 1 for r in ev.zug_tabelle(1, 8))


def test_b8_ausgaben_bei_einem_und_zwei_stapeln():
    assert [Z.zugfolgen_zaehlen(2, n).ausgaben for n in range(1, 7)] == [math.factorial(n) for n in range(1, 7)]
    assert ev.zuege_eingefroren()[(2, 7)]["ausgaben"] == 5018 < math.factorial(7) == 5040
    for n in range(1, 9):
        assert all(not Z.enthaelt_312(a) for a in _ausgaben_eines_stapels(n)) if n <= 6 else True


def _ausgaben_eines_stapels(n):
    erg = Z.zugfolgen_zaehlen(1, n, woerter_bis=2000)
    return [a for _, a in erg.woerter]


# --- B9: Modell V --------------------------------------------------------------------------------------------------------------------------------

def test_b9_vorgerechnete_tabelle_wie_in_der_readme():
    tab = ev.modellv_tabelle()
    assert tab["n"] == 10 and tab["anzahl"] == 20000 and tab["seeds"] == [101, 20261117]
    erwartet = {  # D: (Seed 101: erste Zeile, Zeilenzahl, Form, Folgen mit der häufigsten Form (von 20 000), Formen; Seed 20261117: erste Zeile)
        0.5: (9.388, 1.496, [10], None, 8, 9.397), 1: (8.332, 1.982, [9, 1], None, 17, 8.329), 2: (7.105, 2.466, [8, 2], None, 26, 7.098),
        4: (6.052, 3.024, [6, 3, 1], None, 33, 6.060), 8: (5.314, 3.516, [6, 3, 1], None, 36, 5.302), 16: (4.857, 3.859, [4, 3, 2, 1], None, 37, 4.849),
        None: (4.330, 4.337, [4, 3, 2, 1], None, 39, 4.336)}
    for z in tab["zeilen"]:
        a, b, form, _, formen, zweite = erwartet[z["d"]]
        s = z["seeds"]["101"]
        assert (round(s["mittel_erste_zeile"], 3), round(s["mittel_zeilenzahl"], 3), s["top"], s["formen"]) == (a, b, form, formen)
        assert round(z["seeds"]["20261117"]["mittel_erste_zeile"], 3) == zweite
        assert abs(s["summe_erste_zeile"] / 20000 - s["mittel_erste_zeile"]) < 5e-5 and s["top_anzahl"] / 20000 == s["top_anteil"]
    assert [z["seeds"]["101"]["top_anzahl"] for z in tab["zeilen"]] == [10171, 6795, 4316, 4324, 2959, 2618, 3160]
    assert [z["seeds"]["20261117"]["top_anzahl"] for z in tab["zeilen"]] == [10345, 6730, 4277, 4215, 2831, 2546, 3223]
    assert max(abs(z["seeds"]["101"]["top_anteil"] - z["seeds"]["20261117"]["top_anteil"]) for z in tab["zeilen"]) < 0.009
    assert [z["seeds"]["101"]["mittel_zeilenzahl"] for z in tab["zeilen"]] == sorted(z["seeds"]["101"]["mittel_zeilenzahl"] for z in tab["zeilen"])
    zwischen = max(abs(z["seeds"]["101"]["mittel_erste_zeile"] - z["seeds"]["20261117"]["mittel_erste_zeile"]) for z in tab["zeilen"])
    assert round(zwischen, 3) == 0.012 and zwischen < 0.02


def test_b9_exakter_wert_und_streuung_der_zufallsproben_als_band():
    exakt = float(H.erwartete_erste_zeile(10))
    assert abs(exakt - 4.3350) < 5e-5
    tab = ev.modellv_tabelle()
    u = tab["zeilen"][-1]
    for s in ("101", "20261117"):
        assert abs(u["seeds"][s]["mittel_erste_zeile"] - exakt) < 0.03 and abs(u["seeds"][s]["mittel_zeilenzahl"] - exakt) < 0.03
        assert abs(u["seeds"][s]["top_anteil"] - 256 / 1575) < 0.01


def test_b9_neu_gerechnet_die_ersten_2000_folgen_als_band():
    tab = ev.modellv_tabelle()
    for d in (0.5, None):
        stat = ev.modellv_statistik(10, d, 2000, 101)
        zeile = next(z for z in tab["zeilen"] if z["d"] == d)["seeds"]["101"]
        assert abs(stat["mittel_erste_zeile"] - zeile["mittel_erste_zeile"]) < 0.08 and abs(stat["mittel_zeilenzahl"] - zeile["mittel_zeilenzahl"]) < 0.08
        assert tuple(zeile["top"]) == stat["top"] and abs(stat["top_anteil"] - zeile["top_anteil"]) < 0.04


def test_b9_modell_v_monoton_in_d():
    tab = ev.modellv_tabelle()
    erste = [z["seeds"]["101"]["mittel_erste_zeile"] for z in tab["zeilen"]]
    zeilenzahl = [z["seeds"]["101"]["mittel_zeilenzahl"] for z in tab["zeilen"]]
    assert erste == sorted(erste, reverse=True) and zeilenzahl == sorted(zeilenzahl)
    assert [z["seeds"]["101"]["formen"] for z in tab["zeilen"]] == [8, 17, 26, 33, 36, 37, 39]


# --- B10: Wörter mit Zielgruppen ----------------------------------------------------------------------------------------------------------------

def test_b10_woerter_zahlen():
    soll_woerter = {(2, 2, 2): 90, (3, 2, 1): 60, (2, 2, 1, 1): 180, (2, 1, 1, 1): 60, (3, 3): 20, (2, 2, 2, 1): 630, (1, 1, 1, 1, 1): 120}
    for inhalt, anzahl in soll_woerter.items():
        assert W.zahl_woerter(inhalt) == len(W.woerter_zu_inhalt(inhalt)) == anzahl
    je = {z[0]: (z[1], z[2], z[3]) for z in W.woerter_je_form((2, 2, 2))}
    assert je == {(3, 3): (5, 1, 5), (3, 2, 1): (16, 2, 32), (3, 1, 1, 1): (10, 1, 10), (2, 2, 2): (5, 1, 5), (2, 2, 1, 1): (9, 3, 27), (2, 1, 1, 1, 1): (5, 2, 10), (1,) * 6: (1, 1, 1)}
    assert sum(v[2] for v in je.values()) == 90


def test_b10_streng_gegen_schwach():
    soll = {(2, 2, 2): 74, (3, 2, 1): 55, (2, 2, 1, 1): 111, (2, 2, 2, 1): 463}
    for inhalt, anzahl in soll.items():
        a = ev.analysiere_wort(inhalt, S.standardwort(inhalt), True)
        assert a.verschieden == anzahl and a.anzahl_woerter == W.zahl_woerter(inhalt)
    a = ev.analysiere_wort((2, 2, 2), (1, 1, 2, 2, 3, 3), True)
    assert (a.lis_streng, a.lis_schwach) == (3, 6)
    assert (R.lis_laenge((1, 1, 2, 2), True), R.lis_laenge((1, 1, 2, 2), False)) == (2, 4)
    assert W.mindestzahl_stapel_probieren((2, 1, 2, 3, 1)) == 3 and R.form(R.einfuegen((2, 1, 2, 3, 1), dual=True)[0]) == (3, 1, 1)


@pytest.mark.parametrize("inhalt", [(2, 2, 2), (3, 2, 1), (2, 2, 1, 1), (2, 1, 1, 1), (3, 3), (2, 2, 2, 1), (1, 1, 1, 1, 1)])
def test_b10_erste_zeile_ist_mindestzahl_stapel_und_f_mal_kostka(inhalt):
    for dual in (True, False):
        a = ev.analysiere_wort(inhalt, S.standardwort(inhalt), dual)
        assert all(z[3] == z[4] for z in a.je_form) and sum(z[4] for z in a.je_form) == a.anzahl_woerter
    for w in W.woerter_zu_inhalt(inhalt):
        assert len(R.einfuegen(w, dual=True)[0][0]) == W.mindestzahl_stapel_probieren(w, True)
        assert len(R.einfuegen(w, dual=False)[0][0]) == W.mindestzahl_stapel_probieren(w, False)


# --- B11: Involutionen -------------------------------------------------------------------------------------------------------------------------

def _involutionen_abweichungen(n):
    abw = 0
    zahl = 0
    for p in permutations(range(1, n + 1)):
        P, Q = R.einfuegen(p)
        invol = all(p[p[i] - 1] == i + 1 for i in range(n))
        zahl += invol
        if (P == Q) != invol:
            abw += 1
        if invol and sum(1 for i in range(n) if p[i] == i + 1) != sum(1 for c in R.konjugiert(R.form(P)) if c % 2):
            abw += 1
    return abw, zahl


def test_b11_involutionen_n_bis_7():
    assert [_involutionen_abweichungen(n) for n in range(1, 8)] == [(0, z) for z in (1, 2, 4, 10, 26, 76, 232)]


@pytest.mark.slow
def test_b11_involutionen_n8():
    assert _involutionen_abweichungen(8) == (0, 764)


# --- B12: Eigenschaften (je 30 bis 50 Zufallsfolgen, tests/test_eigenschaften_tableaux_rsk.py) -----------------------------------------------------

def test_b12_eigenschaften_stehen_in_der_eigenen_datei():
    text = (ROOT / "tests" / "test_eigenschaften_tableaux_rsk.py").read_text(encoding="utf-8")
    for stichwort in ("monotone_umbenennung", "spiegeln_der_folge", "komplement", "inverse_folge", "neues_groesstes", "neues_kleinstes", "form_von_q_bis_i"):
        assert stichwort in text


# --- Dateien und Texte ------------------------------------------------------------------------------------------------------------------------

def test_daten_dateien_sind_gueltiges_json():
    for name in ("trk_formen.json", "trk_zuege.json", "trk_modellv.json"):
        assert json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))["erzeugt_von"].startswith("tools/trk_make_")
