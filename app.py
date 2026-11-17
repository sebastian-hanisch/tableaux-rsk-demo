"""Young-Tableaux und Schensted-Einfügen: eine Folge als Paar – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünf Experimente: (1) Einfügen Schritt für Schritt, (2) wie viele Folgen gehören zu welcher Form, (3) die Form im ausgedachten Modell V, (4) Zugfolgen gegen Folgen,
(5) Wörter mit Zielgruppen. Die Folgen stammen aus einem ausgedachten Ankunftsmodell, nicht aus einer Messung.

Lauffähig mit: streamlit run app.py
"""

import math

import pandas as pd
import streamlit as st

import trk_constants as C
import trk_enum as E
import trk_evaluation as ev
import trk_haken as H
import trk_rsk as R
import trk_scenario as S
import trk_zuege as Z
from trk_layout import dunkles_design, kopf_css
from trk_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from trk_texts import MODELL_HINWEIS, de_fest, folge_text, form_text, ganz, prozent
from trk_visualization import (
    build_formen_balken,
    build_formen_live,
    build_modellv_linien,
    build_tableau,
    build_verlauf,
    build_woerter_balken,
    build_zuege,
)

st.set_page_config(page_title="Young-Tableaux und Schensted-Einfügen – Sebastian Hanisch", layout="wide")


# --- Zwischengespeicherte Rechnungen -----------------------------------------------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _analyse_folge(folge, fallend):
    return ev.analysiere_folge(folge, fallend)


@st.cache_data(show_spinner="Zähle alle Folgen auf (bis n = 8: einige Zehntelsekunden) …")
def _aufzaehlung(n):
    return E.aufzaehlen(n)


@st.cache_data(show_spinner=False)
def _formen(n):
    return ev.formen_zusammenfassung(n)


@st.cache_data(show_spinner="Ziehe die Folgen und fasse sie ein (rund 0,4 Sekunden je 1 000 Folgen bei n = 10) …")
def _modellv(n, d, anzahl, seed):
    return ev.modellv_statistik(n, d, anzahl, seed)


@st.cache_data(show_spinner="Zähle die Zugfolgen auf (bei t = 2, n = 6 rund 0,2 Sekunden) …")
def _zugtabelle(t):
    return ev.zug_tabelle(t, C.E4_N_MAX)


@st.cache_data(show_spinner=False)
def _zugdetail(t, n):
    return Z.zugfolgen_zaehlen(t, n, woerter_bis=C.E4_WOERTER_BIS)


@st.cache_data(show_spinner=False)
def _wort(inhalt, wort, dual):
    return ev.analysiere_wort(inhalt, wort, dual)


@st.cache_data(show_spinner=False)
def _modellv_tabelle():
    return ev.modellv_tabelle()


@st.cache_data(show_spinner=False)
def _eingefroren():
    return E.eingefroren()


def _grid(daten):
    """Tabelle ohne Zeilennummern."""
    st.dataframe(pd.DataFrame(daten), hide_index=True, width="stretch")


def _zeige(verdikt):
    art, text = verdikt
    getattr(st, art)(text)


# --- Rückrufe ----------------------------------------------------------------------------------------------------------------------------------------

def _zufallsfolge_wuerfeln():
    n = int(st.session_state["e1_n"])
    st.session_state["e1_text"] = " ".join(str(x) for x in S.zufallsfolge(n, int(st.session_state["seed_input"])))
    st.session_state["e1_schritt"] = n


def _inhalt_gewaehlt():
    inhalt = _inhalt_von(st.session_state["e5_inhalt"])
    st.session_state["e5_text"] = " ".join(str(x) for x in S.standardwort(inhalt))


def _zufallswort_wuerfeln():
    inhalt = _inhalt_von(st.session_state["e5_inhalt"])
    st.session_state["e5_text"] = " ".join(str(x) for x in S.zufallswort(inhalt, int(st.session_state["seed_input"])))


def _inhalt_von(text):
    return tuple(int(x) for x in text.strip("()").split(","))


# --- Kopf und Einleitung -----------------------------------------------------------------------------------------------------------------------------

# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in trk_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Young-Tableaux und Schensted-Einfügen: eine Folge als Paar")
st.markdown(
    """
Container kommen in einer Reihenfolge an; jeder hat eine Abholrangzahl (Rang 1 fährt zuerst). **Das Einfügen nach Schensted** macht aus dieser Folge ein Paar von
**Young-Tableaux** (P und Q) gleicher **Form**: die Form sagt, wie viele Stapel die Folge mindestens braucht (erste Zeile) und wie lang ihre längste fallende Teilfolge ist
(Zeilenzahl), und das Paar lässt sich zurückrechnen. Die Demo zählt außerdem, **wie viele Folgen zu welcher Form gehören**, und zeigt die Falle der **Zähleinheit**:
die Hakenformel zählt Tableaux und Zugfolgen, nicht Folgen. („Tableau“ heißt hier immer Young-Tableau; das Simplex-Tableau der Linearen Programmierung ist ein anderes Objekt.)

Weiter unten: fünf Experimente (🔬), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)
st.info(MODELL_HINWEIS)

with st.expander("So funktioniert das Einfügen nach Schensted", expanded=True):
    st.markdown(
        """
1. **Einfügen:** Die Folge wird der Reihe nach in eine erste Zeile eingefügt. Ist der neue Wert größer als alle Einträge der Zeile, kommt er ans Ende. Sonst **ersetzt er
   den ersten Eintrag, der größer ist**, und der Verdrängte wird auf dieselbe Weise in die nächste Zeile eingefügt, bis ein Eintrag ans Zeilenende passt oder eine neue Zeile beginnt.
   Das Ergebnis ist das Tableau **P**: die Zeilen wachsen nach rechts, die Spalten nach unten.
2. **Aufzeichnen:** Das Tableau **Q** bekommt im Schritt i an der Stelle, an der P gewachsen ist, die Zahl i. Beide haben immer dieselbe Form (λ).
3. **Ablesen:** Die erste Zeile von λ ist die längste wachsende Teilfolge und damit die Mindestzahl **fallender** Stapel (ein Container kommt nur auf einen Stapel mit größerem
   Rang); die Zeilenzahl ist die längste fallende Teilfolge. Bei wachsenden Stapeln liest man die erste Spalte.
4. **Zurückrechnen:** Aus P und Q folgt die Folge: Q nennt die Zelle, die der letzte Schritt geschaffen hat; der Eintrag dort wandert Zeile für Zeile nach oben zurück und fällt
   oben als letzter Wert der Folge heraus.
5. **Warum zählt das:** Jede Folge ergibt genau ein Paar gleichförmiger Standardtableaux, und jedes Paar kommt vor (Lehrsatz nach Schensted; die Demo zählt es bis n = 8 durch Aufzählung nach).
   Zu einer Form λ gehören also f² Folgen (f = Zahl der Standardtableaux von λ), und die Summe aller f² ist n!.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Zufall**")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1,
                           help="Steuert die Zufallsfolge in Experiment 1, die Folgen in Experiment 3 und das Zufallswort in Experiment 5.")
    st.button("🎲 Neuen Zufalls-Seed würfeln", width="stretch", on_click=randomize_seed)
    st.caption("Alle anderen Regler stehen bei den Experimenten.")

sync_query_params({key: st.session_state[key] for key in (
    "seed_input", "e1_text", "e1_n", "e1_schritt", "e1_orient", "e1_zurueck", "e2_n", "e2_hl", "e3_d", "e3_n", "e3_anzahl", "e4_t", "e4_n", "e5_inhalt", "e5_text", "e5_fassung")})

seed = int(seed)

# Eingaben lesen (die Regler stehen weiter unten; ihr Wert liegt im Session State)
folge_eingabe, hinweis1, fehler1 = S.folge_einlesen(st.session_state["e1_text"], C.E1_MAX_LAENGE)
folge1 = folge_eingabe or S.folge_einlesen(C.DEFAULT_TEXT, C.E1_MAX_LAENGE)[0]
fallend = st.session_state["e1_orient"] == C.ORIENT_FALLEND
analyse1 = _analyse_folge(folge1, fallend)
n2 = int(st.session_state["e2_n"])
t4, n4 = int(st.session_state["e4_t"]), int(st.session_state["e4_n"])
zuege4 = _zugtabelle(t4)

# --- Kernfragen --------------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
st.markdown("**1. Wie wird aus einer Folge ein Paar von Tableaux, und was lese ich ab?** (Experiment 1)")
_zeige(ev.kernfrage_1(analyse1))
st.markdown("**2. Wie viele Folgen gehören zu welcher Form?** (Experiment 2)")
_zeige(ev.kernfrage_2(_formen(n2)))
st.markdown("**3. Wo verwechselt man Tableaux, Zugfolgen und Folgen?** (Experiment 4)")
_zeige(ev.kernfrage_3(zuege4, t4, n4))

st.markdown("---")

# --- Experiment 1 ------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Einfügen Schritt für Schritt")
st.caption(
    "Eine Folge der Abholränge in Ankunftsreihenfolge (Rang 1 fährt zuerst), ohne gleiche Werte; sind die Werte nicht 1 bis n, werden sie auf Ränge umgerechnet. "
    "Orange: im letzten Schritt verdrängte Einträge; grün: die neue Zelle; getönt: die abgelesene Zeile oder Spalte."
)
k1, k2 = st.columns([3, 2])
with k1:
    st.text_input("Folge (Zahlen durch Leerzeichen getrennt, bis 12 Zahlen)", key="e1_text", max_chars=80)
