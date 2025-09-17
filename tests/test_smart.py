"""Tests unitaires pour le module smart."""
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from disk_health.dh_types import DiskType, SmartReport
from disk_health.smart import (
    _detect_disk_type,
    _determine_health_from_json,
    _determine_health_from_raw,
    _parse_ata_attributes,
    _parse_nvme_attributes,
    run_smart_check,
    synthesize_report,
)


def test_should_detect_nvme_when_device_path_contains_nvme() -> None:
    # Given
    device = "/dev/nvme0n1"
    json_data: dict[str, Any] | None = None

    # When
    disk_type = _detect_disk_type(device, json_data)

    # Then
    assert disk_type == DiskType.NVME


def test_should_detect_nvme_when_json_contains_nvme_data() -> None:
    # Given
    device = "/dev/sda"
    json_data: dict[str, Any] = {"nvme_smart_health_information_log": {"temperature": 35}}

    # When
    disk_type = _detect_disk_type(device, json_data)

    # Then
    assert disk_type == DiskType.NVME


def test_should_detect_sata_ata_when_json_contains_ata_data() -> None:
    # Given
    device = "/dev/sda"
    json_data: dict[str, Any] = {"ata_smart_attributes": {"table": []}}

    # When
    disk_type = _detect_disk_type(device, json_data)

    # Then
    assert disk_type == DiskType.SATA_ATA


def test_should_detect_unknown_when_no_identifying_data() -> None:
    # Given
    device = "/dev/sda"
    json_data: dict[str, Any] = {"some_other_data": "value"}

    # When
    disk_type = _detect_disk_type(device, json_data)

    # Then
    assert disk_type == DiskType.UNKNOWN


def test_should_parse_ata_attributes_when_given_valid_table() -> None:
    # Given
    ata_table = [
        {
            "id": 5,
            "name": "Reallocated_Sector_Ct",
            "value": 100,
            "worst": 100,
            "thresh": 36,
            "raw": 0,
        },
        {
            "id": 9,
            "name": "Power_On_Hours",
            "value": 99,
            "worst": 99,
            "thresh": 0,
            "raw": 1234,
        },
    ]

    # When
    attributes = _parse_ata_attributes(ata_table)

    # Then
    assert len(attributes) == 2
    assert attributes[0].id == 5
    assert attributes[0].name == "Reallocated_Sector_Ct"
    assert attributes[0].value == 100
    assert attributes[1].id == 9
    assert attributes[1].name == "Power_On_Hours"


def test_should_handle_missing_fields_when_ata_data_incomplete() -> None:
    # Given
    ata_table = [{"id": 5, "name": "Test"}]  # Missing other fields

    # When
    attributes = _parse_ata_attributes(ata_table)

    # Then
    assert len(attributes) == 1
    assert attributes[0].id == 5
    assert attributes[0].name == "Test"
    assert attributes[0].value == ""
    assert attributes[0].worst == ""
    assert attributes[0].thresh == ""
    assert attributes[0].raw == ""


def test_should_return_empty_list_when_given_empty_ata_table() -> None:
    # Given
    ata_table: list[dict[str, str]] = []

    # When
    attributes = _parse_ata_attributes(ata_table)

    # Then
    assert attributes == []


def test_should_parse_nvme_attributes_when_given_valid_log() -> None:
    # Given
    nvme_log = {
        "critical_warning": 0,
        "temperature": 33,
        "available_spare": 100,
        "percentage_used": 1,
    }

    # When
    attributes = _parse_nvme_attributes(nvme_log)

    # Then
    assert len(attributes) == 4
    assert all(attr.id == "-" for attr in attributes)
    assert attributes[0].name == "critical_warning"
    assert attributes[0].value == 0
    assert attributes[1].name == "temperature"
    assert attributes[1].value == 33


def test_should_return_empty_list_when_given_empty_nvme_log() -> None:
    # Given
    nvme_log: dict[str, int] = {}

    # When
    attributes = _parse_nvme_attributes(nvme_log)

    # Then
    assert attributes == []


def test_should_return_passed_when_smart_status_passed_is_true() -> None:
    # Given
    json_data: dict[str, Any] = {"smart_status": {"passed": True}}

    # When
    health = _determine_health_from_json(json_data)

    # Then
    assert health == "PASSED"


