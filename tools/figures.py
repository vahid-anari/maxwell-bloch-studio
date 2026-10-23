"""The pictures and animations of the Maxwell Bloch Studio docs (``docs/figures``).

    python tools/figures.py                     # everything
    python tools/figures.py main_window --dark  # main_window_dark.png
    python tools/figures.py --list

Each item starts the app in a fresh process with empty settings (no update
check, no launcher refresh), so your own settings never show. ``fit_mode``
uses a made-up data folder: two velocity components drawn from the model of
``tests/data/params_fit.json`` with noise. How it works: sciwidgets.devtools.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Iterator, Optional

import numpy as np

from sciwidgets.devtools import Gif, Player, Shot, main

ROOT = Path(__file__).resolve().parent.parent
FIT_PARAMS = ROOT / "tests" / "data" / "params_fit.json"


# ------------------------------------------------------------------- starting the app
def _quiet() -> None:
    """No update check and no launcher refresh while the pictures are taken."""
    from sciwidgets.app.update_ui import AppUpdates
    AppUpdates.check = lambda self, *args, **kwargs: None


def studio(open_path: Optional[Path] = None) -> int:
    """Start the app like ``mbstudio`` does, without the splash, optionally opening a path."""
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from mbstudio.app.main_window import MBESolverApp
    from mbstudio.paths import APP_ICON_PATH

    _quiet()
    app = QApplication([])
    app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    app.setApplicationDisplayName("Maxwell Bloch Studio")
    window = MBESolverApp(app)
    window.show()
    if open_path is not None:  # as File → Open Data Folder would, without asking about unsaved changes
        QTimer.singleShot(0, lambda: window._load_data_folder_from_path(Path(open_path)))
    return app.exec()


def demo_folder() -> Path:
    """A data folder with two velocity components made from the model of the test fit file, plus noise."""
    import mbstudio
    folder = Path(tempfile.mkdtemp(prefix="mbstudio-demo-")) / "G000.00+00.00"
    folder.mkdir()
    source = mbstudio.ParamsFile(FIT_PARAMS)
    rng = np.random.default_rng(7)
    for velocity in source.velocities:
        p = source.params(velocity)
        res = mbstudio.solve(p)
        intensity = res["intensity"][p["slice.z"]["index"]]
        t = p["results.offset.time"] + res["time"] * p["solve.sample"]["t0"] / 86400.0
        flux = p["results.scale.intensity"] * intensity / intensity.max()
        t_obs = np.sort(rng.uniform(t[0] + 120.0, t[-1], 150))
        f_obs = np.interp(t_obs, t, flux) + rng.normal(0.0, 0.025, t_obs.size)
        rows = "\n".join(f"{a:.3f} {b:.4f}" for a, b in zip(t_obs, f_obs))
        (folder / f"G000.00+00.00_v={velocity}.txt").write_text(f"# MJD flux(Jy)\n{rows}\n")
    file = json.loads(FIT_PARAMS.read_text())
    file["metadata"]["source"] = "G000.00+00.00"
    for params in file["params"].values():  # show the observed time span (the test file shows 0-2000)
        params["display.range.time"] = {"use_margins": False, "range": [50100.0, 52000.0], "margins": [10, 10]}
    (folder / "G000.00+00.00_params.json").write_text(json.dumps(file, indent=2))
    return folder


def studio_with_data() -> int:
    return studio(demo_folder())


def splash() -> int:
    """The splash screen as the app shows it while starting."""
    from PySide6.QtWidgets import QApplication
    from sciwidgets.splash import SplashScreen

    from mbstudio.config.app_metadata import APP_VERSION
    from mbstudio.paths import APP_IMAGE_PATH

    app = QApplication([])
    base = 35
    screen = SplashScreen(APP_IMAGE_PATH, size=(16 * base, 9 * base), title="Maxwell\nBloch\nStudio",
                          subtitle=f"Version {APP_VERSION}", font_family="Times New Roman")
    screen.show_message("Starting...")
    return app.exec()


# ------------------------------------------------------------------- picture states
def solved(p: Player) -> Iterator[float]:
    """The main window after the first solve."""
    yield from p.wait_until(lambda: p.win._results)
    yield 0.5


def _model_in_data_time(win) -> bool:
    """Whether the plotted model has been solved for the loaded data (its times are those of the data)."""
    x = win._canvas.line("flux").get_xdata()
    return len(x) > 0 and float(min(x)) > 1000.0


def fitting(p: Player) -> Iterator[float]:
    """Fit mode with the made-up data folder loaded and solved."""
    from PySide6.QtWidgets import QApplication
    quiet = 0
    for _ in range(600):  # loading shows a folder summary and "Data Imported": close them as they come
        dialog = QApplication.activeModalWidget()
        if dialog is not None:
            dialog.accept()
            quiet = 0
        elif p.win._fit_mode and _model_in_data_time(p.win):
            quiet += 1
            if quiet >= 10:
                break
        yield 0.1
    p.win._status_bar.set_path("~/data/G000.00+00.00")  # instead of the temporary folder's path
    yield 0.8


def plot_menu(p: Player) -> Iterator[float]:
    """The plot's right-click menu, opened over the top panel."""
    yield from solved(p)
    canvas = p.win._canvas
    yield from p.move(p.at(canvas, 0.55, 0.3), 0.2)
    p.right_click()
    yield 0.8


def python_dialog(p: Player) -> Iterator[float]:
    """Help → Use from Python..., the example script with syntax colours."""
    yield from solved(p)
    p.trigger("Use from Python...")
    yield 1.0


# ------------------------------------------------------------------- animations
def _tab(p: Player, tab_id: str) -> Iterator[float]:
    """Glide to a parameter tab and open it."""
    tabs = p.win._parameter_tabs
    index = tabs.tab_ids().index(tab_id)
    rect = tabs.tabBar().tabRect(index)
    yield from p.move(p.at(tabs.tabBar(), rect.center().x() / tabs.tabBar().width(), 0.5), 0.6)
    tabs.set_current_tab(tab_id)
    yield 0.4


def tour(p: Player) -> Iterator[float]:
    """The pulse along the medium (z slider), the coherence R on the right axis, then dark mode."""
    yield from solved(p)
    yield from _tab(p, "slice")
    z = p.win._parameter_tabs.get_widget("slice.z")
    yield from p.drag_slider(z, fraction=0.25, seconds=1.4)
    yield 0.4
    yield from p.drag_slider(z, fraction=1.0, seconds=1.4)
    yield 0.6
    yield from p.select(p.win._right_plot_combo, "R")
    yield 1.2
    yield from p.open_menu("View")
    yield from p.choose("Appearance")
    yield from p.choose("Dark")
    yield 1.4
    yield from p.drag_slider(z, fraction=0.5, seconds=1.0)
    yield 0.3
    yield from p.drag_slider(z, fraction=1.0, seconds=1.0)
    yield 0.8


SIZE = (1400, 760)

SHOTS = {
    "main_window": Shot(studio, solved, size=SIZE),
    "fit_mode": Shot(studio_with_data, fitting, size=SIZE),
    "plot_menu": Shot(studio, plot_menu, size=SIZE, composite=True),
    "python_dialog": Shot(studio, python_dialog, target="dialog"),
    "splash": Shot(splash, shadow=False),
}

GIFS = {
    "tour": Gif(studio, tour, width=900, size=SIZE),
}

if __name__ == "__main__":
    raise SystemExit(main(SHOTS, GIFS))
