"""Orakel-Tests (ORACLE-PLAYBOOK §1, DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg.

* Einfügen und Umkehrung gegen die **unabhängige Aufzählung aller Standardtableaux** (jedes Paar gleichförmiger Standardtableaux ist genau ein Bild; n ≤ 6),
* erste Zeile und Zeilenzahl gegen das Probieren aller Teilmengen (n ≤ 6) und gegen ein O(n²)-Programm (n ≤ 8),
* Hakenformel gegen die Eckenrekursion (alle Formen n ≤ 14) und gegen die Aufzählung (Folgen je Form, n ≤ 8; n = 9 im langsamen Test),
* Zugfolgen: Stapelsimulation gegen Ballot-Wörter gegen Hakenformel des Rechtecks,
* Kostka-Zahlen gegen das Füllen Zelle für Zelle, Mindestzahl Stapel gegen eine Suche über alle Stapelspitzen-Zustände,
* ein Stapel (231), Ausgaben eines Stapels (312), Überlappungszahlen gegen Mustersuche.

Die Referenzen stehen in dieser Datei und benutzen nichts aus den Hilfsmodulen der Demo außer dem Prüfling selbst."""

import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations

import pytest

import trk_enum as E
import trk_haken as H
import trk_rsk as R
import trk_woerter as W
import trk_zuege as Z


# --- Referenzen (anderer Rechenweg) -------------------------------------------------------------------------------------------------------------

def partitionen_ref(n, maxteil=None):
    maxteil = n if maxteil is None else maxteil
    if n == 0:
        return [()]
    return [(k,) + rest for k in range(min(n, maxteil), 0, -1) for rest in partitionen_ref(n - k, k)]


@lru_cache(maxsize=None)
def f_ecken(lam):
    """Zahl der Standardtableaux durch die Eckenrekursion: die größte Zahl steht in einer Ecke."""
    if not lam:
        return 1
    gesamt = 0
    for i in range(len(lam)):
        if lam[i] > 0 and (i + 1 == len(lam) or lam[i + 1] < lam[i]):
            neu = list(lam)
            neu[i] -= 1
            gesamt += f_ecken(tuple(x for x in neu if x > 0))
    return gesamt


def alle_syt(lam):
    """Alle Standardtableaux der Form lam: die Zahlen 1, 2, ... der Reihe nach in eine Zelle setzen, die nach rechts und unten Platz lässt."""
    n = sum(lam)
    erg = []
    zeilen = [[] for _ in lam]

    def rek(k):
        if k > n:
            erg.append(tuple(tuple(z) for z in zeilen))
            return
        for i in range(len(lam)):
            if len(zeilen[i]) < lam[i] and (i == 0 or len(zeilen[i - 1]) > len(zeilen[i])):
                zeilen[i].append(k)
                rek(k + 1)
                zeilen[i].pop()

    rek(1)
    return erg


def lis_probieren(a, streng=True):
    for k in range(len(a), 0, -1):
        for idx in combinations(range(len(a)), k):
            w = [a[i] for i in idx]
            if all((w[i] < w[i + 1]) if streng else (w[i] <= w[i + 1]) for i in range(k - 1)):
                return k
    return 0


def lds_probieren(a, streng=True):
    for k in range(len(a), 0, -1):
        for idx in combinations(range(len(a)), k):
            w = [a[i] for i in idx]
            if all((w[i] > w[i + 1]) if streng else (w[i] >= w[i + 1]) for i in range(k - 1)):
                return k
    return 0


def enthaelt(p, muster):
    """Enthält p das Muster (Tupel aus 1..k) als Teilfolge gleicher relativer Ordnung?"""
    k = len(muster)
    for idx in combinations(range(len(p)), k):
        w = [p[i] for i in idx]
        rang = [sorted(w).index(x) + 1 for x in w]
        if tuple(rang) == tuple(muster):
            return True
    return False


def ballot_woerter(t, n):
    """Wörter über {0, …, t} mit je n Buchstaben, in jedem Präfix #i ≥ #(i+1)."""
    erg = []

    def rek(wort, zaehl):
        if len(wort) == n * (t + 1):
            erg.append(tuple(wort))
            return
        for b in range(t + 1):
            if zaehl[b] < n and (b == 0 or zaehl[b] < zaehl[b - 1]):
                zaehl[b] += 1
                wort.append(b)
                rek(wort, zaehl)
                wort.pop()
                zaehl[b] -= 1

    rek([], [0] * (t + 1))
    return erg


