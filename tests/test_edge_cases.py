"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): leere Folge, n = 1, n = 2, sortiert und absteigend, Gleichstände, Werte außerhalb 1 bis n,
Wörter mit einer einzigen Zielgruppe, Zugfolgen ohne Container, Grenzen der Live-Rechnung, Hakenformel bei n = 30."""

import math

import pytest

import trk_enum as E
import trk_evaluation as ev
import trk_haken as H
import trk_rsk as R
import trk_scenario as S
import trk_woerter as W
import trk_zuege as Z


def test_leere_folge_hat_leere_tableaux_und_form():
    P, Q = R.einfuegen(())
    assert P == [] and Q == [] and R.form(P) == () and R.zurueckrechnen(P, Q) == ()
    assert R.lis_laenge(()) == 0 and R.lds_laenge(()) == 0 and R.stapel_bilden(()) == [] and R.stapelzahl_verlauf(()) == []
    assert R.ein_stapel_sortiert(())


def test_eine_folge_aus_einem_wert():
    a = ev.analysiere_folge((1,))
    assert a.form == (1,) and a.f == 1 and a.folgen_dieser_form == 1 and a.fakultaet == 1 and a.verlauf == (1,) and a.q_verlauf == (1,) and a.umkehrung_ok


def test_genau_zwei_werte():
    assert R.einfuegen((1, 2)) == ([[1, 2]], [[1, 2]])
    assert R.einfuegen((2, 1)) == ([[1], [2]], [[1], [2]])
    assert ev.analysiere_folge((2, 1)).form == (1, 1) and ev.analysiere_folge((1, 2)).form == (2,)


@pytest.mark.parametrize("n", (3, 8, 12))
def test_sortiert_aufsteigend_und_absteigend(n):
    auf = tuple(range(1, n + 1))
    ab = auf[::-1]
    assert R.form(R.einfuegen(auf)[0]) == (n,) and R.form(R.einfuegen(ab)[0]) == (1,) * n
    a = ev.analysiere_folge(auf, fallend=True)
    assert a.stapelzahl == n and a.ein_stapel and a.verlauf == tuple(range(1, n + 1))
    b = ev.analysiere_folge(ab, fallend=True)
    assert b.stapelzahl == 1 and b.ein_stapel          # absteigend: ein fallender Stapel, und ein einziger Stapel sortiert sie auch (kein Muster 231)
    assert ev.analysiere_folge(ab, fallend=False).stapelzahl == n


def test_werte_ausserhalb_von_1_bis_n_werden_auf_raenge_umgerechnet():
    folge, hinweis, fehler = S.folge_einlesen("100 7 55", 12)
    assert folge == (3, 1, 2) and hinweis and not fehler
    folge, hinweis, fehler = S.folge_einlesen("-5 0 5", 12)
    assert folge == (1, 2, 3) and hinweis


def test_gleichstaende_im_permutationsmodus_werden_abgewiesen():
    folge, hinweis, fehler = S.folge_einlesen("3 1 3", 12)
    assert folge is None and "Experiment 5" in fehler


def test_zu_lange_und_ungueltige_eingaben():
    assert S.folge_einlesen(" ".join(str(i) for i in range(1, 14)), 12)[2]
    assert S.folge_einlesen(" ".join(str(i) for i in range(1, 13)), 12)[0] == tuple(range(1, 13))
    assert S.folge_einlesen("1 x 3", 12)[2]
    assert S.folge_einlesen("1,2;3", 12)[0] == (1, 2, 3)


def test_wort_mit_einer_einzigen_zielgruppe():
    a = ev.analysiere_wort((3,), (1, 1, 1), dual=True)
    assert a.form == (1, 1, 1) and a.erste_zeile == 1 and a.anzahl_woerter == 1 and a.lis_streng == 1 and a.lis_schwach == 3
    assert len(a.stapel_schwach) == 1 and len(a.stapel_streng) == 3 and a.probiert_schwach == 1 and a.probiert_streng == 3
    b = ev.analysiere_wort((3,), (1, 1, 1), dual=False)
    assert b.form == (3,)


def test_inhalt_mit_einer_gruppe_und_leeres_wort():
    assert W.woerter_zu_inhalt((2,)) == [(1, 1)] and W.zahl_woerter((2,)) == 1
    assert W.mindestzahl_stapel_probieren(()) == 0
    assert W.kostka((), ()) == 1 and W.kostka((1,), ()) == 0


def test_zugfolgen_ohne_container_und_ungueltige_stapelzahl():
    erg = Z.zugfolgen_zaehlen(2, 0)
    assert (erg.zugfolgen, erg.ausgaben) == (1, 1)
    with pytest.raises(ValueError):
        Z.zugfolgen_zaehlen(0, 3)
    with pytest.raises(ValueError):
        Z.zugfolgen_zaehlen(1, -1)


def test_ueber_der_live_grenze_gibt_es_nur_noch_hakenformel_oder_vorgerechnetes():
    zeilen = ev.zug_tabelle(3, 8)
    quellen = [z["quelle"] for z in zeilen]
    assert quellen == ["aufgezählt"] * 4 + ["vorgerechnet"] + ["nur Hakenformel"] * 3
    assert zeilen[5]["zugfolgen"] is None and zeilen[5]["haken"] == 140229804 and zeilen[6]["haken"] == 13672405890
    art, text = ev.verdict_zuege(zeilen, 3, 6)
    assert art == "info" and "nur die Hakenformel" in text and "140" in text
    assert ev.zug_tabelle(2, 8)[6]["quelle"] == "vorgerechnet" and ev.zug_tabelle(2, 8)[7]["quelle"] == "nur Hakenformel"


def test_hakenformel_bei_n_30_ist_ganzzahlig_und_vollstaendig():
    zeilen = H.formverteilung(30)
    assert len(zeilen) == 5604
    assert sum(z[2] for z in zeilen) == math.factorial(30) and sum(z[3] for z in zeilen) == 1
    assert all(isinstance(z[1], int) for z in zeilen)


def test_n_grenzen_der_formverteilung():
    z = ev.formen_zusammenfassung(2)
    assert z.formen == 2 and z.haeufigste == ((2,), (1, 1)) and z.folgen_haeufigste == 1
    z1 = ev.formen_zusammenfassung(1)
    assert z1.formen == 1 and z1.haeufigste == ((1,),) and z1.anteil_haeufigste == 1


def test_aufzaehlung_fuer_n9_kommt_aus_der_tabelle():
    tab = E.eingefroren()
    assert tab is not None and sorted(tab) == list(range(1, 10))
    assert E.ueberlappung(9)["stapel_lis2"] == 37 and E.ueberlappung(8)["stapel_lis2"] == 29
