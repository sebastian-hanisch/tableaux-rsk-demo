"""Kennzahlen und Verdikte der fünf Experimente. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text).

Zähleinheiten (jede Zahl nennt ihre): Folgen (n! Möglichkeiten), Tableaux (Standardtableaux einer Form), Zugfolgen (vollständige Zugreihen einer Maschine aus Stapeln),
Wörter (Folgen mit gleichen Buchstaben). Die Hakenformel zählt Tableaux und Zugfolgen, nicht Folgen."""

import json
import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import trk_constants as C
import trk_enum as E
import trk_haken as H
import trk_rsk as R
import trk_woerter as W
import trk_zuege as Z
from trk_scenario import D_WERTE, d_text, folgen_modell, folge_modell_u, folge_modell_v, strom
from trk_texts import de, de_fest, folge_text, form_text, ganz, prozent

DATA = Path(__file__).resolve().parent / "data"


def _folgen(x):
    """„1 Folge“ oder „5 Folgen“ (mit Tausendertrenner)."""
    return f"{ganz(x)} {'Folge' if x == 1 else 'Folgen'}"


# --- Experiment 1: Einfügen -----------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FolgeAnalyse:
    folge: tuple
    fallend: bool             # Stapel fallend (Stapelzahl = erste Zeile) oder wachsend (Stapelzahl = erste Spalte = Zeilenzahl)
    P: tuple
    Q: tuple
    form: tuple
    f: int
    folgen_dieser_form: int   # f²
    fakultaet: int
    erste_zeile: int
    zeilenzahl: int
    lis: int                  # längste wachsende Teilfolge (O(n²)-Programm)
    lds: int
    stapelzahl: int           # Mindestzahl Stapel in der gewählten Richtung
    stapel: tuple             # die gierig gebildeten Stapel (von unten nach oben)
    verlauf: tuple            # Stapelzahl nach 1, 2, ..., n Ankünften (Stapelbildung)
    q_verlauf: tuple          # dieselbe Zahl, aus Q abgelesen (erste Zeile bzw. Zeilenzahl der Form von Q bis i)
    umkehrung_ok: bool
    ein_stapel: bool          # sortiert ein einziger Stapel die Folge zur Identität?


def analysiere_folge(folge, fallend=True):
    folge = tuple(folge)
    P, Q, _ = R.einfuegen_protokoll(folge)
    lam = R.form(P)
    f = H.f_haken(lam)
    stapel = R.stapel_bilden(folge, fallend=fallend)
    verlauf = tuple(R.stapelzahl_verlauf(folge, fallend=fallend))
    ablesen = (lambda s: s[0]) if fallend else len
    q_verlauf = tuple(ablesen(R.form_nach_schritt(Q, i)) for i in range(1, len(folge) + 1))
    return FolgeAnalyse(
        folge=folge, fallend=fallend, P=tuple(map(tuple, P)), Q=tuple(map(tuple, Q)), form=lam, f=f, folgen_dieser_form=f * f,
        fakultaet=math.factorial(len(folge)), erste_zeile=lam[0], zeilenzahl=len(lam), lis=R.lis_laenge(folge), lds=R.lds_laenge(folge),
        stapelzahl=len(stapel), stapel=tuple(tuple(s) for s in stapel), verlauf=verlauf, q_verlauf=q_verlauf,
        umkehrung_ok=R.zurueckrechnen(P, Q) == folge, ein_stapel=R.ein_stapel_sortiert(folge),
    )


def stapel_text(stapel):
    """Stapel von unten nach oben: [1] [3, 2] [6, 5, 4]."""
    return " ".join("[" + ", ".join(str(x) for x in s) + "]" for s in stapel)


