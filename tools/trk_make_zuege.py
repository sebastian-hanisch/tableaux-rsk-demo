"""Zählt die Zugfolgen der Maschinen, die die App nicht selbst aufzählt (t = 2 mit n = 7, t = 3 mit n = 5), und schreibt data/trk_zuege.json.

Aufruf (aus dem Repo-Ordner, mit dem Python des Test-venv):
    python tools/trk_make_zuege.py            schreibt data/trk_zuege.json (rund 6 Sekunden)
    python tools/trk_make_zuege.py --check    rechnet neu und vergleicht mit der Datei (Exit-Code 1 bei Abweichung)

Alles sind Ganzzahlen. Gezählt wird mit der Stapelsimulation aus trk_zuege.py, nicht mit der Hakenformel."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import trk_zuege as Z  # noqa: E402

ZIEL = ROOT / "data" / "trk_zuege.json"
FAELLE = ((2, 7), (3, 5))


def rechnen():
    eintraege = []
    for t, n in FAELLE:
        erg = Z.zugfolgen_zaehlen(t, n)
        eintraege.append({"t": t, "n": n, "zugfolgen": erg.zugfolgen, "ausgaben": erg.ausgaben})
    return {
        "beschreibung": "Vollständige Zugfolgen von t Stapeln in Serie bei n Containern (Stapelsimulation) und die Zahl der verschiedenen Ausgaben.",
        "erzeugt_von": "tools/trk_make_zuege.py",
        "eintraege": eintraege,
    }


def main(argv):
    neu = rechnen()
    if "--check" in argv:
        alt = json.loads(ZIEL.read_text(encoding="utf-8"))
        if alt != neu:
            print("ABWEICHUNG: data/trk_zuege.json stimmt nicht mit der Neu-Rechnung überein")
            return 1
        print("OK: data/trk_zuege.json stimmt mit der Neu-Rechnung überein")
        return 0
    ZIEL.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("geschrieben:", ZIEL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
