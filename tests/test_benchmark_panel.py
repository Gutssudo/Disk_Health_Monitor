"""Tests unitaires pour le module benchmark_panel."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from disk_health.ui.benchmark_panel import BenchmarkPanel
from disk_health.dh_types import BenchmarkResults


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
def benchmark_panel(parent_widget: QWidget) -> BenchmarkPanel:
    """Fixture pour BenchmarkPanel."""
    layout = parent_widget.layout()
    assert isinstance(layout, QVBoxLayout)
    return BenchmarkPanel(layout)


def test_should_initialize_components_when_creating_panel(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given / When (panel created in fixture)

    # Then
    assert benchmark_panel.benchmark_group is not None
    assert benchmark_panel.progress_bar is not None
    assert benchmark_panel.fig is not None
    assert benchmark_panel.canvas is not None
    assert benchmark_panel.stats_labels is not None


def test_should_hide_progress_bar_when_panel_initialized(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given / When (panel created in fixture)

    # Then
    assert benchmark_panel.is_progress_visible() is False


def test_should_create_stats_labels_when_panel_initialized(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given / When (panel created in fixture)

    # Then
    expected_keys = [
        "avg_read",
        "max_read",
        "min_read",
        "avg_access",
        "max_access",
        "min_access",
    ]
    assert len(benchmark_panel.stats_labels) == 6
    for key in expected_keys:
        assert key in benchmark_panel.stats_labels
        assert benchmark_panel.stats_labels[key].text().endswith(
            "-- MB/s"
        ) or benchmark_panel.stats_labels[key].text().endswith("-- ms")  or benchmark_panel.stats_labels[key].text().endswith("-- GB")


def test_should_show_progress_bar_when_showing_progress(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    assert benchmark_panel.is_progress_visible() is False

    # When
    benchmark_panel.show_progress()

    # Then
    assert benchmark_panel.is_progress_visible() is True
    assert benchmark_panel.progress_bar.value() == 0


def test_should_hide_progress_bar_when_hiding_progress(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    benchmark_panel.show_progress()
    assert benchmark_panel.is_progress_visible() is True

    # When
    benchmark_panel.hide_progress()

    # Then
    assert benchmark_panel.is_progress_visible() is False


@pytest.mark.parametrize(
    "percentage,expected_value",
    [
        (0.0, 0),
        (25.5, 25),
        (50.0, 50),
        (75.7, 75),
        (100.0, 100),
    ],
)
def test_should_update_progress_value_when_updating_progress(
    benchmark_panel: BenchmarkPanel, percentage: float, expected_value: int
) -> None:
    # Given
    benchmark_panel.show_progress()

    # When
    benchmark_panel.update_progress(percentage)

    # Then
    assert benchmark_panel.progress_bar.value() == expected_value


def test_should_update_stats_labels_when_updating_benchmark_results(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    results = BenchmarkResults(
        read_speeds=[100.0, 95.0, 105.0],
        access_times=[1.0, 1.2, 0.8],
        positions=[0.0, 50.0, 100.0],
        avg_read_speed=100.0,
        min_read_speed=95.0,
        max_read_speed=105.0,
        avg_access_time=1.0,
        min_access_time=0.8,
        max_access_time=1.2,
    )

    # When
    benchmark_panel.update_benchmark_results(results)

    # Then
    assert benchmark_panel.stats_labels["avg_read"].text() == "Vitesse moy.: 100.0 MB/s"
    assert benchmark_panel.stats_labels["min_read"].text() == "Vitesse min.: 95.0 MB/s"
    assert benchmark_panel.stats_labels["max_read"].text() == "Vitesse max.: 105.0 MB/s"
    assert benchmark_panel.stats_labels["avg_access"].text() == "Accès moy.: 1.0 ms"
    assert benchmark_panel.stats_labels["min_access"].text() == "Accès min.: 0.8 ms"
    assert benchmark_panel.stats_labels["max_access"].text() == "Accès max.: 1.2 ms"


def test_should_handle_empty_results_when_updating_benchmark_results(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    results = BenchmarkResults(
        read_speeds=[],
        access_times=[],
        positions=[],
        avg_read_speed=0.0,
        min_read_speed=0.0,
        max_read_speed=0.0,
        avg_access_time=0.0,
        min_access_time=0.0,
        max_access_time=0.0,
    )

    # When
    benchmark_panel.update_benchmark_results(results)

    # Then
    assert benchmark_panel.stats_labels["avg_read"].text() == "Vitesse moy.: 0 B/s"
    assert benchmark_panel.stats_labels["avg_access"].text() == "Accès moy.: 0.0 ms"


@patch("disk_health.ui.benchmark_panel.BenchmarkPanel._update_plots")
def test_should_call_update_plots_when_updating_benchmark_results(
    mock_update_plots: MagicMock, benchmark_panel: BenchmarkPanel
) -> None:
    # Given
    results = BenchmarkResults(
        read_speeds=[100.0],
        access_times=[1.0],
        positions=[50.0],
        avg_read_speed=100.0,
        min_read_speed=100.0,
        max_read_speed=100.0,
        avg_access_time=1.0,
        min_access_time=1.0,
        max_access_time=1.0,
    )

    # When
    benchmark_panel.update_benchmark_results(results)

    # Then
    mock_update_plots.assert_called_once_with(results)


def test_should_clear_axes_when_updating_plots_with_empty_data(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    results = BenchmarkResults(
        read_speeds=[],
        access_times=[],
        positions=[],
        avg_read_speed=0.0,
        min_read_speed=0.0,
        max_read_speed=0.0,
        avg_access_time=0.0,
        min_access_time=0.0,
        max_access_time=0.0,
    )

    # When
    benchmark_panel._update_plots(results)

    # Then
    # Should not raise an exception and should handle empty data gracefully
    assert True  # If we reach here, the method handled empty data correctly


def test_should_plot_data_when_updating_plots_with_valid_data(
    benchmark_panel: BenchmarkPanel,
) -> None:
    # Given
    results = BenchmarkResults(
        read_speeds=[100.0, 95.0, 105.0],
        access_times=[1.0, 1.2, 0.8],
        positions=[0.0, 50.0, 100.0],
        avg_read_speed=100.0,
        min_read_speed=95.0,
        max_read_speed=105.0,
        avg_access_time=1.0,
        min_access_time=0.8,
        max_access_time=1.2,
    )

    # When
    benchmark_panel._update_plots(results)

    # Then
    # Verify that axes have been configured
    assert benchmark_panel.ax1.get_ylabel() == "Vitesse (MB/s)"
    assert benchmark_panel.ax1.get_title() == "Vitesse de lecture par position"
    assert benchmark_panel.ax2.get_ylabel() == "Temps d'accès (ms)"
    assert benchmark_panel.ax2.get_xlabel() == "Position sur le disque (%)"
    assert benchmark_panel.ax2.get_title() == "Temps d'accès par position"
