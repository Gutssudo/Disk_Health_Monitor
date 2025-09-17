"""Configuration pytest pour le projet disk_health."""

import os  # Correction PLC0415: import au top-level
import sys

import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> None:
    """Configuration globale pour tous les tests."""
    # Configuration pour éviter les warnings Qt en mode test
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    # Nettoyage après tous les tests
