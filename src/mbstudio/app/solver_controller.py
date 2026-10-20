"""Solver controller: background worker and thread lifecycle management.

Owns the QThread/SolverWorker pair and the pending-request flag used to prevent
overlapping solves.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

import numpy as np
from shiboken6 import isValid

from PySide6.QtCore import QObject, QThread, Signal

from mbstudio.app.solver_adapter import solve_maxwell_bloch


def same_value(a: Any, b: Any) -> bool:
    """Whether two parameter values are equal, looking inside dicts, lists and numpy arrays.

    A plain ``==`` fails on widget values that hold numpy arrays (the step and pulse
    widgets), because comparing arrays gives an array, not a bool.
    """
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return a.keys() == b.keys() and all(same_value(a[k], b[k]) for k in a)
    if isinstance(a, (np.ndarray, list, tuple)) or isinstance(b, (np.ndarray, list, tuple)):
        try:
            return bool(np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True))
        except TypeError:
            return bool(np.array_equal(np.asarray(a, dtype=object), np.asarray(b, dtype=object)))
    try:
        return bool(a == b) or (a != a and b != b)  # NaN equals NaN here
    except (TypeError, ValueError):
        return False


def changed_solve_values(current: Mapping[str, Any], previous: Mapping[str, Any]) -> dict[str, Any]:
    """Return the solver parameters (``solve.*``) whose value differs from ``previous``.

    Used after a refused solve to put back the values of the last successful solve.

    Args:
        current: Parameter mapping that was refused.
        previous: Parameter mapping of the last successful solve.

    Returns:
        ``{path: previous value}`` for every ``solve.*`` path that changed.
    """
    return {
        path: value
        for path, value in previous.items()
        if path.startswith("solve.") and not same_value(current.get(path), value)
    }


class SolverWorker(QObject):
    """Background worker that runs the Maxwell-Bloch solver off the UI thread."""

    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, params: dict[str, Any]) -> None:
        """Initialize the worker with one immutable parameter snapshot.

        Args:
            params: Parameter mapping passed to the solver when ``run`` is called.
        """
        super().__init__()
        self._params = params

    def run(self) -> None:
        """Execute the solver; emit the result, or the error message if the parameters are rejected."""

        try:
            result = solve_maxwell_bloch(self._params)
        except ValueError as e:
            self.failed.emit(str(e))
            return
        self.finished.emit(result)


class SolverController(QObject):
    """Manage solver thread lifecycle and pending-request queuing.

    This controller owns the ``QThread``/``SolverWorker`` pair used for one
    background solve. It also tracks whether a solve is currently running and
    whether another solve was requested while the current one was still active.

    Inheriting from ``QObject`` ensures that the internal finish handlers are
    proper Qt slots. When the worker emits ``finished`` from the background
    thread, Qt can therefore queue the callbacks onto the main thread via an
    auto-connection, avoiding cross-thread UI and timer errors.
    """

    def __init__(
        self,
        parent: QObject,
        on_finished: Callable[[dict], None],
        get_params: Callable[[], dict[str, Any]],
        on_state_solving: Callable[[], None],
        on_state_ready: Callable[[], None],
        on_failed: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize the solver controller.

        Args:
            parent: QObject parent, typically the main window.
            on_finished: Callback invoked on the main thread with the result
                dictionary after a solve completes.
            get_params: Callable returning the current parameter snapshot to solve.
            on_state_solving: Callback invoked on the main thread when a solve starts.
            on_state_ready: Callback invoked on the main thread when a solve finishes.
            on_failed: Callback invoked on the main thread when the solver rejects the
                parameters, with the message and the ``solve.*`` values of the last
                successful solve that differ from the refused ones (empty if there was
                none); the previous results stay shown.
        """
        super().__init__(parent)
        self._on_finished = on_finished
        self._get_params = get_params
        self._on_state_solving = on_state_solving
        self._on_state_ready = on_state_ready
        self._on_failed = on_failed

        self._is_solving = False
        self._has_pending = False
        self._current_params: dict[str, Any] = {}
        self._last_good_params: dict[str, Any] = {}
        self._thread: QThread | None = None
        self._worker: SolverWorker | None = None
        self._shutting_down = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def is_solving(self) -> bool:
        """Return whether a background solve thread is currently running.

        Returns:
            ``True`` while a solve is running, otherwise ``False``.
        """
        return self._is_solving

    @property
    def current_params(self) -> dict[str, Any]:
        """Return the parameter snapshot used for the most recently started solve.

        Returns:
            Parameter mapping used for the active or most recent solve.
        """
        return self._current_params

    def solve(self) -> None:
        """Start a background solve, or queue one if a solve is already running.

        If a solve is already in progress, this method does not start a second
        thread immediately. Instead, it marks a pending request so that another
        solve begins automatically after the current thread finishes.
        """
        if self._shutting_down:
            return
        if self._is_solving:
            self._has_pending = True
            return

        self._is_solving = True
        self._has_pending = False
        self._current_params = self._get_params()
        self._on_state_solving()

        thread = QThread(self)
        worker = SolverWorker(self._current_params)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._handle_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(self._handle_failed)
        worker.failed.connect(thread.quit)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(self._handle_thread_finished)
        thread.finished.connect(thread.deleteLater)

        # Keep references alive for the duration of the solve.
        self._thread = thread
        self._worker = worker
        thread.start()

    # ------------------------------------------------------------------
    # Private slots
    # ------------------------------------------------------------------

    def _handle_finished(self, result: dict) -> None:
        """Handle solver completion on the main thread.

        Args:
            result: Result dictionary emitted by the worker.
        """
        self._is_solving = False
        self._last_good_params = self._current_params
        self._on_state_ready()
        self._on_finished(result)

    def _handle_failed(self, message: str) -> None:
        """Handle a rejected solve on the main thread.

        Args:
            message: Error message from the solver.
        """
        self._is_solving = False
        self._on_state_ready()
        if self._on_failed is not None and not self._has_pending:
            self._on_failed(message, changed_solve_values(self._current_params, self._last_good_params))

    def _handle_thread_finished(self) -> None:
        """Drop references to the finished thread and start any queued solve."""
        self._thread = None
        self._worker = None
        if self._has_pending and not self._shutting_down:
            self.solve()

    def shutdown(self) -> None:
        """Stop the worker thread, wait for it to finish, and block further solves."""

        self._shutting_down = True
        self._has_pending = False
        thread = self._thread
        if thread is not None and isValid(thread) and thread.isRunning():
            thread.quit()
            thread.wait()
