"""View → Appearance: the saved choice, and exports staying light."""

from PySide6.QtCore import QSettings

from mbstudio.app.settings_manager import APPEARANCE_KEY, Settings


def _settings(tmp_path):
    settings = Settings.__new__(Settings)
    settings._settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    return settings


def test_appearance_is_remembered(tmp_path):
    settings = _settings(tmp_path)
    assert settings.get_appearance() == "system"
    for scheme in ("dark", "light", "system"):
        settings.set_appearance(scheme)
        assert settings.get_appearance() == scheme
    settings.set_appearance("dim")                      # unknown values are not saved
    assert settings.get_appearance() == "system"
    settings._settings.setValue(APPEARANCE_KEY, "nonsense")
    assert settings.get_appearance() == "system"