def test_should_return_failed_when_smart_status_passed_is_false() -> None:
    # Given
    json_data: dict[str, Any] = {"smart_status": {"passed": False}}

    # When
    health = _determine_health_from_json(json_data)

    # Then
    assert health == "FAILED"


def test_should_return_unknown_when_smart_status_missing() -> None:
    # Given
    json_data: dict[str, Any] = {"other_data": "value"}

    # When
    health = _determine_health_from_json(json_data)

    # Then
    assert health == "UNKNOWN"


def test_should_return_unknown_when_passed_field_missing() -> None:
    # Given
    json_data: dict[str, Any] = {"smart_status": {"other_field": "value"}}

    # When
    health = _determine_health_from_json(json_data)

    # Then
    assert health == "UNKNOWN"


@pytest.mark.parametrize(
    "raw_data,expected_health",
    [
        # Given / When / Then structure for parametrized tests
        ("SMART overall-health self-assessment test result: PASSED", "PASSED"),
        ("SMART Health Status: OK", "PASSED"),
        ("some text PASSED other text", "PASSED"),
        ("SMART overall-health self-assessment test result: FAILED", "FAILED"),
        ("some text FAILED other text", "FAILED"),
        ("No SMART support", "UNKNOWN"),
        ("", "UNKNOWN"),
        (None, "UNKNOWN"),
    ],
)
def test_should_determine_health_when_given_raw_data(
    raw_data: str | None, expected_health: str
) -> None:
    # Given (in parametrize)
    # When
    health = _determine_health_from_raw(raw_data)

    # Then
    assert health == expected_health


def test_should_create_nvme_report_when_given_nvme_data() -> None:
    # Given
    device = "/dev/nvme0n1"
    smart_payload = {
        "raw": "raw output",
        "json": {
            "smart_status": {"passed": True},
            "nvme_smart_health_information_log": {
                "critical_warning": 0,
                "temperature": 33,
            },
        },
    }

    # When
    report = synthesize_report(device, smart_payload)

    # Then
    assert report.device == device
    assert report.health == "PASSED"
    assert report.disk_type == DiskType.NVME
    assert len(report.attributes) == 2
    assert report.attributes[0].name == "critical_warning"
    assert report.raw == "raw output"


def test_should_create_sata_report_when_given_ata_data() -> None:
    # Given
    device = "/dev/sda"
    smart_payload = {
        "raw": "raw output",
        "json": {
            "smart_status": {"passed": True},
            "ata_smart_attributes": {
                "table": [
                    {
                        "id": 5,
                        "name": "Reallocated_Sector_Ct",
                        "value": 100,
                        "worst": 100,
                        "thresh": 36,
                        "raw": 0,
                    }
                ]
            },
        },
    }

    # When
    report = synthesize_report(device, smart_payload)

    # Then
    assert report.device == device
    assert report.health == "PASSED"
    assert report.disk_type == DiskType.SATA_ATA
    assert len(report.attributes) == 1
    assert report.attributes[0].id == 5


def test_should_fallback_to_raw_parsing_when_json_data_missing() -> None:
    # Given
    device = "/dev/sda"
    smart_payload = {"raw": "SMART test result: PASSED", "json": None}

    # When
    report = synthesize_report(device, smart_payload)

    # Then
    assert report.device == device
    assert report.health == "PASSED"
    assert report.disk_type == DiskType.UNKNOWN
    assert len(report.attributes) == 0
    assert report.json_data is None


@pytest.mark.asyncio
@patch("disk_health.smart.query_smart_json")
async def test_should_return_synthesized_report_when_smart_check_succeeds(
    mock_query: AsyncMock,
) -> None:
    # Given
    device = "/dev/sda"
    mock_query.return_value = {
        "raw": "SMART test result: PASSED",
        "json": {"smart_status": {"passed": True}},
    }

    # When
    report = await run_smart_check(device)

    # Then
    assert isinstance(report, SmartReport)
    assert report.device == device
    assert report.health == "PASSED"
    mock_query.assert_called_once_with(device)
