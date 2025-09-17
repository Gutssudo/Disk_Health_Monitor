"""Utilitaires pour l'exécution de commandes système."""

import asyncio
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from disk_health.dh_types import CommandResult, DeviceInfo

_executor = ThreadPoolExecutor(max_workers=4)


class SmartctlNotFoundError(Exception):
    """Exception levée quand smartctl n'est pas disponible."""

    def __init__(self) -> None:
        message = (
            "smartctl introuvable. "
            "Veuillez installer smartmontools :\n"
            "  - Ubuntu/Debian: sudo apt install smartmontools\n"
            "  - RHEL/CentOS: sudo yum install smartmontools\n"
            "  - Fedora: sudo dnf install smartmontools\n"
            "  - Arch: sudo pacman -S smartmontools\n"
            "Ou exécutez ce programme avec sudo si smartctl est déjà installé."
        )
        super().__init__(message)


def _run_cmd_blocking(
    cmd: list[str], timeout: int = 15
) -> subprocess.CompletedProcess[str]:
    """Exécute une commande de manière synchrone."""
    # S603: subprocess call with shell=False and validated command list
    # Commands are constructed internally with validated arguments, not user input
    return subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,  # UP022
        text=True,
        timeout=timeout,
    )


async def run_cmd(cmd: list[str]) -> CommandResult:
    """Exécute une commande de manière asynchrone."""
    try:
        async with asyncio.timeout(15):
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
    except TimeoutError:
        process.kill()
        await process.communicate()
        raise

    return {
        "returncode": process.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    }


async def list_block_devices() -> list[DeviceInfo]:
    """Liste les périphériques de stockage disponibles."""
    result = await run_cmd(["lsblk", "-J", "-o", "NAME,MODEL,TYPE,SIZE"])
    devices = []

    if result["returncode"] == 0:
        try:
            data = json.loads(result["stdout"])
            devices.extend(
                [
                    DeviceInfo(
                        path=f"/dev/{node['name']}",
                        model=node.get("model", ""),
                        size=node.get("size", ""),
                    )
                    for node in data.get("blockdevices", [])
                    if node.get("type") == "disk"
                ]
            )  # PERF401
        except json.JSONDecodeError:
            pass

    return devices


def has_smartctl() -> bool:
    """Vérifie si smartctl est disponible."""
    return shutil.which("smartctl") is not None


async def query_smart_json(device: str) -> dict[str, Any]:
    """Interroge les données SMART d'un périphérique."""
    if not has_smartctl():
        raise SmartctlNotFoundError

    out = await run_cmd(["smartctl", "-j", "-H", "-A", device])

    if out["returncode"] == 0 and out["stdout"].strip():
        try:
            return {"raw": out["stdout"], "json": json.loads(out["stdout"])}
        except (json.JSONDecodeError, TypeError, ValueError):
            return {"raw": out["stdout"], "json": None}

    return {"raw": out["stdout"], "json": None}


def format_speed(speed_mb_s: float) -> str:
    """Formate une vitesse en MB/s vers l'unité appropriée.

    Args:
        speed_mb_s: Vitesse en MB/s

    Returns:
        Chaîne formatée avec l'unité appropriée
    """
    gb_threshold = 1024  # PLR2004
    kb_threshold = 0.001  # PLR2004
    if speed_mb_s >= gb_threshold:
        return f"{speed_mb_s / gb_threshold:.2f} GB/s"
    if speed_mb_s >= 1:
        return f"{speed_mb_s:.1f} MB/s"
    if speed_mb_s >= kb_threshold:
        return f"{speed_mb_s * 1024:.1f} KB/s"
    # < 1 KB/s
    return f"{speed_mb_s * 1024 * 1024:.0f} B/s"
