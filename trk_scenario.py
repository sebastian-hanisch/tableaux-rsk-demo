"""Ankunftsfolgen: ein ausgedachtes Modell, kein Fall. Es gibt hier keine reale Ankunftsfolge eines Hafens oder Bahnhofs.

Eine Ankunftsfolge p = (p₁, …, p_n) ist eine Permutation der Abholränge 1 … n in der Reihenfolge der Ankunft (Rang 1 fährt zuerst).

* **Modell U:** alle n! Folgen gleich wahrscheinlich (Zufallsmischung mit SplitMix64).
* **Modell V:** Container i kommt zur Zeit i an und bleibt eine exponentialverteilte Zeit mit dem Mittel D (in Ankunftsabständen); der Rang ist die Reihenfolge der
  Abfahrtszeiten. D klein: fast sortiert; D → ∞: Modell U. Modell V benutzt nur die Rangfolge der Abfahrten.

Dazu: Einlesen einer eingetippten Folge (mit Umrechnung auf Ränge) und die Aufzählung aller n! Folgen für kleine n."""

from itertools import permutations

from trk_rng import SplitMix64

D_WERTE = (0.5, 1, 2, 4, 8, 16, None)      # None = D → ∞ (gleichverteilt, Modell U)


def d_text(d):
    return "∞ (gleichverteilt)" if d is None else str(d).replace(".", ",")


def folge_modell_u(n, rng):
    """Gleichverteilte Folge der Ränge 1 … n (Modell U)."""
    p = list(range(1, n + 1))
    rng.shuffle(p)
    return tuple(p)


def folge_modell_v(n, d, rng):
    """Ankunftsfolge im Modell V mit der mittleren Verweilzeit d (in Ankunftsabständen); d = None gibt Modell U."""
    if d is None:
        return folge_modell_u(n, rng)
    abfahrt = [i + rng.expovariate(d) for i in range(n)]
    reihenfolge = sorted(range(n), key=lambda i: abfahrt[i])
    p = [0] * n
    for rang, i in enumerate(reihenfolge, 1):
        p[i] = rang
    return tuple(p)


def strom(seed, d_index):
    """Zufallsstrom je Wert von D: Zufalls-Seed plus Index von D in D_WERTE (so entstehen die Folgen der vorgerechneten Tabelle)."""
    return SplitMix64(seed + d_index)


def folgen_modell(n, d, anzahl, seed):
    """`anzahl` Folgen im Modell V mit Mittel d aus dem Strom des Zufalls-Seeds (Strom nach D_WERTE-Index)."""
    rng = strom(seed, D_WERTE.index(d))
    return [folge_modell_v(n, d, rng) for _ in range(anzahl)]


def zufallsfolge(n, seed):
    """Eine gleichverteilte Folge (Modell U) für den Zufalls-Seed."""
    return folge_modell_u(n, SplitMix64(seed))


def alle_folgen(n):
    return permutations(range(1, n + 1))


def folge_einlesen(text, max_laenge):
    """Liest eine Folge aus Text (Zahlen getrennt durch Leerzeichen oder Komma).

    Rückgabe: (Folge der Ränge oder None, Hinweis oder None, Fehler oder None). Sind die Werte nicht genau 1 … n, werden sie auf Ränge umgerechnet (Hinweis).
    Gleiche Werte werden abgewiesen (dafür gibt es Experiment 5)."""
    teile = [t for t in text.replace(",", " ").replace(";", " ").split() if t]
    if not teile:
        return None, None, "Die Folge ist leer: bitte mindestens eine Zahl eingeben."
    if len(teile) > max_laenge:
        return None, None, f"Höchstens {max_laenge} Zahlen: die Folge hat {len(teile)}."
    try:
        werte = [int(t) for t in teile]
    except ValueError:
        return None, None, "Nur ganze Zahlen, getrennt durch Leerzeichen oder Komma."
    if len(set(werte)) != len(werte):
        return None, None, ("Gleiche Werte kommen mehrfach vor. Eine Folge hier ist eine Permutation ohne Gleichstände; Wörter mit gleichen Buchstaben "
                            "gehören in Experiment 5 (Zielgruppen).")
    rang_von = {w: r for r, w in enumerate(sorted(werte), 1)}
    folge = tuple(rang_von[w] for w in werte)
    hinweis = None
    if sorted(werte) != list(range(1, len(werte) + 1)):
        hinweis = "Die Werte sind nicht genau 1 bis n; sie wurden auf Ränge umgerechnet (kleinster Wert = Rang 1): " + ", ".join(str(r) for r in folge) + "."
    return folge, hinweis, None


def standardwort(inhalt):
    """Ein Wort mit dem Inhalt, das die Buchstaben reihum auslegt (zum Beispiel (3,2,1) -> 1 2 3 1 2 1)."""
    rest = list(inhalt)
    wort = []
    while any(rest):
        for b, m in enumerate(rest):
            if m:
                wort.append(b + 1)
                rest[b] -= 1
    return tuple(wort)


def zufallswort(inhalt, seed):
    """Ein gleichverteiltes Wort mit dem Inhalt (Zufallsmischung der Buchstaben mit SplitMix64)."""
    buchstaben = [b + 1 for b, m in enumerate(inhalt) for _ in range(m)]
    SplitMix64(seed).shuffle(buchstaben)
    return tuple(buchstaben)


def wort_einlesen(text, inhalt):
    """Liest ein Wort mit dem gegebenen Inhalt. Rückgabe: (Wort oder None, Fehler oder None)."""
    teile = [t for t in text.replace(",", " ").replace(";", " ").split() if t]
    try:
        werte = [int(t) for t in teile]
    except ValueError:
        return None, "Nur ganze Zahlen, getrennt durch Leerzeichen oder Komma."
    soll = sorted(b + 1 for b, m in enumerate(inhalt) for _ in range(m))
    if sorted(werte) != soll:
        return None, ("Das Wort passt nicht zum Inhalt: Buchstabe j muss genau " + ", ".join(f"{m}-mal (j = {j})" for j, m in enumerate(inhalt, 1)) + " vorkommen.")
    return tuple(werte), None
