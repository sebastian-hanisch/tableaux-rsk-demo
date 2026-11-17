"""Rechnet die vorgerechnete Tabelle zu Experiment 3 (ausgedachtes Modell V, n = 10, 20 000 Folgen je D und Zufalls-Seed) und schreibt data/trk_modellv.json.

Aufruf (aus dem Repo-Ordner, mit dem Python des Test-venv):
    python tools/trk_make_modellv.py            schreibt data/trk_modellv.json (rund 2 Minuten: 14 Läufe mit je 20 000 Folgen, der exakte Logarithmus ist langsam)
    python tools/trk_make_modellv.py --check    rechnet neu und vergleicht mit der Datei als Band (Mittel ± 0,02, Anteile ± 0,01; Exit-Code 1 bei Abweichung)

Zufall nur aus SplitMix64 (trk_rng.py); der Zufallsstrom je D ist `Zufalls-Seed + Index von D` (trk_scenario.strom). Die Summen sind Ganzzahlen."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import trk_evaluation as ev  # noqa: E402
from trk_scenario import D_WERTE  # noqa: E402

ZIEL = ROOT / "data" / "trk_modellv.json"
N = 10
ANZAHL = 20000
SEEDS = (101, 20261117)


def rechnen():
    zeilen = []
    for d in D_WERTE:
        eintrag = {"d": d, "seeds": {}}
        for seed in SEEDS:
            st = ev.modellv_statistik(N, d, ANZAHL, seed)
            eintrag["seeds"][str(seed)] = {
                "summe_erste_zeile": st["summe_erste_zeile"], "summe_zeilenzahl": st["summe_zeilenzahl"],
                "mittel_erste_zeile": round(st["mittel_erste_zeile"], 4), "mittel_zeilenzahl": round(st["mittel_zeilenzahl"], 4),
                "top": list(st["top"]), "top_anzahl": st["top_anzahl"], "top_anteil": st["top_anzahl"] / ANZAHL, "formen": st["formen_gesehen"],
            }
            print("D =", d, "Zufalls-Seed", seed, "fertig", flush=True)
        zeilen.append(eintrag)
    return {
        "beschreibung": "Ausgedachtes Modell V (Verweilzeit D, in Ankunftsabständen), n = 10: mittlere erste Zeile, mittlere Zeilenzahl, häufigste Form, Zahl der gesehenen Formen "
                        "je 20 000 Folgen; D = null heißt D → ∞ (gleichverteilt, Modell U).",
        "erzeugt_von": "tools/trk_make_modellv.py",
        "n": N, "anzahl": ANZAHL, "seeds": list(SEEDS), "zeilen": zeilen,
    }


def main(argv):
    neu = rechnen()
    if "--check" in argv:
        alt = json.loads(ZIEL.read_text(encoding="utf-8"))
        schlecht = []
        for za, zn in zip(alt["zeilen"], neu["zeilen"]):
            for s in map(str, SEEDS):
                a, b = za["seeds"][s], zn["seeds"][s]
                if (abs(a["mittel_erste_zeile"] - b["mittel_erste_zeile"]) > 0.02 or abs(a["mittel_zeilenzahl"] - b["mittel_zeilenzahl"]) > 0.02
                        or abs(a["top_anteil"] - b["top_anteil"]) > 0.01 or a["top"] != b["top"]):
                    schlecht.append((za["d"], s))
        if schlecht:
            print("ABWEICHUNG:", schlecht)
            return 1
        print("OK: data/trk_modellv.json stimmt mit der Neu-Rechnung überein (Band)")
        return 0
    ZIEL.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("geschrieben:", ZIEL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
