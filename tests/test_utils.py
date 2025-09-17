"""Tests unitaires pour le module utils."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from disk_health.dh_types import DeviceInfo
from disk_health.utils import (
    has_smartctl,
    list_block_devices,
    query_smart_json,
    run_cmd,
)


@pytest.mark.asyncio
async def test_should_return_success_result_when_command_succeeds() -> None:
    # Given
    cmd = ["echo", "test"]

    # When
    result = await run_cmd(cmd)

    # Then
    assert result["returncode"] == 0
    assert "test" in result["stdout"]
    assert result["stderr"] == ""


@pytest.mark.asyncio
async def test_should_return_error_result_when_command_fails() -> None:
    # Given
    cmd = ["false"]  # Command that always fails

    # When
    result = await run_cmd(cmd)

    # Then
    assert result["returncode"] == 1
    assert result["stdout"] == ""


@pytest.mark.asyncio
async def test_should_handle_timeout_when_command_takes_too_long() -> None:
    # Given
    cmd = ["sleep", "20"]  # Plus long que le timeout de 15s intégré

    # When / Then
    with pytest.raises(asyncio.TimeoutError):
        await run_cmd(cmd)


@patch("disk_health.utils.shutil.which")
def test_should_return_true_when_smartctl_is_available(mock_which: MagicMock) -> None:
    # Given
    mock_which.return_value = "/usr/sbin/smartctl"

    # When
    result = has_smartctl()

    # Then
    assert result is True
    mock_which.assert_called_once_with("smartctl")


@patch("disk_health.utils.shutil.which")
def test_should_return_false_when_smartctl_is_not_available(
    mock_which: MagicMock,
) -> None:
    # Given
    mock_which.return_value = None

    # When
    result = has_smartctl()

    # Then
    assert result is False
    mock_which.assert_called_once_with("smartctl")


@pytest.mark.asyncio
@patch("disk_health.utils.run_cmd")
async def test_should_return_devices_when_lsblk_succeeds(
    mock_run_cmd: AsyncMock,
) -> None:
    # Given
    lsblk_output = {
        "blockdevices": [
            {"name": "sda", "model": "Samsung SSD", "type": "disk", "size": "500G"},
            {"name": "nvme0n1", "model": "NVMe SSD", "type": "disk", "size": "1T"},
            {"name": "sr0", "model": "DVD", "type": "rom", "size": "1024M"},
        ]
    }
    mock_run_cmd.return_value = {
        "returncode": 0,
        "stdout": json.dumps(lsblk_output),
        "stderr": "",
    }

    # When
    devices = await list_block_devices()

    # Then
    assert len(devices) == 2  # Only disk type devices
    assert devices[0] == DeviceInfo(path="/dev/sda", model="Samsung SSD", size="500G")
    assert devices[1] == DeviceInfo(path="/dev/nvme0n1", model="NVMe SSD", size="1T")


@pytest.mark.asyncio
@patch("disk_health.utils.run_cmd")
async def test_should_return_empty_list_when_lsblk_fails(
    mock_run_cmd: AsyncMock,
) -> None:
    # Given
    mock_run_cmd.return_value = {
        "returncode": 1,
        "stdout": "",
        "stderr": "lsblk: command not found",
    }

    # When
    devices = await list_block_devices()

    # Then
    assert devices == []


@pytest.mark.asyncio
@patch("disk_health.utils.run_cmd")
async def test_should_handle_invalid_json_when_lsblk_returns_corrupted_data(
    mock_run_cmd: AsyncMock,
) -> None:
    # Given
    mock_run_cmd.return_value = {
        "returncode": 0,
        "stdout": "invalid json",
        "stderr": "",
    }

    # When
    devices = await list_block_devices()

    # Then
    assert devices == []


@pytest.mark.asyncio
@patch("disk_health.utils.run_cmd")
async def test_should_handle_missing_fields_when_device_data_incomplete(
    mock_run_cmd: AsyncMock,
) -> None:
    # Given
    lsblk_output = {
        "blockdevices": [
            {"name": "sda", "type": "disk"},  # Missing model and size
        ]
    }
    mock_run_cmd.return_value = {
        "returncode": 0,
        "stdout": json.dumps(lsblk_output),
        "stderr": "",
    }

    # When
    devices = await list_block_devices()

    # Then
    assert len(devices) == 1
    assert devices[0] == DeviceInfo(path="/dev/sda", model="", size="")


@pytest.mark.asyncio
@patch("disk_health.utils.has_smartctl")
async def test_should_return_error_when_smartctl_not_available(
    mock_has_smartctl: MagicMock,
) -> None:
    # Given
    mock_has_smartctl.return_value = False
    device = "/dev/sda"

    # When / Then
    from disk_health.utils import SmartctlNotFoundError

    with pytest.raises(SmartctlNotFoundError):
        await query_smart_json(device)


@pytest.mark.asyncio
@patch("disk_health.utils.has_smartctl")
@patch("disk_health.utils.run_cmd")
async def test_should_return_parsed_json_when_smartctl_succeeds(
    mock_run_cmd: AsyncMock, mock_has_smartctl: MagicMock
) -> None:
    # Given
    mock_has_smartctl.return_value = True
    device = "/dev/sda"
    smart_data = {"smart_status": {"passed": True}}
    mock_run_cmd.return_value = {
        "returncode": 0,
        "stdout": json.dumps(smart_data),
        "stderr": "",
    }

    # When
    result = await query_smart_json(device)

    # Then
    assert result["raw"] == json.dumps(smart_data)
    assert result["json"] == smart_data
    mock_run_cmd.assert_called_once_with(
        ["smartctl", "-j", "-H", "-A", device]
    )


@pytest.mark.asyncio
@patch("disk_health.utils.has_smartctl")
@patch("disk_health.utils.run_cmd")
async def test_should_handle_invalid_json_when_smartctl_returns_corrupted_data(
    mock_run_cmd: AsyncMock, mock_has_smartctl: MagicMock
) -> None:
    # Given
    mock_has_smartctl.return_value = True
    device = "/dev/sda"
    mock_run_cmd.return_value = {
        "returncode": 0,
        "stdout": "invalid json output",
        "stderr": "",
    }

    # When
    result = await query_smart_json(device)

    # Then
    assert result["raw"] == "invalid json output"
    assert result["json"] is None


@pytest.mark.asyncio
@patch("disk_health.utils.has_smartctl")
@patch("disk_health.utils.run_cmd")
async def test_should_handle_command_failure_when_smartctl_fails(
    mock_run_cmd: AsyncMock, mock_has_smartctl: MagicMock
) -> None:
    # Given
    mock_has_smartctl.return_value = True
    device = "/dev/sda"
    mock_run_cmd.return_value = {
        "returncode": 1,
        "stdout": "SMART command failed",
        "stderr": "Permission denied",
    }

    # When
    result = await query_smart_json(device)

    # Then
    assert result["raw"] == "SMART command failed"
    assert result["json"] is None
