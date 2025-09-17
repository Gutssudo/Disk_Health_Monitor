"""Module de gestion des données SMART."""

from typing import Any

from disk_health.dh_types import DiskType, SmartAttribute, SmartPayload, SmartReport
from disk_health.utils import query_smart_json


def _detect_disk_type(device: str, json_data: dict[str, Any] | None) -> DiskType:
    """Détecte le type de disque à partir du chemin et des données JSON."""
    # Détection par le nom du périphérique
    if "nvme" in device.lower():
        return DiskType.NVME

    # Détection par les données JSON
    if json_data:
        if "nvme_smart_health_information_log" in json_data:
            return DiskType.NVME
        if "ata_smart_attributes" in json_data:
            return DiskType.SATA_ATA

    return DiskType.UNKNOWN


def _parse_ata_attributes(ata_table: list[dict[str, Any]]) -> list[SmartAttribute]:
    """Parse les attributs SMART ATA."""
    return [
        SmartAttribute(
            id=row.get("id", ""),
            name=row.get("name", ""),
            value=row.get("value", ""),
            worst=row.get("worst", ""),
            thresh=row.get("thresh", ""),
            raw=row.get("raw", ""),
        )
        for row in ata_table
    ]  # PERF401: list comprehension


def _parse_nvme_attributes(nvme_log: dict[str, Any]) -> list[SmartAttribute]:
    """Parse les attributs SMART NVMe."""
    attributes = []
    for key, val in nvme_log.items():
        attributes.append(
            SmartAttribute(
                id="-",
                name=key,
                value=val,
                worst="",  # Non applicable pour NVMe
                thresh="",  # Non applicable pour NVMe
                raw=val,
            )
        )
    return attributes


def _determine_health_from_json(json_data: dict[str, Any]) -> str:
    """Détermine l'état de santé depuis les données JSON."""
    smart_status = json_data.get("smart_status")
    if smart_status and "passed" in smart_status:
        return "PASSED" if smart_status["passed"] else "FAILED"
    return "UNKNOWN"


def _determine_health_from_raw(raw_data: str | None) -> str:
    """Détermine l'état de santé depuis les données brutes."""
    if not raw_data:
        return "UNKNOWN"

    raw_upper = raw_data.upper()
    if "PASSED" in raw_upper or "OK" in raw_upper:
        return "PASSED"
    if "FAILED" in raw_upper:
        return "FAILED"
    return "UNKNOWN"


def synthesize_report(device: str, smart_payload: SmartPayload) -> SmartReport:
    """Synthétise un rapport SMART complet."""
    json_data = smart_payload.get("json")
    raw_data = smart_payload.get("raw")

    # Détection du type de disque
    disk_type = _detect_disk_type(device, json_data)

    # Détermination de l'état de santé
    if json_data:
        health = _determine_health_from_json(json_data)
    else:
        health = _determine_health_from_raw(raw_data)

    # Parse des attributs selon le type de disque
    attributes = []
    if json_data:
        if disk_type == DiskType.NVME:
            # Pour NVMe, seules les données de santé sont pertinentes
            nvme_log = json_data.get("nvme_smart_health_information_log", {})
            attributes.extend(_parse_nvme_attributes(nvme_log))
        elif disk_type == DiskType.SATA_ATA:
            # Pour SATA/ATA, utiliser les attributs traditionnels
            ata_table = json_data.get("ata_smart_attributes", {}).get("table", [])
            attributes.extend(_parse_ata_attributes(ata_table))

    return SmartReport(
        device=device,
        health=health,
        disk_type=disk_type,
        attributes=attributes,
        raw=raw_data,
        json_data=json_data,
    )


async def run_smart_check(device: str) -> SmartReport:
    """Effectue une vérification SMART complète d'un p��riphérique."""
    smart_payload = await query_smart_json(device)
    return synthesize_report(device, smart_payload)
