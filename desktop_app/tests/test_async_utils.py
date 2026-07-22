"""Tests for desktop_app/widgets/async_utils.py.

This module holds AsyncRunner/dispatch/run_async, moved here from
extraction_utils.py so desktop_app/pdf/viewer.py can reuse the same
thread-pool dispatch primitive without depending on the views/ package
(a backwards layering dependency for pdf/, which views/ builds on top of).
"""

import time

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from desktop_app.widgets.async_utils import AsyncRunner, dispatch, run_async


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_dispatch_runs_func_and_emits_finished(qapp):
    results = []
    runner = AsyncRunner(lambda: 42)
    runner.finished.connect(results.append)

    dispatch(runner)

    deadline = time.time() + 5.0
    while not results and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)

    assert results == [42]


def test_dispatch_emits_error_on_exception(qapp):
    errors = []

    def boom():
        raise RuntimeError("boom")

    runner = AsyncRunner(boom)
    runner.error.connect(errors.append)

    dispatch(runner)

    deadline = time.time() + 5.0
    while not errors and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)

    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)


def test_run_async_future_reports_result(qapp):
    future = run_async(lambda x, y: x + y, 2, 3)

    deadline = time.time() + 5.0
    while not future.isFinished() and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)

    assert future.isFinished()
    assert future.result() == 5


def test_extraction_utils_reexports_same_objects():
    """Backward-compat re-export must point at the real, shared implementation."""
    from desktop_app.views.main_window_parts import extraction_utils

    assert extraction_utils.AsyncRunner is AsyncRunner
    assert extraction_utils.run_async is run_async