with k2:
    st.radio("Stapel in der Maschine", C.ORIENTIERUNGEN, key="e1_orient",
             help="Fallende Stapel: ein Container kommt nur auf einen Stapel mit größerem Rang; die Mindestzahl Stapel ist die erste Zeile (längste wachsende Teilfolge). "
                  "Wachsende Stapel: umgekehrt; dann ist es die erste Spalte (längste fallende Teilfolge). „Zeile“ und „Spalte“ sind eine Namenskonvention.")
z1, z2, z3 = st.columns([2, 2, 3])
with z1:
    st.slider("Länge n der Zufallsfolge (für den Knopf rechts)", *bounds("e1_n"), key="e1_n")
with z2:
    st.write("")
    st.button("🎲 Zufallsfolge würfeln", on_click=_zufallsfolge_wuerfeln, width="stretch",
              help="Eine gleichverteilte Folge aus dem Zufalls-Seed der Seitenleiste (alle n! Folgen gleich wahrscheinlich).")
with z3:
    st.toggle("Zurückrechnen zeigen", key="e1_zurueck", help="Zeigt, wie aus P und Q Schritt für Schritt die Folge zurückkommt.")

if fehler1:
    st.warning(fehler1 + " Angezeigt wird solange die Handfolge (1, 3, 6, 2, 5, 4).")
elif hinweis1:
    st.info(hinweis1)

n1 = len(folge1)
if n1 >= 2:
    st.session_state["e1_schritt"] = min(max(int(st.session_state["e1_schritt"]), 1), n1)
    i = st.slider("Schritt i: die Folge ist bis zur i-ten Ankunft eingefügt", 1, n1, key="e1_schritt")
else:
    i = 1
P_fin, Q_fin, schritte = R.einfuegen_protokoll(folge1)
max_z, max_s = len(P_fin), len(P_fin[0])
schritt_i = schritte[i - 1]
bewegt = {(r, c) for r, c, _, y in schritt_i.verdraengungen if y is not None}
P_i = [list(z) for z in schritt_i.p_danach]
Q_i = [[x for x in z if x <= i] for z in Q_fin]
Q_i = [z for z in Q_i if z]
lesen = "zeile" if fallend else "spalte"
cp, cq = st.columns(2)
with cp:
    st.plotly_chart(build_tableau(P_i, f"P nach Schritt {i}", max_z, max_s, bewegt=bewegt, neu=schritt_i.neue_zelle, lesen=lesen), width="stretch", key="e1_p", config={"displayModeBar": False})
with cq:
    st.plotly_chart(build_tableau(Q_i, f"Q nach Schritt {i}", max_z, max_s, neu=schritt_i.neue_zelle, lesen=lesen, farbe="rgba(76,120,168,0.16)"), width="stretch", key="e1_q",
                    config={"displayModeBar": False})
st.markdown(f"**Schritt {i}:** der Wert {schritt_i.wert} wird eingefügt: {ev.schritt_text(schritt_i)}. Form von P und von Q jetzt: {form_text(R.form(P_i))}.")

sa, sb = st.columns(2)
with sa:
    nach_i = R.stapel_bilden(folge1[:i], fallend=fallend)
    st.markdown(f"**Stapel nach {i} Ankünften** ({'fallend' if fallend else 'wachsend'}, jeder von unten nach oben; ein Container kommt auf den ersten passenden Stapel):")
    st.code(ev.stapel_text(nach_i), language=None)
    st.caption(f"{len(nach_i)} Stapel = {'erste Zeile' if fallend else 'erste Spalte'} der Form von Q bis {i}. Die beiden Kurven rechts fallen zusammen, weil Q so gebaut ist "
               "(Zelle von Schritt i); das ist eine Konstruktion, kein zweiter Befund.")
with sb:
    st.plotly_chart(build_verlauf(analyse1.verlauf, analyse1.q_verlauf, i, fallend), width="stretch", key="e1_verlauf", config={"displayModeBar": False})

with st.expander("Alle Einfügeschritte bis Schritt i"):
    _grid([{"Schritt": s.nummer, "Wert": s.wert, "was passiert": ev.schritt_text(s), "neue Zelle (Zeile, Spalte)": f"({s.neue_zelle[0] + 1}, {s.neue_zelle[1] + 1})"}
           for s in schritte[:i]])

