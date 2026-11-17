"""Zugfolgen von t Stapeln in Serie: Züge zählen gegen Folgen zählen.

Die Maschine: die Container 1 bis n kommen in dieser Reihenfolge am Eingang an. Jeder Zug ist eines von drei Dingen: den nächsten Container auf Stapel 1 legen
(Buchstabe a), die Spitze von Stapel i auf Stapel i + 1 setzen (b, bei drei Stapeln auch c) oder die Spitze des letzten Stapels ausgeben (der letzte Buchstabe).
Eine **Zugfolge** ist eine vollständige Zugreihe (alle n Container ausgegeben); die **Ausgabe** ist die Folge der ausgegebenen Container. Verschiedene Zugfolgen
können dieselbe Ausgabe haben; bei einem Stapel (t = 1) gibt es je Ausgabe genau eine Zugfolge, bei t ≥ 2 mehrere.

Die Zahl der Zugfolgen wird hier durch Aufzählung mit einer echten Stapelsimulation gezählt (nicht aus der Hakenformel); die Hakenformel des Rechtecks
(t + 1) × n steht in trk_haken.hakenzahl_rechteck und wird nur gegenübergestellt."""

from dataclasses import dataclass

LIVE_GRENZE = {1: 8, 2: 6, 3: 4}   # größtes n je t, das die App selbst aufzählt (darüber: vorgerechnet, data/trk_zuege.json)


@dataclass(frozen=True)
class Zugergebnis:
    t: int
    n: int
    zugfolgen: int
    ausgaben: int
    woerter: tuple          # (Wort, Ausgabe) je Zugfolge, nur wenn nach `woerter_bis` Zugfolgen angefordert (sonst leer)


def buchstaben(t):
    """Buchstaben der Züge: a einlegen, dann umsetzen, zuletzt ausgeben."""
    return "abcd"[: t + 1]


def zugfolgen_zaehlen(t, n, woerter_bis=0):
    """Zählt alle vollständigen Zugfolgen von t Stapeln in Serie bei n Containern und die verschiedenen Ausgaben.

    `woerter_bis` > 0: sind es höchstens so viele Zugfolgen, werden sie samt Ausgabe mitgeliefert."""
    if t < 1 or n < 0:
        raise ValueError("t >= 1 und n >= 0")
    stapel = [[] for _ in range(t)]
    zeichen = buchstaben(t)
    ausgaben = set()
    gesamt = 0
    woerter = []
    wort = []
    aus = []

    def rek(naechster):
        nonlocal gesamt
        if len(aus) == n:
            gesamt += 1
            ausgaben.add(tuple(aus))
            if woerter_bis and len(woerter) <= woerter_bis:
                woerter.append(("".join(wort), tuple(aus)))
            return
        if naechster <= n:                              # einlegen
            stapel[0].append(naechster)
            wort.append(zeichen[0])
            rek(naechster + 1)
            wort.pop()
            stapel[0].pop()
        for i in range(t):                              # Spitze von Stapel i nach i + 1 setzen oder (letzter Stapel) ausgeben
            if not stapel[i]:
                continue
            x = stapel[i].pop()
            wort.append(zeichen[i + 1])
            if i + 1 < t:
                stapel[i + 1].append(x)
                rek(naechster)
                stapel[i + 1].pop()
            else:
                aus.append(x)
                rek(naechster)
                aus.pop()
            wort.pop()
            stapel[i].append(x)

    rek(1)
    behalten = tuple(sorted(woerter)) if woerter_bis and len(woerter) <= woerter_bis else ()
    return Zugergebnis(t, n, gesamt, len(ausgaben), behalten)


def enthaelt_312(p):
    """Enthält p drei Positionen i < j < k mit p[j] < p[k] < p[i] (Muster 312)?"""
    n = len(p)
    return any(p[j] < p[k] < p[i] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))
