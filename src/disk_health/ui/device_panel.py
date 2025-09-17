"""Panneau de gestion des périphériques."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from disk_health.dh_types import DeviceInfo


class DevicePanel:
    """Panneau de gestion des périphériques."""

    def __init__(self, parent_layout: QVBoxLayout) -> None:
        self.device_combo = QComboBox()
        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.run_btn = QPushButton("▶️ Vérification SMART")
        self.bench_btn = QPushButton("📈 Benchmark disque")
        self.health_label = QLabel("Santé: UNKNOWN")

        self._setup_ui(parent_layout)

    def _setup_ui(self, parent_layout: QVBoxLayout) -> None:
        """Configure l'interface du panneau de périphériques."""
        control_group = QGroupBox("Contrôles")
        control_layout = QHBoxLayout(control_group)

        self._style_health_label()

        widgets = [
            self.device_combo,
            self.refresh_btn,
            self.run_btn,
            self.bench_btn,
            self.health_label,
        ]

        for widget in widgets:
            control_layout.addWidget(widget)

        parent_layout.addWidget(control_group)

    def _style_health_label(self) -> None:
        """Applique le style au label de santé."""
        self.health_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.health_label.setFont(font)

    def update_health_display(self, health: str) -> None:
        """Met à jour l'affichage de l'état de santé."""
        self.health_label.setText(f"Santé: {health}")

        # Couleur selon l'état
        if health == "PASSED":
            color = "green"
        elif health == "FAILED":
            color = "red"
        else:
            color = "orange"

        self.health_label.setStyleSheet(f"color: {color};")

    def populate_devices(self, devices: list[DeviceInfo]) -> None:
        """Remplit le combo box avec les périphériques."""
        self.device_combo.clear()
        for device in devices:
            display_text = f"{device.path} - {device.model} ({device.size})"
            self.device_combo.addItem(display_text, device.path)

    def get_selected_device(self) -> str | None:
        """Retourne le périphérique sélectionné."""
        data = self.device_combo.currentData()
        return str(data) if data is not None else None