if st.session_state["e1_zurueck"]:
    st.markdown("**Zurückrechnen aus P und Q (letzter Schritt zuerst):**")
    folge_zurueck, rueck = R.zurueckrechnen_protokoll(P_fin, Q_fin)
    _grid([{"rückgängig": r.nummer, "was passiert": ev.rueck_text(r)} for r in rueck])
    if folge_zurueck == folge1:
        st.success(f"Ergebnis: {folge_text(folge_zurueck)} – das ist die eingegebene Folge.")
    else:
        st.error(f"FEHLER: zurückgerechnet {folge_text(folge_zurueck)}, eingegeben {folge_text(folge1)}.")

_zeige(ev.verdict_einfuegen(analyse1))

st.markdown("---")

# --- Experiment 2 ------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie viele Folgen gehören zu welcher Form?")
st.caption(
    "Zähleinheit: **Folgen** (alle n! Anordnungen der Ränge 1 bis n, gleich wahrscheinlich im Modell U). Die Zahl der Folgen mit der Form λ ist f², weil das Einfügen "
    "jeder Folge ein Paar gleichförmiger Standardtableaux zuordnet; f kommt aus der Hakenformel (Ganzzahlen, bis n = 30). Zum Nachzählen werden bis n = 8 alle Folgen aufgezählt; "
    "n = 9 ist vorgerechnet."
)
e2a, e2b = st.columns([3, 2])
with e2a:
    st.slider("Länge n der Folgen", *bounds("e2_n"), key="e2_n")
with e2b:
    st.radio("Hervorheben", C.HERVORHEBUNGEN, key="e2_hl", horizontal=True,
             help="Orange: Formen mit höchstens 2 Zeilen (längste fallende Teilfolge höchstens 2) bzw. höchstens 2 Spalten (längste wachsende Teilfolge höchstens 2). "
                  "Beide Mengen haben Catalan(n) Folgen.")
z2 = _formen(n2)
zeilen2 = H.formverteilung(n2)
auf = None
auf_live = True
if n2 <= E.LIVE_MAX_N:
    auf = _aufzaehlung(n2)
elif n2 == 9:
    tab = _eingefroren()
    auf = tab.get(9) if tab else None
    auf_live = False
g1, g2 = st.columns([3, 2])
with g1:
    st.plotly_chart(build_formen_balken(zeilen2, st.session_state["e2_hl"], C.E2_TOP), width="stretch", key="e2_balken", config={"displayModeBar": False})
    if len(zeilen2) > C.E2_TOP:
        st.caption(f"Gezeigt sind die {C.E2_TOP} häufigsten von {len(zeilen2)} Formen.")
with g2:
    _grid([{"Form": form_text(lam), "f": ganz(f), "f² = Folgen": ganz(f2), "Anteil (%)": round(float(a) * 100, 3)} for lam, f, f2, a in zeilen2[: C.E2_TOP]])
    haken = H.hakenlaengen(z2.haeufigste[0])
    st.markdown(f"**Hakenlängen der häufigsten Form {form_text(z2.haeufigste[0])}:**")
    st.code("\n".join(" ".join(f"{h:3d}" for h in zeile) for zeile in haken), language=None)
    st.caption(f"f = {ganz(z2.f_haeufigste)} = {z2.n}! geteilt durch das Produkt dieser Hakenlängen.")
if n2 > 9:
    st.caption("Ab n = 10 wird nicht mehr aufgezählt (3 628 800 Folgen bei n = 10): die Zahlen kommen aus der Hakenformel.")
_zeige(ev.verdict_formen(z2, auf, auf_live))