def verdict_einfuegen(a: FolgeAnalyse):
    """Verdikt zu Experiment 1 (eine Folge, eine Richtung)."""
    n = len(a.folge)
    if a.fallend:
        lesen = (f"erste Zeile {a.erste_zeile} = längste wachsende Teilfolge = Mindestzahl **fallender** Stapel ({stapel_text(a.stapel)}); "
                 f"Zeilenzahl {a.zeilenzahl} = längste fallende Teilfolge")
    else:
        lesen = (f"erste Spalte (= Zeilenzahl) {a.zeilenzahl} = längste fallende Teilfolge = Mindestzahl **wachsender** Stapel ({stapel_text(a.stapel)}); "
                 f"erste Zeile {a.erste_zeile} = längste wachsende Teilfolge")
    ein = "Ein einziger Stapel sortiert die Folge." if a.ein_stapel else "Ein einziger Stapel sortiert die Folge nicht (sie enthält das Muster 231)."
    umkehr = "Die Umkehrung liefert die Folge zurück." if a.umkehrung_ok else "FEHLER: die Umkehrung liefert eine andere Folge."
    text = (f"{folge_text(a.folge)}: Form {form_text(a.form)}, f = {ganz(a.f)}; {ganz(a.folgen_dieser_form)} von {_folgen(a.fakultaet)} der Länge {n} {'hat' if a.folgen_dieser_form == 1 else 'haben'} diese Form. "
            f"{lesen[0].upper() + lesen[1:]}. {umkehr} Stapelzahl nach 1 bis {n} Ankünften: {', '.join(str(x) for x in a.verlauf)}. {ein}")
    if not a.umkehrung_ok or a.verlauf != a.q_verlauf:
        return "error", text
    return "success", text


# --- Experiment 2: Formen --------------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FormenZusammenfassung:
    n: int
    formen: int
    haeufigste: tuple          # alle Formen mit der größten Zahl von Folgen
    f_haeufigste: int
    folgen_haeufigste: int
    anteil_haeufigste: Fraction
    anteil_top5: Fraction
    fakultaet: int
    summe_f2: int
    summe_f: int
    involutionen: int
    catalan: int
    hoechstens_2_zeilen: int
    hoechstens_2_spalten: int


def formen_zusammenfassung(n):
    zeilen = H.formverteilung(n)
    top = H.haeufigste_formen(n)
    kopf = zeilen[0]
    return FormenZusammenfassung(
        n=n, formen=len(zeilen), haeufigste=top, f_haeufigste=kopf[1], folgen_haeufigste=kopf[2], anteil_haeufigste=kopf[3],
        anteil_top5=H.anteil_haeufigste(n, 5), fakultaet=math.factorial(n), summe_f2=H.summe_f2(n), summe_f=H.summe_f(n),
        involutionen=H.involutionen(n), catalan=H.catalan(n),
        hoechstens_2_zeilen=H.folgen_mit_hoechstens_zeilen(n, 2), hoechstens_2_spalten=H.folgen_mit_hoechstens_spalten(n, 2),
    )


def aufzaehlung_geprueft(auf):
    """Stimmt die Aufzählung mit der Hakenformel überein? (Folgen je Form = f², verschiedene Paare = n!, Umkehrung für jede Folge)."""
    n = auf["n"]
    soll = {lam: H.f_haken(lam) ** 2 for lam in H.partitionen(n)}
    return auf["formen"] == soll and auf["paare"] == math.factorial(n) and auf["umkehrung_ok"]


