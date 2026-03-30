import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from medextract.__main__ import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    return re.compile(r"\x1b\[[0-9;]*m").sub("", text)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.output)
    assert "convert" in output
    assert "report" in output


def test_convert_help():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.output)
    assert "to-csv" in output
    assert "st-cruz" in output


def test_report_help():
    result = runner.invoke(app, ["report", "--help"])
    assert result.exit_code == 0
    output = strip_ansi(result.output)
    assert "generate" in output


def test_convert_to_csv_with_fixture(tmp_path: Path):
    fixture = Path("tests/fixtures/input_example.pdf")
    if not fixture.exists():
        pytest.skip("Fixture PDF não encontrada")

    result = runner.invoke(
        app, ["convert", "to-csv", str(fixture), "--output", str(tmp_path / "out.csv")]
    )
    assert result.exit_code == 0
    assert (tmp_path / "out.csv").exists()


def test_convert_to_xlsx_with_fixture(tmp_path: Path):
    fixture = Path("tests/fixtures/input_example.pdf")
    if not fixture.exists():
        pytest.skip("Fixture PDF não encontrada")

    out = tmp_path / "out.xlsx"
    result = runner.invoke(
        app, ["convert", "to-csv", str(fixture), "--output", str(out), "--format", "xlsx"]
    )
    assert result.exit_code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_convert_missing_pdf():
    result = runner.invoke(app, ["convert", "to-csv", "/nao/existe.pdf"])
    assert result.exit_code != 0


def test_report_generate_from_csv(tmp_path: Path):
    fixture_csv = Path("tests/fixtures/output_example.csv")
    if not fixture_csv.exists():
        pytest.skip("Fixture CSV não encontrada")

    out = tmp_path / "relatorio.xlsx"
    result = runner.invoke(app, ["report", "generate", str(fixture_csv), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert out.stat().st_size > 0


def test_report_generate_from_empty_dir(tmp_path: Path):
    result = runner.invoke(app, ["report", "generate", str(tmp_path)])
    assert result.exit_code != 0
