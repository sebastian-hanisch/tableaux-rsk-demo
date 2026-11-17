"""Zählt alle n! Folgen für n = 1 bis 9 (Formen, Paare, Überlappung) und schreibt die vorgerechnete Tabelle data/trk_formen.json.

Aufruf (aus dem Repo-Ordner, mit dem Python des Test-venv):
    python tools/trk_make_formen.py            schreibt data/trk_formen.json (rund 3 Sekunden)
    python tools/trk_make_formen.py --check    rechnet neu und vergleicht mit der Datei (Exit-Code 1 bei Abweichung)

Alles sind Ganzzahlen; das Ergebnis hängt weder von der Plattform noch vom Zufall ab. n = 9 hat 362 880 Folgen; die App rechnet nur bis n = 8 selbst."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import trk_enum as E  # noqa: E402

ZIEL = ROOT / "data" / "trk_formen.json"
N_MAX = 9


def rechnen():
    tab = {}
    for n in range(1, N_MAX + 1):
        auf = E.aufzaehlen(n)
        auf["formen"] = {",".join(str(x) for x in lam): v for lam, v in sorted(auf["formen"].items(), reverse=True)}
        tab[str(n)] = auf
    return {
        "beschreibung": "Aufzählung aller n! Folgen (Schensted-Einfügen), n = 1 bis 9: Folgen je Form, verschiedene Paare (P, Q), Umkehrung, "
                        "Überlappung von „ein Stapel sortiert“ mit „erste Zeile höchstens 2“ (lis2) und „höchstens 2 Zeilen“ (lds2).",
        "erzeugt_von": "tools/trk_make_formen.py",
        "n": tab,
    }


def main(argv):
    neu = rechnen()
    if "--check" in argv:
        alt = json.loads(ZIEL.read_text(encoding="utf-8"))
        if alt != neu:
            print("ABWEICHUNG: data/trk_formen.json stimmt nicht mit der Neu-Rechnung überein")
            return 1
        print("OK: data/trk_formen.json stimmt mit der Neu-Rechnung überein")
        return 0
    ZIEL.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("geschrieben:", ZIEL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
