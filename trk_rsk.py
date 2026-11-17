"""Schensted-Einfügen: aus einer Folge werden zwei Tableaux (P und Q), und aus beiden lässt sich die Folge zurückrechnen.

Nur Standardbibliothek. Eine Folge ist hier ein Tupel von Abholrängen in Ankunftsreihenfolge. Ein Tableau ist eine Liste von Zeilen (Listen);
die Zeilen wachsen von links nach rechts, die Spalten von oben nach unten.

Zwei Fassungen des Einfügens (sie unterscheiden sich nur, wenn gleiche Werte vorkommen):
* `dual=False` (Lehrbuch): der neue Wert verdrängt in einer Zeile den **ersten Eintrag, der größer** ist. Zeilen schwach wachsend. Für Folgen ohne gleiche Werte
  ist das die einzige Fassung, die es gibt.
* `dual=True`: der neue Wert verdrängt den **ersten Eintrag, der größer oder gleich** ist. Zeilen streng wachsend, Spalten schwach wachsend. Dazu passen Stapel, auf
  die ein gleicher Rang noch passt (Wörter mit Zielgruppen, Experiment 5).

Alle Wege hier sind in linearer Suche geschrieben (n ist klein); der unabhängige Rechenweg der Tests steht in tests/test_oracle_tableaux_rsk.py."""

from dataclasses import dataclass


def _verdraengt(zeile, x, dual):
    """Index des ersten Eintrags der Zeile, den x verdrängt, sonst None (x kommt ans Ende)."""
    for j, y in enumerate(zeile):
        if (y >= x) if dual else (y > x):
            return j
    return None


@dataclass(frozen=True)
class Schritt:
    """Ein Einfügeschritt: der eingefügte Wert, die Wege durch die Zeilen und die Zelle, in der das Tableau gewachsen ist."""

    nummer: int                       # 1 bis n
    wert: int
    verdraengungen: tuple             # je berührter Zeile: (zeile, spalte, neuer Wert, verdrängter Wert oder None am Zeilenende), Zeilen ab 0
    neue_zelle: tuple                 # (zeile, spalte) in P und Q, ab 0
    p_danach: tuple                   # P nach dem Schritt (Tupel von Tupeln)


def einfuegen_protokoll(folge, dual=False):
    """Fügt die Folge der Reihe nach ein. Rückgabe: (P, Q, Schritte). P und Q sind Listen von Zeilen."""
    P, Q, schritte = [], [], []
    for nummer, wert in enumerate(folge, 1):
        x = wert
        r = 0
        weg = []
        while True:
            if r == len(P):
                P.append([x])
                Q.append([nummer])
                weg.append((r, 0, x, None))
                neue_zelle = (r, 0)
                break
            j = _verdraengt(P[r], x, dual)
            if j is None:
                P[r].append(x)
                Q[r].append(nummer)
                weg.append((r, len(P[r]) - 1, x, None))
                neue_zelle = (r, len(P[r]) - 1)
                break
            y = P[r][j]
            P[r][j] = x
            weg.append((r, j, x, y))
            x = y
            r += 1
        schritte.append(Schritt(nummer, wert, tuple(weg), neue_zelle, tuple(tuple(z) for z in P)))
    return P, Q, schritte


def einfuegen(folge, dual=False):
    """(P, Q) der Folge; Listen von Zeilen."""
    P, Q, _ = einfuegen_protokoll(folge, dual)
    return P, Q


@dataclass(frozen=True)
class RueckSchritt:
    """Ein Schritt der Umkehrung: Q nennt die Zelle, aus der der letzte Wert stammt."""

    nummer: int                       # n, n - 1, ..., 1 (der Schritt, der rückgängig gemacht wird)
    zelle: tuple                      # (zeile, spalte) der Zelle mit dieser Nummer in Q
    weg: tuple                        # je berührter Zeile von unten nach oben: (zeile, spalte, hinein, heraus)
    wert: int                         # der Wert der Folge an Position `nummer`
    p_danach: tuple