def verdict_formen(z: FormenZusammenfassung, auf=None, live=True):
    """Verdikt zu Experiment 2. `auf` ist die Aufzählung (live bis n = 8, sonst vorgerechnet) oder None."""
    if len(z.haeufigste) == 1:
        spitze = f"am häufigsten ist {form_text(z.haeufigste[0])} mit {ganz(z.folgen_haeufigste)} von {_folgen(z.fakultaet)} ({prozent(z.anteil_haeufigste)})"
    else:
        namen = " und ".join(form_text(h) for h in z.haeufigste)
        spitze = (f"am häufigsten sind {namen} mit je {ganz(z.folgen_haeufigste)} von {_folgen(z.fakultaet)} ({prozent(z.anteil_haeufigste)}; "
                  "die transponierte Form ist gleich häufig)")
    teile = [f"Länge n = {z.n}: {z.formen} {'Form' if z.formen == 1 else 'Formen'}; {spitze}."]
    if z.formen > 5:
        teile.append(f"Die fünf häufigsten zusammen: {prozent(z.anteil_top5)}.")
    teile.append(f"Summe der f² = {ganz(z.summe_f2)} = {z.n}! (Zähleinheit Folgen); Summe der f = {ganz(z.summe_f)} = Zahl der Folgen mit σ = σ⁻¹.")
    teile.append(f"Formen mit höchstens 2 Zeilen: Catalan({z.n}) = {_folgen(z.hoechstens_2_zeilen)}.")
    if auf is not None:
        quelle = "aufgezählt" if live else "vorgerechnet aufgezählt"
        if auf["stapel"] == z.catalan and auf["lis2"] == z.hoechstens_2_spalten:
            if auf["stapel_lis2"] == auf["stapel"]:
                teile.append(f"Ein Stapel sortiert ebenfalls {_folgen(auf['stapel'])} ({quelle}); bei dieser kleinen Länge sind es dieselben Folgen wie bei „höchstens 2 Spalten“.")
            else:
                teile.append(f"Ein Stapel sortiert ebenfalls {_folgen(auf['stapel'])} ({quelle}), aber gemeinsam mit „höchstens 2 Spalten“ sind es nur {ganz(auf['stapel_lis2'])}: "
                             "dieselbe Zahl, eine andere Menge.")
        else:
            teile.append("Die Aufzählung weicht von Catalan ab (Fehler).")
        if live and not aufzaehlung_geprueft(auf):
            return "error", " ".join(teile) + " FEHLER: die Aufzählung widerspricht der Hakenformel."
        if live:
            teile.append(f"Aufzählung aller {_folgen(z.fakultaet)}: {len(auf['formen'])} {'Form' if len(auf['formen']) == 1 else 'Formen'}, jede mit genau f² Folgen, "
                         f"{ganz(auf['paare'])} {'Paar' if auf['paare'] == 1 else 'Paare'} (P, Q) paarweise verschieden, die Umkehrung liefert jede Folge zurück.")
    return "info", " ".join(teile)


# --- Experiment 3: Modell V -----------------------------------------------------------------------------------------------------------------------

def formen_statistik(folgen):
    """Statistik der Formen einer Liste von Folgen: Summen als Ganzzahlen (exakt), dazu die Zahl je Form."""
    formen = Counter()
    s_erste = s_zeilen = s_quadrat = 0
    for p in folgen:
        P, _ = R.einfuegen(p)
        lam = R.form(P)
        formen[lam] += 1
        s_erste += lam[0]
        s_quadrat += lam[0] ** 2
        s_zeilen += len(lam)
    anzahl = len(folgen)
    top, cnt = max(formen.items(), key=lambda kv: (kv[1], kv[0]))
    varianz = (s_quadrat - s_erste ** 2 / anzahl) / max(1, anzahl - 1)
    return {"anzahl": anzahl, "summe_erste_zeile": s_erste, "summe_zeilenzahl": s_zeilen, "formen": formen, "top": top, "top_anzahl": cnt,
            "mittel_erste_zeile": s_erste / anzahl, "mittel_zeilenzahl": s_zeilen / anzahl, "top_anteil": cnt / anzahl, "formen_gesehen": len(formen),
            "se_erste_zeile": math.sqrt(max(varianz, 0.0) / anzahl)}


def modellv_statistik(n, d, anzahl, seed):
    """Folgen im Modell V (Mittel d, None = gleichverteilt) aus dem Zufallsstrom des Zufalls-Seeds, Formen und Mittelwerte."""
    return formen_statistik(folgen_modell(n, d, anzahl, seed))