def ausgabe_von_wort(wort, t):
    stapel = [[] for _ in range(t)]
    naechster = 1
    aus = []
    for b in wort:
        if b == 0:
            stapel[0].append(naechster)
            naechster += 1
        elif b < t:
            stapel[b].append(stapel[b - 1].pop())
        else:
            aus.append(stapel[t - 1].pop())
    return tuple(aus)


def kostka_fuellen(lam, inhalt):
    """Füllungen der Form lam mit dem Inhalt: Zeilen schwach, Spalten streng wachsend, Zelle für Zelle."""
    zellen = [(i, j) for i, r in enumerate(lam) for j in range(r)]
    rest = list(inhalt)
    feld = {}

    def rek(k):
        if k == len(zellen):
            return 1
        i, j = zellen[k]
        gesamt = 0
        for v in range(1, len(inhalt) + 1):
            if rest[v - 1] == 0:
                continue
            if j > 0 and feld[(i, j - 1)] > v:
                continue
            if i > 0 and feld[(i - 1, j)] >= v:
                continue
            rest[v - 1] -= 1
            feld[(i, j)] = v
            gesamt += rek(k + 1)
            del feld[(i, j)]
            rest[v - 1] += 1
        return gesamt

    return rek(0)


def min_stapel_suche(wort, schwach):
    """Kleinste Stapelzahl durch Suche über alle Zustände der Stapelspitzen (Stapel sind austauschbar, die Spitzen reichen)."""

    @lru_cache(maxsize=None)
    def rek(pos, spitzen):
        if pos == len(wort):
            return len(spitzen)
        x = wort[pos]
        beste = rek(pos + 1, tuple(sorted(spitzen + (x,))))
        for idx, s in enumerate(spitzen):
            if (s >= x) if schwach else (s > x):
                neu = spitzen[:idx] + (x,) + spitzen[idx + 1:]
                beste = min(beste, rek(pos + 1, tuple(sorted(neu))))
        return beste

    return rek(0, ())


# --- Einfügen und Umkehrung ---------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n", range(1, 7))
def test_einfuegen_ist_bijektion_auf_alle_paare_standardtableaux(n):
    """Die Bilder aller n! Folgen sind genau die Paare (P, Q) gleichförmiger Standardtableaux (Aufzählung der Tableaux unabhängig), und die Umkehrung trifft jede Folge."""
    bilder = {}
    for p in permutations(range(1, n + 1)):
        P, Q = R.einfuegen(p)
        paar = (tuple(map(tuple, P)), tuple(map(tuple, Q)))
        assert paar not in bilder
        bilder[paar] = p
    alle = {(P, Q) for lam in partitionen_ref(n) for P in alle_syt(lam) for Q in alle_syt(lam)}
    assert set(bilder) == alle and len(alle) == math.factorial(n)
    for (P, Q), p in bilder.items():
        assert R.zurueckrechnen(P, Q) == p
        assert R.ist_standard(P, n) and R.ist_standard(Q, n)


@pytest.mark.parametrize("n", range(1, 7))
def test_erste_zeile_und_zeilenzahl_gegen_teilmengen(n):
    for p in permutations(range(1, n + 1)):
        lam = R.form(R.einfuegen(p)[0])
        assert lam[0] == lis_probieren(p) and len(lam) == lds_probieren(p), p


@pytest.mark.parametrize("n", (7, 8))
def test_erste_zeile_und_zeilenzahl_gegen_dp(n):
    for p in permutations(range(1, n + 1)):
        lam = R.form(R.einfuegen(p)[0])
        assert lam[0] == R.lis_laenge(p) and len(lam) == R.lds_laenge(p)


def test_stapelzahl_ist_lis_und_lds_in_beiden_richtungen():
    for n in range(1, 7):
        for p in permutations(range(1, n + 1)):
            assert len(R.stapel_bilden(p, fallend=True)) == lis_probieren(p)
            assert len(R.stapel_bilden(p, fallend=False)) == lds_probieren(p)


def test_q_liest_den_verlauf_aus_der_konstruktion():
    for n in range(1, 7):
        for p in permutations(range(1, n + 1)):
            _, Q = R.einfuegen(p)
            for i in range(1, n + 1):
                assert R.form_nach_schritt(Q, i)[0] == lis_probieren(p[:i])
                assert len(R.form_nach_schritt(Q, i)) == lds_probieren(p[:i])


# --- Hakenformel und Formverteilung -------------------------------------------------------------------------------------------------------------

