"""Module de benchmark de performance des disques."""

import time
from pathlib import Path
from typing import BinaryIO, Protocol

import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox

from disk_health.dh_types import BenchmarkResults


class BenchmarkProgressProtocol(Protocol):
    """Protocole pour les signaux de progression du benchmark."""

    def emit(self, percentage: float, read_speed: float, access_time: float) -> None:
        """Émet un signal de progression."""
        ...


class BenchmarkFinishedProtocol(Protocol):
    """Protocole pour les signaux de fin de benchmark."""

    def emit(self, results: BenchmarkResults) -> None:
        """Émet les résultats finaux."""
        ...


def _calculate_read_speed(data_size: int, elapsed_time: float) -> float:
    """Calcule la vitesse de lecture en MB/s."""
    if elapsed_time <= 0:
        return 0.0
    return (data_size / (1024 * 1024)) / elapsed_time


def _calculate_position_percentage(position: int, total_size: int) -> float:
    """Calcule le pourcentage de position sur le disque."""
    if total_size <= 0:
        return 0.0
    return (position / total_size) * 100


def compute_benchmark_stats(
    read_speeds: list[float], access_times: list[float], positions: list[float]
) -> BenchmarkResults:
    """Calcule les statistiques complètes du benchmark."""
    if not read_speeds:
        return BenchmarkResults(
            read_speeds=[],
            access_times=[],
            positions=[],
            avg_read_speed=0.0,
            min_read_speed=0.0,
            max_read_speed=0.0,
            avg_access_time=0.0,
            min_access_time=0.0,
            max_access_time=0.0,
        )

    return BenchmarkResults(
        read_speeds=read_speeds,
        access_times=access_times,
        positions=positions,
        avg_read_speed=float(np.mean(read_speeds)),
        min_read_speed=float(np.min(read_speeds)),
        max_read_speed=float(np.max(read_speeds)),
        avg_access_time=float(np.mean(access_times)) if access_times else 0.0,
        min_access_time=float(np.min(access_times)) if access_times else 0.0,
        max_access_time=float(np.max(access_times)) if access_times else 0.0,
    )


class BenchmarkWorker(QThread):
    """Worker thread pour exécuter le benchmark de performance."""

    progress = Signal(float, float, float)  # percentage, read_speed, access_time
    finished = Signal(object)  # BenchmarkResults

    def __init__(
        self,
        device: str,
        block_size: int = 4 * 1024 * 1024,
        sample_count: int = 100,
    ) -> None:  # ANN204
        super().__init__()
        self.device = device
        self.block_size = block_size
        self.sample_count = sample_count

    def run(self) -> None:
        """Exécute le benchmark de performance."""
        read_speeds: list[float] = []
        access_times: list[float] = []
        positions: list[float] = []

        try:
            self._run_benchmark(read_speeds, access_times, positions)
            results = compute_benchmark_stats(read_speeds, access_times, positions)
            self.finished.emit(results)

        except PermissionError:
            self._show_permission_error()
        except (OSError, RuntimeError) as e:
            # Catch IO and runtime errors for robustness, but log for debug
            self._show_generic_error(str(e))

    def _run_benchmark(
        self,
        read_speeds: list[float],
        access_times: list[float],
        positions: list[float],
    ) -> None:
        """Exécute la boucle principale du benchmark."""
        with Path(self.device).open("rb") as f:  # PTH123
            total_size = self._get_file_size(f)

            for i in range(self.sample_count):
                seek_pos = (i * total_size) // self.sample_count

                # Mesure du temps d'accès
                seek_time = self._measure_seek_time(f, seek_pos)

                # Mesure de la vitesse de lecture
                read_speed = self._measure_read_speed(f)

                # Calcul des métriques
                percentage = _calculate_position_percentage(seek_pos, total_size)

                read_speeds.append(read_speed)
                access_times.append(seek_time)
                positions.append(percentage)

                self.progress.emit(percentage, read_speed, seek_time)

    def _get_file_size(self, file_obj: BinaryIO) -> int:
        """Obtient la taille du fichier."""
        file_obj.seek(0, 2)  # Fin du fichier
        size = file_obj.tell()
        file_obj.seek(0)  # Retour au début
        return size

    def _measure_seek_time(self, file_obj: BinaryIO, position: int) -> float:
        """Mesure le temps d'accès en millisecondes."""
        start_time = time.time()
        file_obj.seek(position)
        return (time.time() - start_time) * 1000

    def _measure_read_speed(self, file_obj: BinaryIO) -> float:
        """Mesure la vitesse de lecture en MB/s."""
        start_time = time.time()
        data = file_obj.read(self.block_size)

        if not data:
            return 0.0

        elapsed_time = time.time() - start_time
        return _calculate_read_speed(len(data), elapsed_time)

    def _show_permission_error(self) -> None:
        """Affiche une erreur de permission."""
        QMessageBox.critical(None, "Erreur", "Permission refusée (lancer avec sudo).")

    def _show_generic_error(self, error_msg: str) -> None:
        """Affiche une erreur générique."""
        QMessageBox.critical(None, "Erreur", error_msg)