def modellv_tabelle():
    """Die vorgerechnete Tabelle (data/trk_modellv.json): n = 10, 20 000 Folgen je D und Zufalls-Seed; None, falls die Datei fehlt."""
    try:
        return json.loads((DATA / "trk_modellv.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def exakt_modell_u(n):
    """Exakte Erwartungen im Modell U: E[erste Zeile] = E[Zeilenzahl], als Bruch."""
    return H.erwartete_erste_zeile(n)


def verdict_modellv_tabelle(tab):
    """Verdikt zur vorgerechneten Tabelle (n = 10). `tab` ist der Inhalt von data/trk_modellv.json."""
    n, anzahl = tab["n"], tab["anzahl"]
    seeds = [str(s) for s in tab["seeds"]]
    erste = seeds[0]
    z0, zl = tab["zeilen"][0], tab["zeilen"][-1]
    a, b = z0["seeds"][erste], zl["seeds"][erste]
    u = exakt_modell_u(n)
    top_u = H.formverteilung(n)[0]
    return "info", (
        f"Ausgedachtes Modell V, n = {n}, je {ganz(anzahl)} Folgen (Zufalls-Seed {erste}, vorgerechnet): bei D = {d_text(z0['d'])} hat {prozent(a['top_anteil'], 2)} der Folgen die Form "
        f"{form_text(tuple(a['top']))} (fast sortiert: fallende Stapel mit Verzögerung brauchen im Mittel {de_fest(a['mittel_erste_zeile'])}); bei D = ∞ ist {form_text(tuple(b['top']))} mit "
        f"{prozent(b['top_anteil'], 2)} am häufigsten (exakt im Modell U {prozent(top_u[3], 2)} für {form_text(top_u[0])}). Mittlere erste Zeile {de_fest(a['mittel_erste_zeile'])} gegen "
        f"{de_fest(b['mittel_erste_zeile'])} (exakt im Modell U {de_fest(float(u), 4)}), mittlere Zeilenzahl {de_fest(a['mittel_zeilenzahl'])} gegen {de_fest(b['mittel_zeilenzahl'])}. "
        f"Der zweite Zufalls-Seed {seeds[1]} weicht bei der mittleren ersten Zeile um höchstens "
        f"{de_fest(max(abs(z['seeds'][seeds[0]]['mittel_erste_zeile'] - z['seeds'][seeds[1]]['mittel_erste_zeile']) for z in tab['zeilen']), 3)} ab."
    )


def verdict_modellv_live(stat, n, d, seed):
    """Verdikt zur eigenen Einstellung (live gerechnet)."""
    u = exakt_modell_u(n)
    exakt = f" Im Modell U (D = ∞) ist die Erwartung exakt {de_fest(float(u), 4)}."
    return "info", (
        f"Ihre Einstellung (Modell V, D = {d_text(d)}, n = {n}, {ganz(stat['anzahl'])} Folgen, Zufalls-Seed {seed}): mittlere erste Zeile {de_fest(stat['mittel_erste_zeile'])} ± {de_fest(stat['se_erste_zeile'], 3)} "
        f"(Standardfehler), mittlere Zeilenzahl {de_fest(stat['mittel_zeilenzahl'])}; häufigste Form {form_text(stat['top'])} mit {prozent(stat['top_anteil'])}; "
        f"{stat['formen_gesehen']} von {len(H.formverteilung(n))} Formen kamen vor." + exakt
    )


# --- Experiment 4: Zugfolgen ------------------------------------------------------------------------------------------------------------------------

def zuege_eingefroren():
    try:
        roh = json.loads((DATA / "trk_zuege.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {(e["t"], e["n"]): e for e in roh["eintraege"]}


def zug_tabelle(t, n_max=8, zaehlen=Z.zugfolgen_zaehlen):
    """Zeilen für t Stapel in Serie, n = 1 bis n_max: Zugfolgen (aufgezählt oder vorgerechnet), Hakenformel des Rechtecks (t+1) × n, verschiedene Ausgaben."""
    fest = zuege_eingefroren()
    zeilen = []
    for n in range(1, n_max + 1):
        haken = H.hakenzahl_rechteck(t + 1, n)
        if n <= Z.LIVE_GRENZE[t]:
            erg = zaehlen(t, n)
            zugfolgen, ausgaben, quelle = erg.zugfolgen, erg.ausgaben, "aufgezählt"
        elif (t, n) in fest:
            zugfolgen, ausgaben, quelle = fest[(t, n)]["zugfolgen"], fest[(t, n)]["ausgaben"], "vorgerechnet"
        else:
            zugfolgen = ausgaben = None
            quelle = "nur Hakenformel"
        zeilen.append({"t": t, "n": n, "zugfolgen": zugfolgen, "haken": haken, "ausgaben": ausgaben, "quelle": quelle,
                       "je_ausgabe": None if ausgaben is None else Fraction(zugfolgen, ausgaben)})
    return zeilen


def verdict_zuege(zeilen, t, n):
    """Verdikt zu Experiment 4 für t Stapel und n Container; `zeilen` ist die Tabelle von zug_tabelle(t)."""
    z = zeilen[n - 1]
    rechteck = f"{t + 1} × {n}"
    if z["zugfolgen"] is None:
        return "info", (f"t = {t}, n = {n}: für diese Größe wird nur die Hakenformel des Rechtecks {rechteck} gerechnet ({ganz(z['haken'])}); die Zugfolgen sind weder aufgezählt "
                        "noch vorgerechnet. Die Hakenformel zählt Zugfolgen, nicht Folgen.")
    kopf = (f"t = {t}, n = {n}: {ganz(z['zugfolgen'])} Zugfolgen ({z['quelle']}; Hakenformel des Rechtecks {rechteck}: {ganz(z['haken'])}) "
            f"und {ganz(z['ausgaben'])} verschiedene Folgen als Ausgabe")
    if t == 1:
        return "info", kopf + ": je Folge genau eine Zugfolge (die Ausgaben vermeiden das Muster 312); die Hakenformel ist hier scharf."
    if z["zugfolgen"] == z["ausgaben"]:
        return "info", kopf + ": bei einem einzigen Container gibt es nur eine Folge und eine Zugfolge."
    bekannt = [r for r in zeilen if r["ausgaben"] is not None and r["n"] >= 2]
    erste, letzte = bekannt[0], bekannt[-1]
    mittel = f"im Mittel {de_fest(float(z['je_ausgabe']), 2)} Zugfolgen je Folge"
    faktor = (f" Der Faktor wächst von {de_fest(float(erste['je_ausgabe']), 2)} (n = {erste['n']}) auf {de_fest(float(letzte['je_ausgabe']), 2)} (n = {letzte['n']}); "
              "die Hakenformel ist bei zwei oder mehr Stapeln in Serie eine obere Schranke für die Zahl der Folgen und wird mit n schlechter.")
    return "warning", kopf + f", {mittel}." + faktor


# --- Experiment 5: Wörter mit Zielgruppen ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class WortAnalyse:
    inhalt: tuple
    wort: tuple
    dual: bool                # True: streng wachsende Zeilen (duale Einfügung), False: Lehrbuchfassung
    P: tuple
    Q: tuple
    form: tuple
    erste_zeile: int
    zeilenzahl: int
    lis_streng: int
    lis_schwach: int
    lds_schwach: int
    lds_streng: int
    stapel_schwach: tuple      # gierig, schwach fallende Stapel (gleicher Rang darf auf gleichen)
    stapel_streng: tuple       # gierig, streng fallende Stapel
    probiert_schwach: int      # Mindestzahl durch Probieren aller Zerlegungen
    probiert_streng: int
    umkehrung_ok: bool
    anzahl_woerter: int
    je_form: tuple             # (Form, f, Kostka, f·Kostka, gezählt)
    verschieden: int           # Wörter, bei denen streng und schwach verschiedene längste wachsende Teilfolgen haben


def analysiere_wort(inhalt, wort, dual=True):
    inhalt = tuple(inhalt)
    wort = tuple(wort)
    P, Q = R.einfuegen(wort, dual=dual)
    lam = R.form(P)
    alle = W.woerter_zu_inhalt(inhalt)
    gezaehlt = Counter(R.form(R.einfuegen(x, dual=dual)[0]) for x in alle)
    zeilen = []
    for lam2 in H.partitionen(sum(inhalt)):
        k = W.kostka(H.konjugiert(lam2) if dual else lam2, inhalt)
        if k or gezaehlt.get(lam2):
            f = H.f_haken(lam2)
            zeilen.append((lam2, f, k, f * k, gezaehlt.get(lam2, 0)))
    zeilen.sort(key=lambda z: (-z[3], tuple(-x for x in z[0])))
    return WortAnalyse(
        inhalt=inhalt, wort=wort, dual=dual, P=tuple(map(tuple, P)), Q=tuple(map(tuple, Q)), form=lam, erste_zeile=lam[0], zeilenzahl=len(lam),
        lis_streng=R.lis_laenge(wort, True), lis_schwach=R.lis_laenge(wort, False), lds_schwach=R.lds_laenge(wort, False), lds_streng=R.lds_laenge(wort, True),
        stapel_schwach=tuple(tuple(s) for s in R.stapel_bilden(wort, True, True)), stapel_streng=tuple(tuple(s) for s in R.stapel_bilden(wort, True, False)),
        probiert_schwach=W.mindestzahl_stapel_probieren(wort, True), probiert_streng=W.mindestzahl_stapel_probieren(wort, False),
        umkehrung_ok=R.zurueckrechnen(P, Q, dual=dual) == wort, anzahl_woerter=len(alle), je_form=tuple(zeilen),
        verschieden=sum(1 for x in alle if R.lis_laenge(x, True) != R.lis_laenge(x, False)),
    )


def verdict_woerter(a: WortAnalyse):
    """Verdikt zu Experiment 5."""
    n = len(a.wort)
    inhalt = ", ".join(str(x) for x in a.inhalt)
    nenner = " · ".join(f"{m}!" for m in a.inhalt)
    gleich = all(z[3] == z[4] for z in a.je_form)
    f_beispiel = a.je_form[0]
    if a.dual:
        lesen = (f"erste Zeile {a.erste_zeile} = längste **streng** wachsende Teilfolge = Mindestzahl Stapel, auf die ein gleicher Rang noch passt "
                 f"(Gegenprobe über alle Zerlegungen der Positionen: {a.probiert_schwach})")
        ok = a.erste_zeile == a.lis_streng == a.probiert_schwach == len(a.stapel_schwach)
        andere = f"die Lehrbuchfassung hätte als erste Zeile die längste **schwach** wachsende Teilfolge, {a.lis_schwach}"
    else:
        lesen = (f"erste Zeile {a.erste_zeile} = längste **schwach** wachsende Teilfolge = Mindestzahl **streng** fallender Stapel "
                 f"(Gegenprobe über alle Zerlegungen der Positionen: {a.probiert_streng})")
        ok = a.erste_zeile == a.lis_schwach == a.probiert_streng == len(a.stapel_streng)
        andere = f"die duale Fassung hätte als erste Zeile die längste **streng** wachsende Teilfolge, {a.lis_streng}"
    text = (f"Zielgruppen ({inhalt}), Wort {folge_text(a.wort)}: Form {form_text(a.form)}; {lesen}; {andere}. "
            f"Alle {ganz(a.anzahl_woerter)} Wörter dieses Inhalts = {n}!/({nenner}); je Form gilt Wörter = f · Kostka-Zahl (nicht f²), zum Beispiel Form {form_text(f_beispiel[0])}: "
            f"{ganz(f_beispiel[3])} = {ganz(f_beispiel[1])} · {ganz(f_beispiel[2])}, gezählt {ganz(f_beispiel[4])}. "
            f"Streng und schwach geben bei {ganz(a.verschieden)} von {ganz(a.anzahl_woerter)} Wörtern verschiedene Zahlen.")
    if not (ok and a.umkehrung_ok and gleich):
        return "error", text + " FEHLER: eine Gegenprobe stimmt nicht."
    return "success", text


# --- Schritttexte und kurze Antworten auf die Kernfragen -------------------------------------------------------------------------------------------

def schritt_text(s: R.Schritt):
    """Ein Einfügeschritt in Worten (Zeilen ab 1 gezählt)."""
    teile = []
    for r, c, x, y in s.verdraengungen:
        if y is not None:
            teile.append(f"{x} verdrängt {y} aus Zeile {r + 1}")
        elif c == 0:
            teile.append(f"{x} beginnt Zeile {r + 1}")
        else:
            teile.append(f"{x} kommt ans Ende von Zeile {r + 1}")
    return "; ".join(teile)


def rueck_text(rs: R.RueckSchritt):
    """Ein Schritt der Umkehrung in Worten (Zeilen und Spalten ab 1 gezählt)."""
    r, c, y, _ = rs.weg[0]
    teile = [f"Q nennt die Zelle (Zeile {r + 1}, Spalte {c + 1}): dort wird {y} entfernt"]
    for rr, _, hinein, alt in rs.weg[1:]:
        teile.append(f"{hinein} ersetzt in Zeile {rr + 1} den Eintrag {alt}")
    teile.append(f"Wert der Folge an Position {rs.nummer}: {rs.wert}")
    return "; ".join(teile)


def kernfrage_1(a: FolgeAnalyse):
    """Kurze Antwort auf Kernfrage 1 (eine Folge, ein Paar von Tableaux, was man abliest)."""
    if a.fallend:
        lesen = f"die erste Zeile ({a.erste_zeile}) ist die Mindestzahl fallender Stapel, die Zeilenzahl ({a.zeilenzahl}) die längste fallende Teilfolge"
    else:
        lesen = f"die erste Spalte ({a.zeilenzahl}) ist die Mindestzahl wachsender Stapel, die erste Zeile ({a.erste_zeile}) die längste wachsende Teilfolge"
    return "info", f"Aus {folge_text(a.folge)} werden zwei Tableaux P und Q der Form {form_text(a.form)}; {lesen}; mit Q lässt sich die Folge zurückrechnen."


def kernfrage_2(z: FormenZusammenfassung):
    """Kurze Antwort auf Kernfrage 2 (wie viele Folgen gehören zu welcher Form)."""
    if len(z.haeufigste) == 1:
        spitze = f"{form_text(z.haeufigste[0])} hat mit {ganz(z.folgen_haeufigste)} von {_folgen(z.fakultaet)} ({prozent(z.anteil_haeufigste)}) die meisten"
    else:
        spitze = (f"{' und '.join(form_text(h) for h in z.haeufigste)} haben mit je {ganz(z.folgen_haeufigste)} von {_folgen(z.fakultaet)} "
                  f"({prozent(z.anteil_haeufigste)}) die meisten")
    return "info", f"Länge n = {z.n}: {z.formen} {'Form' if z.formen == 1 else 'Formen'}, jede mit f² Folgen (Summe {ganz(z.summe_f2)} = {z.n}!); {spitze}."


def kernfrage_3(zeilen, t, n):
    """Kurze Antwort auf Kernfrage 3 (Tableaux, Zugfolgen und Folgen nicht verwechseln)."""
    z = zeilen[n - 1]
    if z["zugfolgen"] is None:
        return "info", f"t = {t}, n = {n}: die Hakenformel des Rechtecks {t + 1} × {n} gibt {ganz(z['haken'])}; das zählt Zugfolgen, nicht Folgen (hier nicht aufgezählt)."
    if z["zugfolgen"] == z["ausgaben"]:
        return "info", f"t = {t}, n = {n}: {ganz(z['zugfolgen'])} Zugfolgen und {ganz(z['ausgaben'])} verschiedene Folgen: bei einem Stapel gehört zu jeder Folge genau eine Zugfolge."
    return "warning", f"t = {t}, n = {n}: {ganz(z['zugfolgen'])} Zugfolgen, aber nur {ganz(z['ausgaben'])} verschiedene Folgen als Ausgabe."
