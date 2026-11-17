"""Handbeispiele (DEMO-PLAYBOOK §1b): jede Einheit an einer Mini-Instanz, die von Hand nachgerechnet ist. Die Erwartungswerte stehen als Rechnung da, nicht als Abschrift des Codes.

Handfolge n = 6, Schritt für Schritt (Zeile 1 oben):
  1: [1]                        2: [1 3]                  3: [1 3 6]
  4: die 2 verdrängt die 3 -> [1 2 6] / [3]
  5: die 5 verdrängt die 6 -> [1 2 5], die 6 kommt ans Ende von Zeile 2 -> [3 6]
  6: die 4 verdrängt die 5 -> [1 2 4]; die 5 verdrängt die 6 aus Zeile 2 -> [3 5]; die 6 beginnt Zeile 3.
Haken von (3,2,1): 5 3 1 / 3 1 / 1, f = 720 / 45 = 16, also 16² = 256 Folgen mit dieser Form."""

import math
from fractions import Fraction

import pytest

import trk_haken as H
import trk_rsk as R
import trk_scenario as S
import trk_woerter as W
import trk_zuege as Z


def test_einfuegen_der_handfolge_schritt_fuer_schritt(hand):
    P, Q, schritte = R.einfuegen_protokoll(hand)
    assert [s.p_danach for s in schritte] == [
        ((1,),), ((1, 3),), ((1, 3, 6),), ((1, 2, 6), (3,)), ((1, 2, 5), (3, 6)), ((1, 2, 4), (3, 5), (6,)),
    ]
    assert P == [[1, 2, 4], [3, 5], [6]] and Q == [[1, 2, 3], [4, 5], [6]]
    assert R.form(P) == R.form(Q) == (3, 2, 1)
    assert schritte[3].verdraengungen == ((0, 1, 2, 3), (1, 0, 3, None)) and schritte[3].neue_zelle == (1, 0)
    assert schritte[5].neue_zelle == (2, 0)


def test_hakenformel_von_hand():
    assert H.hakenlaengen((3, 2, 1)) == [[5, 3, 1], [3, 1], [1]]
    assert H.f_haken((3, 2, 1)) == 720 // (5 * 3 * 1 * 3 * 1 * 1) == 16
    assert H.f_haken((3, 2, 1)) ** 2 == 256


def test_zurueckrechnen_der_handfolge(hand):
    P, Q = R.einfuegen(hand)
    folge, rueck = R.zurueckrechnen_protokoll(P, Q)
    assert folge == hand
    # von Hand: der letzte Schritt schuf die Zelle (Zeile 3, Spalte 1); die 6 geht nach Zeile 2 (ersetzt die 5), die 5 nach Zeile 1 (ersetzt die 4), die 4 fällt heraus
    assert rueck[0].zelle == (2, 0) and rueck[0].wert == 4
    assert rueck[0].weg == ((2, 0, 6, None), (1, 1, 6, 5), (0, 2, 5, 4))
    assert rueck[0].p_danach == ((1, 2, 5), (3, 6))


def test_ablesen_und_stapel_der_handfolge(hand):
    assert R.lis_laenge(hand) == 3 and R.lds_laenge(hand) == 3
    assert R.stapel_bilden(hand) == [[1], [3, 2], [6, 5, 4]]
    assert R.stapelzahl_verlauf(hand) == [1, 2, 3, 3, 3, 3]
    P, Q = R.einfuegen(hand)
    assert [R.form_nach_schritt(Q, i) for i in range(1, 7)] == [(1,), (2,), (3,), (3, 1), (3, 2), (3, 2, 1)]
    assert not R.ein_stapel_sortiert(hand)          # 3, 6, 2 ist ein Muster 231
    # wachsende Stapel (Spitze kleiner): 1 3 6 | 2 5 | 4, drei Stapel = längste fallende Teilfolge (6, 5, 4)
    assert R.stapel_bilden(hand, fallend=False) == [[1, 3, 6], [2, 5], [4]]


def test_n4_alle_24_folgen_zum_nachzaehlen():
    from collections import Counter
    from itertools import permutations
    je_form = Counter(R.form(R.einfuegen(p)[0]) for p in permutations(range(1, 5)))
    assert dict(je_form) == {(4,): 1, (3, 1): 9, (2, 2): 4, (2, 1, 1): 9, (1, 1, 1, 1): 1}
    f = {lam: H.f_haken(lam) for lam in H.partitionen(4)}
    assert f == {(4,): 1, (3, 1): 3, (2, 2): 2, (2, 1, 1): 3, (1, 1, 1, 1): 1}
    assert sum(x * x for x in f.values()) == 1 + 9 + 4 + 9 + 1 == 24
    assert sum(f.values()) == 10
    assert H.formverteilung(4)[0][3] == Fraction(3, 8)