def test_partitionen_und_hakenformel_gegen_eckenrekursion():
    for n in range(0, 15):
        ref = partitionen_ref(n)
        assert list(H.partitionen(n)) == ref
        for lam in ref:
            assert H.f_haken(lam) == f_ecken(lam), lam
        assert sum(f_ecken(lam) ** 2 for lam in ref) == math.factorial(n)
        assert sum(H.f_haken(lam) ** 2 for lam in ref) == math.factorial(n)


def test_involutionen_summe_f():
    a = [1, 1]
    for k in range(2, 15):
        a.append(a[k - 1] + (k - 1) * a[k - 2])
    assert [H.involutionen(n) for n in range(0, 15)] == a
    assert [sum(f_ecken(lam) for lam in partitionen_ref(n)) for n in range(0, 15)] == a
    for n in range(1, 8):
        zaehl = sum(1 for p in permutations(range(1, n + 1)) if all(p[p[i] - 1] == i + 1 for i in range(n)))
        assert zaehl == a[n]


@pytest.mark.parametrize("n", range(1, 9))
def test_folgen_je_form_gleich_f_quadrat_durch_aufzaehlung(n):
    je_form = Counter(R.form(R.einfuegen(p)[0]) for p in permutations(range(1, n + 1)))
    assert dict(je_form) == {lam: f_ecken(lam) ** 2 for lam in partitionen_ref(n)}
    auf = E.aufzaehlen(n)
    assert auf["formen"] == dict(je_form) and auf["paare"] == math.factorial(n) and auf["umkehrung_ok"]


@pytest.mark.slow
def test_folgen_je_form_n9_gegen_hakenformel_und_tabelle():
    je_form = Counter(R.form(R.einfuegen(p)[0]) for p in permutations(range(1, 10)))
    assert dict(je_form) == {lam: f_ecken(lam) ** 2 for lam in partitionen_ref(9)}
    tab = E.eingefroren()
    assert tab[9]["formen"] == dict(je_form)


def test_exakter_erwartungswert_gegen_aufzaehlung():
    for n in range(1, 8):
        summe = sum(lis_probieren(p) if n <= 6 else R.lis_laenge(p) for p in permutations(range(1, n + 1)))
        assert H.erwartete_erste_zeile(n) == Fraction(summe, math.factorial(n))
    assert H.erwartete_zeilenzahl(7) == H.erwartete_erste_zeile(7)


# --- Ein Stapel, Catalan zweimal, Überlappung ---------------------------------------------------------------------------------------------------

def test_ein_stapel_sortiert_genau_die_231_vermeidenden():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            assert R.ein_stapel_sortiert(p) == (not enthaelt(p, (2, 3, 1)))


def test_catalan_ueberlappung_gegen_mustersuche():
    for n in range(1, 8):
        perms = list(permutations(range(1, n + 1)))
        stapel = {p for p in perms if not enthaelt(p, (2, 3, 1))}
        lis2 = {p for p in perms if not enthaelt(p, (1, 2, 3))}       # höchstens 2 Spalten: keine wachsende Teilfolge der Länge 3
        lds2 = {p for p in perms if not enthaelt(p, (3, 2, 1))}
        cat = math.comb(2 * n, n) // (n + 1)
        assert len(stapel) == len(lis2) == len(lds2) == cat == H.catalan(n)
        e = E.aufzaehlen(n)
        assert (e["stapel"], e["lis2"], e["lds2"]) == (cat, cat, cat)
        assert e["stapel_lis2"] == len(stapel & lis2) and e["stapel_lds2"] == len(stapel & lds2) and e["lis2_lds2"] == len(lis2 & lds2)
        assert H.folgen_mit_hoechstens_zeilen(n, 2) == H.folgen_mit_hoechstens_spalten(n, 2) == cat


# --- Zugfolgen ----------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("t,n", [(1, k) for k in range(1, 7)] + [(2, k) for k in range(1, 5)] + [(3, 1), (3, 2), (3, 3)])
def test_zugfolgen_simulation_gegen_ballot_woerter_gegen_hakenformel(t, n):
    woerter = ballot_woerter(t, n)
    ausgaben = {ausgabe_von_wort(w, t) for w in woerter}
    erg = Z.zugfolgen_zaehlen(t, n)
    assert (erg.zugfolgen, erg.ausgaben) == (len(woerter), len(ausgaben))
    assert erg.zugfolgen == f_ecken((n,) * (t + 1)) == H.hakenzahl_rechteck(t + 1, n)


