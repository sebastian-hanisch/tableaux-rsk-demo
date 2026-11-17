# Young-Tableaux und Schensted-Einfügen: eine Folge als Paar – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-tableaux-rsk-demo.streamlit.app/)** -->

Demo der Konzepte-Gruppe „Sortiermaschinen und Permutationen“ für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Gruppe fragt, was eine Maschine aus Stapeln, Warteschlangen und Gleisen mit einer Ankunftsreihenfolge von
Containern machen kann. Diese Demo behandelt den **Platz einer Folge, nicht als eine Zahl, sondern als ganze Form**: Das **Einfügen nach Schensted** macht aus jeder Folge ein umkehrbares Paar von **Young-Tableaux** (P und Q) gleicher Form; die erste Zeile
der Form ist die Mindestzahl Stapel, die Zeilenzahl die längste fallende Teilfolge, und die Zahl der Folgen je Form ist ein Quadrat. Sie setzt die Demos zu Stapeln und zur Mindestzahl Stapel voraus und zeigt vor allem die **Falle der Zähleinheit**:
die Hakenformel zählt Tableaux und Zugfolgen, nicht Folgen. Nachbarn der Gruppe: [stapel-sortieren-demo](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (ein Stapel), [patience-stapel-demo](https://github.com/sebastian-hanisch/patience-stapel-demo) (Stapelregeln
und die Mindestzahl Stapel), [erdos-szekeres-demo](https://github.com/sebastian-hanisch/erdos-szekeres-demo) (Kapazität und Schärfe der Schranke), [zwei-stapel-serie-demo](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) (zwei Stapel hintereinander) und
[zufallsfolgen-lis-demo](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo) (die Länge der längsten wachsenden Teilfolge zufälliger Folgen).
**Alle Folgen in der Demo stammen aus einem ausgedachten Modell** (Modell U: alle Anordnungen gleich wahrscheinlich; Modell V: Verweilzeit D): es ist ein Modell und kein Fall, es gibt keine reale Ankunftsfolge eines Hafens oder Bahnhofs, und die Zahlen gelten für dieses Modell,
nicht für einen Hafen. **„Tableau“ heißt hier immer Young-Tableau**; das Simplex-Tableau der Linearen Programmierung ([tableau-simplex-demo](https://github.com/sebastian-hanisch/tableau-simplex-demo)) ist ein anderes Objekt.

## Warum dieses Problem

Die Mindestzahl Stapel einer Ankunftsfolge ist eine Zahl (die längste wachsende Teilfolge). Das ist die halbe Auskunft: Die Folge hat eine **ganze Form** (alle Zeilenlängen), und das Einfügen ordnet ihr außerdem ein Paar von Tableaux zu, aus dem sie sich zurückrechnen lässt.
Aus der Form folgen alle Zahlen bisher (erste Zeile = Mindestzahl fallender Stapel, Zeilenzahl = längste fallende Teilfolge) und die Zählung aller Folgen (Summe der f² = n!). Die Falle liegt in der Zähleinheit: Zwei Stapel in Serie haben bei n = 7 genau 1 385 670 Zugfolgen
(Hakenformel des Rechtecks 3 × 7) für nur 5 018 verschiedene Folgen, und die Zahl Catalan(n) zählt zwei verschiedene Mengen. Kernfragen: (1) Wie wird aus einer Folge ein Paar von Tableaux, und was lese ich ab? (2) Wie viele Folgen gehören zu welcher Form?
(3) Wo verwechselt man Tableaux, Zugfolgen und Folgen? **Neu im wissenschaftlichen Sinn ist nichts davon**: Einfügen, Form, Hakenformel und Zuordnung sind Lehrbuchstoff; neu ist nur die Vorführbarkeit mit Zähleinheiten an einem durchgehenden Beispiel.

## Modell

**Ankunftsfolge** p = (p₁, …, p_n): Permutation der Abholränge 1 … n in Ankunftsreihenfolge (Rang 1 fährt zuerst). **Konventionen:** Container-Stapel **fallend** (ein Container kommt nur auf einen Stapel mit größerem Rang; oben liegt der kleinste); Mindestzahl Stapel = **längste wachsende
Teilfolge** (LIS); bei wachsenden Stapeln die längste fallende (LDS). Ein einziger Stapel sortiert genau die Folgen, die das Muster 231 vermeiden; die Ausgaben eines Stapels, in den man 1 … n der Reihe nach gibt, vermeiden 312 (Sortieren und Erzeugen sind invers).

**Schensted-Einfügen (Zeileneinfügen).** Ein Tableau hat Zeilen, die nach rechts wachsen, und Spalten, die nach unten wachsen. Einfügen von x in die erste Zeile: Steht rechts von allen Einträgen kein größerer, kommt x ans Ende; sonst ersetzt x den **ersten Eintrag, der größer ist**, und der Verdrängte
wird in die nächste Zeile eingefügt, und so weiter, bis ein Eintrag ans Zeilenende passt oder eine neue Zeile beginnt. Das **Aufzeichnungstableau Q** bekommt im Schritt i an der Stelle, an der P gewachsen ist, die Zahl i. Aus (P, Q) rechnet man rückwärts die Folge zurück (Q sagt, aus welcher Zelle der letzte
Schritt kam). **Form** λ = Zeilenlängen von P (und Q), eine Partition von n; f^λ = Zahl der Standardtableaux der Form λ = n!/Produkt der Hakenlängen (Hakenformel).

**Ablesen.** Erste Zeile von λ = LIS = Mindestzahl **fallender** Stapel; Zeilenzahl = LDS. Bei **wachsenden** Stapeln ist es die erste Spalte (Schalter in Experiment 1). „Zeile“ und „Spalte“ sind eine Namenskonvention: Die App folgt der heute üblichen Zeilenfassung (erste Zeile = LIS, mit dem eigenen Code
und mit dem Probieren aller Teilmengen geprüft, B2). In Schensteds Aufsatz (1961) stehen Satz 1 und 2 nach den gelesenen Seiten 179 bis 185 mit den Namen „Spalten = LIS, Zeilen = LDS“; ob das an einer anderen Anordnung des Tableaus oder nur an der Benennung liegt, ist nicht nachgelesen.

**Wörter mit gleichen Werten** (Wagen mit Zielgruppen, Experiment 5): Stapel, die einen gleichen Rang aufnehmen dürfen (schwach fallend); die Mindestzahl Stapel ist dann die längste **streng** wachsende Teilfolge. Dazu passt die **duale Einfügung** („ersetzt den ersten Eintrag, der größer **oder gleich** ist“): P hat dann
streng wachsende Zeilen und schwach wachsende Spalten. Die Lehrbuchfassung („größer“) liefert als erste Zeile die längste **schwach** wachsende Teilfolge. Beide Fassungen geben bei Zielgruppen (2, 2, 2) in 74 von 90 Wörtern verschiedene Zahlen (B10).

**Modell U und V.** Modell U: alle n! Folgen gleich wahrscheinlich (Formverteilung exakt aus der Hakenformel). Modell V: Container i kommt zur Zeit i an und bleibt eine exponentialverteilte Zeit mit dem Mittel D (in Ankunftsabständen); der Rang ist die Reihenfolge der Abfahrtszeiten (nur diese Rangfolge geht ein).
D klein: fast sortiert; D → ∞: Modell U. Beides ist **ausgedacht**, nicht an Daten angepasst.

**Zähleinheiten** (jede Zahl nennt ihre): **Folgen** (Anordnungen der Ränge 1 … n), **Tableaux** (Standardtableaux einer Form), **Zugfolgen** (vollständige Zugreihen einer Maschine aus t Stapeln in Serie: einlegen, umsetzen, ausgeben), **Wörter** (Folgen mit gleichen Buchstaben), **Zellen** und **Schritte** des Einfügens.
Die Hakenformel zählt Tableaux und damit Zugfolgen, nicht Folgen. Die Formeln stehen im 📐-Expander der App, beginnend mit einer Lesehilfe.

## Methodik

Die App zeigt oben drei Kernfragen mit je einer kurzen Antwort, die aus der Rechnung kommt, dann fünf Experimente mit je einem Verdikt (eine reine Funktion in `trk_evaluation.py`):

1. **Einfügen Schritt für Schritt.** Eingabe: eine Folge (bis 12 Zahlen; Werte außerhalb 1 bis n werden auf Ränge umgerechnet, gleiche Werte abgewiesen), Schritt i, Stapelrichtung (fallend: erste Zeile, wachsend: erste Spalte), ein Knopf für eine Zufallsfolge (Modell U, Länge 3 bis 12, Zufalls-Seed der Seitenleiste), Schalter „Zurückrechnen“.
   Anzeige: P und Q nach Schritt i (verdrängte Einträge orange, neue Zelle grün), die Stapel nach i Ankünften, die Kurve „Stapelzahl nach i Ankünften“ (aus der Stapelbildung und aus Q abgelesen), die Einfügeschritte und, auf Wunsch, die Umkehrung.
2. **Wie viele Folgen gehören zu welcher Form?** Länge n von 2 bis 30 (Hakenformel, Ganzzahlen), Hervorhebung „höchstens 2 Zeilen“ oder „höchstens 2 Spalten“. Anzeige: Balken Anteil je Form (f²/n!), Tabelle Form, f, f², Anteil, Hakenlängen der häufigsten Form, Summe der f² und der f. Bis n = 8 werden alle Folgen live aufgezählt (Formen, Paare, Umkehrung, Überlappung
   mit „ein Stapel sortiert“); n = 9 ist vorgerechnet (`data/trk_formen.json`, `tools/trk_make_formen.py`). Ein aufklappbarer Block zeigt die Überlappung für n = 1 bis 9.
3. **Die Form im ausgedachten Modell V.** D (0,5 bis ∞), n (6 bis 12), Zahl der Folgen (500 bis 3 000): live gezogene Folgen (SplitMix64, Strom je D aus Zufalls-Seed plus Index von D), mittlere erste Zeile und Zeilenzahl mit Standardfehler, häufigste Form, Verteilung der Formen. Dazu die **vorgerechnete** Tabelle für n = 10 mit je 20 000 Folgen und
   zwei Zufalls-Seeds (`data/trk_modellv.json`, `tools/trk_make_modellv.py`), mit dem exakten Wert des Modells U als gestrichelter Gerade.
4. **Zugfolgen gegen Folgen (die Falle).** Zahl der Stapel in Serie t (1 bis 3), Container n (1 bis 8). Eine Stapelsimulation zählt alle vollständigen Zugfolgen (live bis n = 8 für t = 1, n = 6 für t = 2, n = 4 für t = 3; t = 2 mit n = 7 und t = 3 mit n = 5 sind vorgerechnet in `data/trk_zuege.json`, `tools/trk_make_zuege.py`, darüber nur die Hakenformel).
   Tabelle Zugfolgen, Hakenformel des Rechtecks (t + 1) × n, verschiedene Folgen, n!, Zugfolgen je Folge; bei höchstens 42 Zugfolgen als Buchstabenwörter mit ihrer Ausgabe.
5. **Gleichstände: Wörter mit Zielgruppen.** Sieben Inhalte (zum Beispiel (2,2,2): drei Zielgruppen zu je zwei Wagen), ein Wort eingeben oder würfeln, Fassung streng oder schwach. Anzeige: P und Q, die Stapel in beiden Lesarten mit Gegenprobe durch Probieren aller Zerlegungen, Wörter je Form als f · Kostka-Zahl gegen die Aufzählung.

Presets („Schnellstart“) stehen oben in der Seitenleiste; die Regler der Experimente stehen bei den Experimenten. Die Adresszeile spiegelt die Einstellungen (Permalink, auf die Reglergrenzen begrenzt).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen gelten **für dieses ausgedachte Modell** (Folgen ohne gleiche Werte; Wörter nur in B10), bei den genannten Einstellungen. Ganzzahlen und Brüche sind exakt gerechnet; Zufallsproben (B9) stehen als Band; B2 zweiter Teil ist eine Zählung über feste Zufallsfolgen (Zufalls-Seed 101). Die Messdateien sind `data/trk_formen.json`, `data/trk_zuege.json` und `data/trk_modellv.json`
(mit ihren Werkzeugen und `--check`); die Zahlen prüft `tests/test_claims.py`. Zeiten stehen nur in dieser README und in keinem Test.

| Nr | Frage | Befund (Voraussetzung im Satz) | Test |
|---|---|---|---|
| B1 | Bijektion und Umkehrung | Für alle Folgen der Länge n = 1 bis 8 (Zähleinheit Folgen, aufgezählt) sind die n! Paare (P, Q) paarweise verschieden und das Rückwärts-Einfügen liefert jede Folge zurück; Folgen je Form = f² in allen Formen (n = 8: 22 Formen). Bei n = 9 (362 880 Folgen) nur die Zählung der Folgen je Form: f² in allen 30 Formen | `test_b1_*` (exakt); Orakel: `test_einfuegen_ist_bijektion_*` (n ≤ 6, gegen die unabhängige Aufzählung aller Standardtableaux) |
| B2 | Ablesen | Erste Zeile = LIS und Zeilenzahl = LDS in allen Folgen n ≤ 7 (O(n²)-Programm; in den Orakel-Tests auch n = 8 und, durch Probieren aller Teilmengen, n ≤ 6) und in 2 000 Zufallsfolgen der Längen 12 bis 30 (Zufalls-Seed 101): 0 Abweichungen, die Umkehrung gibt jede dieser Folgen zurück | `test_b2_*` |
| B3 | Σ f² = n! und Σ f | Σ f² = n! und Σ f = Zahl der Involutionen (1, 2, 4, 10, 26, 76, 232, 764, 2 620, 9 496, 35 696, 140 152, 568 504, 2 390 480 für n = 1 bis 14) in der Hakenformel bis n = 14; Zahl der Formen = Partitionszahlen 1, 2, 3, 5, 7, 11, 15, 22, 30, 42 (n = 1 bis 10), 5 604 bei n = 30 | `test_b3_summen_bis_n14` (exakt) |
| B4 | Handfolge n = 6 | (1, 3, 6, 2, 5, 4): P = [[1,2,4],[3,5],[6]], Q = [[1,2,3],[4,5],[6]], Form (3,2,1), f = 720/45 = 16, also 256 von 720 Folgen mit dieser Form; Stapel [1] [3, 2] [6, 5, 4]; Stapelzahl nach 1 bis 6 Ankünften 1, 2, 3, 3, 3, 3; ein Stapel sortiert sie nicht. Folgen je Form bei n = 6: 1, 25, 81, 100, 25, 256, 100, 25, 81, 25, 1 | `test_b4_handfolge`, `tests/test_handbeispiel.py` |
| B5 | Q liest den Verlauf | Für alle Folgen n ≤ 8 und alle i: Form von P nach i Schritten = Form von Q mit Einträgen ≤ i, erste Zeile = Stapelzahl nach i Ankünften (Stapelbildung), Zeilenzahl = längste fallende Teilfolge des Präfixes: 0 Abweichungen. **Die erste Gleichung folgt aus der Konstruktion von Q**, die zweite aus „erste Zeile = LIS“ auf dem Präfix; die Messung prüft die Umsetzung, sie belegt keinen neuen Satz | `test_b5_*` |
| B6 | Formverteilung (Modell U, exakt) | Häufigste Form, f, Folgen, Anteil, fünf häufigste zusammen: n = 4: (3,1) und (2,1,1), 3, je 9 von 24 (37,5 %), alle fünf Formen; n = 6: (3,2,1), 16, 256 von 720 (35,6 %), 85,8 %; n = 8: (4,2,1,1), 90, 8 100 von 40 320 (20,1 %), 64,7 %; n = 10: (4,3,2,1), 768, 589 824 von 3 628 800 (16,3 %; exakt 256/1575), 49,2 %; n = 12: (5,3,2,1,1), 7 700, 59 290 000 von 479 001 600 (12,4 %), 39,5 %. Gleich häufig mit der transponierten Form (zwei häufigste Formen) bei n = 2, 4, 7, 9, 11; eine eindeutig häufigste Form bei n = 3, 5, 6, 8, 10, 12 (in diesen Fällen jeweils selbstkonjugiert: (2,1), (3,1,1), (3,2,1), (4,2,1,1), (4,3,2,1), (5,3,2,1,1)). E[erste Zeile] = E[Zeilenzahl] bei n = 10: 4,3350 (exakt); Summe der LIS-Längen n = 4, 5, 6: 58, 335, 2 261. Eine Grenzform für große n ist **nicht gemessen** | `test_b6_*` (exakt) |
| B7 | Catalan zweimal, andere Menge | Folgen mit höchstens 2 Zeilen = Folgen mit höchstens 2 Spalten = Catalan(n) für n = 1 bis 14 (Hakenformel); bis n = 9 aufgezählt auch gleich der Zahl der Folgen, die ein Stapel sortiert. **Gemeinsam** mit „höchstens 2 Spalten“ sind nur 1, 2, 4, 7, 11, 16, 22, 29, 37 (n = 1 bis 9; n = 6: 16 von 132 = 12,1 %, je 116 nur in einer Menge, 248 in der Vereinigung); mit „höchstens 2 Zeilen“ 1, 2, 4, 8, 16, 32, 64, 128, 256; mit beiden Grenzen (ohne die Stapelbedingung) 1, 2, 4, 4, 0, 0, 0, 0, 0. **C(n,2) + 1 und 2^(n−1) sind Zahlenmuster aus n ≤ 9, kein Beweis** | `test_b7_*` (exakt) |
| B8 | Zugfolgen gegen Folgen | Zugfolgen von t Stapeln in Serie (Stapelsimulation) = Hakenformel des Rechtecks (t + 1) × n in allen gerechneten Fällen. Zugfolgen / verschiedene Folgen: t = 1, n = 4: 14 / 14; n = 8: 1 430 / 1 430 (je Folge eine Zugfolge); t = 2: n = 2: 5 / 2, n = 3: 42 / 6, n = 4: 462 / 24, n = 5: 6 006 / 120, n = 6: 87 516 / 720, **n = 7: 1 385 670 / 5 018** (276,14 je Folge); t = 3: n = 4: 24 024 / 24, n = 5: 1 662 804 / 120 (13 856,7 je Folge). Bei zwei Stapeln sind die Ausgaben bis n = 6 alle n! Folgen, bei n = 7 nur 5 018 von 5 040. Hakenzahl ohne Simulation: t = 3, n = 6: 140 229 804; n = 7: 13 672 405 890 | `test_b8_*` (exakt); n = 7 und t = 3, n = 5 aus `data/trk_zuege.json`, Neu-Rechnung `tests/test_daten.py` (langsam) |
| B9 | Modell V (ausgedacht), n = 10 | Je 20 000 Folgen je D (Zufalls-Seed 101; in Klammern Zufalls-Seed 20261117), Zähleinheit Folgen. Mittlere erste Zeile (= Mindestzahl fallender Stapel bei Verzögerung): D = 0,5: 9,388 (9,397); D = 1: 8,332 (8,329); D = 2: 7,105 (7,098); D = 4: 6,052 (6,060); D = 8: 5,314 (5,302); D = 16: 4,857 (4,849); D = ∞: 4,330 (4,336), exakt im Modell U 4,3350. Mittlere Zeilenzahl von 1,496 (1,487) bei D = 0,5 bis 4,337 (4,336) bei D = ∞. Häufigste Form und Zahl der Folgen mit ihr (Anteil): D = 0,5: (10) mit 10 171 (50,85 %; 51,73 %); D = 1: (9,1) 33,98 % (33,65 %); D = 2: (8,2) 21,58 % (21,39 %); D = 4: (6,3,1) 21,62 % (21,07 %); D = 8: (6,3,1) 14,79 % (14,16 %); D = 16: (4,3,2,1) 13,09 % (12,73 %); D = ∞: (4,3,2,1) 15,80 % (16,11 %), exakt 16,25 %. Gesehene Formen von 42 (Zufalls-Seed 101): 8, 17, 26, 33, 36, 37, 39. Die beiden Zufalls-Seeds unterscheiden sich bei der mittleren ersten Zeile um höchstens 0,012 und beim Anteil der häufigsten Form um höchstens 0,9 Prozentpunkte. Die mittlere erste Zeile sinkt mit D, die mittlere Zeilenzahl steigt (beide Zufalls-Seeds). Wo zwei Formen dicht beieinander liegen (bei D = 1 (9,1) und (8,2), bei D = 16 (4,3,2,1) und (5,3,1,1)), kann „häufigste Form“ mit dem Zufalls-Seed wechseln; die Zahl der gesehenen Formen schwankt ebenfalls | `test_b9_*` (Band); Tabelle `data/trk_modellv.json`, Neu-Rechnung `tests/test_daten.py` (langsam) |
| B10 | Wörter mit Zielgruppen | Inhalte (2,2,2), (3,2,1), (2,2,1,1), (2,1,1,1), (3,3), (2,2,2,1), (1,1,1,1,1): 90, 60, 180, 60, 20, 630, 120 Wörter. Mit der dualen Einfügung ist die erste Zeile die längste streng wachsende Teilfolge und gleich der Mindestzahl Stapel (schwach fallende Stapel; Gegenprobe über alle Zerlegungen der Positionen) in allen Wörtern; die Lehrbuchfassung gibt die längste schwach wachsende Teilfolge = Mindestzahl streng fallender Stapel. Wörter je Form = f · Kostka-Zahl, nicht f² (Inhalt (2,2,2): Form (3,2,1): 32 = 16 · 2; (3,3): 5; (2,2,1,1): 27; (3,1,1,1): 10; (2,2,2): 5; (2,1,1,1,1): 10; (1⁶): 1; Summe 90). Streng und schwach geben verschiedene Zahlen bei 74 von 90 Wörtern (2,2,2), 55 von 60 (3,2,1), 111 von 180 (2,2,1,1), 463 von 630 (2,2,2,1). Kleinstes Beispiel (1,1,2,2): streng 2, schwach 4 | `test_b10_*` (exakt) |
| B11 | Involutionen | P = Q genau dann, wenn die Folge ihre eigene Inverse ist (n ≤ 8: 1, 2, 4, 10, 26, 76, 232, 764 Involutionen), und bei jeder Involution ist die Zahl der Fixpunkte gleich der Zahl der Spalten ungerader Länge der Form (nur n ≤ 8 gemessen) | `test_b11_*` (exakt) |
| B12 | Eigenschaften | Je 30 bis 50 Zufallsfolgen (Zufalls-Seed 20261117, Längen 2 bis 12), 0 Verletzungen: monotone Umbenennung der Werte ändert Q und die Form nicht; Spiegeln und Komplement transponieren die Form, beides zusammen lässt sie gleich; die Inverse vertauscht P und Q; ein neues größtes Element am Ende verlängert die erste Zeile um 1, ein neues kleinstes die erste Spalte um 1; Summe der Zeilenlängen = n | `tests/test_eigenschaften_tableaux_rsk.py` |

### Rechenregeln und Hinweise zu den Zahlen

- **Exakt** heißt: Ganzzahlen und Brüche (`fractions`), kein Gleitkomma. Zufallsproben (B9) sind Bänder: Mittel ± 0,08 für die ersten 2 000 Folgen gegen die Tabelle, ± 0,02 für die Neu-Rechnung aller 20 000; Anteile ± 0,01 bzw. 0,04. Die Folgen kommen aus SplitMix64 (`trk_rng.py`, Kopie der geprüften Vorlage), plattformfest.
- **Zähleinheit:** B1 bis B7 Folgen (n! Möglichkeiten), B8 Zugfolgen und Folgen, B9 Folgen (je 20 000 gezogen), B10 Wörter, B11 Folgen. „Alle“ in B1 bis B5 und B11 heißt: alle Folgen bis zur genannten Länge, aufgezählt.
- **Absolutaussagen und ihre Bedingungen:** „erste Zeile = LIS“ ist für alle Folgen bis n = 7 mit dem O(n²)-Programm, bis n = 6 durch Probieren aller Teilmengen und in 2 000 Zufallsfolgen mit n = 12 bis 30 geprüft, nicht für jedes n (Lehrsatz nach Schensted, Seiten 179 bis 185 gelesen). „Σ f² = n!“ ist bis n = 14 gerechnet und bis n = 9 gegen die Aufzählung
  geprüft, darüber Lehrsatz. „Die Hakenformel zählt Zugfolgen“ ist für t ≤ 3 und die gerechneten n nachgemessen (Bóna 2003, § 3, Gl. (1); gelesen). Die Hakenformel ist nur für t = 1 die Zahl der Folgen; für t ≥ 2 ist sie eine (schlechte) obere Schranke, der Faktor wächst bei zwei Stapeln von 2,50 (n = 2) auf 276,14 (n = 7).
  „Wörter je Form = f · Kostka“ ist für die sieben Inhalte mit n ≤ 7 und beide Fassungen geprüft.

## Befunde und Korrekturen gegenüber der ersten Rechnung

- **Fünf häufigste Formen bei n = 12:** 39,5 % (189 430 098 von 479 001 600 Folgen, bezogen auf 12!), nicht 39,6 % wie in der ersten Rechnung (dort aus 0,3955 gerundet); alle anderen Zahlen der Formverteilung blieben gleich.
- **Modell V mit SplitMix64:** Die erste Rechnung benutzte einen anderen Zufallsgenerator (numpy). Mit SplitMix64 und Zufalls-Seed 101 liegt der Anteil der Form (10) bei D = 0,5 bei 50,85 % (numpy: 50,7 %; Zufalls-Seed 20261117: 51,73 %); die häufigste Form bei D = ∞ hat 15,8 % (Zufalls-Seed 101) bzw. 16,1 % (Zufalls-Seed 20261117) gegen exakt 16,25 %. Die Mittelwerte weichen um höchstens 0,02 von der ersten Rechnung ab;
  die Zahl der gesehenen Formen bei D = 4 ist 33 statt 32. Zufallsproben ändern solche Zahlen von Zufalls-Seed zu Zufalls-Seed; die README nennt deshalb beide Zufalls-Seeds.
- **Zufallsfolgen n = 12 bis 30:** in der ersten Rechnung nicht gemessen; hier 2 000 Zufallsfolgen (Zufalls-Seed 101) ohne Abweichung (B2).
- **Lehrbuchfassung bei Wörtern:** die erste Rechnung prüfte „Wörter je Form = f · Kostka“ nur für die duale Einfügung (mit der transponierten Form); hier ist es für beide Fassungen geprüft (bei der Lehrbuchfassung mit der Kostka-Zahl der Form selbst).
- **Q liest den Verlauf** ist als Konstruktion gekennzeichnet (B5), nicht als Befund: wer die Gleichung als Messergebnis ausgibt, behauptet zu viel.
- **Aufzählung bis n = 8 live:** die App zählt alle 40 320 Folgen samt Umkehrung und Überlappung selbst; gemessen etwa 1,3 s für n = 8 und 0,13 s für n = 7 (Windows, ein Lauf, Rechner durch andere Läufe belegt); das Ergebnis wird danach zwischengespeichert, ein Spinner nennt die Wartezeit. Auf Streamlit Cloud ist die Zeit nicht gemessen.

## Quellen

- Schensted, C. (1961): „Longest increasing and decreasing subsequences“, *Canadian Journal of Mathematics* 13, 179 bis 191: Einfügen, Lemma 1 bis 3 (Folgen ↔ Paare von Standardtableaux gleicher Form), Satz 1 und 2. Gelesen: Seiten 179 bis 185 (Scan mit Texterkennung). Die Hakenformel steht dort als Zitat von Frame, Robinson und Thrall (1954; das Original ist nicht gelesen).
- Bóna, M. (2003): „A survey of stack-sorting disciplines“, *Electronic Journal of Combinatorics* 9(2), #A1, § 3, Gl. (1): Stapelwörter bei t Stapeln in Serie stehen in Bijektion mit Standardtableaux des Rechtecks (t + 1) × n; ihre Zahl (Hakenformel) ist eine obere Schranke für die Zahl der sortierbaren Folgen. Gelesen (Wortlaut). Dort auch: ein Stapel sortiert die Folgen, die 231 vermeiden.
- Catalan(n) für die Folgen mit höchstens 2 Zeilen als Tableaux-Beweis für das Muster 321: nach Knuth, nur über Doyle gelesen (nicht im Original).
- **Nicht gelesen** und nur als Lehrbuchstoff genannt: Knuth, *The Art of Computer Programming* Bd. 3, § 5.1.4; Fulton; Sagan; Stanley, *Enumerative Combinatorics* Bd. 2, Kap. 7; Schützenberger (Satz zu den Fixpunkten, hier nur gemessen, B11). Alles Inhaltliche ist Lehrbuchstoff; **eine Neuheitsaussage gibt es nicht**.

## Ehrliche Grenzen

- **Ein ausgedachtes Modell.** Modell U und V sind keine Messung; Modell V ist nur für n = 10 und sieben Werte von D vorgerechnet. Wie die häufigste Form von n abhängt und wie sich eine reale Ankunftsfolge verhält, ist nicht gemessen.
- **Formverteilung nur bis n = 30 (Hakenformel) und bis n = 12 in den Befunden.** Eine Grenzform für große n kommt nicht vor.
- **Aufzählung bis n = 9** (n = 9 nur als Formenzählung und Überlappung); „Q liest den Verlauf“ ist bis n = 8 aufgezählt. Kein Beweis. Die Fixpunkt-Aussage (B11) gilt nur n ≤ 8 gemessen.
- **C(n,2) + 1 und 2^(n−1)** sind Zahlenmuster aus n ≤ 9.
- **Zugfolgen:** Simulation nur für t = 1 (n ≤ 8), t = 2 (n ≤ 7), t = 3 (n ≤ 5); darüber nur die Hakenformel. Die Bijektion Zugfolge ↔ Standardtableau ist hier gezählt (Zahl gleich der Hakenformel), nicht als Abbildung nachgebaut.
- **Gleichstände:** sieben Inhalte mit n ≤ 7; Wagen mit realen Gruppengrößen, große Gruppen und n > 7 sind nicht gemessen. „Schwach fallende Stapel“ ist eine Konvention dieser Demo.
- **Zeiten:** eine CPU, ein Lauf, Windows, Python 3.14.6, Rechner durch andere Läufe belegt, Streuung nicht bestimmt (Größenordnung): Aufzählung aller Folgen bei n = 8 etwa 1,3 s; Hakenformel für n = 30 etwa 0,07 s; 1 000 Folgen im Modell V bei n = 10 etwa 0,4 s (3 000 Folgen bei n = 12 etwa 1,4 s); Zugfolgen t = 2 mit n = 6 etwa 0,13 s. Die vorgerechneten Läufe brauchen je 2 bis 3 s (t = 2, n = 7 und t = 3, n = 5), die Modell-V-Tabelle rund 2 Minuten (14 Läufe zu 20 000 Folgen, der exakte Logarithmus ist langsam) und die Aufzählung bis n = 9 einige Sekunden. Auf Streamlit Cloud nicht gemessen.
- **Nicht mit echtem Mausklick im Browser getestet:** die Bedienung ist mit AppTest geprüft (jeder Knopf, jeder Regler am Minimum und Maximum, jede Auswahl); die Plotly-Bilder der Tableaux sieht AppTest nur als Elemente.
- **Linux:** alle 237 Tests bestehen im Linux-Container (Docker, Python 3.12, frische Installation, Speichergrenze 16 GB; 80 s Testzeit). Die Zufallsproben sind Bänder, die Zählungen exakt; es gab keinen roten Lauf.

## Abgrenzung zu Nachbarn

- **Stapelregeln und Verteilung der Stapelzahl** ([patience-stapel-demo](https://github.com/sebastian-hanisch/patience-stapel-demo), [mehrhafenstau-demo](https://github.com/sebastian-hanisch/mehrhafenstau-demo)): dort stehen die Stapelregeln (die gierige Regel, die Mindestzahl Stapel als Patience). Hier erscheinen Stapel nur als **Lesart der ersten Zeile**.
- **Kapazität, Greene und Erdős-Szekeres** ([erdos-szekeres-demo](https://github.com/sebastian-hanisch/erdos-szekeres-demo), [ketten-antiketten-demo](https://github.com/sebastian-hanisch/ketten-antiketten-demo)): Summen der ersten Zeilen und Spalten als Kapazität und „Höhe mal Breite ≥ n“ gehören dorthin; hier nur ein Verweis.
- **Zwei Stapel in Serie** ([zwei-stapel-serie-demo](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo)): dort stehen die Zahl 5 018 und das Scheitern bei n = 7; hier erscheint sie nur als Gegenüber zu den Zugfolgen (Experiment 4).
- **Involutionen und Partitionszahlen** ([beschriftete-strukturen-demo](https://github.com/sebastian-hanisch/beschriftete-strukturen-demo), [multimengen-partitionen-demo](https://github.com/sebastian-hanisch/multimengen-partitionen-demo)): dort kommen die Involutionen aus der Exponentialformel und die 42 Zahlpartitionen von 10; hier ist die Summe der f dieselbe Zahl auf einem anderen Rechenweg (Standardtableaux), nur als Querprobe.
- **Verteilung nach Parametern** ([zaehlen-nach-parameter-demo](https://github.com/sebastian-hanisch/zaehlen-nach-parameter-demo)): dort Abstiege, Inversionen, Zyklen; Catalan(n) und Muster-Klassen kommen hier nur als eine Zeile vor. Neu hier ist der Parameter „Form“ (erste Zeile und Zeilenzahl).
- **Simplex-Tableau** ([tableau-simplex-demo](https://github.com/sebastian-hanisch/tableau-simplex-demo)): ein anderes Objekt (Lineare Programmierung); Namensfalle, deshalb steht in Titel und Text „Young-Tableau“.
- **Längenverteilung zufälliger Folgen** ([zufallsfolgen-lis-demo](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo)): der Erwartungswert der ersten Zeile für große n gehört dorthin; hier nur die Formverteilung für n ≤ 30 (Hakenformel) und der Mittelwert bei n = 10.

## Verifikation

- **Kern:** Handbeispiele (Handfolge Schritt für Schritt, Umkehrung von Hand, n = 4 mit allen 24 Folgen, zwei Stapel mit n = 2 und 3, Wort (2, 1, 2, 3, 1)) in `tests/test_handbeispiel.py`; SplitMix64 gegen die Referenzfolge.
- **Orakel** (`tests/test_oracle_tableaux_rsk.py`, anderer Rechenweg): Einfügen und Umkehrung gegen die unabhängige Aufzählung aller Standardtableaux (jedes Paar gleichförmiger Standardtableaux kommt genau einmal vor, n ≤ 6); erste Zeile und Zeilenzahl gegen das Probieren aller Teilmengen (n ≤ 6) und ein O(n²)-Programm (n ≤ 8);
  Hakenformel gegen die Eckenrekursion (alle Formen bis n = 14) und gegen die Aufzählung (Folgen je Form, n ≤ 8, n = 9 im langsamen Test); Zugfolgen: Stapelsimulation gegen Ballot-Wörter gegen Hakenformel des Rechtecks; Ausgaben eines Stapels gegen die 312-vermeidenden Folgen; Kostka-Zahlen gegen das Füllen Zelle für Zelle; Mindestzahl Stapel gegen eine Suche über alle Stapelspitzen-Zustände;
  Überlappung gegen Mustersuche. Die Referenzen stehen in der Testdatei.
- **Eigenschaften** (`tests/test_eigenschaften_tableaux_rsk.py`): siehe B12.
- **Randfälle** (`tests/test_edge_cases.py`): leere Folge, n = 1, n = 2, aufsteigend und absteigend, Werte außerhalb 1 bis n, Gleichstände im Permutationsmodus, Wort mit einer Zielgruppe, Zugfolgen ohne Container, Grenzen der Live-Rechnung, Hakenformel bei n = 30.
- **Verdikte** als reine Funktionen an von Hand gesetzten Werten (`tests/test_verdicts.py`), je Schnellstart-Szenario die erwartete Verdikt-Zeile (`tests/test_presets.py`).
- **Claims:** jede Zahl der Befunde B1 bis B11 (`tests/test_claims.py`), die vorgerechneten Dateien gegen eine Neu-Rechnung (`tests/test_daten.py`, langsam).
- **Oberfläche:** AppTest-Rauchtest (jeder Knopf, jeder Regler am Minimum und Maximum, jede Auswahl, ungültige Eingaben, Permalink), Footer-Test, Layout (Schnellstart in der Seitenleiste, fester Kopf, aktives Szenario hervorgehoben, jede Änderung eines Reglers hebt die Markierung auf), Laufzeit-Importe.
- **Testzahl:** 237 Tests (`pytest --collect-only -q tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Kernfragen, fünf Experimente, Annahmen, Formeln |
| `data/trk_formen.json` | vorgerechnete Aufzählung aller Folgen bis n = 9 (Formen, Paare, Überlappung) |
| `data/trk_modellv.json` | vorgerechnete Tabelle zu Modell V (n = 10, je 20 000 Folgen, zwei Zufalls-Seeds) |
| `data/trk_zuege.json` | vorgerechnete Zugfolgen (t = 2 mit n = 7, t = 3 mit n = 5) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tools/trk_make_formen.py` | erzeugt und prüft (`--check`) `data/trk_formen.json` |
| `tools/trk_make_modellv.py` | erzeugt und prüft (`--check`, Band) `data/trk_modellv.json` |
| `tools/trk_make_zuege.py` | erzeugt und prüft (`--check`) `data/trk_zuege.json` |
| `trk_constants.py` | Regler-Grenzen, Voreinstellungen, Farben, Schnellstart-Szenarien |
| `trk_enum.py` | Aufzählung aller n! Folgen (Formen, Paare, Überlappung), Zugriff auf die vorgerechnete Tabelle |
| `trk_evaluation.py` | Kennzahlen und Verdikte der Experimente (reine Funktionen) |
| `trk_haken.py` | Partitionen, Hakenformel, Formverteilung, Catalan, Involutionen (Ganzzahlen und Brüche) |
| `trk_layout.py` | Fester Kopf (Stylesheet) |
| `trk_presets.py` | Permalink (Begrenzen), Schnellstart in der Seitenleiste, aktives Szenario hervorgehoben, Zufalls-Seed-Knopf |
| `trk_rng.py` | SplitMix64 (Kopie der geprüften Vorlage, plattformfest) |
| `trk_rsk.py` | Schensted-Einfügen (beide Fassungen), Umkehrung, LIS und LDS, Stapelbildung |
| `trk_scenario.py` | Modell U und V, Einlesen der Eingaben, Wörter |
| `trk_texts.py` | Schreibweise der Zahlen (Dezimalkomma, Tausendertrenner) und Modellhinweis |
| `trk_visualization.py` | Plotly-Abbildungen (Tableaux, Verläufe, Balken; Achsen gesperrt) |
| `trk_woerter.py` | Wörter mit gleichen Buchstaben: Aufzählung, Kostka-Zahlen, Mindestzahl Stapel durch Probieren |
| `trk_zuege.py` | Zugfolgen von t Stapeln in Serie (Stapelsimulation) |
| `tests/` | Handbeispiele, Orakel, Eigenschaften, Randfälle, Verdikte, Presets, Claims, Daten, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Jeu de taquin, Knuth-Äquivalenz, Evakuierung und die duale RSK-Zuordnung für Folgen**: kommen nicht vor (Lehrbuchstoff, nicht Gegenstand dieser Demo).
- **Greene** (Summen der ersten Zeilen und Spalten als Kapazität in mehreren Stapeln) und Erdős-Szekeres: Verweis auf [erdos-szekeres-demo](https://github.com/sebastian-hanisch/erdos-szekeres-demo).
- **Grenzform großer Folgen** und die Verteilung der ersten Zeile für große n: nicht gemessen, kommt vor allem in [zufallsfolgen-lis-demo](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo) vor.
- **Ein realer Datensatz**: es gibt keine gelesene Quelle für eine echte Ankunftsfolge; ein Datenbezug wird nicht behauptet.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