def test_catalan_zweimal_n4():
    assert 1 + 9 + 4 == H.folgen_mit_hoechstens_zeilen(4, 2) == 14 == H.catalan(4)
    assert 4 + 9 + 1 == H.folgen_mit_hoechstens_spalten(4, 2) == 14


def test_zugfolgen_zwei_stapel_n2_von_hand():
    erg = Z.zugfolgen_zaehlen(2, 2, woerter_bis=10)
    assert [w for w, _ in erg.woerter] == ["aabbcc", "aabcbc", "ababcc", "abacbc", "abcabc"]
    assert dict(erg.woerter) == {"aabbcc": (1, 2), "aabcbc": (2, 1), "ababcc": (2, 1), "abacbc": (1, 2), "abcabc": (1, 2)}
    assert (erg.zugfolgen, erg.ausgaben) == (5, 2)
    assert H.hakenzahl_rechteck(3, 2) == 720 // (4 * 3 * 3 * 2 * 2 * 1) == 5
    n3 = Z.zugfolgen_zaehlen(2, 3)
    assert (n3.zugfolgen, n3.ausgaben) == (362880 // 8640, 6) == (42, 6)


def test_zugfolgen_ein_stapel_n3():
    erg = Z.zugfolgen_zaehlen(1, 3)
    assert (erg.zugfolgen, erg.ausgaben) == (5, 5)


def test_woerter_handwort_duale_einfuegung():
    w = (2, 1, 2, 3, 1)
    P, Q = R.einfuegen(w, dual=True)
    assert P == [[1, 2, 3], [1], [2]] and Q == [[1, 3, 4], [2], [5]]
    assert R.zurueckrechnen(P, Q, dual=True) == w
    P2, _ = R.einfuegen(w, dual=False)
    assert P2 == [[1, 1, 3], [2, 2]]
    assert (R.lis_laenge((1, 1, 2, 2), True), R.lis_laenge((1, 1, 2, 2), False)) == (2, 4)
    assert W.mindestzahl_stapel_probieren((1, 1, 2, 2)) == 2 and W.mindestzahl_stapel_probieren((1, 1, 2, 2), schwach=False) == 4


def test_woerter_inhalt_2_1():
    assert sorted(W.woerter_zu_inhalt((2, 1))) == [(1, 1, 2), (1, 2, 1), (2, 1, 1)]
    assert W.kostka((2, 1), (2, 1)) == 1 and W.kostka((1, 1, 1), (2, 1)) == 0 and W.kostka((3,), (2, 1)) == 1
    zeilen = {z[0]: z[3] for z in W.woerter_je_form((2, 1))}
    assert zeilen == {(2, 1): 2, (1, 1, 1): 1}


def test_bruchwerte_der_erwartung():
    assert H.erwartete_erste_zeile(4) == Fraction(58, 24) == Fraction(29, 12)
    assert H.erwartete_erste_zeile(5) == Fraction(335, 120) == Fraction(67, 24)
    assert sum(z[0][0] * z[2] for z in H.formverteilung(6)) == 2261
    top = H.formverteilung(10)[0]
    assert top[0] == (4, 3, 2, 1) and top[1] == 768 and top[3] == Fraction(256, 1575)


def test_standardisieren_und_einlesen():
    assert S.folge_einlesen("1 3 6 2 5 4", 12) == ((1, 3, 6, 2, 5, 4), None, None)
    folge, hinweis, fehler = S.folge_einlesen("10, 30 60 20", 12)
    assert folge == (1, 3, 4, 2) and "Ränge" in hinweis and fehler is None
    assert S.folge_einlesen("1 2 2", 12)[2] and "Experiment 5" in S.folge_einlesen("1 2 2", 12)[2]
    assert S.folge_einlesen("", 12)[2] and S.folge_einlesen("a b", 12)[2] and S.folge_einlesen("1 " * 13, 12)[2]
    assert S.standardwort((3, 2, 1)) == (1, 2, 3, 1, 2, 1)
    assert S.wort_einlesen("1 2 1 3 2 1", (3, 2, 1)) == ((1, 2, 1, 3, 2, 1), None)
    assert S.wort_einlesen("1 2 3", (3, 2, 1))[0] is None


def test_rng_splitmix64_referenzwerte():
    import trk_rng as RNG
    g = RNG.SplitMix64(0)
    assert [g.next_u64() for _ in range(3)] == [16294208416658607535, 7960286522194355700, 487617019471545679]   # Referenzfolge von SplitMix64 mit Seed 0
    assert RNG.SplitMix64(7).below(10) == RNG.SplitMix64(7).below(10)
    assert sorted(S.zufallsfolge(9, 5)) == list(range(1, 10)) and S.zufallsfolge(9, 5) == S.zufallsfolge(9, 5)
    p = S.folge_modell_v(10, 4, RNG.SplitMix64(3))
    assert sorted(p) == list(range(1, 11))


def test_fakultaet_der_summen():
    assert [sum(z[2] for z in H.formverteilung(n)) for n in range(1, 8)] == [math.factorial(n) for n in range(1, 8)]
