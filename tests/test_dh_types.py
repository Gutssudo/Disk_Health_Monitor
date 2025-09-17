"""Tests unitaires pour le module dh_types."""

from disk_health.dh_types import (
    BenchmarkResults,
    DeviceInfo,
    DiskType,
    SmartAttribute,
    SmartReport,
)


def test_should_have_correct_nvme_value_when_accessing_disk_type_enum() -> None:
    # Given / When
    disk_type = DiskType.NVME

    # Then
    assert disk_type.value == "nvme"


def test_should_have_correct_sata_ata_value_when_accessing_disk_type_enum() -> None:
    # Given / When
    disk_type = DiskType.SATA_ATA

    # Then
    assert disk_type.value == "sata_ata"


def test_should_have_correct_unknown_value_when_accessing_disk_type_enum() -> None:
    # Given / When
    disk_type = DiskType.UNKNOWN

    # Then
    assert disk_type.value == "unknown"


def test_should_create_device_info_when_given_valid_parameters() -> None:
    # Given
    path = "/dev/sda"
    model = "Samsung SSD"
    size = "500GB"

    # When
    device = DeviceInfo(path=path, model=model, size=size)

    # Then
    assert device.path == path
    assert device.model == model
    assert device.size == size


def test_should_handle_empty_model_when_creating_device_info() -> None:
    # Given
    path = "/dev/sda"
    model = ""
    size = "500GB"

    # When
    device = DeviceInfo(path=path, model=model, size=size)

    # Then
    assert device.path == path
    assert device.model == ""
    assert device.size == size


def test_should_create_smart_attribute_when_given_valid_parameters() -> None:
    # Given
    attr_id = 5
    name = "Reallocated_Sector_Ct"
    value = 100
    worst = 100
    thresh = 36
    raw = 0

    # When
    attribute = SmartAttribute(
        id=attr_id, name=name, value=value, worst=worst, thresh=thresh, raw=raw
    )

    # Then
    assert attribute.id == attr_id
    assert attribute.name == name
    assert attribute.value == value
    assert attribute.worst == worst
    assert attribute.thresh == thresh
    assert attribute.raw == raw


def test_should_handle_string_id_when_creating_nvme_attribute() -> None:
    # Given
    attr_id = "-"
    name = "critical_warning"
    value = 0

    # When
    attribute = SmartAttribute(
        id=attr_id, name=name, value=value, worst="", thresh="", raw=value
    )

    # Then
    assert attribute.id == "-"
    assert attribute.name == name
    assert attribute.value == 0


def test_should_create_smart_report_when_given_valid_parameters() -> None:
    # Given
    device = "/dev/sda"
    health = "PASSED"
    disk_type = DiskType.SATA_ATA
    attributes = [
        SmartAttribute(id=5, name="Test", value=100, worst=100, thresh=36, raw=0)
    ]
    raw_data = "raw smart output"
    json_data = {"smart_status": {"passed": True}}

    # When
    report = SmartReport(
        device=device,
        health=health,
        disk_type=disk_type,
        attributes=attributes,
        raw=raw_data,
        json_data=json_data,
    )

    # Then
    assert report.device == device
    assert report.health == health
    assert report.disk_type == disk_type
    assert len(report.attributes) == 1
    assert report.raw == raw_data
    assert report.json_data == json_data


def test_should_handle_none_values_when_creating_smart_report() -> None:
    # Given
    device = "/dev/sda"
    health = "UNKNOWN"
    disk_type = DiskType.UNKNOWN

    # When
    report = SmartReport(
        device=device,
        health=health,
        disk_type=disk_type,
        attributes=[],
        raw=None,
        json_data=None,
    )

    # Then
    assert report.device == device
    assert report.health == health
    assert report.raw is None
    assert report.json_data is None
    assert len(report.attributes) == 0


def test_should_create_benchmark_results_when_given_valid_data() -> None:
    # Given
    read_speeds = [100.5, 95.2, 102.1]
    access_times = [1.2, 1.5, 1.1]
    positions = [0.0, 50.0, 100.0]

    # When
    results = BenchmarkResults(
        read_speeds=read_speeds,
        access_times=access_times,
        positions=positions,
        avg_read_speed=99.3,
        min_read_speed=95.2,
        max_read_speed=102.1,
        avg_access_time=1.27,
        min_access_time=1.1,
        max_access_time=1.5,
    )

    # Then
    assert results.read_speeds == read_speeds
    assert results.access_times == access_times
    assert results.positions == positions
    assert results.avg_read_speed == 99.3
    assert results.min_read_speed == 95.2
    assert results.max_read_speed == 102.1


def test_should_handle_empty_lists_when_creating_benchmark_results() -> None:
    # Given
    empty_list: list[float] = []

    # When
    results = BenchmarkResults(
        read_speeds=empty_list,
        access_times=empty_list,
        positions=empty_list,
        avg_read_speed=0.0,
        min_read_speed=0.0,
        max_read_speed=0.0,
        avg_access_time=0.0,
        min_access_time=0.0,
        max_access_time=0.0,
    )

    # Then
    assert len(results.read_speeds) == 0
    assert len(results.access_times) == 0
    assert len(results.positions) == 0
    assert results.avg_read_speed == 0.0
