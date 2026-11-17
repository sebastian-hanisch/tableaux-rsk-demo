"""Gemeinsame Fixtures: die Handfolge, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b), und die Marke „slow“."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: dauert einige Sekunden (Aufzählung aller 9! Folgen, Neu-Rechnung des Modells V)")


@pytest.fixture
def hand():
    """Handfolge n = 6: (1, 3, 6, 2, 5, 4). Von Hand: P = [[1,2,4],[3,5],[6]], Q = [[1,2,3],[4,5],[6]], Form (3,2,1), f = 16."""
    return (1, 3, 6, 2, 5, 4)
