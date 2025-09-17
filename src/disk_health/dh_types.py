"""Types personnalisés pour le projet disk_health."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DiskType(Enum):
    """Type de disque détecté."""

    NVME = "nvme"
    SATA_ATA = "sata_ata"
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    """Information sur un périphérique de stockage."""

    path: str
    model: str
    size: str


@dataclass
class SmartAttribute:
    """Attribut SMART d'un disque."""

    id: str | int
    name: str
    value: Any
    worst: str | int
    thresh: str | int
    raw: Any


@dataclass
class SmartReport:
    """Rapport SMART complet d'un disque."""

    device: str
    health: str
    disk_type: DiskType
    attributes: list[SmartAttribute]
    raw: str | None
    json_data: dict[str, Any] | None


@dataclass
class BenchmarkResults:
    """Résultats du benchmark de performance."""

    read_speeds: list[float]
    access_times: list[float]
    positions: list[float]
    avg_read_speed: float
    min_read_speed: float
    max_read_speed: float
    avg_access_time: float
    min_access_time: float
    max_access_time: float


SmartPayload = dict[str, Any]
CommandResult = dict[str, Any]
