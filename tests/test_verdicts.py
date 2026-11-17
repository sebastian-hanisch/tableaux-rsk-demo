"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Art (success, info, warning, error) steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text). Die Zahlen unten sind von Hand gerechnet (Handfolge: Form (3,2,1), f = 16, 16² = 256 von 720; (3,4,1,2): Form (2,2), f = 2,
4 von 24; n = 4: Formen (3,1) und (2,1,1) mit je 9 von 24 = 37,5 %; zwei Stapel n = 4: 462 Zugfolgen, 24 Folgen, 462/24 = 19,25)."""

import trk_enum as E
import trk_evaluation as ev
import trk_haken as H
import trk_rsk as R
from trk_texts import ganz, prozent


def test_einfuegen_handfolge_fallend():
    art, text = ev.verdict_einfuegen(ev.analysiere_folge((1, 3, 6, 2, 5, 4)))
    assert art == "success"
    for stueck in ("(1, 3, 6, 2, 5, 4): Form (3,2,1), f = 16", "256 von 720 Folgen der Länge 6 haben diese Form", "Erste Zeile 3 = längste wachsende Teilfolge",
                   "Mindestzahl **fallender** Stapel ([1] [3, 2] [6, 5, 4])", "Zeilenzahl 3 = längste fallende Teilfolge", "Die Umkehrung liefert die Folge zurück",
                   "Stapelzahl nach 1 bis 6 Ankünften: 1, 2, 3, 3, 3, 3", "sortiert die Folge nicht (sie enthält das Muster 231)"):
        assert stueck in text, stueck


def test_einfuegen_wachsende_stapel_liest_die_spalte():
    art, text = ev.verdict_einfuegen(ev.analysiere_folge((1, 3, 6, 2, 5, 4), fallend=False))
    assert art == "success"
    assert "Erste Spalte (= Zeilenzahl) 3 = längste fallende Teilfolge = Mindestzahl **wachsender** Stapel ([1, 3, 6] [2, 5] [4])" in text
    assert "Stapelzahl nach 1 bis 6 Ankünften: 1, 1, 1, 2, 2, 3" in text


def test_einfuegen_ein_stapel_sortiert_und_einzahl():
    art, text = ev.verdict_einfuegen(ev.analysiere_folge((3, 4, 1, 2)))
    assert "Form (2,2), f = 2" in text and "4 von 24 Folgen der Länge 4 haben" in text and "[3, 1] [4, 2]" in text and "Stapelzahl nach 1 bis 4 Ankünften: 1, 2, 2, 2" in text
    art, text = ev.verdict_einfuegen(ev.analysiere_folge((1, 2, 3)))
    assert "Ein einziger Stapel sortiert die Folge." in text and "Form (3), f = 1" in text and "1 von 6 Folgen der Länge 3 hat diese Form" in text
    art, text = ev.verdict_einfuegen(ev.analysiere_folge((1,)))
    assert "1 von 1 Folge der Länge 1 hat diese Form" in text


def test_einfuegen_meldet_fehler_bei_widerspruch():
    a = ev.analysiere_folge((1, 3, 6, 2, 5, 4))
    kaputt = ev.FolgeAnalyse(**{**a.__dict__, "umkehrung_ok": False})
    assert ev.verdict_einfuegen(kaputt)[0] == "error" and "FEHLER" in ev.verdict_einfuegen(kaputt)[1]
    anders = ev.FolgeAnalyse(**{**a.__dict__, "q_verlauf": (1, 2, 3, 3, 3, 2)})
    assert ev.verdict_einfuegen(anders)[0] == "error"


def test_formen_n4_gleichstand_und_aufzaehlung():
    art, text = ev.verdict_formen(ev.formen_zusammenfassung(4), E.aufzaehlen(4))
    assert art == "info"
    for stueck in ("Länge n = 4: 5 Formen", "am häufigsten sind (3,1) und (2,1,1) mit je 9 von 24 Folgen (37,5 %", "Summe der f² = 24 = 4!", "Summe der f = 10",
                   "Catalan(4) = 14 Folgen", "Ein Stapel sortiert ebenfalls 14 Folgen (aufgezählt)", "nur 7", "Aufzählung aller 24 Folgen: 5 Formen, jede mit genau f² Folgen, 24 Paare"):
        assert stueck in text, stueck
    assert "fünf häufigsten" not in text            # bei genau 5 Formen gäbe der Satz nichts her


def test_formen_n6_und_n10_nennen_die_fuenf_haeufigsten():
    _, t6 = ev.verdict_formen(ev.formen_zusammenfassung(6), E.aufzaehlen(6))
    assert "11 Formen" in t6 and "am häufigsten ist (3,2,1) mit 256 von 720 Folgen (35,6 %)" in t6 and "zusammen: 85,8 %" in t6 and "Catalan(6) = 132" in t6 and "nur 16" in t6
    _, t10 = ev.verdict_formen(ev.formen_zusammenfassung(10))
    assert "42 Formen" in t10 and f"{ganz(589824)} von {ganz(3628800)} Folgen (16,3 %)" in t10 and "zusammen: 49,2 %" in t10 and "Aufzählung" not in t10 and "Ein Stapel" not in t10


def test_formen_n9_aus_tabelle_ist_als_vorgerechnet_gekennzeichnet():
    _, text = ev.verdict_formen(ev.formen_zusammenfassung(9), E.eingefroren()[9], live=False)
    assert "vorgerechnet aufgezählt" in text and "nur 37" in text and "Aufzählung aller" not in text


def test_formen_widerspruch_zur_hakenformel_wird_gemeldet():
    auf = dict(E.aufzaehlen(4))
    auf["paare"] = 23
    assert ev.verdict_formen(ev.formen_zusammenfassung(4), auf)[0] == "error"


def test_formen_kleine_laengen_ohne_ueberlappungsbehauptung():
    _, text = ev.verdict_formen(ev.formen_zusammenfassung(2), E.aufzaehlen(2))
    assert "dieselben Folgen wie bei „höchstens 2 Spalten“" in text and "eine andere Menge" not in text


def test_zugfolgen_verdikte():
    z1 = ev.zug_tabelle(1, 8)
    art, text = ev.verdict_zuege(z1, 1, 4)
    assert art == "info" and "14 Zugfolgen" in text and "14 verschiedene Folgen" in text and "je Folge genau eine Zugfolge" in text and "scharf" in text
    z2 = ev.zug_tabelle(2, 8)
    art, text = ev.verdict_zuege(z2, 2, 4)
    assert art == "warning" and "462 Zugfolgen" in text and "Rechtecks 3 × 4: 462" in text and "24 verschiedene Folgen" in text and "19,25 Zugfolgen je Folge" in text
    assert "wächst von 2,50 (n = 2) auf 276,14 (n = 7)" in text
    art, text = ev.verdict_zuege(z2, 2, 7)
    assert f"{ganz(1385670)} Zugfolgen (vorgerechnet" in text and "5018 verschiedene Folgen" in text and "276,14" in text
    art, text = ev.verdict_zuege(z2, 2, 1)
    assert art == "info" and "nur eine Folge" in text
    assert "nur die Hakenformel" in ev.verdict_zuege(z2, 2, 8)[1]


def test_kernfragen_kurzantworten():
    assert ev.kernfrage_1(ev.analysiere_folge((1, 3, 6, 2, 5, 4)))[1].startswith("Aus (1, 3, 6, 2, 5, 4) werden zwei Tableaux P und Q der Form (3,2,1); die erste Zeile (3) ist die Mindestzahl fallender")
    assert "die erste Spalte (3) ist die Mindestzahl wachsender Stapel" in ev.kernfrage_1(ev.analysiere_folge((1, 3, 6, 2, 5, 4), False))[1]
    art, text = ev.kernfrage_2(ev.formen_zusammenfassung(6))
    assert "11 Formen" in text and "(3,2,1) hat mit 256 von 720 Folgen (35,6 %)" in text and "Summe 720 = 6!" in text
    assert "(4,2,1) und (3,2,1,1) haben mit je 1225 von 5040 Folgen" in ev.kernfrage_2(ev.formen_zusammenfassung(7))[1]
    assert ev.kernfrage_3(ev.zug_tabelle(2, 8), 2, 4) == ("warning", "t = 2, n = 4: 462 Zugfolgen, aber nur 24 verschiedene Folgen als Ausgabe.")
    assert ev.kernfrage_3(ev.zug_tabelle(1, 8), 1, 4)[0] == "info" and "genau eine Zugfolge" in ev.kernfrage_3(ev.zug_tabelle(1, 8), 1, 4)[1]
    assert "nicht aufgezählt" in ev.kernfrage_3(ev.zug_tabelle(2, 8), 2, 8)[1]


def test_woerter_verdikt_beide_fassungen():
    art, text = ev.verdict_woerter(ev.analysiere_wort((2, 2, 2), (1, 3, 2, 2, 3, 1), True))
    assert art == "success"
    for stueck in ("Form (3,1,1,1)", "erste Zeile 3 = längste **streng** wachsende Teilfolge", "Alle 90 Wörter dieses Inhalts = 6!/(2! · 2! · 2!)", "Form (3,2,1): 32 = 16 · 2, gezählt 32",
                   "bei 74 von 90 Wörtern", "längste **schwach** wachsende Teilfolge, 4"):
        assert stueck in text, stueck
    art, text = ev.verdict_woerter(ev.analysiere_wort((2, 2, 2), (1, 3, 2, 2, 3, 1), False))
    assert art == "success" and "Form (4,1,1)" in text and "erste Zeile 4 = längste **schwach** wachsende Teilfolge = Mindestzahl **streng** fallender Stapel" in text
    assert "längste **streng** wachsende Teilfolge, 3" in text


def test_woerter_verdikt_meldet_widerspruch():
    a = ev.analysiere_wort((2, 1), (1, 2, 1), True)
    kaputt = ev.WortAnalyse(**{**a.__dict__, "probiert_schwach": 99})
    assert ev.verdict_woerter(kaputt)[0] == "error"


def test_modellv_verdikte_aus_den_zeilen():
    tab = {"n": 10, "anzahl": 20000, "seeds": [1, 2], "zeilen": [
        {"d": 0.5, "seeds": {"1": {"mittel_erste_zeile": 9.5, "mittel_zeilenzahl": 1.5, "top": [10], "top_anteil": 0.5, "formen": 8},
                             "2": {"mittel_erste_zeile": 9.4, "mittel_zeilenzahl": 1.5, "top": [10], "top_anteil": 0.5, "formen": 8}}},
        {"d": None, "seeds": {"1": {"mittel_erste_zeile": 4.25, "mittel_zeilenzahl": 4.25, "top": [4, 3, 2, 1], "top_anteil": 0.25, "formen": 39},
                              "2": {"mittel_erste_zeile": 4.3, "mittel_zeilenzahl": 4.3, "top": [4, 3, 2, 1], "top_anteil": 0.25, "formen": 39}}}]}
    art, text = ev.verdict_modellv_tabelle(tab)
    assert art == "info"
    for stueck in ("n = 10, je 20\xa0000 Folgen (Zufalls-Seed 1", "bei D = 0,5 hat 50,00 % der Folgen die Form (10)", "bei D = ∞ ist (4,3,2,1) mit 25,00 % am häufigsten",
                   "exakt im Modell U 16,25 % für (4,3,2,1)", "Mittlere erste Zeile 9,50 gegen 4,25 (exakt im Modell U 4,3350)", "um höchstens 0,100"):
        assert stueck in text, stueck


def test_modellv_live_verdikt():
    stat = {"anzahl": 1000, "mittel_erste_zeile": 6.04, "se_erste_zeile": 0.03, "mittel_zeilenzahl": 3.0, "top": (6, 3, 1), "top_anteil": 0.216, "formen_gesehen": 33}
    art, text = ev.verdict_modellv_live(stat, 10, 4, 101)
    assert art == "info" and "D = 4, n = 10, 1000 Folgen, Zufalls-Seed 101" in text and "6,04 ± 0,030" in text and "(6,3,1) mit 21,6 %" in text and "33 von 42 Formen" in text
    assert "exakt 4,3350" in text


def test_zahlenschreibweise():
    assert ganz(1385670) == "1\xa0385\xa0670" and ganz(5018) == "5018" and ganz(-12345) == "−12\xa0345"
    assert prozent(H.formverteilung(10)[0][3]) == "16,3 %" and prozent(0.5) == "50,0 %"
    assert R.form(R.einfuegen((2, 1, 3))[0]) == (2, 1)
