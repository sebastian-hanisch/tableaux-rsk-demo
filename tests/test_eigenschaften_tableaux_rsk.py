"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen über das Einfügen, die ohne bekanntes Ergebnis prüfbar sind. Je Eigenschaft 30 bis 50 Zufallsfolgen mit festem Zufalls-Seed
(SplitMix64), dazu Randfälle. Jede Eigenschaft gilt für Folgen ohne gleiche Werte (Permutationen); wo es um Wörter geht, steht es dabei.

Die Eigenschaften sind Lehrbuchstoff (Schensted 1961, Symmetrien der Zuordnung), hier nur nachgemessen."""

import pytest

import trk_rsk as R
import trk_scenario as S
from trk_rng import SplitMix64

ZUFALLS_SEED = 20261117


def _folgen(anzahl, n_min=2, n_max=12, seed=ZUFALLS_SEED):
    rng = SplitMix64(seed)
    erg = []
    for _ in range(anzahl):
        n = n_min + rng.below(n_max - n_min + 1)
        erg.append(S.folge_modell_u(n, rng))
    return erg


def test_monotone_umbenennung_der_werte_aendert_q_und_form_nicht():
    rng = SplitMix64(5)
    for p in _folgen(40):
        werte = sorted(rng.below(10 ** 6) + 10 * i for i in range(len(p)))     # streng wachsende, beliebige Werte
        neu = tuple(werte[x - 1] for x in p)
        P1, Q1 = R.einfuegen(p)
        P2, Q2 = R.einfuegen(neu)
        assert Q1 == Q2 and R.form(P1) == R.form(P2)
        assert [[werte[x - 1] for x in z] for z in P1] == P2


def test_spiegeln_der_folge_transponiert_die_form():
    for p in _folgen(50):
        assert R.form(R.einfuegen(p[::-1])[0]) == R.konjugiert(R.form(R.einfuegen(p)[0]))


def test_komplement_transponiert_die_form():
    for p in _folgen(50):
        n = len(p)
        assert R.form(R.einfuegen(tuple(n + 1 - x for x in p))[0]) == R.konjugiert(R.form(R.einfuegen(p)[0]))


def test_spiegeln_und_komplement_zusammen_lassen_die_form_gleich():
    for p in _folgen(40):
        n = len(p)
        assert R.form(R.einfuegen(tuple(n + 1 - x for x in p[::-1]))[0]) == R.form(R.einfuegen(p)[0])


def test_die_inverse_folge_vertauscht_p_und_q():
    for p in _folgen(50):
        inv = tuple(p.index(v) + 1 for v in range(1, len(p) + 1))
        P1, Q1 = R.einfuegen(p)
        P2, Q2 = R.einfuegen(inv)
        assert P2 == Q1 and Q2 == P1


def test_neues_groesstes_element_am_ende_verlaengert_die_erste_zeile_um_eins():
    for p in _folgen(40):
        lam = R.form(R.einfuegen(p)[0])
        neu = R.form(R.einfuegen(p + (len(p) + 1,))[0])
        assert neu[0] == lam[0] + 1 and neu[1:] == lam[1:]


def test_neues_kleinstes_element_am_ende_verlaengert_die_erste_spalte_um_eins():
    for p in _folgen(40):
        lam = R.form(R.einfuegen(p)[0])
        neu = R.form(R.einfuegen(tuple(x + 1 for x in p) + (1,))[0])
        assert len(neu) == len(lam) + 1 and R.konjugiert(neu)[1:] == R.konjugiert(lam)[1:]


def test_form_von_q_bis_i_ist_die_form_von_p_nach_i_schritten_und_die_erste_zeile_nimmt_nie_ab():
    for p in _folgen(40):
        P, Q, schritte = R.einfuegen_protokoll(p)
        erste = 0
        for i, s in enumerate(schritte, 1):
            assert R.form(s.p_danach) == R.form_nach_schritt(Q, i)
            assert sum(R.form(s.p_danach)) == i
            assert R.form(s.p_danach)[0] >= erste
            erste = R.form(s.p_danach)[0]


def test_q_eines_praefixes_ist_q_eingeschraenkt():
    for p in _folgen(30):
        _, Q = R.einfuegen(p)
        for i in range(1, len(p) + 1):
            Pi, Qi = R.einfuegen(p[:i])
            assert Qi == [[x for x in z if x <= i] for z in Q if any(x <= i for x in z)]


def test_die_form_haengt_nicht_an_der_darstellung_der_eingabe():
    for p in _folgen(30):
        P, Q = R.einfuegen(p)
        for variante in (list(p), tuple(p), tuple(10 * x + 3 for x in p), tuple(x * x for x in p)):
            assert R.form(R.einfuegen(variante)[0]) == R.form(P)
        folge, _, fehler = S.folge_einlesen(" ".join(str(10 * x + 3) for x in p), 40)
        assert fehler is None and folge == p


def test_summe_der_zeilenlaengen_ist_n_und_p_hat_genau_die_werte_der_folge():
    for p in _folgen(40):
        P, Q = R.einfuegen(p)
        assert sum(R.form(P)) == len(p) and sorted(x for z in P for x in z) == sorted(p)
        assert R.ist_standard(P, len(p)) and R.ist_standard(Q, len(p))


def test_p_gleich_q_fuer_selbstinverse_folgen():
    rng = SplitMix64(11)
    gesehen = 0
    for _ in range(60):
        n = 2 + rng.below(9)
        p = list(range(1, n + 1))
        # eine Involution: zufällige Paare vertauschen
        frei = list(p)
        rng.shuffle(frei)
        for k in range(0, len(frei) - 1, 2):
            if rng.below(2):
                a, b = frei[k], frei[k + 1]
                p[a - 1], p[b - 1] = b, a
        p = tuple(p)
        assert all(p[p[i] - 1] == i + 1 for i in range(n))
        P, Q = R.einfuegen(p)
        assert P == Q
        gesehen += 1
    assert gesehen == 60


def test_wort_mit_umbenannten_buchstaben_haelt_die_form():
    """Gilt für Wörter (duale Einfügung): eine streng wachsende Umbenennung der Buchstaben ändert Q und die Form nicht."""
    rng = SplitMix64(9)
    for _ in range(40):
        inhalt = (2, 1, 3, 1)
        wort = S.zufallswort(inhalt, rng.below(10 ** 6))
        P1, Q1 = R.einfuegen(wort, dual=True)
        neu = tuple(7 * x + 2 for x in wort)
        P2, Q2 = R.einfuegen(neu, dual=True)
        assert Q1 == Q2 and R.form(P1) == R.form(P2)


@pytest.mark.parametrize("n", (1, 2, 3))
def test_randfaelle_kleine_n(n):
    from itertools import permutations
    for p in permutations(range(1, n + 1)):
        P, Q = R.einfuegen(p)
        assert R.zurueckrechnen(P, Q) == p and sum(R.form(P)) == n
