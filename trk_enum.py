"""Aufzählung aller n! Folgen: Formen, Paare (P, Q) und die Überlappung von „ein Stapel sortiert“ mit „höchstens 2 Spalten“ bzw. „höchstens 2 Zeilen“.

Live bis n = 8 (40 320 Folgen, einige Zehntelsekunden); n = 9 (362 880 Folgen) ist vorgerechnet: tools/trk_make_formen.py schreibt data/trk_formen.json."""

import json
from collections import Counter
from pathlib import Path

from trk_rsk import einfuegen, ein_stapel_sortiert, form, zurueckrechnen
from trk_scenario import alle_folgen

LIVE_MAX_N = 8
DATEI = Path(__file__).resolve().parent / "data" / "trk_formen.json"


def aufzaehlen(n):
    """Zählt alle n! Folgen der Länge n. Rückgabe: Wörterbuch mit
    formen (Form -> Zahl der Folgen), paare (Zahl verschiedener Paare (P, Q)), umkehrung_ok (liefert das Rückwärts-Einfügen jede Folge zurück?),
    stapel (ein Stapel sortiert), lis2 (erste Zeile höchstens 2), lds2 (höchstens 2 Zeilen), stapel_lis2, stapel_lds2, lis2_lds2 (Schnitte)."""
    formen = Counter()
    paare = set()
    umkehrung_ok = True
    zaehler = Counter()
    for p in alle_folgen(n):
        P, Q = einfuegen(p)
        lam = form(P)
        formen[lam] += 1
        paare.add((tuple(map(tuple, P)), tuple(map(tuple, Q))))
        if zurueckrechnen(P, Q) != p:
            umkehrung_ok = False
        s = ein_stapel_sortiert(p)
        a = bool(lam) and lam[0] <= 2
        b = len(lam) <= 2
        zaehler["stapel"] += s
        zaehler["lis2"] += a
        zaehler["lds2"] += b
        zaehler["stapel_lis2"] += s and a
        zaehler["stapel_lds2"] += s and b
        zaehler["lis2_lds2"] += a and b
    erg = {"n": n, "formen": dict(formen), "paare": len(paare), "umkehrung_ok": umkehrung_ok}
    erg.update({k: int(zaehler[k]) for k in ("stapel", "lis2", "lds2", "stapel_lis2", "stapel_lds2", "lis2_lds2")})
    return erg


def eingefroren():
    """Die vorgerechnete Tabelle (n = 1 bis 9) aus data/trk_formen.json oder None, falls die Datei fehlt."""
    try:
        roh = json.loads(DATEI.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    tab = {}
    for n_text, eintrag in roh["n"].items():
        e = dict(eintrag)
        e["formen"] = {tuple(int(x) for x in k.split(",")): v for k, v in eintrag["formen"].items()}
        tab[int(n_text)] = e
    return tab


def ueberlappung(n):
    """Zahlen der Überlappung für n (live aufgezählt bis n = 8, sonst aus der vorgerechneten Tabelle); None, wenn weder noch möglich."""
    if n <= LIVE_MAX_N:
        return aufzaehlen(n)
    tab = eingefroren()
    return None if tab is None else tab.get(n)
