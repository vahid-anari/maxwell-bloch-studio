"""Tests for the temporary adiabatic (rate-equation) solver switch, ``"solve.adiabatic"``."""

import json
import math
from pathlib import Path

import numpy as np
import pytest

import mbstudio
from mbstudio.app.solver_adapter import solve_maxwell_bloch
from mbstudio.io.legacy_keys import migrate_legacy_params

pytest.importorskip("mbsolver.two_level", reason="mbsolver missing")
from mbsolver import two_level  # noqa: E402

pytestmark = pytest.mark.skipif(not hasattr(two_level, "solve_1d_adiabatic"),
                                reason="needs mbsolver from the adiabatic branch")

PLAIN = Path(__file__).parent / "data" / "params_plain.json"


def _small_params(**changes):
    params = mbstudio.ParamsFile(PLAIN).params()
    params.update({"solve.grid.nt": 400, "solve.grid.nz": 40, "solve.t2": 0.05})
    params.update(changes)
    return params


def test_old_files_get_the_full_solver():
    params = json.loads(PLAIN.read_text())["params"]
    assert "solve.adiabatic" not in params
    assert migrate_legacy_params(params)["solve.adiabatic"] is False
    assert mbstudio.ParamsFile(PLAIN).params()["solve.adiabatic"] is False


def test_switch_selects_the_solver():
    full = solve_maxwell_bloch(_small_params(**{"solve.adiabatic": False}))
    adiabatic = solve_maxwell_bloch(_small_params(**{"solve.adiabatic": True}))
    assert set(full) == set(adiabatic)
    assert full["w"].shape == adiabatic["w"].shape
    assert not np.array_equal(full["w"], adiabatic["w"])
    np.testing.assert_array_equal(full["time"], adiabatic["time"])


def test_off_is_unchanged():
    params = _small_params()
    params.pop("solve.adiabatic", None)
    default = solve_maxwell_bloch(params)
    off = solve_maxwell_bloch(_small_params(**{"solve.adiabatic": False}))
    for key in default:
        np.testing.assert_array_equal(default[key], off[key])


def test_infinite_t2_is_refused():
    with pytest.raises(ValueError, match="t2 must be finite"):
        solve_maxwell_bloch(_small_params(**{"solve.adiabatic": True, "solve.t2": math.inf}))


def test_worker_reports_the_refusal():
    from mbstudio.app.solver_controller import SolverWorker

    worker = SolverWorker(_small_params(**{"solve.adiabatic": True, "solve.t2": math.inf}))
    finished, failed = [], []
    worker.finished.connect(finished.append)
    worker.failed.connect(failed.append)
    worker.run()
    assert finished == []
    assert len(failed) == 1 and "t2 must be finite" in failed[0]