def test_ausgaben_eines_stapels_sind_die_312_vermeidenden_und_invers_die_sortierbaren():
    for n in range(1, 8):
        ausgaben = {ausgabe_von_wort(w, 1) for w in ballot_woerter(1, n)}
        assert ausgaben == {p for p in permutations(range(1, n + 1)) if not enthaelt(p, (3, 1, 2))}
        assert {tuple(p.index(v) + 1 for v in range(1, n + 1)) for p in ausgaben} == {p for p in permutations(range(1, n + 1)) if R.ein_stapel_sortiert(p)}


def test_ausgaben_bei_zwei_stapeln_werte():
    assert [Z.zugfolgen_zaehlen(2, n).ausgaben for n in range(1, 7)] == [1, 2, 6, 24, 120, 720]
    assert [Z.zugfolgen_zaehlen(3, n).ausgaben for n in range(1, 5)] == [1, 2, 6, 24]


def test_verlaesst_die_maschine_nur_vollstaendige_zugfolgen():
    erg = Z.zugfolgen_zaehlen(2, 2, woerter_bis=10)
    for wort, aus in erg.woerter:
        assert len(wort) == 6 and wort.count("a") == 2 and sorted(aus) == [1, 2]
        for i in range(1, 7):
            assert wort[:i].count("a") >= wort[:i].count("b") >= wort[:i].count("c")


# --- Wörter mit gleichen Buchstaben -------------------------------------------------------------------------------------------------------------

INHALTE = [(2, 2, 2), (3, 2, 1), (2, 2, 1, 1), (2, 1, 1, 1), (3, 3), (2, 2, 2, 1), (1, 1, 1, 1, 1)]


@pytest.mark.parametrize("inhalt", INHALTE)
def test_woerter_je_form_gleich_f_mal_kostka_beide_fassungen(inhalt):
    woerter = W.woerter_zu_inhalt(inhalt)
    assert len(woerter) == len(set(woerter)) == math.factorial(sum(inhalt)) // math.prod(math.factorial(m) for m in inhalt) == W.zahl_woerter(inhalt)
    for dual in (True, False):
        gezaehlt = Counter(R.form(R.einfuegen(w, dual)[0]) for w in woerter)
        erwartet = {}
        for lam in partitionen_ref(sum(inhalt)):
            k = kostka_fuellen(tuple(sum(1 for x in lam if x > j) for j in range(lam[0])) if dual else lam, inhalt)
            if k:
                erwartet[lam] = f_ecken(lam) * k
        assert dict(gezaehlt) == erwartet, (inhalt, dual)


@pytest.mark.parametrize("inhalt", INHALTE)
def test_woerter_erste_zeile_ist_mindestzahl_stapel_und_umkehrung(inhalt):
    for w in W.woerter_zu_inhalt(inhalt):
        P, Q = R.einfuegen(w, dual=True)
        assert len(P[0]) == lis_probieren(w, True) == min_stapel_suche(w, True) == len(R.stapel_bilden(w, True, True))
        assert len(P) == lds_probieren(w, False)
        assert R.zurueckrechnen(P, Q, dual=True) == w
        P2, Q2 = R.einfuegen(w, dual=False)
        assert len(P2[0]) == lis_probieren(w, False) == min_stapel_suche(w, False) == len(R.stapel_bilden(w, True, False))
        assert R.zurueckrechnen(P2, Q2, dual=False) == w
        assert W.mindestzahl_stapel_probieren(w, True) == min_stapel_suche(w, True)
        assert W.mindestzahl_stapel_probieren(w, False) == min_stapel_suche(w, False)


def test_kostka_gegen_fuellen():
    for inhalt in INHALTE:
        for lam in partitionen_ref(sum(inhalt)):
            assert W.kostka(lam, inhalt) == kostka_fuellen(lam, inhalt), (lam, inhalt)
    assert W.kostka((2, 1), (2, 1)) == 1 and W.kostka((3,), (3,)) == 1 and W.kostka((1, 1, 1), (1, 1, 1)) == 1


# --- Involutionen -------------------------------------------------------------------------------------------------------------------------------

def test_p_gleich_q_genau_fuer_involutionen_und_fixpunkte_sind_ungerade_spalten():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            P, Q = R.einfuegen(p)
            invol = all(p[p[i] - 1] == i + 1 for i in range(n))
            assert (P == Q) == invol
            if invol:
                assert sum(1 for i in range(n) if p[i] == i + 1) == sum(1 for c in R.konjugiert(R.form(P)) if c % 2 == 1)
