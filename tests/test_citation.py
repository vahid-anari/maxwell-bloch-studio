"""The references for citing results (About and the PDF report), defined once in app_metadata."""

from mbstudio.config import app_metadata as meta


def test_references_name_both_dois_and_versions():
    studio, solver = meta.citation_references()
    assert f"https://doi.org/{meta.STUDIO_DOI}" in studio and meta.APP_VERSION in studio
    assert f"https://doi.org/{meta.MBSOLVER_DOI}" in solver and "Rashidi" in solver
    assert meta.STUDIO_DOI == "10.5281/zenodo.23487624" and meta.MBSOLVER_DOI == "10.5281/zenodo.23407483"


def test_pdf_report_starts_with_how_to_cite():
    from mbstudio.app.plot import PlotExporter

    exporter = object.__new__(PlotExporter)  # only the two callables the report text needs
    exporter._get_metadata = lambda: {"saved_by": "test"}
    exporter._get_parameter_tabs_value = lambda: {"solve.grid.nt": 10}
    text = exporter._build_report_text()
    assert text.startswith("How to cite")
    assert text.index(meta.STUDIO_DOI) < text.index("Metadata") < text.index("Parameters")
    lines = PlotExporter._wrap_report_lines(text, width=110)
    assert all(len(line) <= 110 for line in lines)
