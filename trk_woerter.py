"""Wörter mit gleichen Buchstaben (Wagen mit Zielgruppen): Kostka-Zahlen, Aufzählung der Wörter, Mindestzahl Stapel durch Probieren.

Ein Wort hat den Inhalt μ = (μ₁, …, μ_g): der Buchstabe (Zielgruppe) j kommt μ_j-mal vor. Mit der dualen Einfügung (trk_rsk.einfuegen(..., dual=True)) hat P streng
wachsende Zeilen und schwach wachsende Spalten; die erste Zeile ist die längste **streng** wachsende Teilfolge und gleich der Mindestzahl von Stapeln, auf die ein
gleicher Rang noch passt. Die Zahl der Wörter mit der Form λ ist f^λ · K(λ', μ), nicht f²: K ist die Kostka-Zahl (Zahl der Füllungen der transponierten Form mit
dem Inhalt μ, Zeilen schwach und Spalten streng wachsend)."""

import math
from functools import lru_cache
from itertools import combinations

from trk_haken import f_haken, konjugiert, partitionen


def woerter_zu_inhalt(inhalt):
    """Alle verschiedenen Wörter mit dem Inhalt (Buchstabe j kommt inhalt[j-1]-mal vor), sortiert."""
    n = sum(inhalt)
    zaehler = list(inhalt)
    wort = []
    erg = []

    def rek():
        if len(wort) == n:
            erg.append(tuple(wort))
            return
        for b in range(len(zaehler)):
            if zaehler[b]:
                zaehler[b] -= 1
                wort.append(b + 1)
                rek()
                wort.pop()
                zaehler[b] += 1

    rek()
    return erg


def zahl_woerter(inhalt):
    """Mehrfachmengen-Permutationen n! / (μ₁! μ₂! …)."""
    z = math.factorial(sum(inhalt))
    for m in inhalt:
        z //= math.factorial(m)
    return z


def _waagrechte_streifen(lam, groesse):
    """Alle Formen ν ⊆ lam, bei denen lam/ν ein waagrechter Streifen mit `groesse` Zellen ist (keine zwei Zellen in einer Spalte)."""
    erg = []
    k = len(lam)

    def rek(i, nu, rest):
        if i == k:
            if rest == 0:
                erg.append(tuple(x for x in nu if x > 0))
            return
        untere_grenze = lam[i + 1] if i + 1 < k else 0
        for v in range(lam[i], untere_grenze - 1, -1):
            if lam[i] - v > rest:
                break
            rek(i + 1, nu + [v], rest - (lam[i] - v))

    rek(0, [], groesse)
    return erg


@lru_cache(maxsize=None)
def kostka(lam, inhalt):
    """Zahl der Füllungen der Form lam mit dem Inhalt `inhalt` (Zeilen schwach, Spalten streng wachsend).

    Rechenweg: der größte Buchstabe füllt einen waagrechten Streifen; der Rest ist eine Füllung der kleineren Form mit dem kürzeren Inhalt."""
    if sum(lam) != sum(inhalt):
        return 0
    if not inhalt:
        return 1 if not lam else 0
    letzte = inhalt[-1]
    return sum(kostka(nu, inhalt[:-1]) for nu in _waagrechte_streifen(lam, letzte))


def woerter_je_form(inhalt):
    """Zeilen (lam, f, K(lam', inhalt), Wörter = f·K) für alle Formen, bei denen K > 0 ist, sortiert absteigend nach Wörtern."""
    n = sum(inhalt)
    zeilen = []
    for lam in partitionen(n):
        k = kostka(konjugiert(lam), tuple(inhalt))
        if k:
            f = f_haken(lam)
            zeilen.append((lam, f, k, f * k))
    zeilen.sort(key=lambda z: (-z[3], tuple(-x for x in z[0])))
    return zeilen


def mindestzahl_stapel_probieren(wort, schwach=True):
    """Kleinste Zahl von Stapeln, in denen jeder (von unten nach oben gelesen) schwach fallend (schwach=True) oder streng fallend (schwach=False) ist:
    alle Zerlegungen der Positionen probieren."""
    n = len(wort)
    if n == 0:
        return 0
    for k in range(1, n + 1):
        for zuordnung in _zuordnungen(n, k):
            spitzen = [None] * k
            ok = True
            for pos, b in enumerate(zuordnung):
                if spitzen[b] is not None and ((wort[pos] > spitzen[b]) if schwach else (wort[pos] >= spitzen[b])):
                    ok = False
                    break
                spitzen[b] = wort[pos]
            if ok:
                return k
    return n


def _zuordnungen(n, k):
    """Alle Zuordnungen der n Positionen zu genau k nummerierten Stapeln in Normalform (Stapel in der Reihenfolge ihres ersten Elements)."""

    def rek(pre, benutzt):
        if len(pre) == n:
            if benutzt == k:
                yield tuple(pre)
            return
        if benutzt + (n - len(pre)) < k:
            return
        for b in range(min(benutzt + 1, k)):
            pre.append(b)
            yield from rek(pre, max(benutzt, b + 1))
            pre.pop()

    yield from rek([], 0)


def laengste_wachsende_probieren(wort, streng=True):
    """Längste wachsende Teilfolge durch Probieren aller Teilmengen (für die kurzen Wörter dieser Seite)."""
    n = len(wort)
    for k in range(n, 0, -1):
        for idx in combinations(range(n), k):
            w = [wort[i] for i in idx]
            if all((w[i] < w[i + 1]) if streng else (w[i] <= w[i + 1]) for i in range(k - 1)):
                return k
    return 0
