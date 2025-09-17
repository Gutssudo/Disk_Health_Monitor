"""Tests unitaires pour le module report_manager."""

import csv
import json
import tempfile
from pathlib import Path

import pytest

from disk_health.dh_types import DiskType, SmartAttribute, SmartReport
from disk_health.report_manager import ReportManager


def test_should_save_json_file_when_given_valid_report() -> None:
    # Given
    manager = ReportManager()
    sample_report = SmartReport(
        device="/dev/nvme0n1",
        health="PASSED",
        disk_type=DiskType.NVME,
        attributes=[
            SmartAttribute(
                id="-", name="critical_warning", value=0, worst="", thresh="", raw=0
            ),
            SmartAttribute(
                id="-", name="temperature", value=33, worst="", thresh="", raw=33
            ),
        ],
        raw="raw smart output",
        json_data={"smart_status": {"passed": True}},
    )

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        filepath = f.name

    try:
        # When
        manager.save_json(sample_report, filepath)

        # Then
        with open(filepath, encoding="utf-8") as f:
            saved_data = json.load(f)

        assert saved_data["device"] == "/dev/nvme0n1"
        assert saved_data["health"] == "PASSED"
        assert saved_data["disk_type"] == "nvme"
        assert len(saved_data["attributes"]) == 2
        assert saved_data["attributes"][0]["name"] == "critical_warning"
        assert saved_data["raw"] == "raw smart output"
    finally:
        Path(filepath).unlink(missing_ok=True)


def test_should_handle_none_values_when_saving_json() -> None:
    # Given
    manager = ReportManager()
    report_with_none = SmartReport(
        device="/dev/sda",
        health="UNKNOWN",
        disk_type=DiskType.UNKNOWN,
        attributes=[],
        raw=None,
        json_data=None,
    )

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        filepath = f.name

    try:
        # When
        manager.save_json(report_with_none, filepath)

        # Then
        with open(filepath, encoding="utf-8") as f:
            saved_data = json.load(f)

        assert saved_data["raw"] is None
        assert saved_data["json_data"] is None
        assert saved_data["attributes"] == []
    finally:
        Path(filepath).unlink(missing_ok=True)


def test_should_save_nvme_csv_when_given_nvme_report() -> None:
    # Given
    manager = ReportManager()
    nvme_report = SmartReport(
        device="/dev/nvme0n1",
        health="PASSED",
        disk_type=DiskType.NVME,
        attributes=[
            SmartAttribute(
                id="-", name="critical_warning", value=0, worst="", thresh="", raw=0
            ),
            SmartAttribute(
                id="-", name="temperature", value=33, worst="", thresh="", raw=33
            ),
        ],
        raw="raw smart output",
        json_data={"smart_status": {"passed": True}},
    )

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        filepath = f.name

    try:
        # When
        manager.save_csv(nvme_report, filepath)

        # Then
        with open(filepath, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[0] == ["Device", "Health", "Type"]
        assert rows[1] == ["/dev/nvme0n1", "PASSED", "nvme"]
        assert rows[2] == []  # Empty line
        assert rows[3] == ["Name", "Value", "Raw"]  # NVMe headers
        assert rows[4] == ["critical_warning", "0", "0"]
        assert rows[5] == ["temperature", "33", "33"]
    finally:
        Path(filepath).unlink(missing_ok=True)


def test_should_save_sata_csv_when_given_sata_report() -> None:
    # Given
    manager = ReportManager()
    sata_report = SmartReport(
        device="/dev/sda",
        health="PASSED",
        disk_type=DiskType.SATA_ATA,
        attributes=[
            SmartAttribute(
                id=5,
                name="Reallocated_Sector_Ct",
                value=100,
                worst=100,
                thresh=36,
                raw=0,
            )
        ],
        raw="raw output",
        json_data={"smart_status": {"passed": True}},
    )

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        filepath = f.name

    try:
        # When
        manager.save_csv(sata_report, filepath)

        # Then
        with open(filepath, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[0] == ["Device", "Health", "Type"]
        assert rows[1] == ["/dev/sda", "PASSED", "sata_ata"]
        assert rows[3] == [
            "ID",
            "Name",
            "Value",
            "Worst",
            "Thresh",
            "Raw",
        ]  # SATA headers
        assert rows[4] == ["5", "Reallocated_Sector_Ct", "100", "100", "36", "0"]
    finally:
        Path(filepath).unlink(missing_ok=True)


@pytest.mark.parametrize(
    "device,expected_json,expected_csv",
    [
        # Given / When / Then structure for parametrized tests
        ("/dev/sda", "smart_report__dev_sda.json", "smart_report__dev_sda.csv"),
        (
            "/dev/nvme0n1",
            "smart_report__dev_nvme0n1.json",
            "smart_report__dev_nvme0n1.csv",
        ),
        (
            "/dev/disk with spaces",
            "smart_report__dev_disk_with_spaces.json",
            "smart_report__dev_disk_with_spaces.csv",
        ),
    ],
)
def test_should_generate_safe_filenames_when_given_device_paths(
    device: str, expected_json: str, expected_csv: str
) -> None:
    # Given
    manager = ReportManager()

    # When
    json_filename = manager.get_default_json_filename(device)
    csv_filename = manager.get_default_csv_filename(device)

    # Then
    assert json_filename == expected_json
    assert csv_filename == expected_csv


def test_should_sanitize_special_characters_when_generating_filenames() -> None:
    # Given
    manager = ReportManager()
    device = "/dev/weird:device|name*with?chars"

    # When
    json_filename = manager.get_default_json_filename(device)
    csv_filename = manager.get_default_csv_filename(device)

    # Then
    assert "/" not in json_filename
    assert "/" not in csv_filename
    assert " " not in json_filename
    assert " " not in csv_filename
