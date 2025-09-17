"""Widget principal avec onglets Benchmark et SMART."""

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from disk_health.ui.benchmark_panel import BenchmarkPanel
from disk_health.ui.smart_data_panel import SmartDataPanel


class MainTabs(QTabWidget):
    """Widget principal avec onglets séparés pour Benchmark et SMART."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_tabs()

    def _setup_tabs(self) -> None:
        """Configure les onglets principaux."""
        # Onglet SMART
        self.smart_widget = QWidget()
        smart_layout = QVBoxLayout(self.smart_widget)
        self.smart_panel = SmartDataPanel(smart_layout)
        self.addTab(self.smart_widget, "SMART")

        # Onglet Benchmark
        self.benchmark_widget = QWidget()
        benchmark_layout = QVBoxLayout(self.benchmark_widget)
        self.benchmark_panel = BenchmarkPanel(benchmark_layout)
        self.addTab(self.benchmark_widget, "Benchmark")

    def get_smart_panel(self) -> SmartDataPanel:
        """Retourne le panel SMART."""
        return self.smart_panel

    def get_benchmark_panel(self) -> BenchmarkPanel:
        """Retourne le panel Benchmark."""
        return self.benchmark_panel
