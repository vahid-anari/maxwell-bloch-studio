"""Tests for the coherence R: solver results, old parameter files and the right-axis choice."""

import json
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

import mbstudio
from mbstudio.app.settings_manager import RIGHT_PLOT_KEY, Settings
from mbstudio.app.solver_adapter import solve_maxwell_bloch
from mbstudio.io.legacy_keys import migrate_legacy_config, migrate_legacy_params

PLAIN = Path(__file__).parent / "data" / "params_plain.json"


def _small_params(**changes):
    params = mbstudio.ParamsFile(PLAIN).params()
    params.update({"solve.grid.nt": 400, "solve.grid.nz": 40, "solve.t2": 0.05})
    params.update(changes)
    return params


@pytest.mark.parametrize("adiabatic", [False, True])
def test_both_solvers_return_R(adiabatic):
    res = solve_maxwell_bloch(_small_params(**{"solve.adiabatic": adiabatic}))
    assert res["R"].shape == res["w"].shape == res["intensity"].shape


def test_old_files_get_an_R_range():
    file = json.loads(PLAIN.read_text())
    assert "display.range.R" not in file["params"]
    assert migrate_legacy_params(file["params"])["display.range.R"]["use_margins"] is True
    assert migrate_legacy_config(file["config"])["display.range.R"] == {}


def _settings(tmp_path, **values):
    settings = Settings.__new__(Settings)
    settings._settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    for key, value in values.items():
        settings._settings.setValue(key, value)
    return settings


def test_right_plot_follows_the_old_w_check_box(tmp_path):
    assert _settings(tmp_path / "a").get_right_plot() == "w"
    assert _settings(tmp_path / "b", **{"view/show_w": True}).get_right_plot() == "w"
    assert _settings(tmp_path / "c", **{"view/show_w": False}).get_right_plot() is None


def test_right_plot_is_remembered(tmp_path):
    settings = _settings(tmp_path, **{"view/show_w": False})
    for choice in ("R", "w", None):
        settings.set_right_plot(choice)
        assert settings.get_right_plot() == choice
    assert settings._settings.value(RIGHT_PLOT_KEY) == "none"
