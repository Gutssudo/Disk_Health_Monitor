"""Panneau de benchmark de performance."""

from typing import Any

import matplotlib as mpl  # ICN001: alias matplotlib as mpl
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)

from disk_health.dh_types import BenchmarkResults
from disk_health.utils import format_speed

mpl.use("QtAgg")  # Correction ICN001


class BenchmarkPanel:
    """Panneau de benchmark de performance."""

    def __init__(self, parent_layout: QVBoxLayout) -> None:
        self.benchmark_group = QGroupBox("Benchmark de Performance")
        self.progress_bar = QProgressBar()
        self.fig = Figure(figsize=(10, 6), facecolor="white")
        self.canvas: Any = FigureCanvas(self.fig)  # type: ignore[no-untyped-call]
        self.stats_labels: dict[str, QLabel] = {}
        self._is_progress_visible = False  # Track visibility state manually

        self._setup_ui(parent_layout)

    def _setup_ui(self, parent_layout: QVBoxLayout) -> None:
        """Configure l'interface du panneau de benchmark."""
        # Masquer explicitement la barre de progression au départ
        self.progress_bar.hide()
        self._is_progress_visible = False
        parent_layout.addWidget(self.progress_bar)

        benchmark_layout = QHBoxLayout(self.benchmark_group)

        # Graphiques
        self._setup_plots()
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.canvas)

        # Statistiques
        stats_layout = self._create_stats_panel()

        benchmark_layout.addLayout(graph_layout)
        benchmark_layout.addLayout(stats_layout)

        parent_layout.addWidget(self.benchmark_group)

    def _setup_plots(self) -> None:
        """Configure les graphiques matplotlib."""
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        # Style des graphiques
        for ax in [self.ax1, self.ax2]:
            ax.grid(visible=True, alpha=0.3)  # FBT003: argument nommé
            ax.set_facecolor("#f8f9fa")

    def _create_stats_panel(self) -> QVBoxLayout:
        """Crée le panneau de statistiques."""
        stats_layout = QVBoxLayout()

        stat_names = [
            ("avg_read", "Vitesse moy.: -- MB/s"),
            ("max_read", "Vitesse max.: -- MB/s"),
            ("min_read", "Vitesse min.: -- MB/s"),
            ("avg_access", "Accès moy.: -- ms"),
            ("max_access", "Accès max.: -- ms"),
            ("min_access", "Accès min.: -- ms"),
        ]

        for key, text in stat_names:
            label = QLabel(text)
            label.setFont(QFont("Monospace", 9))
            self.stats_labels[key] = label
            stats_layout.addWidget(label)

        stats_layout.addStretch()
        return stats_layout

    def update_progress(self, percentage: float) -> None:
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(int(percentage))

    def show_progress(self) -> None:
        """Affiche la barre de progression."""
        self.progress_bar.show()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self._is_progress_visible = True

    def hide_progress(self) -> None:
        """Cache la barre de progression."""
        self.progress_bar.hide()
        self.progress_bar.setVisible(False)
        self._is_progress_visible = False

    def is_progress_visible(self) -> bool:
        """Retourne l'état de visibilité de la barre de progression."""
        return self._is_progress_visible

    def update_benchmark_results(self, results: BenchmarkResults) -> None:
        """Met à jour l'affichage des résultats de benchmark."""
        self._update_plots(results)
        self._update_stats(results)

    def _update_plots(self, results: BenchmarkResults) -> None:
        """Met à jour les graphiques."""
        self.ax1.clear()
        self.ax2.clear()

        if results.positions:
            # Graphique de vitesse de lecture
            self.ax1.plot(results.positions, results.read_speeds, "b-", alpha=0.7)
            self.ax1.set_ylabel("Vitesse (MB/s)")
            self.ax1.set_title("Vitesse de lecture par position")
            self.ax1.grid(visible=True, alpha=0.3)  # FBT003
            self.ax1.set_ylim(bottom=0)  # Force l'axe Y à commencer à 0

            # Graphique de temps d'accès
            self.ax2.plot(results.positions, results.access_times, "r-", alpha=0.7)
            self.ax2.set_ylabel("Temps d'accès (ms)")
            self.ax2.set_xlabel("Position sur le disque (%)")
            self.ax2.set_title("Temps d'accès par position")
            self.ax2.grid(visible=True, alpha=0.3)  # FBT003

        self.canvas.draw()  # type: ignore[no-untyped-call]

    def _update_stats(self, results: BenchmarkResults) -> None:
        """Met à jour les statistiques affichées."""
        stats_updates = {
            "avg_read": f"Vitesse moy.: {format_speed(results.avg_read_speed)}",
            "max_read": f"Vitesse max.: {format_speed(results.max_read_speed)}",
            "min_read": f"Vitesse min.: {format_speed(results.min_read_speed)}",
            "avg_access": f"Accès moy.: {results.avg_access_time:.1f} ms",
            "max_access": f"Accès max.: {results.max_access_time:.1f} ms",
            "min_access": f"Accès min.: {results.min_access_time:.1f} ms",
        }

        for key, text in stats_updates.items():
            if key in self.stats_labels:
                self.stats_labels[key].setText(text)
