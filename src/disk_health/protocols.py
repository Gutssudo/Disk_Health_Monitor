"""Protocoles pour définir les contrats d'interface."""

from typing import Protocol

from PySide6.QtCore import Signal

from disk_health.dh_types import DeviceInfo, SmartReport


class AsyncWorkerProtocol(Protocol):
    """Protocole pour les workers asynchrones."""

    finished: Signal

    def run(self) -> None:
        """Exécute le worker."""
        ...


class BenchmarkWorkerProtocol(Protocol):
    """Protocole pour les workers de benchmark."""

    progress: Signal
    finished: Signal

    def __init__(
        self,
        device: str,
        block_size: int = 4 * 1024 * 1024,
        sample_count: int = 100,
    ) -> None:
        """Initialise le worker de benchmark."""
        ...

    def run(self) -> None:
        """Exécute le benchmark."""
        ...


class SmartMonitorProtocol(Protocol):
    """Protocole pour le moniteur SMART principal."""

    def refresh_devices(self) -> None:
        """Rafraîchit la liste des périphériques."""
        ...

    def run_check(self) -> None:
        """Lance une vérification SMART."""
        ...

    def run_benchmark(self) -> None:
        """Lance un benchmark."""
        ...

    def save_report(self) -> None:
        """Sauvegarde le rapport."""
        ...

    def export_csv(self) -> None:
        """Exporte en CSV."""
        ...


class DeviceManagerProtocol(Protocol):
    """Protocole pour la gestion des périphériques."""

    async def list_devices(self) -> list[DeviceInfo]:
        """Liste les périphériques disponibles."""
        ...

    async def check_device(self, device: str) -> SmartReport:
        """Vérifie un périphérique."""
        ...


class ReportManagerProtocol(Protocol):
    """Protocole pour la gestion des rapports."""

    def save_json(self, report: SmartReport, filepath: str) -> None:
        """Sauvegarde un rapport en JSON."""
        ...

    def save_csv(self, report: SmartReport, filepath: str) -> None:
        """Sauvegarde un rapport en CSV."""
        ...
