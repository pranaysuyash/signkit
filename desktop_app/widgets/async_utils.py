"""Generic Qt background-task helpers shared across the app.

Moved here from desktop_app/views/main_window_parts/extraction_utils.py:
that module is scoped to the extraction tab, but desktop_app/pdf/viewer.py
needs the same run-in-thread-pool primitive for async field detection.
desktop_app/widgets is already a valid shared dependency for both pdf/ and
views/ (pdf/viewer.py already imports ModernMacButton from here), whereas
pdf/ depending on views/main_window_parts/ would be a backwards layering
dependency. extraction_utils.py re-exports these names for compatibility.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class AsyncRunner(QObject):
    """Run a callable in the global thread pool and emit its result."""

    finished = Signal(object)
    error = Signal(Exception)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


def dispatch(runner: AsyncRunner) -> None:
    """Submit an AsyncRunner to the global QThreadPool.

    Callers must keep a reference to `runner` themselves (e.g. as an
    instance attribute) for as long as its signals matter — nothing here
    holds one, so an unreferenced runner can be garbage-collected before
    it emits.
    """
    thread_pool = QThreadPool.globalInstance()
    runnable = QRunnable.create(lambda: runner.run())
    runnable.setAutoDelete(True)
    thread_pool.start(runnable)


def run_async(func, *args, **kwargs):
    """Run *func* in the thread pool and return a future-like object."""

    runner = AsyncRunner(func, *args, **kwargs)

    class Future:
        def __init__(self, runner):
            self.runner = runner
            self._result = None
            self._error = None
            self._finished = False
            runner.finished.connect(self._on_finished)
            runner.error.connect(self._on_error)

        def _on_finished(self, result):
            self._result = result
            self._finished = True

        def _on_error(self, error):
            self._error = error
            self._finished = True

        def result(self):
            if self._error:
                raise self._error
            return self._result

        def isFinished(self):
            return self._finished

    future = Future(runner)
    dispatch(runner)
    return future
