# Changelog

What changed in each version of Maxwell Bloch Studio, newest first. Pushing a
version's tag publishes its section as the GitHub Release (`.github/workflows/release.yml`),
where the app's update notice reads it.

## 10.7.4 — 2026-10-19
- PDF exports: the report page starts with "How to cite", the references of Maxwell Bloch
  Studio and mbsolver with their versions and DOIs.

## 10.7.3 — 2026-10-19
- Maxwell Bloch Studio has its own DOI, 10.5281/zenodo.23487624 (all versions): About, the
  README and `CITATION.cff` cite it, next to mbsolver's.

## 10.7.2 — 2026-10-19
- No changes in the app. First release archived on Zenodo, which gives Maxwell Bloch Studio a
  citable DOI; `CITATION.cff` has an abstract and keywords for it.

## 10.7.1 — 2026-10-19
- About asks you to cite the app and the solver it runs on (mbsolver, with its DOI) if you use
  them in published work (sciwidgets 0.12.1).

## 10.7.0 — 2026-10-19
- The Help menu is now the same in all of the author's apps (Maxwell Bloch Studio, Line Catalog
  Explorer, daftarche): User Guide, Equations Reference (moved here from the Info menu),
  Use from Python..., Check for Updates… (new shortcut Ctrl+U / ⌘U) and About.
- About lists the libraries the app is built on, with their versions and licenses, including
  Qt; the separate "About Qt" item is gone.
- Shortcuts: Open Data Folder... is now Ctrl+O / ⌘O (the usual "Open"), Open Current Source
  Folder Ctrl+Alt+O / ⌥⌘O, and Data Summary Ctrl+I / ⌘I — on a Mac the old ⌥⌘D shows or hides
  the Dock, so the app never received it.
- Needs sciwidgets 0.12.

## 10.6.2 — 2026-10-19
- When the solver refuses a change (for example T₂ = ∞ with the adiabatic option on, or
  ticking the option while T₂ is ∞), the changed setting now goes back to its previous
  value, so the panel always matches the plot; the message names the tab.

## 10.6.1 — 2026-10-19
- On/off options ("Adiabatic (rate equations)", "Normalize to max") start at the left
  edge of their group, with the formula right after the text (sciwidgets 0.11.4).

## 10.6.0 — 2026-10-19
- New option **Adiabatic (rate equations)** on the Solver tab: the coherence follows
  its steady state, R = R₀ − T₂ A w, and only w and A are solved. Useful when T₂ is short;
  it differs from the full model during the first few T₂ and in fast bursts. It needs a
  finite T₂. Parameter files from earlier versions open with it off (the full model).
- The Grid tab is now called **Solver**.
- When the solver rejects the parameters (for example T₂ = ∞ with the adiabatic option),
  a "Cannot Solve" message appears and the previous results stay shown; before, the app
  could stay in the Solving state.
- Needs mbsolver 0.5 (was 0.3).
- The equations reference is now mbsolver's two-level model document
  (`docs/two_level.pdf`), with a section mapping symbols to the solver's
  arguments and a list of references. Its LaTeX source moved to mbsolver;
  `tools/build_docs.sh` copies the PDF from a clone of mbsolver next to this repository.

## 10.5.0 — 2026-10-17
- The launcher (`mbstudio install-app`) and the update check (`mbstudio update`,
  Help ▸ Check for Updates…, Update Now) now come from sciwidgets 0.11 (`sciwidgets.app`),
  shared with linecat. Nothing changes for users; installed launchers keep working.
- Needs sciwidgets 0.11 (was 0.8): with it come the table, dialog and plot fixes of
  sciwidgets 0.9–0.10.

## 10.4.0 — 2026-10-16
- The launcher made by `mbstudio install-app` now updates itself: after an update, the
  app refreshes it on its next start (icon and version shown in Finder), so you never
  need to run `mbstudio install-app` again for that.

## 10.3.0 — 2026-10-16
- *Update Now* in the update notice: the app installs the new version itself (no terminal
  needed), shows the progress, and then offers to restart. If the update cannot finish, it
  says how to do it by hand.

## 10.2.0 — 2026-10-16
- Start the app with a double-click: `mbstudio install-app` adds Maxwell Bloch Studio to
  your Applications folder (macOS; also Launchpad, Spotlight and the Dock), the Start menu
  (Windows) or the applications menu (Linux). It keeps working after `mbstudio update`;
  `mbstudio install-app --remove` takes it away. The Windows shortcut is new and not yet
  tried on many machines; please report problems.

## 10.1.1 — 2026-10-16
- The curve and grid style dialogs now show each change on the plot at once, like the
  span dialog; *Cancel* puts the old style back.
- Uses sciwidgets 0.8.1.

## 10.1.0 — 2026-10-16
- The current span can be restyled: right-click the plot → *Current span style…* sets
  the shaded area's fill colour and opacity and its edge colour, opacity, width and line,
  and the centre line's colour, opacity, width and line. Saved between sessions;
  *View → Reset Plot Style* resets it.
- Uses sciwidgets 0.8.

## 10.0.8 — 2026-10-15
- New terminal commands: `mbstudio --version`, `mbstudio update`, `mbstudio solve FILE`
  (without the window, e.g. on a cluster), `mbstudio example`, and `mbstudio PATH` to open
  a parameter file or data folder at start. See `mbstudio --help` and the User Guide.

## 10.0.7 — 2026-10-15
- The splash screen now comes from sciwidgets 0.7 (looks the same).

## 10.0.6 — 2026-10-15
- No changes for users (version number only).

## 10.0.5 — 2026-10-15
- User Guide: new main-window screenshot.
- Tests for the Python script API and the update notice.

## 10.0.4 — 2026-10-15
- `mbstudio.scaling` now comes from the solver package (`mbsolver.scaling`,
  mbsolver 0.3); same results. Scripts that use only `mbsolver` can now get
  η and θ₀ from the physical sample values too.

## 10.0.3 — 2026-10-15
- The update notice now lists what is new in the newer versions.

## 10.0.2 — 2026-10-15
- New app icon: a superradiant burst computed with the solver.
- User Guide: screenshots of the main window, the plot menu, fit mode and the
  *Use from Python* dialog.
- Uses sciwidgets 0.6.

## 10.0.1 — 2026-10-15
- New splash screen with the app name and version.
- User Guide and equations reference: new title pages; their sources are now
  part of the repository (`docs/`).

## 10.0.0 — 2026-10-14
- New name: **Maxwell Bloch Studio** (was Maxwell Bloch Solver). Install with
  `pipx install maxwell-bloch-studio`; start with `mbstudio` or
  `maxwell-bloch-studio`. Your settings carry over.
- The numerical solver is now the separate package `mbsolver`.
- Scripts use `import mbstudio` (`mbstudio.ParamsFile`, `mbstudio.solve`,
  `mbstudio.scaling`).

Earlier versions were released as Maxwell Bloch Solver
(`maxwell-bloch-solver` on PyPI, up to 9.2.0).
