"""Tests unitaires pour le module workers."""

import asyncio
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from disk_health.workers import AsyncWorker


@pytest.fixture
def app() -> QApplication:
    """Fixture pour l'application Qt."""
    app_instance = QApplication.instance() or QApplication([])
    assert isinstance(app_instance, QApplication)
    return app_instance


def test_should_initialize_worker_when_given_coroutine(app: QApplication) -> None:
    # Given
    async def dummy_coroutine() -> str:
        return "test_result"

    # When
    worker = AsyncWorker(dummy_coroutine())

    # Then
    assert worker.coroutine is not None


def test_should_emit_result_when_coroutine_completes_successfully(
    app: QApplication,
) -> None:
    # Given
    expected_result = "test_result"

    async def dummy_coroutine() -> str:
        return expected_result

    worker = AsyncWorker(dummy_coroutine())
    result_received: str | None = None

    def capture_result(result: str) -> None:
        nonlocal result_received
        result_received = result

    worker.finished.connect(capture_result)

    # When
    worker.run()

    # Then
    assert result_received == expected_result


def test_should_handle_async_operations_when_coroutine_has_delay(
    app: QApplication,
) -> None:
    # Given
    expected_result = 42

    async def delayed_coroutine() -> int:
        await asyncio.sleep(0.01)  # Small delay
        return expected_result

    worker = AsyncWorker(delayed_coroutine())
    result_received: int | None = None

    def capture_result(result: int) -> None:
        nonlocal result_received
        result_received = result

    worker.finished.connect(capture_result)

    # When
    worker.run()

    # Then
    assert result_received == expected_result


def test_should_propagate_exception_when_coroutine_raises_error(
    app: QApplication,
) -> None:
    # Given
    async def failing_coroutine() -> None:
        raise ValueError("Test error")

    worker = AsyncWorker(failing_coroutine())
    exception_raised = False

    # When / Then
    try:
        worker.run()
    except ValueError:
        exception_raised = True

    assert exception_raised


def test_should_handle_none_result_when_coroutine_returns_none(
    app: QApplication,
) -> None:
    # Given
    async def none_coroutine() -> None:
        return None

    worker = AsyncWorker(none_coroutine())
    result_received: Any = "not_set"

    def capture_result(result: None) -> None:
        nonlocal result_received
        result_received = result

    worker.finished.connect(capture_result)

    # When
    worker.run()

    # Then
    assert result_received is None


def test_should_handle_complex_data_when_coroutine_returns_dict(
    app: QApplication,
) -> None:
    # Given
    expected_data = {"key": "value", "number": 123, "nested": {"inner": "data"}}

    async def complex_coroutine() -> dict[str, Any]:
        return expected_data

    worker = AsyncWorker(complex_coroutine())
    result_received: dict[str, Any] | None = None

    def capture_result(result: dict[str, Any]) -> None:
        nonlocal result_received
        result_received = result

    worker.finished.connect(capture_result)

    # When
    worker.run()

    # Then
    assert result_received == expected_data
    assert isinstance(result_received, dict)
    assert result_received["key"] == "value"
    assert result_received["nested"]["inner"] == "data"
