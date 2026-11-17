"""Schreibweise der Zahlen (deutsches Dezimalkomma, Tausendertrenner ab fünf Stellen) und Texte, die an mehreren Stellen vorkommen."""

import math
from fractions import Fraction

THIN = " "   # geschütztes Leerzeichen als Tausendertrenner

MODELL_HINWEIS = (
    "**Alle Folgen auf dieser Seite stammen aus einem ausgedachten Modell, nicht aus einer Messung an einem Hafen oder Bahnhof.** Die Zahlen gelten für dieses Modell "
    "und die genannten Einstellungen, nicht für eine wirkliche Ankunftsfolge."
)


def ganz(n: int) -> str:
    """Ganzzahl mit geschütztem Leerzeichen als Tausendertrenner ab fünf Stellen (1385670 -> 1 385 670; 5018 bleibt 5018)."""
    s = f"{abs(n)}"
    if len(s) >= 5:
        gruppen = []
        while s:
            gruppen.append(s[-3:])
            s = s[:-3]
        s = THIN.join(reversed(gruppen))
    return ("−" if n < 0 else "") + s


def de(x, nd=2) -> str:
    """Dezimalzahl mit Komma; Nachkommastellen ohne abschließende Nullen (4,3350 bleibt bei nd = 4 stehen: siehe `de_fest`)."""
    x = float(x)
    if not math.isfinite(x):
        return "–"
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", "−")


def de_fest(x, nd=2) -> str:
    """Dezimalzahl mit Komma und genau nd Nachkommastellen."""
    s = f"{float(x):.{nd}f}"
    return s.replace(".", ",").replace("-", "−")


def prozent(anteil, nd=1) -> str:
    """Anteil (Bruch oder Zahl zwischen 0 und 1) als Prozentangabe mit Komma: 0.1625 -> „16,3 %“ bei nd = 1."""
    return de_fest(float(Fraction(anteil) * 100) if isinstance(anteil, Fraction) else float(anteil) * 100, nd) + " %"


def form_text(lam) -> str:
    """Form als Text: (3, 2, 1) -> „(3,2,1)“."""
    return "(" + ",".join(str(x) for x in lam) + ")" if lam else "()"


def folge_text(p) -> str:
    return "(" + ", ".join(str(x) for x in p) + ")"
