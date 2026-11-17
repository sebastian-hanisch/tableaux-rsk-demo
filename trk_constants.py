"""Konstanten: Regler-Grenzen, Voreinstellungen, Farben und Schnellstart-Szenarien."""

SEED_MAX, DEFAULT_SEED = 999999, 101

# Experiment 1: eine Folge einfügen
E1_MAX_LAENGE = 12                 # längste eingegebene Folge
E1_N_MIN, E1_N_MAX, E1_DEFAULT_N = 3, 12, 6   # Länge der Zufallsfolge
DEFAULT_TEXT = "1 3 6 2 5 4"       # die Handfolge
ORIENT_FALLEND = "Stapel fallend: Stapelzahl = erste Zeile"
ORIENT_WACHSEND = "Stapel wachsend: Stapelzahl = erste Spalte"
ORIENTIERUNGEN = (ORIENT_FALLEND, ORIENT_WACHSEND)

# Experiment 2: Formen
E2_N_MIN, E2_N_MAX, E2_DEFAULT_N = 2, 30, 6
HL_KEINE, HL_ZEILEN, HL_SPALTEN = "keine", "höchstens 2 Zeilen", "höchstens 2 Spalten"
HERVORHEBUNGEN = (HL_KEINE, HL_ZEILEN, HL_SPALTEN)
E2_TOP = 24                        # so viele häufigste Formen zeigt das Balkendiagramm höchstens

# Experiment 3: Modell V
D_LABELS = ("0,5", "1", "2", "4", "8", "16", "∞")
E3_N_MIN, E3_N_MAX, E3_DEFAULT_N = 6, 12, 10
E3_ANZAHL_MIN, E3_ANZAHL_MAX, E3_ANZAHL_SCHRITT, E3_DEFAULT_ANZAHL = 500, 3000, 500, 1000

# Experiment 4: Zugfolgen
E4_T_MIN, E4_T_MAX, E4_DEFAULT_T = 1, 3, 1
E4_N_MIN, E4_N_MAX, E4_DEFAULT_N = 1, 8, 4
E4_WOERTER_BIS = 42                # so viele Zugfolgen werden höchstens als Buchstabenwörter aufgelistet

# Experiment 5: Wörter mit Zielgruppen
INHALTE = ("(2,2,2)", "(3,2,1)", "(2,2,1,1)", "(2,1,1,1)", "(3,3)", "(2,2,2,1)", "(1,1,1,1,1)")
DEFAULT_INHALT = "(3,2,1)"
DEFAULT_WORT = "1 2 1 3 2 1"
FASSUNG_STRENG = "streng wachsend (duale Einfügung)"
FASSUNG_SCHWACH = "schwach wachsend (Lehrbuch)"
FASSUNGEN = (FASSUNG_STRENG, FASSUNG_SCHWACH)

COLOR_P = "#2F6B65"
COLOR_Q = "#4c78a8"
COLOR_NEU = "#2F6B65"
COLOR_BEWEGT = "#e9a23b"
COLOR_ZELLE = "rgba(76,120,168,0.16)"
COLOR_HERVOR = "#e9a23b"
COLOR_LINE = "#4c78a8"
COLOR_LINE2 = "#d9534f"
COLOR_GRAU = "rgba(150,150,150,0.55)"

PRESETS = {
    "Handfolge n = 6 (1,3,6,2,5,4)": {"e1_text": DEFAULT_TEXT, "e1_schritt": 6},
    "Alle Folgen n = 4": {"e2_n": 4},
    "Ein Stapel gegen zwei: (3,4,1,2)": {"e1_text": "3 4 1 2", "e1_schritt": 4},
    "Formverteilung n = 10": {"e2_n": 10},
    "Verweilzeit D = 4": {"e3_d": "4", "e3_n": 10},
    "Zugfolgen: zwei Stapel, n = 4": {"e4_t": 2, "e4_n": 4},
    "Zielgruppen (2,2,2)": {"e5_inhalt": "(2,2,2)", "e5_text": "1 3 2 2 3 1"},
}
PRESET_HELP = {
    "Handfolge n = 6 (1,3,6,2,5,4)": "Die Folge (1, 3, 6, 2, 5, 4): Experiment 1 zeigt Schritt für Schritt, wie P und Q entstehen (Form (3,2,1), f = 16).",
    "Alle Folgen n = 4": "Experiment 2 mit n = 4: alle 24 Folgen, fünf Formen, zum Nachzählen von Hand.",
    "Ein Stapel gegen zwei: (3,4,1,2)": "Die Folge (3, 4, 1, 2): ein Stapel sortiert sie nicht, zwei fallende Stapel genügen (Experiment 1, Stapelzahl und Form).",
    "Formverteilung n = 10": "Experiment 2 mit n = 10: 42 Formen, die häufigste (4,3,2,1) hat 589 824 von 3 628 800 Folgen.",
    "Verweilzeit D = 4": "Experiment 3 im ausgedachten Modell V mit der mittleren Verweilzeit D = 4 und n = 10 Containern.",
    "Zugfolgen: zwei Stapel, n = 4": "Experiment 4 mit zwei Stapeln in Serie und n = 4: 462 Zugfolgen für nur 24 verschiedene Folgen.",
    "Zielgruppen (2,2,2)": "Experiment 5: Wörter mit drei Zielgruppen zu je zwei Wagen (90 Wörter), duale Einfügung.",
}
