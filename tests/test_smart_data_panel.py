"""Tests unitaires pour le module smart_data_panel."""

import pytest
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QVBoxLayout, QWidget

from disk_health.dh_types import DiskType, SmartAttribute, SmartReport
from disk_health.ui.smart_data_panel import SmartDataPanel


@pytest.fixture
def app() -> QApplication:
    """Fixture pour l'application Qt."""
    app_instance = QApplication.instance() or QApplication([])
    assert isinstance(app_instance, QApplication)
    return app_instance


@pytest.fixture
def parent_widget(app: QApplication) -> QWidget:
    """Fixture pour le widget parent."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    return widget


@pytest.fixture
def smart_panel(parent_widget: QWidget) -> SmartDataPanel:
    """Fixture pour SmartDataPanel."""
    layout = parent_widget.layout()
    assert isinstance(layout, QVBoxLayout)
    return SmartDataPanel(layout)


def test_should_initialize_components_when_creating_panel(
    smart_panel: SmartDataPanel,
) -> None:
    # Given / When (panel created in fixture)

    # Then
    assert smart_panel.table is not None
    assert smart_panel.csv_btn is not None
    assert smart_panel.raw_text is not None
    assert smart_panel.save_btn is not None
    assert smart_panel.current_disk_type is None


def test_should_set_default_headers_when_panel_initialized(
    smart_panel: SmartDataPanel,
) -> None:
    # Given / When (panel created in fixture)

    # Then
    assert smart_panel.table.columnCount() == 7
    expected_headers = ["ID", "Nom", "Valeur", "Worst", "Seuil", "Raw", "Indicateur"]
    for i, header in enumerate(expected_headers):
        header_item = smart_panel.table.horizontalHeaderItem(i)
        assert isinstance(header_item, QTableWidgetItem)
        assert header_item.text() == header


def test_should_return_nvme_headers_when_getting_headers_for_nvme_disk() -> None:
    # Given
    panel = SmartDataPanel.__new__(SmartDataPanel)  # Create without __init__
    disk_type = DiskType.NVME

    # When
    headers = panel._get_headers_for_disk_type(disk_type)

    # Then
    expected_headers = ["Nom", "Valeur", "Raw", "Indicateur"]
    assert headers == expected_headers


def test_should_return_sata_headers_when_getting_headers_for_sata_disk() -> None:
    # Given
    panel = SmartDataPanel.__new__(SmartDataPanel)  # Create without __init__
    disk_type = DiskType.SATA_ATA

    # When
    headers = panel._get_headers_for_disk_type(disk_type)

    # Then
    expected_headers = ["ID", "Nom", "Valeur", "Worst", "Seuil", "Raw", "Indicateur"]
    assert headers == expected_headers


def test_should_configure_table_for_nvme_when_given_nvme_report(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
    nvme_report = SmartReport(
        device="/dev/nvme0n1",
        health="PASSED",
        disk_type=DiskType.NVME,
        attributes=[
            SmartAttribute(
                id="-", name="temperature", value=33, worst="", thresh="", raw=33
            )
        ],
        raw="raw data",
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(nvme_report)

    # Then
    assert smart_panel.table.columnCount() == 4  # NVMe has 4 columns
    assert smart_panel.current_disk_type == DiskType.NVME


def test_should_configure_table_for_sata_when_given_sata_report(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
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
        raw="raw data",
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(sata_report)

    # Then
    assert smart_panel.table.columnCount() == 7  # SATA has 7 columns
    assert smart_panel.current_disk_type == DiskType.SATA_ATA


def test_should_populate_nvme_table_when_displaying_nvme_report(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
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
        raw="raw data",
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(nvme_report)

    # Then
    assert smart_panel.table.rowCount() == 2

    # Vérifier la première ligne
    item_0_0 = smart_panel.table.item(0, 0)
    assert isinstance(item_0_0, QTableWidgetItem)
    assert item_0_0.text() == "critical_warning"

    item_0_1 = smart_panel.table.item(0, 1)
    assert isinstance(item_0_1, QTableWidgetItem)
    assert item_0_1.text() == "0"

    # Vérifier la deuxième ligne
    item_1_0 = smart_panel.table.item(1, 0)
    assert isinstance(item_1_0, QTableWidgetItem)
    assert item_1_0.text() == "temperature"

    item_1_1 = smart_panel.table.item(1, 1)
    assert isinstance(item_1_1, QTableWidgetItem)
    assert item_1_1.text() == "33"


def test_should_populate_sata_table_when_displaying_sata_report(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
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
        raw="raw data",
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(sata_report)

    # Then
    assert smart_panel.table.rowCount() == 1

    # Vérifier chaque cellule avec isinstance
    item_0_0 = smart_panel.table.item(0, 0)
    assert isinstance(item_0_0, QTableWidgetItem)
    assert item_0_0.text() == "5"

    item_0_1 = smart_panel.table.item(0, 1)
    assert isinstance(item_0_1, QTableWidgetItem)
    assert item_0_1.text() == "Reallocated_Sector_Ct"

    item_0_2 = smart_panel.table.item(0, 2)
    assert isinstance(item_0_2, QTableWidgetItem)
    assert item_0_2.text() == "100"


@pytest.mark.parametrize(
    "attribute_name,attribute_value,expected_indicator",
    [
        ("critical_warning", 0, "✅"),
        ("critical_warning", 1, "⚠️"),
        ("available_spare", 100, "✅"),
        ("available_spare", 5, "⚠️"),
        ("percentage_used", 50, "✅"),
        ("percentage_used", 85, "⚠️"),
        ("media_errors", 0, "✅"),
        ("media_errors", 1, "⚠️"),
        ("temperature", 45, "✅"),
    ],
)
def test_should_return_correct_nvme_health_indicator_when_evaluating_attributes(
    attribute_name: str, attribute_value: int, expected_indicator: str
) -> None:
    # Given
    panel = SmartDataPanel.__new__(SmartDataPanel)  # Create without __init__
    panel.current_disk_type = DiskType.NVME
    attribute = SmartAttribute(
        id="-",
        name=attribute_name,
        value=attribute_value,
        worst="",
        thresh="",
        raw=attribute_value,
    )

    # When
    indicator = panel._get_health_indicator(attribute)

    # Then
    assert indicator == expected_indicator


def test_should_return_warning_indicator_when_sata_value_below_threshold() -> None:
    # Given
    panel = SmartDataPanel.__new__(SmartDataPanel)  # Create without __init__
    panel.current_disk_type = DiskType.SATA_ATA
    attribute = SmartAttribute(id=5, name="Test", value=35, worst=35, thresh=36, raw=0)

    # When
    indicator = panel._get_health_indicator(attribute)

    # Then
    assert indicator == "⚠️"


def test_should_return_ok_indicator_when_sata_value_above_threshold() -> None:
    # Given
    panel = SmartDataPanel.__new__(SmartDataPanel)  # Create without __init__
    panel.current_disk_type = DiskType.SATA_ATA
    attribute = SmartAttribute(
        id=5, name="Test", value=100, worst=100, thresh=36, raw=0
    )

    # When
    indicator = panel._get_health_indicator(attribute)

    # Then
    assert indicator == "✅"


def test_should_display_raw_data_when_report_has_raw_content(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
    raw_content = "SMART Health Status: OK"
    report = SmartReport(
        device="/dev/sda",
        health="PASSED",
        disk_type=DiskType.SATA_ATA,
        attributes=[],
        raw=raw_content,
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(report)

    # Then
    assert smart_panel.raw_text.toPlainText() == raw_content


def test_should_display_no_data_message_when_report_has_no_raw_content(
    smart_panel: SmartDataPanel,
) -> None:
    # Given
    report = SmartReport(
        device="/dev/sda",
        health="PASSED",
        disk_type=DiskType.SATA_ATA,
        attributes=[],
        raw=None,
        json_data=None,
    )

    # When
    smart_panel.display_smart_report(report)

    # Then
    assert smart_panel.raw_text.toPlainText() == "Aucune donnée brute disponible"
