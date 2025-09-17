"""Module de gestion des rapports et export de données."""

import csv
import json
from pathlib import Path

from disk_health.dh_types import DiskType, SmartReport


class ReportManager:
    """Gestionnaire pour la sauvegarde et l'export de rapports."""

    def save_json(self, report: SmartReport, filepath: str) -> None:
        """Sauvegarde un rapport au format JSON."""
        report_data = {
            "device": report.device,
            "health": report.health,
            "disk_type": report.disk_type.value,
            "attributes": [
                {
                    "id": attr.id,
                    "name": attr.name,
                    "value": attr.value,
                    "worst": attr.worst,
                    "thresh": attr.thresh,
                    "raw": attr.raw,
                }
                for attr in report.attributes
            ],
            "raw": report.raw,
            "json_data": report.json_data,
        }

        with Path(filepath).open("w", encoding="utf-8") as f:  # PTH123
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def save_csv(self, report: SmartReport, filepath: str) -> None:
        """Sauvegarde les attributs SMART au format CSV adapté au type de disque."""
        with Path(filepath).open("w", newline="", encoding="utf-8") as f:  # PTH123
            writer = csv.writer(f)
            writer.writerow(["Device", "Health", "Type"])
            writer.writerow([report.device, report.health, report.disk_type.value])
            writer.writerow([])  # Ligne vide

            # Headers adaptés au type de disque
            if report.disk_type == DiskType.NVME:
                writer.writerow(["Name", "Value", "Raw"])
                for attr in report.attributes:
                    writer.writerow(
                        [
                            attr.name,
                            attr.value,
                            attr.raw,
                        ]
                    )
            else:  # SATA_ATA ou UNKNOWN
                writer.writerow(["ID", "Name", "Value", "Worst", "Thresh", "Raw"])
                for attr in report.attributes:
                    writer.writerow(
                        [
                            attr.id,
                            attr.name,
                            attr.value,
                            attr.worst,
                            attr.thresh,
                            attr.raw,
                        ]
                    )

    def get_default_json_filename(self, device: str) -> str:
        """Génère un nom de fichier par défaut pour JSON."""
        safe_device = device.replace("/", "_").replace(" ", "_")
        return f"smart_report_{safe_device}.json"

    def get_default_csv_filename(self, device: str) -> str:
        """Génère un nom de fichier par défaut pour CSV."""
        safe_device = device.replace("/", "_").replace(" ", "_")
        return f"smart_report_{safe_device}.csv"
