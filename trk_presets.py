"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio).

Alle Regler, die ein Schnellstart-Szenario setzt oder die das aktive Szenario aufheben sollen, stehen in SETTING_SPECS (auch die im Hauptbereich).
Der Schlüssel ist der Regler-Schlüssel im Session State; `url_param` der Name in der Adresszeile."""

import random
from dataclasses import dataclass

import streamlit as st

import trk_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    options: tuple | None = None     # erlaubte Werte (Auswahlfelder)
    max_len: int | None = None       # Texte werden auf diese Länge gekürzt


SETTING_SPECS = {
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "e1_text": SettingSpec("folge", str, C.DEFAULT_TEXT, max_len=80),
    "e1_n": SettingSpec("zn", int, C.E1_DEFAULT_N, C.E1_N_MIN, C.E1_N_MAX),
    "e1_schritt": SettingSpec("schritt", int, 6, 1, C.E1_MAX_LAENGE),
    "e1_orient": SettingSpec("orient", str, C.ORIENT_FALLEND, options=C.ORIENTIERUNGEN),
    "e1_zurueck": SettingSpec("zurueck", bool, False),
    "e2_n": SettingSpec("fn", int, C.E2_DEFAULT_N, C.E2_N_MIN, C.E2_N_MAX),
    "e2_hl": SettingSpec("hl", str, C.HL_KEINE, options=C.HERVORHEBUNGEN),
    "e3_d": SettingSpec("d", str, "1", options=C.D_LABELS),
    "e3_n": SettingSpec("vn", int, C.E3_DEFAULT_N, C.E3_N_MIN, C.E3_N_MAX),
    "e3_anzahl": SettingSpec("anzahl", int, C.E3_DEFAULT_ANZAHL, C.E3_ANZAHL_MIN, C.E3_ANZAHL_MAX),
    "e4_t": SettingSpec("t", int, C.E4_DEFAULT_T, C.E4_T_MIN, C.E4_T_MAX),
    "e4_n": SettingSpec("zugn", int, C.E4_DEFAULT_N, C.E4_N_MIN, C.E4_N_MAX),
    "e5_inhalt": SettingSpec("inhalt", str, C.DEFAULT_INHALT, options=C.INHALTE),
    "e5_text": SettingSpec("wort", str, C.DEFAULT_WORT, max_len=40),
    "e5_fassung": SettingSpec("fassung", str, C.FASSUNG_STRENG, options=C.FASSUNGEN),
}
PRESET_KEYS = {key: key for key in SETTING_SPECS if key != "seed_input"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def _bool(text):
    return str(text).strip().lower() in ("1", "true", "ja", "wahr")


def begrenze(spec, roh):
    """Wandelt einen Wert aus der Adresszeile in einen gültigen Reglerwert um; None, wenn das nicht geht."""
    try:
        wert = _bool(roh) if spec.caster is bool else spec.caster(roh)
    except (ValueError, TypeError):
        return None
    if spec.options is not None and wert not in spec.options:
        return None
    if spec.lo is not None:
        wert = max(spec.lo, wert)
    if spec.hi is not None:
        wert = min(spec.hi, wert)
    if spec.max_len is not None:
        wert = wert[: spec.max_len]
    return wert


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            wert = begrenze(spec, qp[spec.url_param])
            if wert is not None:
                st.session_state[state_key] = wert
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Setzt die Regler des Szenarios; alle übrigen Regler gehen auf ihre Voreinstellung zurück, damit das Szenario wirklich das gewählte ist."""
    for key, spec in SETTING_SPECS.items():
        if key == "seed_input":
            continue
        st.session_state[key] = C.PRESETS[name].get(key, spec.default)


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen Standardwert) mit dem Session State.
    Der Zufalls-Seed gehört nicht zu den Szenarien (er steuert nur die Zufallsfolgen)."""
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(state_key, spec.default)
            for state_key, spec in SETTING_SPECS.items()
            if state_key != "seed_input"
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