tab = _eingefroren()
if tab:
    with st.expander("Dieselbe Zahl, andere Menge: Überlappung für n = 1 bis 9 (vorgerechnet)"):
        st.caption("Ein Stapel sortiert Catalan(n) Folgen (231-vermeidend); „höchstens 2 Spalten“ (längste wachsende Teilfolge höchstens 2, zwei fallende Stapel mit Verzögerung) "
                   "trifft ebenfalls Catalan(n) Folgen. Gemeinsam sind es viel weniger. Die Formeln C(n,2) + 1 und 2^(n−1) sind **Zahlenmuster aus n ≤ 9**, kein Beweis.")
        _grid([{"n": n, "Catalan(n)": ganz(H.catalan(n)), "ein Stapel sortiert": ganz(e["stapel"]), "höchstens 2 Spalten": ganz(e["lis2"]),
                "gemeinsam": ganz(e["stapel_lis2"]), "C(n,2) + 1": ganz(n * (n - 1) // 2 + 1), "Stapel und höchstens 2 Zeilen": ganz(e["stapel_lds2"]),
                "2^(n−1)": ganz(2 ** (n - 1)), "beide Grenzen 2 (ohne Stapelbedingung)": ganz(e["lis2_lds2"])} for n, e in sorted(tab.items())])

st.markdown("---")

# --- Experiment 3 ------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Die Form im ausgedachten Modell V (Verweilzeit D)")
st.caption(
    "**Modell V ist ausgedacht** (keine reale Ankunftsfolge): Container i kommt zur Zeit i an und bleibt eine exponentialverteilte Zeit mit dem Mittel D (in Ankunftsabständen); "
    "der Rang ist die Reihenfolge der Abfahrten. D klein: fast sortiert; D → ∞: alle Folgen gleich wahrscheinlich (Modell U). Zähleinheit: Folgen. "
    "Oben die eigene Einstellung (live gerechnet), darunter die vorgerechnete Tabelle für n = 10 mit je 20 000 Folgen."
)
v1, v2, v3 = st.columns(3)
with v1:
    st.select_slider("Mittlere Verweilzeit D", options=C.D_LABELS, key="e3_d", help="In Ankunftsabständen; ∞ heißt alle Folgen gleich wahrscheinlich.")
with v2:
    st.slider("Länge n der Folgen", *bounds("e3_n"), key="e3_n")
with v3:
    st.slider("Zahl der Folgen", *bounds("e3_anzahl"), key="e3_anzahl", step=C.E3_ANZAHL_SCHRITT, help="Rund 0,4 Sekunden je 1 000 Folgen bei n = 10.")
d3 = dict(zip(C.D_LABELS, S.D_WERTE))[st.session_state["e3_d"]]
n3, anzahl3 = int(st.session_state["e3_n"]), int(st.session_state["e3_anzahl"])
stat3 = _modellv(n3, d3, anzahl3, seed)
m1, m2, m3 = st.columns(3)
m1.metric("Mittlere erste Zeile", de_fest(stat3["mittel_erste_zeile"], 3), delta=f"± {de_fest(stat3['se_erste_zeile'], 3)} Standardfehler", delta_color="off")
m2.metric("Mittlere Zeilenzahl", de_fest(stat3["mittel_zeilenzahl"], 3), delta=f"exakt im Modell U: {de_fest(float(ev.exakt_modell_u(n3)), 4)}", delta_color="off")
m3.metric("Häufigste Form", form_text(stat3["top"]), delta=f"{prozent(stat3['top_anteil'])} der Folgen", delta_color="off")
h1, h2 = st.columns([3, 2])
with h1:
    st.plotly_chart(build_formen_live(stat3["formen"], stat3["anzahl"]), width="stretch", key="e3_formen", config={"displayModeBar": False})
with h2:
    top = stat3["top"]
    st.plotly_chart(build_tableau([[""] * c for c in top], f"häufigste Form {form_text(top)}", len(top), top[0], leer=True), width="stretch", key="e3_top",
                    config={"displayModeBar": False})
_zeige(ev.verdict_modellv_live(stat3, n3, d3, seed))

tabv = _modellv_tabelle()
if tabv:
    st.markdown("**Vorgerechnet: n = 10, je 20 000 Folgen, zwei Zufalls-Seeds**")
    exakt10 = float(ev.exakt_modell_u(tabv["n"]))
    st.plotly_chart(build_modellv_linien(tabv, exakt10), width="stretch", key="e3_linien", config={"displayModeBar": False})
    s0, s1 = (str(s) for s in tabv["seeds"])
    _grid([{"D": S.d_text(z["d"]), f"erste Zeile (Seed {s0})": de_fest(z["seeds"][s0]["mittel_erste_zeile"], 3), f"erste Zeile (Seed {s1})": de_fest(z["seeds"][s1]["mittel_erste_zeile"], 3),
            f"Zeilenzahl (Seed {s0})": de_fest(z["seeds"][s0]["mittel_zeilenzahl"], 3), f"häufigste Form (Seed {s0})": form_text(tuple(z["seeds"][s0]["top"])),
            f"Anteil (Seed {s0})": prozent(z["seeds"][s0]["top_anteil"], 2), "Formen gesehen (von 42)": z["seeds"][s0]["formen"]} for z in tabv["zeilen"]])
    _zeige(ev.verdict_modellv_tabelle(tabv))
else:
    st.warning("Die vorgerechnete Tabelle (data/trk_modellv.json) fehlt; `tools/trk_make_modellv.py` erzeugt sie.")

st.markdown("---")

# --- Experiment 4 ------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Zugfolgen gegen Folgen (die Falle der Zähleinheit)")
st.caption(
    "t Stapel in Serie: die Container 1 bis n kommen in dieser Reihenfolge an; jeder Zug legt den nächsten Container auf den ersten Stapel (a), setzt eine Spitze auf den nächsten Stapel "
    "(b, bei drei Stapeln auch c) oder gibt die Spitze des letzten Stapels aus. Eine **Zugfolge** ist eine vollständige Zugreihe, die **Ausgabe** die Folge der ausgegebenen Container. "
    "Die Hakenformel des Rechtecks (t + 1) × n zählt die Zugfolgen. Aufgezählt wird bis n = 8 (t = 1), 6 (t = 2) und 4 (t = 3); t = 2 mit n = 7 und t = 3 mit n = 5 sind vorgerechnet."
)
w1, w2 = st.columns(2)
with w1:
    st.slider("Zahl der Stapel in Serie t", *bounds("e4_t"), key="e4_t")
with w2:
    st.slider("Zahl der Container n", *bounds("e4_n"), key="e4_n")
_grid([{"n": z["n"], "Zugfolgen": "–" if z["zugfolgen"] is None else ganz(z["zugfolgen"]), "Hakenformel Rechteck": ganz(z["haken"]),
        "verschiedene Folgen": "–" if z["ausgaben"] is None else ganz(z["ausgaben"]), "alle Folgen (n!)": ganz(math.factorial(z["n"])),
        "Zugfolgen je Folge": "–" if z["je_ausgabe"] is None else de_fest(float(z["je_ausgabe"]), 2), "Quelle": z["quelle"]} for z in zuege4])
st.plotly_chart(build_zuege(zuege4), width="stretch", key="e4_zuege", config={"displayModeBar": False})
if n4 <= Z.LIVE_GRENZE[t4]:
    det = _zugdetail(t4, n4)
    if det.woerter:
        st.markdown(f"**Alle {len(det.woerter)} Zugfolgen für t = {t4}, n = {n4}** (a einlegen, {'b umsetzen' if t4 == 2 else 'b und c umsetzen' if t4 == 3 else 'b ausgeben'}"
                    f"{', c ausgeben' if t4 == 2 else ', d ausgeben' if t4 == 3 else ''}):")
        _grid([{"Zugfolge": w, "Ausgabe": folge_text(a)} for w, a in det.woerter])
    else:
        st.caption(f"Für t = {t4}, n = {n4} sind es {ganz(det.zugfolgen)} Zugfolgen: zu viele zum Auflisten (Grenze {C.E4_WOERTER_BIS}).")
_zeige(ev.verdict_zuege(zuege4, t4, n4))

st.markdown("---")

# --- Experiment 5 ------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Gleichstände – Wörter mit Zielgruppen")
st.caption(
    "Wagen mit Zielgruppen: mehrere Container haben denselben Rang (dieselbe Zielgruppe). Dann ist die Eingabe keine Permutation, sondern ein **Wort**, und es gibt zwei Fassungen "
    "des Einfügens. Hier gilt: ein Stapel darf einen Container mit gleichem Rang aufnehmen (schwach fallende Stapel); die Mindestzahl Stapel ist dann die längste **streng** wachsende "
    "Teilfolge. Zähleinheit: Wörter (nicht Folgen)."
)
x1, x2 = st.columns([1, 2])
with x1:
    st.selectbox("Inhalt (Wagen je Zielgruppe)", C.INHALTE, key="e5_inhalt", on_change=_inhalt_gewaehlt,
                 help="(2,2,2): drei Zielgruppen zu je zwei Wagen; mit der Auswahl wird ein Beispielwort gesetzt.")
with x2:
    st.text_input("Wort (Zielgruppen 1, 2, … durch Leerzeichen getrennt)", key="e5_text", max_chars=40)
y1, y2 = st.columns([2, 1])
with y1:
    st.radio("Fassung des Einfügens", C.FASSUNGEN, key="e5_fassung", horizontal=True,
             help="Streng: ein neuer Wert verdrängt den ersten Eintrag, der größer oder gleich ist (Zeilen streng wachsend). Schwach (Lehrbuch): nur den ersten, der größer ist.")
with y2:
    st.button("🎲 Zufälliges Wort würfeln", on_click=_zufallswort_wuerfeln, width="stretch", help="Ein gleichverteiltes Wort mit diesem Inhalt aus dem Zufalls-Seed der Seitenleiste.")
inhalt5 = _inhalt_von(st.session_state["e5_inhalt"])
wort5, fehler5 = S.wort_einlesen(st.session_state["e5_text"], inhalt5)
if fehler5:
    st.warning(fehler5 + " Angezeigt wird solange das Standardwort.")
    wort5 = S.standardwort(inhalt5)
dual5 = st.session_state["e5_fassung"] == C.FASSUNG_STRENG
a5 = _wort(inhalt5, wort5, dual5)
max_z5, max_s5 = len(a5.P), len(a5.P[0])
cw1, cw2 = st.columns(2)
with cw1:
    st.plotly_chart(build_tableau(a5.P, "P (Zeilen " + ("streng" if dual5 else "schwach") + " wachsend, Spalten " + ("schwach" if dual5 else "streng") + ")", max_z5, max_s5, lesen="zeile"),
                    width="stretch", key="e5_p", config={"displayModeBar": False})
with cw2:
    st.plotly_chart(build_tableau(a5.Q, "Q", max_z5, max_s5, farbe="rgba(76,120,168,0.16)", lesen="zeile"), width="stretch", key="e5_q", config={"displayModeBar": False})
st.markdown(
    f"**Stapel mit gleichem Rang erlaubt (schwach fallend):** {ev.stapel_text(a5.stapel_schwach)} = {len(a5.stapel_schwach)} Stapel, Gegenprobe durch Probieren {a5.probiert_schwach}; "
    f"längste streng wachsende Teilfolge {a5.lis_streng}.  \n"
    f"**Nur streng fallende Stapel:** {ev.stapel_text(a5.stapel_streng)} = {len(a5.stapel_streng)} Stapel, Gegenprobe {a5.probiert_streng}; längste schwach wachsende Teilfolge {a5.lis_schwach}."
)
st.plotly_chart(build_woerter_balken(a5.je_form), width="stretch", key="e5_balken", config={"displayModeBar": False})
_grid([{"Form": form_text(z[0]), "f": ganz(z[1]), "Kostka-Zahl": ganz(z[2]), "f · Kostka": ganz(z[3]), "gezählt": ganz(z[4])} for z in a5.je_form])
st.caption("Die Kostka-Zahl ist die Zahl der Füllungen der Form (bei der dualen Fassung: der transponierten Form) mit dem Inhalt; sie wird getrennt von der Aufzählung berechnet.")
_zeige(ev.verdict_woerter(a5))

st.markdown("---")

# --- Grenzen -----------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wo |
|---|---|---|
| **Die Folge hat keine gleichen Werte** | Mit gleichen Werten gibt es zwei Fassungen des Einfügens; bei Inhalt (2,2,2) geben streng und schwach in 74 von 90 Wörtern verschiedene längste wachsende Teilfolgen. Die Zahl der Wörter je Form ist f · Kostka-Zahl, nicht f². | Experiment 5 |
| **Zählen heißt Folgen zählen** | Die Hakenformel zählt Tableaux und Zugfolgen. Zwei Stapel in Serie haben bei n = 7 genau 1 385 670 Zugfolgen für nur 5 018 verschiedene Folgen. | Experiment 4 |
| **Dieselbe Zahl heißt dieselbe Menge** | Catalan(n) zählt die Folgen, die ein Stapel sortiert, und die Folgen mit höchstens 2 Zeilen; gemeinsam sind bei n = 6 nur 16 von 132. | Experiment 2 |
| **Die Ankunftsfolge stammt aus Modell U oder V** | Beides ist ausgedacht; Modell V ist nur für n = 10 und sieben Werte von D vorgerechnet. Über eine reale Ankunftsfolge sagt die Seite nichts. | Experiment 3 |
| **Die Zahlen gelten bis zu den aufgezählten Grenzen** | Aufgezählt sind alle Folgen bis n = 8 (n = 9 nur die Formenzählung); Σ f² = n! und die Summe der f (Involutionen) sind bis n = 14 gerechnet, darüber gilt es als Lehrsatz. Grenzformen für große n sind nicht gemessen. | Experiment 2 |
| **„Zeile“ heißt Stapelzahl** | Das gilt für fallende Stapel; bei wachsenden Stapeln ist es die erste Spalte. Die Namen sind eine Konvention. | Experiment 1 |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben und gesucht.** Gegeben ist eine Folge $p = (p_1, \dots, p_n)$ der Ränge $1, \dots, n$ (jeder Rang einmal). Gesucht sind zwei Standardtableaux $P$ und $Q$ gleicher Form
$\lambda$ und die Antwort auf zwei Fragen: Welche Zahlen liest man an $\lambda$ ab, und wie viele Folgen haben die Form $\lambda$?

| Symbol | Bedeutung |
|---|---|
| $p$ | Ankunftsfolge der Abholränge (eine Permutation von $1, \dots, n$) |
| $\lambda = (\lambda_1 \ge \lambda_2 \ge \dots)$ | Form: Zeilenlängen von $P$ (und $Q$), eine Partition von $n$ |
| $P$ | Einfügetableau: Zeilen wachsen nach rechts, Spalten nach unten |
| $Q$ | Aufzeichnungstableau: Eintrag $i$ in der Zelle, in der $P$ im Schritt $i$ gewachsen ist |
| $h(c)$ | Hakenlänge der Zelle $c$: Zellen rechts davon plus Zellen darunter plus 1 |
| $f^\lambda$ | Zahl der Standardtableaux der Form $\lambda$ |
| $t$ | Zahl der Stapel in Serie (Experiment 4) |

**Einfügen (Schensted).** Der Wert $x$ wird in die erste Zeile eingefügt: Gibt es keinen größeren Eintrag, steht $x$ am Zeilenende; sonst ersetzt $x$ den **ersten** Eintrag $y > x$,
und $y$ wird auf dieselbe Weise in die nächste Zeile eingefügt, bis ein Wert ans Zeilenende passt oder eine neue Zeile beginnt. $P$ entsteht durch Einfügen von $p_1, \dots, p_n$;
$Q$ bekommt im Schritt $i$ die Zahl $i$ in die Zelle, in der $P$ gewachsen ist. Die Form von $Q$ mit den Einträgen $\le i$ ist die Form von $P$ nach $i$ Schritten.

**Umkehrung.** Der Schritt $n$ schuf die Zelle von $Q$ mit der Zahl $n$. Ihren Eintrag $y$ aus $P$ entfernen; in der Zeile darüber den **rechtesten** Eintrag $z < y$ suchen, $y$ an seine Stelle
setzen und $z$ in die nächste Zeile nach oben weitergeben, bis oben ein Wert herausfällt: das ist $p_n$. Danach mit $n - 1$ weiter. Deshalb ist $p \mapsto (P, Q)$ umkehrbar.

**Ablesen.** Die erste Zeile $\lambda_1$ ist die Länge der längsten wachsenden Teilfolge (LIS) und gleich der Mindestzahl **fallender** Stapel; die Zeilenzahl ist die Länge der längsten
fallenden Teilfolge (LDS). Bei wachsenden Stapeln ist die Mindestzahl die LDS (erste Spalte).

**Zählen.** Jede Folge gibt genau ein Paar gleichförmiger Standardtableaux, und jedes solche Paar kommt vor. Also hat genau $(f^\lambda)^2$ Folgen die Form $\lambda$, und
$$\sum_{\lambda \vdash n} \left(f^\lambda\right)^2 = n!, \qquad f^\lambda = \frac{n!}{\prod_{c \in \lambda} h(c)}.$$
Die Summe der $f^\lambda$ über alle Formen ist die Zahl der Folgen mit $p = p^{-1}$ (Involutionen). Der Anteil der Form $\lambda$ im Modell U ist $(f^\lambda)^2 / n!$.

**Zugfolgen.** Bei $t$ Stapeln in Serie ist jede vollständige Zugreihe ein Wort der Länge $n(t+1)$ mit $n$ Einlegezügen; die Wörter stehen in Bijektion mit den Standardtableaux des Rechtecks
$(t+1) \times n$ (Bóna 2003). Ihre Zahl ist $f^{((n)^{t+1})}$ nach der Hakenformel. Verschiedene Zugfolgen können dieselbe Ausgabe haben; nur bei $t = 1$ gehört zu jeder Ausgabe genau eine Zugfolge (gemessen für $t \le 3$; bei $t \ge 2$ und $n \ge 2$ gibt es in allen gerechneten Fällen mehrere).

**Wörter.** Bei gleichen Werten (Inhalt $\mu$) hat die duale Einfügung ($x$ ersetzt den ersten Eintrag $\ge x$) streng wachsende Zeilen und schwach wachsende Spalten; die erste Zeile ist die längste streng
wachsende Teilfolge. Die Zahl der Wörter mit der Form $\lambda$ ist $f^\lambda \cdot K_{\lambda',\mu}$ mit der Kostka-Zahl $K$ (Zahl der Füllungen der transponierten Form $\lambda'$ mit dem Inhalt $\mu$).

**Vollständigkeit.** Das ist das ganze Verfahren (Einfügeregel, Umkehrregel, Hakenformel). Nicht bewiesen wird hier, dass die Zuordnung eine Bijektion ist und dass die erste Zeile die LIS ist: beides ist Lehrbuchstoff
(Schensted 1961, Satz 1 und 2, Lemma 3) und wird von der Demo durch Aufzählung nachgeprüft (alle Folgen bis $n = 8$, $n = 9$ nur die Formenzählung).

**Literatur.** Schensted, C. (1961): Longest increasing and decreasing subsequences, *Canadian Journal of Mathematics* 13, 179–191 (Seiten 179 bis 185 gelesen: Einfügen, Lemma 1 bis 3, Satz 1 und 2; die Hakenformel steht
dort als Zitat von Frame, Robinson und Thrall). Bóna, M. (2003): A survey of stack-sorting disciplines, *Electronic Journal of Combinatorics* 9(2), #A1, § 3 Gl. (1): Stapelwörter und Rechtecktableaux (gelesen).
Nicht gelesen sind Knuth, *The Art of Computer Programming* Bd. 3 (§ 5.1.4), Fulton, Sagan und Stanley (Enumerative Combinatorics Bd. 2, Kap. 7): sie werden nur als Lehrbuchstoff genannt.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
