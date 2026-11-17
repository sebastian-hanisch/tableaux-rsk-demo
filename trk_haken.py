"""Partitionen, Hakenformel und die Verteilung der Formen (nur Ganzzahlen und Brüche, kein Gleitkomma).

Eine Form λ ist eine Partition von n (Zeilenlängen, fallend). f^λ ist die Zahl der Standardtableaux der Form λ; die Hakenformel gibt f^λ = n! / (Produkt der
Hakenlängen). Das Einfügen nach Schensted ordnet jeder Folge ein Paar gleichförmiger Standardtableaux zu; deshalb haben genau f² Folgen die Form λ und es gilt
Σ f² = n! (bis n = 14 in tests/test_claims.py nachgerechnet)."""

import math
from fractions import Fraction
from functools import lru_cache


def partitionen(n, maxteil=None):
    """Alle Partitionen von n als fallende Tupel, in absteigender lexikografischer Reihenfolge."""
    maxteil = n if maxteil is None else maxteil
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxteil), 0, -1):
        for rest in partitionen(n - k, k):
            yield (k,) + rest


def konjugiert(lam):
    if not lam:
        return ()
    return tuple(sum(1 for x in lam if x > j) for j in range(lam[0]))


def hakenlaengen(lam):
    """Hakenlänge jeder Zelle: Zellen rechts davon + Zellen darunter + 1."""
    spalten = konjugiert(lam)
    return [[(lam[i] - j - 1) + (spalten[j] - i - 1) + 1 for j in range(lam[i])] for i in range(len(lam))]


def f_haken(lam):
    """Zahl der Standardtableaux der Form lam nach der Hakenformel (Ganzzahl)."""
    n = sum(lam)
    produkt = 1
    for zeile in hakenlaengen(lam):
        for h in zeile:
            produkt *= h
    return math.factorial(n) // produkt


@lru_cache(maxsize=64)
def formverteilung(n):
    """Zeilen (lam, f, f², Anteil als Bruch) für alle Formen von n, sortiert nach f² (absteigend), bei Gleichstand nach der Form."""
    zeilen = []
    fak = math.factorial(n)
    for lam in partitionen(n):
        f = f_haken(lam)
        zeilen.append((lam, f, f * f, Fraction(f * f, fak)))
    zeilen.sort(key=lambda z: (-z[2], tuple(-x for x in z[0])))
    return tuple(zeilen)


def haeufigste_formen(n):
    """Alle Formen mit der größten Zahl von Folgen (mehr als eine bei Gleichstand; die transponierte Form ist gleich häufig)."""
    zeilen = formverteilung(n)
    top = zeilen[0][2]
    return tuple(z[0] for z in zeilen if z[2] == top)


def anteil_haeufigste(n, k):
    """Anteil der k häufigsten Formen (nach f², Gleichstände in der Sortierung von formverteilung) an allen n! Folgen."""
    return sum((z[3] for z in formverteilung(n)[:k]), Fraction(0))


def summe_f2(n):
    return sum(z[2] for z in formverteilung(n))


def summe_f(n):
    return sum(z[1] for z in formverteilung(n))


def involutionen(n):
    """Zahl der Folgen mit σ = σ⁻¹ (Rekursion a(n) = a(n−1) + (n−1)·a(n−2))."""
    a, b = 1, 1
    for k in range(2, n + 1):
        a, b = b, b + (k - 1) * a
    return b if n >= 1 else 1


def catalan(n):
    return math.comb(2 * n, n) // (n + 1)


def folgen_mit_hoechstens_zeilen(n, z):
    """Zahl der Folgen, deren Form höchstens z Zeilen hat (längste fallende Teilfolge höchstens z)."""
    return sum(s[2] for s in formverteilung(n) if len(s[0]) <= z)


def folgen_mit_hoechstens_spalten(n, s):
    """Zahl der Folgen, deren Form höchstens s Spalten hat (längste wachsende Teilfolge höchstens s)."""
    return sum(z[2] for z in formverteilung(n) if (z[0][0] if z[0] else 0) <= s)


def erwartete_erste_zeile(n):
    """E[erste Zeile] bei gleichverteilter Folge, als Bruch (= E[LIS]); wegen f^λ = f^λ' ist E[Zeilenzahl] derselbe Bruch."""
    return sum((Fraction(z[0][0] * z[2], math.factorial(n)) for z in formverteilung(n)), Fraction(0))


def erwartete_zeilenzahl(n):
    return sum((Fraction(len(z[0]) * z[2], math.factorial(n)) for z in formverteilung(n)), Fraction(0))


def hakenzahl_rechteck(zeilen, spalten):
    """Zahl der Standardtableaux des Rechtecks zeilen × spalten (Hakenformel)."""
    return f_haken((spalten,) * zeilen)

