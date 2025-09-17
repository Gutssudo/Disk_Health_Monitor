"""Panneau d'affichage des données SMART."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from disk_health.dh_types import DiskType, SmartReport

CRITICAL_SPARE_THRESHOLD = 10  # PLR2004
CRITICAL_USED_THRESHOLD = 80  # PLR2004
NVME_COLUMN_COUNT = 4  # PLR2004
SATA_COLUMN_COUNT = 6  # PLR2004


class SmartDataPanel:
    """Panneau d'affichage des données SMART."""

    def __init__(self, parent_layout: QVBoxLayout) -> None:
        self.table = QTableWidget(0, 7)
        self.csv_btn = QPushButton("📄 Exporter CSV")
        self.raw_text = QTextEdit()
        self.save_btn = QPushButton("💾 Sauvegarder rapport")
        self.current_disk_type: DiskType | None = None

        self._setup_ui(parent_layout)

    def _setup_ui(self, parent_layout: QVBoxLayout) -> None:
        """Configure l'interface du panneau de données SMART."""
        # Layout horizontal principal pour côte à côte
        main_horizontal_layout = QHBoxLayout()

        # Table SMART (côté gauche)
        smart_group = QGroupBox("Données SMART")
        smart_layout = QVBoxLayout(smart_group)

        # Headers par défaut (seront mis à jour dynamiquement)
        self._set_default_headers()

        smart_layout.addWidget(self.table)
        smart_layout.addWidget(self.csv_btn)

        # Données brutes (côté droit)
        raw_group = QGroupBox("Données brutes")
        raw_layout = QVBoxLayout(raw_group)

        self.raw_text.setReadOnly(True)
        # Définir une taille minimale pour les données brutes
        self.raw_text.setMinimumWidth(300)

        raw_layout.addWidget(self.raw_text)
        raw_layout.addWidget(self.save_btn)

        # Ajouter les groupes au layout horizontal
        main_horizontal_layout.addWidget(smart_group)
        main_horizontal_layout.addWidget(raw_group)

        # Ajuster les proportions (table SMART plus large que données brutes)
        main_horizontal_layout.setStretchFactor(smart_group, 2)
        main_horizontal_layout.setStretchFactor(raw_group, 1)

        parent_layout.addLayout(main_horizontal_layout)

    def _set_default_headers(self) -> None:
        """Configure les headers par défaut."""
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Valeur", "Worst", "Seuil", "Raw", "Indicateur"]
        )
        self._configure_table_resize()

    def _configure_table_resize(self) -> None:
        """Configure le redimensionnement automatique du tableau."""
        # Configuration de la politique de redimensionnement du tableau
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Redimensionnement automatique des colonnes
        header = self.table.horizontalHeader()

        # Diviser équitablement l'espace entre toutes les colonnes
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def _get_headers_for_disk_type(self, disk_type: DiskType) -> list[str]:
        """Retourne les headers appropriés selon le type de disque."""
        if disk_type == DiskType.NVME:
            return ["Nom", "Valeur", "Raw", "Indicateur"]
        if disk_type == DiskType.SATA_ATA:
            return ["ID", "Nom", "Valeur", "Worst", "Seuil", "Raw", "Indicateur"]
        return ["ID", "Nom", "Valeur", "Worst", "Seuil", "Raw", "Indicateur"]

    def _configure_table_for_disk_type(self, disk_type: DiskType) -> None:
        """Configure le tableau selon le type de disque."""
        headers = self._get_headers_for_disk_type(disk_type)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.current_disk_type = disk_type
        # Reconfigurer le redimensionnement après changement de colonnes
        self._configure_table_resize()

    def display_smart_report(self, report: SmartReport) -> None:
        """Affiche un rapport SMART dans l'interface."""
        # Reconfigurer le tableau selon le type de disque
        self._configure_table_for_disk_type(report.disk_type)

        self._populate_table(report)
        self._display_raw_data(report)

    def _populate_table(self, report: SmartReport) -> None:
        """Remplit le tableau avec les attributs SMART."""
        self.table.setRowCount(len(report.attributes))

        for row, attr in enumerate(report.attributes):
            if report.disk_type == DiskType.NVME:
                items = [
                    str(attr.name),
                    str(attr.value),
                    str(attr.raw),
                    self._get_health_indicator(attr),
                ]
            else:  # SATA_ATA ou UNKNOWN
                items = [
                    str(attr.id),
                    str(attr.name),
                    str(attr.value),
                    str(attr.worst),
                    str(attr.thresh),
                    str(attr.raw),
                    self._get_health_indicator(attr),
                ]

            for col, item_text in enumerate(items):
                item = QTableWidgetItem(item_text)
                # La colonne indicateur est toujours la dernière
                if col == len(items) - 1:
                    self._style_health_indicator(item, item_text)
                self.table.setItem(row, col, item)

    def _get_health_indicator(self, attr: object) -> str:
        """Détermine l'indicateur de santé pour un attribut."""
        if self.current_disk_type == DiskType.NVME:
            return self._get_nvme_health_indicator(attr)
        return self._get_sata_health_indicator(attr)

    def _get_nvme_health_indicator(self, attr: object) -> str:
        """Détermine l'indicateur de santé pour un disque NVME."""
        attr_name = str(getattr(attr, "name", "")).lower()
        value_str = str(getattr(attr, "value", ""))

        if "critical_warning" in attr_name and value_str != "0":
            return "⚠️"

        if "available_spare" in attr_name:
            spare = self._safe_int_conversion(value_str)
            if spare is not None and spare < CRITICAL_SPARE_THRESHOLD:
                return "⚠️"

        if "percentage_used" in attr_name:
            used = self._safe_int_conversion(value_str)
            if used is not None and used > CRITICAL_USED_THRESHOLD:
                return "⚠️"

        if "media_errors" in attr_name and value_str != "0":
            return "⚠️"

        return "✅"

    def _get_sata_health_indicator(self, attr: object) -> str:
        """Détermine l'indicateur de santé pour un disque SATA."""
        if not (hasattr(attr, "value") and hasattr(attr, "thresh")):
            return "✅"

        value_str = str(getattr(attr, "value", ""))
        thresh_str = str(getattr(attr, "thresh", ""))

        value = self._safe_int_conversion(value_str, default=0)
        thresh = self._safe_int_conversion(thresh_str, default=0)

        if value < thresh:
            return "⚠️"

        return "✅"

    def _safe_int_conversion(
        self, value_str: str, default: int | None = None
    ) -> int | None:
        """Convertit une chaîne en entier de manière sécurisée."""
        try:
            return int(value_str) if value_str.isdigit() else default
        except (ValueError, TypeError):
            return default

    def _style_health_indicator(self, item: QTableWidgetItem, text: str) -> None:
        """Applique le style à l'indicateur de santé."""
        if text == "⚠️":
            item.setBackground(QColor(255, 200, 200))  # Rouge clair
        else:
            item.setBackground(QColor(200, 255, 200))  # Vert clair

    def _display_raw_data(self, report: SmartReport) -> None:
        """Affiche les données brutes."""
        if report.raw:
            self.raw_text.setPlainText(report.raw)
        else:
            self.raw_text.setPlainText("Aucune donnée brute disponible")