def zurueckrechnen_protokoll(P, Q, dual=False):
    """Rückwärts-Einfügen. Rückgabe: (Folge als Tupel, Liste der RueckSchritte). P und Q werden nicht verändert."""
    P = [list(z) for z in P]
    Q = [list(z) for z in Q]
    n = sum(len(z) for z in P)
    aus = [0] * n
    protokoll = []
    for nummer in range(n, 0, -1):
        r = next(i for i, z in enumerate(Q) if z and z[-1] == nummer)
        c = len(Q[r]) - 1
        Q[r].pop()
        y = P[r].pop()
        if not P[r]:
            P.pop()
            Q.pop()
        weg = [(r, c, y, None)]
        for rr in range(r - 1, -1, -1):
            zeile = P[rr]
            j = max(i for i, v in enumerate(zeile) if ((v <= y) if dual else (v < y)))
            weg.append((rr, j, y, zeile[j]))
            zeile[j], y = y, zeile[j]
        aus[nummer - 1] = y
        protokoll.append(RueckSchritt(nummer, (r, c), tuple(weg), y, tuple(tuple(z) for z in P)))
    return tuple(aus), protokoll


def zurueckrechnen(P, Q, dual=False):
    return zurueckrechnen_protokoll(P, Q, dual)[0]


def form(T):
    """Zeilenlängen des Tableaus (eine Partition von n)."""
    return tuple(len(z) for z in T)


def konjugiert(lam):
    """Transponierte Form (Zeilen und Spalten vertauscht)."""
    if not lam:
        return ()
    return tuple(sum(1 for x in lam if x > j) for j in range(lam[0]))


def form_nach_schritt(Q, i):
    """Form der Einträge von Q, die höchstens i sind: das ist die Form von P nach i Schritten (Konstruktion von Q)."""
    return tuple(c for c in (sum(1 for x in z if x <= i) for z in Q) if c > 0)


def ist_standard(T, n):
    """Zeilen und Spalten wachsen streng und die Einträge sind genau 1 bis n."""
    werte = sorted(x for z in T for x in z)
    if werte != list(range(1, n + 1)):
        return False
    for r, z in enumerate(T):
        for c, x in enumerate(z):
            if c > 0 and z[c - 1] >= x:
                return False
            if r > 0 and (c >= len(T[r - 1]) or T[r - 1][c] >= x):
                return False
    return True


def lis_laenge(a, streng=True):
    """Länge der längsten wachsenden Teilfolge (O(n^2)-Programm); streng=False lässt gleiche Werte nebeneinander zu."""
    best = []
    for i, x in enumerate(a):
        b = 1
        for j in range(i):
            if (a[j] < x) if streng else (a[j] <= x):
                b = max(b, best[j] + 1)
        best.append(b)
    return max(best, default=0)


def lds_laenge(a, streng=True):
    """Länge der längsten fallenden Teilfolge; streng=False lässt gleiche Werte nebeneinander zu."""
    best = []
    for i, x in enumerate(a):
        b = 1
        for j in range(i):
            if (a[j] > x) if streng else (a[j] >= x):
                b = max(b, best[j] + 1)
        best.append(b)
    return max(best, default=0)


def stapel_bilden(folge, fallend=True, schwach=False):
    """Gierige Stapelbildung (erster passender Stapel). Rückgabe: Liste von Stapeln, jeder von unten nach oben.

    fallend=True: ein Container kommt auf einen Stapel, dessen oberster Rang größer ist (oben liegt der kleinste); Mindestzahl Stapel = längste wachsende Teilfolge.
    fallend=False: umgekehrt (wachsende Stapel); Mindestzahl = längste fallende Teilfolge.
    schwach=True: ein gleicher Rang darf auf einen gleichen (Wörter mit Zielgruppen)."""
    stapel = []
    for x in folge:
        for s in stapel:
            oben = s[-1]
            passt = (oben >= x if schwach else oben > x) if fallend else (oben <= x if schwach else oben < x)
            if passt:
                s.append(x)
                break
        else:
            stapel.append([x])
    return stapel


def stapelzahl_verlauf(folge, fallend=True, schwach=False):
    """Zahl der Stapel nach 1, 2, ..., n Ankünften."""
    return [len(stapel_bilden(folge[:i], fallend, schwach)) for i in range(1, len(folge) + 1)]


def ein_stapel_sortiert(p):
    """Ein einziger Stapel sortiert die Folge zur Identität (die Folge vermeidet das Muster 231)."""
    st, naechster = [], 1
    for x in p:
        st.append(x)
        while st and st[-1] == naechster:
            st.pop()
            naechster += 1
    return not st
