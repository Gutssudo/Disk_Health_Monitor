"""Interface utilisateur principale pour le monitoring SMART."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QThread

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from disk_health.benchmark import BenchmarkWorker
from disk_health.dh_types import BenchmarkResults, DeviceInfo, SmartReport
from disk_health.report_manager import ReportManager
from disk_health.smart import run_smart_check
from disk_health.ui.device_panel import DevicePanel
from disk_health.ui.main_tabs import MainTabs
from disk_health.utils import SmartctlNotFoundError, has_smartctl, list_block_devices
from disk_health.workers import AsyncWorker


class SmartMonitor(QWidget):
    """Interface principale de monitoring SMART avec onglets séparés."""

    def __init__(self) -> None:
        super().__init__()

        # Vérification de smartctl au démarrage
        if not has_smartctl():
            raise SmartctlNotFoundError

        self.setWindowTitle("SMART Disk Monitor + Advanced Benchmark")
        self.resize(1200, 800)

        # Composants
        self.report_manager = ReportManager()
        self.current_report: SmartReport | None = None
        self.threads: list[QThread] = []

        # Interface utilisateur
        self._setup_ui()
        self._connect_signals()
        self._initialize_devices()

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        main_layout = QVBoxLayout(self)

        # Panel de sélection de périphérique (en haut)
        self.device_panel = DevicePanel(main_layout)

        # Onglets principaux
        self.main_tabs = MainTabs()
        main_layout.addWidget(self.main_tabs)

    def _connect_signals(self) -> None:
        """Connecte tous les signaux."""
        # Signaux du device panel
        self.device_panel.refresh_btn.clicked.connect(self.refresh_devices)
        self.device_panel.run_btn.clicked.connect(self.run_check)
        self.device_panel.bench_btn.clicked.connect(self.run_benchmark)

        # Signaux du panel SMART
        smart_panel = self.main_tabs.get_smart_panel()
        smart_panel.save_btn.clicked.connect(self.save_report)
        smart_panel.csv_btn.clicked.connect(self.export_csv)

    def _initialize_devices(self) -> None:
        """Initialise la liste des périphériques."""
        self.refresh_devices()

    def refresh_devices(self) -> None:
        """Rafraîchit la liste des périphériques."""
        worker = AsyncWorker(list_block_devices())
        worker.finished.connect(self._on_devices_loaded)
        self.threads.append(worker)
        worker.start()

    def _on_devices_loaded(self, devices: list[DeviceInfo]) -> None:
        """Callback quand les périphériques sont chargés."""
        self.device_panel.populate_devices(devices)

    def run_check(self) -> None:
        """Lance une vérification SMART."""
        device = self.device_panel.get_selected_device()
        if not device:
            QMessageBox.warning(self, "Erreur", "Aucun périphérique sélectionné")
            return

        # Basculer vers l'onglet SMART
        self.main_tabs.setCurrentIndex(0)

        worker = AsyncWorker(run_smart_check(device))
        worker.finished.connect(self._on_smart_check_finished)
        self.threads.append(worker)
        worker.start()

    def _on_smart_check_finished(self, report: SmartReport | Exception) -> None:
        """Callback quand la vérification SMART est terminée."""
        if isinstance(report, SmartctlNotFoundError):
            QMessageBox.critical(self, "Smartctl introuvable", str(report))
            return
        if isinstance(report, Exception):
            QMessageBox.critical(
                self,
                "Erreur lors de la vérification SMART",
                f"Une erreur s'est produite : {report!s}",
            )
            return

        self.current_report = report
        self.device_panel.update_health_display(report.health)
        self.main_tabs.get_smart_panel().display_smart_report(report)

    def run_benchmark(self) -> None:
        """Lance un benchmark de performance."""
        device = self.device_panel.get_selected_device()
        if not device:
            QMessageBox.warning(self, "Erreur", "Aucun périphérique sélectionné")
            return

        # Basculer vers l'onglet Benchmark
        self.main_tabs.setCurrentIndex(1)

        benchmark_panel = self.main_tabs.get_benchmark_panel()
        benchmark_panel.show_progress()

        worker = BenchmarkWorker(device)
        worker.progress.connect(self._on_benchmark_progress)
        worker.finished.connect(self._on_benchmark_finished)
        self.threads.append(worker)
        worker.start()

    def _on_benchmark_progress(
        self, percentage: float, _read_speed: float, _access_time: float
    ) -> None:
        """Callback pour la progression du benchmark."""
        self.main_tabs.get_benchmark_panel().update_progress(percentage)

    def _on_benchmark_finished(self, results: BenchmarkResults) -> None:
        """Callback quand le benchmark est terminé."""
        benchmark_panel = self.main_tabs.get_benchmark_panel()
        benchmark_panel.hide_progress()
        benchmark_panel.update_benchmark_results(results)

    def save_report(self) -> None:
        """Sauvegarde le rapport au format JSON."""
        if not self.current_report:
            QMessageBox.warning(self, "Erreur", "Aucun rapport à sauvegarder")
            return

        default_name = self.report_manager.get_default_json_filename(
            self.current_report.device
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le rapport", default_name, "Fichiers JSON (*.json)"
        )

        if filepath:
            try:
                self.report_manager.save_json(self.current_report, filepath)
                QMessageBox.information(self, "Succès", "Rapport sauvegardé")
            except (OSError, PermissionError) as e:
                QMessageBox.critical(
                    self, "Erreur", f"Erreur lors de la sauvegarde: {e}"
                )

    def export_csv(self) -> None:
        """Exporte le rapport au format CSV."""
        if not self.current_report:
            QMessageBox.warning(self, "Erreur", "Aucun rapport à exporter")
            return

        default_name = self.report_manager.get_default_csv_filename(
            self.current_report.device
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", default_name, "Fichiers CSV (*.csv)"
        )

        if filepath:
            try:
                self.report_manager.save_csv(self.current_report, filepath)
                QMessageBox.information(self, "Succès", "Rapport exporté")
            except (OSError, PermissionError) as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {e}")
