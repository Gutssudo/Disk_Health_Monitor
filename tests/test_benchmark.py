"""Tests unitaires pour le module benchmark."""

import pytest

from disk_health.benchmark import (
    _calculate_position_percentage,
    _calculate_read_speed,
    compute_benchmark_stats,
)


def test_should_calculate_correct_speed_when_given_valid_parameters() -> None:
    # Given
    data_size = 4 * 1024 * 1024  # 4MB
    elapsed_time = 1.0  # 1 second
    expected_speed = 4.0  # 4 MB/s

    # When
    speed = _calculate_read_speed(data_size, elapsed_time)

    # Then
    assert speed == expected_speed


def test_should_return_zero_when_elapsed_time_is_zero() -> None:
    # Given
    data_size = 4 * 1024 * 1024
    elapsed_time = 0.0

    # When
    speed = _calculate_read_speed(data_size, elapsed_time)

    # Then
    assert speed == 0.0


def test_should_return_zero_when_elapsed_time_is_negative() -> None:
    # Given
    data_size = 4 * 1024 * 1024
    elapsed_time = -1.0

    # When
    speed = _calculate_read_speed(data_size, elapsed_time)

    # Then
    assert speed == 0.0


@pytest.mark.parametrize(
    "data_size,elapsed_time,expected_speed",
    [
        # Given / When / Then structure for parametrized tests
        (1024 * 1024, 0.5, 2.0),  # 1MB in 0.5s = 2 MB/s
        (2 * 1024 * 1024, 0.25, 8.0),  # 2MB in 0.25s = 8 MB/s
        (8 * 1024 * 1024, 2.0, 4.0),  # 8MB in 2s = 4 MB/s
    ],
)
def test_should_calculate_speed_correctly_when_given_various_inputs(
    data_size: int, elapsed_time: float, expected_speed: float
) -> None:
    # Given (in parametrize)
    # When
    speed = _calculate_read_speed(data_size, elapsed_time)

    # Then
    assert speed == expected_speed


def test_should_calculate_correct_percentage_when_given_valid_parameters() -> None:
    # Given
    position = 500
    total_size = 1000
    expected_percentage = 50.0

    # When
    percentage = _calculate_position_percentage(position, total_size)

    # Then
    assert percentage == expected_percentage


def test_should_return_zero_when_total_size_is_zero() -> None:
    # Given
    position = 100
    total_size = 0

    # When
    percentage = _calculate_position_percentage(position, total_size)

    # Then
    assert percentage == 0.0


def test_should_return_zero_when_total_size_is_negative() -> None:
    # Given
    position = 100
    total_size = -1000

    # When
    percentage = _calculate_position_percentage(position, total_size)

    # Then
    assert percentage == 0.0


@pytest.mark.parametrize(
    "position,total_size,expected_percentage",
    [
        # Given / When / Then structure for parametrized tests
        (0, 1000, 0.0),
        (250, 1000, 25.0),
        (750, 1000, 75.0),
        (1000, 1000, 100.0),
        (1500, 1000, 150.0),  # Position can exceed total
    ],
)
def test_should_calculate_percentage_correctly_when_given_various_inputs(
    position: int, total_size: int, expected_percentage: float
) -> None:
    # Given (in parametrize)
    # When
    percentage = _calculate_position_percentage(position, total_size)

    # Then
    assert percentage == expected_percentage


def test_should_compute_stats_when_given_valid_data() -> None:
    # Given
    read_speeds = [100.0, 95.0, 105.0, 90.0, 110.0]
    access_times = [1.0, 1.2, 0.8, 1.5, 0.9]
    positions = [0.0, 25.0, 50.0, 75.0, 100.0]

    # When
    results = compute_benchmark_stats(read_speeds, access_times, positions)

    # Then
    assert results.read_speeds == read_speeds
    assert results.access_times == access_times
    assert results.positions == positions
    assert results.avg_read_speed == 100.0  # Mean of read_speeds
    assert results.min_read_speed == 90.0
    assert results.max_read_speed == 110.0
    assert results.avg_access_time == 1.08  # Mean of access_times
    assert results.min_access_time == 0.8
    assert results.max_access_time == 1.5


def test_should_return_zero_stats_when_given_empty_lists() -> None:
    # Given
    empty_list: list[float] = []

    # When
    results = compute_benchmark_stats(empty_list, empty_list, empty_list)

    # Then
    assert results.read_speeds == []
    assert results.access_times == []
    assert results.positions == []
    assert results.avg_read_speed == 0.0
    assert results.min_read_speed == 0.0
    assert results.max_read_speed == 0.0
    assert results.avg_access_time == 0.0
    assert results.min_access_time == 0.0
    assert results.max_access_time == 0.0


def test_should_handle_single_value_lists_when_computing_stats() -> None:
    # Given
    read_speeds = [50.0]
    access_times = [2.0]
    positions = [0.0]

    # When
    results = compute_benchmark_stats(read_speeds, access_times, positions)

    # Then
    assert results.avg_read_speed == 50.0
    assert results.min_read_speed == 50.0
    assert results.max_read_speed == 50.0
    assert results.avg_access_time == 2.0
    assert results.min_access_time == 2.0
    assert results.max_access_time == 2.0


def test_should_handle_mismatched_list_lengths_when_computing_stats() -> None:
    # Given
    read_speeds = [100.0, 95.0]
    access_times = [1.0]  # Different length
    positions = [0.0, 50.0, 100.0]  # Different length

    # When
    results = compute_benchmark_stats(read_speeds, access_times, positions)

    # Then
    assert results.avg_read_speed == 97.5
    assert results.avg_access_time == 1.0
    assert len(results.read_speeds) == 2
    assert len(results.access_times) == 1
    assert len(results.positions) == 3
