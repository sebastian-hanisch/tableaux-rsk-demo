"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben.

Tableaux werden in englischer Schreibweise gezeichnet: die erste Zeile oben, die Zeilen nach unten kürzer. Beschriftungen sind Annotationen (kein Text-Trace)."""

import math

import plotly.graph_objects as go

import trk_constants as C
from trk_texts import form_text


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_tableau(T, titel, max_zeilen, max_spalten, bewegt=(), neu=None, farbe=C.COLOR_ZELLE, leer=False, lesen=None):
    """Ein Young-Tableau als Kästchen mit Zahlen. `bewegt`: Zellen (Zeile, Spalte), deren Eintrag im letzten Schritt ersetzt wurde; `neu`: die neue Zelle.
    `leer=True` zeichnet nur die Form ohne Zahlen. `lesen`: "zeile" oder "spalte" tönt die erste Zeile bzw. erste Spalte (die abgelesene Stapelzahl). Der Zeichenbereich ist fest (max_zeilen × max_spalten), damit das Bild beim Weiterschalten nicht springt."""
    fig = go.Figure()
    for r, zeile in enumerate(T):
        for c, x in enumerate(zeile):
            if neu == (r, c):
                fuell = C.COLOR_NEU
            elif (r, c) in bewegt:
                fuell = C.COLOR_BEWEGT
            elif (lesen == "zeile" and r == 0) or (lesen == "spalte" and c == 0):
                fuell = "rgba(233,162,59,0.30)"
            else:
                fuell = farbe
            fig.add_shape(type="rect", x0=c, x1=c + 1, y0=r, y1=r + 1, line=dict(color="rgba(120,120,120,0.9)", width=1.5), fillcolor=fuell, layer="below")
            if not leer:
                weiss = neu == (r, c)
                fig.add_annotation(x=c + 0.5, y=r + 0.5, text=f"<b>{x}</b>", showarrow=False, font=dict(size=15, color="white" if weiss else None))
    # zwei unsichtbare Marker an den Ecken erzwingen den festen Zeichenbereich
    fig.add_trace(go.Scatter(x=[0, max_spalten], y=[0, max_zeilen], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(range=[-0.05, max_spalten + 0.05], visible=False)
    fig.update_yaxes(range=[max_zeilen + 0.05, -0.05], visible=False)
    fig.update_layout(title=dict(text=titel, font=dict(size=14)), height=48 * max_zeilen + 60, margin=dict(l=10, r=10, t=36, b=6), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_verlauf(verlauf, q_verlauf, i, fallend):
    """Stapelzahl nach i Ankünften: aus der Stapelbildung und aus Q abgelesen (beide Kurven fallen zusammen: Q ist so gebaut)."""
    xs = list(range(1, len(verlauf) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=list(verlauf), mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3, shape="hv"), marker=dict(size=9),
                             name="Stapel gebildet", hovertemplate="nach %{x} Ankünften: %{y} Stapel<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=list(q_verlauf), mode="markers", marker=dict(symbol="diamond-open", size=15, color=C.COLOR_LINE2, line=dict(width=2)),
                             name="aus Q abgelesen", hovertemplate="Q bis %{x}: %{y}<extra></extra>"))
    fig.add_vline(x=i, line_dash="dot", line_color="rgba(120,120,120,0.9)")
    fig.update_xaxes(title_text="Ankünfte i", dtick=1, range=[0.5, len(xs) + 0.5])
    fig.update_yaxes(title_text="Stapelzahl", dtick=1, rangemode="tozero")
    return _base(fig, 280)


def build_formen_balken(zeilen, hl, top):
    """Anteil je Form (f²/n!) als waagrechte Balken der `top` häufigsten Formen. hl: 'keine', 'höchstens 2 Zeilen', 'höchstens 2 Spalten'."""
    zeilen = list(zeilen)[:top]
    namen, werte, farben = [], [], []
    for lam, _, _, anteil in zeilen:
        namen.append(form_text(lam))
        werte.append(float(anteil) * 100)
        markiert = (hl == C.HL_ZEILEN and len(lam) <= 2) or (hl == C.HL_SPALTEN and lam[0] <= 2)
        farben.append(C.COLOR_HERVOR if markiert else C.COLOR_P)
    fig = go.Figure(go.Bar(x=werte, y=namen, orientation="h", marker_color=farben, hovertemplate="%{y}: %{x:.2f} %<extra></extra>"))
    fig.update_yaxes(autorange="reversed", title_text="Form")
    fig.update_xaxes(title_text="Anteil der Folgen (%)")
    return _base(fig, max(260, 22 * len(namen) + 70))


def build_modellv_linien(tab, exakt_u, seed_index=0):
    """Mittlere erste Zeile und mittlere Zeilenzahl gegen D (vorgerechnet), Band über die beiden Zufalls-Seeds; waagrecht der exakte Wert im Modell U."""
    seeds = [str(s) for s in tab["seeds"]]
    labels = [("∞" if z["d"] is None else str(z["d"]).replace(".", ",")) for z in tab["zeilen"]]
    fig = go.Figure()
    for name, feld, farbe in (("mittlere erste Zeile (Stapel verzögert)", "mittel_erste_zeile", C.COLOR_LINE), ("mittlere Zeilenzahl", "mittel_zeilenzahl", C.COLOR_LINE2)):
        lo = [min(z["seeds"][s][feld] for s in seeds) for z in tab["zeilen"]]
        hi = [max(z["seeds"][s][feld] for s in seeds) for z in tab["zeilen"]]
        mitte = [z["seeds"][seeds[seed_index]][feld] for z in tab["zeilen"]]
        fig.add_trace(go.Scatter(x=labels + labels[::-1], y=hi + lo[::-1], fill="toself", fillcolor="rgba(150,150,150,0.25)", line=dict(width=0), hoverinfo="skip",
                                 showlegend=False))
        fig.add_trace(go.Scatter(x=labels, y=mitte, mode="lines+markers", line=dict(color=farbe, width=3), name=name,
                                 hovertemplate="D = %{x}: %{y:.3f}<extra></extra>"))
    fig.add_hline(y=exakt_u, line_dash="dot", line_color="rgba(120,120,120,0.9)", annotation_text=f"exakt Modell U: {exakt_u:.4f}".replace(".", ","), annotation_position="top right")
    fig.update_xaxes(title_text="mittlere Verweilzeit D (in Ankunftsabständen)", type="category")
    fig.update_yaxes(title_text="Mittel über 20 000 Folgen", rangemode="tozero")
    return _base(fig, 340)


def build_formen_live(formen, anzahl, top=12):
    """Verteilung der Formen der live gezogenen Folgen (häufigste zuerst)."""
    rang = sorted(formen.items(), key=lambda kv: (-kv[1], tuple(-x for x in kv[0])))[:top]
    fig = go.Figure(go.Bar(x=[form_text(l) for l, _ in rang], y=[c / anzahl * 100 for _, c in rang], marker_color=C.COLOR_P,
                           hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Form", type="category")
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig, 300)


def build_zuege(zeilen):
    """Zugfolgen, verschiedene Folgen und n! gegen n (logarithmische Achse)."""
    xs = [z["n"] for z in zeilen]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[z["haken"] for z in zeilen], mode="lines+markers", line=dict(color=C.COLOR_GRAU, dash="dot"), name="Hakenformel des Rechtecks",
                             hovertemplate="n = %{x}: %{y:,} (Hakenformel)<extra></extra>"))
    bekannt = [z for z in zeilen if z["zugfolgen"] is not None]
    fig.add_trace(go.Scatter(x=[z["n"] for z in bekannt], y=[z["zugfolgen"] for z in bekannt], mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3),
                             name="Zugfolgen", hovertemplate="n = %{x}: %{y:,} Zugfolgen<extra></extra>"))
    fig.add_trace(go.Scatter(x=[z["n"] for z in bekannt], y=[z["ausgaben"] for z in bekannt], mode="lines+markers", line=dict(color=C.COLOR_LINE2, width=3),
                             name="verschiedene Folgen", hovertemplate="n = %{x}: %{y:,} Folgen<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[math.factorial(n) for n in xs], mode="lines", line=dict(color="rgba(120,120,120,0.9)", dash="dash"), name="n! (alle Folgen)",
                             hovertemplate="n = %{x}: %{y:,}<extra></extra>"))
    fig.update_xaxes(title_text="Container n", dtick=1)
    fig.update_yaxes(title_text="Anzahl (logarithmisch)", type="log")
    return _base(fig, 340)


def build_woerter_balken(je_form, top=12):
    """Wörter je Form: Formel f · Kostka gegen gezählt (die beiden Balken müssen gleich lang sein)."""
    zeilen = list(je_form)[:top]
    namen = [form_text(z[0]) for z in zeilen]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=namen, y=[z[3] for z in zeilen], name="f · Kostka-Zahl", marker_color=C.COLOR_P, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.add_trace(go.Bar(x=namen, y=[z[4] for z in zeilen], name="gezählt", marker_color=C.COLOR_LINE2, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Form", type="category")
    fig.update_yaxes(title_text="Wörter")
    return _base(fig, 300)
